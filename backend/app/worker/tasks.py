import uuid

from celery import Task
from celery.exceptions import MaxRetriesExceededError
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.ai.provider import TemporaryAIError, get_ai_provider
from app.auth.models import User
from app.chat.models import (
    ChatMessage,
    ChatSession,
    MessageRole,
    MessageStatus,
)
from app.db.session import SessionLocal
from app.worker.celery_app import celery_app


TERMINAL_STATUSES = {
    MessageStatus.COMPLETED,
    MessageStatus.BLOCKED,
    MessageStatus.FAILED,
}


@celery_app.task(
    bind=True,
    name="chat.process_message",
    max_retries=5,
)
def process_chat_message(
    self: Task,
    message_id: str,
) -> dict[str, str]:
    parsed_message_id = uuid.UUID(message_id)

    with SessionLocal() as db:
        # Lock the message row so duplicate task deliveries cannot process it
        # concurrently.
        message = db.scalar(
            select(ChatMessage)
            .where(ChatMessage.id == parsed_message_id)
            .with_for_update()
        )

        if message is None:
            return {"status": "not_found"}

        if message.status in TERMINAL_STATUSES:
            return {"status": message.status.value}

        session = db.scalar(
            select(ChatSession).where(
                ChatSession.id == message.session_id
            )
        )

        if session is None:
            message.status = MessageStatus.FAILED
            message.error_message = "Chat session no longer exists"
            db.commit()
            return {"status": "failed"}

        user = db.get(User, session.user_id)

        # Execution-time authorization check.
        if user is None or user.is_suspended:
            message.status = MessageStatus.BLOCKED
            message.error_message = "User account is suspended"
            db.commit()
            return {"status": "blocked"}

        message.status = MessageStatus.PROCESSING
        message.error_message = None
        db.commit()

    try:
        with SessionLocal() as db:
            current_message = db.get(ChatMessage, parsed_message_id)

            if current_message is None:
                return {"status": "not_found"}

            conversation = db.scalars(
                select(ChatMessage)
                .where(
                    ChatMessage.session_id == current_message.session_id,
                    ChatMessage.created_at <= current_message.created_at,
                )
                .order_by(ChatMessage.created_at.asc())
            ).all()

            history = [
                {
                    "role": item.role.value,
                    "content": item.content,
                }
                for item in conversation
            ]

            provider = get_ai_provider()
            response_text = provider.generate_response(
                message=current_message.content,
                conversation_history=history,
            )

        with SessionLocal() as db:
            # Lock the user message again before writing the response.
            message = db.scalar(
                select(ChatMessage)
                .where(ChatMessage.id == parsed_message_id)
                .with_for_update()
            )

            if message is None:
                return {"status": "not_found"}

            if message.status in TERMINAL_STATUSES:
                return {"status": message.status.value}

            session = db.get(ChatSession, message.session_id)
            user = db.get(User, session.user_id) if session else None

            # Second suspension check immediately before delivery.
            if user is None or user.is_suspended:
                message.status = MessageStatus.BLOCKED
                message.error_message = "User account is suspended"
                db.commit()
                return {"status": "blocked"}

            assistant_message = ChatMessage(
                session_id=message.session_id,
                role=MessageRole.ASSISTANT,
                status=MessageStatus.COMPLETED,
                content=response_text,
            )

            db.add(assistant_message)
            message.status = MessageStatus.COMPLETED
            message.error_message = None
            db.commit()

            return {
                "status": "completed",
                "assistant_message_id": str(assistant_message.id),
            }

    except TemporaryAIError as exc:
        with SessionLocal() as db:
            message = db.get(ChatMessage, parsed_message_id)

            if message is not None:
                message.status = MessageStatus.RETRYING
                message.error_message = str(exc)
                db.commit()

        try:
            raise self.retry(
                exc=exc,
                countdown=min(2 ** self.request.retries, 60),
            )
        except MaxRetriesExceededError:
            with SessionLocal() as db:
                message = db.get(ChatMessage, parsed_message_id)

                if message is not None:
                    message.status = MessageStatus.FAILED
                    message.error_message = (
                        "AI service remained unavailable after retries"
                    )
                    db.commit()

            return {"status": "failed"}
