from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.db.session import AsyncSessionLocal
from app.db.user_session import UserSessionManager

scheduler = AsyncIOScheduler()

async def cleanup_sessions_job():
    async with AsyncSessionLocal() as db_session:
        await UserSessionManager.fix_null_sessions(db_session)
        await UserSessionManager.cleanup_sessions(db_session)

def start_scheduler():
    interval = 1
    scheduler.add_job(
        cleanup_sessions_job,
        trigger="interval",
        hours=interval,
        id="cleanup_sessions",
        next_run_time=datetime.now()
    )
    scheduler.start()
    print(f"Scheduler started for session cleanup every {interval} hr(s).")

def shutdown_scheduler():
    scheduler.shutdown()
