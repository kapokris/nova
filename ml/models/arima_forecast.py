import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy import create_engine
from statsmodels.tsa.stattools import adfuller
import pmdarima as pm
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt

DATABASE_URL = "postgresql://nova_user:nova_pass@localhost:5432/nova_db"
TEST_SIZE = 30  # Hold out last 30 days for testing

def load_data(ticker: str) -> pd.DataFrame:
    engine = create_engine(DATABASE_URL)
    df = pd.read_sql(
        f"SELECT date, close FROM market_prices WHERE symbol = '{ticker}' ORDER BY date",
        engine
    )
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    print(f"Loaded {len(df)} rows for {ticker}")
    return df

def check_stationarity(series: pd.Series, label: str):
    result = adfuller(series.dropna())
    print(f"\n--- ADF Test: {label} ---")
    print(f"ADF Statistic: {result[0]:.4f}, p-value: {result[1]:.4f}")
    print("=> Stationary" if result[1] <= 0.05 else "=> Non-stationary")

def train_test_split(df: pd.DataFrame, test_size: int):
    train = df.iloc[:-test_size]
    test = df.iloc[-test_size:]
    print(f"\nTrain: {len(train)} rows ({train.index.min().date()} to {train.index.max().date()})")
    print(f"Test:  {len(test)} rows ({test.index.min().date()} to {test.index.max().date()})")
    return train, test

def fit_auto_arima(train_series: pd.Series):
    print("\nSearching for best ARIMA parameters...")
    train_values = train_series.reset_index(drop=True)
    model = pm.auto_arima(
        train_values,
        start_p=0, start_q=0,
        max_p=5, max_q=5,
        d=None,
        seasonal=False,
        trace=True,
        error_action='ignore',
        suppress_warnings=True,
        stepwise=True
    )
    print(f"\nBest model: ARIMA{model.order}")
    return model

def evaluate_forecast(actual, predicted):
    mae = mean_absolute_error(actual, predicted)
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    mape = np.mean(np.abs((actual - predicted) / actual)) * 100
    print(f"\n--- Forecast Evaluation ---")
    print(f"MAE:  {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")
    print(f"MAPE: {mape:.2f}%")
    return {"mae": mae, "rmse": rmse, "mape": mape}

def plot_forecast(train, test, forecast, ticker):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(train.index, train['close'], label='Train', color='black')
    ax.plot(test.index, test['close'], label='Actual (Test)', color='blue')
    ax.plot(test.index, forecast, label='ARIMA Forecast', color='red', linestyle='--')
    ax.set_title(f'{ticker} — ARIMA Forecast vs Actual')
    ax.legend()
    plt.tight_layout()
    save_path = Path(__file__).parent / f"arima_{ticker}_forecast.png"
    plt.savefig(save_path)
    print(f"\nForecast chart saved to {save_path}")

if __name__ == "__main__":
    TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    all_metrics = {}

    for ticker in TICKERS:
        print(f"\n{'='*50}")
        print(f"Processing {ticker}")
        print('='*50)

        df = load_data(ticker)
        check_stationarity(df['close'], f"{ticker} Raw Close Price")

        train, test = train_test_split(df, TEST_SIZE)
        model = fit_auto_arima(train['close'])
        forecast, conf_int = model.predict(n_periods=TEST_SIZE, return_conf_int=True)
        metrics = evaluate_forecast(test['close'].values, forecast)
        plot_forecast(train, test, forecast, ticker)

        all_metrics[ticker] = metrics

    print(f"\n{'='*50}")
    print("SUMMARY — ARIMA Performance Across All Tickers")
    print('='*50)
    summary_df = pd.DataFrame(all_metrics).T
    print(summary_df.round(2))
    summary_df.to_csv(Path(__file__).parent / "arima_summary.csv")