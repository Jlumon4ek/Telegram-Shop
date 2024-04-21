from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
import random
"""Importing my own modules"""


async def profile_keyboard():
    builder = InlineKeyboardBuilder()
    kb = [
        types.InlineKeyboardButton(
            text="Purchase history", callback_data="order_history"),
        types.InlineKeyboardButton(
            text="Top up the balance", callback_data="add_balance"),
        types.InlineKeyboardButton(
            text="History of Replenishment", callback_data="balance_history"),
        types.InlineKeyboardButton(
            text="Featured Products", callback_data="favorite_items"),
    ]

    for i in range(0, len(kb), 2):
        builder.row(*kb[i:i+2])

    return builder.as_markup()
