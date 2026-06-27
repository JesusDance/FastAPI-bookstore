from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine

from app.config import settings

# sqlite_url = "sqlite:///db.sqlite"
# engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

engine = create_engine(settings.DATABASE_URL)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
