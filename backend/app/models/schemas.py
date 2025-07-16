from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime
from typing import List


class TokenAuth(BaseModel):
    token: str


class RecaptchaRequest(BaseModel):
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
    archived: bool
    final_message: Optional[bool] = False


class ArchiveCreate(BaseModel):
    portfolio_id: int
    original_question: str
    openai_response: str
    title: Optional[str] = None


class ArchiveOut(BaseModel):
    id: int
    user_id: int
    portfolio_id: int
    original_question: str
    openai_response: str
    timestamp: datetime
    summary_tags: List[str] = Field(default_factory=list)
    title: Optional[str] = None

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


class AccessRequest(BaseModel):
    email: EmailStr


class DetermineAugmentationPayload(BaseModel):
    question: str
    portfolio_id: int
    user_id: int


class RetrieveNewsPayload(BaseModel):
    question: str
    portfolio_id: int
    user_id: int


class ValidatePromptPayload(BaseModel):
    question: str
    portfolio_id: int
    user_id: int


class GetUserPortfolioPayload(BaseModel):
    portfolio_id: int
    user_id: int


class ValidateInvestmentGoalPayload(BaseModel):
    question: str
    portfolio_id: int
    user_id: int


class ValidatePromptResponse(BaseModel):
    valid: bool


class ValidateInvestmentGoalResponse(BaseModel):
    valid: bool
    short_term_objective: Optional[str] = None
    long_term_objective: Optional[str] = None


class RetrieveNewsResponse(BaseModel):
    articles: List[dict]


class UserProfileBase(BaseModel):
    portfolio_id: Optional[int] = None  # None = all portfolios
    short_term_objectives: Optional[List[str]] = []
    long_term_objectives: Optional[List[str]] = []
    sector_preferences: Optional[List[str]] = []
    regional_preferences: Optional[List[str]] = []
    asset_preferences: Optional[List[str]] = []


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(UserProfileBase):
    pass


class UserProfileResponse(UserProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ProfileDeleteRequest(BaseModel):
    profile_id: int


class ProfileDeleteResponse(BaseModel):
    deleted: bool


class GetUserProfilesPayload(BaseModel):
    user_id: int
    portfolio_id: int
    question: str | None = None


class AdminPortfolioRequest(BaseModel):
    user_id: int