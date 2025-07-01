from fastapi import APIRouter, Depends, HTTPException
from app.db.archive_crud import save_archive, get_archive_by_id, get_archived_responses, delete_archive_by_id, delete_all_archives_by_user_id
from app.dependencies.user import get_current_user
from app.models.schemas import ArchiveCreate, ArchiveOut
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from html import escape

router = APIRouter()


@router.get("/archives", response_model=list[ArchiveOut])
async def get_user_archives(
    user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    result = await get_archived_responses(db=db, user_id=user_id)
    return result or []


@router.post("/archives", response_model=ArchiveOut)
async def create_archive(
    archive_data: ArchiveCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    archive = await save_archive(db=db, archive_data=archive_data, user_id=user_id)
    return ArchiveOut.model_validate(archive)


@router.get("/responses/{id}", response_model=ArchiveOut)
async def get_archive(
    id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    record = await get_archive_by_id(db=db, archive_id=id, user_id=user_id)
    if not record:
        raise HTTPException(status_code=404, detail="Archive not found")
    return ArchiveOut.model_validate(record)


@router.delete("/archives/{id}")
async def delete_archive(
    id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    success = await delete_archive_by_id(db=db, archive_id=id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Archive not found")
    return {"deleted": True}


@router.delete("/archives")
async def delete_all_archives(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    success = await delete_all_archives_by_user_id(db=db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete archives")
    return {"deleted": True}


