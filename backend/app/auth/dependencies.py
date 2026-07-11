import uuid
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from app.auth.models import User, UserRole
from app.core.config import settings
from app.db.session import get_db


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
)

DatabaseSession = Annotated[Session, Depends(get_db)]
AccessToken = Annotated[str, Depends(oauth2_scheme)]


def credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    token: AccessToken,
    db: DatabaseSession,
) -> User:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

        if payload.get("type") != "access":
            raise credentials_exception()

        subject = payload.get("sub")

        if subject is None:
            raise credentials_exception()

        user_id = uuid.UUID(subject)

    except (InvalidTokenError, ValueError):
        raise credentials_exception()

    user = db.get(User, user_id)

    if user is None:
        raise credentials_exception()

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_user(
    current_user: CurrentUser,
) -> User:
    if current_user.is_suspended:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is suspended",
        )

    return current_user


ActiveUser = Annotated[
    User,
    Depends(get_current_active_user),
]


def require_admin(
    current_user: ActiveUser,
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required",
        )

    return current_user


AdminUser = Annotated[
    User,
    Depends(require_admin),
]
