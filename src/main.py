from fastapi import FastAPI
from routes.base import base_router
from routes.data import data_router
from helpers.config import get_settings, Settings
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from stores.llm.LLMProviderFactory import LLMProviderFactory

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

    llm_provider_factory = LLMProviderFactory(settings)

    # Generation Client
    app.generation_client = llm_provider_factory.create(
        provider=settings.GENERATION_BACKEND
    )
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)
    
    # Embedding Client
    app.embedding_client = llm_provider_factory.create(
        provider=settings.EMBEDDING_BACKEND
    )
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID, embedding_size=settings.EMBEDDING_MODEL_SIZE)
    
    yield
    app.mongo_conn.close()

app = FastAPI(lifespan=lifespan)

app.include_router(base_router)
app.include_router(data_router)