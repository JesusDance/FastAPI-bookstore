from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlmodel import SQLModel

from app.db import engine
from app.books import router as book_router
from app.user import router as user_router


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(book_router)
app.include_router(user_router)


@app.get("/")
def get_root():
    return {"message": "Hello from FastAPI!"}