import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select

from app.admin.schemas import AdminUserResponse, UserListResponse
from app.audit.service import record_audit_event
from app.auth.dependencies import AdminUser, DatabaseSession
from app.auth.models import User


router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin"],
)


@router.get("/users", response_model=UserListResponse)
def list_users(
    admin: AdminUser,
    db: DatabaseSession,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> UserListResponse:
    users = db.scalars(
        select(User)
        .order_by(User.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()

    total = db.scalar(select(func.count()).select_from(User)) or 0

    return UserListResponse(
        users=[AdminUserResponse.model_validate(user) for user in users],
        total=total,
    )


@router.post(
    "/users/{user_id}/suspend",
    response_model=AdminUserResponse,
)
def suspend_user(
    user_id: uuid.UUID,
    admin: AdminUser,
    db: DatabaseSession,
) -> AdminUserResponse:
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Administrators cannot suspend themselves",
        )

    if not user.is_suspended:
        user.is_suspended = True
        user.suspended_at = datetime.now(timezone.utc)

        record_audit_event(
            db,
            actor_id=admin.id,
            action="user.suspended",
            target_type="user",
            target_id=str(user.id),
            metadata={"email": user.email},
        )

        db.commit()
        db.refresh(user)

    return AdminUserResponse.model_validate(user)


@router.post(
    "/users/{user_id}/reinstate",
    response_model=AdminUserResponse,
)
def reinstate_user(
    user_id: uuid.UUID,
    admin: AdminUser,
    db: DatabaseSession,
) -> AdminUserResponse:
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.is_suspended:
        user.is_suspended = False
        user.suspended_at = None

        record_audit_event(
            db,
            actor_id=admin.id,
            action="user.reinstated",
            target_type="user",
            target_id=str(user.id),
            metadata={"email": user.email},
        )

        db.commit()
        db.refresh(user)

    return AdminUserResponse.model_validate(user)