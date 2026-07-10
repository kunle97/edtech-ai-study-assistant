# Import every SQLAlchemy model here so Alembic can discover it.
from app.auth.models import User

__all__ = ["User"]
