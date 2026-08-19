from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from keyboards import settings_keyboard


router = Router(name=__name__)


@router.message(F.text == "⚙️ Настройки")
async def settings(message: Message, user_repository):
    data = user_repository.get_settings(message.from_user.id)

    await message.answer(
        "⚙️ <b>Настройки</b>\n\n"
        f"Утренняя сводка: {data['morning_digest_time']}\n"
        f"Вечерняя сводка: {data['evening_digest_time']}",
        reply_markup=settings_keyboard(data),
    )


@router.callback_query(F.data == "settings:morning")
async def toggle_morning(callback: CallbackQuery, user_repository):
    data = user_repository.get_settings(callback.from_user.id)
    enabled = not bool(data["morning_digest_enabled"])
    user_repository.set_digest(
        callback.from_user.id,
        "morning",
        enabled,
    )
    data = user_repository.get_settings(callback.from_user.id)

    await callback.message.edit_reply_markup(
        reply_markup=settings_keyboard(data)
    )
    await callback.answer("Настройка изменена")


@router.callback_query(F.data == "settings:evening")
async def toggle_evening(callback: CallbackQuery, user_repository):
    data = user_repository.get_settings(callback.from_user.id)
    enabled = not bool(data["evening_digest_enabled"])
    user_repository.set_digest(
        callback.from_user.id,
        "evening",
        enabled,
    )
    data = user_repository.get_settings(callback.from_user.id)

    await callback.message.edit_reply_markup(
        reply_markup=settings_keyboard(data)
    )
    await callback.answer("Настройка изменена")
