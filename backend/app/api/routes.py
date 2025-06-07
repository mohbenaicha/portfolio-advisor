from fastapi import APIRouter
from app.api.portfolio_routes import router as portfolio_router
from app.api.archive_routes import router as archive_router
from app.api.advisor_routes import router as advisor_router
from app.api.auth_routes import router as auth_router
from app.api.provider_routes import router as provider_router
from app.api.registration_routes import router as registration_router
from app.api.recaptcha_route import router as recaptcha_router

router = APIRouter()

# Routers for core functionalities
router.include_router(portfolio_router, tags=["Portfolio"])
router.include_router(archive_router, tags=["Archive"])
router.include_router(advisor_router, tags=["Advisor"])
router.include_router(provider_router, prefix="/tool", tags=["Tool"])

# login, registration and validation
router.include_router(auth_router, tags=["Auth"])
router.include_router(registration_router, tags=["Registration"])
router.include_router(recaptcha_router, tags=["reCAPTCHA"])

