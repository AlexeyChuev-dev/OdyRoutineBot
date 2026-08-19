from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards import (
    cancel_keyboard,
    main_keyboard,
    recurrence_keyboard,
    time_keyboard,
    weekday_keyboard,
)
from states import NewRecurringTask
from utils import WEEKDAY_BY_NAME, WEEKDAY_NAMES, format_datetime


router = Router(name=__name__)


@router.message(F.text == "🔁 Регулярные")
async def recurring(message: Message, recurring_repository, config):
    items = recurring_repository.list(message.from_user.id)

    if not items:
        await message.answer(
            "🔁 Регулярных задач пока нет.\n\n"
            "Нажми «➕ Добавить регулярную».",
            reply_markup=main_keyboard(),
        )
    else:
        text = ["🔁 <b>Регулярные задачи</b>\n"]
        for item in items:
            recurrence = {
                "daily": "каждый день",
                "weekdays": "по будням",
                "weekly": f"каждый {WEEKDAY_NAMES.get(item.weekday, '').lower()}",
            }.get(item.recurrence, item.recurrence)

            text.append(
                f"#{item.id} — {item.title}\n"
                f"↻ {recurrence} в {item.time}\n"
                f"Следующая: {format_datetime(item.next_run_at, config.timezone)}\n"
            )

        await message.answer("\n".join(text), reply_markup=main_keyboard())

    await message.answer(
        "Чтобы создать новую регулярную задачу, отправь /recurring"
    )


@router.message(F.text == "/recurring")
async def recurring_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(NewRecurringTask.title)
    await message.answer(
        "Название регулярной задачи:",
        reply_markup=cancel_keyboard(),
    )


@router.message(NewRecurringTask.title, F.text == "❌ Отмена")
@router.message(NewRecurringTask.recurrence, F.text == "❌ Отмена")
@router.message(NewRecurringTask.weekday, F.text == "❌ Отмена")
@router.message(NewRecurringTask.time, F.text == "❌ Отмена")
async def recurring_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменено.", reply_markup=main_keyboard())


@router.message(NewRecurringTask.title)
async def recurring_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(NewRecurringTask.recurrence)
    await message.answer(
        "Как часто повторять?",
        reply_markup=recurrence_keyboard(),
    )


@router.message(NewRecurringTask.recurrence)
async def recurring_type(message: Message, state: FSMContext):
    mapping = {
        "Каждый день": "daily",
        "По будням": "weekdays",
        "Раз в неделю": "weekly",
    }

    recurrence = mapping.get(message.text)
    if not recurrence:
        await message.answer("Выбери вариант кнопкой.")
        return

    await state.update_data(recurrence=recurrence)

    if recurrence == "weekly":
        await state.set_state(NewRecurringTask.weekday)
        await message.answer(
            "В какой день недели?",
            reply_markup=weekday_keyboard(),
        )
        return

    await state.update_data(weekday=None)
    await state.set_state(NewRecurringTask.time)
    await message.answer("Во сколько?", reply_markup=time_keyboard())


@router.message(NewRecurringTask.weekday)
async def recurring_weekday(message: Message, state: FSMContext):
    weekday = WEEKDAY_BY_NAME.get(message.text)
    if weekday is None:
        await message.answer("Выбери день кнопкой.")
        return

    await state.update_data(weekday=weekday)
    await state.set_state(NewRecurringTask.time)
    await message.answer("Во сколько?", reply_markup=time_keyboard())


@router.message(NewRecurringTask.time)
async def recurring_time(
    message: Message,
    state: FSMContext,
    recurring_service,
    recurring_repository,
):
    if message.text == "Без времени":
        await message.answer("Для регулярной задачи нужно выбрать время.")
        return

    try:
        hour, minute = map(int, message.text.split(":"))
        if not 0 <= hour <= 23 or not 0 <= minute <= 59:
            raise ValueError
    except ValueError:
        await message.answer("Используй время ЧЧ:ММ.")
        return

    data = await state.get_data()

    first_run = recurring_service.first_run(
        data["recurrence"],
        message.text,
        data.get("weekday"),
    )

    item_id = recurring_repository.create(
        user_id=message.from_user.id,
        title=data["title"],
        recurrence=data["recurrence"],
        time=message.text,
        weekday=data.get("weekday"),
        next_run_at=first_run.isoformat(),
    )

    await state.clear()
    await message.answer(
        f"✅ Регулярная задача #{item_id} создана.",
        reply_markup=main_keyboard(),
    )
