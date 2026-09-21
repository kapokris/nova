function ForecastCard({ data }) {
  if (!data) return null;
  const isPositive = data.predicted_change >= 0;

  return (
    <div className="card">
      <h3>XGBoost Forecast</h3>
      <div className="forecast-row">
        <div>
          <span className="label">Current</span>
          <span className="value">${data.current_close.toFixed(2)}</span>
        </div>
        <span className="arrow">→</span>
        <div>
          <span className="label">Predicted Next</span>
          <span className="value">${data.predicted_next_close.toFixed(2)}</span>
        </div>
      </div>
      <div className={`forecast-change ${isPositive ? 'positive' : 'negative'}`}>
        {isPositive ? '+' : ''}{data.predicted_change.toFixed(2)} ({isPositive ? '+' : ''}{data.predicted_change_pct.toFixed(2)}%)
      </div>
    </div>
  );
}

export default ForecastCard;