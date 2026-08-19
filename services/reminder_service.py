from datetime import datetime, timedelta


class ReminderService:
    @staticmethod
    def calculate_reminder(due_at: str | None, option: str) -> str | None:
        if not due_at or option == "Без напоминания":
            return None

        due = datetime.fromisoformat(due_at)

        if option == "За 15 минут":
            return (due - timedelta(minutes=15)).isoformat()

        if option == "За 1 час":
            return (due - timedelta(hours=1)).isoformat()

        if option == "В момент срока":
            return due.isoformat()

        return None
