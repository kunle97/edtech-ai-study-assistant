import uuid

from sqlalchemy.orm import Session

from app.ai.retrieval import normalize_retrieval_query, retrieve_curriculum
from app.auth.models import User, UserRole
from app.auth.security import hash_password
from app.imports.models import CurriculumContent, ImportJob, ImportStatus


def test_normalize_retrieval_query_removes_instruction_words() -> None:
    result = normalize_retrieval_query(
        "Explain Newton's first law."
    )

    assert result == "newton OR first OR law"


def test_normalize_retrieval_query_keeps_subject_term() -> None:
    result = normalize_retrieval_query(
        "What is photosynthesis?"
    )

    assert result == "photosynthesis"


def test_retrieve_curriculum_finds_relevant_content(
    db_session: Session,
) -> None:
    admin = User(
        email=f"retrieval-admin-{uuid.uuid4()}@example.com",
        password_hash=hash_password("StudyPass123!"),
        role=UserRole.ADMIN,
    )
    db_session.add(admin)
    db_session.flush()

    import_job = ImportJob(
        created_by_id=admin.id,
        filename="test.jsonl",
        file_path="/tmp/test.jsonl",
        file_hash=uuid.uuid4().hex * 2,
        status=ImportStatus.COMPLETE,
    )
    db_session.add(import_job)
    db_session.flush()

    db_session.add(
        CurriculumContent(
            external_id=f"physics-test-{uuid.uuid4()}",
            topic="Physics",
            body=(
                "Newton's first law states that an object remains "
                "at rest or in uniform motion unless acted upon by "
                "a net external force."
            ),
            source_import_id=import_job.id,
        )
    )
    db_session.flush()

    results = retrieve_curriculum(
        db_session,
        query="Explain Newton's first law.",
    )

    assert results
    assert any(
        result["external_id"].startswith("physics-test-")
        for result in results
    )
    assert all(result["topic"] == "Physics" for result in results)
