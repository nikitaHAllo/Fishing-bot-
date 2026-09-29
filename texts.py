"""Тексты сообщений."""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from html import escape

from game import ACHIEVEMENTS
from game_data import (
    BAITS,
    FISH,
    FISH_BY_ID,
    LOCATIONS,
    RARITY_ORDER,
    RODS,
    WAIT_LINES,
    level_from_xp,
    location_index,
    rod_index,
    upgrade_cost,
)


def fmt_int(value: int) -> str:
    return f"{int(value):,}".replace(",", " ")


def fmt_weight(grams: int) -> str:
    grams = int(grams)
    if abs(grams) >= 1000:
        text = f"{grams / 1000:.2f}".replace(".", ",")
        return f"{text} кг"
    return f"{grams} г"


def fmt_seconds(seconds: float) -> str:
    return f"{max(0.0, seconds):.1f}".replace(".", ",") + " с"


def fmt_cooldown(seconds: int) -> str:
    seconds = max(0, int(seconds))
    minutes, secs = divmod(seconds, 60)
    if minutes:
        return f"{minutes} мин {secs} с"
    return f"{secs} с"


def bar(current: int, total: int, width: int = 10) -> str:
    if total <= 0:
        return "░" * width
    filled = max(0, min(width, round(width * current / total)))
    return "█" * filled + "░" * (width - filled)


def short_name(name: str | None) -> str:
    raw = (name or "Рыбак").strip() or "Рыбак"
    if len(raw) > 22:
        raw = raw[:21] + "…"
    return escape(raw)


def achievements_block(items: list[dict]) -> str:
    if not items:
        return ""
    lines = ["", "<b>Достижения</b>"]
    for item in items:
        reward = f" +{fmt_int(item['reward'])} 💰" if item["reward"] else ""
        lines.append(f"🏅 {escape(item['name'])}{reward}")
    return "\n".join(lines)


def welcome(player: dict, chat_link: str | None = None, chat_title: str | None = None) -> str:
    level, into, need = level_from_xp(player["xp"])
    text = (
        "🐟 <b>Клёв</b>\n\n"
        "Текстовая рыбалка. Забрасываешь удочку, ждёшь поклёвку и подсекаешь, пока рыба не ушла.\n\n"
        "🎣 <b>Рыбачить</b> — заброс. Когда клюнет, жми «Подсечь».\n"
        "🎒 Улов лежит в садке, пока не продашь его.\n"
        "📍 Локации открываются с уровнем.\n"
        "🏪 Удочки и наживка повышают удачу.\n\n"
        f"Сейчас ты на {level} уровне. Монет: {fmt_int(player['coins'])} 💰\n"
        f"{bar(into, need)} {into}/{need} XP"
    )
    if chat_link:
        title = escape(chat_title or "общий чат")
        text += f"\n\n🌲 Рыбачить вместе: <a href=\"{escape(chat_link)}\">{title}</a>"
    else:
        text += (
            "\n\n🌲 Общий чат: создай группу, добавь туда бота и напиши /here. "
            "Ссылка на чат появится здесь."
        )
    return text


def group_welcome() -> str:
    return (
        "🐟 <b>Клёв</b>\n\n"
        "Это общий водоём: заброс и улов видны всем в чате.\n"
        "Жми «Рыбачить». Когда клюнет — «Подсечь». Чужую поклёвку взять нельзя.\n"
        "Садок, монеты и удочка у каждого свои."
    )


def help_text() -> str:
    return (
        "<b>Как ловить</b>\n\n"
        "1. Жми «Рыбачить» и жди поклёвку.\n"
        "2. Как только появится кнопка «Подсечь» — жми сразу. Быстрая реакция увеличивает вес.\n"
        "3. Если опоздать или рыба рванёт сильнее снасти, она сорвётся.\n"
        "4. Продай садок и покупай удочки. Старую сдадут со скидкой.\n"
        "5. Наживка тратится на каждую поклёвку, даже если рыба ушла.\n"
        "6. В садке помещается 40 рыб. Дальше надо продавать.\n\n"
        "В общем чате улов виден всем. Свой чат выбирается командой /here.\n\n"
        "Команды: /fish /location /bait /net /inventory /profile /help"
    )


def until_midnight() -> str:
    now = datetime.now()
    tomorrow = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
    left = max(0, int((tomorrow - now).total_seconds()))
    hours, rem = divmod(left, 3600)
    minutes = rem // 60
    if hours:
        return f"{hours} ч {minutes} мин"
    return f"{max(minutes, 1)} мин"


def cast_wait() -> str:
    line = random.choice(WAIT_LINES)
    return f"🎣 <b>Заброс</b>\n{line}\n\nЖдёшь поклёвку…"


def bite_text() -> str:
    return (
        "⚡ <b>Клюёт!</b>\n"
        "Жми «Подсечь» — у тебя около 5 секунд."
    )


def miss_text() -> str:
    return (
        "💨 <b>Ушла.</b>\n"
        "Ты не успел подсечь. Круги на воде уже стихли.\n\n"
        "Кнопка «Рыбачить» снова заработает, когда остынет снасть."
    )


def escape_text(data: dict) -> str:
    lines = [
        "💨 <b>Сорвалась!</b>",
        f"{data['emoji']} {escape(data['name'])} рванула и ушла.",
        f"Редкость: {data['rarity_emoji']} {data['rarity_name']}",
        f"Примерно {fmt_weight(data['weight'])}. Подсечка: {fmt_seconds(data['reaction'])}.",
    ]
    if data.get("bait_empty"):
        lines.append(f"\n{data.get('bait_emoji', '🪱')} Наживка «{escape(data['bait_name'])}» закончилась.")
    return "\n".join(lines)


def linked_name(name: str, url: str | None) -> str:
    safe = escape(name)
    if not url:
        return safe
    return f'<a href="{escape(url, quote=True)}">{safe}</a>'


def catch_text(data: dict, fish_url: str | None = None) -> str:
    title = "находка" if data.get("kind") == "find" else "поклёвка"
    name = linked_name(data["name"], fish_url)
    if not fish_url:
        name = f"<b>{name}</b>"
    lines = [
        f"{data['rarity_emoji']} <b>{data['rarity_name']} {title}</b>",
        "",
        f"{data['emoji']} {name}",
        f"Вес: {fmt_weight(data['weight'])}",
    ]
    if data.get("location_name"):
        lines.append(
            f"📍 {data.get('location_emoji', '')} {escape(data['location_name'])}".strip()
        )
    if data.get("same_count"):
        lines.append(f"В садке теперь: {fmt_int(data['same_count'])} шт.")
    lines += [
        f"В садок: {fmt_int(data['price'])} 💰",
        f"Опыт: +{fmt_int(data['xp'])} XP",
        f"{data['reaction_label']} · {fmt_seconds(data['reaction'])}",
    ]
    chance = data.get("chance")
    if chance:
        percent = f"{chance * 100:.1f}".replace(".", ",")
        lines.append(f"Вероятность этой находки: {percent}%.")
    if data.get("trophy"):
        lines.append("🏆 Трофейный экземпляр — тяжелее обычного.")
    if data.get("record"):
        lines.append("🥇 Новый личный рекорд по весу.")
    if data.get("note"):
        lines.append(f"\n<i>{escape(data['note'])}</i>")
    level = data["level"]
    lines.append(
        f"\n⭐ Уровень {level}  {bar(data['into'], data['need'])}  {data['into']}/{data['need']}"
    )
    if data.get("leveled"):
        lines.append(f"🎉 Новый уровень: <b>{level}</b>")
    for location in data.get("new_locations") or []:
        lines.append(f"📍 Открыто: {location['emoji']} {escape(location['name'])}")
    if data.get("bait_empty"):
        lines.append(f"\nНаживка «{escape(data['bait_name'])}» закончилась.")
    kn = data["keepnet"]
    lines.append(
        f"\n🎒 В садке: {kn['count']} · {fmt_int(kn['value'])} 💰"
    )
    lines.append(achievements_block(data.get("achievements") or []))
    return "\n".join(line for line in lines if line is not None)


def profile_text(snap: dict) -> str:
    player = snap["player"]
    level, into, need = level_from_xp(player["xp"])
    rod = RODS[rod_index(player["rod_id"])]
    location = LOCATIONS[location_index(player["location_id"])]
    bait = snap.get("bait")
    if bait:
        bait_line = f"{bait['emoji']} {bait['name']} ×{snap['bait_qty']}  (+{bait['luck']} удачи)"
    else:
        bait_line = "нет"
    best = "—"
    if player["best_fish_id"] and player["best_weight"]:
        fish = FISH_BY_ID.get(player["best_fish_id"])
        name = fish["name"] if fish else str(player["best_fish_id"])
        best = f"{escape(name)} · {fmt_weight(player['best_weight'])}"
    return (
        f"👤 <b>{short_name(player['first_name'])}</b>\n"
        f"⭐ Уровень {level}  {bar(into, need)}  {into}/{need} XP\n"
        f"💰 {fmt_int(player['coins'])} монет\n"
        f"🎣 {rod['name']}\n"
        f"📍 {location['emoji']} {location['name']}\n"
        f"🪱 Наживка: {bait_line}\n\n"
        f"<b>Статистика</b>\n"
        f"Поймано: {fmt_int(player['catches'])}\n"
        f"Общий вес: {fmt_weight(player['total_weight'])}\n"
        f"Рекорд: {best}\n"
        f"Продано на: {fmt_int(player['earned'])} 💰\n"
        f"Справочник: {snap['unique']}/{len(FISH)}\n"
        f"Достижения: {snap['ach_count']}/{len(ACHIEVEMENTS)}\n"
        f"Место в топе: {snap['place']}"
    )


def top_text(rows: list[dict], place: int, me: dict) -> str:
    lines = ["🏆 <b>Топ рыбаков</b>", ""]
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    if not rows:
        lines.append("Пока тихо. Будь первым.")
    for index, row in enumerate(rows, start=1):
        level = level_from_xp(row["xp"])[0]
        mark = medals.get(index, f"{index}.")
        lines.append(
            f"{mark} {short_name(row['first_name'])} — ур. {level}, "
            f"{fmt_int(row['catches'])} рыб"
        )
    my_level = level_from_xp(me["xp"])[0]
    lines.append(
        f"\nТы: {place} место · ур. {my_level} · {fmt_int(me['catches'])} рыб"
    )
    return "\n".join(lines)


def shop_home(coins: int) -> str:
    return (
        "🏪 <b>Магазин</b>\n\n"
        f"В кармане {fmt_int(coins)} 💰.\n"
        "Удочка остаётся с тобой: при покупке новой старую примут обратно за часть цены.\n"
        "Наживка одноразовая — одна штука на одну поклёвку."
    )


def rods_text(player: dict) -> str:
    current = rod_index(player["rod_id"])
    lines = [
        "🎣 <b>Удочки</b>",
        f"Монеты: {fmt_int(player['coins'])} 💰",
        "",
    ]
    for index, rod in enumerate(RODS):
        mark = " ← твоя" if index == current else ""
        cost = upgrade_cost(player["rod_id"], rod["id"])
        price = "старт" if rod["price"] == 0 else f"{fmt_int(rod['price'])} 💰"
        extra = f", доплата {fmt_int(cost)}" if cost is not None else ""
        lines.append(
            f"<b>{rod['name']}</b>{mark}\n"
            f"{rod['desc']}\n"
            f"Удача +{rod['luck']} · пауза {rod['cooldown']} с · цена {price}{extra}"
        )
    if current == len(RODS) - 1:
        lines.append("\nЛучше этой снасти в лавке нет.")
    return "\n".join(lines)


def bait_text(player: dict, stock: dict[str, int]) -> str:
    lines = [
        "🪱 <b>Наживка</b>",
        f"Монеты: {fmt_int(player['coins'])} 💰",
        "",
    ]
    equipped = player.get("bait_id")
    for bait in BAITS:
        qty = stock.get(bait["id"], 0)
        worn = " · надета" if equipped == bait["id"] else ""
        lines.append(
            f"{bait['emoji']} <b>{bait['name']}</b> — {fmt_int(bait['price'])} 💰, "
            f"+{bait['luck']} удачи, в запасе {qty}{worn}"
        )
    return "\n".join(lines)


def locations_text(player: dict) -> str:
    level = level_from_xp(player["xp"])[0]
    lines = [
        "📍 <b>Куда забросить</b>",
        "Чем дальше вода, тем крупнее и страннее добыча.",
        "",
    ]
    for location in LOCATIONS:
        here = " · ты здесь" if location["id"] == player["location_id"] else ""
        if level < location["level"]:
            lock = f" · с {location['level']} ур."
        else:
            lock = ""
        chance = int(round(float(location.get("find", 0.08)) * 100))
        lines.append(
            f"{location['emoji']} <b>{location['name']}</b>{here}{lock}\n"
            f"{location['desc']} Удача +{location['luck']}. Шанс находки {chance}%."
        )
    return "\n".join(lines)


def dex_text(index: int, records: dict[str, dict]) -> str:
    location = LOCATIONS[index]
    fishes = [fish for fish in FISH if location["id"] in fish["locations"]]
    fishes.sort(key=lambda fish: (RARITY_ORDER.index(fish["rarity"]), fish["name"]))
    opened = sum(1 for fish in fishes if fish["id"] in records)
    lines = [
        f"📖 <b>{location['emoji']} {location['name']}</b>",
        f"Открыто {opened}/{len(fishes)}",
        "",
    ]
    for fish in fishes:
        row = records.get(fish["id"])
        if not row:
            lines.append(f"🔒 {fish['name']}")
            continue
        lines.append(
            f"{fish['emoji']} <b>{escape(fish['name'])}</b> ×{row['count']} · "
            f"рекорд {fmt_weight(row['best_weight'])}"
        )
    return "\n".join(lines)


def keepnet_text(items: list[dict], count: int, total: int) -> str:
    if count == 0:
        return "🎒 <b>Садок пуст.</b>\nЗабрось удочку — сюда сядет улов."
    lines = [f"🎒 <b>Садок</b> · {count} шт. · {fmt_int(total)} 💰", ""]
    shown = items[:15]
    for item in shown:
        lines.append(
            f"{item['emoji']} {escape(item['name'])} — {fmt_weight(item['weight'])} — "
            f"{fmt_int(item['price'])} 💰"
        )
    hidden = count - len(shown)
    if hidden > 0:
        lines.append(f"…и ещё {hidden}")
    return "\n".join(lines)


def sold_text(count: int, money: int, coins: int, achievements: list[dict]) -> str:
    body = (
        f"💰 <b>Продано</b>\n\n"
        f"{count} шт. на {fmt_int(money)} 💰.\n"
        f"Теперь в кармане {fmt_int(coins)} 💰."
    )
    return body + achievements_block(achievements)


def daily_ok(gain: int, coins: int, xp: int, level: int, locations: list[dict], achievements: list[dict]) -> str:
    lines = [
        "🎁 <b>Дневной бонус</b>",
        "",
        f"+{fmt_int(gain)} 💰 и +{xp} XP.",
        f"В кармане {fmt_int(coins)} 💰. Уровень {level}.",
    ]
    for location in locations:
        lines.append(f"📍 Открыто: {location['emoji']} {location['name']}")
    return "\n".join(lines) + achievements_block(achievements)


def net_text(data: dict, fish_url: str | None = None, linked_fish_id: str | None = None) -> str:
    lines = ["🕸️ <b>Сеть поднята</b>"]
    if data.get("location_name"):
        lines.append(
            f"📍 {data.get('location_emoji', '')} {escape(data['location_name'])}".strip()
        )
    lines.append("")
    for item in data["items"]:
        count = item.get("same_count")
        tail = f" · теперь {fmt_int(count)} шт." if count else ""
        url = fish_url if linked_fish_id and item.get("fish_id") == linked_fish_id else None
        lines.append(
            f"{item['emoji']} {linked_name(item['name'], url)} — {fmt_weight(item['weight'])}{tail}"
        )
    gained = sum(item["xp"] for item in data["items"])
    lines.append(f"\nОпыт: +{fmt_int(gained)} XP")
    lines.append(
        f"⭐ Уровень {data['level']}  {bar(data['into'], data['need'])}  {data['into']}/{data['need']}"
    )
    if data.get("leveled"):
        lines.append(f"🎉 Новый уровень: <b>{data['level']}</b>")
    for location in data.get("new_locations") or []:
        lines.append(f"📍 Открыто: {location['emoji']} {escape(location['name'])}")
    kn = data["keepnet"]
    lines.append(f"\n🎒 В садке: {kn['count']} · {fmt_int(kn['value'])} 💰")
    lines.append("Следующая сеть — завтра.")
    lines.append(achievements_block(data.get("achievements") or []))
    return "\n".join(lines)


def net_wait(left: str) -> str:
    return f"🕸️ Сеть уже доставали сегодня.\nСледующий заброс через {left}."


def daily_wait(left: str) -> str:
    return f"🎁 Бонус уже взят сегодня.\nСледующий через {left}."


def cooldown_text(left: int) -> str:
    return f"🎣 Снасть ещё гудит. Следующий заброс через {fmt_cooldown(left)}."


def full_net_text() -> str:
    return "🎒 Садок полон. Продай улов, иначе новая рыба просто не влезет."


def biting_text() -> str:
    return "⚡ Сначала подсеки текущую поклёвку."
