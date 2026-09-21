import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const getAssets = () => api.get('/assets').then(res => res.data);

export const getMarketData = (symbol, limit = 100) =>
  api.get(`/market-data/${symbol}?limit=${limit}`).then(res => res.data);

export const getForecast = (symbol) =>
  api.get(`/forecast/${symbol}`).then(res => res.data);

export const getRisk = (symbol) =>
  api.get(`/risk/${symbol}`).then(res => res.data);

export const getSentiment = (symbol) =>
  api.get(`/sentiment/${symbol}`).then(res => res.data);

export const getExplanation = (symbol) =>
  api.get(`/explain/${symbol}`).then(res => res.data);

export default api;