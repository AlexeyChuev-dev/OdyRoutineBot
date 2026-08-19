import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Config:
    bot_token: str
    timezone: str = "Europe/Moscow"
    database_path: str = str(BASE_DIR / "data" / "bot.db")
    morning_digest_time: str = "09:00"
    evening_digest_time: str = "18:30"


def load_config() -> Config:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN не найден в .env")

    return Config(
        bot_token=token,
        timezone=os.getenv("BOT_TIMEZONE", "Europe/Moscow"),
        database_path=os.getenv(
            "DATABASE_PATH",
            str(BASE_DIR / "data" / "bot.db"),
        ),
        morning_digest_time=os.getenv("MORNING_DIGEST_TIME", "09:00"),
        evening_digest_time=os.getenv("EVENING_DIGEST_TIME", "18:30"),
    )
