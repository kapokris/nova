# Nova — Financial ML Forecasting & Risk Analytics Platform

Nova is a full-stack financial analytics platform that forecasts stock prices, analyzes news sentiment, computes risk metrics, and explains model predictions — built as an end-to-end demonstration of applied ML, quantitative analytics, and production deployment practices.

**Nova is an analytics and forecasting platform, not a trading bot or stock-picking tool.** It's designed to demonstrate the kind of quantitative, risk-aware ML work relevant to roles like Quant Analyst Intern, Risk Analytics Intern, or ML Engineer Intern.

## Live Demo

- **App:** http://3.96.170.91:5173
- **API:** http://3.96.170.91:8000

> Note: hosted on an AWS EC2 free-tier instance that may be stopped when not actively demoed to control costs. If the link is down, clone and run locally (see below), or reach out and I'll spin it back up.

## What It Does

For 5 tickers (AAPL, MSFT, GOOGL, AMZN, TSLA), Nova provides:

- **Price forecasting** — next-day close price prediction via XGBoost (outperforms ARIMA on 4/5 tickers) and ARIMA baseline
- **Sentiment analysis** — real-time news sentiment via FinBERT (finance-tuned transformer), pulled from Google News RSS
- **Risk analytics** — annualized volatility, max drawdown, Value-at-Risk (95%/99%), Sharpe ratio
- **Model explainability** — SHAP-based feature attribution showing exactly why the model predicted what it did
- **Interactive dashboard** — React frontend with live charts, forecasts, sentiment, and risk panels per ticker

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   React      │────▶│   FastAPI     │────▶│   PostgreSQL     │
│   Frontend   │     │   Backend     │     │   (market data)  │
└─────────────┘     └──────┬───────┘     └─────────────────┘
                            │
                    ┌───────┴────────┐
                    │  Saved Models   │
                    │  (XGBoost,      │
                    │   SHAP)         │
                    └────────────────┘

Data pipeline (offline): yfinance → clean → feature engineer → PostgreSQL
ML pipeline (offline): ARIMA + XGBoost forecasting, FinBERT sentiment, risk analytics, SHAP explainability
```

Fully containerized with Docker Compose (backend, frontend, PostgreSQL) and deployed to AWS EC2.

## Tech Stack

| Layer | Tools |
|---|---|
| Data ingestion | yfinance, pandas |
| Feature engineering | Custom indicators: RSI, MACD, Bollinger Bands, EMA/SMA, lag features |
| Forecasting | XGBoost, ARIMA (pmdarima), chronological train/test split (no lookahead bias) |
| Sentiment | FinBERT (Hugging Face transformers), Google News RSS |
| Risk analytics | Historical VaR, Sharpe ratio, max drawdown, annualized volatility |
| Explainability | SHAP (TreeExplainer) |
| Backend | FastAPI, SQLAlchemy, PostgreSQL |
| Frontend | React, Vite, Recharts, Axios |
| Infra | Docker, Docker Compose, AWS EC2 |

## Key Results

**XGBoost vs. ARIMA (test MAPE, 30-day holdout):**

| Ticker | ARIMA | XGBoost |
|---|---|---|
| AAPL | 2.80% | 1.72% |
| MSFT | 1.52% | 1.57% |
| GOOGL | 6.09% | 2.17% |
| AMZN | 5.13% | 1.69% |
| TSLA | 9.16% | 3.00% |

XGBoost outperforms ARIMA on 4 of 5 tickers, with the largest gains on the more volatile names (TSLA, GOOGL). TSLA is consistently the hardest to forecast and carries the highest risk metrics (59.9% annualized volatility, -53.8% max drawdown) — a finding confirmed independently across EDA, both forecasting models, and risk analytics.

**Sentiment model selection:** An initial general-purpose sentiment model (DistilBERT, tuned on movie reviews) produced implausibly uniform negative scores across all 5 unrelated tickers — a domain-transfer failure where neutral financial language gets misread as negative. Switching to FinBERT (finance-specific) produced a realistic, balanced sentiment distribution (53% neutral, 15% positive, 15% negative).

## Running Locally

```bash
git clone https://github.com/kapokris/nova.git
cd nova

# Backend + DB + Frontend, all containerized
docker compose up -d --build
```

Then visit `http://localhost:5173`. Note: pre-trained models (`ml/saved_models/`) and sentiment data (`data-pipeline/raw_data/`) aren't tracked in git — you'll need to run the data pipeline scripts first (see `data-pipeline/scripts/`) to populate the database and train models before the API returns data.

## Project Structure

```
nova/
├── data-pipeline/     # Ingestion, cleaning, feature engineering
├── ml/                # ARIMA, XGBoost, sentiment, risk, SHAP models
├── backend/           # FastAPI service
├── frontend/          # React dashboard
└── docker-compose.yml
```
