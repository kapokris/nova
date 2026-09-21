import feedparser
import pandas as pd
from pathlib import Path
from datetime import datetime
from transformers import pipeline

TICKERS = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Google",
    "AMZN": "Amazon",
    "TSLA": "Tesla"
}

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "data-pipeline" / "raw_data"

def fetch_news(ticker: str, company_name: str, max_articles: int = 15):
    """Fetch recent news headlines for a ticker via Google News RSS (free, no API key)."""
    url = f"https://news.google.com/rss/search?q={company_name}+stock&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)

    articles = []
    for entry in feed.entries[:max_articles]:
        articles.append({
            "symbol": ticker,
            "title": entry.title,
            "published": entry.get("published", ""),
            "link": entry.link
        })
    print(f"Fetched {len(articles)} articles for {ticker}")
    return articles

def load_sentiment_model():
    print("Loading FinBERT (finance-specific sentiment model, ~440MB, cached after first run)...")
    return pipeline("sentiment-analysis", model="ProsusAI/finbert")

def analyze_sentiment(articles, sentiment_model):
    for article in articles:
        result = sentiment_model(article["title"][:512])[0]
        label = result["label"].lower()  # finbert returns: positive / negative / neutral
        article["sentiment_label"] = label
        if label == "positive":
            article["sentiment_score"] = result["score"]
        elif label == "negative":
            article["sentiment_score"] = -result["score"]
        else:
            article["sentiment_score"] = 0.0
    return articles

if __name__ == "__main__":
    sentiment_model = load_sentiment_model()
    all_articles = []

    for ticker, company_name in TICKERS.items():
        articles = fetch_news(ticker, company_name)
        articles = analyze_sentiment(articles, sentiment_model)
        all_articles.extend(articles)

    df = pd.DataFrame(all_articles)
    print(f"\nTotal articles processed: {len(df)}")

    print("\nSentiment label distribution:")
    print(df['sentiment_label'].value_counts())

    print("\nAverage sentiment score by ticker:")
    print(df.groupby('symbol')['sentiment_score'].mean().round(3))

    filename = f"news_sentiment_{datetime.now().strftime('%Y%m%d')}.csv"
    filepath = OUTPUT_DIR / filename
    df.to_csv(filepath, index=False)
    print(f"\nSaved to {filepath}")