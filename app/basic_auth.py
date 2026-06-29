import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasicCredentials, HTTPBasic

from app.config import settings

security = HTTPBasic()
BASIC_AUTH = Annotated[HTTPBasicCredentials, Depends(security)]


def get_current_username(credentials: BASIC_AUTH):
    current_username_b = credentials.username.encode("utf-8")
    correct_username_b = settings.ADMIN_NAME.encode("utf-8")
    is_correct_username = secrets.compare_digest(current_username_b, correct_username_b)

    current_password_b = credentials.password.encode("utf-8")
    correct_password_b = settings.ADMIN_PASS.encode("utf-8")
    is_correct_password = secrets.compare_digest(current_password_b, correct_password_b)

    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
