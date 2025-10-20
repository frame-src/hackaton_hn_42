from fastapi import FastAPI, HTTPException
import httpx
import os
import time

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
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url, timeout=10.0)
            r.raise_for_status()
            return r.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# --- 42 Intra API helpers ---
_token_cache = {"access_token": None, "expires_at": 0}
@app.post("/token")
async def fetch_42_token() -> str:
    """Fetch an application token using client_credentials grant and cache it in-memory."""
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    if not client_id or not client_secret:
        raise HTTPException(status_code=500, detail='CLIENT_ID/CLIENT_SECRET not set')

    # reuse cached token when still valid
    if _token_cache["access_token"] and _token_cache["expires_at"] > time.time():
        return _token_cache["access_token"]

    token_url = 'https://api.intra.42.fr/oauth/token'
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(token_url, data=data, timeout=10.0)
            resp.raise_for_status()
            obj = resp.json()
        except httpx.HTTPStatusError as e:
            # propagate 4xx/5xx from token endpoint as 502
            raise HTTPException(status_code=502, detail=f'Token error: {e.response.status_code} {e.response.text}')
        except Exception as e:
            raise HTTPException(status_code=502, detail=str(e))

    # expected fields: access_token, expires_in
    access_token = obj.get('access_token')
    expires_in = obj.get('expires_in', 0)
    if not access_token:
        raise HTTPException(status_code=502, detail='No access_token in token response')

    # set a small safety margin
    _token_cache['access_token'] = access_token
    _token_cache['expires_at'] = time.time() + max(0, int(expires_in) - 30)
    return access_token


@app.get('/user/{login}')
async def get_user(login: str):
    """Return basic user info fetched from 42 Intra API for `login`."""
    token = await fetch_42_token()
    url = f'https://api.intra.42.fr/v2/users/{login}'
    headers = {'Authorization': f'Bearer {token}'}
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, headers=headers, timeout=10.0)
            if resp.status_code == 404:
                raise HTTPException(status_code=404, detail='User not found')
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=502, detail=f'42 API error: {e.response.status_code} - {e.response.text}')
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # map to small response
    return {
        'login': data.get('login'),
        'displayname': data.get('displayname'),
        'email': data.get('email'),
        'raw': data,
    }

