import pandas as pd
import numpy as np
from app.services.market_data import get_engine

RISK_FREE_RATE = 0.045

def get_risk_metrics(symbol: str):
    engine = get_engine()
    df = pd.read_sql(
        f"SELECT date, close FROM market_prices WHERE symbol = '{symbol}' ORDER BY date",
        engine
    )
    if df.empty:
        return None

    df['date'] = pd.to_datetime(df['date'])
    df['daily_return'] = df['close'].pct_change()
    df = df.dropna()

    daily_vol = df['daily_return'].std()
    annual_vol = daily_vol * np.sqrt(252)

    cumulative_max = df['close'].cummax()
    drawdown = (df['close'] - cumulative_max) / cumulative_max
    max_drawdown = drawdown.min()

    var_95 = np.percentile(df['daily_return'], 5)
    var_99 = np.percentile(df['daily_return'], 1)

    daily_rf = RISK_FREE_RATE / 252
    excess_returns = df['daily_return'] - daily_rf
    sharpe = (excess_returns.mean() / df['daily_return'].std()) * np.sqrt(252)

    return {
        "symbol": symbol,
        "daily_volatility_pct": round(daily_vol * 100, 2),
        "annualized_volatility_pct": round(annual_vol * 100, 2),
        "max_drawdown_pct": round(max_drawdown * 100, 2),
        "var_95_pct": round(var_95 * 100, 2),
        "var_99_pct": round(var_99 * 100, 2),
        "sharpe_ratio": round(sharpe, 2)
    }