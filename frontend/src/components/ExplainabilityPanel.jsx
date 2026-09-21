function ExplainabilityPanel({ data }) {
  if (!data) return null;

  return (
    <div className="card">
      <h3>Prediction Explainability (SHAP)</h3>
      <p className="explain-summary">
        Base value: ${data.base_value} → Predicted: ${data.predicted_next_close}
      </p>
      <div className="shap-bars">
        {data.top_feature_contributions.map((f, i) => (
          <div key={i} className="shap-row">
            <span className="shap-feature">{f.feature}</span>
            <div className="shap-bar-track">
              <div
                className={`shap-bar ${f.impact >= 0 ? 'positive' : 'negative'}`}
                style={{ width: `${Math.min(Math.abs(f.impact) * 15, 100)}%` }}
              />
            </div>
            <span className="shap-value">{f.impact >= 0 ? '+' : ''}{f.impact}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ExplainabilityPanel;