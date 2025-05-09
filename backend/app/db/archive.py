from app.models.archive_models import ArchivedResponse
from sqlalchemy.orm import Session
from datetime import datetime

def save_archive(db: Session, archive_data):
    record = ArchivedResponse(
        portfolio_id=archive_data.portfolio_id,
        original_question=archive_data.original_question,
        openai_response=archive_data.openai_response,
        associated_article_ids=archive_data.article_ids,
        summary_tags=archive_data.summary_tags,
        timestamp=datetime.utcnow()
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def list_archives(db: Session):
    return db.query(ArchivedResponse).order_by(ArchivedResponse.timestamp.desc()).all()

def get_archive_by_id(db: Session, archive_id: int):
    return db.query(ArchivedResponse).filter(ArchivedResponse.id == archive_id).first()
