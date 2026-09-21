from fastapi import APIRouter, HTTPException
from app.services.explain_service import get_explanation
from app.services.market_data import get_available_symbols

router = APIRouter()

@router.get("/explain/{symbol}")
def explain(symbol: str):
    symbol = symbol.upper()
    available = get_available_symbols()
    if symbol not in available:
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found")

    result = get_explanation(symbol)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No trained model found for '{symbol}'")

    return result