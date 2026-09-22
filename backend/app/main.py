from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import market, forecast, risk, sentiment, explain

app = FastAPI(title="Nova API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://3.96.170.91:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(market.router)
app.include_router(forecast.router)
app.include_router(risk.router)
app.include_router(sentiment.router)
app.include_router(explain.router)

@app.get("/")
def root():
    return {"status": "Nova API is running"}