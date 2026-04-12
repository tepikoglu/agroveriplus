import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.services.notifications import get_user_notifications, mark_read

router = APIRouter()


class NotificationResponse(BaseModel):
    id: uuid.UUID
    event: str
    title: str
    body: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("", response_model=list[NotificationResponse])
async def list_notifications(
    unread_only: bool = False,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List notifications for the current user."""
    return await get_user_notifications(db, user.id, unread_only=unread_only)


@router.post("/{notification_id}/read", status_code=204)
async def read_notification(
    notification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Mark a notification as read."""
    ok = await mark_read(db, notification_id, user.id)
    if not ok:
        raise HTTPException(404, "Notification not found")
