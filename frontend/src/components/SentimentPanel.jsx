function SentimentPanel({ data }) {
  if (!data) return null;
  const score = data.average_sentiment_score;
  const sentimentClass = score > 0.05 ? 'positive' : score < -0.05 ? 'negative' : 'neutral';

  return (
    <div className="card">
      <h3>News Sentiment</h3>
      <div className={`sentiment-score ${sentimentClass}`}>
        {score > 0 ? '+' : ''}{score.toFixed(3)}
      </div>
      <div className="label-distribution">
        {Object.entries(data.label_distribution).map(([label, count]) => (
          <span key={label} className={`badge ${label}`}>{label}: {count}</span>
        ))}
      </div>
      <ul className="article-list">
        {data.recent_articles.slice(0, 3).map((article, i) => (
          <li key={i}>
            <a href={article.link} target="_blank" rel="noreferrer">{article.title}</a>
            <span className={`tag ${article.sentiment_label}`}>{article.sentiment_label}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default SentimentPanel;