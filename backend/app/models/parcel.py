import uuid
from datetime import datetime

from sqlalchemy import Float, JSON, String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Parcel(Base):
    __tablename__ = "parcels"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(300))
    location_lat: Mapped[float] = mapped_column(Float)
    location_lon: Mapped[float] = mapped_column(Float)
    area_hectares: Mapped[float] = mapped_column(Float)
    crop_type: Mapped[str] = mapped_column(String(100))
    province: Mapped[str | None] = mapped_column(String(100))
    district: Mapped[str | None] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(100), default="Türkiye")

    # EUDR fields
    geojson_polygon: Mapped[dict | None] = mapped_column(JSON, default=None)
    commodity_code: Mapped[str | None] = mapped_column(String(20))

    is_deleted: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    certificates: Mapped[list["Certificate"]] = relationship(back_populates="parcel")  # noqa: F821
