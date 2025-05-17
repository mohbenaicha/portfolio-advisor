from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.portfolio_crud import (
    get_all_portfolios,
    create_portfolio,
    delete_portfolio,
    update_portfolio,
    get_portfolio_by_id
)
from app.models.schemas import PortfolioCreate, PortfolioOut
from app.db.session import get_db

router = APIRouter()


@router.get("/portfolios", response_model=list[PortfolioOut])
async def list_portfolios(db: AsyncSession = Depends(get_db)):
    portfolios = await get_all_portfolios(db)
    return [PortfolioOut.model_validate(p) for p in portfolios]


@router.post("/portfolios", response_model=PortfolioOut)
async def add_portfolio(portfolio: PortfolioCreate, db: AsyncSession = Depends(get_db)):
    created = await create_portfolio(db, portfolio)
    return PortfolioOut.model_validate(created)


@router.delete("/portfolios/{id}")
async def remove_portfolio(id: int, db: AsyncSession = Depends(get_db)):
    deleted = await delete_portfolio(db, id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return {"deleted": True}


@router.put("/portfolios/{id}", response_model=PortfolioOut)
async def update_portfolio_route(
    id: int, portfolio: PortfolioCreate, db: AsyncSession = Depends(get_db)
):
    updated = await update_portfolio(db, id, portfolio)
    return PortfolioOut.model_validate(updated)


@router.get("/portfolios/{id}", response_model=PortfolioOut)
async def get_portfolio(id: int, db: AsyncSession = Depends(get_db)):
    portfolio = await get_portfolio_by_id(db, id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return PortfolioOut.model_validate(portfolio)

