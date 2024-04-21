from aiogram import types
from aiogram.filters.command import Command
from aiogram import F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

"""Importing my own modules"""
from db.mongo_db import get_user_balance
from keyboards.inline_keyboards import profile_keyboard


async def register_message_handlers(dp, bot, mongo):
    @dp.message(F.text.lower() == "rules")
    async def rules(message: types.Message):
        with open("./files/txt/rules_message.txt", "r", encoding="utf-8") as file:
            rules_text = file.read()
        await message.reply(rules_text)

    @dp.message(F.text.lower() == "help")
    async def help(message: types.Message):
        await message.reply("For any questions please contact me: \n\nTG: https://t.me/xwikkwix")

    @dp.message(F.text.lower() == "about us")
    async def about_us(message: types.Message):
        with open(".//files//txt//about_us_message.txt", "r", encoding="utf-8") as file:
            about_us_text = file.read()
        await message.reply(about_us_text)

    @dp.message(F.text.lower() == "profile")
    async def profile(message: types.Message):
        user_id = message.from_user.id
        balance = await get_user_balance(mongo, message.from_user.id)
        user_info = {
            "Username": message.from_user.full_name,
            "ID": user_id,
            "Balance": f"{balance}$"
        }

        profile_message = "\n".join(
            [f"{key}: {value}" for key, value in user_info.items()])
        keyboard = await profile_keyboard()
        await message.reply(profile_message, reply_markup=keyboard)
