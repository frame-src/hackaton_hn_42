from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI(title="App", version="1.0.0")


@app.get("/")
async def root():
    return {"message": "Welcome!"}


@app.get("/ping")
async def ping():
    """Simple health check endpoint."""
    return {"status": "ok"}


@app.get("/tom")
async def fetch_data(url: str):
    """
    TOMEK: 
        Fetch data from an external API using httpx.
    """
    async with httpx

