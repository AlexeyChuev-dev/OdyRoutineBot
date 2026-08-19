from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards import (
    cancel_keyboard,
    main_keyboard,
    people_keyboard,
    person_actions_keyboard,
)
from states import NewPerson


router = Router(name=__name__)


@router.message(F.text == "👤 Люди")
async def people(message: Message, person_repository):
    items = person_repository.list(message.from_user.id)
    text = (
        "👤 <b>Люди</b>\n\n"
        "Добавь человека, чтобы ставить ему задачи. "
        "Он должен хотя бы один раз запустить этого бота через /start."
    )
    await message.answer(text, reply_markup=people_keyboard(items))


@router.callback_query(F.data == "person:add")
async def person_add(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(NewPerson.username)
    await callback.message.answer(
        "Введи Telegram username человека, например @artem.\n\n"
        "Важно: человек должен хотя бы один раз запустить этого бота через /start.",
        reply_markup=cancel_keyboard(),
    )
    await callback.answer()


@router.message(NewPerson.username, F.text == "❌ Отмена")
@router.message(NewPerson.alias, F.text == "❌ Отмена")
async def person_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменено.", reply_markup=main_keyboard())


@router.message(NewPerson.username)
async def person_username(
    message: Message,
    state: FSMContext,
    user_repository,
):
    username = (message.text or "").strip()
    user = user_repository.find_by_username(username)

    if not user:
        await message.answer(
            "Не нашёл этого пользователя. Попроси его открыть бота, нажать /start, "
            "а потом попробуй снова."
        )
        return

    if user["id"] == message.from_user.id:
        await message.answer("Себя добавлять не нужно — свои задачи и так доступны.")
        return

    await state.update_data(target_user_id=user["id"], username=user["username"])
    await state.set_state(NewPerson.alias)
    suggested = user.get("first_name") or user.get("username") or "человек"
    await message.answer(
        f"Как будем называть человека в быстрых командах?\n"
        f"Например: <b>{suggested}</b>\n\n"
        "Можно будет писать как в обычной форме имени, так и в падеже:\n"
        "«Таска Артем проверить кассу» или «Таска Артему дай доступы»."
    )


@router.message(NewPerson.alias)
async def person_alias(
    message: Message,
    state: FSMContext,
    person_repository,
):
    alias = (message.text or "").strip()
    if not alias or " " in alias:
        await message.answer("Алиас должен быть одним словом, например Артем.")
        return

    data = await state.get_data()
    person_id, error = person_repository.create(
        owner_user_id=message.from_user.id,
        target_user_id=data["target_user_id"],
        alias=alias,
    )

    if error:
        await message.answer(error, reply_markup=main_keyboard())
        await state.clear()
        return

    await state.clear()
    await message.answer(
        f"✅ <b>{alias}</b> добавлен.\n\n"
        "Примеры быстрых команд:\n"
        f"<code>Таска {alias} проверить задачу</code>\n"
        f"<code>Задача @{data['username']} проверить задачу</code>\n\n"
        "Падеж имени можно писать естественно — бот попробует распознать его по основе.",
        reply_markup=main_keyboard(),
    )


@router.callback_query(F.data.startswith("person:view:"))
async def person_view(callback: CallbackQuery, person_repository):
    person_id = int(callback.data.rsplit(":", 1)[1])
    person = person_repository.get(person_id, callback.from_user.id)
    if not person:
        await callback.answer("Человек не найден.")
        return

    username = f"@{person.username}" if person.username else "без username"
    await callback.message.answer(
        f"👤 <b>{person.alias}</b>\n{username}\n\n"
        f"Быстрая команда:\n"
        f"<code>Таска {person.alias} проверить задачу</code>",
        reply_markup=person_actions_keyboard(person.id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("person:delete:"))
async def person_delete(callback: CallbackQuery, person_repository):
    person_id = int(callback.data.rsplit(":", 1)[1])
    if not person_repository.delete(person_id, callback.from_user.id):
        await callback.answer("Человек не найден.")
        return

    await callback.message.edit_text("🗑 Человек удалён из списка.")
    await callback.answer("Удалено")
