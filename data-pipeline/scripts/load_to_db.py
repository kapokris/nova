import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Load DATABASE_URL from backend/.env
load_dotenv(Path(__file__).resolve().parent.parent.parent / "backend" / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found. Check backend/.env exists and is correct.")

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "processed_data"

def find_latest_cleaned_file() -> Path:
    files = sorted(PROCESSED_DIR.glob("cleaned_prices_*.csv"))
    if not files:
        raise FileNotFoundError("No cleaned_prices_*.csv found. Run clean_data.py first.")
    return files[-1]

def create_table(engine):
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS market_prices (
                id SERIAL PRIMARY KEY,
                date TIMESTAMP NOT NULL,
                open NUMERIC,
                high NUMERIC,
                low NUMERIC,
                close NUMERIC,
                volume BIGINT,
                dividends NUMERIC,
                stock_splits NUMERIC,
                symbol VARCHAR(10) NOT NULL,
                UNIQUE(date, symbol)
            );
        """))
        conn.commit()
    print("Table 'market_prices' ready.")

def load_data(engine, df: pd.DataFrame):
    df = df.rename(columns={
        "Date": "date",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
        "Dividends": "dividends",
        "Stock Splits": "stock_splits",
        "symbol": "symbol"
    })

    with engine.connect() as conn:
        for _, row in df.iterrows():
            conn.execute(text("""
                INSERT INTO market_prices (date, open, high, low, close, volume, dividends, stock_splits, symbol)
                VALUES (:date, :open, :high, :low, :close, :volume, :dividends, :stock_splits, :symbol)
                ON CONFLICT (date, symbol) DO UPDATE SET
                    open = EXCLUDED.open,
                    high = EXCLUDED.high,
                    low = EXCLUDED.low,
                    close = EXCLUDED.close,
                    volume = EXCLUDED.volume
            """), {
                "date": row["date"],
                "open": row["open"],
                "high": row["high"],
                "low": row["low"],
                "close": row["close"],
                "volume": int(row["volume"]),
                "dividends": row["dividends"],
                "stock_splits": row["stock_splits"],
                "symbol": row["symbol"]
            })
        conn.commit()
    print(f"Loaded {len(df)} rows into market_prices.")

if __name__ == "__main__":
    engine = create_engine(DATABASE_URL)
    create_table(engine)

    latest_file = find_latest_cleaned_file()
    df = pd.read_csv(latest_file, parse_dates=["Date"])
    print(f"Loading {latest_file.name} into database...")

    load_data(engine, df)