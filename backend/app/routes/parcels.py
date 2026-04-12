from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user, require_role
from app.models.parcel import Parcel
from app.models.user import User, UserRole
from app.schemas import ParcelCreate, ParcelResponse, ParcelUpdate

router = APIRouter()


@router.post("", response_model=ParcelResponse, status_code=201)
async def create_parcel(
    body: ParcelCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.farmer, UserRole.cooperative_admin)),
):
    """Register a new parcel (farm plot)."""
    parcel = Parcel(user_id=user.id, **body.model_dump())
    db.add(parcel)
    await db.commit()
    await db.refresh(parcel)

    from app.services.notifications import NotificationEvent, notify
    await notify(db, user_id=user.id, event=NotificationEvent.parcel_created, parcel_name=body.name, area_hectares=body.area_hectares)

    return parcel


@router.get("", response_model=list[ParcelResponse])
async def list_parcels(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List the current user's parcels."""
    result = await db.execute(
        select(Parcel)
        .where(Parcel.user_id == user.id, Parcel.is_deleted == False)
        .order_by(Parcel.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{parcel_id}", response_model=ParcelResponse)
async def get_parcel(
    parcel_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get a specific parcel."""
    parcel = await _get_user_parcel(db, parcel_id, user.id)
    return parcel


@router.put("/{parcel_id}", response_model=ParcelResponse)
async def update_parcel(
    parcel_id: UUID,
    body: ParcelUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update a parcel."""
    parcel = await _get_user_parcel(db, parcel_id, user.id)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(parcel, field, value)
    await db.commit()
    await db.refresh(parcel)
    return parcel


@router.delete("/{parcel_id}", status_code=204)
async def delete_parcel(
    parcel_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Soft-delete a parcel."""
    parcel = await _get_user_parcel(db, parcel_id, user.id)
    parcel.is_deleted = True
    await db.commit()


@router.get("/{parcel_id}/eudr-summary")
async def eudr_summary(
    parcel_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Return EUDR Due Diligence Statement data for a parcel."""
    parcel = await _get_user_parcel(db, parcel_id, user.id)
    return {
        "parcel_name": parcel.name,
        "country_of_production": parcel.country,
        "geolocation": {"lat": parcel.location_lat, "lon": parcel.location_lon},
        "area_hectares": parcel.area_hectares,
        "commodity": parcel.crop_type,
        "commodity_code": parcel.commodity_code,
        "geojson_polygon": parcel.geojson_polygon,
        "eudr_ready": bool(parcel.geojson_polygon and parcel.commodity_code),
    }


async def _get_user_parcel(db: AsyncSession, parcel_id: UUID, user_id: UUID) -> Parcel:
    result = await db.execute(
        select(Parcel).where(
            Parcel.id == parcel_id,
            Parcel.user_id == user_id,
            Parcel.is_deleted == False,
        )
    )
    parcel = result.scalar_one_or_none()
    if not parcel:
        raise HTTPException(404, "Parcel not found")
    return parcel
