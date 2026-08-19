from aiogram.fsm.state import State, StatesGroup


class NewTask(StatesGroup):
    title = State()
    date = State()
    time = State()
    client = State()
    reminder = State()


class MoveTask(StatesGroup):
    task_id = State()
    date = State()
    time = State()


class NewClient(StatesGroup):
    name = State()
    notes = State()


class NewRecurringTask(StatesGroup):
    title = State()
    recurrence = State()
    weekday = State()
    time = State()
