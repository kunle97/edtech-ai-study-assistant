import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth.models import User
from app.chat.models import ChatMessage, ChatSession, MessageRole, MessageStatus


class ChatSessionNotFoundError(Exception):
    pass


def create_session(db: Session, *, user: User, title: str | None) -> ChatSession:
    session = ChatSession(user_id=user.id, title=title)
    db.add(session)
    db.flush()
    return session


def list_user_sessions(db: Session, *, user_id: uuid.UUID) -> list[ChatSession]:
    return list(
        db.scalars(
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.created_at.desc())
        ).all()
    )


def get_session_with_messages(
    db: Session,
    *,
    session_id: uuid.UUID,
    user_id: uuid.UUID,
) -> ChatSession:
    session = db.scalar(
        select(ChatSession)
        .options(selectinload(ChatSession.messages))
        .where(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id,
        )
    )

    if session is None:
        raise ChatSessionNotFoundError

    return session


def queue_user_message(
    db: Session,
    *,
    session_id: uuid.UUID,
    user_id: uuid.UUID,
    content: str,
) -> ChatMessage:
    session = db.scalar(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id,
        )
    )

    if session is None:
        raise ChatSessionNotFoundError

    message = ChatMessage(
        session_id=session.id,
        role=MessageRole.USER,
        status=MessageStatus.QUEUED,
        content=content.strip(),
    )

    db.add(message)
    db.flush()
    return message
