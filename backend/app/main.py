import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.middleware import RateLimitMiddleware, RequestLoggingMiddleware
from app.routes.admin import router as admin_router
from app.routes.auth import router as auth_router
from app.routes.certificates import router as certificates_router
from app.routes.dashboard import router as dashboard_router
from app.routes.health import router as health_router
from app.routes.notifications import router as notifications_router
from app.routes.parcels import router as parcels_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (use Alembic migrations in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    description="Digital Certification Verification Platform for Organic Agriculture",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(certificates_router, prefix="/api/certificates", tags=["certificates"])
app.include_router(parcels_router, prefix="/api/parcels", tags=["parcels"])
app.include_router(notifications_router, prefix="/api/notifications", tags=["notifications"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
