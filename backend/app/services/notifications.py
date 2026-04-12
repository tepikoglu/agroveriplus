"""Notification service — logs events to DB.

Future: add email, push, and webhook delivery channels.
"""

from enum import Enum as PyEnum
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


class NotificationEvent(str, PyEnum):
    certificate_uploaded = "certificate_uploaded"
    certificate_verified = "certificate_verified"
    certificate_expired = "certificate_expired"
    external_check_failed = "external_check_failed"
    parcel_created = "parcel_created"


EVENT_TEMPLATES = {
    NotificationEvent.certificate_uploaded: {
        "title": "New certificate uploaded",
        "body": "Certificate '{filename}' has been uploaded and sealed with SHA-256.",
    },
    NotificationEvent.certificate_verified: {
        "title": "Certificate verified",
        "body": "Certificate '{filename}' was verified by a consumer.",
    },
    NotificationEvent.certificate_expired: {
        "title": "Certificate expired",
        "body": "Certificate '{filename}' has expired. Please upload a renewed certificate.",
    },
    NotificationEvent.external_check_failed: {
        "title": "External verification failed",
        "body": "Certificate '{filename}' could not be verified by {provider}.",
    },
    NotificationEvent.parcel_created: {
        "title": "New parcel registered",
        "body": "Parcel '{parcel_name}' ({area_hectares} ha) has been registered.",
    },
}


async def notify(
    db: AsyncSession,
    *,
    user_id: UUID,
    event: NotificationEvent,
    **kwargs,
) -> Notification:
    """Create a notification for a user. kwargs are used to format template strings."""
    template = EVENT_TEMPLATES.get(event, {"title": event.value, "body": ""})
    title = template["title"].format(**kwargs) if kwargs else template["title"]
    body = template["body"].format(**kwargs) if kwargs else template["body"]

    n = Notification(
        user_id=user_id,
        event=event.value,
        title=title,
        body=body,
    )
    db.add(n)
    await db.commit()
    await db.refresh(n)
    return n


async def get_user_notifications(
    db: AsyncSession, user_id: UUID, *, unread_only: bool = False, limit: int = 50
) -> list[Notification]:
    q = select(Notification).where(Notification.user_id == user_id)
    if unread_only:
        q = q.where(Notification.is_read == False)
    q = q.order_by(Notification.created_at.desc()).limit(limit)
    result = await db.execute(q)
    return list(result.scalars().all())


async def mark_read(db: AsyncSession, notification_id: UUID, user_id: UUID) -> bool:
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
    )
    n = result.scalar_one_or_none()
    if not n:
        return False
    n.is_read = True
    await db.commit()
    return True
