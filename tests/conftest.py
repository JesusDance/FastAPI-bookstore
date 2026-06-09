import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport
from pytest_httpx import HTTPXMock
from sqlmodel import create_engine, Session, SQLModel

from app.db import get_session
from app.main import app
from app.models import User, Book
from app.security import get_password_hash

test_engine = create_engine(
    "sqlite:///test.db", connect_args={"check_same_thread": False}
)


def override_get_session():
    with Session(test_engine) as session:
        yield session


@pytest.fixture(scope="module")
def create_test_db():
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)

    with Session(test_engine) as session:
        default_user = User(
            username="Bob",
            password=get_password_hash("12345"),
            email="bob@gmail.com",
            full_name="Bob Dilan",
            second_name="Dilan",
        )
        second_user = User(
            username="Steven",
            password=get_password_hash("12345"),
            email="steven@gmail.com",
            full_name="Steven King",
            second_name="King",
        )

        session.add_all([default_user, second_user])
        session.commit()

        book1 = Book(
            title="Horror",
            author="some_author",
            price=45,
            description="some_horror_book",
            in_stock=True,
            user_id=default_user.id,
        )
        book2 = Book(
            title="Mystic",
            author="some_author2",
            price=35,
            description="some_mystic_book",
            in_stock=False,
            user_id=second_user.id,
        )
        book3 = Book(
            title="Story",
            author="some_author3",
            price=25,
            description="some_story_book",
            in_stock=True,
            user_id=default_user.id,
        )

        session.add_all([book1, book2, book3])
        session.commit()

    yield
    SQLModel.metadata.drop_all(test_engine)


@pytest_asyncio.fixture
async def mock_api_client(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        http_version="HTTP/2.0",
        is_optional=True,
        is_reusable=True,
        json={
            "docs": [
                {
                    "title": "test_book",
                    "author_name": ["test_author"],
                },
            ],
        },
    )


@pytest_asyncio.fixture
async def test_client_api(create_test_db, mock_api_client):
    app.dependency_overrides[get_session] = override_get_session
    async with LifespanManager(app) as manager:
        async with AsyncClient(
                transport=ASGITransport(app=manager.app),
                base_url="http://test",
                http2=True,
                follow_redirects=True) as as_client:
            await as_client.get(
                "https://openlibrary.org/search.json?title=test+book")
            yield as_client
    app.dependency_overrides = {}


@pytest_asyncio.fixture(scope="module")
async def test_client(create_test_db):
    app.dependency_overrides[get_session] = override_get_session
    async with LifespanManager(app) as manager:
        async with AsyncClient(
                transport=ASGITransport(app=manager.app),
                base_url="http://test",
                http2=True,
                follow_redirects=True) as as_client:
            yield as_client
    app.dependency_overrides = {}


@pytest_asyncio.fixture(scope="module")
async def default_user_token(test_client):
    response = await test_client.post(
        "/register/login/",
        json={
            "username": "Bob",
            "password": "12345",
            "email": "bob@gmail.com",
            "full_name": "Bob Dilan",
            "second_name": "Dilan",
        },
    )
    json_response = response.json()
    yield json_response["access_token"]


@pytest_asyncio.fixture(scope="module", autouse=True)
async def second_user_token(test_client):
    response = await test_client.post(
        "/register/login/",
        json={
            "username": "Steven",
            "password": "12345",
            "email": "steven@gmail.com",
            "full_name": "Steven King",
            "second_name": "King",
        },
    )
    json_response = response.json()
    yield json_response["access_token"]
