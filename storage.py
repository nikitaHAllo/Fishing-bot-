"""SQLite-хранилище игроков, улова и поклёвок."""

from __future__ import annotations

import asyncio
import math
import random
import secrets
import sqlite3
import time
from datetime import date
from pathlib import Path

from game import apply_reaction, did_escape, new_achievements, roll_catch
from game_data import (
    BAIT_BY_ID,
    FISH_BY_ID,
    KEEPNET_LIMIT,
    LOC_BY_ID,
    ROD_BY_ID,
    RODS,
    level_from_xp,
    location_index,
    locations_unlocked,
    rod_index,
    upgrade_cost,
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    coins INTEGER NOT NULL DEFAULT 50,
    xp INTEGER NOT NULL DEFAULT 0,
    rod_id TEXT NOT NULL DEFAULT 'bamboo',
    location_id TEXT NOT NULL DEFAULT 'pond',
    bait_id TEXT,
    last_cast REAL NOT NULL DEFAULT 0,
    catches INTEGER NOT NULL DEFAULT 0,
    total_weight INTEGER NOT NULL DEFAULT 0,
    best_weight INTEGER NOT NULL DEFAULT 0,
    best_fish_id TEXT,
    earned INTEGER NOT NULL DEFAULT 0,
    loc_rank INTEGER NOT NULL DEFAULT 0,
    daily_on TEXT,
    net_on TEXT,
    created_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS bait_stock (
    user_id INTEGER NOT NULL,
    bait_id TEXT NOT NULL,
    qty INTEGER NOT NULL,
    PRIMARY KEY (user_id, bait_id)
);

CREATE TABLE IF NOT EXISTS keepnet (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    fish_id TEXT NOT NULL,
    weight INTEGER NOT NULL,
    price INTEGER NOT NULL,
    caught_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_keepnet_user ON keepnet(user_id);

CREATE TABLE IF NOT EXISTS bestiary (
    user_id INTEGER NOT NULL,
    fish_id TEXT NOT NULL,
    count INTEGER NOT NULL,
    best_weight INTEGER NOT NULL,
    PRIMARY KEY (user_id, fish_id)
);

CREATE TABLE IF NOT EXISTS achievements (
    user_id INTEGER NOT NULL,
    ach_id TEXT NOT NULL,
    PRIMARY KEY (user_id, ach_id)
);

CREATE TABLE IF NOT EXISTS bites (
    user_id INTEGER PRIMARY KEY,
    token TEXT NOT NULL,
    chat_id INTEGER NOT NULL,
    message_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    bite_at REAL,
    created_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""

STALE_BITE_SECONDS = 25


class Database:
    def __init__(self, path: Path):
        self.path = path
        self.conn: sqlite3.Connection | None = None
        self.lock = asyncio.Lock()

    async def init(self) -> None:
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA busy_timeout=3000")
        self.conn.executescript(SCHEMA)
        columns = {row[1] for row in self.conn.execute("PRAGMA table_info(users)")}
        if "net_on" not in columns:
            self.conn.execute("ALTER TABLE users ADD COLUMN net_on TEXT")
        self.conn.execute("DELETE FROM bites")
        self.conn.commit()

    async def close(self) -> None:
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    async def _run(self, func):
        async with self.lock:
            try:
                result = func()
                self.conn.commit()
                return result
            except Exception:
                self.conn.rollback()
                raise

    def _user(self, user_id: int) -> dict:
        row = self.conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
        if row is None:
            raise KeyError(user_id)
        return dict(row)

    def _bite(self, user_id: int) -> dict | None:
        row = self.conn.execute("SELECT * FROM bites WHERE user_id=?", (user_id,)).fetchone()
        return dict(row) if row else None

    def _qty(self, user_id: int, bait_id: str) -> int:
        row = self.conn.execute(
            "SELECT qty FROM bait_stock WHERE user_id=? AND bait_id=?",
            (user_id, bait_id),
        ).fetchone()
        return int(row["qty"]) if row else 0

    def _stock(self, user_id: int) -> dict[str, int]:
        rows = self.conn.execute(
            "SELECT bait_id, qty FROM bait_stock WHERE user_id=? AND qty>0",
            (user_id,),
        ).fetchall()
        return {row["bait_id"]: int(row["qty"]) for row in rows}

    def _keepnet_summary(self, user_id: int) -> dict:
        row = self.conn.execute(
            "SELECT COUNT(*), COALESCE(SUM(price), 0) FROM keepnet WHERE user_id=?",
            (user_id,),
        ).fetchone()
        return {"count": int(row[0]), "value": int(row[1])}

    def _unlocked(self, user_id: int) -> set[str]:
        rows = self.conn.execute(
            "SELECT ach_id FROM achievements WHERE user_id=?",
            (user_id,),
        ).fetchall()
        return {row["ach_id"] for row in rows}

    def _stats(self, user: dict) -> dict:
        rows = self.conn.execute(
            "SELECT fish_id FROM bestiary WHERE user_id=?",
            (user["user_id"],),
        ).fetchall()
        rarities: set[str] = set()
        for row in rows:
            fish = FISH_BY_ID.get(row["fish_id"])
            if fish:
                rarities.add(fish["rarity"])
        return {
            "catches": user["catches"],
            "total_weight": user["total_weight"],
            "best_weight": user["best_weight"],
            "level": level_from_xp(user["xp"])[0],
            "earned": user["earned"],
            "unique": len(rows),
            "rarities": rarities,
            "rod_index": rod_index(user["rod_id"]),
            "loc_index": int(user["loc_rank"]),
        }

    def _grant_achievements(self, user_id: int) -> list[dict]:
        gained = []
        for _ in range(8):
            user = self._user(user_id)
            batch = new_achievements(self._stats(user), self._unlocked(user_id))
            if not batch:
                break
            reward = 0
            for achievement in batch:
                self.conn.execute(
                    "INSERT OR IGNORE INTO achievements (user_id, ach_id) VALUES (?, ?)",
                    (user_id, achievement["id"]),
                )
                reward += int(achievement["reward"])
                gained.append(
                    {
                        "id": achievement["id"],
                        "name": achievement["name"],
                        "desc": achievement["desc"],
                        "reward": achievement["reward"],
                    }
                )
            if reward:
                self.conn.execute(
                    "UPDATE users SET coins = coins + ? WHERE user_id=?",
                    (reward, user_id),
                )
        return gained

    def _consume_bait(self, user: dict) -> dict:
        info = {"luck": 0, "empty": False, "name": None, "emoji": "🪱"}
        bait_id = user["bait_id"]
        if not bait_id:
            return info
        bait = BAIT_BY_ID.get(bait_id)
        user_id = user["user_id"]
        if bait is None or self._qty(user_id, bait_id) <= 0:
            self.conn.execute("UPDATE users SET bait_id=NULL WHERE user_id=?", (user_id,))
            return info
        qty = self._qty(user_id, bait_id) - 1
        info.update(luck=bait["luck"], name=bait["name"], emoji=bait["emoji"])
        if qty <= 0:
            self.conn.execute(
                "DELETE FROM bait_stock WHERE user_id=? AND bait_id=?",
                (user_id, bait_id),
            )
            self.conn.execute("UPDATE users SET bait_id=NULL WHERE user_id=?", (user_id,))
            info["empty"] = True
        else:
            self.conn.execute(
                "UPDATE bait_stock SET qty=? WHERE user_id=? AND bait_id=?",
                (qty, user_id, bait_id),
            )
        return info

    def _place(self, user: dict) -> int:
        row = self.conn.execute(
            """
            SELECT COUNT(*) + 1 FROM users
            WHERE xp > ? OR (xp = ? AND catches > ?)
            """,
            (user["xp"], user["xp"], user["catches"]),
        ).fetchone()
        return int(row[0])

    async def fishing_chat(self) -> dict | None:
        def run():
            rows = self.conn.execute(
                "SELECT key, value FROM settings WHERE key IN ('chat_id', 'chat_title', 'chat_link')"
            ).fetchall()
            data = {row["key"]: row["value"] for row in rows}
            if not data.get("chat_id") or data.get("chat_id") == "0":
                return None
            return data

        return await self._run(run)

    async def save_fishing_chat(self, chat_id: int, title: str, link: str) -> None:
        def run():
            pairs = (
                ("chat_id", str(chat_id)),
                ("chat_title", title),
                ("chat_link", link),
            )
            for key, value in pairs:
                self.conn.execute(
                    """
                    INSERT INTO settings (key, value) VALUES (?, ?)
                    ON CONFLICT(key) DO UPDATE SET value=excluded.value
                    """,
                    (key, value),
                )

        await self._run(run)

    async def clear_fishing_chat(self) -> None:
        def run():
            self.conn.execute(
                "DELETE FROM settings WHERE key IN ('chat_id', 'chat_title', 'chat_link')"
            )

        await self._run(run)

    async def get_or_create(self, user_id: int, username: str | None, first_name: str | None) -> dict:
        def run():
            self.conn.execute(
                """
                INSERT INTO users (user_id, username, first_name, created_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username=excluded.username,
                    first_name=excluded.first_name
                """,
                (user_id, username, first_name or "Рыбак", time.time()),
            )
            return self._user(user_id)

        return await self._run(run)

    async def begin_cast(self, user_id: int, now: float) -> dict:
        def run():
            user = self._user(user_id)
            if self._keepnet_summary(user_id)["count"] >= KEEPNET_LIMIT:
                return {"ok": False, "error": "full"}
            bite = self._bite(user_id)
            if bite and now - float(bite["created_at"]) > STALE_BITE_SECONDS:
                self.conn.execute("DELETE FROM bites WHERE user_id=?", (user_id,))
                bite = None
            if bite:
                return {"ok": False, "error": "biting"}
            rod = ROD_BY_ID.get(user["rod_id"], RODS[0])
            left = rod["cooldown"] - (now - float(user["last_cast"] or 0))
            if left > 0.4:
                return {"ok": False, "error": "cooldown", "left": int(math.ceil(left))}
            token = secrets.token_hex(8)
            self.conn.execute(
                "UPDATE users SET last_cast=? WHERE user_id=?",
                (now, user_id),
            )
            self.conn.execute(
                """
                INSERT INTO bites (user_id, token, chat_id, message_id, status, bite_at, created_at)
                VALUES (?, ?, 0, 0, 'waiting', NULL, ?)
                """,
                (user_id, token, now),
            )
            return {"ok": True, "token": token}

        return await self._run(run)

    async def attach_bite(self, user_id: int, token: str, chat_id: int, message_id: int) -> bool:
        def run():
            cur = self.conn.execute(
                """
                UPDATE bites SET chat_id=?, message_id=?
                WHERE user_id=? AND token=? AND status='waiting'
                """,
                (chat_id, message_id, user_id, token),
            )
            return cur.rowcount == 1

        return await self._run(run)

    async def mark_biting(self, user_id: int, token: str, now: float) -> bool:
        def run():
            cur = self.conn.execute(
                """
                UPDATE bites SET status='biting', bite_at=?
                WHERE user_id=? AND token=? AND status='waiting'
                """,
                (now, user_id, token),
            )
            return cur.rowcount == 1

        return await self._run(run)

    async def resolve_miss(self, user_id: int, token: str) -> bool:
        def run():
            cur = self.conn.execute(
                "DELETE FROM bites WHERE user_id=? AND token=? AND status IN ('waiting', 'biting')",
                (user_id, token),
            )
            return cur.rowcount == 1

        return await self._run(run)

    async def resolve_hook(self, user_id: int, token: str, now: float) -> dict | None:
        def run():
            bite = self._bite(user_id)
            if not bite or bite["token"] != token or bite["status"] != "biting":
                return None
            self.conn.execute("DELETE FROM bites WHERE user_id=?", (user_id,))
            user = self._user(user_id)
            rod = ROD_BY_ID.get(user["rod_id"], RODS[0])
            location = LOC_BY_ID.get(user["location_id"])
            loc_luck = location["luck"] if location else 0
            bait = self._consume_bait(user)
            luck = rod["luck"] + loc_luck + bait["luck"]
            reaction = max(0.0, now - float(bite["bite_at"] or now))
            catch = apply_reaction(roll_catch(user["location_id"], luck), reaction)
            escaped = catch.get("kind") != "find" and did_escape(catch["rarity"], luck)
            payload = {
                **catch,
                "escaped": escaped,
                "bait_empty": bait["empty"],
                "bait_name": bait["name"],
                "bait_emoji": bait["emoji"],
            }
            if escaped:
                return payload

            old_level = level_from_xp(user["xp"])[0]
            new_xp = user["xp"] + catch["xp"]
            record = user["best_weight"] > 0 and catch["weight"] > user["best_weight"]
            best_weight = user["best_weight"]
            best_fish = user["best_fish_id"]
            if catch["weight"] > best_weight:
                best_weight = catch["weight"]
                best_fish = catch["fish_id"]
            self.conn.execute(
                """
                UPDATE users
                SET xp=?, catches=catches+1, total_weight=total_weight+?,
                    best_weight=?, best_fish_id=?
                WHERE user_id=?
                """,
                (new_xp, catch["weight"], best_weight, best_fish, user_id),
            )
            self.conn.execute(
                """
                INSERT INTO keepnet (user_id, fish_id, weight, price, caught_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, catch["fish_id"], catch["weight"], catch["price"], now),
            )
            self.conn.execute(
                """
                INSERT INTO bestiary (user_id, fish_id, count, best_weight)
                VALUES (?, ?, 1, ?)
                ON CONFLICT(user_id, fish_id) DO UPDATE SET
                    count=count+1,
                    best_weight=MAX(bestiary.best_weight, excluded.best_weight)
                """,
                (user_id, catch["fish_id"], catch["weight"]),
            )
            achievements = self._grant_achievements(user_id)
            fresh = self._user(user_id)
            level, into, need = level_from_xp(fresh["xp"])
            payload.update(
                record=record,
                level=level,
                into=into,
                need=need,
                leveled=level > old_level,
                new_locations=locations_unlocked(old_level, level),
                achievements=achievements,
                keepnet=self._keepnet_summary(user_id),
                coins=fresh["coins"],
            )
            return payload

        return await self._run(run)

    async def cast_net(self, user_id: int) -> dict:
        def run():
            user = self._user(user_id)
            today = date.today().isoformat()
            if user.get("net_on") == today:
                return {"ok": False, "error": "used"}
            room = KEEPNET_LIMIT - self._keepnet_summary(user_id)["count"]
            if room <= 0:
                return {"ok": False, "error": "full"}
            rod = ROD_BY_ID.get(user["rod_id"], RODS[0])
            location = LOC_BY_ID.get(user["location_id"])
            loc_luck = location["luck"] if location else 0
            bait_luck = 0
            bait = BAIT_BY_ID.get(user["bait_id"]) if user["bait_id"] else None
            if bait and self._qty(user_id, bait["id"]) > 0:
                bait_luck = bait["luck"]
            luck = rod["luck"] + loc_luck + bait_luck
            pulls = min(room, random.randint(4, 6))
            now = time.time()
            old_level = level_from_xp(user["xp"])[0]
            xp = user["xp"]
            total_weight = user["total_weight"]
            best_weight = user["best_weight"]
            best_fish = user["best_fish_id"]
            items = []
            for _ in range(pulls):
                catch = apply_reaction(roll_catch(user["location_id"], luck), 3.0)
                if catch["weight"] > best_weight:
                    best_weight = catch["weight"]
                    best_fish = catch["fish_id"]
                xp += catch["xp"]
                total_weight += catch["weight"]
                self.conn.execute(
                    """
                    INSERT INTO keepnet (user_id, fish_id, weight, price, caught_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (user_id, catch["fish_id"], catch["weight"], catch["price"], now),
                )
                self.conn.execute(
                    """
                    INSERT INTO bestiary (user_id, fish_id, count, best_weight)
                    VALUES (?, ?, 1, ?)
                    ON CONFLICT(user_id, fish_id) DO UPDATE SET
                        count=count+1,
                        best_weight=MAX(bestiary.best_weight, excluded.best_weight)
                    """,
                    (user_id, catch["fish_id"], catch["weight"]),
                )
                items.append(catch)
            self.conn.execute(
                """
                UPDATE users
                SET xp=?, catches=catches+?, total_weight=?,
                    best_weight=?, best_fish_id=?, net_on=?
                WHERE user_id=?
                """,
                (xp, pulls, total_weight, best_weight, best_fish, today, user_id),
            )
            achievements = self._grant_achievements(user_id)
            fresh = self._user(user_id)
            level, into, need = level_from_xp(fresh["xp"])
            return {
                "ok": True,
                "items": items,
                "achievements": achievements,
                "level": level,
                "into": into,
                "need": need,
                "leveled": level > old_level,
                "new_locations": locations_unlocked(old_level, level),
                "keepnet": self._keepnet_summary(user_id),
            }

        return await self._run(run)

    async def keepnet_view(self, user_id: int) -> dict:
        def run():
            rows = self.conn.execute(
                "SELECT fish_id, weight, price FROM keepnet WHERE user_id=? ORDER BY id DESC",
                (user_id,),
            ).fetchall()
            items = []
            for row in rows:
                fish = FISH_BY_ID.get(row["fish_id"])
                items.append(
                    {
                        "name": fish["name"] if fish else row["fish_id"],
                        "emoji": fish["emoji"] if fish else "🐟",
                        "weight": row["weight"],
                        "price": row["price"],
                    }
                )
            summary = self._keepnet_summary(user_id)
            return {"items": items, "count": summary["count"], "total": summary["value"]}

        return await self._run(run)

    async def sell_all(self, user_id: int) -> dict:
        def run():
            summary = self._keepnet_summary(user_id)
            if summary["count"] <= 0:
                return {"ok": False, "error": "empty"}
            self.conn.execute("DELETE FROM keepnet WHERE user_id=?", (user_id,))
            self.conn.execute(
                "UPDATE users SET coins=coins+?, earned=earned+? WHERE user_id=?",
                (summary["value"], summary["value"], user_id),
            )
            achievements = self._grant_achievements(user_id)
            user = self._user(user_id)
            return {
                "ok": True,
                "count": summary["count"],
                "money": summary["value"],
                "coins": user["coins"],
                "achievements": achievements,
            }

        return await self._run(run)

    async def buy_rod(self, user_id: int, rod_id: str) -> dict:
        def run():
            rod = ROD_BY_ID.get(rod_id)
            if rod is None:
                return {"ok": False, "error": "missing"}
            user = self._user(user_id)
            cost = upgrade_cost(user["rod_id"], rod_id)
            if cost is None:
                return {"ok": False, "error": "worse"}
            if user["coins"] < cost:
                return {"ok": False, "error": "money", "cost": cost, "coins": user["coins"]}
            self.conn.execute(
                "UPDATE users SET coins=coins-?, rod_id=? WHERE user_id=?",
                (cost, rod_id, user_id),
            )
            achievements = self._grant_achievements(user_id)
            return {
                "ok": True,
                "cost": cost,
                "player": self._user(user_id),
                "achievements": achievements,
            }

        return await self._run(run)

    async def bait_stock(self, user_id: int) -> dict[str, int]:
        return await self._run(lambda: self._stock(user_id))

    async def buy_bait(self, user_id: int, bait_id: str, count: int) -> dict:
        def run():
            bait = BAIT_BY_ID.get(bait_id)
            if bait is None or count not in (1, 5):
                return {"ok": False, "error": "missing"}
            user = self._user(user_id)
            cost = bait["price"] * count
            if user["coins"] < cost:
                return {"ok": False, "error": "money", "cost": cost, "coins": user["coins"]}
            self.conn.execute(
                "UPDATE users SET coins=coins-? WHERE user_id=?",
                (cost, user_id),
            )
            self.conn.execute(
                """
                INSERT INTO bait_stock (user_id, bait_id, qty) VALUES (?, ?, ?)
                ON CONFLICT(user_id, bait_id) DO UPDATE SET qty=qty+excluded.qty
                """,
                (user_id, bait_id, count),
            )
            if not user["bait_id"]:
                self.conn.execute(
                    "UPDATE users SET bait_id=? WHERE user_id=?",
                    (bait_id, user_id),
                )
            achievements = self._grant_achievements(user_id)
            return {
                "ok": True,
                "player": self._user(user_id),
                "stock": self._stock(user_id),
                "achievements": achievements,
            }

        return await self._run(run)

    async def equip_bait(self, user_id: int, bait_id: str) -> dict:
        def run():
            if bait_id not in BAIT_BY_ID:
                return {"ok": False, "error": "missing"}
            user = self._user(user_id)
            if user["bait_id"] == bait_id:
                return {"ok": False, "error": "already"}
            if self._qty(user_id, bait_id) <= 0:
                return {"ok": False, "error": "empty"}
            self.conn.execute(
                "UPDATE users SET bait_id=? WHERE user_id=?",
                (bait_id, user_id),
            )
            return {"ok": True, "player": self._user(user_id), "stock": self._stock(user_id)}

        return await self._run(run)

    async def unequip_bait(self, user_id: int) -> dict:
        def run():
            self.conn.execute("UPDATE users SET bait_id=NULL WHERE user_id=?", (user_id,))
            return {"player": self._user(user_id), "stock": self._stock(user_id)}

        return await self._run(run)

    async def set_location(self, user_id: int, location_id: str) -> dict:
        def run():
            location = LOC_BY_ID.get(location_id)
            if location is None:
                return {"ok": False, "error": "missing"}
            user = self._user(user_id)
            level = level_from_xp(user["xp"])[0]
            if level < location["level"]:
                return {"ok": False, "error": "locked", "level": location["level"]}
            if user["location_id"] == location_id:
                return {"ok": False, "error": "same"}
            rank = max(int(user["loc_rank"]), location_index(location_id))
            self.conn.execute(
                "UPDATE users SET location_id=?, loc_rank=? WHERE user_id=?",
                (location_id, rank, user_id),
            )
            achievements = self._grant_achievements(user_id)
            return {
                "ok": True,
                "player": self._user(user_id),
                "achievements": achievements,
                "name": location["name"],
            }

        return await self._run(run)

    async def claim_daily(self, user_id: int) -> dict:
        def run():
            user = self._user(user_id)
            today = date.today().isoformat()
            if user["daily_on"] == today:
                return {"ok": False, "error": "claimed"}
            old_level, _, _ = level_from_xp(user["xp"])
            gain = 60 + old_level * 25
            xp_gain = 15
            new_xp = user["xp"] + xp_gain
            new_level = level_from_xp(new_xp)[0]
            self.conn.execute(
                "UPDATE users SET coins=coins+?, xp=?, daily_on=? WHERE user_id=?",
                (gain, new_xp, today, user_id),
            )
            achievements = self._grant_achievements(user_id)
            fresh = self._user(user_id)
            level = level_from_xp(fresh["xp"])[0]
            return {
                "ok": True,
                "gain": gain,
                "xp": xp_gain,
                "coins": fresh["coins"],
                "level": level,
                "locations": locations_unlocked(old_level, new_level),
                "achievements": achievements,
            }

        return await self._run(run)

    async def snapshot(self, user_id: int) -> dict:
        def run():
            user = self._user(user_id)
            bait = BAIT_BY_ID.get(user["bait_id"]) if user["bait_id"] else None
            unique = self.conn.execute(
                "SELECT COUNT(*) FROM bestiary WHERE user_id=?",
                (user_id,),
            ).fetchone()[0]
            ach_count = self.conn.execute(
                "SELECT COUNT(*) FROM achievements WHERE user_id=?",
                (user_id,),
            ).fetchone()[0]
            return {
                "player": user,
                "bait": bait,
                "bait_qty": self._qty(user_id, user["bait_id"]) if user["bait_id"] else 0,
                "unique": int(unique),
                "ach_count": int(ach_count),
                "place": self._place(user),
            }

        return await self._run(run)

    async def leaderboard(self, user_id: int) -> dict:
        def run():
            rows = self.conn.execute(
                """
                SELECT first_name, xp, catches
                FROM users
                ORDER BY xp DESC, catches DESC
                LIMIT 10
                """
            ).fetchall()
            user = self._user(user_id)
            return {
                "rows": [dict(row) for row in rows],
                "place": self._place(user),
                "me": user,
            }

        return await self._run(run)

    async def bestiary(self, user_id: int) -> dict[str, dict]:
        def run():
            rows = self.conn.execute(
                "SELECT fish_id, count, best_weight FROM bestiary WHERE user_id=?",
                (user_id,),
            ).fetchall()
            return {
                row["fish_id"]: {"count": row["count"], "best_weight": row["best_weight"]}
                for row in rows
            }

        return await self._run(run)


db = Database(Path(__file__).resolve().parent / "fishing.db")
