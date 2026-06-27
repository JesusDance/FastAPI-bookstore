from typing import Annotated, Any

from fastapi import APIRouter, Body, HTTPException, Depends
from fastapi.params import Query
from fastapi.security import OAuth2PasswordBearer
from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.client import BookClient
from app.client import get_httpx_client
from app.config import settings
from app.db import SessionDep
from app.models import Book
from app.schemas import CreateBook, ReadBook, UpdateBook
from app.security import decode_token
from cache.cache_redis import RedisCacheClient, get_redis_client

router = APIRouter(prefix="/bookstore", tags=["bookstore"])
oauth2_schema = OAuth2PasswordBearer(tokenUrl="/register/login")

BOOKSTORE_API_URL = "https://openlibrary.org/search.json?title="

BOOK = Annotated[CreateBook, Body()]
UPDATE_BOOK = Annotated[UpdateBook, Body()]
TOKEN_DEP = Annotated[str, Depends(oauth2_schema)]
CLIENT = Annotated[AsyncClient, Depends(get_httpx_client)]
REDIS_CLIENT = Annotated[Redis, Depends(get_redis_client)]


async def check_book_limit(session: SessionDep, user_id: int):
    books = session.exec(select(Book).where(Book.user_id == user_id)).all()
    if len(books) >= 20:
        raise HTTPException(400, "Max books in case")


@router.post("/", response_model=ReadBook, status_code=201)
async def create_book(
    session: SessionDep,
    client: CLIENT,
    cache: REDIS_CLIENT,
    book: BOOK,
    token: TOKEN_DEP,
) -> Any:
    user_id = decode_token(token)
    await check_book_limit(session, user_id)

    client = BookClient(BOOKSTORE_API_URL, client)
    title, author = await client.fetch_book_from_api(book.title)

    cache_pattern = f"books:{user_id}:*"
    redis_client = RedisCacheClient(cache, settings.CACHE_TTL_SECONDS)

    existing_book = session.exec(
        select(Book).where(Book.title == title, Book.user_id == user_id)
    ).first()

    if existing_book:
        raise HTTPException(409, "Book already exists")

    book_db = Book(
        **book.model_dump(exclude={"title", "author"}),
        title=title,
        author=author,
        user_id=user_id,
    )
    session.add(book_db)
    session.commit()

    await redis_client.delete_by_pattern(cache_pattern)
    session.refresh(book_db)
    return book_db


@router.get("/", response_model=list[ReadBook])
async def get_books(
    session: SessionDep,
    token: TOKEN_DEP,
    redis_client: REDIS_CLIENT,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(le=10)] = 10,
) -> Any:
    user_id = decode_token(token)

    cache = RedisCacheClient(redis_client, settings.CACHE_TTL_SECONDS)
    cache_key = f"books:{user_id}:{offset}:{limit}"
    cached_books = await cache.get(cache_key)

    # 1. Перевірка якщо є дані в редіс
    if cached_books is not None:
        return cached_books

    # 2. Йдемо в бд якщо в кеше немає даних
    books = session.exec(
        select(Book).where(Book.user_id == user_id).offset(offset).limit(limit)
    ).all()

    # 3. Зберегти в кеш якщо даних в кеше немає
    books_read = [ReadBook.model_validate(book) for book in books]
    books_for_cache = [book.model_dump() for book in books_read]
    await cache.set_cache(cache_key, books_for_cache)

    return books


@router.get("/{book_id}", response_model=ReadBook)
async def get_book(
    session: SessionDep, book_id: int, token: TOKEN_DEP, redis_client: REDIS_CLIENT
) -> Any:
    user_id = decode_token(token)

    cache = RedisCacheClient(redis_client, settings.CACHE_TTL_SECONDS)
    cache_key = f"book:{user_id}:{book_id}"
    checked_book = await cache.get(cache_key)

    if checked_book is not None:
        return checked_book

    book_db = session.get(Book, book_id)
    if not (book_db and book_db.user_id == user_id):
        raise HTTPException(404, "Book not found")

    book_for_cache = book_db.model_dump()
    await cache.set_cache(cache_key, book_for_cache)

    return book_db


@router.patch("/{book_id}", response_model=ReadBook)
async def update_book(
    session: SessionDep,
    book_id: int,
    book: UPDATE_BOOK,
    token: TOKEN_DEP,
    redis_client: REDIS_CLIENT,
) -> Any:
    user_id = decode_token(token)

    cache = RedisCacheClient(redis_client, settings.CACHE_TTL_SECONDS)
    cache_key = f"book:{user_id}:{book_id}"
    cache_pattern = f"books:{user_id}:*"

    book_db = session.get(Book, book_id)

    if not (book_db and book_db.user_id == user_id):
        raise HTTPException(404, "Book not found")

    updated_book = book.model_dump(exclude_unset=True)
    book_db.sqlmodel_update(updated_book)

    session.add(book_db)
    try:
        session.commit()
        await cache.delete(cache_key)
        await cache.delete_by_pattern(cache_pattern)
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(422, detail=f"{e.orig}")
    session.refresh(book_db)
    return book_db


@router.delete("/{book_id}")
async def delete_book(
    session: SessionDep, book_id: int, token: TOKEN_DEP, redis_client: REDIS_CLIENT
) -> Any:
    user_id = decode_token(token)

    cache = RedisCacheClient(redis_client, settings.CACHE_TTL_SECONDS)
    cache_key = f"book:{user_id}:{book_id}"
    cache_pattern = f"books:{user_id}:*"
    book_db = session.get(Book, book_id)

    if not (book_db and book_db.user_id == user_id):
        raise HTTPException(404, "Book not found")

    session.delete(book_db)
    session.commit()
    await cache.delete(cache_key)
    await cache.delete_by_pattern(cache_pattern)

    return {"message": "Book deleted successfully"}
