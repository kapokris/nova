from fastapi import APIRouter, HTTPException
from app.services.sentiment_service import get_sentiment
from app.services.market_data import get_available_symbols

router = APIRouter()

@router.get("/sentiment/{symbol}")
def sentiment(symbol: str):
    symbol = symbol.upper()
    available = get_available_symbols()
    if symbol not in available:
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found")

    result = get_sentiment(symbol)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No sentiment data found for '{symbol}'")

    return result