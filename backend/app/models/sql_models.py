from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Enum,
    ForeignKey,
    DateTime,
    Date,
    Text,
    MetaData
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone
from enum import Enum as PyEnum

Base = declarative_base(metadata=MetaData(schema="public"))


class AssetType(PyEnum):
    stock = "stock"
    bond = "bond"
    option = "option"
    future = "future"
    swap = "swap"


class Sector(PyEnum):
    Technology = "Technology"
    Finance = "Finance"
    Utilities = "Utilities"
    Healthcare = "Healthcare"
    ConsumerGoods = "Consumer Goods"
    Energy = "Energy"
    RealEstate = "Real Estate"
    GovernmentBonds = "Government Bonds"
    Retail = "Retail"
    LifeSciences = "Life Sciences"
    Manufacturing = "Manufacturing"


class Region(PyEnum):
    US = "US"
    Europe = "Europe"
    Asia = "Asia"
    EmergingMarkets = "Emerging Markets"
    Global = "Global"


class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, unique=False, nullable=False)
    assets = relationship(
        "Asset", back_populates="portfolio", cascade="all, delete-orphan"
    )


class Asset(Base):
    __tablename__ = "assets"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id", ondelete="CASCADE"))
    portfolio = relationship("Portfolio", back_populates="assets")

    ticker = Column(String)
    name = Column(String)
    asset_type = Column(Enum(AssetType, name="assettype", schema="public"))
    sector = Column(Enum(Sector, name="sector", schema="public"))
    region = Column(Enum(Region, name="region", schema="public"))
    market_price = Column(Float)
    units_held = Column(Float)
    is_hedge = Column(Boolean, default=False)
    hedges_asset = Column(String, nullable=True)


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    token = Column(String, unique=True, nullable=False)
    created_at = Column(
        DateTime, default=datetime.now(timezone.utc).replace(tzinfo=None)
    )


class ArchivedResponse(Base):
    __tablename__ = "archived_responses"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id", ondelete="CASCADE"))
    timestamp = Column(
        DateTime, default=datetime.now(timezone.utc).replace(tzinfo=None)
    )
    original_question = Column(Text)
    openai_response = Column(Text)
    title = Column(String(255), nullable=True)


class LLMMemory(Base):
    __tablename__ = "llm_memory"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date)
    assoc_portfolio_id = Column(
        Integer, ForeignKey("portfolios.id", ondelete="CASCADE")
    )
    short_term_goal = Column(String)
    long_term_goal = Column(String)
    created_at = Column(
        DateTime, default=datetime.now(timezone.utc).replace(tzinfo=None)
    )


class UserSession(Base):
    __tablename__ = "user_sessions"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, unique=True)  # Each user has one session
    timestamp = Column(
        DateTime, nullable=True, default=datetime.now(timezone.utc).replace(tzinfo=None)
    )  # Last activity timestamp
    total_prompts_used = Column(Integer, nullable=False, default=0)  # Tracks usage
    failed_prompts = Column(Integer, nullable=False, default=0)  # Tracks failed prompt attempts
