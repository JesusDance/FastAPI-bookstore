from typing import Annotated, Any

from fastapi import APIRouter, Body, HTTPException, Depends
from fastapi.params import Query
from fastapi.security import OAuth2PasswordBearer
from httpx import AsyncClient
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.client import BookClient
from app.client import get_httpx_client
from app.db import SessionDep
from app.models import Book
from app.schemas import CreateBook, ReadBook, UpdateBook
from app.security import decode_token

router = APIRouter(prefix="/bookstore", tags=["bookstore"])
oauth2_schema = OAuth2PasswordBearer(tokenUrl="/register/login")

BOOKSTORE_API_URL = "https://openlibrary.org/search.json?title="

BOOK = Annotated[CreateBook, Body()]
UPDATE_BOOK = Annotated[UpdateBook, Body()]
TOKEN_DEP = Annotated[str, Depends(oauth2_schema)]
CLIENT = Annotated[AsyncClient, Depends(get_httpx_client)]


async def check_book_limit(session: SessionDep, user_id: int):
    books = session.exec(select(Book).where(Book.user_id == user_id)).all()
    if len(books) >= 20:
        raise HTTPException(400, "Max books in case")


@router.post("/", response_model=ReadBook, status_code=201)
async def create_book(
    session: SessionDep, client: CLIENT, book: BOOK, token: TOKEN_DEP
) -> Any:
    user_id = decode_token(token)
    await check_book_limit(session, user_id)

    client = BookClient(BOOKSTORE_API_URL, client)
    title, author = await client.fetch_book_from_api(book.title)

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
    session.refresh(book_db)
    return book_db


@router.get("/", response_model=list[ReadBook])
async def get_books(
    session: SessionDep,
    token: TOKEN_DEP,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(le=10)] = 10,
) -> Any:
    user_id = decode_token(token)
    books = session.exec(
        select(Book).where(Book.user_id == user_id).offset(offset).limit(limit)
    ).all()
    return books


@router.get("/{book_id}", response_model=ReadBook)
async def get_book(session: SessionDep, book_id: int, token: TOKEN_DEP) -> Any:
    user_id = decode_token(token)
    book_db = session.get(Book, book_id)

    if not (book_db and book_db.user_id == user_id):
        raise HTTPException(404, "Book not found")
    return book_db


@router.patch("/{book_id}", response_model=ReadBook)
async def update_book(
    session: SessionDep, book_id: int, book: UPDATE_BOOK, token: TOKEN_DEP
) -> Any:

    book_db = session.get(Book, book_id)
    user_id = decode_token(token)

    if not (book_db and book_db.user_id == user_id):
        raise HTTPException(404, "Book not found")

    updated_book = book.model_dump(exclude_unset=True)
    book_db.sqlmodel_update(updated_book)

    session.add(book_db)
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(422, detail=f"{e.orig}")
    session.refresh(book_db)
    return book_db


@router.delete("/{book_id}")
async def delete_book(session: SessionDep, book_id: int, token: TOKEN_DEP) -> Any:
    user_id = decode_token(token)
    book_db = session.get(Book, book_id)

    if not (book_db and book_db.user_id == user_id):
        raise HTTPException(404, "Book not found")

    session.delete(book_db)
    session.commit()
    return {"message": "Book deleted successfully"}
