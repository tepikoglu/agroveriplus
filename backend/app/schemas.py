import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


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
    valid_from: datetime | None
    valid_until: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Verification ---

class VerifyRequest(BaseModel):
    hash: str


class VerifyResponse(BaseModel):
    verified: bool
    message: str
    certificate: CertificateDetail | None = None
