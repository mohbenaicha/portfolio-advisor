from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from typing import List


class TokenAuth(BaseModel):
    token: str


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
    portfolio_id: int


class PromptResponse(BaseModel):
    summary: str


class ArchiveCreate(BaseModel):
    portfolio_id: int
    original_question: str
    openai_response: str


class ArchiveOut(BaseModel):
    id: int
    user_id: int
    portfolio_id: int
    original_question: str
    openai_response: str
    timestamp: datetime
    summary_tags: List[str] = Field(default_factory=list)

    model_config = {"from_attributes": True, "populate_by_name": True}


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
