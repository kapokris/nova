import pandas as pd
import shap
from app.services.forecast_service import load_model, engineer_features, FEATURE_COLS
from app.services.market_data import get_engine

def get_explanation(symbol: str):
    model = load_model(symbol)
    if model is None:
        return None

    engine = get_engine()
    df = pd.read_sql(
        f"SELECT * FROM market_prices WHERE symbol = '{symbol}' ORDER BY date",
        engine
    )
    df['date'] = pd.to_datetime(df['date'])
    df = engineer_features(df)
    df = df.dropna().reset_index(drop=True)

    latest_row = df.iloc[[-1]][FEATURE_COLS]

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(latest_row)

    contributions = pd.DataFrame({
        "feature": FEATURE_COLS,
        "shap_value": shap_values[0]
    }).sort_values("shap_value", key=abs, ascending=False)

    predicted_close = float(model.predict(latest_row)[0])
    base_value = float(explainer.expected_value)

    top_contributions = [
        {
            "feature": row["feature"],
            "impact": round(float(row["shap_value"]), 3),
            "direction": "increases" if row["shap_value"] > 0 else "decreases"
        }
        for _, row in contributions.head(8).iterrows()
    ]

    return {
        "symbol": symbol,
        "as_of_date": str(df.iloc[-1]['date'].date()),
        "predicted_next_close": round(predicted_close, 2),
        "base_value": round(base_value, 2),
        "top_feature_contributions": top_contributions
    }