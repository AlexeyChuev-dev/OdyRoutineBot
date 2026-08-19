from repositories.task_repository import TaskRepository


class ReminderRepository:
    """
    Напоминание хранится внутри tasks.remind_at.
    Этот репозиторий оставлен отдельным, чтобы позже можно было
    без переделки handlers/services вынести напоминания в свою таблицу.
    """

    def __init__(self, task_repository: TaskRepository):
        self.tasks = task_repository

    def list_active(self, user_id: int):
        return self.tasks.list_active_reminders(user_id)

    def list_due(self, now_iso: str):
        return self.tasks.list_due_reminders(now_iso)

    def mark_sent(self, task_id: int):
        self.tasks.mark_reminder_sent(task_id)
