from aiogram import F
from aiogram import types
from aiogram.fsm.context import FSMContext
import asyncio
from aiogram.enums import ParseMode
import random

""""Importing my own modules"""
from keyboards.inline_keyboards import cancel_payment_input_button
from utils.states import TopUpState
from utils.states import BanUserState
from utils.states import UnbanUserState
from utils.states import CountOfProductsState
from utils.states import ProductState
from utils.states import SubcategoryForm
from utils.payments import invoice_cancel
from db.mongo_db import get_balance_history
from db.mongo_db import get_category_info
from db.mongo_db import get_fileds
from db.mongo_db import get_subcategory_info
from db.mongo_db import delete_favorite
from db.mongo_db import add_to_favorites
from db.mongo_db import get_group_values
from db.mongo_db import buy_product_logic
from db.mongo_db import get_product_info
from keyboards.inline_keyboards import get_subcategories_buttons
from keyboards.inline_keyboards import get_groups_buttons
from keyboards.inline_keyboards import action_buttons
from keyboards.inline_keyboards import single_group_buttons
from keyboards.inline_keyboards import get_admin_subcategories_buttons
from keyboards.inline_keyboards import get_categories_buttons
from keyboards.inline_keyboards import get_favorites_button
from keyboards.inline_keyboards import purchase_buttons


async def register_callback_query_handlers(dp, bot, mongo):
    @dp.callback_query(F.data == "add_balance")
    async def create_invoice(callback: types.CallbackQuery, state: FSMContext):
        keyboard = await cancel_payment_input_button()
        await callback.message.answer("Enter the top-up amount:", reply_markup=keyboard)
        await callback.answer()
        await state.set_state(TopUpState.waiting_for_amount, )

    @dp.callback_query(F.data.startswith("cancel_"))
    async def cancel_invoice(callback: types.CallbackQuery):
        uuid = callback.data.split('_')[1]
        response, data = await invoice_cancel(uuid)
        if response == "Success:" and data.get('status') == 'success' and 'ok' in data.get('result', []):
            message_text = f"Payment with unique identifier: {
                uuid} was cancelled."

        else:
            message_text = "An error occurred while trying to cancel the payment."

        await callback.message.edit_text(f"{message_text}")
        await callback.answer()

    @dp.callback_query(F.data == "undo_input_amount")
    async def cancel_input_amount(callback: types.CallbackQuery, state: FSMContext):
        await callback.answer()
        await callback.message.edit_text("You have canceled the operation.")
        await state.clear()

    @dp.callback_query(F.data == "balance_history")
    async def balance_history(callback: types.CallbackQuery):
        balance_history = await get_balance_history(mongo, callback.from_user.id)
        await callback.answer()
        await callback.message.answer(balance_history)

    @dp.callback_query(F.data == "ban_user_button")
    async def ban_user(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.answer("Input user ID to ban")
        await callback.answer()
        await state.set_state(BanUserState.waiting_for_user_id,)

    @dp.callback_query(F.data == "unban_user_button")
    async def unban_user(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.answer("Input user ID to unban")
        await callback.answer()
        await state.set_state(UnbanUserState.waiting_for_user_id,)

    @dp.callback_query(F.data.startswith("category_"))
    async def get_products_by_category(callback: types.CallbackQuery):
        category_id = callback.data.split('_')[1]
        category = await get_category_info(mongo, category_id)
        category_name = category.get("name")
        keyboards = await get_subcategories_buttons(mongo, category_id)
        await callback.answer()
        await callback.message.answer(f"Subcategories of {category_name}:", reply_markup=keyboards)

    @dp.callback_query(F.data.startswith("subcategory_"))
    async def get_products_by_subcategory(callback: types.CallbackQuery):
        subcategory_id = callback.data.split('_')[1]
        subcategory = await get_subcategory_info(mongo, subcategory_id)
        subcategory_name = subcategory.get("name")
        group_by = subcategory.get("group_by")
        group_by = str(group_by)
        if group_by == 'None':
            single_group = await single_group_buttons(mongo, subcategory_id, subcategory_name)
            await callback.message.answer(f"Products of subcategory {subcategory_name}:", reply_markup=single_group)

        if group_by != 'None':
            group_keyboards = await get_groups_buttons(mongo, subcategory_id, group_by)
            await callback.message.answer(f"Products of subcategory {subcategory_name}", reply_markup=group_keyboards)

        await callback.answer()

    @dp.callback_query(F.data.startswith("group_"))
    async def get_products_by_group(callback: types.CallbackQuery):
        data = callback.data.split('_')
        subcategory_id = data[1]
        group_by = data[2]
        group_value = data[3]
        user_id = callback.from_user.id
        subcategory = await get_subcategory_info(mongo, subcategory_id)
        keyboard = await action_buttons(mongo, user_id, subcategory_id, group_by, group_value)
        await callback.answer()
        await callback.message.answer(f"You have selected a product: {group_value}, from subcategory {subcategory['name']}", reply_markup=keyboard)

    @dp.callback_query(F.data.startswith("item_"))
    async def get_products_by_group(callback: types.CallbackQuery):
        data = callback.data.split('_')
        subcategory_id = data[1]
        subcategory_name = data[2]
        user_id = callback.from_user.id
        keyboard = await action_buttons(mongo, user_id, subcategory_id)
        await callback.answer()
        await callback.message.answer(f"You have selected a product: {subcategory_name}", reply_markup=keyboard)

    @dp.callback_query(lambda c: c.data.startswith('back_to_categories_button'))
    async def back_to_categories(callback_query: types.CallbackQuery):
        categories = await get_categories_buttons(mongo)
        await callback_query.message.answer("Categories:", reply_markup=categories)
        await callback_query.answer()

    @dp.callback_query(lambda c: c.data.startswith('buy_'))
    async def buy_product(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        _, group_info = callback_query.data.split('buy_', 1)
        data = group_info.split('_')
        subcategory_id = data[0]
        group_by = data[1]
        group_value = data[2]
        text = await buy_product_logic(mongo, user_id, subcategory_id, group_by, group_value)
        await callback_query.answer()
        await callback_query.message.answer(text)

    @dp.callback_query(lambda c: c.data.startswith('add_to_favorites_'))
    async def add_to_favorites_button(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        _, group_info = callback_query.data.split(
            'add_to_favorites_', 1)
        data = group_info.split('_')
        subcategory_id = data[0]
        group_by = data[1]
        group_value = data[2]
        await callback_query.answer()
        was_added, title = await add_to_favorites(mongo, user_id, subcategory_id, group_by, group_value)
        if was_added:
            message_text = f"{title} has been added to your favorites."

        reply_markup = await action_buttons(
            mongo, user_id, subcategory_id, group_by, group_value)\

        await callback_query.answer(message_text)
        await callback_query.message.edit_reply_markup(reply_markup=reply_markup)

    @dp.callback_query(lambda c: c.data.startswith('delete_favorite_'))
    async def delete_from_favorite(callback_query: types.CallbackQuery):
        _, group_info = callback_query.data.split(
            'delete_favorite_', 1)
        data = group_info.split('_')
        subcategory_id = data[0]
        group_by = data[1]
        group_value = data[2]
        await callback_query.answer()
        was_delete, title = await delete_favorite(mongo, callback_query.from_user.id, subcategory_id, group_by, group_value)
        if was_delete:
            message_text = f"{title} has been deleted from your favorites."

        reply_markup = await action_buttons(
            mongo, callback_query.from_user.id, subcategory_id, group_by, group_value)
        await callback_query.message.edit_reply_markup(reply_markup=reply_markup)

    @dp.callback_query(lambda c: c.data.startswith('random_'))
    async def handle_random_choice(callback_query: types.CallbackQuery):
        action, subcategory_id, group_by = callback_query.data.split('_')
        group_values = await get_group_values(mongo, subcategory_id, group_by)
        group_value = random.choice(group_values).get('_id')
        keyboard = await action_buttons(mongo, callback_query.from_user.id, subcategory_id, group_by, group_value)
        await callback_query.answer()
        await callback_query.message.answer("Randomly choose", reply_markup=keyboard)

    @dp.callback_query(F.data == "favorite_items")
    async def get_favorites(callback: types.CallbackQuery):
        favorites_buttons = await get_favorites_button(mongo, callback.from_user.id)
        await callback.message.answer("List of favorites", reply_markup=favorites_buttons)
        await callback.answer()

    @dp.callback_query(F.data == "order_history")
    async def get_order_history(callback: types.CallbackQuery):
        await callback.answer()
        message = await purchase_buttons(mongo, callback.from_user.id)
        await callback.message.answer(f"Order history:", reply_markup=message)

    @dp.callback_query(F.data.startswith("purchase_"))
    async def get_order_history(callback: types.CallbackQuery):
        _, order_id = callback.data.split('purchase_', 1)
        order_info = await get_product_info(mongo, order_id)
        await callback.answer()
        await callback.message.answer(f"Item:\n{order_info}")

    @dp.callback_query(F.data.startswith("multiple_"))
    async def multiple_purchase(callback: types.CallbackQuery, state: FSMContext):
        user_id = callback.from_user.id
        _, group_info = callback.data.split('multiple_', 1)
        data = group_info.split('_')
        subcategory_id = data[0]
        group_by = data[1]
        group_value = data[2]
        await state.update_data(subcategory_id=subcategory_id, group_by=group_by, group_value=group_value)
        await callback.answer()
        await callback.message.answer("Input count of items to buy:")
        await state.set_state(CountOfProductsState.waiting_for_count, )

    @dp.callback_query(F.data.startswith("admincategory_"))
    async def get_add_product_category(callback: types.CallbackQuery):
        category_id = callback.data.split('_')[1]
        category = await get_category_info(mongo, category_id)
        category_name = category.get("name")
        keyboards = await get_admin_subcategories_buttons(mongo, category_id)
        await callback.answer()
        await callback.message.answer(f"Subcategories of {category_name}:", reply_markup=keyboards)

    @dp.callback_query(F.data.startswith("adminsubcategory_"))
    async def get_add_product_subcategory(callback: types.CallbackQuery, state: FSMContext):
        subcategory_id = callback.data.split('_')[1]
        await callback.answer()
        message_text = await get_fileds(mongo, subcategory_id)
        await callback.message.answer(f"Enter as follows: {':'.join(message_text)}")
        await state.update_data(subcategory_id=subcategory_id)
        await state.set_state(ProductState.waiting_for_product, )

    @dp.callback_query(F.data.startswith("choose_"))
    async def choose_category(callback: types.CallbackQuery, state: FSMContext):
        category_id = callback.data.split('_')[1]
        await state.update_data(category_id=category_id)
        await callback.message.answer("Input subcategory name for adding: ")
        await callback.answer()
        await state.set_state(SubcategoryForm.waiting_for_subcategory_name)
