"""Клавиатуры бота."""

from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from game_data import BAITS, LOCATIONS, RODS, upgrade_cost

BTN_FISH = "🎣 Рыбачить"
BTN_NET = "🎒 Садок"
BTN_SHOP = "🏪 Магазин"
BTN_LOC = "📍 Локация"
BTN_DEX = "📖 Справочник"
BTN_PROFILE = "👤 Профиль"
BTN_TOP = "🏆 Топ"
BTN_DAILY = "🎁 Бонус"


def main_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_FISH)],
            [KeyboardButton(text=BTN_NET), KeyboardButton(text=BTN_SHOP)],
            [KeyboardButton(text=BTN_LOC), KeyboardButton(text=BTN_DEX)],
            [KeyboardButton(text=BTN_PROFILE), KeyboardButton(text=BTN_TOP)],
            [KeyboardButton(text=BTN_DAILY)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def hook_kb(token: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⚡ Подсечь", callback_data=f"h:{token}")]
        ]
    )


def keepnet_kb(total: int, owner_id: int | None = None) -> InlineKeyboardMarkup | None:
    if total <= 0:
        return None
    label = f"Продать всё · {total} 💰"
    if len(label) > 60:
        label = "Продать всё"
    data = f"sell:{owner_id}" if owner_id else "sell:all"
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=label, callback_data=data)]]
    )


def group_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=BTN_FISH, callback_data="go:fish")],
            [
                InlineKeyboardButton(text=BTN_NET, callback_data="go:net"),
                InlineKeyboardButton(text=BTN_SHOP, callback_data="go:shop"),
            ],
            [
                InlineKeyboardButton(text=BTN_LOC, callback_data="go:loc"),
                InlineKeyboardButton(text=BTN_DEX, callback_data="go:dex"),
            ],
            [
                InlineKeyboardButton(text=BTN_PROFILE, callback_data="go:profile"),
                InlineKeyboardButton(text=BTN_TOP, callback_data="go:top"),
            ],
            [InlineKeyboardButton(text="🕸️ Сеть", callback_data="go:haul")],
            [InlineKeyboardButton(text=BTN_DAILY, callback_data="go:bonus")],
        ]
    )


def shop_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎣 Удочки", callback_data="shop:rods")],
            [InlineKeyboardButton(text="🪱 Наживка", callback_data="shop:bait")],
        ]
    )


def rods_kb(rod_id: str) -> InlineKeyboardMarkup:
    rows = []
    for rod in RODS:
        cost = upgrade_cost(rod_id, rod["id"])
        if cost is None:
            continue
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{rod['name']} · {cost} 💰",
                    callback_data=f"rod:{rod['id']}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text="← Назад", callback_data="shop:home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def bait_kb(stock: dict[str, int], equipped: str | None) -> InlineKeyboardMarkup:
    rows = []
    for bait in BAITS:
        qty = stock.get(bait["id"], 0)
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{bait['emoji']} ×1 · {bait['price']}",
                    callback_data=f"bait:{bait['id']}:1",
                ),
                InlineKeyboardButton(
                    text=f"×5 · {bait['price'] * 5}",
                    callback_data=f"bait:{bait['id']}:5",
                ),
            ]
        )
        if qty > 0 and equipped != bait["id"]:
            rows.append(
                [
                    InlineKeyboardButton(
                        text=f"Надеть {bait['name']} ({qty})",
                        callback_data=f"equip:{bait['id']}",
                    )
                ]
            )
    if equipped:
        rows.append(
            [InlineKeyboardButton(text="Снять наживку", callback_data="unequip")]
        )
    rows.append([InlineKeyboardButton(text="← Назад", callback_data="shop:home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def locations_kb(location_id: str, level: int) -> InlineKeyboardMarkup:
    rows = []
    for location in LOCATIONS:
        if location["id"] == location_id:
            mark = "✅ "
        elif level < location["level"]:
            mark = "🔒 "
        else:
            mark = ""
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{mark}{location['emoji']} {location['name']}",
                    callback_data=f"loc:{location['id']}",
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def dex_kb(index: int) -> InlineKeyboardMarkup:
    nav = []
    if index > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"dex:{index - 1}"))
    nav.append(
        InlineKeyboardButton(
            text=f"{index + 1}/{len(LOCATIONS)}",
            callback_data="dex:stay",
        )
    )
    if index < len(LOCATIONS) - 1:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"dex:{index + 1}"))
    return InlineKeyboardMarkup(inline_keyboard=[nav])
