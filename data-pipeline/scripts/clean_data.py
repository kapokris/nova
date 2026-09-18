import pandas as pd
from pathlib import Path
from datetime import datetime

RAW_DATA_DIR = Path(__file__).resolve().parent.parent / "raw_data"
PROCESSED_DIR = Path(__file__).resolve().parent.parent / "processed_data"
PROCESSED_DIR.mkdir(exist_ok=True)

def find_latest_combined_file() -> Path:
    files = sorted(RAW_DATA_DIR.glob("combined_*.csv"))
    if not files:
        raise FileNotFoundError("No combined_*.csv file found. Run ingest_prices.py first.")
    return files[-1]

def load_data(filepath: Path) -> pd.DataFrame:
    df = pd.read_csv(filepath, parse_dates=["Date"])
    print(f"Loaded {len(df)} rows from {filepath.name}")
    return df

def check_data_quality(df: pd.DataFrame):
    print("\n--- Data Quality Report ---")
    print(f"Total rows: {len(df)}")
    print(f"Tickers: {df['symbol'].unique().tolist()}")
    print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")

    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if len(missing) > 0:
        print(f"\nMissing values found:\n{missing}")
    else:
        print("\nNo missing values.")

    duplicates = df.duplicated(subset=["Date", "symbol"]).sum()
    print(f"Duplicate (Date, symbol) rows: {duplicates}")

    # Check for impossible price values
    invalid_prices = df[(df["Open"] <= 0) | (df["High"] <= 0) | (df["Low"] <= 0) | (df["Close"] <= 0)]
    print(f"Rows with zero/negative prices: {len(invalid_prices)}")

    # Check High >= Low sanity
    bad_hl = df[df["High"] < df["Low"]]
    print(f"Rows where High < Low (impossible): {len(bad_hl)}")

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)

    # Drop exact duplicates
    df = df.drop_duplicates(subset=["Date", "symbol"])

    # Drop rows with missing critical fields
    df = df.dropna(subset=["Open", "High", "Low", "Close", "Volume"])

    # Drop impossible prices
    df = df[(df["Open"] > 0) & (df["High"] > 0) & (df["Low"] > 0) & (df["Close"] > 0)]
    df = df[df["High"] >= df["Low"]]

    # Sort chronologically per ticker
    df = df.sort_values(["symbol", "Date"]).reset_index(drop=True)

    after = len(df)
    print(f"\nCleaned: {before} -> {after} rows ({before - after} removed)")
    return df

def save_cleaned(df: pd.DataFrame):
    filename = f"cleaned_prices_{datetime.now().strftime('%Y%m%d')}.csv"
    filepath = PROCESSED_DIR / filename
    df.to_csv(filepath, index=False)
    print(f"Saved cleaned dataset to {filepath}")

if __name__ == "__main__":
    latest_file = find_latest_combined_file()
    df = load_data(latest_file)
    check_data_quality(df)
    df_clean = clean_data(df)
    save_cleaned(df_clean)