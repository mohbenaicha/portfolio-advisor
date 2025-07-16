from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.portfolio_crud import (
    create_portfolio,
    delete_portfolio,
    update_portfolio,
    get_portfolio_by_id,
    get_user_portfolios
)
from app.models.schemas import PortfolioCreate, PortfolioOut, AdminPortfolioRequest
from app.dependencies.user import get_current_user
from app.db.session import get_db

router = APIRouter(prefix="/portfolios", tags=["portfolios"])


@router.get("/", response_model=list[PortfolioOut])
async def read_user_portfolios(user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    portfolios = await get_user_portfolios(user_id=user_id, db=db)
    return [PortfolioOut.model_validate(p) for p in portfolios]

@router.post("/", response_model=PortfolioOut)
async def add_portfolio(
    portfolio: PortfolioCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    created = await create_portfolio(db=db, data=portfolio, user_id=user_id)
    return PortfolioOut.model_validate(created)


@router.delete("/{id}")
async def remove_portfolio(
    id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    deleted = await delete_portfolio(db, id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return {"deleted": True}


@router.put("/{id}", response_model=PortfolioOut)
async def update_portfolio_route(
    id: int,
    portfolio: PortfolioCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    updated = await update_portfolio(db, id, portfolio, user_id)
    return PortfolioOut.model_validate(updated)


@router.get("/{id}", response_model=PortfolioOut)
async def get_portfolio(
    id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    portfolio = await get_portfolio_by_id(db, id, user_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return PortfolioOut.model_validate(portfolio)


@router.get("/admin/{id}", response_model=PortfolioOut)
async def get_portfolio_as_admin(
    id: int,
    request: AdminPortfolioRequest,
    db: AsyncSession = Depends(get_db)
):
    portfolio = await get_portfolio_by_id(db, id, request.user_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return PortfolioOut.model_validate(portfolio)