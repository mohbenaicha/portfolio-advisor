from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.portfolio_crud import get_all_portfolios, create_portfolio, delete_portfolio
from app.models.schemas import PortfolioCreate, PortfolioOut
from app.db.session import get_db

router = APIRouter()

@router.get("/portfolios", response_model=list[PortfolioOut])
def list_portfolios(db: Session = Depends(get_db)):
    return get_all_portfolios(db)

@router.post("/portfolios", response_model=PortfolioOut)
def add_portfolio(portfolio: PortfolioCreate, db: Session = Depends(get_db)):
    return create_portfolio(db, portfolio)

@router.delete("/portfolios/{id}")
def remove_portfolio(id: int, db: Session = Depends(get_db)):
    deleted = delete_portfolio(db, id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return {"deleted": True}
