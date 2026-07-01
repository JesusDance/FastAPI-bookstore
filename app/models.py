from typing import List

from sqlalchemy import ForeignKey, String, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase): ...


class User(Base):
    __tablename__ = "user"

    __table_args__ = (
        CheckConstraint(
            "length(username) >= 3 AND length(username) <= 50",
            name="username_length"
        ),
        CheckConstraint(
            "length(password) >= 5 AND length(password) <= 250",
            name="password_length"
        ),
        CheckConstraint(
            "full_name IS NULL OR length(full_name) <= 50",
            name="full_name_length"
        ),
        CheckConstraint(
            "second_name IS NULL OR length(second_name) <= 50",
            name="second_name_length",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    second_name: Mapped[str | None] = mapped_column(String(50), nullable=True)

    books: Mapped[List["Book"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"User(id={self.id}, username={self.username}, books={self.books})"
        )


class Book(Base):
    __tablename__ = "book"

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

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50))
    author: Mapped[str] = mapped_column(String(50))
    price: Mapped[float]
    description: Mapped[str | None] = mapped_column(String(50), nullable=True)
    in_stock: Mapped[bool]

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="books")

    def __repr__(self) -> str:
        return f"Book(id={self.id}, title={self.title}, user_id={self.user_id})"
