from aiogram import F, Router
from aiogram.types import Message

from keyboards import main_keyboard, task_actions_keyboard
from utils import format_task


router = Router(name=__name__)


@router.message(F.text == "🔴 Просрочено")
async def overdue(message: Message, task_service, config):
    tasks = task_service.overdue(message.from_user.id)

    if not tasks:
        await message.answer(
            "🎉 Просроченных задач нет.",
            reply_markup=main_keyboard(),
        )
        return

    await message.answer(
        f"🔴 Просрочено: {len(tasks)}",
        reply_markup=main_keyboard(),
    )

    for task in tasks:
        await message.answer(
            format_task(task, config.timezone),
            reply_markup=task_actions_keyboard(task.id),
        )
