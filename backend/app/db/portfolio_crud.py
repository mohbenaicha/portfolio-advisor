from sqlalchemy.orm import Session
from app.models.sql_models import Portfolio, Asset
from app.models.schemas import PortfolioCreate

def get_all_portfolios(db: Session):
    return db.query(Portfolio).all()

def create_portfolio(db: Session, data: PortfolioCreate):
    portfolio = Portfolio(name=data.name)
    db.add(portfolio)
    db.flush()

    for a in data.assets:
        asset = Asset(**a.dict(), portfolio_id=portfolio.id)
        db.add(asset)

    db.commit()
    db.refresh(portfolio)
    return portfolio

def delete_portfolio(db: Session, portfolio_id: int):
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if portfolio:
        db.delete(portfolio)
        db.commit()
        return True
    return False
