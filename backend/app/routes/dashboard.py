from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models.certificate import Certificate
from app.models.parcel import Parcel
from app.models.user import User
from app.models.verification import Verification
from app.schemas import DashboardStats

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Dashboard statistics for the current user."""
    total_certs = (await db.execute(select(func.count(Certificate.id)))).scalar() or 0
    total_verif = (await db.execute(select(func.count(Verification.id)))).scalar() or 0
    total_parcels = (await db.execute(
        select(func.count(Parcel.id)).where(Parcel.is_deleted == False)
    )).scalar() or 0

    # User-specific
    my_certs = (await db.execute(
        select(func.count(Certificate.id)).where(Certificate.farmer_id == user.id)
    )).scalar() or 0
    my_parcels = (await db.execute(
        select(func.count(Parcel.id)).where(Parcel.user_id == user.id, Parcel.is_deleted == False)
    )).scalar() or 0

    # Recent verifications (last 7 days)
    from datetime import datetime, timedelta, timezone
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    recent = (await db.execute(
        select(func.count(Verification.id)).where(Verification.created_at >= week_ago)
    )).scalar() or 0

    return DashboardStats(
        total_certificates=total_certs,
        total_verifications=total_verif,
        total_parcels=total_parcels,
        my_certificates=my_certs,
        my_parcels=my_parcels,
        recent_verifications=recent,
    )
