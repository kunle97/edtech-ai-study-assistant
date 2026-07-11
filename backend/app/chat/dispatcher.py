import uuid

from kombu.exceptions import OperationalError

from app.worker.tasks import process_chat_message


def dispatch_chat_message(message_id: uuid.UUID) -> bool:
    try:
        process_chat_message.delay(str(message_id))
        return True
    except OperationalError:
        # The message is already durable in PostgreSQL. A recovery dispatcher
        # will be added with the transactional outbox step.
        return False
