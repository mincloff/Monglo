# Monglo

**Framework-agnostic MongoDB admin library for Python.**

Auto-generate REST APIs and admin interfaces for MongoDB collections with minimal configuration.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-53%2F53%20passing-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-90%25+-brightgreen.svg)]()

## Features

- 🚀 **Auto-discovery** - Automatically introspect MongoDB collections
- 🔄 **Relationship Detection** - Smart detection of collection relationships
- 📊 **Multiple Views** - Table and document views with configuration
- 🎨 **Framework Adapters** - FastAPI, Flask, and Django support
- 🔍 **Advanced Querying** - Filtering, sorting, pagination, search
- 📤 **Export** - JSON, CSV, NDJSON export formats
- ⚡ **Async-first** - Built on Motor for performance
- 🎯 **Type-safe** - Full type hints and Pydantic validation

## Quick Start

### Installation

```bash
pip install monglo

# Install with framework support
pip install "monglo[fastapi]"  # or flask, django
```

### FastAPI Example

```python
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI
from monglo import MongloEngine
from monglo.adapters.fastapi import create_fastapi_router

# Setup
app = FastAPI()
client = AsyncIOMotorClient("mongodb://localhost:27017")
engine = MongloEngine(database=client.mydb, auto_discover=True)

# Mount admin router
@app.on_event("startup")
async def startup():
    await engine.initialize()
    app.include_router(create_fastapi_router(engine))

# That's it! Auto-generated endpoints at /api/admin/*
```

Visit `http://localhost:8000/docs` to see all generated endpoints.

## Usage

### Core Components

```python
from monglo import (
    MongloEngine,
    CRUDOperations,
    TableView,
    DocumentView,
    JSONSerializer,
)

# Initialize engine
engine = MongloEngine(database=db, auto_discover=True)
await engine.initialize()

# CRUD operations
admin = engine.registry.get("users")
crud = CRUDOperations(admin)

# List with pagination
result = await crud.list(page=1, per_page=20, filters={"status": "active"})

# Create
user = await crud.create({"name": "Alice", "email": "alice@example.com"})

# Update
updated = await crud.update(user["_id"], {"status": "verified"})

# Views
table_view = TableView(admin)
config = table_view.render_config()  # Table configuration for frontend
```

### Configuration

```python
from monglo import CollectionConfig, FilterConfig

config = CollectionConfig(
    display_name="Users",
    list_fields=["name", "email", "created_at"],
    search_fields=["name", "email"],
    sortable_fields=["name", "created_at"],
    filters=[
        FilterConfig(field="status", type="eq", options=["active", "inactive"])
    ]
)

await engine.register_collection("users", config=config)
```

## Documentation

- [Examples](./examples/) - Complete working examples
- [API Reference](#) - Full API documentation
- [Guide](#) - Comprehensive guide

## Framework Support

| Framework | Status | Adapter |
|-----------|--------|---------|
| FastAPI | ✅ Supported | `monglo.adapters.fastapi` |
| Flask | ✅ Supported | `monglo.adapters.flask` |
| Django | ✅ Supported | `monglo.adapters.django` |

## Requirements

- Python 3.10+
- MongoDB 4.4+
- Motor 3.3+

## Development

```bash
# Clone repository
git clone https://github.com/me-umar/monglo.git
cd monglo

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=monglo --cov-report=html
```

## License

MIT License - see [LICENSE](LICENSE) file.

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

## Credits

Built with:
- [Motor](https://motor.readthedocs.io/) - Async MongoDB driver
- [Pydantic](https://pydantic.dev/) - Data validation
- [FastAPI](https://fastapi.tiangolo.com/) / [Flask](https://flask.palletsprojects.com/) / [Django](https://www.djangoproject.com/)
