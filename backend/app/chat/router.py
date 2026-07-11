import uuid

from fastapi import APIRouter, HTTPException, status

from app.auth.dependencies import ActiveUser, DatabaseSession
from app.auth.models import UserRole
from app.chat.schemas import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatSessionCreate,
    ChatSessionDetail,
    ChatSessionResponse,
)
from app.chat.service import (
    ChatSessionNotFoundError,
    create_session,
    get_session_with_messages,
    list_user_sessions,
    queue_user_message,
)


router = APIRouter(
    prefix="/api/v1/chat",
    tags=["Chat"],
)


def require_student(user: ActiveUser) -> None:
    if user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student access required",
        )


@router.post(
    "/sessions",
    response_model=ChatSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_session(
    payload: ChatSessionCreate,
    user: ActiveUser,
    db: DatabaseSession,
) -> ChatSessionResponse:
    require_student(user)

    session = create_session(
        db,
        user=user,
        title=payload.title,
    )

    db.commit()
    db.refresh(session)

    return ChatSessionResponse.model_validate(session)


@router.get(
    "/sessions",
    response_model=list[ChatSessionResponse],
)
def list_sessions(
    user: ActiveUser,
    db: DatabaseSession,
) -> list[ChatSessionResponse]:
    require_student(user)

    sessions = list_user_sessions(
        db,
        user_id=user.id,
    )

    return [
        ChatSessionResponse.model_validate(session)
        for session in sessions
    ]


@router.get(
    "/sessions/{session_id}",
    response_model=ChatSessionDetail,
)
def get_session(
    session_id: uuid.UUID,
    user: ActiveUser,
    db: DatabaseSession,
) -> ChatSessionDetail:
    require_student(user)

    try:
        session = get_session_with_messages(
            db,
            session_id=session_id,
            user_id=user.id,
        )
    except ChatSessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found",
        )

    return ChatSessionDetail.model_validate(session)


@router.post(
    "/sessions/{session_id}/messages",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def send_message(
    session_id: uuid.UUID,
    payload: ChatMessageCreate,
    user: ActiveUser,
    db: DatabaseSession,
) -> ChatMessageResponse:
    require_student(user)

    try:
        message = queue_user_message(
            db,
            session_id=session_id,
            user_id=user.id,
            content=payload.content,
        )
    except ChatSessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found",
        )

    db.commit()
    db.refresh(message)

    return ChatMessageResponse.model_validate(message)
