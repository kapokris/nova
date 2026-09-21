import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from app.services.market_data import get_engine

MODEL_DIR = Path(__file__).resolve().parent.parent.parent.parent / "ml" / "saved_models"

FEATURE_COLS = [
    'daily_return', 'return_7d', 'return_14d',
    'ma_7', 'ma_30', 'ema_12', 'ema_26',
    'volatility_14', 'rsi_14', 'macd', 'macd_signal',
    'bb_upper', 'bb_lower', 'bb_middle',
    'close_lag_1', 'close_lag_2', 'close_lag_3', 'close_lag_5',
    'volume'
]

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values('date').reset_index(drop=True)

    df['daily_return'] = df['close'].pct_change()
    df['return_7d'] = df['close'].pct_change(periods=7)
    df['return_14d'] = df['close'].pct_change(periods=14)
    df['ma_7'] = df['close'].rolling(window=7).mean()
    df['ma_30'] = df['close'].rolling(window=30).mean()
    df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
    df['volatility_14'] = df['daily_return'].rolling(window=14).std()

    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df['rsi_14'] = 100 - (100 / (1 + rs))

    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()

    rolling_mean = df['close'].rolling(window=20).mean()
    rolling_std = df['close'].rolling(window=20).std()
    df['bb_upper'] = rolling_mean + (rolling_std * 2)
    df['bb_lower'] = rolling_mean - (rolling_std * 2)
    df['bb_middle'] = rolling_mean

    for lag in [1, 2, 3, 5]:
        df[f'close_lag_{lag}'] = df['close'].shift(lag)

    return df

def load_model(symbol: str):
    model_path = MODEL_DIR / f"xgboost_{symbol}.joblib"
    if not model_path.exists():
        return None
    return joblib.load(model_path)

def get_forecast(symbol: str):
    model = load_model(symbol)
    if model is None:
        return None

    engine = get_engine()
    df = pd.read_sql(
        f"SELECT * FROM market_prices WHERE symbol = '{symbol}' ORDER BY date",
        engine
    )
    df['date'] = pd.to_datetime(df['date'])
    df = engineer_features(df)
    df = df.dropna().reset_index(drop=True)

    latest_row = df.iloc[[-1]][FEATURE_COLS]
    predicted_close = float(model.predict(latest_row)[0])
    current_close = float(df.iloc[-1]['close'])
    latest_date = str(df.iloc[-1]['date'].date())

    change = predicted_close - current_close
    change_pct = (change / current_close) * 100

    return {
        "symbol": symbol,
        "as_of_date": latest_date,
        "current_close": round(current_close, 2),
        "predicted_next_close": round(predicted_close, 2),
        "predicted_change": round(change, 2),
        "predicted_change_pct": round(change_pct, 2)
    }