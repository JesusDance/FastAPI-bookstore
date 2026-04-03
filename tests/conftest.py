import pytest

from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session, SQLModel
from app.config import TestingConfig
from app.models import User, Book
from app.security import get_password_hash
from app.main import app
from app.db import get_session

settings = TestingConfig()

test_engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False})


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
            second_name="Dilan")
        second_user = User(
            username="Steven",
            password=get_password_hash("12345"),
            email="steven@gmail.com",
            full_name="Steven King",
            second_name="King")

        session.add_all([default_user, second_user])
        session.commit()

        book1 = Book(title="Horror", author="some_author", price=45,
                     description="some_horror_book", in_stock=True,
                     user_id=default_user.id)
        book2 = Book(title="Mystic", author="some_author2", price=35,
                     description="some_mystic_book", in_stock=False,
                     user_id=second_user.id)
        book3 = Book(title="Story", author="some_author3", price=25,
                     description="some_story_book", in_stock=True,
                     user_id=default_user.id)

        session.add_all([book1, book2, book3])
        session.commit()

    yield
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture(scope="module")
def test_client(create_test_db):
    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides = {}


@pytest.fixture(scope="module")
def default_user(test_client):
    response = test_client.post(
        "/register/login/",
        json={
            "username": "Bob",
            "password": "12345",
            "email": "bob@gmail.com",
            "full_name": "Bob Dilan",
            "second_name": "Dilan"
        }
    )
    json_response = response.json()
    yield json_response


@pytest.fixture(scope="module")
def default_user_token(test_client):
    response = test_client.post(
        "/register/login/",
        json={
            "username": "Bob",
            "password": "12345",
            "email": "bob@gmail.com",
            "full_name": "Bob Dilan",
            "second_name": "Dilan"
        }
    )
    json_response = response.json()
    yield json_response["access_token"]


@pytest.fixture(scope="module")
def second_user_token(test_client):
    response = test_client.post(
        "/register/login/",
        json={
            "username": "Steven",
            "password": "12345",
            "email": "steven@gmail.com",
            "full_name": "Steven King",
            "second_name": "King"
        }
    )
    json_response = response.json()
    yield json_response["access_token"]