from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import ALLOWED_ORIGINS
from app.api.profile_routes import router as profile_router

app = FastAPI()

ALLOWED_ORIGINS.append("http://advisor:8004")
app.add_middleware(
    CORSMiddleware,
    # allow_origins=ALLOWED_ORIGINS,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile_router)