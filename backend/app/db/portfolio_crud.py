from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.sql_models import Portfolio, Asset
from app.models.schemas import PortfolioCreate
from app.dependencies.user import get_current_user  # Assuming this dependency exists
from app.db.session import get_db


async def get_all_portfolios(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Portfolio).options(selectinload(Portfolio.assets)))
    return result.scalars().all()


async def get_user_portfolios(db: AsyncSession = Depends(get_db), user_id: int = Depends(get_current_user)):
    result = await db.execute(
        select(Portfolio)
        .options(selectinload(Portfolio.assets))
        .where(Portfolio.user_id == user_id)
    )
    return result.scalars().all()


async def create_portfolio(
    db: AsyncSession = Depends(get_db), data: PortfolioCreate = None, user_id: int = Depends(get_current_user)
):
    if data is None:
        raise HTTPException(status_code=400, detail="Portfolio data is required")
    
    portfolio = Portfolio(name=data.name, user_id=user_id)
    db.add(portfolio)
    await db.flush()

    for a in data.assets:
        asset = Asset(**a.model_dump(), portfolio_id=portfolio.id)
        db.add(asset)

    await db.commit()
    await db.refresh(portfolio, attribute_names=["assets"])
    return portfolio


async def get_portfolio_by_id(
    db: AsyncSession = Depends(get_db), id: int = None, user_id: int = Depends(get_current_user)
):
    if id is None:
        raise HTTPException(status_code=400, detail="Portfolio ID is required")
    result = await db.execute(
        select(Portfolio)
        .options(selectinload(Portfolio.assets))
        .where(Portfolio.id == id, Portfolio.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def delete_portfolio(
    db: AsyncSession = Depends(get_db), portfolio_id: int = None, user_id: int = Depends(get_current_user)
):
    if portfolio_id is None:
        raise HTTPException(status_code=400, detail="Portfolio ID is required")
    result = await db.execute(
        select(Portfolio).where(
            Portfolio.id == portfolio_id, Portfolio.user_id == user_id
        )
    )
    portfolio = result.scalar_one_or_none()
    if portfolio:
        await db.delete(portfolio)
        await db.commit()
        return True
    return False


async def update_portfolio(
    db: AsyncSession = Depends(get_db),
    portfolio_id: int = None,
    data: PortfolioCreate = None,
    user_id: int = Depends(get_current_user),
):
    if not portfolio_id or not data:
        raise HTTPException(status_code=400, detail="Portfolio ID and data are required")
    
    result = await db.execute(
        select(Portfolio)
        .options(selectinload(Portfolio.assets))
        .where(Portfolio.id == portfolio_id, Portfolio.user_id == user_id)
    )

    portfolio = result.scalar_one_or_none()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    portfolio.name = data.name

    # Load current assets
    current_assets = {a.ticker: a for a in portfolio.assets}

    for new in data.assets:
        new_data = new.model_dump()
        ticker = new_data["ticker"]

        if ticker in current_assets:

            asset = current_assets[ticker]
            for key, value in new_data.items():
                setattr(asset, key, value)
        else:
            asset = Asset(**new_data, portfolio_id=portfolio_id)
            db.add(asset)

    await db.commit()
    await db.refresh(portfolio, attribute_names=["assets"])
    return portfolio
