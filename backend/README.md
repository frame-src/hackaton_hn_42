# Project Setup Guide

## 1. Create a Virtual Environment

To keep dependencies isolated from your system Python, it’s best to use a virtual environment.

### For macOS / Linux

```bash
# Create a new virtual environment named 'venv'
python3 -m venv venv
```

```bash
# Activate the virtual environment
source venv/bin/activate
```

```bash
# Install Dependencies
pip install -r requirements.txt
```

```bash
# Run the App
uvicorn main:app --reload
```
curl and test:
http://127.0.0.1:8000/ → Root endpoint
http://127.0.0.1:8000/ping → Health check
http://127.0.0.1:8000/fetch?url=URL → Fetch data from API

## /users/filter (Heilbronn filter)

This endpoint pages the 42 Intra API and returns users filtered by campus name, email domain, and active account status.

Endpoint: GET /users/filter

Query parameters (all optional):
- `campus` (default: `Heilbronn`) — substring matched (case-insensitive) against user's campus names.
- `email_domain` (default: `42heilbronn.de`) — case-insensitive suffix match for user's email.
- `per_page` (default: `100`) — number of users requested per page to the 42 API.
- `max_pages` (default: `5`) — maximum number of pages to fetch (safety limit).

Response JSON:
```
{
	"count": <number of matches>,
	"results": [
		{"login":"...","displayname":"...","email":"...","campus":"..."},
		...
	]
}
```

Example calls:

Default (Heilbronn emails, active accounts):
```bash
curl -s 'http://127.0.0.1:8000/users/filter' | jq
```

Custom domain and more pages:
```bash
curl -s 'http://127.0.0.1:8000/users/filter?campus=Heilbronn&email_domain=@42heilbronn.de&per_page=200&max_pages=10' | jq
```

Notes:
- The endpoint requires that `CLIENT_ID` and `CLIENT_SECRET` are set as environment variables (used to fetch the application token). See project setup above.
- Adjust `max_pages` if you need to search a larger user base; this endpoint is conservative by default to avoid excessive requests.
