from aiogram import F
from aiogram import types
from aiogram.fsm.context import FSMContext
import asyncio
from aiogram.enums import ParseMode
import random

""""Importing my own modules"""
from keyboards.inline_keyboards import cancel_payment_input_button
from utils.states import TopUpState
from utils.payments import invoice_cancel, check_payment_status
from db.mongo_db import get_balance_history


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
            message_text = f"Payment with unique identifier: {uuid} was cancelled."

        else:
            message_text = "An error occurred while trying to cancel the payment."

        await callback.message.edit_text(f"{message_text}")
        await callback.answer()

    @dp.callback_query(F.data.startswith("done_"))
    async def check_invoice(callback: types.CallbackQuery):
        uuid = callback.data.split('_')[1]
        await callback.message.edit_text("Your payment is processed and the money will be credited to your account within a few minutes")
        await callback.answer()
        user_id = callback.from_user.id
        username = callback.from_user.username
        fullname = callback.from_user.full_name
        asyncio.create_task(check_payment_status(
            mongo, uuid, user_id, username, fullname, bot))

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
