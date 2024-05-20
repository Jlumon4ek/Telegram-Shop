import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
"""Importing my modules"""
from utils.config import TOKEN
from utils.register_handlers import register_handlers
from db.mongo_db import create_mongo_connection
from aiogram.exceptions import TelegramServerError, TelegramNetworkError, TelegramAPIError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main():
    mongo = create_mongo_connection()

    await register_handlers(dp, bot, mongo)

    retry_attempts = 5
    for attempt in range(retry_attempts):
        try:
            logger.info("Start polling")
            await dp.start_polling(bot)
            break
        except TelegramNetworkError as e:
            logger.error(f"Network error: {e}")
            await asyncio.sleep(2 ** attempt)
        except TelegramAPIError as e:
            logger.error(f"API error: {e}")
            await asyncio.sleep(2 ** attempt)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            await asyncio.sleep(2 ** attempt)
    else:
        logger.error("Max retry attempts reached. Could not start bot.")

if __name__ == "__main__":
    asyncio.run(main())
