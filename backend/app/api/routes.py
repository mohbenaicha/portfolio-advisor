# backend/app/api/routes.py

from fastapi import APIRouter
from .portfolio_routes import router as portfolio_router
from .archive_routes import router as archive_router
from .advisor_routes import router as advisor_router
from .auth_routes import router as auth_router
from .session_crash_recovery_test import router as session_router
router = APIRouter()

# Mount sub-routers with prefixes
router.include_router(portfolio_router, tags=["Portfolio"])
router.include_router(archive_router, tags=["Archive"])
router.include_router(advisor_router, tags=["Advisor"])
router.include_router(auth_router, tags=["Auth"])
router.include_router(session_router, prefix="/session", tags=["Session"])

