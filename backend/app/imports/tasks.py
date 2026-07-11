import json
import uuid

from pydantic import ValidationError
from sqlalchemy import select

from app.db.session import SessionLocal
from app.imports.models import (
    CurriculumContent,
    ImportError,
    ImportJob,
    ImportStatus,
)
from app.imports.schemas import CurriculumRecord
from app.worker.celery_app import celery_app


PROGRESS_UPDATE_INTERVAL = 100


@celery_app.task(
    name="imports.process_curriculum",
    acks_late=True,
)
def process_curriculum_import(job_id: str) -> dict[str, int | str]:
    parsed_job_id = uuid.UUID(job_id)

    with SessionLocal() as db:
        job = db.get(ImportJob, parsed_job_id)

        if job is None:
            return {"status": "not_found"}

        if job.status == ImportStatus.COMPLETE:
            return {"status": "complete"}

        job.status = ImportStatus.RUNNING
        job.error_message = None
        db.commit()

        processed = job.processed_records
        failed = job.failed_records
        total = 0

        try:
            with open(job.file_path, encoding="utf-8") as import_file:
                for line_number, line in enumerate(import_file, start=1):
                    total += 1
                    raw_record = None

                    try:
                        raw_record = json.loads(line)
                        record = CurriculumRecord.model_validate(raw_record)

                        existing = db.scalar(
                            select(CurriculumContent).where(
                                CurriculumContent.external_id == record.id
                            )
                        )

                        if existing is None:
                            content = CurriculumContent(
                                external_id=record.id,
                                topic=record.topic.strip(),
                                body=record.body.strip(),
                                source_import_id=job.id,
                            )
                            db.add(content)
                        else:
                            existing.topic = record.topic.strip()
                            existing.body = record.body.strip()

                        processed += 1

                    except (json.JSONDecodeError, ValidationError) as exc:
                        failed += 1

                        db.add(
                            ImportError(
                                import_job_id=job.id,
                                line_number=line_number,
                                raw_record=(
                                    raw_record
                                    if isinstance(raw_record, dict)
                                    else None
                                ),
                                error_message=str(exc),
                            )
                        )

                    if total % PROGRESS_UPDATE_INTERVAL == 0:
                        job.total_records = total
                        job.processed_records = processed
                        job.failed_records = failed
                        db.commit()

            job.total_records = total
            job.processed_records = processed
            job.failed_records = failed
            job.status = ImportStatus.COMPLETE
            db.commit()

            return {
                "status": "complete",
                "processed": processed,
                "failed": failed,
            }

        except Exception as exc:
            db.rollback()

            job = db.get(ImportJob, parsed_job_id)

            if job is not None:
                job.status = ImportStatus.FAILED
                job.error_message = str(exc)[:2000]
                db.commit()

            raise
