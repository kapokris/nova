from fastapi import APIRouter, HTTPException
from app.services.risk_service import get_risk_metrics
from app.services.market_data import get_available_symbols

router = APIRouter()

@router.get("/risk/{symbol}")
def risk(symbol: str):
    symbol = symbol.upper()
    available = get_available_symbols()
    if symbol not in available:
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found")

    result = get_risk_metrics(symbol)
    return result