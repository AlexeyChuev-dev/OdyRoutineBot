from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from keyboards import reminder_actions_keyboard
from utils import format_task, now


class BotScheduler:
    def __init__(
        self,
        bot,
        config,
        task_repository,
        reminder_repository,
        recurring_repository,
        recurring_service,
        user_repository,
        task_service,
    ):
        self.bot = bot
        self.config = config
        self.task_repository = task_repository
        self.reminder_repository = reminder_repository
        self.recurring_repository = recurring_repository
        self.recurring_service = recurring_service
        self.user_repository = user_repository
        self.task_service = task_service

        self.scheduler = AsyncIOScheduler(
            timezone=config.timezone,
        )

    def start(self):
        self.scheduler.add_job(
            self.process_reminders,
            "interval",
            seconds=30,
            max_instances=1,
            coalesce=True,
        )

        self.scheduler.add_job(
            self.process_recurring,
            "interval",
            seconds=30,
            max_instances=1,
            coalesce=True,
        )

        self.scheduler.add_job(
            self.process_digests,
            "cron",
            minute="*",
            max_instances=1,
            coalesce=True,
        )

        self.scheduler.start()

    async def shutdown(self):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    async def process_reminders(self):
        current_iso = now(self.config.timezone).isoformat()
        tasks = self.reminder_repository.list_due(current_iso)

        for task in tasks:
            try:
                await self.bot.send_message(
                    task.user_id,
                    "🔔 <b>Напоминание</b>\n\n"
                    + format_task(task, self.config.timezone),
                    reply_markup=reminder_actions_keyboard(task.id),
                )
                self.reminder_repository.mark_sent(task.id)
            except Exception as exc:
                print(f"Reminder error for task {task.id}: {exc}")

    async def process_recurring(self):
        current = now(self.config.timezone)
        items = self.recurring_repository.list_due(current.isoformat())

        for item in items:
            try:
                due_at = datetime.fromisoformat(item.next_run_at)
                self.task_repository.create(
                    user_id=item.user_id,
                    title=item.title,
                    client_id=item.client_id,
                    due_at=due_at.isoformat(),
                    remind_at=due_at.isoformat(),
                )

                next_run = self.recurring_service.next_run(item)
                self.recurring_repository.update_next_run(
                    item.id,
                    next_run.isoformat(),
                )
            except Exception as exc:
                print(f"Recurring error for {item.id}: {exc}")

    async def process_digests(self):
        current = now(self.config.timezone)
        clock = current.strftime("%H:%M")
        users = self.user_repository.list_digest_users()

        for user in users:
            user_id = user["user_id"]

            try:
                if (
                    user["morning_digest_enabled"]
                    and user["morning_digest_time"] == clock
                ):
                    tasks = self.task_service.today(user_id)
                    overdue = self.task_service.overdue(user_id)

                    text = (
                        "🌅 <b>Утренняя сводка</b>\n\n"
                        f"На сегодня: {len(tasks)}\n"
                        f"Просрочено: {len(overdue)}"
                    )
                    await self.bot.send_message(user_id, text)

                if (
                    user["evening_digest_enabled"]
                    and user["evening_digest_time"] == clock
                ):
                    tasks = self.task_service.today(user_id)
                    overdue = self.task_service.overdue(user_id)

                    text = (
                        "🌙 <b>Итоги дня</b>\n\n"
                        f"Осталось на сегодня: {len(tasks)}\n"
                        f"Просрочено: {len(overdue)}"
                    )
                    await self.bot.send_message(user_id, text)

            except Exception as exc:
                print(f"Digest error for user {user_id}: {exc}")
