import pandas as pd
from pathlib import Path

RAW_DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data-pipeline" / "raw_data"

def get_latest_sentiment_file():
    files = sorted(RAW_DATA_DIR.glob("news_sentiment_*.csv"))
    if not files:
        return None
    return files[-1]

def get_sentiment(symbol: str):
    filepath = get_latest_sentiment_file()
    if filepath is None:
        return None

    df = pd.read_csv(filepath)
    symbol_df = df[df['symbol'] == symbol]

    if symbol_df.empty:
        return None

    avg_score = symbol_df['sentiment_score'].mean()
    label_counts = symbol_df['sentiment_label'].value_counts().to_dict()

    recent_articles = symbol_df.sort_values('published', ascending=False).head(5)
    articles = recent_articles[['title', 'sentiment_label', 'sentiment_score', 'link']].to_dict(orient='records')

    return {
        "symbol": symbol,
        "average_sentiment_score": round(float(avg_score), 3),
        "label_distribution": label_counts,
        "total_articles": len(symbol_df),
        "recent_articles": articles
    }