from aiogram import types
"""Importing my own modules"""
from db.mongo_db import get_user_role


async def main_buttons(mongo, user_id):
    buttons = [
        [
            types.KeyboardButton(text="All products"),
            types.KeyboardButton(text="Product availability"),
            types.KeyboardButton(text="Profile"),
        ],
        [
            types.KeyboardButton(text="Rules"),
            types.KeyboardButton(text="Help"),
            types.KeyboardButton(text="About us"),
        ],
    ]
    keyboard_markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=buttons,
    )

    user_role = await get_user_role(mongo, user_id)

    if user_role == 'admin':
        buttons.append([types.KeyboardButton(text="Admin Panel")])

    keyboard_markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=buttons,
    )
    return keyboard_markup


async def admin_panel_buttons(mongo, user_id):
    buttons = [
        [
            types.KeyboardButton(text="Admins management"),
            types.KeyboardButton(text="Users management"),
            types.KeyboardButton(text="Mailing"),
        ],
        [
            types.KeyboardButton(text="Product management"),
            types.KeyboardButton(text="Category management"),
            types.KeyboardButton(text="Subcategory managment"),
        ],
        [
            types.KeyboardButton(text="Back to main menu"),
        ],
    ]

    keyboard_markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=buttons,
    )

    return keyboard_markup
