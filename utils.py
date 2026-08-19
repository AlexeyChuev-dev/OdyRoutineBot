from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def now(timezone: str) -> datetime:
    return datetime.now(ZoneInfo(timezone))


def parse_date(value: str, timezone: str):
    value = value.strip()
    current = now(timezone)

    if value == "Сегодня":
        return current.date()

    if value == "Завтра":
        return (current + timedelta(days=1)).date()

    if value == "Без даты":
        return None

    return datetime.strptime(value, "%d.%m.%Y").date()


def parse_time(value: str):
    value = value.strip()

    if value == "Без времени":
        return None

    return datetime.strptime(value, "%H:%M").time()


def combine_due(date_value, time_value, timezone: str):
    if date_value is None:
        return None

    if time_value is None:
        time_value = datetime.strptime("23:59", "%H:%M").time()

    return datetime.combine(
        date_value,
        time_value,
        tzinfo=ZoneInfo(timezone),
    ).isoformat()


def format_datetime(value: str | None, timezone: str) -> str:
    if not value:
        return "Без срока"

    dt = datetime.fromisoformat(value)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(timezone))

    local = dt.astimezone(ZoneInfo(timezone))
    return local.strftime("%d.%m.%Y %H:%M")


def format_date_only(value: str | None, timezone: str) -> str:
    if not value:
        return "Без даты"

    dt = datetime.fromisoformat(value)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(timezone))

    return dt.astimezone(ZoneInfo(timezone)).strftime("%d.%m.%Y")


def format_task(task, timezone: str) -> str:
    client = f"\n👤 {task.client_name}" if task.client_name else ""
    priority_icons = {
        "low": "🟢",
        "normal": "🟡",
        "high": "🔴",
    }
    priority = priority_icons.get(task.priority, "🟡")

    return (
        f"📌 <b>Задача #{task.id}</b>\n"
        f"{priority} {task.title}"
        f"{client}\n"
        f"📅 {format_datetime(task.due_at, timezone)}"
    )


WEEKDAY_NAMES = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье",
}

WEEKDAY_BY_NAME = {value: key for key, value in WEEKDAY_NAMES.items()}
