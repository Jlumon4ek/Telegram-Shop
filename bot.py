import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
"""Importing my modules"""
from utils.config import TOKEN
from utils.register_handlers import register_handlers
from db.mongo_db import create_mongo_connection

logging.basicConfig(level=logging.INFO)

bot = Bot(token='7034430423:AAHD8aGVY3UiU1qH9dPGGuJbZQdMSn0y_Tk')
dp = Dispatcher()


async def main():
    mongo = create_mongo_connection()

    await register_handlers(dp, bot, mongo)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
