# Flask Minimal Example

The absolute minimum code needed to get a full MongoDB admin interface with Flask.

## What You Get

With just **10 lines of code**, you get the same features as FastAPI - complete admin interface!

## Installation

```bash
pip install monglo motor flask
```

## The Code (10 lines!)

```python
from flask import Flask
from motor.motor_asyncio import AsyncIOMotorClient
from monglo import MongloEngine
from monglo.adapters.flask import create_flask_blueprint
from monglo.ui_helpers.flask import create_ui_blueprint

client = AsyncIOMotorClient("mongodb://localhost:27017")
app = Flask(__name__)
engine = MongloEngine(database=client.mydb, auto_discover=True)

@app.before_serving
async def startup():
    await engine.initialize()
    app.register_blueprint(create_flask_blueprint(engine))  # API
    app.register_blueprint(create_ui_blueprint(engine))      # UI
```

## Run

```bash
python app.py
```

## Access

- **Admin UI**: http://localhost:5000/admin
- **API**: http://localhost:5000/api/admin

## Features

Same as FastAPI example - library handles everything:
- Auto-discovery of collections
- Schema inference
- Relationship detection
- Complete REST API
- Professional UI
- Search, filter, sort
- CRUD operations

## Comparison

**Without Monglo**:
- Manual Flask-Admin setup
- SQLAlchemy/MongoEngine integration
- Custom views and forms
- Template development
- 300+ lines of code

**With Monglo**:
- 10 lines total
- Everything automatic
- 5 minutes setup

See [FastAPI example README](../simple_fastapi_example/README.md) for full feature list.
