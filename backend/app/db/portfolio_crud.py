from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.sql_models import Portfolio, Asset
from app.models.schemas import PortfolioCreate
from app.dependencies.user import get_current_user  # Assuming this dependency exists
from app.db.session import get_db


async def get_all_portfolios(db: AsyncSession = None):
    if db is None:
        raise HTTPException(
            status_code=400,
            detail="Error in portfolio_crud.py/get_all_portfolios: db is None",
        )
    result = await db.execute(select(Portfolio).options(selectinload(Portfolio.assets)))
    return result.scalars().all()


async def get_user_portfolios(
    db: AsyncSession = None, user_id: int = Depends(get_current_user)
):
    if db is None:
        raise HTTPException(
            status_code=400,
            detail="Error in portfolio_crud.py/get_user_portfolios: db is None",
        )
    result = await db.execute(
        select(Portfolio)
        .options(selectinload(Portfolio.assets))
        .where(Portfolio.user_id == user_id)
    )
    return result.scalars().all()


async def create_portfolio(
    db: AsyncSession = None,
    data: PortfolioCreate = None,
    user_id: int = Depends(get_current_user),
):
    if db is None:
        raise HTTPException(
            status_code=400,
            detail="Error in portfolio_crud.py/create_portfolio: db is None",
        )
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
    db: AsyncSession = None, id: int = None, user_id: int = Depends(get_current_user)
):
    if db is None:
        raise HTTPException(
            status_code=400,
            detail="Error in portfolio_crud.py/get_portfolio_by_id: db is None",
        )
    if id is None:
        raise HTTPException(status_code=400, detail="Portfolio ID is required")
    result = await db.execute(
        select(Portfolio)
        .options(selectinload(Portfolio.assets))
        .where(Portfolio.id == id, Portfolio.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def delete_portfolio(
    db: AsyncSession = None,
    portfolio_id: int = None,
    user_id: int = Depends(get_current_user),
):
    if db is None:
        raise HTTPException(
            status_code=400,
            detail="Error in portfolio_crud.py/delete_portfolio: db is None",
        )
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
    db: AsyncSession = None,
    portfolio_id: int = None,
    data: PortfolioCreate = None,
    user_id: int = Depends(get_current_user),
):
    if db is None:
        raise HTTPException(
            status_code=400,
            detail="Error in portfolio_crud.py/update_portfolio: db is None",
        )
    if not portfolio_id or not data:
        raise HTTPException(
            status_code=400, detail="Portfolio ID and data are required"
        )

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
    current_assets = {(a.ticker, a.asset_type): a for a in portfolio.assets}
    new_assets_dict = {(a.ticker, a.asset_type): a for a in data.assets}

    current_keys = set(current_assets.keys())
    new_keys = set(new_assets_dict.keys())

    # Calculate sets for update, add, delete
    assets_to_update = current_keys & new_keys
    assets_to_add = new_keys - current_keys

    # Update existing assets
    for key in assets_to_update:
        existing_asset = current_assets[key]
        new_data = new_assets_dict[key].model_dump()
        # (Optional: Only update fields that changed)
        for attr, value in new_data.items():
            setattr(existing_asset, attr, value)

    # Add new assets
    for key in assets_to_add:
        new_asset_data = new_assets_dict[key].model_dump()
        asset = Asset(**new_asset_data, portfolio_id=portfolio_id)
        db.add(asset)

    await db.commit()
    await db.refresh(portfolio, attribute_names=["assets"])
    return portfolio
