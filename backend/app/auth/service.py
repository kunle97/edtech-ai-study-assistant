from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.models import User, UserRole
from app.auth.schemas import UserRegister
from app.auth.security import hash_password, verify_password


class EmailAlreadyRegisteredError(Exception):
    pass


def normalize_email(email: str) -> str:
    return email.strip().lower()


def get_user_by_email(db: Session, email: str) -> User | None:
    statement = select(User).where(
        User.email == normalize_email(email)
    )
    return db.scalar(statement)


def create_student(db: Session, payload: UserRegister) -> User:
    user = User(
        email=normalize_email(payload.email),
        password_hash=hash_password(payload.password),
        role=UserRole.STUDENT,
    )

    db.add(user)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise EmailAlreadyRegisteredError from exc

    db.refresh(user)
    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User | None:
    user = get_user_by_email(db, email)

    if user is None:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user