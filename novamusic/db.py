import os
from typing import List, Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

_client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None


async def init_db() -> None:
    global _client, db
    mongo_uri = os.getenv("MONGO_DB_URI", "")
    if not mongo_uri:
        return
    _client = AsyncIOMotorClient(mongo_uri)
    if "+srv" in mongo_uri:
        try:
            db = _client.get_default_database()
        except Exception:
            db_name = os.getenv("MONGO_DB_NAME", "novamusic")
            db = _client[db_name]
    else:
        db = _client[os.getenv("MONGO_DB_NAME", "novamusic")]


# SUDOERS
async def get_sudoers() -> List[int]:
    if not db:
        ids = os.getenv("SUDO_IDS", "").split()
        return [int(x) for x in ids if x.isdigit()]
    row = await db.sudoers.find_one({"_id": "sudo"})
    return row.get("ids", []) if row else []


async def add_sudo(user_id: int) -> None:
    if not db:
        return
    sudoers = await get_sudoers()
    if user_id in sudoers:
        return
    sudoers.append(user_id)
    await db.sudoers.update_one({"_id": "sudo"}, {"$set": {"ids": sudoers}}, upsert=True)


async def remove_sudo(user_id: int) -> None:
    if not db:
        return
    sudoers = await get_sudoers()
    if user_id not in sudoers:
        return
    sudoers.remove(user_id)
    await db.sudoers.update_one({"_id": "sudo"}, {"$set": {"ids": sudoers}}, upsert=True)


# SERVED CHATS for broadcast
async def add_served_chat(chat_id: int) -> None:
    if not db:
        return
    await db.served_chats.update_one({"_id": chat_id}, {"$set": {"_id": chat_id}}, upsert=True)


async def get_served_chats() -> List[int]:
    if not db:
        return []
    cursor = db.served_chats.find({}, {"_id": 1})
    return [doc["_id"] async for doc in cursor]

