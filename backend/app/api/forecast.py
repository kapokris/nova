from fastapi import APIRouter, HTTPException
from app.services.forecast_service import get_forecast
from app.services.market_data import get_available_symbols

router = APIRouter()

@router.get("/forecast/{symbol}")
def forecast(symbol: str):
    symbol = symbol.upper()
    available = get_available_symbols()
    if symbol not in available:
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found")

    result = get_forecast(symbol)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No trained model found for '{symbol}'")

    return result