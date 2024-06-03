from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
import random
"""Importing my own modules"""
from db.mongo_db import get_categories_list
from db.mongo_db import get_subcategories_list
from db.mongo_db import get_group_values
from db.mongo_db import is_favorite_product
from db.mongo_db import get_favorites_list
from db.mongo_db import check_have_products
from db.mongo_db import get_groupped_count
from db.mongo_db import get_subcategory_info
from db.mongo_db import check_have_subcategories
from db.mongo_db import get_single_group_count
from db.mongo_db import get_subcategory_count
from db.mongo_db import history_purchase
from bson.objectid import ObjectId  # Заметьте изменение способа импорта
from datetime import datetime


async def profile_keyboard():
    builder = InlineKeyboardBuilder()
    kb = [
        types.InlineKeyboardButton(
            text="📜 Purchase history", callback_data="order_history"),
        types.InlineKeyboardButton(
            text="💳 Top up the balance", callback_data="add_balance"),
        types.InlineKeyboardButton(
            text="📈 History of Replenishment", callback_data="balance_history"),
        types.InlineKeyboardButton(
            text="🌟 Featured Products", callback_data="favorite_items"),
    ]

    for i in range(0, len(kb), 2):
        builder.row(*kb[i:i+2])

    return builder.as_markup()


async def cancel_payment_input_button():
    builder = InlineKeyboardBuilder()
    kb = [
        types.InlineKeyboardButton(
            text="❌ Cancel",
            callback_data="undo_input_amount"),
    ]

    builder.row(*kb)

    return builder.as_markup()


async def payment_button(uuid, link):
    builder = InlineKeyboardBuilder()
    kb = [
        types.InlineKeyboardButton(
            text="💳 Pay",
            url=f"{link}",
            callback_data=f"pay"),
        types.InlineKeyboardButton(
            text="❌ Cancel",
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


async def get_categories_buttons(mongo):
    categories = await get_categories_list(mongo)
    builder = InlineKeyboardBuilder()
    kb = []
    for category in categories:
        count = await check_have_subcategories(mongo, category['_id'])
        if count > 0:
            builder.row(types.InlineKeyboardButton(
                text=f"📂 {category['name']}",
                callback_data=f"category_{category['_id']}"))

    return builder.as_markup()


async def get_subcategories_buttons(mongo, category_id):
    subcategories = await get_subcategories_list(mongo, category_id)
    builder = InlineKeyboardBuilder()
    for subcategory in subcategories:
        count = await get_subcategory_count(mongo, subcategory['_id'])
        if count > 0:
            builder.row(types.InlineKeyboardButton(
                text=f"📌 {subcategory['name']} | {
                    count} items | 💲{subcategory['price']}$",
                callback_data=f"subcategory_{subcategory['_id']}"))

    return builder.as_markup()


async def get_groups_buttons(mongo, subcategory_id, group_by):
    group_values = await get_group_values(mongo, subcategory_id, group_by)
    builder = InlineKeyboardBuilder()
    kb = []

    subcategrory = await get_subcategory_info(mongo, subcategory_id)

    if len(group_values) > 1:
        builder.row(
            types.InlineKeyboardButton(
                text="Random choose 🎲",
                callback_data=f"random_{subcategory_id}_{group_by}"),
        )
    for group in group_values:
        products = await get_groupped_count(mongo, subcategory_id, group_by, group['_id'])
        if products != 0:
            kb.append(types.InlineKeyboardButton(
                text=f"📦 {group['_id']} | 💲{subcategrory.get('price')}$ | 📊 {
                    products} items",
                callback_data=f"group_{subcategory_id}_{group_by}_{group['_id']}"))

    for i in range(0, len(kb), 2):
        builder.row(*kb[i:i+2])

    return builder.as_markup()


async def single_group_buttons(mongo, subcategory_id, subcategory_name):
    builder = InlineKeyboardBuilder()
    count = await get_single_group_count(mongo, subcategory_id)
    if count > 0:
        subcategory = await get_subcategory_info(mongo, subcategory_id)
        builder.row(types.InlineKeyboardButton(
            text=f"📦 {subcategory_name} | 📊 {
                count} items | 💲{subcategory.get('price')}$",
            callback_data=f"item_{subcategory_id}_{subcategory_name}"))

    return builder.as_markup()


async def action_buttons(mongo, user_id, subcategory_id, group_by=None, group_value=None):
    builder = InlineKeyboardBuilder()

    is_favorite = await is_favorite_product(mongo, user_id, subcategory_id, group_by, group_value)
    builder.add(types.InlineKeyboardButton(
        text="💲Buy", callback_data=f"buy_{subcategory_id}_{group_by}_{group_value}"))
    if is_favorite:
        builder.add(types.InlineKeyboardButton(
            text="🗑 Delete from favorites", callback_data=f"delete_favorite_{subcategory_id}_{group_by}_{group_value}"))
    if not is_favorite:
        builder.add(types.InlineKeyboardButton(text="⭐️ Add to favorites",
                    callback_data=f"add_to_favorites_{subcategory_id}_{group_by}_{group_value}"))

    builder.row(
        types.InlineKeyboardButton(
            text="💸Multiple purchase",
            callback_data=f"multiple_{subcategory_id}_{group_by}_{group_value}"),
    )

    builder.row(
        types.InlineKeyboardButton(
            text="⬅ Back to categories",
            callback_data="back_to_categories_button"),
    )
    return builder.as_markup()


async def get_favorites_button(mongo, user_id):
    favorites = await get_favorites_list(mongo, user_id)
    builder = InlineKeyboardBuilder()

    for favorite in favorites:
        if str(favorite['group_by']) == "none":
            builder.row(types.InlineKeyboardButton(
                text=f"❤️ {favorite['product']}",
                callback_data=f"item_{favorite['subcategory_id']}_{favorite['product']}"))

        else:
            builder.row(types.InlineKeyboardButton(
                text=f"{favorite['product']}",
                callback_data=f"group_{favorite['subcategory_id']}_{favorite['group_by']}_{favorite['product']}"))

    return builder.as_markup()


async def purchase_buttons(mongo, user_id):
    results = await history_purchase(mongo, user_id)
    builder = InlineKeyboardBuilder()

    for result in results:
        builder.row(types.InlineKeyboardButton(
            text=f"🛍️ {result['product']} | 💲{result['price']}$",
            callback_data=f"purchase_{result['product_id']}"))

    return builder.as_markup()


async def get_admin_categories_buttons(mongo):
    categories = await get_categories_list(mongo)
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.row(types.InlineKeyboardButton(
            text=f"{category['name']}",
            callback_data=f"admincategory_{category['_id']}"))

    return builder.as_markup()


async def get_admin_subcategories_buttons(mongo, category_id):
    subcategories = await get_subcategories_list(mongo, category_id)
    builder = InlineKeyboardBuilder()
    for subcategory in subcategories:
        count = await get_subcategory_count(mongo, subcategory['_id'])

        builder.row(types.InlineKeyboardButton(
            text=f"{subcategory['name']}",
            callback_data=f"adminsubcategory_{subcategory['_id']}"))

    return builder.as_markup()


async def choose_category(mongo):
    categories = await get_categories_list(mongo)
    builder = InlineKeyboardBuilder()
    kb = []
    for category in categories:
        builder.row(types.InlineKeyboardButton(
            text=f"{category['name']}",
            callback_data=f"choose_{category['_id']}"))

    return builder.as_markup()
