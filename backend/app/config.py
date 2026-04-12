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

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
