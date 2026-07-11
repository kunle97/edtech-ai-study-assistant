from app.auth.models import User, UserRole
from app.auth.security import hash_password
from app.chat.models import MessageStatus
from app.chat.service import create_session, queue_user_message


def test_create_session(db_session):
    user = User(
        email="chat-user@example.com",
        password_hash=hash_password("StudyPass123!"),
        role=UserRole.STUDENT,
    )
    db_session.add(user)
    db_session.flush()

    session = create_session(db_session, user=user, title="Biology")

    assert session.id is not None
    assert session.user_id == user.id
    assert session.title == "Biology"


def test_queue_message(db_session):
    user = User(
        email="message-user@example.com",
        password_hash=hash_password("StudyPass123!"),
        role=UserRole.STUDENT,
    )
    db_session.add(user)
    db_session.flush()

    session = create_session(db_session, user=user, title=None)

    message = queue_user_message(
        db_session,
        session_id=session.id,
        user_id=user.id,
        content=" Explain photosynthesis ",
    )

    assert message.content == "Explain photosynthesis"
    assert message.status == MessageStatus.QUEUED
