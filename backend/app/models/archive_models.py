from sqlalchemy import Column, Integer, String, Text, DateTime, ARRAY, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ArchivedResponse(Base):
    __tablename__ = "archived_responses"

    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    original_question = Column(Text)
    openai_response = Column(Text)
    associated_article_ids = Column(ARRAY(Text))  # Store article URLs or hashes
    summary_tags = Column(ARRAY(String))
