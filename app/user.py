from typing import Annotated, Any
from fastapi import Body, APIRouter, HTTPException
from sqlmodel import select

from app.schemas import UserIn, UserOut, Token
from app.models import User
from app.db import SessionDep
from app.security import get_password_hash, verify_password, \
                         create_access_token


router = APIRouter(prefix="/register", tags=["register"])

USER = Annotated[UserIn, Body()]


@router.post("/", response_model=UserOut, status_code=201)
def register_user(session: SessionDep, user: USER) -> Any:
    existing_user = session.exec(select(User).where(User.username == user.username)).first()
    if existing_user:
        raise HTTPException(400, "User already exist")
    if not user:
        raise HTTPException(status_code=422)

    # user_db = User(username=user.username,
    #                password=get_password_hash(user.password),
    #                email=user.email,
    #                full_name=user.full_name,
    #                second_name=user.second_name)

    current_user = user.model_dump()
    user_plain_password = current_user.pop("password")
    hash_password = get_password_hash(user_plain_password)
    user_db = User(**current_user, password=hash_password)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)

    return user_db


@router.post("/login", response_model=Token)
def login_user(session: SessionDep, user: USER) -> Any:
    existing_user = session.exec(select(User).where(User.username == user.username)).first()

    if not existing_user or not verify_password(user.password, existing_user.password):
        raise HTTPException(401, "Incorrect username or password")

    token = create_access_token(existing_user.id)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/{user_id}", response_model=UserOut)
def get_user(session: SessionDep, user_id: int) -> Any:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(404,"User not found")
    return user


@router.get("/", response_model=list[UserOut])
def get_users(session: SessionDep) -> Any:
    users = session.exec(select(User)).all()
    return users


