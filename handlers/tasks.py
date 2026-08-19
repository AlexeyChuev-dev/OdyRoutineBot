from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards import (
    cancel_keyboard,
    date_keyboard,
    main_keyboard,
    reminder_keyboard,
    task_actions_keyboard,
    task_client_keyboard,
    time_keyboard,
)
from states import MoveTask, NewTask
from utils import combine_due, format_task, parse_date, parse_time


router = Router(name=__name__)


async def send_task_list(message, tasks, timezone, empty_text):
    if not tasks:
        await message.answer(empty_text, reply_markup=main_keyboard())
        return

    await message.answer(
        f"Найдено задач: {len(tasks)}",
        reply_markup=main_keyboard(),
    )

    for task in tasks:
        await message.answer(
            format_task(task, timezone),
            reply_markup=task_actions_keyboard(task.id),
        )


@router.message(F.text == "➕ Новая задача")
async def new_task(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(NewTask.title)
    await message.answer(
        "Напиши название задачи:",
        reply_markup=cancel_keyboard(),
    )


@router.message(NewTask.title, F.text == "❌ Отмена")
@router.message(NewTask.date, F.text == "❌ Отмена")
@router.message(NewTask.time, F.text == "❌ Отмена")
@router.message(NewTask.reminder, F.text == "❌ Отмена")
@router.message(MoveTask.date, F.text == "❌ Отмена")
@router.message(MoveTask.time, F.text == "❌ Отмена")
async def cancel_flow(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменено.", reply_markup=main_keyboard())


@router.message(NewTask.title)
async def new_task_title(message: Message, state: FSMContext):
    title = (message.text or "").strip()
    if not title:
        await message.answer("Название не может быть пустым.")
        return

    await state.update_data(title=title)
    await state.set_state(NewTask.date)
    await message.answer(
        "Когда выполнить?\nМожно написать дату в формате 21.08.2026.",
        reply_markup=date_keyboard(),
    )


@router.message(NewTask.date)
async def new_task_date(message: Message, state: FSMContext, config):
    try:
        date_value = parse_date(message.text, config.timezone)
    except ValueError:
        await message.answer(
            "Не понял дату. Используй формат ДД.ММ.ГГГГ, например 21.08.2026."
        )
        return

    await state.update_data(
        date=date_value.isoformat() if date_value else None
    )
    await state.set_state(NewTask.time)
    await message.answer("Во сколько?", reply_markup=time_keyboard())


@router.message(NewTask.time)
async def new_task_time(message: Message, state: FSMContext, config, client_repository):
    try:
        time_value = parse_time(message.text)
    except ValueError:
        await message.answer("Не понял время. Используй формат ЧЧ:ММ, например 14:30.")
        return

    data = await state.get_data()
    date_value = (
        datetime.fromisoformat(data["date"]).date()
        if data.get("date")
        else None
    )

    due_at = combine_due(date_value, time_value, config.timezone)
    await state.update_data(due_at=due_at)

    clients = client_repository.list(message.from_user.id)
    await state.set_state(NewTask.client)
    await message.answer(
        "Привязать задачу к клиенту?",
        reply_markup=task_client_keyboard(clients),
    )


@router.callback_query(NewTask.client, F.data.startswith("taskclient:"))
async def new_task_client(callback: CallbackQuery, state: FSMContext):
    value = callback.data.split(":", 1)[1]
    client_id = None if value == "none" else int(value)
    await state.update_data(client_id=client_id)
    await state.set_state(NewTask.reminder)

    await callback.message.answer(
        "Когда напомнить?",
        reply_markup=reminder_keyboard(),
    )
    await callback.answer()


@router.message(NewTask.reminder)
async def new_task_reminder(
    message: Message,
    state: FSMContext,
    task_repository,
    reminder_service,
    config,
):
    data = await state.get_data()
    remind_at = reminder_service.calculate_reminder(
        data.get("due_at"),
        message.text,
    )

    task_id = task_repository.create(
        user_id=message.from_user.id,
        title=data["title"],
        due_at=data.get("due_at"),
        remind_at=remind_at,
        client_id=data.get("client_id"),
    )

    task = task_repository.get(task_id, message.from_user.id)
    await state.clear()

    await message.answer("✅ Задача создана", reply_markup=main_keyboard())
    await message.answer(
        format_task(task, config.timezone),
        reply_markup=task_actions_keyboard(task.id),
    )


@router.message(F.text == "📋 Сегодня")
async def today(message: Message, task_service, config):
    tasks = task_service.today(message.from_user.id)
    await send_task_list(
        message,
        tasks,
        config.timezone,
        "📋 На сегодня задач нет.",
    )


@router.message(F.text == "📆 Все задачи")
async def all_tasks(message: Message, task_service, config):
    tasks = task_service.all_active(message.from_user.id)
    await send_task_list(
        message,
        tasks,
        config.timezone,
        "📆 Активных задач пока нет.",
    )


@router.callback_query(F.data.startswith("task:complete:"))
async def complete_task(callback: CallbackQuery, task_repository):
    task_id = int(callback.data.rsplit(":", 1)[1])
    if not task_repository.complete(task_id, callback.from_user.id):
        await callback.answer("Задача уже закрыта или не найдена.")
        return

    await callback.message.edit_text(
        callback.message.html_text + "\n\n✅ <b>Выполнено</b>"
    )
    await callback.answer("Готово")


@router.callback_query(F.data.startswith("task:delete:"))
async def delete_task(callback: CallbackQuery, task_repository):
    task_id = int(callback.data.rsplit(":", 1)[1])
    if not task_repository.delete(task_id, callback.from_user.id):
        await callback.answer("Задача не найдена.")
        return

    await callback.message.edit_text(
        callback.message.html_text + "\n\n🗑 <b>Удалено</b>"
    )
    await callback.answer("Удалено")


@router.callback_query(F.data.startswith("task:tomorrow:"))
async def tomorrow_task(callback: CallbackQuery, task_repository, task_service, config):
    task_id = int(callback.data.rsplit(":", 1)[1])
    task = task_repository.get(task_id, callback.from_user.id)

    if not task:
        await callback.answer("Задача не найдена.")
        return

    new_due = task_service.tomorrow_due(task.due_at)
    task_repository.move(task_id, callback.from_user.id, new_due, None)
    task = task_repository.get(task_id, callback.from_user.id)

    await callback.message.edit_text(
        format_task(task, config.timezone),
        reply_markup=task_actions_keyboard(task.id),
    )
    await callback.answer("Перенесено на завтра")


@router.callback_query(F.data.startswith("task:move:"))
async def move_task(callback: CallbackQuery, state: FSMContext):
    task_id = int(callback.data.rsplit(":", 1)[1])
    await state.clear()
    await state.update_data(task_id=task_id)
    await state.set_state(MoveTask.date)

    await callback.message.answer(
        "На какую дату перенести?",
        reply_markup=date_keyboard(),
    )
    await callback.answer()


@router.message(MoveTask.date)
async def move_task_date(message: Message, state: FSMContext, config):
    try:
        date_value = parse_date(message.text, config.timezone)
    except ValueError:
        await message.answer("Используй дату ДД.ММ.ГГГГ.")
        return

    if not date_value:
        await message.answer("Для переноса нужна дата.")
        return

    await state.update_data(date=date_value.isoformat())
    await state.set_state(MoveTask.time)
    await message.answer("Во сколько?", reply_markup=time_keyboard())


@router.message(MoveTask.time)
async def move_task_time(
    message: Message,
    state: FSMContext,
    task_repository,
    config,
):
    try:
        time_value = parse_time(message.text)
    except ValueError:
        await message.answer("Используй время ЧЧ:ММ.")
        return

    data = await state.get_data()
    date_value = datetime.fromisoformat(data["date"]).date()
    due_at = combine_due(date_value, time_value, config.timezone)
    task_repository.move(
        data["task_id"],
        message.from_user.id,
        due_at,
        None,
    )

    task = task_repository.get(data["task_id"], message.from_user.id)
    await state.clear()

    await message.answer("✅ Задача перенесена", reply_markup=main_keyboard())
    if task:
        await message.answer(
            format_task(task, config.timezone),
            reply_markup=task_actions_keyboard(task.id),
        )
