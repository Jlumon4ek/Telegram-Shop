import asyncio
from pymongo.errors import ConnectionFailure
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from bson.objectid import ObjectId
import random
from utils.config import db_username, db_password, db_auth_source


def create_mongo_connection():
    try:
        client = AsyncIOMotorClient(
            f"mongodb://{db_username}:{db_password}@31.220.17.247:27017/?authSource={db_auth_source}")
        db = client["gv_store"]
        print("Connection to MongoDB successful")
        return db
    except ConnectionFailure as e:
        print(f"The error '{e}' occurred")
        return None


async def add_user(mongo, user_id=None, fullname=None, username=None, banned=False):
    users_collection = mongo["users"]
    existing_user = await users_collection.find_one({"_id": user_id})

    if existing_user is None:
        user_data = {
            "_id": user_id,
            "banned": banned,
            "register_date": datetime.utcnow(),
            "username": f"@{username}",
            "fullname": fullname,
            "balance": 0,
            "role": "default"
        }
        try:
            result = await users_collection.insert_one(user_data)
            if result.inserted_id:
                print("[INFO] User added successfully")
                return "Welcome to our store! How can I help?"
            else:
                print("[INFO] Failed to add user.")
        except Exception as e:
            print(f"[INFO] An error occurred: {e}")
    else:
        updates = {}
        if username and existing_user.get("username") != f"@{username}":
            updates["username"] = f"@{username}"
        if fullname and existing_user.get("fullname") != fullname:
            updates["fullname"] = fullname

        if updates:
            await users_collection.update_one({"_id": user_id}, {"$set": updates})
            print(f"[INFO] User with ID {user_id} updated successfully.")
            return "Hello! How can I help?"
        else:
            print(f"[INFO] No updates required for user with ID {user_id}.")

    return "Hello! How can I help?"


async def get_user_role(mongo, user_id):
    users_collection = mongo["users"]
    user = await users_collection.find_one({"_id": user_id})
    if user:
        return user.get("role", "default")
    return "default"


async def get_user_balance(mongo, user_id):
    users_collection = mongo["users"]
    user = await users_collection.find_one({"_id": user_id})
    if user:
        return user.get("balance", 0)
    return 0


async def update_user_balance(mongo, user_id, received_usd):
    await mongo.users.update_one(
        {"_id": user_id},
        {"$inc": {"balance": received_usd}}
    )


async def record_balance_history(mongo, user_id, received_usd, username, fullname, uuid):
    document = {
        "user_id": user_id,
        "amount": received_usd,
        "date": datetime.utcnow(),
        "username": username,
        "fullname": fullname,
        "payment_link": f"https://pay.cryptocloud.plus/{uuid}"
    }

    await mongo.balance_history.insert_one(document)
    print("[INFO] Balance history recorded successfully")


async def get_balance_history(mongo, user_id):
    balance_history_collection = mongo['balance_history']
    cursor = balance_history_collection.find(
        {"user_id": user_id}, {"_id": 0, "date": 1, "amount": 1})
    results = await cursor.to_list(length=None)
    output = "History of replenishment:\n\n"
    for result in results:
        date = result.get('date').strftime(
            '%Y-%m-%d %H:%M:%S')

        amount = result.get('amount')
        output += f"{date} : {amount}$\n"
    return output


async def get_admin_list(mongo):
    users_collection = mongo["users"]
    cursor = users_collection.find({"role": "admin"})
    results = await cursor.to_list(length=None)
    output = "List of admins:\n\n"
    for result in results:
        output += f"{result.get('fullname')} - {result.get('username')}\n"
    return output


async def get_users_list(mongo):
    users_collection = mongo["users"]
    cursor = users_collection.find()
    results = await cursor.to_list(length=None)
    output = "List of users:\n\n"
    for result in results:
        output += f"{result.get('_id')} - {result.get('fullname')} - {result.get('username')} - {result.get('banned')}\n"
    return output


async def change_users_status(mongo, user_id, status: bool):
    try:
        user_id = int(user_id)

        user = await mongo.users.find_one({"_id": user_id})

        if user.get("banned", False) == status:
            if status:
                return "The user is already banned."
            else:
                return "The user is already unbanned."

        result = await mongo.users.update_one(
            {"_id": user_id},
            {"$set": {"banned": status}}
        )

        if result.matched_count == 0:
            return f"No user found with ID {user_id}."

        else:
            if status:
                return f"User {user_id} has been banned."
            else:
                return f"User {user_id} has been unbanned."

    except Exception as e:
        return f"An error occurred while updating the status of user {user_id}."


async def get_categories_list(mongo):
    cursor = mongo.categories.find({}, {'name': 1})
    return [category async for category in cursor]


async def get_category_info(mongo, category_id):
    oid = ObjectId(category_id)
    return await mongo.categories.find_one({"_id": oid})


async def get_subcategories_list(mongo, category_id):
    oid = ObjectId(category_id)

    cursor = mongo.subcategories.find(
        {'category_id': oid}, {'name': 1, 'price': 1})
    return [subcategory async for subcategory in cursor]


async def get_subcategory_info(mongo, subcategory_id):
    oid = ObjectId(subcategory_id)
    return await mongo.subcategories.find_one({"_id": oid})


async def get_group_values(mongo, subcategory_id, group_by):
    oid = ObjectId(subcategory_id)
    cursor = mongo.products.aggregate([
        {"$match": {"subcategory_id": oid}},
        {"$group": {"_id": f"${group_by}"}}
    ])

    return [group async for group in cursor]


async def is_favorite_product(mongo, user_id, subcategory_id, group_by, group_value):
    group_by = str(group_by)
    if group_by == 'None':
        subcategory = await get_subcategory_info(mongo, subcategory_id)
        subcategory_name = subcategory.get("name")

        result = await mongo.favorites.find_one({
            "user_id": user_id,
            "product": subcategory_name,
            "subcategory_id": subcategory_id,
        })
    else:
        result = await mongo.favorites.find_one({
            "user_id": user_id,
            "product": group_value,
            "subcategory_id": subcategory_id
        })

    return bool(result)


async def add_to_favorites(mongo, user_id, subcategory_id, group_by, group_value):
    if group_by == 'None':
        subcategory = await get_subcategory_info(mongo, subcategory_id)
        subcategory_name = subcategory.get("name")
        document = {
            "user_id": user_id,
            "product": subcategory_name,
            "subcategory_id": subcategory_id,
            "group_by": group_value,
            "group_value": group_value,
            "timestamp": datetime.utcnow(),
        }
        title = subcategory_name
    else:
        document = {
            "user_id": user_id,
            "product": group_value,
            "subcategory_id": subcategory_id,
            "group_by": group_by,
            "group_value": group_value,
            "timestamp": datetime.utcnow(),
        }
        title = group_value

    await mongo.favorites.insert_one(document)
    return True, title


async def delete_favorite(mongo, user_id, subcategory_id, group_by, group_value):
    if group_by == 'None':
        subcategory = await get_subcategory_info(mongo, subcategory_id)
        subcategory_name = subcategory.get("name")
        document = {
            "user_id": user_id,
            "product": subcategory_name,
            "subcategory_id": subcategory_id,
            "group_by": group_value,
            "group_value": group_value,
        }
        title = subcategory_name
    else:
        document = {
            "user_id": user_id,
            "product": group_value,
            "subcategory_id": subcategory_id,
            "group_by": group_by,
            "group_value": group_value,
        }
        title = group_value

    await mongo.favorites.delete_one(document)
    return True, title


async def get_favorites_list(mongo, user_id):
    cursor = mongo.favorites.find({"user_id": user_id})
    results = await cursor.to_list(length=None)
    return results


async def buy_product_logic(mongo, user_id, subcategory_id, group_by, group_value):
    subcategory = await get_subcategory_info(mongo, subcategory_id)
    subcategory_price = subcategory.get("price")
    user_balance = await get_user_balance(mongo, user_id)

    if float(user_balance) < float(subcategory_price):
        return "Insufficient funds."
    else:
        if group_by == 'None':
            cursor = mongo.products.find({
                "subcategory_id": ObjectId(subcategory_id),
                "status": 'available',
            })
            results = await cursor.to_list(length=None)

            if not results:
                return "No products found for this group value."

            product = random.choice(results)

            await update_user_balance(mongo, user_id, -subcategory_price)

            mongo.purchase_history.insert_one({
                "user_id": user_id,
                "product": subcategory.get("name"),
                "product_id": product.get("_id"),
                "subcategory_id": subcategory_id,
                "group_by": group_by,
                "group_value": group_value,
                "timestamp": datetime.utcnow(),
                'price': subcategory_price,

            })

            mongo.products.update_one(
                {"_id": product.get("_id")},
                {"$set": {"status": "sold"}}
            )
            hidden_fields = {"_id", "status",
                             "subcategory_id", "subcategory_name"}
            filtered_product = {k: v for k,
                                v in product.items() if k not in hidden_fields}

            product_str = "\n".join(
                [f"{key} : {value}" for key, value in filtered_product.items()])

            return f"Product purchased successfully\n{product_str} "

        else:
            cursor = mongo.products.find({
                f"{group_by}": f"{group_value}",
                "status": 'available',
            })
            results = await cursor.to_list(length=None)

            if not results:
                return "No products found for this group value."

            product = random.choice(results)

            await update_user_balance(mongo, user_id, -subcategory_price)

            mongo.purchase_history.insert_one({
                "user_id": user_id,
                "product": group_value,
                "product_id": product.get("_id"),
                "subcategory_id": subcategory_id,
                "group_by": group_by,
                "group_value": group_value,
                "timestamp": datetime.utcnow(),
                'price': subcategory_price,
            })

            mongo.products.update_one(
                {"_id": product.get("_id")},
                {"$set": {"status": "sold"}}
            )
            hidden_fields = {"_id", "status",
                             "subcategory_id", "subcategory_name"}
            filtered_product = {k: v for k,
                                v in product.items() if k not in hidden_fields}

            product_str = "\n".join(
                [f"{key} : {value}" for key, value in filtered_product.items()])

            return f"Product purchased successfully\n{product_str} "


async def history_purchase(mongo, user_id):
    cursor = mongo.purchase_history.find({"user_id": user_id})
    results = await cursor.to_list(length=None)

    return results


async def get_product_info(mongo, product_id):
    oid = ObjectId(product_id)
    product = await mongo.products.find_one({"_id": oid})
    hidden_fields = {"_id", "status",
                     "subcategory_id", "subcategory_name"}
    filtered_product = {k: v for k,
                        v in product.items() if k not in hidden_fields}

    product_str = "\n".join(
        [f"{key} : {value}" for key, value in filtered_product.items()])
    return product_str


async def get_groupped_count(mongo, subcategory_id, group_by, group_value):
    oid = ObjectId(subcategory_id)
    count = await mongo.products.count_documents({
        "subcategory_id": oid,
        f"{group_by}": f"{group_value}",
        "status": "available"
    })

    return count


async def get_single_group_count(mongo, subcategory_id):
    oid = ObjectId(subcategory_id)
    cursor = await mongo.products.count_documents({
        "subcategory_id": oid,
        "status": "available"
    })

    return cursor


async def get_subcategory_count(mongo, subcategory_id):
    oid = ObjectId(subcategory_id)
    count = await mongo.products.count_documents({
        "subcategory_id": oid,
        "status": "available"
    })

    return count


async def add_category(mongo, category_name):
    category = {
        "name": category_name,
    }
    await mongo.categories.insert_one(category)
    return "Category added"


async def structure_data(mongo):
    structured_data = {}

    cursor = mongo.categories.find({})
    categories = [category async for category in cursor]

    for category in categories:
        category_name = category['name']
        structured_data[category_name] = {}

        cursor = mongo.subcategories.find({'category_id': category['_id']})
        subcategories = [subcategory async for subcategory in cursor]

        for subcategory in subcategories:
            subcategory_name = subcategory['name']
            cursor = mongo.products.find({
                'subcategory_id': subcategory['_id'],
                'status': 'available'
            })
            products = [product async for product in cursor]

            product_count = len(products)

            if (product_count > 0):
                price = subcategory['price'] if 'price' in subcategory else 'N/A'
                if subcategory['group_by'] is not None:
                    group_by = subcategory['group_by']
                    groups = {}
                    for product in products:
                        group_name = product[group_by]
                        if group_name in groups:
                            groups[group_name] += 1
                        else:
                            groups[group_name] = 1
                    structured_data[category_name][subcategory_name] = {
                        'product_count': product_count, 'price': price, 'groups': groups}
                else:
                    structured_data[category_name][subcategory_name] = {
                        'product_count': product_count, 'price': price}

            else:
                continue
    formatted_data = []

    for category, subcategories in structured_data.items():
        formatted_data.append(category + ':')
        for subcategory, details in subcategories.items():
            formatted_data.append(
                f'{subcategory} | {details["product_count"]} items | {details["price"]}$:')
            if 'groups' in details:
                for group, count in details['groups'].items():
                    formatted_data.append(f'- {group} | {count}')
        formatted_data.append('')

    return '\n'.join(formatted_data)


async def multiple_buy_update(mongo, user_id, subcategory_id, group_by, group_value, count):
    subcategory = await get_subcategory_info(mongo, subcategory_id)
    subcategory_price = subcategory.get("price")
    user_balance = await get_user_balance(mongo, user_id)
    total = float(subcategory_price) * float(count)
    if float(user_balance) < total:
        return "Insufficient funds."

    else:
        product_str = ''
        if group_by == 'None':
            count_of_products = await get_single_group_count(mongo, subcategory_id)
            if int(count) > int(count_of_products):
                return "Not enough products in stock."

            cursor = mongo.products.find({
                "subcategory_id": ObjectId(subcategory_id),
                "status": 'available',
            }).limit(int(count))
            results = await cursor.to_list(length=None)

            if not results:
                return "No products found for this group value."

            await update_user_balance(mongo, user_id, -float(subcategory_price)*float(count))

            for result in results:
                mongo.products.update_one(
                    {"_id": result.get("_id")},
                    {"$set": {"status": "sold"}}
                )

                mongo.purchase_history.insert_one({
                    "user_id": user_id,
                    "product": subcategory.get("name"),
                    "product_id": result.get("_id"),
                    "subcategory_id": subcategory_id,
                    "group_by": group_by,
                    "group_value": group_value,
                    "timestamp": datetime.utcnow(),
                    'price': subcategory_price,
                })

                hidden_fields = {"_id", "status",
                                 "subcategory_id", "subcategory_name"}

                filtered_product = {k: v for k,
                                    v in result.items() if k not in hidden_fields}

                product_str += "\n\n" + "\n".join(
                    [f"{key} : {value}" for key, value in filtered_product.items()])

        else:
            count_of_products = await get_groupped_count(
                mongo, subcategory_id, group_by, group_value)
            if int(count) > int(count_of_products):
                return "Not enough products in stock."

            cursor = mongo.products.find({
                f"{group_by}": f"{group_value}",
                "status": 'available',
            }).limit(int(count))
            results = await cursor.to_list(length=None)

            if not results:
                return "No products found for this group value."

            await update_user_balance(mongo, user_id, -float(subcategory_price)*float(count))

            for result in results:
                mongo.products.update_one(
                    {"_id": result.get("_id")},
                    {"$set": {"status": "sold"}}
                )

                mongo.purchase_history.insert_one({
                    "user_id": user_id,
                    "product": group_value,
                    "product_id": result.get("_id"),
                    "subcategory_id": subcategory_id,
                    "group_by": group_by,
                    "group_value": group_value,
                    "timestamp": datetime.utcnow(),
                    'price': subcategory_price,
                })

                hidden_fields = {"_id", "status",
                                 "subcategory_id", "subcategory_name"}

                filtered_product = {k: v for k,
                                    v in result.items() if k not in hidden_fields}

                product_str += "\n\n" + "\n".join(
                    [f"{key} : {value}" for key, value in filtered_product.items()])

        return f"Product purchased successfully\n{product_str}"


async def get_fileds(mongo, subcategory_id):
    oid = ObjectId(subcategory_id)
    cursor = await mongo.subcategories.find_one({"_id": oid})
    return cursor['field']


async def add_product_db(mongo, subcategory_id, products):
    fields = await get_fileds(mongo, subcategory_id)
    subcategory_info = await get_subcategory_info(mongo, subcategory_id)
    added_products = []
    existing_products = []
    for product in products.split('\n'):
        product_data = product.split(':')
        fields = [field.strip() for field in fields]
        product_data = [data.strip() if isinstance(
            data, str) else data for data in product_data]
        product_dict = dict(zip(fields, product_data))

        existing_product = await mongo.products.find_one(product_dict)
        if existing_product:
            existing_products.append(product)
        else:
            product_dict['price'] = subcategory_info['price']
            product_dict['subcategory_name'] = subcategory_info['name']
            product_dict['status'] = 'available'
            product_dict['subcategory_id'] = ObjectId(subcategory_id)
            await mongo.products.insert_one(product_dict)
            added_products.append(product)

    added_products_str = "\n".join(added_products)
    existing_products_str = "\n".join(existing_products)
    return f"Products added successfully:\n{added_products_str}\nProducts that are already in the database:\n{existing_products_str}"


async def add_subcategory_db(mongo, category_id, subcategory_name, price, group_by, fields):
    group_by = None if group_by.lower() == 'none' else group_by

    subcategory = {
        "name": subcategory_name,
        "price": price,
        "category_id": ObjectId(category_id),
        "group_by": group_by,
        "field": [field.strip() for field in fields.split(',')]

    }
    await mongo.subcategories.insert_one(subcategory)
    return "Subcategory added"
