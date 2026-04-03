from pydantic import EmailStr
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship


class BaseUser(SQLModel):
    username: str = Field(index=True, min_length=3, max_length=50)
    password: str = Field(min_length=5, max_length=50)
    email: EmailStr
    full_name: str | None = Field(default=None, max_length=50)
    second_name: str | None = Field(default=None, max_length=50)


class User(BaseUser, table=True):
    id: int | None = Field(default=None, primary_key=True)

    books: List["Book"] = Relationship(back_populates="user")


class BaseBook(SQLModel):
    title: str = Field(min_length=3, max_length=50)
    author: str = Field(min_length=5, max_length=50)
    price: float = Field(gt=0, lt=50)
    description: str | None = Field(default=None, min_length=0, max_length=50)
    in_stock: bool


class Book(BaseBook, table=True):
    id: int | None = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="books")






