import os

import dotenv
import motor.motor_asyncio

dotenv.load_dotenv()

def setup_mongodb():
    client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
    db = client["test"]
    return db
