import { useState, useEffect } from 'react';
import { getAssets, getMarketData, getForecast, getRisk, getSentiment, getExplanation } from './api';
import MarketOverview from './components/MarketOverview';
import PriceChart from './components/PriceChart';
import ForecastCard from './components/ForecastCard';
import RiskPanel from './components/RiskPanel';
import SentimentPanel from './components/SentimentPanel';
import ExplainabilityPanel from './components/ExplainabilityPanel';
import './App.css';

function App() {
  const [symbols, setSymbols] = useState([]);
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');
  const [marketData, setMarketData] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [risk, setRisk] = useState(null);
  const [sentiment, setSentiment] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getAssets().then(data => setSymbols(data.symbols)).catch(err => setError(err.message));
  }, []);

  useEffect(() => {
    setLoading(true);
    setError(null);

    Promise.all([
      getMarketData(selectedSymbol),
      getForecast(selectedSymbol),
      getRisk(selectedSymbol),
      getSentiment(selectedSymbol),
      getExplanation(selectedSymbol),
    ])
      .then(([marketRes, forecastRes, riskRes, sentimentRes, explanationRes]) => {
        setMarketData(marketRes);
        setForecast(forecastRes);
        setRisk(riskRes);
        setSentiment(sentimentRes);
        setExplanation(explanationRes);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [selectedSymbol]);

  return (
    <div className="app">
      <header className="header">
        <h1>Nova <span className="subtitle">Financial ML Dashboard</span></h1>
        <select value={selectedSymbol} onChange={(e) => setSelectedSymbol(e.target.value)}>
          {symbols.map(sym => (
            <option key={sym} value={sym}>{sym}</option>
          ))}
        </select>
      </header>

      {error && <div className="error">Error: {error}</div>}
      {loading && <div className="loading">Loading {selectedSymbol}...</div>}

      {!loading && !error && (
        <div className="dashboard-grid">
          <MarketOverview data={marketData} />
          <ForecastCard data={forecast} />
          <PriceChart data={marketData} />
          <RiskPanel data={risk} />
          <SentimentPanel data={sentiment} />
          <ExplainabilityPanel data={explanation} />
        </div>
      )}
    </div>
  );
}

export default App;