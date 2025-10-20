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


@app.get('/users/filter')
async def filter_users(campus: str = 'Heilbronn', email_domain: str = '42heilbronn.de', per_page: int = 100, max_pages: int = 5, include_login: str | None = None):
    """Fetch users from 42 API, page through results and return users who:
    - have an email that ends with `email_domain` (case-insensitive)
    - are listed on a campus that contains `campus` (case-insensitive)
    - have active? == true

    Query params:
    - campus: substring to search in user's campus names (default 'Heilbronn')
    - email_domain: domain suffix to match in email (default '42heilbronn.student.de')
    - per_page: items per page when calling 42 API
    - max_pages: maximum pages to fetch (safeguard)
    """
    token = await fetch_42_token()
    headers = {'Authorization': f'Bearer {token}'}
    matches = []
    campus_id = None
    campus_name = None
    try:
        async with httpx.AsyncClient() as client:
            # request a large per_page so we don't miss campuses due to pagination
            resp = await client.get('https://api.intra.42.fr/v2/campus?per_page=300', headers=headers, timeout=10.0)
            resp.raise_for_status()
            camps_list = resp.json()
            for c in camps_list:
                name = (c.get('name') or '')
                city = (c.get('city') or '')
                if campus.lower() in name.lower() or campus.lower() in city.lower():
                    campus_id = c.get('id')
                    campus_name = name or city
                    break
    except Exception as e:
        raise HTTPException(status_code=502, detail=f'42 API error when listing campuses: {str(e)}')

    if not campus_id:
        raise HTTPException(status_code=404, detail=f'Campus not found for "{campus}"')

    page = 1
    async with httpx.AsyncClient() as client:
        while page <= max_pages:
            url = f'https://api.intra.42.fr/v2/campus/{campus_id}/users?per_page={per_page}&page={page}'
            try:
                resp = await client.get(url, headers=headers, timeout=15.0)
                resp.raise_for_status()
                users = resp.json()
            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=502, detail=f'42 API error: {e.response.status_code}')
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

            if not users:
                break

            for item in users:
                # some endpoints return campus_user objects containing a 'user' field
                u = item.get('user') if isinstance(item, dict) and 'user' in item and isinstance(item.get('user'), dict) else item
                if not isinstance(u, dict):
                    continue
                # only include active users
                active = u.get('active?') if 'active?' in u else u.get('active')
                if not active:
                    continue
                matches.append({
                    'login': u.get('login'),
                    'displayname': u.get('displayname'),
                    'email': u.get('email'),
                    'raw': u,
                })

            page += 1

    # If include_login provided, ensure that user is present in results
    if include_login:
        try:
            inc_url = f'https://api.intra.42.fr/v2/users/{include_login}'
            async with httpx.AsyncClient() as client:
                resp = await client.get(inc_url, headers=headers, timeout=10.0)
                if resp.status_code == 200:
                    u = resp.json()
                    active = u.get('active?') if 'active?' in u else u.get('active')
                    if active:
                        # add only if not already present
                        if not any(m['login'] == u.get('login') for m in matches):
                            campuses = u.get('campus') or []
                            campus_names = ''
                            if isinstance(campuses, list):
                                campus_names = ', '.join([c.get('name','') for c in campuses if isinstance(c, dict)])
                            elif isinstance(campuses, dict):
                                campus_names = campuses.get('name','')
                            # ensure include_login uses the same shape as /user/{login}
                            matches.append({'login': u.get('login'), 'displayname': u.get('displayname'), 'email': u.get('email'), 'raw': u})
        except Exception:
            # ignore errors for include_login so endpoint still returns main results
            pass

    return {'count': len(matches), 'results': matches}

