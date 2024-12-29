import os
from beanie import init_beanie
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from fastapi import FastAPI
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from fast_app.api.models.event import EventModel


load_dotenv()

DATABASE_URL = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

print(f"DATABASE_URL={DATABASE_URL}")
print(f"DATABASE_NAME={DATABASE_NAME}")

class MongoDB:
    client: AsyncIOMotorClient = None

mongodb = MongoDB()

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:

        if not DATABASE_URL:
            raise ValueError("MONGO_URI is not set in environment variables.")

        print(f"Connecting to MongoDB at {DATABASE_URL}...")
        mongodb.client = AsyncIOMotorClient(DATABASE_URL)
        print(f"Connected to MongoDB at {DATABASE_URL}")


        db = mongodb.client[DATABASE_NAME]
        await db.command('ping')  
        print(f"Database '{DATABASE_NAME}' is ready.")
        await init_beanie(db, document_models=[EventModel])
        
        yield
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise e
    finally:
        if mongodb.client:
            mongodb.client.close()
            print("MongoDB connection closed")



async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    if mongodb.client is None:
        print(f"DATABASE_URL: {DATABASE_URL}, DATABASE_NAME: {DATABASE_NAME}")
        print("MongoDB client is not initialized!")
        raise ValueError("Database client is not initialized.")
    
    print("Providing database connection.")
    yield mongodb.client[DATABASE_NAME]
