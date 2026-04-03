from sqlmodel import SQLModel
from pydantic import EmailStr,BaseModel
from app.models import BaseUser, User, BaseBook


class Token(BaseModel):
    access_token: str
    token_type: str


class CreateBook(BaseBook):
    pass


class ReadBook(SQLModel):
    id: int
    title: str
    author: str
    price: float
    description: str
    in_stock: bool


class UpdateBook(BaseBook):
    title: str | None = None
    author: str | None = None
    price: float | None = None
    description: str | None = None
    in_stock: bool | None = None


class UserIn(BaseUser):
    email: EmailStr | None = None


class UserOut(SQLModel):
    id: int
    username: str
    email: EmailStr
    full_name: str | None = None
    second_name: str | None = None

    #books: list[ReadBook] | None = None

