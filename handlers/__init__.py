from .start import router as start_router
from .tasks import router as tasks_router
from .reminders import router as reminders_router
from .overdue import router as overdue_router
from .clients import router as clients_router
from .recurring import router as recurring_router
from .settings import router as settings_router


def get_routers():
    return [
        start_router,
        tasks_router,
        reminders_router,
        overdue_router,
        clients_router,
        recurring_router,
        settings_router,
    ]
