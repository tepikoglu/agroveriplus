from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, case, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import require_role
from app.models.certificate import Certificate
from app.models.external_check import ExternalCheck
from app.models.notification import Notification
from app.models.parcel import Parcel
from app.models.user import User, UserRole
from app.models.verification import Verification
from app.schemas import UserResponse

router = APIRouter()

require_admin = require_role(UserRole.admin)


# ─── System Stats ────────────────────────────────────────

@router.get("/stats")
async def system_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    """System-wide statistics for admin dashboard."""
    users_total = (await db.execute(select(func.count(User.id)))).scalar() or 0
    users_active = (await db.execute(select(func.count(User.id)).where(User.is_active == True))).scalar() or 0
    certs_total = (await db.execute(select(func.count(Certificate.id)))).scalar() or 0
    parcels_total = (await db.execute(select(func.count(Parcel.id)).where(Parcel.is_deleted == False))).scalar() or 0
    verifications_total = (await db.execute(select(func.count(Verification.id)))).scalar() or 0
    checks_total = (await db.execute(select(func.count(ExternalCheck.id)))).scalar() or 0

    # Role breakdown
    role_q = await db.execute(
        select(User.role, func.count(User.id)).group_by(User.role)
    )
    roles = {str(r): c for r, c in role_q.all()}

    # External check status breakdown
    check_q = await db.execute(
        select(ExternalCheck.status, func.count(ExternalCheck.id)).group_by(ExternalCheck.status)
    )
    check_statuses = {s: c for s, c in check_q.all()}

    return {
        "users": {"total": users_total, "active": users_active, "by_role": roles},
        "certificates": {"total": certs_total},
        "parcels": {"total": parcels_total},
        "verifications": {"total": verifications_total},
        "external_checks": {"total": checks_total, "by_status": check_statuses},
    }


# ─── User Management ────────────────────────────────────

@router.get("/users", response_model=list[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    """List all users."""
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return [UserResponse.model_validate(u) for u in result.scalars().all()]


@router.put("/users/{user_id}/role")
async def change_user_role(
    user_id: UUID,
    role: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Change a user's role."""
    valid = {r.value for r in UserRole}
    if role not in valid:
        raise HTTPException(400, f"Invalid role. Choose from: {sorted(valid)}")

    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(404, "User not found")

    target.role = role
    await db.commit()
    return {"id": str(target.id), "email": target.email, "role": role}


@router.put("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Deactivate a user account."""
    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(404, "User not found")
    if target.id == admin.id:
        raise HTTPException(400, "Cannot deactivate yourself")

    target.is_active = False
    await db.commit()
    return {"id": str(target.id), "is_active": False}


@router.put("/users/{user_id}/activate")
async def activate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Reactivate a user account."""
    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(404, "User not found")

    target.is_active = True
    await db.commit()
    return {"id": str(target.id), "is_active": True}


# ─── All Certificates ───────────────────────────────────

@router.get("/certificates")
async def list_all_certificates(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    """List all certificates in the system."""
    result = await db.execute(
        select(Certificate).order_by(Certificate.created_at.desc()).limit(100)
    )
    certs = result.scalars().all()
    return [
        {
            "id": str(c.id),
            "filename": c.original_filename,
            "sha256": c.sha256_hash[:16] + "...",
            "certifier": c.certifier_name,
            "product": c.product_type,
            "farmer_id": str(c.farmer_id) if c.farmer_id else None,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in certs
    ]
