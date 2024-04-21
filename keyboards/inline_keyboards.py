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


async def cancel_payment_input_button():
    builder = InlineKeyboardBuilder()
    kb = [
        types.InlineKeyboardButton(
            text="Cancel",
            callback_data="undo_input_amount"),
    ]

    builder.row(*kb)

    return builder.as_markup()


async def payment_button(uuid, link):
    builder = InlineKeyboardBuilder()
    kb = [
        types.InlineKeyboardButton(
            text="Pay",
            url=f"{link}",
            callback_data="pay"),
        types.InlineKeyboardButton(
            text="Done",
            callback_data=f"done_{uuid}"),
        types.InlineKeyboardButton(
            text="Cancel",
            callback_data=f"cancel_{uuid}"),
    ]

    for i in range(0, len(kb), 2):
        builder.row(*kb[i:i+2])

    return builder.as_markup()


async def users_managment_button():
    builder = InlineKeyboardBuilder()
    kb = [
        types.InlineKeyboardButton(
            text="Ban user",
            callback_data="ban_user_button"),
        types.InlineKeyboardButton(
            text="Unban user",
            callback_data=f"unban_user_button"),
    ]

    for i in range(0, len(kb), 2):
        builder.row(*kb[i:i+2])

    return builder.as_markup()
