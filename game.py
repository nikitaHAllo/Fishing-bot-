"""Бросок удочки: редкость, вес, срыв, достижения."""

from __future__ import annotations

import random

from game_data import (
    ESCAPE_CHANCE,
    FISH_BY_ID,
    RARITY,
    RODS,
    calc_price,
    find_chance,
    finds_for,
    fishes_for,
    is_catch_fish,
    location_index,
    rarities_in_location,
    rod_index,
)

ACHIEVEMENTS = [
    {
        "id": "first",
        "name": "Первая поклёвка",
        "desc": "Поймай первую добычу",
        "reward": 40,
        "ok": lambda s: s["catches"] >= 1,
    },
    {
        "id": "c25",
        "name": "На крючке",
        "desc": "Поймай 25 раз",
        "reward": 120,
        "ok": lambda s: s["catches"] >= 25,
    },
    {
        "id": "c100",
        "name": "Завсегдатай",
        "desc": "Поймай 100 раз",
        "reward": 450,
        "ok": lambda s: s["catches"] >= 100,
    },
    {
        "id": "c500",
        "name": "Рыбак",
        "desc": "Поймай 500 раз",
        "reward": 2_000,
        "ok": lambda s: s["catches"] >= 500,
    },
    {
        "id": "rare",
        "name": "Редкая добыча",
        "desc": "Поймай редкую рыбу",
        "reward": 200,
        "ok": lambda s: "rare" in s["rarities"],
    },
    {
        "id": "epic",
        "name": "Эпический улов",
        "desc": "Поймай эпическую рыбу",
        "reward": 600,
        "ok": lambda s: "epic" in s["rarities"],
    },
    {
        "id": "legend",
        "name": "Легенда глубин",
        "desc": "Поймай легендарную рыбу",
        "reward": 2_000,
        "ok": lambda s: "legendary" in s["rarities"],
    },
    {
        "id": "mythic",
        "name": "Миф на крючке",
        "desc": "Поймай мифическую рыбу",
        "reward": 10_000,
        "ok": lambda s: "mythic" in s["rarities"],
    },
    {
        "id": "kg10",
        "name": "Десять кило",
        "desc": "Набери 10 кг суммарного улова",
        "reward": 250,
        "ok": lambda s: s["total_weight"] >= 10_000,
    },
    {
        "id": "kg100",
        "name": "Центнер",
        "desc": "Набери 100 кг суммарного улова",
        "reward": 2_000,
        "ok": lambda s: s["total_weight"] >= 100_000,
    },
    {
        "id": "trophy",
        "name": "Трофей",
        "desc": "Поймай рыбу от 20 кг",
        "reward": 800,
        "ok": lambda s: s["best_weight"] >= 20_000,
    },
    {
        "id": "monster",
        "name": "Монстр",
        "desc": "Поймай рыбу от 150 кг",
        "reward": 5_000,
        "ok": lambda s: s["best_weight"] >= 150_000,
    },
    {
        "id": "lv5",
        "name": "Свой берег",
        "desc": "Дойди до 5 уровня",
        "reward": 200,
        "ok": lambda s: s["level"] >= 5,
    },
    {
        "id": "lv10",
        "name": "Солёная вода",
        "desc": "Дойди до 10 уровня",
        "reward": 800,
        "ok": lambda s: s["level"] >= 10,
    },
    {
        "id": "lv20",
        "name": "Старый капитан",
        "desc": "Дойди до 20 уровня",
        "reward": 3_000,
        "ok": lambda s: s["level"] >= 20,
    },
    {
        "id": "collector",
        "name": "Коллекционер",
        "desc": "Открой 15 видов в справочнике",
        "reward": 700,
        "ok": lambda s: s["unique"] >= 15,
    },
    {
        "id": "museum",
        "name": "Музей рыбы",
        "desc": "Открой 30 видов в справочнике",
        "reward": 2_500,
        "ok": lambda s: s["unique"] >= 30,
    },
    {
        "id": "rod_pro",
        "name": "Снасти профи",
        "desc": "Купи профи-комплект",
        "reward": 400,
        "ok": lambda s: s["rod_index"] >= rod_index("pro"),
    },
    {
        "id": "rod_best",
        "name": "Снасть бездны",
        "desc": "Купи удочку бездны",
        "reward": 6_000,
        "ok": lambda s: s["rod_index"] >= rod_index("abyss"),
    },
    {
        "id": "abyss_loc",
        "name": "Ниже дна",
        "desc": "Дойди до локации Бездна",
        "reward": 2_000,
        "ok": lambda s: s["loc_index"] >= location_index("abyss"),
    },
    {
        "id": "purse",
        "name": "Первый куш",
        "desc": "Заработай продажами 20 000 монет",
        "reward": 500,
        "ok": lambda s: s["earned"] >= 20_000,
    },
    {
        "id": "magnate",
        "name": "Хозяин причала",
        "desc": "Заработай продажами 200 000 монет",
        "reward": 4_000,
        "ok": lambda s: s["earned"] >= 200_000,
    },
]


def roll_rarity(location_id: str, luck: int) -> str:
    weights = _fish_weights(location_id, luck)
    population = list(weights)
    return random.choices(population, weights=[weights[key] for key in population], k=1)[0]


def roll_catch(location_id: str, luck: int) -> dict:
    finds = finds_for(location_id)
    if finds and random.random() < find_chance(location_id, luck):
        return _from_item(_pick_find(finds, luck), luck, location_id)
    rarity = roll_rarity(location_id, luck)
    pool = fishes_for(location_id, rarity)
    if not pool:
        for fallback in ("common", "uncommon", "rare", "trash", "epic"):
            pool = fishes_for(location_id, fallback)
            if pool:
                break
    if not pool:
        pool = [
            fish
            for fish in FISH_BY_ID.values()
            if is_catch_fish(fish) and location_id in fish["locations"]
        ]
    if not pool:
        pool = [next(iter(FISH_BY_ID.values()))]
    return _from_item(random.choice(pool), luck, location_id)


def _pick_find(finds: list[dict], luck: int) -> dict:
    weights = _find_weights(finds, luck)
    population = list(weights)
    rarity = random.choices(population, weights=[weights[key] for key in population], k=1)[0]
    pool = [item for item in finds if item["rarity"] == rarity]
    return random.choice(pool or finds)


def _from_item(fish: dict, luck: int, location_id: str) -> dict:
    weight = random.randint(fish["min_g"], fish["max_g"])
    weight = int(weight * (1 + min(max(luck, 0), 100) / 100 * 0.12))
    packed = _pack(fish, weight)
    packed["chance"] = item_chance(location_id, luck, fish)
    return packed


def item_chance(location_id: str, luck: int, item: dict) -> float:
    finds = finds_for(location_id)
    p_find = find_chance(location_id, luck) if finds else 0.0
    if item.get("kind") == "find":
        weights = _find_weights(finds, luck)
        same = [found for found in finds if found["rarity"] == item["rarity"]]
        return p_find * _share(weights, item["rarity"]) / max(1, len(same))
    weights = _fish_weights(location_id, luck)
    pool = fishes_for(location_id, item["rarity"])
    return (1 - p_find) * _share(weights, item["rarity"]) / max(1, len(pool))


def _share(weights: dict[str, float], rarity: str) -> float:
    total = sum(weights.values())
    if total <= 0:
        return 0.0
    return weights.get(rarity, 0.0) / total


def _fish_weights(location_id: str, luck: int) -> dict[str, float]:
    luck = max(0, min(int(luck), 150))
    available = rarities_in_location(location_id)
    raw = {
        "trash": max(4.0, 26 - luck * 0.30),
        "common": max(18.0, 50 - luck * 0.22),
        "uncommon": 16 + luck * 0.10,
        "rare": 6 + luck * 0.16,
        "epic": 1.8 + luck * 0.08,
        "legendary": 0.45 + luck * 0.035,
        "mythic": 0.06 + luck * 0.008,
    }
    weights = {key: value for key, value in raw.items() if key in available and value > 0}
    return weights or {"common": 1.0}


def _find_weights(finds: list[dict], luck: int) -> dict[str, float]:
    luck = max(0, min(int(luck), 150))
    raw = {
        "trash": 8.0,
        "common": max(8.0, 34 - luck * 0.12),
        "uncommon": 26 + luck * 0.05,
        "rare": 18 + luck * 0.1,
        "epic": 8 + luck * 0.06,
        "legendary": 4 + luck * 0.03,
        "mythic": 1.4 + luck * 0.015,
    }
    available = {item["rarity"] for item in finds}
    weights = {key: value for key, value in raw.items() if key in available and value > 0}
    return weights or {"common": 1.0}


def reaction_bonus(seconds: float) -> tuple[float, str]:
    if seconds <= 1.2:
        return 1.40, "Молниеносная подсечка"
    if seconds <= 2.5:
        return 1.22, "Чёткая подсечка"
    if seconds <= 4.0:
        return 1.10, "Нормальная подсечка"
    return 1.0, "В последний момент"


def apply_reaction(catch: dict, seconds: float) -> dict:
    mult, label = reaction_bonus(seconds)
    fish = FISH_BY_ID[catch["fish_id"]]
    weight = max(1, int(catch["weight"] * mult))
    packed = _pack(fish, weight)
    packed["reaction"] = seconds
    packed["reaction_label"] = label
    packed["trophy"] = weight > fish["max_g"]
    packed["chance"] = catch.get("chance")
    return packed


def did_escape(rarity: str, luck: int) -> bool:
    chance = ESCAPE_CHANCE.get(rarity, 0.1) - max(0, luck) * 0.0018
    if chance <= 0:
        return False
    return random.random() < chance


def new_achievements(stats: dict, unlocked: set[str]) -> list[dict]:
    found = []
    for achievement in ACHIEVEMENTS:
        if achievement["id"] in unlocked:
            continue
        if achievement["ok"](stats):
            found.append(achievement)
    return found


def _pack(fish: dict, weight: int) -> dict:
    rarity = RARITY[fish["rarity"]]
    return {
        "fish_id": fish["id"],
        "name": fish["name"],
        "emoji": fish["emoji"],
        "rarity": fish["rarity"],
        "rarity_name": rarity["name"],
        "rarity_emoji": rarity["emoji"],
        "weight": int(weight),
        "price": calc_price(fish, weight),
        "xp": rarity["xp"],
        "note": fish.get("note"),
        "max_g": fish["max_g"],
        "kind": fish.get("kind", "fish"),
    }


if __name__ == "__main__":
    from collections import Counter

    counts: Counter[str] = Counter()
    for _ in range(20_000):
        counts[roll_catch("pond", 0)["rarity"]] += 1
    print("pond luck 0", dict(counts))
    counts = Counter()
    for _ in range(20_000):
        counts[roll_catch("abyss", 60 + 48 + 26)["rarity"]] += 1
    print("abyss max luck", dict(counts))
    sample = apply_reaction(roll_catch("ocean", 40), 0.8)
    print("sample", sample["name"], sample["weight"], sample["price"], sample["reaction_label"])
    print("rods", len(RODS), "ach", len(ACHIEVEMENTS))
