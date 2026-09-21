import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy import create_engine
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt

DATABASE_URL = "postgresql://nova_user:nova_pass@localhost:5432/nova_db"
TEST_SIZE = 30

FEATURE_COLS = [
    'daily_return', 'return_7d', 'return_14d',
    'ma_7', 'ma_30', 'ema_12', 'ema_26',
    'volatility_14', 'rsi_14', 'macd', 'macd_signal',
    'bb_upper', 'bb_lower', 'bb_middle',
    'close_lag_1', 'close_lag_2', 'close_lag_3', 'close_lag_5',
    'volume'
]

def load_and_engineer_features(ticker: str) -> pd.DataFrame:
    engine = create_engine(DATABASE_URL)
    df = pd.read_sql(
        f"SELECT * FROM market_prices WHERE symbol = '{ticker}' ORDER BY date",
        engine
    )
    df['date'] = pd.to_datetime(df['date'])
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

    df['target'] = df['close'].shift(-1)

    df = df.dropna().reset_index(drop=True)
    return df

def chronological_split(df: pd.DataFrame, test_size: int):
    train = df.iloc[:-test_size]
    test = df.iloc[-test_size:]
    return train, test

def train_xgboost(train: pd.DataFrame):
    X_train = train[FEATURE_COLS]
    y_train = train['target']

    model = xgb.XGBRegressor(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )
    model.fit(X_train, y_train)
    return model

def evaluate_forecast(actual, predicted, label=""):
    mae = mean_absolute_error(actual, predicted)
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    mape = np.mean(np.abs((actual - predicted) / actual)) * 100
    print(f"\n--- {label} Forecast Evaluation ---")
    print(f"MAE:  {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")
    print(f"MAPE: {mape:.2f}%")
    return {"mae": mae, "rmse": rmse, "mape": mape}

def plot_forecast(test, predictions, ticker):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(test['date'], test['target'], label='Actual', color='blue')
    ax.plot(test['date'], predictions, label='XGBoost Forecast', color='green', linestyle='--')
    ax.set_title(f'{ticker} — XGBoost Forecast vs Actual')
    ax.legend()
    plt.tight_layout()
    save_path = Path(__file__).parent / f"xgboost_{ticker}_forecast.png"
    plt.savefig(save_path)
    print(f"Chart saved to {save_path}")

if __name__ == "__main__":
    TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    all_metrics = {}

    for ticker in TICKERS:
        print(f"\n{'='*50}")
        print(f"Processing {ticker}")
        print('='*50)

        df = load_and_engineer_features(ticker)
        train, test = chronological_split(df, TEST_SIZE)
        print(f"Train: {len(train)} rows, Test: {len(test)} rows")

        model = train_xgboost(train)
        predictions = model.predict(test[FEATURE_COLS])

        metrics = evaluate_forecast(test['target'].values, predictions, ticker)
        plot_forecast(test, predictions, ticker)

        all_metrics[ticker] = metrics

    print(f"\n{'='*50}")
    print("SUMMARY — XGBoost Performance Across All Tickers")
    print('='*50)
    summary_df = pd.DataFrame(all_metrics).T
    print(summary_df.round(2))
    summary_df.to_csv(Path(__file__).parent / "xgboost_summary.csv")