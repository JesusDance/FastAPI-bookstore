from pydantic import EmailStr, BaseModel, ConfigDict, Field


class Token(BaseModel):
    access_token: str
    token_type: str


class CreateBook(BaseModel):
    title: str = Field(min_length=3, max_length=50)
    author: str | None = Field(default=None, max_length=50)
    price: float = Field(gt=0, lt=50)
    description: str | None = Field(default=None, min_length=0, max_length=50)
    in_stock: bool | None = Field(default=True)


class ReadBook(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    author: str
    price: float
    description: str | None = None
    in_stock: bool


class UpdateBook(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=50)
    author: str | None = Field(default=None, max_length=50)
    price: float | None = Field(default=None, gt=0, lt=50)
    description: str | None = Field(default=None, min_length=0, max_length=50)
    in_stock: bool | None = None


class UserIn(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=5, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=50)
    full_name: str | None = Field(default=None, min_length=3, max_length=50)
    second_name: str | None = Field(default=None, min_length=3, max_length=50)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    full_name: str | None = None
    second_name: str | None = None
    books: list[ReadBook] | None = None
