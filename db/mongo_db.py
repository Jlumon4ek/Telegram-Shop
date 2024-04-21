import asyncio
from pymongo.errors import ConnectionFailure
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime


def create_mongo_connection():
    try:
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        db = client["gv_market"]
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
