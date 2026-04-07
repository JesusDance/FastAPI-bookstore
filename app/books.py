from typing import Annotated, Any

from fastapi import APIRouter, Path, Body, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.db import SessionDep
from app.models import Book
from app.schemas import CreateBook, ReadBook, UpdateBook
from app.security import decode_token

router = APIRouter(prefix="/bookstore", tags=["bookstore"])
oauth2_schema = OAuth2PasswordBearer(tokenUrl="/register/login")

BOOK = Annotated[CreateBook, Body()]
BOOK_ID: Annotated[int, Path(ge=0, le=100)]
UPDATE_BOOK = Annotated[UpdateBook, Body()]
TOKEN_DEP = Annotated[str, Depends(oauth2_schema)]


@router.post("/", response_model=ReadBook, status_code=201)
def create_book(session: SessionDep, book: BOOK, token: TOKEN_DEP) -> Any:
    user_id = decode_token(token)
    book_db = Book(**book.model_dump(), user_id=user_id)

    session.add(book_db)
    session.commit()
    session.refresh(book_db)
    return book_db


@router.get("/", response_model=list[ReadBook])
def get_books(session: SessionDep, token: TOKEN_DEP) -> Any:
    user_id = decode_token(token)
    books = session.exec(select(Book).where(Book.user_id == user_id)).all()
    return books


@router.get("/{book_id}", response_model=ReadBook)
def get_book(session: SessionDep, book_id: int, token: TOKEN_DEP) -> Any:
    user_id = decode_token(token)
    book_db = session.get(Book, book_id)

    if not book_db:
        raise HTTPException(404, "Book not found")

    if not book_db.user_id == user_id:
        raise HTTPException(404, "You don't have access for this book")
    return book_db


@router.patch("/{book_id}", response_model=ReadBook)
def update_book(
    session: SessionDep, book_id: int, book: UPDATE_BOOK, token: TOKEN_DEP
) -> Any:

    book_db = session.get(Book, book_id)
    user_id = decode_token(token)

    if not book_db:
        raise HTTPException(404, "Book not found")

    if not book_db.user_id == user_id:
        raise HTTPException(404, "You don't have access for this book")

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
def delete_book(session: SessionDep, book_id: int, token: TOKEN_DEP) -> Any:
    user_id = decode_token(token)
    book_db = session.get(Book, book_id)

    if not book_db:
        raise HTTPException(404, "Book not found")

    if not book_db.user_id == user_id:
        raise HTTPException(404, "You don't have access for this book")

    session.delete(book_db)
    session.commit()
    return {"message": "Book deleted successfully"}
