from fastapi import FastAPI
from routes import base, data, nlp
from pymongo import AsyncMongoClient
from contextlib import asynccontextmanager
from stores.llm import LLMProviderFactory
from helpers.configurations import get_settings
from stores.vectordb import VectorDBProvider
from stores.llm.templates import TemplateParser

@asynccontextmanager
async def lifespan(app: FastAPI):

    print(" Application is starting up...")

    settings = get_settings()

    # Initialize MongoDB connection
    app.state.mongo_client_conn = AsyncMongoClient(settings.MONGO_URL)
    app.state.db_client = app.state.mongo_client_conn[settings.MONGODB_DATABASE]

    # Initialize LLM and VectorDB provider factories
    app.state.llm_provider_factory = LLMProviderFactory(
        configuration=settings
    )

    app.state.vectordb_provider_factory = VectorDBProvider(
            configuration=settings
        )

    # Initialize Template Parser
    app.state.template_parser = TemplateParser(
        language=settings.ENGLISH_LANGUAGE,
        default_language=settings.DEFAULT_LANGUAGE
    )


    # generation client
    app.state.generation_client = app.state.llm_provider_factory.get_llm_provider(provider_name=settings.GENERATION_BACKEND)
    app.state.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    # embedding client
    app.state.embedding_client = app.state.llm_provider_factory.get_llm_provider(provider_name=settings.EMBEDDING_BACKEND)
    app.state.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                            embedding_size=settings.EMBEDDING_MODEL_SIZE)

    # vectorDB client
    app.state.vectorDB_client = app.state.vectordb_provider_factory.get_vectorDB_provider(provider_name=settings.VECTORDB_BACKEND)
    app.state.vectorDB_client.connect()

    yield

    print(" Application is shutting down...")
    await app.state.mongo_client_conn.close()
    app.state.vectorDB_client.disconnect()
    print(" Closed all connections cleanly.")

app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
