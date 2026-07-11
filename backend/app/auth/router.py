from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.dependencies import ActiveUser
from app.auth.schemas import (
    LoginResponse,
    UserRegister,
    UserResponse,
)
from app.auth.security import create_access_token
from app.auth.service import (
    EmailAlreadyRegisteredError,
    authenticate_user,
    create_student,
)
from app.db.session import get_db


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: UserRegister,
    db: DatabaseSession,
) -> UserResponse:
    try:
        return create_student(db, payload)
    except EmailAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )


@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends(),
    ],
    db: DatabaseSession,
) -> LoginResponse:
    user = authenticate_user(
        db,
        email=form_data.username,
        password=form_data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.is_suspended:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is suspended",
        )

    token = create_access_token(user.id)

    return LoginResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(current_user: ActiveUser) -> UserResponse:
    return UserResponse.model_validate(current_user)