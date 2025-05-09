from sqlalchemy import Column, Integer, String, Float, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from enum import Enum as PyEnum

Base = declarative_base()

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

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    assets = relationship("Asset", back_populates="portfolio", cascade="all, delete-orphan")

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    portfolio = relationship("Portfolio", back_populates="assets")

    ticker = Column(String)
    name = Column(String)
    asset_type = Column(Enum(AssetType))
    sector = Column(Enum(Sector))
    region = Column(Enum(Region))
    market_price = Column(Float)
    units_held = Column(Float)
    is_hedge = Column(Boolean, default=False)
    hedges_asset = Column(String, nullable=True)
