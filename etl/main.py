import motor.motor_asyncio
import asyncio
from typing import List
from dotenv import load_dotenv
import os
from extract.extract_data import validated_data

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

async def insert_data(validated_data: List[dict]):
    if validated_data:
        result = await collection.insert_many(validated_data)
        print(f"Inserted {len(result.inserted_ids)} documents.")
    else:
        print("No valid documents to insert.")

loop = asyncio.get_event_loop()
loop.run_until_complete(insert_data(validated_data))
