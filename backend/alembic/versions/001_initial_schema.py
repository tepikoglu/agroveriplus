"""Initial schema — all Sprint 1+2 tables.

Revision ID: 001
Revises: None
Create Date: 2026-04-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, index=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("phone", sa.String(20)),
        sa.Column("role", sa.String(30), nullable=False, server_default="farmer"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Farmers (legacy — Sprint 1)
    op.create_table(
        "farmers",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("email", sa.String(255), unique=True, index=True, nullable=False),
        sa.Column("phone", sa.String(20)),
        sa.Column("organization", sa.String(300)),
        sa.Column("city", sa.String(100)),
        sa.Column("country", sa.String(100), server_default="Türkiye"),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Parcels
    op.create_table(
        "parcels",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id"), index=True, nullable=False),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("location_lat", sa.Float(), nullable=False),
        sa.Column("location_lon", sa.Float(), nullable=False),
        sa.Column("area_hectares", sa.Float(), nullable=False),
        sa.Column("crop_type", sa.String(100), nullable=False),
        sa.Column("province", sa.String(100)),
        sa.Column("district", sa.String(100)),
        sa.Column("country", sa.String(100), server_default="Türkiye"),
        sa.Column("geojson_polygon", sa.JSON()),
        sa.Column("commodity_code", sa.String(20)),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Certificates
    op.create_table(
        "certificates",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("farmer_id", sa.UUID(), sa.ForeignKey("farmers.id")),
        sa.Column("parcel_id", sa.UUID(), sa.ForeignKey("parcels.id")),
        sa.Column("original_filename", sa.String(500), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("content_type", sa.String(100), nullable=False),
        sa.Column("sha256_hash", sa.String(64), unique=True, index=True, nullable=False),
        sa.Column("ipfs_cid", sa.String(100)),
        sa.Column("certifier_name", sa.String(200)),
        sa.Column("certificate_number", sa.String(100)),
        sa.Column("product_type", sa.String(200)),
        sa.Column("valid_from", sa.DateTime(timezone=True)),
        sa.Column("valid_until", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Verifications
    op.create_table(
        "verifications",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("certificate_id", sa.UUID(), sa.ForeignKey("certificates.id")),
        sa.Column("queried_hash", sa.String(64), index=True, nullable=False),
        sa.Column("is_valid", sa.Boolean(), nullable=False),
        sa.Column("ip_address", sa.String(45)),
        sa.Column("user_agent", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # External Checks
    op.create_table(
        "external_checks",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("certificate_id", sa.UUID(), sa.ForeignKey("certificates.id"), index=True, nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("details", sa.JSON()),
        sa.Column("checked_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Notifications
    op.create_table(
        "notifications",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id"), index=True, nullable=False),
        sa.Column("event", sa.String(50), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("external_checks")
    op.drop_table("verifications")
    op.drop_table("certificates")
    op.drop_table("parcels")
    op.drop_table("farmers")
    op.drop_table("users")
