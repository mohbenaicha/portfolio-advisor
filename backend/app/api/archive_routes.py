from fastapi import APIRouter, Depends, HTTPException
from app.db.archive import save_archive, list_archives, get_archive_by_id
from app.models.schemas import ArchiveCreate, ArchiveOut
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db

router = APIRouter()


@router.get("/archives", response_model=list[ArchiveOut])
async def get_all_archives(db: AsyncSession = Depends(get_db)):
    return await list_archives(db)


@router.post("/archives", response_model=ArchiveOut)
async def create_archive(
    archive_data: ArchiveCreate, db: AsyncSession = Depends(get_db)
):
    archive = await save_archive(db, archive_data)
    return ArchiveOut.model_validate(archive)


@router.get("/responses/{id}", response_model=ArchiveOut)
async def get_archive(id: int, db: AsyncSession = Depends(get_db)):
    record = await get_archive_by_id(db, id)
    if not record:
        raise HTTPException(status_code=404, detail="Archive not found")
    return record
