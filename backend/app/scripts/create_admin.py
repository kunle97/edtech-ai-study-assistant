import argparse
import getpass
import sys

from sqlalchemy import select

from app.auth.models import User, UserRole
from app.auth.security import hash_password
from app.auth.service import normalize_email
from app.db.session import SessionLocal


def create_admin(email: str, password: str) -> None:
    normalized_email = normalize_email(email)

    with SessionLocal() as db:
        existing_user = db.scalar(
            select(User).where(User.email == normalized_email)
        )

        if existing_user is not None:
            if existing_user.role == UserRole.ADMIN:
                print(f"Admin already exists: {normalized_email}")
                return

            print(
                "A student account already exists with that email. "
                "Use a different email.",
                file=sys.stderr,
            )
            raise SystemExit(1)

        admin = User(
            email=normalized_email,
            password_hash=hash_password(password),
            role=UserRole.ADMIN,
        )

        db.add(admin)
        db.commit()

        print(f"Admin created successfully: {normalized_email}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create the initial LearnPath administrator."
    )
    parser.add_argument(
        "--email",
        required=True,
        help="Administrator email address",
    )
    args = parser.parse_args()

    password = getpass.getpass("Admin password: ")
    confirmation = getpass.getpass("Confirm password: ")

    if password != confirmation:
        print("Passwords do not match.", file=sys.stderr)
        raise SystemExit(1)

    if len(password) < 8:
        print(
            "Password must contain at least 8 characters.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    create_admin(args.email, password)


if __name__ == "__main__":
    main()