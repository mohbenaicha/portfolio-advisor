from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from typing import List

class Asset(BaseModel):
    ticker: str
    name: str
    asset_type: str
    sector: str
    region: str
    market_price: float
    units_held: float
    is_hedge: Optional[bool] = False
    hedges_asset: Optional[str] = None


class Portfolio(BaseModel):
    id: int
    name: str
    assets: List[Asset]


class PromptRequest(BaseModel):
    question: str
    portfolio_data: List[Asset]
    portfolio_summary: (
        dict  # {"asset_types": [...], "sectors": [...], "regions": [...]}
    )


class Article(BaseModel):
    title: str
    source: str
    url: str
    summary: str
    time_published: str


class PromptResponse(BaseModel):
    summary: str
    articles: List[Article]


class ArchiveCreate(BaseModel):
    portfolio_id: int
    original_question: str
    openai_response: str
    article_ids: List[str]
    summary_tags: List[str]


class ArchiveOut(BaseModel):
    id: int
    portfolio_id: int
    original_question: str
    openai_response: str
    article_ids: List[str] = Field(alias="associated_article_ids")  # ✅ real field name in DB
    summary_tags: List[str]
    timestamp: datetime

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }


class AssetCreate(BaseModel):
    ticker: str
    name: str
    asset_type: str
    sector: str
    region: str
    market_price: float
    units_held: float
    is_hedge: bool = False
    hedges_asset: Optional[str] = None


class PortfolioCreate(BaseModel):
    name: str
    assets: List[AssetCreate]


class AssetOut(AssetCreate):
    id: int

    model_config = {"from_attributes": True}


class PortfolioOut(BaseModel):
    id: int
    name: str
    assets: List[AssetOut]

    model_config = {"from_attributes": True}
