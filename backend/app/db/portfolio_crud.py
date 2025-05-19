from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import delete as sa_delete
from app.models.sql_models import Portfolio, Asset
from app.models.schemas import PortfolioCreate


async def get_all_portfolios(db: AsyncSession):
    result = await db.execute(select(Portfolio).options(selectinload(Portfolio.assets)))

    return result.scalars().all()


async def get_user_portfolios(user_id: int, db: AsyncSession):
    result = await db.execute(
        select(Portfolio)
        .options(selectinload(Portfolio.assets))
        .where(Portfolio.user_id == user_id)
    )
    return result.scalars().all()


async def create_portfolio(db: AsyncSession, data: PortfolioCreate, user_id: int):
    portfolio = Portfolio(name=data.name, user_id=user_id)
    db.add(portfolio)
    await db.flush()

    for a in data.assets:
        asset = Asset(**a.model_dump(), portfolio_id=portfolio.id)
        db.add(asset)

    await db.commit()
    await db.refresh(portfolio, attribute_names=["assets"])
    return portfolio


async def get_portfolio_by_id(db: AsyncSession, id: int, user_id: int):

    result = await db.execute(
        select(Portfolio)
        .options(selectinload(Portfolio.assets))
        .where(Portfolio.id == id, Portfolio.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def delete_portfolio(db: AsyncSession, portfolio_id: int, user_id: int):
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
    db: AsyncSession, portfolio_id: int, data: PortfolioCreate, user_id: int
):
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
