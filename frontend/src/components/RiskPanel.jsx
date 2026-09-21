function RiskPanel({ data }) {
  if (!data) return null;

  return (
    <div className="card">
      <h3>Risk Metrics</h3>
      <div className="metric-grid">
        <div className="metric">
          <span className="label">Annualized Volatility</span>
          <span className="value">{data.annualized_volatility_pct}%</span>
        </div>
        <div className="metric">
          <span className="label">Max Drawdown</span>
          <span className="value negative">{data.max_drawdown_pct}%</span>
        </div>
        <div className="metric">
          <span className="label">VaR (95%)</span>
          <span className="value">{data.var_95_pct}%</span>
        </div>
        <div className="metric">
          <span className="label">VaR (99%)</span>
          <span className="value">{data.var_99_pct}%</span>
        </div>
        <div className="metric">
          <span className="label">Sharpe Ratio</span>
          <span className="value">{data.sharpe_ratio}</span>
        </div>
      </div>
    </div>
  );
}

export default RiskPanel;