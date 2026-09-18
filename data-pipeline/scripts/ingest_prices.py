import yfinance as yf
import pandas as pd
from pathlib import Path
from datetime import datetime

# --- Config ---
TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]  # Add/remove as you like
PERIOD = "2y"
INTERVAL = "1d"

# --- Paths ---
RAW_DATA_DIR = Path(__file__).resolve().parent.parent / "raw_data"
RAW_DATA_DIR.mkdir(exist_ok=True)

def fetch_price_data(ticker: str, period: str, interval: str) -> pd.DataFrame:
    print(f"Fetching {ticker}...")
    stock = yf.Ticker(ticker)
    df = stock.history(period=period, interval=interval)

    if df.empty:
        print(f"  WARNING: No data returned for '{ticker}'. Skipping.")
        return None

    df.reset_index(inplace=True)
    df["symbol"] = ticker
    return df

def save_to_csv(df: pd.DataFrame, ticker: str):
    filename = f"{ticker}_{datetime.now().strftime('%Y%m%d')}.csv"
    filepath = RAW_DATA_DIR / filename
    df.to_csv(filepath, index=False)
    print(f"  Saved {len(df)} rows to {filepath.name}")

if __name__ == "__main__":
    all_data = []
    for ticker in TICKERS:
        df = fetch_price_data(ticker, PERIOD, INTERVAL)
        if df is not None:
            save_to_csv(df, ticker)
            all_data.append(df)

    # Also save one combined file with all tickers
    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        combined_path = RAW_DATA_DIR / f"combined_{datetime.now().strftime('%Y%m%d')}.csv"
        combined.to_csv(combined_path, index=False)
        print(f"\nCombined dataset: {len(combined)} total rows across {len(TICKERS)} tickers")
        print(f"Saved to {combined_path.name}")