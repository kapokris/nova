from fastapi import FastAPI

app = FastAPI(title="Nova API", version="0.1.0")

@app.get("/")
def root():
    return {"status": "Nova API is running"}