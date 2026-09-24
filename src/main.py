from fastapi import FastAPI
from .routes import base, data
from pymongo import AsyncMongoClient
from contextlib import asynccontextmanager
from .stores.llm import LLMProviderFactory
from .helpers.configurations import get_settings

@asynccontextmanager
async def lifespan(app: FastAPI):

    print(" Application is starting up...")

    settings = get_settings()

    app.state.mongo_client_conn = AsyncMongoClient(settings.MONGO_URL)
    app.state.db_client = app.state.mongo_client_conn[settings.MONGODB_DATABASE]

    app.state.llm_provider_factory = LLMProviderFactory(
        configuration=settings
    )

    # generation client
    app.state.generation_client = app.state.llm_provider_factory.get_llm_provider(provider_name=settings.GENERATION_BACKEND)
    app.state.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    # embedding client
    app.state.embedding_client = app.state.llm_provider_factory.get_llm_provider(provider_name=settings.EMBEDDING_BACKEND)
    app.state.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                            embedding_size=settings.EMBEDDING_MODEL_SIZE)

    yield

    print(" Application is shutting down...")
    await app.state.mongo_client_conn.close()
    print(" Closed all connections cleanly.")

app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)