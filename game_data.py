"""Статичные данные рыбалки: локации, снасти, рыба."""

from __future__ import annotations

RARITY_ORDER = (
    "trash",
    "common",
    "uncommon",
    "rare",
    "epic",
    "legendary",
    "mythic",
)

# name, emoji, price multiplier, xp
RARITY = {
    "trash": {"name": "Мусор", "emoji": "🗑️", "price_mult": 0.35, "xp": 1},
    "common": {"name": "Обычная", "emoji": "🐟", "price_mult": 1.0, "xp": 6},
    "uncommon": {"name": "Необычная", "emoji": "🐠", "price_mult": 1.7, "xp": 14},
    "rare": {"name": "Редкая", "emoji": "✨", "price_mult": 3.2, "xp": 32},
    "epic": {"name": "Эпическая", "emoji": "💠", "price_mult": 6.5, "xp": 75},
    "legendary": {"name": "Легендарная", "emoji": "👑", "price_mult": 14.0, "xp": 170},
    "mythic": {"name": "Мифическая", "emoji": "🔮", "price_mult": 32.0, "xp": 420},
}

ESCAPE_CHANCE = {
    "trash": 0.0,
    "common": 0.04,
    "uncommon": 0.07,
    "rare": 0.11,
    "epic": 0.17,
    "legendary": 0.24,
    "mythic": 0.32,
}

KEEPNET_LIMIT = 40
HOOK_SECONDS = 5.5
BITE_DELAY = (1.4, 3.4)
ROD_REFUND = 0.35

LOCATIONS = [
    {
        "id": "pond",
        "name": "Тихий пруд",
        "emoji": "🌿",
        "level": 1,
        "luck": 0,
        "find": 0.08,
        "desc": "Ряска, комары и мелочь у берега.",
    },
    {
        "id": "river",
        "name": "Лесная река",
        "emoji": "🏞️",
        "level": 3,
        "luck": 4,
        "find": 0.09,
        "desc": "Течение тащит наживку под коряги.",
    },
    {
        "id": "swamp",
        "name": "Тёмное болото",
        "emoji": "🐸",
        "level": 4,
        "luck": 5,
        "find": 0.12,
        "desc": "Тишина, ряска и редкие всплески.",
    },
    {
        "id": "lake",
        "name": "Большое озеро",
        "emoji": "🌊",
        "level": 6,
        "luck": 8,
        "find": 0.10,
        "desc": "Глубокие ямы и утренний туман.",
    },
    {
        "id": "quarry",
        "name": "Каменный карьер",
        "emoji": "🪨",
        "level": 8,
        "luck": 10,
        "find": 0.14,
        "desc": "Прозрачная холодная вода между скал.",
    },
    {
        "id": "sea",
        "name": "Тёплое море",
        "emoji": "🏖️",
        "level": 10,
        "luck": 12,
        "find": 0.11,
        "desc": "Соль на губах и стаи у поверхности.",
    },
    {
        "id": "pier",
        "name": "Ночной причал",
        "emoji": "🌃",
        "level": 13,
        "luck": 14,
        "find": 0.15,
        "desc": "Фонари, свайный лес и ночная мелочь.",
    },
    {
        "id": "ocean",
        "name": "Открытый океан",
        "emoji": "🌐",
        "level": 16,
        "luck": 18,
        "find": 0.13,
        "desc": "Дна не видно. Клюёт то, что крупнее лодки.",
    },
    {
        "id": "reef",
        "name": "Коралловый риф",
        "emoji": "🪸",
        "level": 19,
        "luck": 20,
        "find": 0.16,
        "desc": "Цветная вода и узкие щели между кораллами.",
    },
    {
        "id": "wreck",
        "name": "Кладбище кораблей",
        "emoji": "🚢",
        "level": 22,
        "luck": 23,
        "find": 0.22,
        "desc": "Мачты торчат из воды. Здесь чаще находят, чем ловят.",
    },
    {
        "id": "abyss",
        "name": "Бездна",
        "emoji": "🌑",
        "level": 24,
        "luck": 26,
        "find": 0.18,
        "desc": "Темнота, давление и очень старые глаза.",
    },
    {
        "id": "moon",
        "name": "Лунная бухта",
        "emoji": "🌙",
        "level": 32,
        "luck": 34,
        "find": 0.2,
        "desc": "Вода светится. Рыба здесь будто из серебра.",
    },
]

RODS = [
    {
        "id": "bamboo",
        "name": "Бамбуковая удочка",
        "price": 0,
        "luck": 0,
        "cooldown": 28,
        "desc": "Палка, леска и надежда.",
    },
    {
        "id": "spin",
        "name": "Спиннинг",
        "price": 450,
        "luck": 8,
        "cooldown": 24,
        "desc": "Нормальная снасть для нормальной рыбы.",
    },
    {
        "id": "carbon",
        "name": "Карбоновое удилище",
        "price": 2_000,
        "luck": 16,
        "cooldown": 20,
        "desc": "Лёгкое, звонкое, уже не стыдно.",
    },
    {
        "id": "pro",
        "name": "Профи-комплект",
        "price": 8_000,
        "luck": 28,
        "cooldown": 16,
        "desc": "Катушка мурлычет, фрикцион держит.",
    },
    {
        "id": "legend",
        "name": "Легендарный спиннинг",
        "price": 32_000,
        "luck": 42,
        "cooldown": 13,
        "desc": "Им ловили байки. Теперь ловишь ты.",
    },
    {
        "id": "abyss",
        "name": "Удочка бездны",
        "price": 140_000,
        "luck": 60,
        "cooldown": 11,
        "desc": "Леска темнее воды. Крючок тёплый.",
    },
]

BAITS = [
    {"id": "bread", "name": "Хлеб", "emoji": "🍞", "price": 15, "luck": 4},
    {"id": "worm", "name": "Червь", "emoji": "🪱", "price": 40, "luck": 10},
    {"id": "maggot", "name": "Опарыш", "emoji": "🐛", "price": 90, "luck": 18},
    {"id": "shrimp", "name": "Креветка", "emoji": "🦐", "price": 220, "luck": 30},
    {"id": "gold", "name": "Золотая наживка", "emoji": "✨", "price": 700, "luck": 48},
]

FISH = [
    {"id": "boot", "name": "Старый сапог", "emoji": "👢", "rarity": "trash", "locations": ("pond", "river", "lake"), "min_g": 180, "max_g": 900, "price": 3, "note": "Пахнет приключением и тиной."},
    {"id": "can", "name": "Жестяная банка", "emoji": "🥫", "rarity": "trash", "locations": ("pond", "river"), "min_g": 40, "max_g": 250, "price": 4},
    {"id": "branch", "name": "Мокрая ветка", "emoji": "🪵", "rarity": "trash", "locations": ("pond", "lake"), "min_g": 80, "max_g": 600, "price": 2},
    {"id": "sea_boot", "name": "Резиновый сапог", "emoji": "🥾", "rarity": "trash", "locations": ("sea", "ocean"), "min_g": 200, "max_g": 1100, "price": 3},
    {"id": "debris", "name": "Обломок корпуса", "emoji": "⚙️", "rarity": "trash", "locations": ("abyss",), "min_g": 300, "max_g": 2500, "price": 6, "note": "На металле царапины от зубов."},
    {"id": "coin", "name": "Старинная монета", "emoji": "🪙", "rarity": "rare", "locations": ("pond", "river", "lake", "sea", "ocean", "abyss"), "min_g": 8, "max_g": 40, "price": 1400, "note": "На ребре ещё читается чужой герб."},
    {"id": "bottle", "name": "Бутылка с запиской", "emoji": "🍾", "rarity": "uncommon", "locations": ("pond", "river", "sea"), "min_g": 200, "max_g": 700, "price": 28, "note": "Записка размыта. Видно только слово «клюёт»."},
    {"id": "crucian", "name": "Карась", "emoji": "🐟", "rarity": "common", "locations": ("pond",), "min_g": 80, "max_g": 1200, "price": 12},
    {"id": "roach", "name": "Плотва", "emoji": "🐟", "rarity": "common", "locations": ("pond", "river"), "min_g": 40, "max_g": 500, "price": 10},
    {"id": "bleak", "name": "Уклейка", "emoji": "🐟", "rarity": "common", "locations": ("pond",), "min_g": 15, "max_g": 80, "price": 14},
    {"id": "perch", "name": "Окунь", "emoji": "🐠", "rarity": "uncommon", "locations": ("pond", "lake"), "min_g": 80, "max_g": 1800, "price": 16},
    {"id": "tench", "name": "Линь", "emoji": "🐠", "rarity": "uncommon", "locations": ("pond",), "min_g": 200, "max_g": 3000, "price": 15},
    {"id": "carp", "name": "Карп", "emoji": "🐡", "rarity": "rare", "locations": ("pond", "lake"), "min_g": 400, "max_g": 9000, "price": 18},
    {"id": "pike", "name": "Щука", "emoji": "🐊", "rarity": "epic", "locations": ("pond", "lake"), "min_g": 600, "max_g": 12000, "price": 22, "note": "Зубы чиркнули по поводку."},
    {"id": "gold_crucian", "name": "Золотой карась", "emoji": "🌟", "rarity": "epic", "locations": ("pond",), "min_g": 150, "max_g": 900, "price": 80, "note": "Чешуя блестит, как монета."},
    {"id": "gudgeon", "name": "Пескарь", "emoji": "🐟", "rarity": "common", "locations": ("river",), "min_g": 15, "max_g": 90, "price": 11},
    {"id": "chub", "name": "Голавль", "emoji": "🐟", "rarity": "common", "locations": ("river",), "min_g": 150, "max_g": 2500, "price": 13},
    {"id": "dace", "name": "Елец", "emoji": "🐟", "rarity": "common", "locations": ("river",), "min_g": 30, "max_g": 250, "price": 11},
    {"id": "ide", "name": "Язь", "emoji": "🐠", "rarity": "uncommon", "locations": ("river",), "min_g": 250, "max_g": 4000, "price": 16},
    {"id": "asp", "name": "Жерех", "emoji": "🐠", "rarity": "uncommon", "locations": ("river",), "min_g": 400, "max_g": 6000, "price": 18},
    {"id": "zander", "name": "Судак", "emoji": "🐡", "rarity": "rare", "locations": ("river", "lake"), "min_g": 500, "max_g": 10000, "price": 20},
    {"id": "catfish", "name": "Сом", "emoji": "💠", "rarity": "epic", "locations": ("river", "lake"), "min_g": 2000, "max_g": 45000, "price": 10, "note": "Усы толще пальца."},
    {"id": "taimen", "name": "Таймень", "emoji": "👑", "rarity": "legendary", "locations": ("river",), "min_g": 4000, "max_g": 40000, "price": 28, "note": "Река на миг стала тише."},
    {"id": "bream", "name": "Лещ", "emoji": "🐟", "rarity": "common", "locations": ("lake",), "min_g": 200, "max_g": 3500, "price": 12},
    {"id": "silver_bream", "name": "Густера", "emoji": "🐟", "rarity": "common", "locations": ("lake",), "min_g": 80, "max_g": 800, "price": 11},
    {"id": "ruff", "name": "Ёрш", "emoji": "🐟", "rarity": "common", "locations": ("lake",), "min_g": 20, "max_g": 200, "price": 9},
    {"id": "burbot", "name": "Налим", "emoji": "🐠", "rarity": "uncommon", "locations": ("lake", "abyss"), "min_g": 300, "max_g": 5000, "price": 17},
    {"id": "wels", "name": "Сом-великан", "emoji": "💠", "rarity": "epic", "locations": ("lake",), "min_g": 8000, "max_g": 70000, "price": 9},
    {"id": "gold_bream", "name": "Золотой лещ", "emoji": "👑", "rarity": "legendary", "locations": ("lake",), "min_g": 1500, "max_g": 8000, "price": 55, "note": "В тумане он светился сам."},
    {"id": "herring", "name": "Сельдь", "emoji": "🐟", "rarity": "common", "locations": ("sea",), "min_g": 80, "max_g": 500, "price": 12},
    {"id": "sardine", "name": "Сардина", "emoji": "🐟", "rarity": "common", "locations": ("sea",), "min_g": 30, "max_g": 180, "price": 13},
    {"id": "scad", "name": "Ставрида", "emoji": "🐟", "rarity": "common", "locations": ("sea",), "min_g": 80, "max_g": 700, "price": 13},
    {"id": "mackerel", "name": "Скумбрия", "emoji": "🐠", "rarity": "uncommon", "locations": ("sea",), "min_g": 200, "max_g": 2000, "price": 16},
    {"id": "flounder", "name": "Камбала", "emoji": "🐠", "rarity": "uncommon", "locations": ("sea",), "min_g": 250, "max_g": 4000, "price": 17},
    {"id": "cod", "name": "Треска", "emoji": "🐡", "rarity": "rare", "locations": ("sea", "ocean"), "min_g": 800, "max_g": 20000, "price": 14},
    {"id": "tuna", "name": "Тунец", "emoji": "🐡", "rarity": "rare", "locations": ("sea", "ocean"), "min_g": 4000, "max_g": 80000, "price": 11},
    {"id": "swordfish", "name": "Меч-рыба", "emoji": "💠", "rarity": "epic", "locations": ("sea", "ocean"), "min_g": 15000, "max_g": 120000, "price": 8, "note": "Клюв чиркнул по борту."},
    {"id": "marlin", "name": "Марлин", "emoji": "👑", "rarity": "legendary", "locations": ("sea",), "min_g": 30000, "max_g": 250000, "price": 7},
    {"id": "gold_mackerel", "name": "Золотая макрель", "emoji": "🔮", "rarity": "mythic", "locations": ("sea",), "min_g": 2000, "max_g": 18000, "price": 40, "note": "За ней тянется тёплая искра."},
    {"id": "anchovy", "name": "Анчоус", "emoji": "🐟", "rarity": "common", "locations": ("ocean",), "min_g": 10, "max_g": 60, "price": 15},
    {"id": "saury", "name": "Сайра", "emoji": "🐟", "rarity": "common", "locations": ("ocean",), "min_g": 40, "max_g": 250, "price": 13},
    {"id": "dorado", "name": "Дорадо", "emoji": "🐠", "rarity": "uncommon", "locations": ("ocean",), "min_g": 400, "max_g": 5000, "price": 20},
    {"id": "snapper", "name": "Луциан", "emoji": "🐠", "rarity": "uncommon", "locations": ("ocean",), "min_g": 500, "max_g": 8000, "price": 18},
    {"id": "halibut", "name": "Палтус", "emoji": "🐡", "rarity": "rare", "locations": ("ocean",), "min_g": 2000, "max_g": 50000, "price": 12},
    {"id": "shark", "name": "Акула", "emoji": "🦈", "rarity": "epic", "locations": ("ocean",), "min_g": 20000, "max_g": 280000, "price": 6, "note": "Леска поёт, как струна."},
    {"id": "blue_marlin", "name": "Синий марлин", "emoji": "👑", "rarity": "legendary", "locations": ("ocean",), "min_g": 50000, "max_g": 450000, "price": 6},
    {"id": "oarfish", "name": "Сельдяной король", "emoji": "👑", "rarity": "legendary", "locations": ("ocean", "abyss"), "min_g": 8000, "max_g": 90000, "price": 16, "note": "Длинный, как причал."},
    {"id": "moonfish", "name": "Лунная рыба", "emoji": "🔮", "rarity": "mythic", "locations": ("ocean",), "min_g": 20000, "max_g": 200000, "price": 14, "note": "Бок круглый и холодный, как луна."},
    {"id": "eel", "name": "Глубоководный угорь", "emoji": "🐍", "rarity": "uncommon", "locations": ("abyss",), "min_g": 400, "max_g": 6000, "price": 22},
    {"id": "angler", "name": "Удильщик", "emoji": "🏮", "rarity": "rare", "locations": ("abyss",), "min_g": 200, "max_g": 4000, "price": 36, "note": "Фонарик на лбу ещё тлеет."},
    {"id": "viperfish", "name": "Рыба-гадюка", "emoji": "🦷", "rarity": "rare", "locations": ("abyss",), "min_g": 50, "max_g": 800, "price": 48},
    {"id": "squid", "name": "Гигантский кальмар", "emoji": "🦑", "rarity": "epic", "locations": ("abyss",), "min_g": 15000, "max_g": 180000, "price": 8},
    {"id": "sleeper", "name": "Полярная акула", "emoji": "🦈", "rarity": "legendary", "locations": ("abyss",), "min_g": 40000, "max_g": 500000, "price": 6, "note": "Глаза старше любого порта."},
    {"id": "kraken", "name": "Кракен", "emoji": "🐙", "rarity": "mythic", "locations": ("abyss",), "min_g": 80000, "max_g": 600000, "price": 10, "note": "Вода вокруг стала чернильной."},
    {"id": "leviathan", "name": "Левиафан", "emoji": "🐉", "rarity": "mythic", "locations": ("abyss",), "min_g": 150000, "max_g": 900000, "price": 12, "note": "Дно на секунду поднялось само."},
    {"id": "mud_boot", "name": "Грязный сапог", "emoji": "👢", "rarity": "trash", "locations": ("swamp",), "min_g": 200, "max_g": 900, "price": 3},
    {"id": "rotan", "name": "Ротан", "emoji": "🐟", "rarity": "common", "locations": ("swamp",), "min_g": 30, "max_g": 400, "price": 11},
    {"id": "loach", "name": "Вьюн", "emoji": "🐟", "rarity": "common", "locations": ("swamp",), "min_g": 40, "max_g": 250, "price": 12},
    {"id": "swamp_pike", "name": "Болотная щука", "emoji": "🐊", "rarity": "uncommon", "locations": ("swamp",), "min_g": 400, "max_g": 6000, "price": 18},
    {"id": "swamp_cat", "name": "Болотный сом", "emoji": "🐡", "rarity": "rare", "locations": ("swamp",), "min_g": 800, "max_g": 15000, "price": 16, "note": "Пахнет тиной и грозой."},
    {"id": "swamp_wels", "name": "Хозяин трясины", "emoji": "💠", "rarity": "epic", "locations": ("swamp",), "min_g": 4000, "max_g": 40000, "price": 14},
    {"id": "quarry_perch", "name": "Карьерный окунь", "emoji": "🐠", "rarity": "common", "locations": ("quarry",), "min_g": 80, "max_g": 1500, "price": 13},
    {"id": "quarry_roach", "name": "Карьерная плотва", "emoji": "🐟", "rarity": "common", "locations": ("quarry",), "min_g": 40, "max_g": 500, "price": 11},
    {"id": "trout", "name": "Форель", "emoji": "🐠", "rarity": "uncommon", "locations": ("quarry",), "min_g": 200, "max_g": 4000, "price": 22},
    {"id": "quarry_zander", "name": "Глубинный судак", "emoji": "🐡", "rarity": "rare", "locations": ("quarry",), "min_g": 700, "max_g": 12000, "price": 20},
    {"id": "sturgeon", "name": "Осётр", "emoji": "💠", "rarity": "epic", "locations": ("quarry",), "min_g": 3000, "max_g": 50000, "price": 18, "note": "Чешуя как каменная плитка."},
    {"id": "silver_sturgeon", "name": "Серебряный осётр", "emoji": "👑", "rarity": "legendary", "locations": ("quarry",), "min_g": 8000, "max_g": 70000, "price": 24},
    {"id": "goby", "name": "Бычок", "emoji": "🐟", "rarity": "common", "locations": ("pier",), "min_g": 20, "max_g": 200, "price": 12},
    {"id": "smelt", "name": "Корюшка", "emoji": "🐟", "rarity": "common", "locations": ("pier",), "min_g": 15, "max_g": 120, "price": 14},
    {"id": "river_eel", "name": "Речной угорь", "emoji": "🐍", "rarity": "uncommon", "locations": ("pier",), "min_g": 200, "max_g": 2500, "price": 18},
    {"id": "mullet", "name": "Кефаль", "emoji": "🐡", "rarity": "rare", "locations": ("pier",), "min_g": 300, "max_g": 4000, "price": 17},
    {"id": "sea_bass", "name": "Морской судак", "emoji": "💠", "rarity": "epic", "locations": ("pier",), "min_g": 1500, "max_g": 20000, "price": 16},
    {"id": "night_halibut", "name": "Ночной палтус", "emoji": "👑", "rarity": "legendary", "locations": ("pier",), "min_g": 5000, "max_g": 60000, "price": 14, "note": "Поднялся к фонарям и сразу ушёл в тень."},
    {"id": "clownfish", "name": "Рыба-клоун", "emoji": "🐠", "rarity": "common", "locations": ("reef",), "min_g": 20, "max_g": 200, "price": 20},
    {"id": "parrotfish", "name": "Рыба-попугай", "emoji": "🐟", "rarity": "common", "locations": ("reef",), "min_g": 200, "max_g": 4000, "price": 16},
    {"id": "moray", "name": "Мурена", "emoji": "🐍", "rarity": "uncommon", "locations": ("reef", "wreck"), "min_g": 400, "max_g": 8000, "price": 18},
    {"id": "lionfish", "name": "Крылатка", "emoji": "🦁", "rarity": "uncommon", "locations": ("reef",), "min_g": 80, "max_g": 1200, "price": 24},
    {"id": "barracuda", "name": "Барракуда", "emoji": "🐡", "rarity": "rare", "locations": ("reef",), "min_g": 1000, "max_g": 20000, "price": 16},
    {"id": "reef_shark", "name": "Рифовая акула", "emoji": "🦈", "rarity": "epic", "locations": ("reef",), "min_g": 8000, "max_g": 80000, "price": 10},
    {"id": "manta", "name": "Манта", "emoji": "👑", "rarity": "legendary", "locations": ("reef",), "min_g": 30000, "max_g": 300000, "price": 8, "note": "Тень накрыла лодку целиком."},
    {"id": "wreck_boot", "name": "Сапог моряка", "emoji": "🥾", "rarity": "trash", "locations": ("wreck",), "min_g": 300, "max_g": 1200, "price": 4},
    {"id": "grouper", "name": "Групер", "emoji": "🐡", "rarity": "rare", "locations": ("wreck",), "min_g": 2000, "max_g": 40000, "price": 14},
    {"id": "nurse_shark", "name": "Акула-нянька", "emoji": "🦈", "rarity": "epic", "locations": ("wreck",), "min_g": 15000, "max_g": 150000, "price": 8},
    {"id": "ship_grouper", "name": "Корабельный групер", "emoji": "👑", "rarity": "legendary", "locations": ("wreck",), "min_g": 20000, "max_g": 180000, "price": 12},
    {"id": "captain_shade", "name": "Тень капитана", "emoji": "🔮", "rarity": "mythic", "locations": ("wreck",), "min_g": 5000, "max_g": 40000, "price": 36, "note": "Сеть прошла сквозь неё и всё равно стала тяжёлой."},
    {"id": "silver_scad", "name": "Серебряная ставрида", "emoji": "🐠", "rarity": "uncommon", "locations": ("moon",), "min_g": 200, "max_g": 2000, "price": 26},
    {"id": "moon_ray", "name": "Лунный скат", "emoji": "🐡", "rarity": "rare", "locations": ("moon",), "min_g": 3000, "max_g": 50000, "price": 18},
    {"id": "star_tuna", "name": "Звёздный тунец", "emoji": "💠", "rarity": "epic", "locations": ("moon",), "min_g": 10000, "max_g": 120000, "price": 12},
    {"id": "moon_whale", "name": "Лунный кит", "emoji": "👑", "rarity": "legendary", "locations": ("moon",), "min_g": 80000, "max_g": 700000, "price": 7, "note": "Бухта на минуту стала мельче."},
    {"id": "moon_leviathan", "name": "Серебряный змей", "emoji": "🔮", "rarity": "mythic", "locations": ("moon",), "min_g": 100000, "max_g": 800000, "price": 14, "note": "Чешуя гасит лунный свет."},
    {"id": "rusty_key", "name": "Ржавый ключ", "emoji": "🗝️", "kind": "find", "rarity": "common", "locations": ("pond", "river", "swamp"), "min_g": 15, "max_g": 60, "price": 80, "note": "От какого замка — уже не узнать."},
    {"id": "glass_float", "name": "Стеклянный поплавок", "emoji": "🟢", "kind": "find", "rarity": "uncommon", "locations": ("pond", "river", "lake", "swamp"), "min_g": 40, "max_g": 180, "price": 70},
    {"id": "compass", "name": "Старый компас", "emoji": "🧭", "kind": "find", "rarity": "uncommon", "locations": ("lake", "quarry", "pier"), "min_g": 30, "max_g": 120, "price": 90, "note": "Стрелка дрожит, но север всё ещё узнаёт."},
    {"id": "silver_spoon", "name": "Серебряная ложка", "emoji": "🥄", "kind": "find", "rarity": "rare", "locations": ("lake", "quarry", "river"), "min_g": 20, "max_g": 80, "price": 220},
    {"id": "pearl", "name": "Жемчужина", "emoji": "⚪", "kind": "find", "rarity": "rare", "locations": ("sea", "pier", "ocean", "reef"), "min_g": 5, "max_g": 30, "price": 1800, "note": "Тёплая, будто только из раковины."},
    {"id": "gold_chain", "name": "Золотая цепочка", "emoji": "📿", "kind": "find", "rarity": "epic", "locations": ("sea", "ocean", "pier", "reef"), "min_g": 10, "max_g": 80, "price": 900},
    {"id": "black_pearl", "name": "Чёрная жемчужина", "emoji": "⚫", "kind": "find", "rarity": "epic", "locations": ("reef", "wreck"), "min_g": 8, "max_g": 40, "price": 2200},
    {"id": "captain_chest", "name": "Сундук капитана", "emoji": "🧰", "kind": "find", "rarity": "legendary", "locations": ("wreck", "ocean"), "min_g": 2000, "max_g": 15000, "price": 80, "note": "Замок сорван, а внутри всё ещё сухо."},
    {"id": "idol", "name": "Глубинный идол", "emoji": "🗿", "kind": "find", "rarity": "epic", "locations": ("abyss", "wreck"), "min_g": 800, "max_g": 8000, "price": 70},
    {"id": "abyss_pearl", "name": "Жемчуг бездны", "emoji": "💠", "kind": "find", "rarity": "legendary", "locations": ("abyss",), "min_g": 20, "max_g": 90, "price": 3500, "note": "В темноте он светится сам."},
    {"id": "moon_shard", "name": "Лунный осколок", "emoji": "🌙", "kind": "find", "rarity": "legendary", "locations": ("moon", "reef"), "min_g": 30, "max_g": 200, "price": 1600},
    {"id": "moon_crown", "name": "Лунная корона", "emoji": "👑", "kind": "find", "rarity": "mythic", "locations": ("moon",), "min_g": 200, "max_g": 900, "price": 4000, "note": "Надевать её не стоит. Продать — очень даже."},
]

WAIT_LINES = (
    "Поплавок лёг на воду.",
    "Леска уходит в глубину.",
    "Тишина. Только круги на воде.",
    "Удочка чуть дрожит в руках.",
    "Где-то внизу кто-то присматривается.",
    "Ветер стих. Самое время.",
)

LOC_BY_ID = {item["id"]: item for item in LOCATIONS}
ROD_BY_ID = {item["id"]: item for item in RODS}
BAIT_BY_ID = {item["id"]: item for item in BAITS}
FISH_BY_ID = {item["id"]: item for item in FISH}


def rod_index(rod_id: str) -> int:
    for index, rod in enumerate(RODS):
        if rod["id"] == rod_id:
            return index
    return 0


def location_index(location_id: str) -> int:
    for index, location in enumerate(LOCATIONS):
        if location["id"] == location_id:
            return index
    return 0


def xp_to_next(level: int) -> int:
    return 30 + (level - 1) * 20


def level_from_xp(xp: int) -> tuple[int, int, int]:
    level = 1
    rest = max(0, int(xp))
    while True:
        need = xp_to_next(level)
        if rest < need:
            return level, rest, need
        rest -= need
        level += 1


def locations_unlocked(old_level: int, new_level: int) -> list[dict]:
    if new_level <= old_level:
        return []
    return [loc for loc in LOCATIONS if old_level < loc["level"] <= new_level]


def is_catch_fish(item: dict) -> bool:
    return item.get("kind", "fish") == "fish"


def fishes_for(location_id: str, rarity: str) -> list[dict]:
    return [
        fish
        for fish in FISH
        if is_catch_fish(fish) and fish["rarity"] == rarity and location_id in fish["locations"]
    ]


def finds_for(location_id: str) -> list[dict]:
    return [
        item
        for item in FISH
        if item.get("kind") == "find" and location_id in item["locations"]
    ]


def rarities_in_location(location_id: str) -> set[str]:
    return {
        fish["rarity"]
        for fish in FISH
        if is_catch_fish(fish) and location_id in fish["locations"]
    }


def find_chance(location_id: str, luck: int) -> float:
    location = LOC_BY_ID.get(location_id) or LOCATIONS[0]
    base = float(location.get("find", 0.08))
    return min(0.42, base + max(0, luck) * 0.0011)


def upgrade_cost(current_rod_id: str, new_rod_id: str) -> int | None:
    current = rod_index(current_rod_id)
    new = rod_index(new_rod_id)
    if new <= current:
        return None
    refund = int(RODS[current]["price"] * ROD_REFUND)
    return max(0, RODS[new]["price"] - refund)


def calc_price(fish: dict, weight: int) -> int:
    mult = RARITY[fish["rarity"]]["price_mult"]
    return max(1, int(weight / 100 * fish["price"] * mult))
