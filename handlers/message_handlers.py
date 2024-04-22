from aiogram import types
from aiogram.filters.command import Command
from aiogram import F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

"""Importing my own modules"""
from db.mongo_db import get_user_balance
from db.mongo_db import get_user_role
from db.mongo_db import get_admin_list
from db.mongo_db import get_users_list
from db.mongo_db import change_users_status
from keyboards.inline_keyboards import profile_keyboard
from keyboards.inline_keyboards import get_categories_buttons
from keyboards.inline_keyboards import payment_button
from keyboards.inline_keyboards import users_managment_button
from keyboards.reply_keyboards import admin_panel_buttons
from keyboards.reply_keyboards import main_buttons
from utils.states import TopUpState
from utils.states import UnbanUserState
from utils.states import BanUserState
from utils.states import MailingState
from utils.payments import create_invoice


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

    @dp.message(TopUpState.waiting_for_amount, F.text)
    async def process_top_up_amount(message: types.Message, state: FSMContext):
        amount = message.text
        if amount.isdigit() is False:
            await message.answer("Amount must be a number")

        uuid, link = await create_invoice(amount=amount)
        if link:
            keyboard = await payment_button(uuid, link)
            await message.answer("Click on the button to pay", reply_markup=keyboard)
        await state.clear()

    @dp.message(F.text.lower() == "admin panel")
    async def admin_panel(message: types.Message):
        user_id = message.from_user.id
        user_role = await get_user_role(mongo, user_id)
        if user_role == 'admin':
            keyboard = await admin_panel_buttons(mongo, user_id)
            await message.answer("You have access to the admin panel", reply_markup=keyboard)
        else:
            await message.answer("Wrong message, try again.")

    @dp.message(F.text.lower() == "mailing")
    async def mailing(message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        user_role = await get_user_role(mongo, user_id)
        if user_role == 'admin':
            await message.answer("Input message for mailing")
            await state.set_state(MailingState.waiting_for_message)
        else:
            await message.answer("Wrong message, try again.")

    @dp.message(F.text.lower() == "admins management")
    async def admins_management(message: types.Message):
        user_id = message.from_user.id
        user_role = await get_user_role(mongo, user_id)
        if user_role == 'admin':
            message_text = await get_admin_list(mongo)
            await message.reply(message_text)
        else:
            await message.answer("Wrong message, try again.")

    @dp.message(F.text.lower() == "users management")
    async def users_management(message: types.Message):
        user_id = message.from_user.id
        user_role = await get_user_role(mongo, user_id)
        if user_role == 'admin':
            message_text = await get_users_list(mongo)
            keyboard = await users_managment_button()
            await message.reply(message_text, reply_markup=keyboard)
        else:
            await message.answer("Wrong message, try again.")

    @dp.message(F.text.lower() == "back to main menu")
    async def back_to_main_menu(message: types.Message):
        user_id = message.from_user.id
        user_role = await get_user_role(mongo, user_id)
        if user_role == 'admin':
            keyboard = await main_buttons(mongo, message.from_user.id)
            await message.reply("You are back to the main menu", reply_markup=keyboard)
        else:
            await message.answer("Wrong message, try again.")

    @dp.message(BanUserState.waiting_for_user_id, F.text)
    async def ban_user(message: types.Message, state: FSMContext):
        user_id = message.text
        if user_id.isdigit() is False:
            await message.answer("User ID must be a number")

        message_text = await change_users_status(mongo, user_id, True)
        await message.answer(message_text)
        await state.clear()

    @dp.message(UnbanUserState.waiting_for_user_id, F.text)
    async def unban_user(message: types.Message, state: FSMContext):
        user_id = message.text
        if user_id.isdigit() is False:
            await message.answer("User ID must be a number")

        message_text = await change_users_status(mongo, user_id, False)
        await message.answer(message_text)

    @dp.message(F.text.lower() == "all products")
    async def all_products(message: types.Message):
        keyboards = await get_categories_buttons(mongo)
        await message.reply("All products:", reply_markup=keyboards)
