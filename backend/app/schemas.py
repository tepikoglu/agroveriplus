import uuid
from datetime import datetime

from pydantic import BaseModel


# --- Auth ---

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    phone: str | None = None
    role: str = "farmer"


class LoginRequest(BaseModel):
    email: str
    password: str


class GoogleAuthRequest(BaseModel):
    id_token: str
    role: str = "farmer"


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    phone: str | None
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Certificate ---

class CertificateUploadResponse(BaseModel):
    id: uuid.UUID
    sha256_hash: str
    original_filename: str
    file_size: int
    ipfs_cid: str | None
    created_at: datetime
    qr_data: str

    model_config = {"from_attributes": True}


class CertificateDetail(BaseModel):
    id: uuid.UUID
    sha256_hash: str
    original_filename: str
    file_size: int
    content_type: str
    ipfs_cid: str | None
    certifier_name: str | None
    certificate_number: str | None
    product_type: str | None
    parcel_id: uuid.UUID | None = None
    valid_from: datetime | None
    valid_until: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CertificateMetadataUpdate(BaseModel):
    certifier_name: str | None = None
    certificate_number: str | None = None
    product_type: str | None = None
    parcel_id: uuid.UUID | None = None
    valid_from: datetime | None = None
    valid_until: datetime | None = None


# --- Verification ---

class VerifyRequest(BaseModel):
    hash: str


class VerifyResponse(BaseModel):
    verified: bool
    message: str
    certificate: CertificateDetail | None = None


# --- Parcel ---

class ParcelCreate(BaseModel):
    name: str
    location_lat: float
    location_lon: float
    area_hectares: float
    crop_type: str
    province: str | None = None
    district: str | None = None
    country: str = "Türkiye"
    geojson_polygon: dict | None = None
    commodity_code: str | None = None


class ParcelUpdate(BaseModel):
    name: str | None = None
    location_lat: float | None = None
    location_lon: float | None = None
    area_hectares: float | None = None
    crop_type: str | None = None
    province: str | None = None
    district: str | None = None
    geojson_polygon: dict | None = None
    commodity_code: str | None = None


class ParcelResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    location_lat: float
    location_lon: float
    area_hectares: float
    crop_type: str
    province: str | None
    district: str | None
    country: str
    geojson_polygon: dict | None
    commodity_code: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- External Check ---

class ExternalCheckResponse(BaseModel):
    id: uuid.UUID
    provider: str
    status: str
    details: dict | None
    checked_at: datetime

    model_config = {"from_attributes": True}


class ExternalCheckResult(BaseModel):
    certificate_id: uuid.UUID
    checks: list[ExternalCheckResponse]
    summary: str


# --- Dashboard ---

class DashboardStats(BaseModel):
    total_certificates: int
    total_verifications: int
    total_parcels: int
    my_certificates: int
    my_parcels: int
    recent_verifications: int
