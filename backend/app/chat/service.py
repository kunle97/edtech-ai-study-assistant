import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth.models import User
from app.chat.models import ChatMessage, ChatSession, MessageRole, MessageStatus
from app.events.service import CHAT_MESSAGE_QUEUED, add_outbox_event


class ChatSessionNotFoundError(Exception):
    pass


def create_session(
    db: Session,
    *,
    user: User,
    title: str | None,
) -> ChatSession:
    session = ChatSession(
        user_id=user.id,
        title=title,
    )

    db.add(session)
    db.flush()

    return session


def list_user_sessions(
    db: Session,
    *,
    user_id: uuid.UUID,
) -> list[ChatSession]:
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

    add_outbox_event(
        db,
        event_type=CHAT_MESSAGE_QUEUED,
        aggregate_type="chat_message",
        aggregate_id=message.id,
        payload={
            "message_id": str(message.id),
            "session_id": str(session.id),
            "user_id": str(user_id),
        },
    )

    return message
