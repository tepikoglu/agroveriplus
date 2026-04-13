from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AgroVeri+"
    app_env: str = "development"
    debug: bool = True

    # Database
    database_url: str = "postgresql+asyncpg://agroveri:agroveri@db:5432/agroveriplus"

    # IPFS (Pinata)
    ipfs_api_url: str = ""
    ipfs_api_key: str = ""
    ipfs_api_secret: str = ""

    # JWT Auth
    jwt_secret: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24

    # File uploads
    max_upload_size_mb: int = 10
    allowed_extensions: list[str] = ["pdf", "jpg", "jpeg", "png"]

    # CORS
    cors_origins: list[str] = ["http://localhost:8080", "http://localhost:3000"]

    # Google OAuth (optional — leave empty to disable)
    google_client_id: str = ""

    # Email / SMTP (optional — leave empty to skip email delivery)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_name: str = "AgroVeri+"
    smtp_from_email: str = ""

    # External Registries (optional — leave empty for mock mode)
    otbis_api_url: str = ""
    ecocert_api_url: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
