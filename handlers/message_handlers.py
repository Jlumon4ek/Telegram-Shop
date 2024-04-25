from aiogram import types
from aiogram.filters.command import Command
from aiogram import F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

"""Importing my own modules"""
from db.mongo_db import get_user_balance
from db.mongo_db import get_user_role
from db.mongo_db import get_admin_list
from db.mongo_db import structure_data
from db.mongo_db import get_users_list
from db.mongo_db import add_subcategory_db
from db.mongo_db import add_category
from db.mongo_db import add_product_db
from db.mongo_db import multiple_buy_update
from db.mongo_db import change_users_status
from keyboards.inline_keyboards import profile_keyboard
from keyboards.inline_keyboards import get_categories_buttons
from keyboards.inline_keyboards import payment_button
from keyboards.inline_keyboards import choose_category
from keyboards.inline_keyboards import users_managment_button
from keyboards.inline_keyboards import get_admin_categories_buttons
from keyboards.reply_keyboards import admin_panel_buttons
from keyboards.reply_keyboards import main_buttons
from utils.states import TopUpState
from utils.states import UnbanUserState
from utils.states import BanUserState
from utils.states import CountOfProductsState
from utils.states import CategoryNameState
from utils.states import ProductState
from utils.states import MailingState
from utils.payments import create_invoice
from utils.states import SubcategoryForm


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

    @dp.message(F.text.lower() == "category management")
    async def category_management(message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        user_role = await get_user_role(mongo, user_id)
        if user_role == 'admin':
            await message.reply("Input category name for adding: ")
            await state.set_state(CategoryNameState.waiting_for_category_name,)

    @dp.message(CategoryNameState.waiting_for_category_name, F.text)
    async def input_add_category(message: types.Message, state: FSMContext):
        category_name = message.text
        message_text = await add_category(mongo, category_name)
        await message.answer(message_text)
        await state.clear()

    @dp.message(F.text.lower() == "product availability")
    async def product_availability(message: types.Message):
        message_text = await structure_data(mongo)
        await message.answer(f"Product availability\n {message_text}")

    @dp.message(CountOfProductsState.waiting_for_count, F.text)
    async def input_count_of_products(message: types.Message, state: FSMContext):
        data = await state.get_data()
        user_id = message.from_user.id
        subcategory_id = data.get('subcategory_id')
        group_by = data.get('group_by')
        group_value = data.get('group_value')
        count = message.text
        if count.isdigit() is False:
            await message.answer("Count must be a number")

        else:
            message_text = await multiple_buy_update(mongo, user_id, subcategory_id,
                                                     group_by, group_value, count)

            await message.answer(f"{message_text}")
        await state.clear()

    @dp.message(F.text.lower() == "product management")
    async def category_management(message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        user_role = await get_user_role(mongo, user_id)
        if user_role == 'admin':
            keyboards = await get_admin_categories_buttons(mongo)
            await message.reply("Choose category for adding products: ", reply_markup=keyboards)

    @dp.message(ProductState.waiting_for_product, F.text)
    async def input_products(message: types.Message, state: FSMContext):
        products = message.text
        data = await state.get_data()
        subcategory_id = data.get('subcategory_id')

        message_text = await add_product_db(mongo, subcategory_id, products)
        await message.answer(f"{message_text}")
        await state.clear()

    @dp.message(F.text.lower() == "subcategory managment")
    async def subcategory_management(message: types.Message, state: FSMContext):
        message_text = await choose_category(mongo)
        await message.answer(f"Subcategory management\n Choose category for adding subcategory: ", reply_markup=message_text)

    @dp.message(SubcategoryForm.waiting_for_subcategory_name, F.text)
    async def input_subcategory_name(message: types.Message, state: FSMContext):
        subcategory_name = message.text
        await state.update_data(subcategory_name=subcategory_name)
        await message.answer("Input subcategory price: ")
        await state.set_state(SubcategoryForm.waiting_for_subcategory_price, )

    @dp.message(SubcategoryForm.waiting_for_subcategory_price, F.text)
    async def input_subcategory_price(message: types.Message, state: FSMContext):
        subcategory_price = message.text
        await state.update_data(subcategory_price=subcategory_price)
        await message.answer("Enter the fields that will be in the product, separated by commas: ")
        await state.set_state(SubcategoryForm.waiting_for_subcategory_fileds,)

    @dp.message(SubcategoryForm.waiting_for_subcategory_fileds, F.text)
    async def input_subcategory_fields(message: types.Message, state: FSMContext):
        fields = message.text
        await state.update_data(fields=fields)
        await message.answer("Input product subgroups, if you don’t need to group them, enter none: ")
        await state.set_state(SubcategoryForm.waiting_for_subcategory_group_by, )

    @dp.message(SubcategoryForm.waiting_for_subcategory_group_by, F.text)
    async def input_subcategory_group_by(message: types.Message, state: FSMContext):
        group_by = message.text
        data = await state.get_data()
        category_id = data.get('category_id')
        subcategory_name = data.get('subcategory_name')
        subcategory_price = data.get('subcategory_price')
        fields = data.get('fields')
        message_text = await add_subcategory_db(mongo, category_id, subcategory_name, subcategory_price, group_by, fields)
        await message.answer(f"{message_text}")
