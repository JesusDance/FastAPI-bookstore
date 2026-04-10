from typing import List, Optional

from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship, CheckConstraint


class BaseUser(SQLModel):
    __table_args__ = (
        CheckConstraint(
            "length(username) >= 3 AND length(username) <= 50", name="username_length"
        ),
        CheckConstraint(
            "length(password) >= 5 AND length(password) <= 250", name="password_length"
        ),
        CheckConstraint(
            "full_name IS NULL OR length(full_name) <= 50", name="full_name_length"
        ),
        CheckConstraint(
            "second_name IS NULL OR length(second_name) <= 50",
            name="second_name_length",
        ),
    )
    username: str = Field(index=True, min_length=3, max_length=50)
    password: str = Field(min_length=5, max_length=250)
    email: EmailStr
    full_name: str | None = Field(default=None, max_length=50)
    second_name: str | None = Field(default=None, max_length=50)


class User(BaseUser, table=True):
    id: int | None = Field(default=None, primary_key=True)

    books: List["Book"] = Relationship(back_populates="user")


class BaseBook(SQLModel):
    __table_args__ = (
        CheckConstraint(
            "length(title) >= 3 AND length(title) <= 50", name="title_length"
        ),
        CheckConstraint(
            "length(author) >= 5 AND length(author) <= 50", name="author_length"
        ),
        CheckConstraint("price > 0 AND price < 50", name="price_gt_lt"),
        CheckConstraint(
            "description IS NULL OR length(description) <= 50",
            name="description_length",
        ),
    )
    title: str = Field(min_length=3, max_length=50)
    author: str = Field(min_length=5, max_length=50)
    price: float = Field(gt=0, lt=50)
    description: str | None = Field(default=None, min_length=0, max_length=50)
    in_stock: bool


class Book(BaseBook, table=True):
    id: int | None = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="books")
