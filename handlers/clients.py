from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards import (
    cancel_keyboard,
    client_actions_keyboard,
    client_list_keyboard,
    main_keyboard,
    task_actions_keyboard,
)
from states import NewClient
from utils import format_task


router = Router(name=__name__)


@router.message(F.text == "👥 Клиенты")
async def clients(message: Message, client_repository):
    items = client_repository.list(message.from_user.id)
    await message.answer(
        "👥 Клиенты:",
        reply_markup=client_list_keyboard(items),
    )


@router.callback_query(F.data == "client:add")
async def add_client(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(NewClient.name)
    await callback.message.answer(
        "Название клиента:",
        reply_markup=cancel_keyboard(),
    )
    await callback.answer()


@router.message(NewClient.name, F.text == "❌ Отмена")
@router.message(NewClient.notes, F.text == "❌ Отмена")
async def cancel_client(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменено.", reply_markup=main_keyboard())


@router.message(NewClient.name)
async def client_name(message: Message, state: FSMContext):
    await state.update_data(name=(message.text or "").strip())
    await state.set_state(NewClient.notes)
    await message.answer(
        "Добавь заметку о клиенте или отправь «-», если она не нужна."
    )


@router.message(NewClient.notes)
async def client_notes(
    message: Message,
    state: FSMContext,
    client_service,
):
    data = await state.get_data()
    notes = None if message.text.strip() == "-" else message.text.strip()

    client_id, error = client_service.create(
        message.from_user.id,
        data["name"],
        notes,
    )

    if error:
        await message.answer(error, reply_markup=main_keyboard())
        await state.clear()
        return

    await state.clear()
    await message.answer(
        f"✅ Клиент #{client_id} добавлен.",
        reply_markup=main_keyboard(),
    )


@router.callback_query(F.data.startswith("client:view:"))
async def view_client(callback: CallbackQuery, client_repository):
    client_id = int(callback.data.rsplit(":", 1)[1])
    client = client_repository.get(client_id, callback.from_user.id)

    if not client:
        await callback.answer("Клиент не найден.")
        return

    notes = client.notes or "Без заметок"
    await callback.message.answer(
        f"👤 <b>{client.name}</b>\n\n{notes}",
        reply_markup=client_actions_keyboard(client.id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("client:tasks:"))
async def client_tasks(
    callback: CallbackQuery,
    client_repository,
    task_repository,
    config,
):
    client_id = int(callback.data.rsplit(":", 1)[1])
    client = client_repository.get(client_id, callback.from_user.id)

    if not client:
        await callback.answer("Клиент не найден.")
        return

    tasks = task_repository.list_for_client(
        callback.from_user.id,
        client_id,
    )

    if not tasks:
        await callback.message.answer(
            f"У {client.name} активных задач нет."
        )
    else:
        await callback.message.answer(
            f"📋 Задачи: {client.name}"
        )
        for task in tasks:
            await callback.message.answer(
                format_task(task, config.timezone),
                reply_markup=task_actions_keyboard(task.id),
            )

    await callback.answer()


@router.callback_query(F.data.startswith("client:delete:"))
async def delete_client(callback: CallbackQuery, client_repository):
    client_id = int(callback.data.rsplit(":", 1)[1])

    if not client_repository.delete(client_id, callback.from_user.id):
        await callback.answer("Клиент не найден.")
        return

    await callback.message.edit_text("🗑 Клиент удалён.")
    await callback.answer("Удалено")
