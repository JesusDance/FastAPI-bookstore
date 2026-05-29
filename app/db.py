import os
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine

from dotenv import load_dotenv

# sqlite_url = "sqlite:///db.sqlite"
# engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
