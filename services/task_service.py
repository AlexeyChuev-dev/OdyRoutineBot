from datetime import timedelta

from repositories.task_repository import TaskRepository
from utils import now


class TaskService:
    def __init__(self, repository: TaskRepository, timezone: str):
        self.repository = repository
        self.timezone = timezone

    def today(self, user_id: int):
        current = now(self.timezone)
        start = current.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        return self.repository.list_today(
            user_id,
            start.isoformat(),
            end.isoformat(),
        )

    def overdue(self, user_id: int):
        return self.repository.list_overdue(
            user_id,
            now(self.timezone).isoformat(),
        )

    def all_active(self, user_id: int):
        return self.repository.list_active(user_id)

    def tomorrow_due(self, original_due_at: str | None) -> str:
        current = now(self.timezone)

        if original_due_at:
            from datetime import datetime
            old = datetime.fromisoformat(original_due_at)
            target = (current + timedelta(days=1)).replace(
                hour=old.hour,
                minute=old.minute,
                second=0,
                microsecond=0,
            )
        else:
            target = (current + timedelta(days=1)).replace(
                hour=18,
                minute=0,
                second=0,
                microsecond=0,
            )

        return target.isoformat()
