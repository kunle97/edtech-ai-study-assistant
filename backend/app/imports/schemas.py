import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.imports.models import ImportStatus


class CurriculumRecord(BaseModel):
    id: str = Field(min_length=1, max_length=255)
    topic: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1)


class ImportJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filename: str
    status: ImportStatus
    total_records: int
    processed_records: int
    failed_records: int
    error_message: str | None
    created_at: datetime
    updated_at: datetime


class ImportErrorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    line_number: int
    raw_record: dict | None
    error_message: str
    created_at: datetime
