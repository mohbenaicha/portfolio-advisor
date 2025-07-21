from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import ALLOWED_ORIGINS, BACKEND_SERVICE_MAP
from app.api.advisor_routes import router as advisor_router
from app.api.provider_routes import router as provider_router

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    # allow_origins=ALLOWED_ORIGINS,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(provider_router, prefix="/tool", tags=["Tool"])
app.include_router(advisor_router)
