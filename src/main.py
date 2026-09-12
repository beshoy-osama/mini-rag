from fastapi import FastAPI
from routes import base, data
from pymongo import AsyncMongoClient
from contextlib import asynccontextmanager

from helpers.configurations import get_settings

@asynccontextmanager
async def lifespan(app: FastAPI):

    print(" Application is starting up...")

    app.state.mongo_client_conn = AsyncMongoClient(get_settings().MONGO_URL)
    app.state.db_client = app.state.mongo_client_conn[get_settings().MONGODB_DATABASE]

    yield

    print(" Application is shutting down...")
    await app.state.mongo_client_conn.close()
    print(" Closed all connections cleanly.")

app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)