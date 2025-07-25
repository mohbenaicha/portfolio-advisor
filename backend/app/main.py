from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.models.sql_models import Base
from app.api.routes import router as api_router
from app.db.session import engine
from app.scheduler.session_cleanup import start_scheduler, shutdown_scheduler
from app.config import DATABASE_URL, ALLOWED_ORIGINS

print("DEBUG: SQL Database URL:", DATABASE_URL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    start_scheduler()
    yield
    shutdown_scheduler()
    
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
