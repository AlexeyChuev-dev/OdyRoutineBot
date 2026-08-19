from datetime import timedelta

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from keyboards import main_keyboard, task_actions_keyboard
from utils import format_datetime, format_task, now


router = Router(name=__name__)


@router.message(F.text == "⏰ Напоминания")
async def reminders(message: Message, reminder_repository, config):
    tasks = reminder_repository.list_active(message.from_user.id)

    if not tasks:
        await message.answer(
            "⏰ Активных напоминаний нет.",
            reply_markup=main_keyboard(),
        )
        return

    await message.answer(
        f"⏰ Активных напоминаний: {len(tasks)}",
        reply_markup=main_keyboard(),
    )

    for task in tasks:
        await message.answer(
            format_task(task, config.timezone)
            + f"\n🔔 {format_datetime(task.remind_at, config.timezone)}",
            reply_markup=task_actions_keyboard(task.id),
        )


@router.callback_query(F.data.startswith("reminder:snooze60:"))
async def snooze(callback: CallbackQuery, task_repository, config):
    task_id = int(callback.data.rsplit(":", 1)[1])
    task = task_repository.get(task_id, callback.from_user.id)

    if not task:
        await callback.answer("Задача не найдена.")
        return

    remind_at = (now(config.timezone) + timedelta(hours=1)).isoformat()
    task_repository.set_reminder(
        task_id,
        callback.from_user.id,
        remind_at,
    )
    await callback.answer("Напомню через час")
