from fastapi import FastAPI
from routes.base import base_router
from routes.data import data_router
from helpers.config import get_settings, Settings
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]
    yield
    app.mongo_conn.close()

app = FastAPI(lifespan=lifespan)

app.include_router(base_router)
app.include_router(data_router)