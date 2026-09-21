import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy import create_engine
import matplotlib.pyplot as plt

DATABASE_URL = "postgresql://nova_user:nova_pass@localhost:5432/nova_db"
RISK_FREE_RATE = 0.045  # ~4.5% annualized, roughly current T-bill rate — adjust as needed

def load_data(ticker: str) -> pd.DataFrame:
    engine = create_engine(DATABASE_URL)
    df = pd.read_sql(
        f"SELECT date, close FROM market_prices WHERE symbol = '{ticker}' ORDER BY date",
        engine
    )
    df['date'] = pd.to_datetime(df['date'])
    df['daily_return'] = df['close'].pct_change()
    return df.dropna()

def calculate_volatility(returns: pd.Series):
    daily_vol = returns.std()
    annualized_vol = daily_vol * np.sqrt(252)
    return daily_vol, annualized_vol

def calculate_max_drawdown(prices: pd.Series):
    cumulative_max = prices.cummax()
    drawdown = (prices - cumulative_max) / cumulative_max
    max_drawdown = drawdown.min()
    return max_drawdown, drawdown

def calculate_var(returns: pd.Series, confidence: float = 0.95):
    """Historical VaR: the loss threshold not exceeded (confidence)% of the time."""
    var = np.percentile(returns, (1 - confidence) * 100)
    return var

def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float):
    daily_rf = risk_free_rate / 252
    excess_returns = returns - daily_rf
    sharpe = (excess_returns.mean() / returns.std()) * np.sqrt(252)
    return sharpe

def analyze_ticker(ticker: str):
    df = load_data(ticker)

    daily_vol, annual_vol = calculate_volatility(df['daily_return'])
    max_dd, drawdown_series = calculate_max_drawdown(df['close'])
    var_95 = calculate_var(df['daily_return'], confidence=0.95)
    var_99 = calculate_var(df['daily_return'], confidence=0.99)
    sharpe = calculate_sharpe_ratio(df['daily_return'], RISK_FREE_RATE)

    return {
        "daily_volatility": daily_vol,
        "annualized_volatility": annual_vol,
        "max_drawdown": max_dd,
        "var_95": var_95,
        "var_99": var_99,
        "sharpe_ratio": sharpe
    }, df, drawdown_series

def plot_risk_summary(ticker, df, drawdown_series):
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    axes[0].plot(df['date'], df['close'], color='black')
    axes[0].set_title(f'{ticker} — Price History')

    axes[1].fill_between(df['date'], drawdown_series * 100, 0, color='red', alpha=0.4)
    axes[1].set_title(f'{ticker} — Drawdown (%)')
    axes[1].set_ylabel('Drawdown %')

    plt.tight_layout()
    save_path = Path(__file__).parent / f"risk_{ticker}.png"
    plt.savefig(save_path)
    print(f"Chart saved to {save_path}")

if __name__ == "__main__":
    TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    all_metrics = {}

    for ticker in TICKERS:
        print(f"\n{'='*50}")
        print(f"Risk Analysis: {ticker}")
        print('='*50)

        metrics, df, drawdown_series = analyze_ticker(ticker)

        print(f"Daily Volatility:       {metrics['daily_volatility']*100:.2f}%")
        print(f"Annualized Volatility:  {metrics['annualized_volatility']*100:.2f}%")
        print(f"Max Drawdown:           {metrics['max_drawdown']*100:.2f}%")
        print(f"VaR (95% confidence):   {metrics['var_95']*100:.2f}% (daily)")
        print(f"VaR (99% confidence):   {metrics['var_99']*100:.2f}% (daily)")
        print(f"Sharpe Ratio:           {metrics['sharpe_ratio']:.2f}")

        plot_risk_summary(ticker, df, drawdown_series)
        all_metrics[ticker] = metrics

    print(f"\n{'='*50}")
    print("SUMMARY — Risk Metrics Across All Tickers")
    print('='*50)
    summary_df = pd.DataFrame(all_metrics).T
    summary_df = summary_df.round(4)
    print(summary_df)
    summary_df.to_csv(Path(__file__).parent / "risk_summary.csv")