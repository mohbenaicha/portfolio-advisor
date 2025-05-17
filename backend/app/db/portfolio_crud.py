from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import delete as sa_delete
from app.models.sql_models import Portfolio, Asset
from app.models.schemas import PortfolioCreate


async def get_all_portfolios(db: AsyncSession):
    result = await db.execute(select(Portfolio).options(selectinload(Portfolio.assets)))

    return result.scalars().all()


async def create_portfolio(db: AsyncSession, data: PortfolioCreate):
    portfolio = Portfolio(name=data.name)
    db.add(portfolio)
    await db.flush()

    for a in data.assets:
        asset = Asset(**a.model_dump(), portfolio_id=portfolio.id)
        db.add(asset)

    await db.commit()
    await db.refresh(portfolio, attribute_names=["assets"])
    return portfolio

async def get_portfolio_by_id(db: AsyncSession, portfolio_id: int):
    result = await db.execute(
        select(Portfolio).options(selectinload(Portfolio.assets)).filter(Portfolio.id == portfolio_id)
    )
    return result.scalar_one_or_none()

async def delete_portfolio(db: AsyncSession, portfolio_id: int):
    result = await db.execute(select(Portfolio).filter(Portfolio.id == portfolio_id))
    portfolio = result.scalar_one_or_none()
    if portfolio:
        await db.delete(portfolio)
        await db.commit()
        return True
    return False


async def update_portfolio(db: AsyncSession, portfolio_id: int, data: PortfolioCreate):
    result = await db.execute(select(Portfolio).filter(Portfolio.id == portfolio_id))
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        raise ValueError("Portfolio not found")

    portfolio.name = data.name
    await db.execute(sa_delete(Asset).where(Asset.portfolio_id == portfolio_id))
    for a in data.assets:
        asset = Asset(**a.dict(), portfolio_id=portfolio_id)
        db.add(asset)

    await db.commit()
    await db.refresh(portfolio, attribute_names=["assets"])
    return portfolio
