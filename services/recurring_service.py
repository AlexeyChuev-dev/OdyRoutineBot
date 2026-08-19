from datetime import datetime, timedelta

from utils import now


class RecurringService:
    def __init__(self, timezone: str):
        self.timezone = timezone

    def first_run(self, recurrence: str, time_value: str, weekday: int | None):
        current = now(self.timezone)
        hour, minute = map(int, time_value.split(":"))

        candidate = current.replace(
            hour=hour,
            minute=minute,
            second=0,
            microsecond=0,
        )

        if recurrence == "daily":
            if candidate <= current:
                candidate += timedelta(days=1)
            return candidate

        if recurrence == "weekdays":
            while candidate <= current or candidate.weekday() >= 5:
                candidate += timedelta(days=1)
            return candidate

        if recurrence == "weekly":
            if weekday is None:
                raise ValueError("Для weekly нужен weekday")

            days_ahead = (weekday - candidate.weekday()) % 7
            candidate += timedelta(days=days_ahead)

            if candidate <= current:
                candidate += timedelta(days=7)

            return candidate

        raise ValueError("Неизвестный recurrence")

    def next_run(self, item):
        current = datetime.fromisoformat(item.next_run_at)

        if item.recurrence == "daily":
            return current + timedelta(days=1)

        if item.recurrence == "weekdays":
            candidate = current + timedelta(days=1)
            while candidate.weekday() >= 5:
                candidate += timedelta(days=1)
            return candidate

        if item.recurrence == "weekly":
            return current + timedelta(days=7)

        raise ValueError("Неизвестный recurrence")
