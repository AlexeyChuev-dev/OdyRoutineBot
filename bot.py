import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import load_config
from database import init_db
from handlers import get_routers
from repositories.client_repository import ClientRepository
from repositories.person_repository import PersonRepository
from repositories.recurring_repository import RecurringRepository
from repositories.reminder_repository import ReminderRepository
from repositories.task_repository import TaskRepository
from repositories.user_repository import UserRepository
from scheduler import BotScheduler
from services.client_service import ClientService
from services.recurring_service import RecurringService
from services.reminder_service import ReminderService
from services.task_service import TaskService


async def main():
    logging.basicConfig(level=logging.INFO)

    config = load_config()
    init_db(config.database_path)

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher(storage=MemoryStorage())

    task_repository = TaskRepository(config.database_path)
    client_repository = ClientRepository(config.database_path)
    person_repository = PersonRepository(config.database_path)
    recurring_repository = RecurringRepository(config.database_path)
    user_repository = UserRepository(config.database_path)
    reminder_repository = ReminderRepository(task_repository)

    task_service = TaskService(task_repository, config.timezone)
    client_service = ClientService(client_repository)
    reminder_service = ReminderService()
    recurring_service = RecurringService(config.timezone)

    for router in get_routers():
        dp.include_router(router)

    scheduler = BotScheduler(
        bot=bot,
        config=config,
        task_repository=task_repository,
        reminder_repository=reminder_repository,
        recurring_repository=recurring_repository,
        recurring_service=recurring_service,
        user_repository=user_repository,
        task_service=task_service,
    )
    scheduler.start()

    try:
        await dp.start_polling(
            bot,
            config=config,
            task_repository=task_repository,
            client_repository=client_repository,
            person_repository=person_repository,
            recurring_repository=recurring_repository,
            user_repository=user_repository,
            reminder_repository=reminder_repository,
            task_service=task_service,
            client_service=client_service,
            reminder_service=reminder_service,
            recurring_service=recurring_service,
        )
    finally:
        await scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
