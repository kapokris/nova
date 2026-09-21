import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy import create_engine
from datetime import datetime

DATABASE_URL = "postgresql://nova_user:nova_pass@localhost:5432/nova_db"
PROCESSED_DIR = Path(__file__).resolve().parent.parent / "processed_data"

def load_from_db():
    engine = create_engine(DATABASE_URL)
    df = pd.read_sql("SELECT * FROM market_prices ORDER BY symbol, date", engine)
    df['date'] = pd.to_datetime(df['date'])
    print(f"Loaded {len(df)} rows from database")
    return df

def add_return_features(df):
    df = df.sort_values(['symbol', 'date'])
    df['daily_return'] = df.groupby('symbol')['close'].pct_change()
    df['return_7d'] = df.groupby('symbol')['close'].pct_change(periods=7)
    df['return_14d'] = df.groupby('symbol')['close'].pct_change(periods=14)
    return df

def add_moving_averages(df):
    df['ma_7'] = df.groupby('symbol')['close'].transform(lambda x: x.rolling(window=7).mean())
    df['ma_30'] = df.groupby('symbol')['close'].transform(lambda x: x.rolling(window=30).mean())
    df['ema_12'] = df.groupby('symbol')['close'].transform(lambda x: x.ewm(span=12, adjust=False).mean())
    df['ema_26'] = df.groupby('symbol')['close'].transform(lambda x: x.ewm(span=26, adjust=False).mean())
    return df

def add_volatility(df):
    df['volatility_14'] = df.groupby('symbol')['daily_return'].transform(lambda x: x.rolling(window=14).std())
    return df

def add_rsi(df, period=14):
    def compute_rsi(close):
        delta = close.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    df['rsi_14'] = df.groupby('symbol')['close'].transform(compute_rsi)
    return df

def add_macd(df):
    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df.groupby('symbol')['macd'].transform(lambda x: x.ewm(span=9, adjust=False).mean())
    return df

def add_bollinger_bands(df, window=20):
    rolling_mean = df.groupby('symbol')['close'].transform(lambda x: x.rolling(window=window).mean())
    rolling_std = df.groupby('symbol')['close'].transform(lambda x: x.rolling(window=window).std())
    df['bb_upper'] = rolling_mean + (rolling_std * 2)
    df['bb_lower'] = rolling_mean - (rolling_std * 2)
    df['bb_middle'] = rolling_mean
    return df

def add_lag_features(df, lags=[1, 2, 3, 5]):
    for lag in lags:
        df[f'close_lag_{lag}'] = df.groupby('symbol')['close'].shift(lag)
    return df

def save_features(df):
    filename = f"features_{datetime.now().strftime('%Y%m%d')}.csv"
    filepath = PROCESSED_DIR / filename
    df.to_csv(filepath, index=False)
    print(f"Saved {len(df)} rows with {len(df.columns)} columns to {filepath.name}")

if __name__ == "__main__":
    df = load_from_db()
    df = add_return_features(df)
    df = add_moving_averages(df)
    df = add_volatility(df)
    df = add_rsi(df)
    df = add_macd(df)
    df = add_bollinger_bands(df)
    df = add_lag_features(df)

    print(f"\nFinal dataset: {len(df)} rows, {len(df.columns)} columns")
    print(f"Columns: {list(df.columns)}")
    print(f"\nNaN counts (expected in early rows due to rolling windows):")
    print(df.isnull().sum()[df.isnull().sum() > 0])

    save_features(df)