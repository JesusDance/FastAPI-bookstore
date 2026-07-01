from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.config import settings

engine = create_engine(settings.DATABASE_URL)
session_local = sessionmaker(bind=engine)


def get_session():
    with session_local() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
