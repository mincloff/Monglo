# Quickstart Guide

Get started with Monglo in 5 minutes.

## Installation

```bash
pip install monglo motor fastapi  # or flask, or django
```

## Basic Setup

### 1. Connect to MongoDB

```python
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.your_database
```

### 2. Initialize Monglo

```python
from monglo import MongloEngine

engine = MongloEngine(database=db, auto_discover=True)
await engine.initialize()
```

### 3. Add to Your App

**FastAPI:**
```python
from fastapi import FastAPI
from monglo.ui_helpers.fastapi import create_ui_router

app = FastAPI()

@app.on_event("startup")
async def startup():
    await engine.initialize()
    app.include_router(create_ui_router(engine))
```

**Flask:**
```python
from flask import Flask
from monglo.ui_helpers.flask import create_ui_blueprint

app = Flask(__name__)
app.register_blueprint(create_ui_blueprint(engine))
```

**Django:**
```python
# In urls.py
from monglo.ui_helpers.django import create_ui_urlpatterns

urlpatterns = [
    *create_ui_urlpatterns(engine, prefix="admin"),
]
```

## That's It!

Visit `http://localhost:8000/admin` and you have a full admin interface.

## What You Get

- ✅ Auto-detected collections
- ✅ Professional admin UI
- ✅ Complete REST API
- ✅ Search, filter, sort
- ✅ Relationship navigation
- ✅ CRUD operations

## Next Steps

- [Configuration Guide](guides/configuration.md)
- [Authentication](guides/authentication.md)
- [Advanced Features](guides/advanced.md)
