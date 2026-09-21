import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy import create_engine
import xgboost as xgb
import shap
import matplotlib.pyplot as plt

DATABASE_URL = "postgresql://nova_user:nova_pass@localhost:5432/nova_db"
TEST_SIZE = 30
TICKER = "TSLA"  # Most volatile ticker — most interesting to explain

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

if __name__ == "__main__":
    df = load_and_engineer_features(TICKER)
    train, test = chronological_split(df, TEST_SIZE)

    model = train_xgboost(train)

    print(f"Computing SHAP values for {TICKER}...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(test[FEATURE_COLS])

    plt.figure()
    shap.summary_plot(shap_values, test[FEATURE_COLS], show=False)
    plt.tight_layout()
    save_path = Path(__file__).parent / f"shap_summary_{TICKER}.png"
    plt.savefig(save_path, bbox_inches='tight')
    print(f"Summary plot saved to {save_path}")
    plt.close()

    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    importance_df = pd.DataFrame({
        'feature': FEATURE_COLS,
        'mean_abs_shap': mean_abs_shap
    }).sort_values('mean_abs_shap', ascending=False)

    print(f"\n--- Feature Importance (by mean |SHAP value|) ---")
    print(importance_df.to_string(index=False))
    importance_df.to_csv(Path(__file__).parent / f"shap_importance_{TICKER}.csv", index=False)

    last_idx = len(test) - 1
    print(f"\n--- Explaining prediction for {test.iloc[last_idx]['date'].date()} ---")
    print(f"Predicted next-day close: {model.predict(test[FEATURE_COLS].iloc[[last_idx]])[0]:.2f}")
    print(f"Actual next-day close:    {test.iloc[last_idx]['target']:.2f}")

    single_shap = pd.DataFrame({
        'feature': FEATURE_COLS,
        'shap_value': shap_values[last_idx]
    }).sort_values('shap_value', key=abs, ascending=False)
    print("\nTop feature contributions to this prediction:")
    print(single_shap.head(8).to_string(index=False))