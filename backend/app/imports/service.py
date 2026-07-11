import hashlib
import os
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.imports.models import ImportJob, ImportStatus


UPLOAD_DIRECTORY = Path(
    os.getenv("UPLOAD_DIRECTORY", "uploads")
).resolve()
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".jsonl"}
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024


class DuplicateImportError(Exception):
    def __init__(self, job: ImportJob) -> None:
        self.job = job


class InvalidImportFileError(Exception):
    pass


def save_import_file(
    db: Session,
    *,
    upload: UploadFile,
    admin_id: uuid.UUID,
) -> ImportJob:
    filename = upload.filename or "curriculum.jsonl"
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise InvalidImportFileError("Only .jsonl files are supported")

    destination = UPLOAD_DIRECTORY / f"{uuid.uuid4()}.jsonl"
    digest = hashlib.sha256()
    total_size = 0

    with destination.open("wb") as output:
        while chunk := upload.file.read(1024 * 1024):
            total_size += len(chunk)

            if total_size > MAX_FILE_SIZE_BYTES:
                destination.unlink(missing_ok=True)
                raise InvalidImportFileError(
                    "File exceeds the 50 MB upload limit"
                )

            digest.update(chunk)
            output.write(chunk)

    file_hash = digest.hexdigest()

    existing = db.scalar(
        select(ImportJob).where(ImportJob.file_hash == file_hash)
    )

    if existing is not None:
        if existing.status == ImportStatus.FAILED:
            existing.filename = filename
            existing.file_path = str(destination)
            existing.status = ImportStatus.PENDING
            existing.total_records = 0
            existing.processed_records = 0
            existing.failed_records = 0
            existing.error_message = None
            db.flush()
            return existing

        destination.unlink(missing_ok=True)
        raise DuplicateImportError(existing)

    job = ImportJob(
        created_by_id=admin_id,
        filename=filename,
        file_path=str(destination),
        file_hash=file_hash,
        status=ImportStatus.PENDING,
    )

    db.add(job)
    db.flush()

    return job
