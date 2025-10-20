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
