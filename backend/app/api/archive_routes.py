from fastapi import APIRouter, Depends, HTTPException
from app.db.archive_crud import save_archive, get_archive_by_id, get_archived_responses, delete_archive_by_id, delete_all_archives_by_user_id
from app.dependencies.user import get_current_user
from app.models.schemas import ArchiveCreate, ArchiveOut
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.logging_config import logger

router = APIRouter()


@router.get("/archives", response_model=list[ArchiveOut])
async def get_user_archives(
    user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    logger.debug(f"Fetching archives for user_id: {user_id}")
    result = await get_archived_responses(db=db, user_id=user_id)
    logger.info(f"Fetched {len(result) if result else 0} archives for user_id: {user_id}")
    return result or []


@router.post("/archives", response_model=ArchiveOut)
async def create_archive(
    archive_data: ArchiveCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    logger.debug(f"Creating archive for user_id: {user_id} with data: {archive_data}")
    archive = await save_archive(db=db, archive_data=archive_data, user_id=user_id)
    logger.info(f"Archive created with id: {archive.id} for user_id: {user_id}")
    return ArchiveOut.model_validate(archive)


@router.get("/archives/{id}", response_model=ArchiveOut)
async def get_archive(
    id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user),
):  
    logger.debug(f"Fetching archive with id: {id} for user_id: {user_id}")
    record = await get_archive_by_id(db=db, archive_id=id, user_id=user_id)
    if not record:
        raise HTTPException(status_code=404, detail="Archive not found")
    logger.info(f"Archive with id: {id} fetched for user_id: {user_id}")
    return ArchiveOut.model_validate(record)


@router.delete("/archives/{id}")
async def delete_archive(
    id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    logger.debug(f"Deleting archive with id: {id} for user_id: {user_id}")
    success = await delete_archive_by_id(db=db, archive_id=id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Archive not found")
    logger.info(f"Archive with id: {id} deleted for user_id: {user_id}")
    return {"deleted": True}


@router.delete("/archives")
async def delete_all_archives(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    logger.debug(f"Deleting all archives for user_id: {user_id}")
    success = await delete_all_archives_by_user_id(db=db, user_id=user_id)
    if not success:
        logger.error(f"Failed to delete archives for user_id: {user_id}")
        raise HTTPException(status_code=500, detail="Failed to delete archives")
    logger.info(f"All archives deleted for user_id: {user_id}")
    return {"deleted": True}


