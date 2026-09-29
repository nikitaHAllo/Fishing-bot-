"""Рисует стикер улова и загружает его в набор бота."""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import FSInputFile, InputSticker
from PIL import Image, ImageDraw

from game_data import FISH_BY_ID

log = logging.getLogger("fishing")

ROOT = Path(__file__).resolve().parent
CACHE_PATH = ROOT / "sticker_cache.json"
ART_DIR = ROOT / "stickers"
LOCK = asyncio.Lock()

# Стикеры набора FISH_0bcc9_by_TgEmodziBot для рыб Тихого пруда, по порядку в паке.
POND_PACK = {
    "carp": "CAACAgIAAxUAAWq72T5VOTvUew6z9lZV-XuUHz_dAAIirQAC5gbYSbdxf_l9T_JHPQQ",
    "bleak": "CAACAgIAAxUAAWq72T42cydF2jyAD5LPJasn2OGHAAIlswAC3LnhSaFE4HihMETSPQQ",
    "roach": "CAACAgIAAxUAAWq72T7zH2T8uN0rdwuSER-GjarzAAIspAACk1jYSZYOIN6kiHN6PQQ",
    "perch": "CAACAgIAAxUAAWq72T7ouSoEHthY2MCPFF-bcVzpAALloQACiofgSQXDal0-elqOPQQ",
    "tench": "CAACAgIAAxUAAWq72T7URT9vPaan7JmLZjJiuY4DAALOpwACUq3hSVOehydzVvDCPQQ",
    "pike": "CAACAgIAAxUAAWq72T6sUEYLC7d8TbPVpdcq6OM2AAJvnwAChFfYSfuF-QdbPad2PQQ",
    "gold_crucian": "CAACAgIAAxUAAWq72T4ojNxKfR7nEkarS0RDkdoXAALtpgAC3knhSSHT8_9bb5SdPQQ",
}

PALETTE = (
    (214, 176, 92),
    (168, 178, 188),
    (86, 138, 96),
    (72, 122, 168),
    (196, 112, 74),
    (128, 96, 168),
    (210, 154, 64),
    (64, 150, 156),
    (176, 92, 96),
    (120, 148, 86),
    (98, 118, 150),
    (232, 196, 120),
)


def color_for(fish_id: str) -> tuple[int, int, int]:
    index = sum(ord(char) for char in fish_id) % len(PALETTE)
    return PALETTE[index]


def shape_for(fish: dict) -> str:
    if fish.get("kind") == "find":
        return "item"
    fish_id = fish["id"]
    if "shark" in fish_id:
        return "shark"
    if any(part in fish_id for part in ("eel", "pike", "oar", "viper", "loach", "barracuda")):
        return "long"
    if any(part in fish_id for part in ("flounder", "halibut", "ray", "manta", "moonfish")):
        return "flat"
    if any(part in fish_id for part in ("whale", "leviathan", "kraken", "wels", "catfish")):
        return "big"
    return "fish"


def _mix(color: tuple[int, int, int], other: tuple[int, int, int], amount: float) -> tuple[int, int, int, int]:
    return tuple(int(channel * (1 - amount) + target * amount) for channel, target in zip(color, other)) + (255,)


def render_sticker(fish: dict, path: Path) -> None:
    image = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    color = color_for(fish["id"])
    shape = shape_for(fish)
    if shape == "item":
        _draw_item(draw, fish, color)
    else:
        _draw_fish(draw, color, shape)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, "WEBP", lossless=True)


def _draw_fish(draw: ImageDraw.ImageDraw, color: tuple[int, int, int], shape: str) -> None:
    outline = (36, 48, 58, 255)
    belly = _mix(color, (255, 248, 230), 0.55)
    shade = _mix(color, (20, 30, 40), 0.35)
    body = _mix(color, (255, 255, 255), 0.08)
    if shape == "long":
        torso = (78, 196, 430, 318)
        tail = [(418, 256), (486, 176), (486, 340)]
        eye = (118, 228, 168, 278)
    elif shape == "flat":
        torso = (96, 150, 430, 360)
        tail = [(400, 250), (482, 190), (482, 330)]
        eye = (150, 220, 198, 268)
    elif shape == "big":
        torso = (70, 150, 400, 370)
        tail = [(360, 250), (488, 150), (470, 390)]
        eye = (130, 210, 186, 266)
    elif shape == "shark":
        torso = (70, 188, 430, 330)
        tail = [(400, 255), (488, 170), (470, 300)]
        eye = (128, 220, 172, 264)
    else:
        torso = (92, 168, 400, 348)
        tail = [(378, 256), (478, 168), (478, 348)]
        eye = (138, 214, 196, 272)
    draw.polygon(tail, fill=shade)
    draw.ellipse(torso, fill=body, outline=outline, width=8)
    top = torso[1]
    bottom = torso[3]
    belly_box = (torso[0] + 36, top + (bottom - top) // 2, torso[2] - 30, bottom - 8)
    draw.ellipse(belly_box, fill=belly)
    if shape == "shark":
        draw.polygon([(230, 188), (300, 70), (340, 196)], fill=shade, outline=outline)
    elif shape != "flat":
        fin_top = top + 10
        draw.polygon(
            [(220, fin_top), (280, fin_top - 70), (320, fin_top + 16)],
            fill=shade,
        )
    draw.ellipse(eye, fill=(248, 248, 242, 255), outline=outline, width=4)
    pupil = (eye[0] + 16, eye[1] + 12, eye[2] - 10, eye[3] - 10)
    draw.ellipse(pupil, fill=(28, 32, 38, 255))
    draw.ellipse((pupil[0] + 6, pupil[1] + 4, pupil[0] + 16, pupil[1] + 14), fill=(255, 255, 255, 230))


def _draw_item(draw: ImageDraw.ImageDraw, fish: dict, color: tuple[int, int, int]) -> None:
    fish_id = fish["id"]
    if "chest" in fish_id:
        draw.rounded_rectangle((128, 168, 392, 372), radius=28, fill=(122, 78, 42, 255), outline=(62, 38, 18, 255), width=8)
        draw.rectangle((146, 214, 374, 236), fill=(86, 52, 26, 255))
        draw.ellipse((226, 248, 294, 316), fill=(214, 170, 62, 255), outline=(92, 64, 16, 255), width=4)
        return
    if "crown" in fish_id:
        draw.polygon(
            [(120, 340), (140, 180), (200, 260), (256, 140), (312, 260), (372, 180), (392, 340)],
            fill=(214, 170, 62, 255),
            outline=(92, 64, 16, 255),
        )
        return
    if "pearl" in fish_id or "shard" in fish_id:
        fill = (236, 236, 232, 255) if "black" not in fish_id else (48, 52, 64, 255)
        draw.ellipse((146, 146, 366, 366), fill=fill, outline=(180, 180, 176, 255), width=8)
        draw.ellipse((196, 186, 250, 240), fill=(255, 255, 255, 180))
        return
    if "key" in fish_id:
        draw.ellipse((150, 150, 310, 310), outline=(214, 170, 62, 255), width=18)
        draw.rectangle((280, 214, 390, 246), fill=(214, 170, 62, 255))
        draw.rectangle((350, 246, 378, 300), fill=(214, 170, 62, 255))
        return
    if "compass" in fish_id:
        draw.ellipse((136, 136, 376, 376), fill=(214, 196, 150, 255), outline=(92, 64, 36, 255), width=10)
        draw.polygon([(256, 168), (236, 280), (276, 280)], fill=(176, 64, 64, 255))
        draw.ellipse((240, 264, 272, 296), fill=(48, 48, 48, 255))
        return
    draw.ellipse((156, 156, 356, 356), fill=_mix(color, (255, 220, 120), 0.4), outline=(92, 64, 16, 255), width=8)
    draw.ellipse((196, 186, 246, 236), fill=(255, 248, 220, 180))


def _load() -> dict:
    if not CACHE_PATH.exists():
        return {"owner_id": None, "set_name": "", "files": {}}
    try:
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"owner_id": None, "set_name": "", "files": {}}


def _save(cache: dict) -> None:
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")


def _emoji(fish: dict) -> str:
    emoji = fish.get("emoji") or "🐟"
    if emoji in {"🦁", "🦷", "🏮"}:
        return "🐟"
    return emoji


async def sticker_file_id(bot: Bot, user_id: int, fish_id: str) -> str | None:
    fish = FISH_BY_ID.get(fish_id)
    if fish is None:
        return None
    packed = POND_PACK.get(fish_id)
    if packed:
        return packed
    async with LOCK:
        cache = _load()
        cached = cache.get("files", {}).get(fish_id)
        if cached:
            return cached
        path = ART_DIR / f"{fish_id}.webp"
        render_sticker(fish, path)
        me = await bot.get_me()
        set_name = cache.get("set_name") or f"klev_by_{me.username}"
        owner = int(cache.get("owner_id") or user_id)
        sticker = InputSticker(
            sticker=FSInputFile(path),
            format="static",
            emoji_list=[_emoji(fish)],
        )
        try:
            if cache.get("files"):
                await bot.add_sticker_to_set(user_id=owner, name=set_name, sticker=sticker)
            else:
                await bot.create_new_sticker_set(
                    user_id=owner,
                    name=set_name,
                    title="Клёв",
                    stickers=[sticker],
                    sticker_type="regular",
                    sticker_format="static",
                )
        except TelegramBadRequest as error:
            text = str(error).lower()
            if "already occupied" in text or "name is already" in text:
                await bot.add_sticker_to_set(user_id=owner, name=set_name, sticker=sticker)
            else:
                log.warning("Стикер не загрузился: %s", error)
                return None
        pack = await bot.get_sticker_set(set_name)
        if not pack.stickers:
            return None
        file_id = pack.stickers[-1].file_id
        cache["owner_id"] = owner
        cache["set_name"] = set_name
        cache.setdefault("files", {})[fish_id] = file_id
        _save(cache)
        return file_id
