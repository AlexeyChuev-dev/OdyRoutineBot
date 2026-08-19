from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📋 Сегодня"),
                KeyboardButton(text="➕ Новая задача"),
            ],
            [
                KeyboardButton(text="⏰ Напоминания"),
                KeyboardButton(text="🔴 Просрочено"),
            ],
            [
                KeyboardButton(text="👤 Люди"),
                KeyboardButton(text="📤 Я поставил"),
            ],
            [
                KeyboardButton(text="👥 Клиенты"),
                KeyboardButton(text="🔁 Регулярные"),
            ],
            [
                KeyboardButton(text="📆 Все задачи"),
                KeyboardButton(text="⚙️ Настройки"),
            ],
        ],
        resize_keyboard=True,
    )


def cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True,
    )


def date_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Сегодня"),
                KeyboardButton(text="Завтра"),
            ],
            [KeyboardButton(text="Без даты")],
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def time_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="09:00"),
                KeyboardButton(text="12:00"),
                KeyboardButton(text="15:00"),
            ],
            [
                KeyboardButton(text="18:00"),
                KeyboardButton(text="Без времени"),
            ],
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def reminder_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="За 15 минут"),
                KeyboardButton(text="За 1 час"),
            ],
            [
                KeyboardButton(text="В момент срока"),
                KeyboardButton(text="Без напоминания"),
            ],
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def task_actions_keyboard(task_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Выполнено",
                    callback_data=f"task:complete:{task_id}",
                ),
                InlineKeyboardButton(
                    text="📅 Перенести",
                    callback_data=f"task:move:{task_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🌅 На завтра",
                    callback_data=f"task:tomorrow:{task_id}",
                ),
                InlineKeyboardButton(
                    text="🗑 Удалить",
                    callback_data=f"task:delete:{task_id}",
                ),
            ],
        ]
    )


def reminder_actions_keyboard(task_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Выполнено",
                    callback_data=f"task:complete:{task_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⏰ +1 час",
                    callback_data=f"reminder:snooze60:{task_id}",
                ),
                InlineKeyboardButton(
                    text="🌅 Завтра",
                    callback_data=f"task:tomorrow:{task_id}",
                ),
            ],
        ]
    )


def client_list_keyboard(clients):
    rows = [
        [
            InlineKeyboardButton(
                text=client.name,
                callback_data=f"client:view:{client.id}",
            )
        ]
        for client in clients
    ]
    rows.append(
        [
            InlineKeyboardButton(
                text="➕ Добавить клиента",
                callback_data="client:add",
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def client_actions_keyboard(client_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📋 Задачи клиента",
                    callback_data=f"client:tasks:{client_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Удалить клиента",
                    callback_data=f"client:delete:{client_id}",
                ),
            ],
        ]
    )


def task_client_keyboard(clients):
    rows = [
        [
            InlineKeyboardButton(
                text=client.name,
                callback_data=f"taskclient:{client.id}",
            )
        ]
        for client in clients
    ]
    rows.append(
        [
            InlineKeyboardButton(
                text="Без клиента",
                callback_data="taskclient:none",
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def people_keyboard(people):
    rows = [
        [
            InlineKeyboardButton(
                text=f"{person.alias} (@{person.username})" if person.username else person.alias,
                callback_data=f"person:view:{person.id}",
            )
        ]
        for person in people
    ]
    rows.append(
        [
            InlineKeyboardButton(
                text="➕ Добавить человека",
                callback_data="person:add",
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def person_actions_keyboard(person_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🗑 Удалить",
                    callback_data=f"person:delete:{person_id}",
                )
            ]
        ]
    )


def recurrence_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Каждый день"),
                KeyboardButton(text="По будням"),
            ],
            [KeyboardButton(text="Раз в неделю")],
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def weekday_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Понедельник"),
                KeyboardButton(text="Вторник"),
            ],
            [
                KeyboardButton(text="Среда"),
                KeyboardButton(text="Четверг"),
            ],
            [
                KeyboardButton(text="Пятница"),
                KeyboardButton(text="Суббота"),
            ],
            [KeyboardButton(text="Воскресенье")],
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def settings_keyboard(settings):
    morning = "✅" if settings["morning_digest_enabled"] else "❌"
    evening = "✅" if settings["evening_digest_enabled"] else "❌"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{morning} Утренняя сводка",
                    callback_data="settings:morning",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{evening} Вечерняя сводка",
                    callback_data="settings:evening",
                )
            ],
        ]
    )
