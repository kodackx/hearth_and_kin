import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


def setup_mongodb() -> AsyncIOMotorDatabase:
    client = AsyncIOMotorClient(os.environ['MONGODB_URL'])
    db = client['test']
    return db
