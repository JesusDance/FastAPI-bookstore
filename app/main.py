from contextlib import asynccontextmanager
from typing import Annotated

import httpx
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from httpx import AsyncClient
from sqlmodel import SQLModel

from app.basic_auth import get_current_username
from app.books import router as book_router
from app.db import engine
from app.user import router as user_router

ORIGINS = ['http://localhost', 'http://localhost:8080', 'https://localhost']

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    limits = httpx.Limits(
        max_connections=50,
        max_keepalive_connections=10,
        keepalive_expiry=5)
    app.state.httpx_client = AsyncClient(http2=True, limits=limits)
    yield
    await app.state.httpx_client.aclose()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_methods=['GET', 'POST', 'PATCH', 'DELETE'],
    allow_headers=['*'],
    allow_credentials=True,
)
app.include_router(book_router)
app.include_router(user_router)


@app.get("/")
async def get_root(username: Annotated[str, Depends(get_current_username)]):
    return {"message": f"Hello {username}"}
