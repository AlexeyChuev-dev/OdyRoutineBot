from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards import main_keyboard


router = Router(name=__name__)


@router.message(CommandStart())
async def start_handler(message: Message, user_repository):
    user_repository.ensure_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )

    await message.answer(
        "Привет 👋\n\n"
        "Это твой личный бот для задач и напоминаний.\n"
        "Теперь сюда можно назначать задачи и другим людям.\n\n"
        "Выбери нужный раздел:",
        reply_markup=main_keyboard(),
    )
