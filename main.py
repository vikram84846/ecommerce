from fastapi import FastAPI
from contextlib import asynccontextmanager
from routes import auth
from utils.twilio import twilio_verify_client
from core.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await twilio_verify_client.close()


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
