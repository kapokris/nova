function MarketOverview({ data }) {
  if (!data || !data.latest) return null;
  const { latest } = data;
  const isPositive = latest.change >= 0;

  return (
    <div className="card">
      <h3>Market Overview</h3>
      <div className="price-display">
        <span className="price">${latest.close.toFixed(2)}</span>
        <span className={`change ${isPositive ? 'positive' : 'negative'}`}>
          {isPositive ? '+' : ''}{latest.change.toFixed(2)} ({isPositive ? '+' : ''}{latest.change_pct.toFixed(2)}%)
        </span>
      </div>
      <div className="meta">
        <span>Volume: {latest.volume.toLocaleString()}</span>
        <span>As of: {latest.date}</span>
      </div>
    </div>
  );
}

export default MarketOverview;