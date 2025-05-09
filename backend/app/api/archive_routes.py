from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.archive import save_archive, list_archives, get_archive_by_id
from app.models.schemas import ArchiveCreate, ArchiveOut
from app.db.session import get_db

router = APIRouter()

@router.get("/archives", response_model=list[ArchiveOut])
def get_all_archives(db: Session = Depends(get_db)):
    return list_archives(db)

@router.post("/archives", response_model=ArchiveOut)
def create_archive(archive: ArchiveCreate, db: Session = Depends(get_db)):
    return save_archive(db, archive)

@router.get("/responses/{id}", response_model=ArchiveOut)
def get_archive(id: int, db: Session = Depends(get_db)):
    record = get_archive_by_id(db, id)
    if not record:
        raise HTTPException(status_code=404, detail="Archive not found")
    return record
