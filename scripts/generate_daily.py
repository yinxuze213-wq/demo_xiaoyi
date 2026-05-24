from __future__ import annotations

import argparse
import http.client
import json
import os
import random
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config.json"
DATA_PATH = ROOT / "data.json"
PUSHPLUS_URL = "https://www.pushplus.plus/send/"
HITOKOTO_URL = "https://v1.hitokoto.cn/"

WEATHER_CODES = {
    0: "晴",
    1: "大致晴",
    2: "局部多云",
    3: "阴天",
    45: "有雾",
    48: "雾凇",
    51: "小毛毛雨",
    53: "毛毛雨",
    55: "较强毛毛雨",
    61: "小雨",
    63: "中雨",
    65: "大雨",
    71: "小雪",
    73: "中雪",
    75: "大雪",
    80: "小阵雨",
    81: "阵雨",
    82: "强阵雨",
    95: "雷雨",
    96: "雷雨伴小冰雹",
    99: "雷雨伴冰雹",
}

WEEKDAYS = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]

THEMES = [
    {
        "name": "草莓气泡",
        "mood": "甜甜的、但不吵",
        "effect": "petal",
        "sticker": "strawberry",
        "vars": {
            "--bg-top": "#fff4f7",
            "--bg-mid": "#f3fbf8",
            "--bg-bottom": "#fffaf1",
            "--paper": "rgba(255, 255, 255, 0.86)",
            "--ink": "#28323b",
            "--muted": "#6b7280",
            "--accent": "#f06f91",
            "--accent-2": "#52aeb3",
            "--accent-3": "#f4bd4f",
            "--accent-4": "#8a79c8",
            "--soft": "rgba(240, 111, 145, 0.12)",
        },
    },
    {
        "name": "海盐蜜桃",
        "mood": "清透、轻盈、适合慢慢来",
        "effect": "bubble",
        "sticker": "peach",
        "vars": {
            "--bg-top": "#fff2ea",
            "--bg-mid": "#ecfbff",
            "--bg-bottom": "#fff7dc",
            "--paper": "rgba(255, 255, 255, 0.84)",
            "--ink": "#263440",
            "--muted": "#687480",
            "--accent": "#ff8f70",
            "--accent-2": "#4fa6c8",
            "--accent-3": "#f2c95f",
            "--accent-4": "#86b874",
            "--soft": "rgba(79, 166, 200, 0.13)",
        },
    },
    {
        "name": "薄荷奶盖",
        "mood": "干净、松弛、被照顾",
        "effect": "star",
        "sticker": "mint",
        "vars": {
            "--bg-top": "#effcf6",
            "--bg-mid": "#fff8ef",
            "--bg-bottom": "#f2f3ff",
            "--paper": "rgba(255, 255, 255, 0.86)",
            "--ink": "#25333a",
            "--muted": "#66747c",
            "--accent": "#61b99b",
            "--accent-2": "#6f86d9",
            "--accent-3": "#f4b84f",
            "--accent-4": "#df7c9b",
            "--soft": "rgba(97, 185, 155, 0.13)",
        },
    },
    {
        "name": "蓝莓月光",
        "mood": "安静、柔软、有一点浪漫",
        "effect": "moon",
        "sticker": "moon",
        "vars": {
            "--bg-top": "#f2f0ff",
            "--bg-mid": "#f7fbff",
            "--bg-bottom": "#fff4f6",
            "--paper": "rgba(255, 255, 255, 0.85)",
            "--ink": "#283143",
            "--muted": "#6d7280",
            "--accent": "#7c78cf",
            "--accent-2": "#5aa7c8",
            "--accent-3": "#f0b75e",
            "--accent-4": "#ef7d95",
            "--soft": "rgba(124, 120, 207, 0.13)",
        },
    },
    {
        "name": "柠檬花园",
        "mood": "明亮、舒服、带一点元气",
        "effect": "leaf",
        "sticker": "lemon",
        "vars": {
            "--bg-top": "#fffbe8",
            "--bg-mid": "#eefbf2",
            "--bg-bottom": "#fff2f3",
            "--paper": "rgba(255, 255, 255, 0.86)",
            "--ink": "#2c332a",
            "--muted": "#66715f",
            "--accent": "#eeb946",
            "--accent-2": "#62ae7c",
            "--accent-3": "#ec7d96",
            "--accent-4": "#5a90c9",
            "--soft": "rgba(238, 185, 70, 0.14)",
        },
    },
]

LUCKY_COLORS = [
    ("草莓粉", "#f06f91"),
    ("海盐蓝", "#5aa7c8"),
    ("奶油白", "#fff8ef"),
    ("薄荷绿", "#61b99b"),
    ("月光紫", "#8a79c8"),
    ("柠檬黄", "#f2c95f"),
    ("蜜桃橙", "#ff8f70"),
    ("小雏菊", "#f4bd4f"),
]

MOOD_WORDS = [
    "被偏爱",
    "松弛一点",
    "慢慢来",
    "甜度刚好",
    "闪闪发光",
    "轻轻呼吸",
    "好好吃饭",
    "准时休息",
    "先爱自己",
]

FORTUNE_FOCUS = [
    "把难的事情拆成一小步，会比硬撑更顺",
    "今天适合先照顾心情，再处理事情",
    "别急着证明什么，舒服的节奏更重要",
    "适合整理计划，也适合给自己留一点空白",
    "遇到不开心时先暂停，别让情绪替你做决定",
    "今天的好运藏在细节里，慢一点反而更稳",
]

SUITABLE_POOL = [
    "喝一杯温热的东西",
    "把今天最重要的一件事先做完",
    "散步十分钟",
    "听一首轻音乐",
    "给桌面或房间留一点清爽",
    "认真吃一顿饭",
    "早点洗漱",
    "拍一张喜欢的照片",
    "和喜欢的人说一句想说的话",
    "给自己买一点小甜",
]

AVOID_POOL = [
    "空腹喝冰的",
    "把小情绪憋到很晚",
    "临睡前一直刷手机",
    "为了赶进度不吃饭",
    "和自己较劲太久",
    "反复想已经过去的事",
    "被别人的节奏带着跑",
    "把所有事都放到最后一刻",
]

BOYFRIEND_NOTES = [
    "今天想让你先把自己照顾好。饭要好好吃，水要记得喝，累了就停一下，我会一直站在你这边。",
    "如果今天有一点点不顺，也别急着怪自己。你已经很好了，剩下的慢慢来，我陪你一起把日子过软一点。",
    "今天希望你少一点逞强，多一点被照顾。可以先完成一件小事，然后奖励自己休息一下。",
    "想提醒你：不需要每一分钟都很厉害。你只要平平安安、舒舒服服，我就觉得今天很好。",
    "今天把心情放在前面一点。难过可以说，开心也要说，我都想听，也都会认真接住。",
]

HERO_TITLES = [
    "今天也要被温柔照顾",
    "今日份好运正在靠近",
    "把今天过得甜一点",
    "慢慢来，也很漂亮",
    "今天适合闪闪发光",
    "给你一张今日小卡片",
]

HERO_SUBTITLES = [
    "天气、运势、纪念日和一点偏爱，都放在这里了。",
    "不用赶时间，先把今天打开成柔软的样子。",
    "这张卡片每天都会换一套颜色和一句想对你说的话。",
    "希望你今天被好好对待，也好好对待自己。",
    "先收下这份小提醒，剩下的事情慢慢完成。",
]

MUSIC_PRESETS = [
    {
        "title": "晨光钢琴盒",
        "subtitle": "明亮、轻快、像早晨的窗边",
        "tempo": 96,
        "waveform": "sine",
        "scale": [261.63, 293.66, 329.63, 392.0, 440.0, 523.25],
    },
    {
        "title": "海盐八音盒",
        "subtitle": "清透、安静、适合放空",
        "tempo": 84,
        "waveform": "triangle",
        "scale": [293.66, 329.63, 369.99, 440.0, 493.88, 587.33],
    },
    {
        "title": "月光小夜曲",
        "subtitle": "柔软、慢一点、适合睡前",
        "tempo": 72,
        "waveform": "sine",
        "scale": [220.0, 261.63, 293.66, 329.63, 392.0, 440.0],
    },
    {
        "title": "薄荷午后",
        "subtitle": "轻盈、干净、像风吹过杯沿",
        "tempo": 90,
        "waveform": "triangle",
        "scale": [246.94, 293.66, 329.63, 392.0, 493.88, 587.33],
    },
    {
        "title": "柠檬花园",
        "subtitle": "有一点元气，也有一点温柔",
        "tempo": 102,
        "waveform": "sine",
        "scale": [261.63, 329.63, 349.23, 392.0, 440.0, 523.25],
    },
]

LOCAL_QUOTES = [
    "把普通的今天，也过成值得记住的一天。",
    "万事都要全力以赴，包括开心。",
    "慢慢来，漂亮的事情总会一点点发生。",
    "不需要特别勇敢，也可以被好好喜欢。",
    "今天不追赶世界，先照顾自己。",
]

FESTIVAL_RULES = [
    {"name": "元旦", "date": "01-01", "kind": "新年", "tone": "新的一年，适合一起许一个轻轻的愿望。"},
    {"name": "情人节", "date": "02-14", "kind": "恋爱", "tone": "适合准备花、甜品和一句认真说出口的喜欢。"},
    {"name": "女生节", "date": "03-07", "kind": "宠爱", "tone": "适合把她放在第一位，安排一点小惊喜。"},
    {"name": "白色情人节", "date": "03-14", "kind": "恋爱", "tone": "适合回一份温柔，也适合认真约会。"},
    {"name": "520", "date": "05-20", "kind": "恋爱", "tone": "适合把喜欢说得直接一点，也可以准备一张小卡片。"},
    {"name": "521", "date": "05-21", "kind": "恋爱", "tone": "适合继续表达喜欢，把普通一天过成纪念日。"},
    {"name": "六一儿童节", "date": "06-01", "kind": "可爱", "tone": "适合买小零食、小玩具，哄她开心一下。"},
    {"name": "七夕", "date": "lunar-qixi", "kind": "恋爱", "tone": "适合认真约会，也适合留一封只给她看的话。"},
    {"name": "圣诞节", "date": "12-25", "kind": "节日", "tone": "适合交换小礼物，拍一张有氛围感的照片。"},
    {"name": "跨年夜", "date": "12-31", "kind": "新年", "tone": "适合一起倒数，把新年的第一份偏爱留给她。"},
]

QIXI_DATES = {
    2026: "2026-08-19",
    2027: "2027-08-08",
    2028: "2028-08-26",
    2029: "2029-08-16",
    2030: "2030-08-05",
}

LOVE_TIPS = [
    "今天适合把喜欢说得具体一点，比如夸她一个很小但很真的细节",
    "适合轻轻陪着，不急着讲道理，先让她感觉被站在同一边",
    "今天的小浪漫不用很贵，重点是你真的记得她喜欢什么",
    "适合主动问一句今天累不累，再给她一个不用逞强的空间",
    "今天适合多一点回应，消息不用很多，但要让她感到稳定",
]

WORK_STUDY_TIPS = [
    "适合先做最容易推进的一件事，打开状态比追求完美重要",
    "今天不要把任务排太满，留一点缓冲会更顺",
    "适合整理待办，把复杂事情分成二十分钟的小段",
    "重要决定可以先记下来，晚一点再确认也不迟",
    "今天适合清理杂事，给后面的事情腾出一点空间",
]

ENERGY_TIPS = [
    "能量适中，适合稳稳推进",
    "能量偏柔软，适合少一点硬撑",
    "能量轻快，适合做一点会让心情变好的事",
    "能量需要慢慢蓄起来，别太早消耗完",
    "能量不错，但要记得及时休息",
]

LUCKY_ITEMS = [
    "发圈",
    "小甜品",
    "热饮",
    "香香的护手霜",
    "舒服的鞋子",
    "一首轻音乐",
    "干净桌面",
    "柔软外套",
]

DATE_IDEAS = [
    "一起散步，买一杯她喜欢的饮料",
    "晚上挑一部轻松的电影，不赶时间地看完",
    "一起吃一顿不用纠结热量的小饭",
    "拍一张今天的照片，留作普通日子的纪念",
    "给她准备一个小零食袋，里面放她常吃的东西",
    "一起听今日 BGM，然后说一句今天最想说的话",
]

PHOTO_IDEAS = [
    "拍今天的天空",
    "拍一张她喜欢的小物件",
    "拍一张饮料或甜品",
    "拍今天的穿搭细节",
    "拍一个看起来很舒服的角落",
]

COMFORT_FOODS = [
    "一杯热饮",
    "清淡但认真吃的一顿饭",
    "一点点甜品",
    "热汤或热粥",
    "她最近想吃的那一口",
]


def log(message: str) -> None:
    sys.stdout.write(message + "\n")


def http_json(url: str, *, payload: dict[str, Any] | None = None, timeout: int = 18) -> dict[str, Any]:
    data = None
    method = "GET"
    headers = {"User-Agent": "xiaoyi-card/2.0"}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
        method = "POST"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def china_today() -> date:
    return datetime.now(timezone(timedelta(hours=8))).date()


def day_rng(today: date, key: str) -> random.Random:
    return random.Random(f"{today.isoformat()}:{key}:xiaoyi-card-v2")


def pick_many(pool: list[str], count: int, rng: random.Random) -> list[str]:
    items = pool[:]
    rng.shuffle(items)
    return items[:count]


def parse_date(value: str) -> tuple[int | None, int, int]:
    parts = str(value).replace("/", "-").split("-")
    if len(parts) == 3:
        return int(parts[0]), int(parts[1]), int(parts[2])
    if len(parts) == 2:
        return None, int(parts[0]), int(parts[1])
    raise ValueError(f"Bad date: {value}")


def safe_date(year: int, month: int, day: int) -> date:
    try:
        return date(year, month, day)
    except ValueError:
        if month == 2 and day == 29:
            return date(year, 2, 28)
        raise


def next_occurrence(month: int, day: int, today: date) -> date:
    current = safe_date(today.year, month, day)
    if current < today:
        current = safe_date(today.year + 1, month, day)
    return current


def next_qixi(today: date) -> date | None:
    candidates = [date.fromisoformat(value) for year, value in QIXI_DATES.items() if year >= today.year]
    future = [item for item in candidates if item >= today]
    if future:
        return min(future)
    return None


def festival_occurrence(rule: dict[str, Any], today: date) -> date | None:
    value = str(rule.get("date", ""))
    if value == "lunar-qixi":
        return next_qixi(today)
    year, month, day = parse_date(value)
    if year:
        target = safe_date(year, month, day)
        return target if target >= today else None
    return next_occurrence(month, day, today)


def build_festivals(config: dict[str, Any], today: date) -> dict[str, Any]:
    rules = FESTIVAL_RULES + list(config.get("custom_festivals", []))
    items: list[dict[str, Any]] = []
    for rule in rules:
        occurrence = festival_occurrence(rule, today)
        if not occurrence:
            continue
        days_left = (occurrence - today).days
        name = str(rule.get("name", "节日"))
        if days_left == 0:
            line = f"今天就是{name}，适合把仪式感安排上。"
        else:
            line = f"距离{name}还有 {days_left} 天。"
        items.append({
            "name": name,
            "kind": rule.get("kind", "节日"),
            "date": occurrence.isoformat(),
            "date_label": occurrence.strftime("%m.%d"),
            "days_left": days_left,
            "tone": rule.get("tone", "适合提前准备一点小惊喜。"),
            "line": line,
        })
    items.sort(key=lambda item: (item["days_left"], item["name"]))
    return {
        "next": items[0] if items else None,
        "items": items[:8],
    }


def build_theme(today: date) -> dict[str, Any]:
    rng = day_rng(today, "theme")
    theme = THEMES[rng.randrange(len(THEMES))]
    return {
        "name": theme["name"],
        "mood": theme["mood"],
        "effect": theme["effect"],
        "sticker": theme["sticker"],
        "vars": theme["vars"],
    }


def outfit_tip(summary: str, low: int, high: int) -> str:
    if any(word in summary for word in ["雨", "雷"]):
        return "记得带伞，鞋子尽量选舒服防滑的。"
    if high >= 30:
        return "天气偏热，穿轻薄一点，记得补水防晒。"
    if low <= 12:
        return "早晚可能凉，外套别省。"
    if high - low >= 8:
        return "温差有点存在感，薄外套会更稳。"
    return "穿舒服一点就好，今天不需要太用力。"


def fetch_weather(config: dict[str, Any]) -> dict[str, str]:
    weather = config.get("weather", {})
    city = weather.get("city", "她的城市")
    lat = weather.get("latitude")
    lon = weather.get("longitude")
    fallback = {
        "city": city,
        "summary": "天气暂时没有取到",
        "temperature": "--",
        "outfit": "出门前看一眼实时天气，穿舒服一点。",
    }
    if lat in (None, "") or lon in (None, ""):
        return fallback
    query = urllib.parse.urlencode({
        "latitude": lat,
        "longitude": lon,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min",
        "forecast_days": 1,
        "timezone": "auto",
    })
    try:
        data = http_json(f"https://api.open-meteo.com/v1/forecast?{query}")
        daily = data.get("daily", {})
        code = (daily.get("weather_code") or [None])[0]
        high = round((daily.get("temperature_2m_max") or [0])[0])
        low = round((daily.get("temperature_2m_min") or [0])[0])
        text = WEATHER_CODES.get(code, "天气")
        summary = f"{city}今天{text}，约 {low}-{high}°C。"
        return {"city": city, "summary": summary, "temperature": f"{low}-{high}°", "outfit": outfit_tip(summary, low, high)}
    except (urllib.error.URLError, http.client.RemoteDisconnected, TimeoutError, json.JSONDecodeError, KeyError, TypeError, ValueError, OSError):
        return fallback


def build_relationship(config: dict[str, Any], today: date) -> dict[str, Any]:
    start_value = config.get("profile", {}).get("relationship_start")
    if not start_value:
        return {
            "days_together": "--",
            "line": "在一起的日期还没有配置。",
            "anniversary": {"days_left": "--", "line": "把纪念日写进 config.json 就能自动提醒。"},
        }
    year, month, day = parse_date(start_value)
    if not year:
        return {
            "days_together": "--",
            "line": "在一起的日期需要写完整年月日。",
            "anniversary": {"days_left": "--", "line": "把纪念日写完整就能自动计算。"},
        }
    start = safe_date(year, month, day)
    days = max(0, (today - start).days + 1)
    next_day = next_occurrence(month, day, today)
    days_left = (next_day - today).days
    years = max(0, next_day.year - start.year)
    if days_left == 0:
        anniversary_line = f"今天是第 {years} 年纪念日，值得认真开心一下。"
    else:
        anniversary_line = f"距离第 {years} 年纪念日还有 {days_left} 天。"
    return {
        "start": start.isoformat(),
        "days_together": days,
        "line": f"你们已经在一起 {days} 天。",
        "anniversary": {"days_left": days_left, "years": years, "line": anniversary_line},
    }


def build_birthday(person: dict[str, Any], today: date) -> dict[str, Any]:
    nickname = person.get("nickname") or person.get("label") or "她"
    year, month, day = parse_date(person.get("birthday", "01-01"))
    next_day = next_occurrence(month, day, today)
    days_left = (next_day - today).days
    next_age = next_day.year - year if year else None
    if days_left == 0:
        line = f"今天是{nickname}生日，生日快乐要放在第一位。"
    elif next_age:
        line = f"距离{nickname}生日还有 {days_left} 天，下一次是 {next_age} 岁生日。"
    else:
        line = f"距离{nickname}生日还有 {days_left} 天。"
    return {
        "label": person.get("label", nickname),
        "nickname": nickname,
        "date": f"{month:02d}.{day:02d}",
        "days_left": days_left,
        "next_age": next_age,
        "line": line,
    }


def collect_events(config: dict[str, Any], today: date, relationship: dict[str, Any], birthdays: list[dict[str, Any]]) -> list[str]:
    lines = [relationship.get("line", "")]
    anniversary = relationship.get("anniversary", {})
    if anniversary.get("line"):
        lines.append(anniversary["line"])
    lines.extend(birthday["line"] for birthday in birthdays)

    default_window = int(config.get("event_remind_days", 30))
    for event in config.get("events", []):
        if event.get("type") == "anniversary":
            continue
        original_year, month, day = parse_date(event["date"])
        occurrence = next_occurrence(month, day, today) if event.get("recurring", True) else safe_date(original_year, month, day)
        days_left = (occurrence - today).days
        if days_left < 0 or days_left > int(event.get("remind_days", default_window)):
            continue
        name = event.get("name", "重要日子")
        lines.append(f"今天是{name}。" if days_left == 0 else f"距离{name}还有 {days_left} 天。")

    deduped: list[str] = []
    for line in lines:
        if line and line not in deduped:
            deduped.append(line)
    return deduped[:6]


def build_horoscope(person_key: str, person: dict[str, Any], today: date) -> dict[str, Any]:
    sign = person.get("sign", "天秤座")
    nickname = person.get("nickname") or person.get("label") or sign
    rng = day_rng(today, f"horoscope:{person_key}:{sign}")
    color_name, color_hex = rng.choice(LUCKY_COLORS)
    keyword = rng.choice(MOOD_WORDS)
    focus = rng.choice(FORTUNE_FOCUS)
    suitable = pick_many(SUITABLE_POOL, 3, rng)
    avoid = pick_many(AVOID_POOL, 3, rng)
    love_tip = rng.choice(LOVE_TIPS)
    work_tip = rng.choice(WORK_STUDY_TIPS)
    energy = rng.choice(ENERGY_TIPS)
    lucky_item = rng.choice(LUCKY_ITEMS)
    return {
        "label": person.get("label", nickname),
        "nickname": nickname,
        "sign": sign,
        "keyword": keyword,
        "focus": focus,
        "summary": f"{sign}今日关键词是「{keyword}」。{focus}。",
        "overall": rng.randint(3, 5),
        "love": rng.randint(3, 5),
        "mood": rng.randint(3, 5),
        "energy_score": rng.randint(3, 5),
        "lucky_color": color_name,
        "lucky_color_hex": color_hex,
        "lucky_number": str(rng.randint(1, 9)),
        "lucky_item": lucky_item,
        "energy": energy,
        "love_tip": love_tip,
        "work_tip": work_tip,
        "suitable": suitable,
        "avoid": avoid,
    }


def build_today_guide(today: date, weather: dict[str, str], girlfriend_horoscope: dict[str, Any]) -> dict[str, Any]:
    rng = day_rng(today, "today-guide")
    suitable = list(girlfriend_horoscope.get("suitable", []))
    avoid = list(girlfriend_horoscope.get("avoid", []))
    for item in pick_many(SUITABLE_POOL, 4, rng):
        if item not in suitable:
            suitable.append(item)
    for item in pick_many(AVOID_POOL, 4, rng):
        if item not in avoid:
            avoid.append(item)
    return {
        "suitable": suitable[:4],
        "avoid": avoid[:4],
        "care": [
            weather.get("outfit", "穿舒服一点就好。"),
            rng.choice([
                "今天先做最重要的一件事，剩下的慢慢补。",
                "心情如果乱了，就先离开屏幕休息三分钟。",
                "别把自己放在最后，先照顾身体和情绪。",
                "需要开心的时候，就给自己一点小奖励。",
            ]),
        ],
    }


def build_boyfriend_message(today: date, guide: dict[str, Any]) -> dict[str, Any]:
    rng = day_rng(today, "boyfriend-message")
    action = rng.choice(guide.get("suitable", SUITABLE_POOL))
    note = rng.choice(BOYFRIEND_NOTES)
    wishes = [
        f"今天希望你可以{action}。",
        rng.choice([
            "不要因为一点小事否定自己。",
            "遇到不舒服的事情可以先停下来。",
            "吃饭、喝水、休息都要排进今天。",
            "不想说话也没关系，我会乖乖在。",
        ]),
        rng.choice([
            "晚上尽量早点放下手机。",
            "想吃什么就告诉我，我会记住。",
            "今天的开心也要第一时间分享给我。",
            "如果累了，就把今天的任务变小一点。",
        ]),
    ]
    return {"title": "男朋友的小提醒", "text": note, "wishes": wishes}


def build_daily_capsule(today: date, theme: dict[str, Any], festivals: dict[str, Any]) -> dict[str, Any]:
    rng = day_rng(today, "daily-capsule")
    next_festival = festivals.get("next") if festivals else None
    if next_festival:
        prepare = f"可以提前为{next_festival['name']}准备：{next_festival['tone']}"
    else:
        prepare = "今天没有临近节日，也可以把普通日子过得有一点特别。"
    return {
        "title": f"{theme.get('name', '今日')}小安排",
        "items": [
            {"label": "约会灵感", "value": rng.choice(DATE_IDEAS)},
            {"label": "照片任务", "value": rng.choice(PHOTO_IDEAS)},
            {"label": "今日小食", "value": rng.choice(COMFORT_FOODS)},
            {"label": "提前准备", "value": prepare},
        ],
    }


def fetch_quote(config: dict[str, Any], today: date) -> str:
    quote_cfg = config.get("quote", {})
    if not quote_cfg.get("enabled", True):
        return day_rng(today, "quote").choice(LOCAL_QUOTES)
    query = [urllib.parse.urlencode({"encode": "json", "max_length": int(quote_cfg.get("max_length", 34))})]
    query.extend(f"c={urllib.parse.quote(str(category))}" for category in quote_cfg.get("categories", ["d", "i", "k"]))
    try:
        data = http_json(f"{HITOKOTO_URL}?{'&'.join(query)}")
        text = str(data.get("hitokoto") or "").strip()
        source = str(data.get("from") or data.get("from_who") or "").strip()
        if text and source:
            return f"{text} —— {source}"
        if text:
            return text
    except (urllib.error.URLError, urllib.error.HTTPError, http.client.RemoteDisconnected, TimeoutError, json.JSONDecodeError, ValueError, OSError):
        pass
    return day_rng(today, "quote-fallback").choice(LOCAL_QUOTES)


def build_music(config: dict[str, Any], today: date) -> dict[str, Any]:
    music_cfg = config.get("music", {})
    tracks = [track for track in music_cfg.get("tracks", []) if track.get("src")]
    rng = day_rng(today, "music")
    if tracks and music_cfg.get("mode") in ("track", "tracks", "auto"):
        track = tracks[rng.randrange(len(tracks))]
        return {
            "mode": "track",
            "title": track.get("title", "今日轻音乐"),
            "artist": track.get("artist", ""),
            "src": track["src"],
            "seed": f"{today.isoformat()}:track",
        }
    preset = MUSIC_PRESETS[rng.randrange(len(MUSIC_PRESETS))]
    melody = preset["scale"][:]
    rng.shuffle(melody)
    return {
        "mode": "generated",
        "title": preset["title"],
        "subtitle": preset["subtitle"],
        "tempo": preset["tempo"],
        "waveform": preset["waveform"],
        "scale": melody,
        "seed": f"{today.isoformat()}:generated:{preset['title']}",
    }


def build_data(config: dict[str, Any], today: date) -> dict[str, Any]:
    people = config.get("people", {})
    girlfriend = people.get("girlfriend", {})
    boyfriend = people.get("boyfriend", {})
    rng = day_rng(today, "copy")
    theme = build_theme(today)
    weather = fetch_weather(config)
    festivals = build_festivals(config, today)
    horoscopes = {
        "girlfriend": build_horoscope("girlfriend", girlfriend, today),
        "boyfriend": build_horoscope("boyfriend", boyfriend, today),
    }
    if horoscopes["boyfriend"]["keyword"] == horoscopes["girlfriend"]["keyword"]:
        current = horoscopes["boyfriend"]["keyword"]
        horoscopes["boyfriend"]["keyword"] = MOOD_WORDS[(MOOD_WORDS.index(current) + 3) % len(MOOD_WORDS)]
    if horoscopes["boyfriend"]["focus"] == horoscopes["girlfriend"]["focus"]:
        current = horoscopes["boyfriend"]["focus"]
        horoscopes["boyfriend"]["focus"] = FORTUNE_FOCUS[(FORTUNE_FOCUS.index(current) + 2) % len(FORTUNE_FOCUS)]
    for horoscope in horoscopes.values():
        horoscope["summary"] = f"{horoscope['sign']}今日关键词是「{horoscope['keyword']}」。{horoscope['focus']}。"
    relationship = build_relationship(config, today)
    birthdays = [build_birthday(girlfriend, today), build_birthday(boyfriend, today)]
    events = collect_events(config, today, relationship, birthdays)
    guide = build_today_guide(today, weather, horoscopes["girlfriend"])
    boyfriend_message = build_boyfriend_message(today, guide)
    daily_capsule = build_daily_capsule(today, theme, festivals)
    site = config.get("site", {})
    return {
        "generated_at": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
        "date_iso": today.isoformat(),
        "date_label": today.strftime("%Y.%m.%d"),
        "weekday_label": WEEKDAYS[today.weekday()],
        "site_title": site.get("title", "今日能量小卡片"),
        "hero_title": rng.choice(HERO_TITLES),
        "hero_subtitle": rng.choice(HERO_SUBTITLES),
        "theme": theme,
        "weather": weather,
        "relationship": relationship,
        "birthdays": birthdays,
        "festivals": festivals,
        "events": events,
        "horoscopes": horoscopes,
        "today_guide": guide,
        "daily_capsule": daily_capsule,
        "boyfriend_message": boyfriend_message,
        "quote": fetch_quote(config, today),
        "music": build_music(config, today),
        "push_message": "今日小卡片已经准备好，打开就能看到天气、运势、纪念日、节日倒计时和想对你说的话。",
        "footer": site.get("footer", "不用立刻回复，打开看看就好。"),
    }


def send_pushplus(data: dict[str, Any], site_url: str) -> None:
    token = os.environ.get("PUSHPLUS_TOKEN", "").strip()
    to = os.environ.get("PUSHPLUS_TO", "").strip()
    if not token:
        log("Skip PushPlus: PUSHPLUS_TOKEN is not set.")
        return
    card_url = site_url.rstrip("/") + "/"
    content = f"""
<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;line-height:1.8;color:#263238;">
  <div style="font-size:18px;font-weight:700;">今日小卡片已经准备好</div>
  <p>{data.get("push_message", "打开看看今天的小卡片。")}</p>
  <p><a href="{card_url}">点这里打开今日小卡片</a></p>
  <p style="color:#66747c;font-size:13px;">{data.get("weather", {}).get("summary", "")}</p>
</div>
"""
    payload = {"token": token, "title": "今日能量小卡片", "content": content, "template": "html"}
    if to:
        payload["to"] = to
    result = http_json(PUSHPLUS_URL, payload=payload)
    log(f"PushPlus result: {json.dumps(result, ensure_ascii=False)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate daily card data without AI.")
    parser.add_argument("--push", action="store_true", help="Send PushPlus notification after generating data.")
    parser.add_argument("--push-only", action="store_true", help="Send PushPlus notification with existing data.json.")
    parser.add_argument("--url", default=os.environ.get("SITE_URL", ""), help="Published GitHub Pages URL.")
    args = parser.parse_args()
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8-sig"))
    if args.push_only:
        if DATA_PATH.exists():
            data = json.loads(DATA_PATH.read_text(encoding="utf-8-sig"))
        else:
            data = build_data(config, china_today())
        if args.url:
            send_pushplus(data, args.url)
        else:
            log("Skip PushPlus: --url or SITE_URL is not set.")
        return 0

    data = build_data(config, china_today())
    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"Generated {DATA_PATH}")
    log(f"Theme: {data['theme']['name']}")
    log(f"Weather: {data['weather']['summary']}")
    log(f"Music: {data['music']['title']}")
    if args.push:
        if args.url:
            send_pushplus(data, args.url)
        else:
            log("Skip PushPlus: --url or SITE_URL is not set.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
