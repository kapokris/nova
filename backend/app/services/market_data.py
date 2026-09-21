import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")
DATABASE_URL = os.getenv("DATABASE_URL")

def get_engine():
    return create_engine(DATABASE_URL)

def get_available_symbols():
    engine = get_engine()
    df = pd.read_sql("SELECT DISTINCT symbol FROM market_prices ORDER BY symbol", engine)
    return df['symbol'].tolist()

def get_price_history(symbol: str, limit: int = 100):
    engine = get_engine()
    df = pd.read_sql(
        f"SELECT date, open, high, low, close, volume FROM market_prices "
        f"WHERE symbol = '{symbol}' ORDER BY date DESC LIMIT {limit}",
        engine
    )
    df = df.sort_values('date')
    df['date'] = df['date'].astype(str)
    return df.to_dict(orient='records')

def get_latest_price(symbol: str):
    engine = get_engine()
    df = pd.read_sql(
        f"SELECT date, close, volume FROM market_prices "
        f"WHERE symbol = '{symbol}' ORDER BY date DESC LIMIT 2",
        engine
    )
    if len(df) < 2:
        return None
    latest = df.iloc[0]
    previous = df.iloc[1]
    change = latest['close'] - previous['close']
    change_pct = (change / previous['close']) * 100
    return {
        "symbol": symbol,
        "date": str(latest['date']),
        "close": float(latest['close']),
        "volume": int(latest['volume']),
        "change": float(change),
        "change_pct": float(change_pct)
    }