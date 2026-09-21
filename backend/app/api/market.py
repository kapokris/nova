from fastapi import APIRouter, HTTPException
from app.services.market_data import get_available_symbols, get_price_history, get_latest_price

router = APIRouter()

@router.get("/assets")
def list_assets():
    symbols = get_available_symbols()
    return {"symbols": symbols}

@router.get("/market-data/{symbol}")
def market_data(symbol: str, limit: int = 100):
    symbol = symbol.upper()
    available = get_available_symbols()
    if symbol not in available:
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found")

    history = get_price_history(symbol, limit)
    latest = get_latest_price(symbol)
    return {
        "symbol": symbol,
        "latest": latest,
        "history": history
    }