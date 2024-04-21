from aiogram import types
from aiogram.filters.command import Command
from aiogram import F
from aiogram.fsm.context import FSMContext

"""Importing my own modules"""
from keyboards.reply_keyboards import main_buttons
from db.mongo_db import add_user


async def register_command_handlers(dp, bot, mongo):
    @dp.message(Command("start"))
    async def start(message: types.Message):
        user_id = message.from_user.id
        full_name = message.from_user.full_name
        username = message.from_user.username
        message_text = await add_user(mongo, user_id, full_name, username)

        keyboard = await main_buttons(mongo, user_id)

        await message.reply(message_text, reply_markup=keyboard)

    @dp.message(Command("cancel"))
    async def cancel(message: types.Message,  state: FSMContext):
        await message.reply("Operation canceled")
        user_id = message.from_user.id
        keyboard = await main_buttons(mongo, user_id)
        await state.clear()
        await message.reply("Hello! How can I help?", reply_markup=keyboard)

    @dp.message(Command("help"))
    async def help_command(message: types.Message):
        await message.reply("For any questions please contact me: \n\nTG: https://t.me/xwikkwix")
