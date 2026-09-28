"""Текстовая рыбалка в Telegram."""

from __future__ import annotations

import asyncio
import logging
import os
import random
import sys
import time
from pathlib import Path

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    BotCommand,
    BotCommandScopeAllGroupChats,
    CallbackQuery,
    ChatMemberUpdated,
    ErrorEvent,
    InlineKeyboardMarkup,
    Message,
)
from dotenv import load_dotenv

from game_data import BITE_DELAY, HOOK_SECONDS, LOCATIONS
from keyboards import (
    BTN_DAILY,
    BTN_DEX,
    BTN_FISH,
    BTN_LOC,
    BTN_NET,
    BTN_PROFILE,
    BTN_SHOP,
    BTN_TOP,
    bait_kb,
    dex_kb,
    group_menu_kb,
    hook_kb,
    keepnet_kb,
    locations_kb,
    main_kb,
    rods_kb,
    shop_kb,
)
from storage import Database, db
import texts

load_dotenv(Path(__file__).resolve().parent / ".env")
TOKEN = os.getenv("BOT_TOKEN", "").strip()

LOG_PATH = Path(__file__).resolve().parent / "bot.log"
_handlers: list[logging.Handler] = [logging.FileHandler(LOG_PATH, encoding="utf-8")]
if sys.stdout is not None:
    _handlers.append(logging.StreamHandler())
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=_handlers,
)
log = logging.getLogger("fishing")

NO_INLINE = InlineKeyboardMarkup(inline_keyboard=[])
TASKS: set[asyncio.Task] = set()

private = Router()
public = Router()
private.message.filter(F.chat.type.in_({"private", "group", "supergroup"}))
private.callback_query.filter(F.message.chat.type.in_({"private", "group", "supergroup"}))


class DbUserMiddleware(BaseMiddleware):
    def __init__(self, database: Database):
        self.database = database

    async def __call__(self, handler, event, data):
        data["db"] = self.database
        user = getattr(event, "from_user", None)
        if user is not None and not user.is_bot:
            data["player"] = await self.database.get_or_create(
                user.id,
                user.username,
                user.first_name,
            )
        return await handler(event, data)


def spawn(coro) -> None:
    task = asyncio.create_task(coro)
    TASKS.add(task)
    task.add_done_callback(TASKS.discard)


def who(player: dict | None, chat_type: str) -> str:
    if not player or chat_type == "private":
        return ""
    return f"👤 <b>{texts.short_name(player.get('first_name'))}</b>\n"


def cast_error(started: dict) -> str:
    error = started["error"]
    if error == "full":
        return texts.full_net_text()
    if error == "biting":
        return texts.biting_text()
    return texts.cooldown_text(started.get("left", 1))


async def begin_fishing(bot: Bot, chat_id: int, user_id: int, header: str) -> str | None:
    started = await db.begin_cast(user_id, time.time())
    if not started["ok"]:
        return cast_error(started)
    sent = await bot.send_message(chat_id, header + texts.cast_wait())
    await db.attach_bite(user_id, started["token"], sent.chat.id, sent.message_id)
    spawn(bite_job(bot, user_id, started["token"], sent.chat.id, sent.message_id, header))
    return None


async def remember_chat(bot: Bot, chat) -> str:
    link = f"https://t.me/{chat.username}" if chat.username else ""
    if not link:
        try:
            invite = await bot.create_chat_invite_link(chat.id, name="Клёв")
            link = invite.invite_link
        except TelegramBadRequest:
            log.info("Не удалось создать ссылку на чат %s", chat.id)
    await db.save_fishing_chat(chat.id, chat.title or "Чат рыбаков", link)
    return link


async def bite_job(
    bot: Bot,
    user_id: int,
    token: str,
    chat_id: int,
    message_id: int,
    header: str = "",
) -> None:
    try:
        await asyncio.sleep(random.uniform(*BITE_DELAY))
        if await db.mark_biting(user_id, token, time.time()):
            try:
                await bot.edit_message_text(
                    header + texts.bite_text(),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=hook_kb(token),
                )
            except TelegramBadRequest:
                log.info("Не удалось показать поклёвку, user=%s", user_id)
            await asyncio.sleep(HOOK_SECONDS)
    except Exception:
        log.exception("Ошибка поклёвки user=%s", user_id)
    try:
        if not await db.resolve_miss(user_id, token):
            return
        await bot.edit_message_text(
            header + texts.miss_text(),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=NO_INLINE,
        )
    except TelegramBadRequest:
        pass
    except Exception:
        log.exception("Не удалось закрыть поклёвку user=%s", user_id)


async def on_error(event: ErrorEvent) -> None:
    log.error("Сбой обработчика", exc_info=event.exception)
    update = event.update
    try:
        if update.message:
            await update.message.answer("Что-то пошло не так. Попробуй ещё раз.")
        elif update.callback_query:
            await update.callback_query.answer("Не вышло, попробуй ещё раз", show_alert=True)
    except Exception:
        log.debug("Не удалось сообщить об ошибке пользователю")


@public.my_chat_member()
async def on_bot_status(event: ChatMemberUpdated, bot: Bot) -> None:
    chat = event.chat
    if chat.type not in ("group", "supergroup"):
        return
    status = str(event.new_chat_member.status)
    if status in ("member", "administrator", "restricted"):
        link = await remember_chat(bot, chat)
        text = texts.group_welcome()
        if not link:
            text += (
                "\n\nЧтобы ссылка появилась в личке, сделай группу публичной "
                "или назначь бота админом с правом приглашать. Потом напиши /here."
            )
        await bot.send_message(chat.id, text, reply_markup=group_menu_kb())
        return
    if status in ("left", "kicked"):
        current = await db.fishing_chat()
        if current and str(current.get("chat_id")) == str(chat.id):
            await db.clear_fishing_chat()


@private.message(CommandStart())
async def start(message: Message, player: dict, db: Database) -> None:
    if message.chat.type == "private":
        chat = await db.fishing_chat()
        link = (chat or {}).get("chat_link") or None
        title = (chat or {}).get("chat_title") or None
        await message.answer(texts.welcome(player, link, title), reply_markup=main_kb())
        return
    await message.answer(texts.group_welcome(), reply_markup=group_menu_kb())


@private.message(Command("here"))
async def set_here(message: Message, bot: Bot) -> None:
    if message.chat.type == "private":
        await message.answer("Команду /here пиши в группе, где все будут рыбачить.")
        return
    link = await remember_chat(bot, message.chat)
    text = "Этот чат теперь общий водоём. Открой бота в личке — там будет ссылка."
    if not link:
        text += " Ссылку не вышло создать: сделай группу публичной или дай боту право приглашать."
    await message.answer(text, reply_markup=group_menu_kb())


@private.message(Command("help"))
async def help_cmd(message: Message) -> None:
    markup = main_kb() if message.chat.type == "private" else group_menu_kb()
    await message.answer(texts.help_text(), reply_markup=markup)


@private.message(Command("fish"))
@private.message(F.text == BTN_FISH)
async def fish(message: Message, player: dict) -> None:
    header = who(player, message.chat.type)
    error = await begin_fishing(message.bot, message.chat.id, message.from_user.id, header)
    if error:
        await message.answer(header + error)


@private.callback_query(F.data.startswith("h:"))
async def hook(cb: CallbackQuery, player: dict, db: Database) -> None:
    result = await db.resolve_hook(cb.from_user.id, cb.data[2:], time.time())
    if result is None:
        await cb.answer("Это не твоя поклёвка или она уже прошла", show_alert=True)
        return
    header = who(player, cb.message.chat.type)
    if result["escaped"]:
        await cb.answer("Сорвалась")
        await cb.message.edit_text(header + texts.escape_text(result), reply_markup=NO_INLINE)
        return
    await cb.answer("Есть")
    await cb.message.edit_text(header + texts.catch_text(result), reply_markup=NO_INLINE)


@private.message(F.text == BTN_NET)
async def keepnet(message: Message, db: Database) -> None:
    view = await db.keepnet_view(message.from_user.id)
    await message.answer(
        texts.keepnet_text(view["items"], view["count"], view["total"]),
        reply_markup=keepnet_kb(view["total"], message.from_user.id),
    )


async def answer_sold(target: Message, db: Database, user_id: int, edit: bool) -> None:
    result = await db.sell_all(user_id)
    if not result["ok"]:
        if edit:
            return
        await target.answer("Садок пуст.")
        return
    text = texts.sold_text(
        result["count"],
        result["money"],
        result["coins"],
        result["achievements"],
    )
    if edit:
        await target.edit_text(text, reply_markup=NO_INLINE)
    else:
        await target.answer(text)


@private.callback_query(F.data.startswith("sell:"))
async def sell_callback(cb: CallbackQuery, db: Database) -> None:
    owner_raw = cb.data.split(":", 1)[1]
    if owner_raw != "all":
        try:
            owner_id = int(owner_raw)
        except ValueError:
            await cb.answer()
            return
        if owner_id != cb.from_user.id:
            await cb.answer("Это чужой садок. Открой свой кнопкой «Садок».", show_alert=True)
            return
    result = await db.sell_all(cb.from_user.id)
    if not result["ok"]:
        await cb.answer("Садок уже пуст", show_alert=True)
        return
    await cb.answer("Продано")
    await cb.message.edit_text(
        texts.sold_text(result["count"], result["money"], result["coins"], result["achievements"]),
        reply_markup=NO_INLINE,
    )


@private.message(Command("sell"))
async def sell_cmd(message: Message, db: Database) -> None:
    await answer_sold(message, db, message.from_user.id, edit=False)


@private.message(F.text == BTN_SHOP)
async def shop(message: Message, player: dict) -> None:
    await message.answer(texts.shop_home(player["coins"]), reply_markup=shop_kb())


@private.callback_query(F.data == "shop:home")
async def shop_home(cb: CallbackQuery, player: dict) -> None:
    await cb.answer()
    await cb.message.edit_text(texts.shop_home(player["coins"]), reply_markup=shop_kb())


@private.callback_query(F.data == "shop:rods")
async def shop_rods(cb: CallbackQuery, player: dict) -> None:
    await cb.answer()
    await cb.message.edit_text(texts.rods_text(player), reply_markup=rods_kb(player["rod_id"]))


@private.callback_query(F.data.startswith("rod:"))
async def buy_rod(cb: CallbackQuery, db: Database) -> None:
    result = await db.buy_rod(cb.from_user.id, cb.data.split(":", 1)[1])
    if not result["ok"]:
        if result["error"] == "money":
            await cb.answer(
                f"Не хватает монет. Нужно {result['cost']}, есть {result['coins']}.",
                show_alert=True,
            )
        elif result["error"] == "worse":
            await cb.answer("Эта удочка не лучше твоей.", show_alert=True)
        else:
            await cb.answer("Нет такой удочки.", show_alert=True)
        return
    player = result["player"]
    await cb.answer("Удочка твоя")
    await cb.message.edit_text(
        texts.rods_text(player) + texts.achievements_block(result["achievements"]),
        reply_markup=rods_kb(player["rod_id"]),
    )


@private.callback_query(F.data == "shop:bait")
async def shop_bait(cb: CallbackQuery, db: Database, player: dict) -> None:
    stock = await db.bait_stock(cb.from_user.id)
    await cb.answer()
    await cb.message.edit_text(
        texts.bait_text(player, stock),
        reply_markup=bait_kb(stock, player["bait_id"]),
    )


@private.callback_query(F.data.startswith("bait:"))
async def buy_bait(cb: CallbackQuery, db: Database) -> None:
    parts = cb.data.split(":")
    if len(parts) != 3:
        await cb.answer()
        return
    try:
        count = int(parts[2])
    except ValueError:
        await cb.answer()
        return
    result = await db.buy_bait(cb.from_user.id, parts[1], count)
    if not result["ok"]:
        if result["error"] == "money":
            await cb.answer(
                f"Не хватает монет. Нужно {result['cost']}, есть {result['coins']}.",
                show_alert=True,
            )
        else:
            await cb.answer("Нет такой наживки.", show_alert=True)
        return
    player = result["player"]
    await cb.answer("Наживка в кармане")
    await cb.message.edit_text(
        texts.bait_text(player, result["stock"]) + texts.achievements_block(result["achievements"]),
        reply_markup=bait_kb(result["stock"], player["bait_id"]),
    )


@private.callback_query(F.data.startswith("equip:"))
async def equip(cb: CallbackQuery, db: Database) -> None:
    result = await db.equip_bait(cb.from_user.id, cb.data.split(":", 1)[1])
    if not result["ok"]:
        messages = {
            "empty": "Этой наживки нет в запасе.",
            "already": "Уже надета.",
            "missing": "Нет такой наживки.",
        }
        await cb.answer(messages.get(result["error"], "Не вышло."), show_alert=True)
        return
    player = result["player"]
    await cb.answer("Наживка надета")
    await cb.message.edit_text(
        texts.bait_text(player, result["stock"]),
        reply_markup=bait_kb(result["stock"], player["bait_id"]),
    )


@private.callback_query(F.data == "unequip")
async def unequip(cb: CallbackQuery, db: Database) -> None:
    result = await db.unequip_bait(cb.from_user.id)
    player = result["player"]
    await cb.answer("Снял")
    await cb.message.edit_text(
        texts.bait_text(player, result["stock"]),
        reply_markup=bait_kb(result["stock"], player["bait_id"]),
    )


@private.message(F.text == BTN_LOC)
async def locations(message: Message, player: dict) -> None:
    level = texts.level_from_xp(player["xp"])[0]
    await message.answer(
        texts.locations_text(player),
        reply_markup=locations_kb(player["location_id"], level),
    )


@private.callback_query(F.data.startswith("loc:"))
async def choose_location(cb: CallbackQuery, db: Database) -> None:
    result = await db.set_location(cb.from_user.id, cb.data.split(":", 1)[1])
    if not result["ok"]:
        if result["error"] == "locked":
            await cb.answer(f"Нужен {result['level']} уровень.", show_alert=True)
        elif result["error"] == "same":
            await cb.answer("Ты уже здесь")
        else:
            await cb.answer("Нет такой воды", show_alert=True)
        return
    player = result["player"]
    level = texts.level_from_xp(player["xp"])[0]
    await cb.answer(f"Теперь: {result['name']}")
    await cb.message.edit_text(
        texts.locations_text(player) + texts.achievements_block(result["achievements"]),
        reply_markup=locations_kb(player["location_id"], level),
    )


@private.message(F.text == BTN_DEX)
async def dex(message: Message, db: Database) -> None:
    records = await db.bestiary(message.from_user.id)
    await message.answer(texts.dex_text(0, records), reply_markup=dex_kb(0))


@private.callback_query(F.data.startswith("dex:"))
async def dex_page(cb: CallbackQuery, db: Database) -> None:
    raw = cb.data.split(":", 1)[1]
    if raw == "stay":
        await cb.answer()
        return
    try:
        index = int(raw)
    except ValueError:
        await cb.answer()
        return
    if index < 0 or index >= len(LOCATIONS):
        await cb.answer()
        return
    records = await db.bestiary(cb.from_user.id)
    await cb.answer()
    await cb.message.edit_text(texts.dex_text(index, records), reply_markup=dex_kb(index))


@private.message(Command("profile"))
@private.message(F.text == BTN_PROFILE)
async def profile(message: Message, db: Database) -> None:
    snap = await db.snapshot(message.from_user.id)
    await message.answer(texts.profile_text(snap))


@private.message(Command("top"))
@private.message(F.text == BTN_TOP)
async def top(message: Message, db: Database) -> None:
    board = await db.leaderboard(message.from_user.id)
    await message.answer(texts.top_text(board["rows"], board["place"], board["me"]))


@private.message(Command("bonus"))
@private.message(F.text == BTN_DAILY)
async def daily(message: Message, db: Database) -> None:
    result = await db.claim_daily(message.from_user.id)
    if not result["ok"]:
        await message.answer(texts.daily_wait(texts.until_midnight()))
        return
    await message.answer(
        texts.daily_ok(
            result["gain"],
            result["coins"],
            result["xp"],
            result["level"],
            result["locations"],
            result["achievements"],
        )
    )


@private.callback_query(F.data.startswith("go:"))
async def menu_action(cb: CallbackQuery, player: dict, db: Database) -> None:
    action = cb.data.split(":", 1)[1]
    header = who(player, cb.message.chat.type)
    if action == "fish":
        error = await begin_fishing(cb.bot, cb.message.chat.id, cb.from_user.id, header)
        if error:
            await cb.answer(error.replace("<b>", "").replace("</b>", ""), show_alert=True)
            return
        await cb.answer("Заброс")
        return
    await cb.answer()
    if action == "net":
        view = await db.keepnet_view(cb.from_user.id)
        await cb.message.answer(
            header + texts.keepnet_text(view["items"], view["count"], view["total"]),
            reply_markup=keepnet_kb(view["total"], cb.from_user.id),
        )
    elif action == "shop":
        await cb.message.answer(header + texts.shop_home(player["coins"]), reply_markup=shop_kb())
    elif action == "loc":
        level = texts.level_from_xp(player["xp"])[0]
        await cb.message.answer(
            header + texts.locations_text(player),
            reply_markup=locations_kb(player["location_id"], level),
        )
    elif action == "dex":
        records = await db.bestiary(cb.from_user.id)
        await cb.message.answer(header + texts.dex_text(0, records), reply_markup=dex_kb(0))
    elif action == "profile":
        snap = await db.snapshot(cb.from_user.id)
        await cb.message.answer(texts.profile_text(snap))
    elif action == "top":
        board = await db.leaderboard(cb.from_user.id)
        await cb.message.answer(texts.top_text(board["rows"], board["place"], board["me"]))
    elif action == "bonus":
        result = await db.claim_daily(cb.from_user.id)
        if not result["ok"]:
            await cb.message.answer(header + texts.daily_wait(texts.until_midnight()))
            return
        await cb.message.answer(
            header
            + texts.daily_ok(
                result["gain"],
                result["coins"],
                result["xp"],
                result["level"],
                result["locations"],
                result["achievements"],
            )
        )


@private.message()
async def fallback(message: Message) -> None:
    if message.chat.type != "private":
        return
    await message.answer("Жми кнопки под полем ввода. Если их не видно — отправь /start.")


@private.callback_query()
async def callback_fallback(cb: CallbackQuery) -> None:
    await cb.answer()


@public.error()
@private.error()
async def error_event(event: ErrorEvent) -> None:
    await on_error(event)


async def main() -> None:
    if not TOKEN or "сюда" in TOKEN or TOKEN == "сюда_токен_от_BotFather":
        raise SystemExit(
            "В файле .env нет токена. Скопируй .env.example в .env и вставь токен от @BotFather."
        )
    await db.init()
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(public)
    dp.include_router(private)
    middleware = DbUserMiddleware(db)
    private.message.middleware(middleware)
    private.callback_query.middleware(middleware)
    commands = [
        BotCommand(command="start", description="Начать рыбалку"),
        BotCommand(command="fish", description="Забросить удочку"),
        BotCommand(command="profile", description="Профиль"),
        BotCommand(command="top", description="Топ рыбаков"),
        BotCommand(command="sell", description="Продать садок"),
        BotCommand(command="bonus", description="Ежедневный бонус"),
        BotCommand(command="here", description="Сделать этот чат общим"),
        BotCommand(command="help", description="Как играть"),
    ]
    await bot.set_my_commands(commands)
    await bot.set_my_commands(commands, scope=BotCommandScopeAllGroupChats())
    log.info("Бот запущен")
    allowed = list(dp.resolve_used_update_types())
    if "my_chat_member" not in allowed:
        allowed.append("my_chat_member")
    try:
        await dp.start_polling(bot, allowed_updates=allowed)
    finally:
        await db.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
