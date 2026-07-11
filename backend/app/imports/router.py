import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from sqlalchemy import select

from app.audit.service import record_audit_event
from app.auth.dependencies import AdminUser, DatabaseSession
from app.imports.models import ImportError, ImportJob
from app.imports.schemas import ImportErrorResponse, ImportJobResponse
from app.imports.service import (
    DuplicateImportError,
    InvalidImportFileError,
    save_import_file,
)
from app.imports.tasks import process_curriculum_import


router = APIRouter(
    prefix="/api/v1/admin/imports",
    tags=["Admin Imports"],
)


@router.post(
    "",
    response_model=ImportJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def upload_curriculum(
    admin: AdminUser,
    db: DatabaseSession,
    file: UploadFile = File(...),
) -> ImportJobResponse:
    try:
        job = save_import_file(
            db,
            upload=file,
            admin_id=admin.id,
        )
    except DuplicateImportError as exc:
        return ImportJobResponse.model_validate(exc.job)
    except InvalidImportFileError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    record_audit_event(
        db,
        actor_id=admin.id,
        action="curriculum.import_started",
        target_type="import_job",
        target_id=str(job.id),
        metadata={"filename": job.filename},
    )

    db.commit()
    db.refresh(job)

    process_curriculum_import.delay(str(job.id))

    return ImportJobResponse.model_validate(job)


@router.get("", response_model=list[ImportJobResponse])
def list_imports(
    admin: AdminUser,
    db: DatabaseSession,
) -> list[ImportJobResponse]:
    jobs = db.scalars(
        select(ImportJob).order_by(ImportJob.created_at.desc())
    ).all()

    return [
        ImportJobResponse.model_validate(job)
        for job in jobs
    ]


@router.get("/{job_id}", response_model=ImportJobResponse)
def get_import(
    job_id: uuid.UUID,
    admin: AdminUser,
    db: DatabaseSession,
) -> ImportJobResponse:
    job = db.get(ImportJob, job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Import job not found",
        )

    return ImportJobResponse.model_validate(job)


@router.get(
    "/{job_id}/errors",
    response_model=list[ImportErrorResponse],
)
def list_import_errors(
    job_id: uuid.UUID,
    admin: AdminUser,
    db: DatabaseSession,
) -> list[ImportErrorResponse]:
    errors = db.scalars(
        select(ImportError)
        .where(ImportError.import_job_id == job_id)
        .order_by(ImportError.line_number.asc())
    ).all()

    return [
        ImportErrorResponse.model_validate(error)
        for error in errors
    ]
