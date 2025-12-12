# Monglo

**Modern MongoDB Admin Library for Python**

Build production-ready MongoDB admin interfaces in minutes, not days.

---

## What is Monglo?

Monglo is a **framework-agnostic** Python library that auto-generates beautiful, functional admin interfaces for MongoDB. It's designed for developers who want:

- ✅ **Zero Configuration** - Auto-discovers collections and relationships
- ✅ **Framework Agnostic** - Works with FastAPI, Flask, Django, Starlette
- ✅ **Intelligent Relationships** - Automatically detects ObjectId references
- ✅ **Dual Views** - Table view AND document view for every collection
- ✅ **Production Ready** - Built on Motor (async) with proper error handling
- ✅ **Beautiful UI** - Modern dark mode interface included

---

## Quick Start

### Installation

```bash
pip install monglo[fastapi]  # or flask, django
```

### 3-Line Setup

```python
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from monglo import MongloEngine
from monglo.adapters.fastapi import create_fastapi_router
from monglo.ui_helpers.fastapi import create_ui_router

app = FastAPI()
client = AsyncIOMotorClient("mongodb://localhost:27017")
engine = MongloEngine(database=client.mydb, auto_discover=True)

@app.on_event("startup")
async def startup():
    await engine.initialize()
    app.include_router(create_fastapi_router(engine))  # API
    app.include_router(create_ui_router(engine))       # UI
```

**That's it!** Visit `http://localhost:8000/admin` 🎉

---

## Features

### 🔍 Auto-Discovery

Monglo automatically discovers all collections in your database and introspects their schemas:

```python
engine = MongloEngine(database=db, auto_discover=True)
await engine.initialize()
# All collections are now registered!
```

### 🔗 Smart Relationships

Automatically detects relationships using multiple strategies:

- **Naming conventions** - `user_id` → `users._id`
- **ObjectId fields** - Any field containing ObjectIds
- **DBRef** - Full DBRef support
- **Arrays** - One-to-many via ObjectId arrays

```python
# No configuration needed! Relationships detected automatically
await engine.register_collection("orders")  # Finds user_id → users
```

### 📊 Dual View System

#### Table View
Spreadsheet-like interface with:
- Sorting, filtering, searching
- Pagination
- Bulk actions (delete, export)
- Customizable columns

#### Document View
JSON tree structure with:
- Syntax highlighting
- Nested document support
- Edit modal
- Relationship navigation

### 🎨 Beautiful UI

Modern interface with:
- **Dark mode** (auto-saved preference)
- **MongoDB green** color scheme
- **Resizable sidebar**
- **Responsive design**
- **FontAwesome icons**

---

## Core Concepts

### Framework Agnostic Design

Monglo separates core logic from framework integration:

```
monglo/
├── core/          # Framework-agnostic engine
├── operations/    # CRUD, search, pagination
├── views/         # Table, document, relationship views
└── adapters/      # FastAPI, Flask, Django adapters
```

### Engine

The `MongloEngine` is the heart of Monglo:

```python
from monglo import MongloEngine

engine = MongloEngine(
    database=db,
    auto_discover=True,              # Auto-register all collections
    relationship_detection="auto"    # auto | manual | off
)

await engine.initialize()
```

### Collection Admin

Each collection gets a `CollectionAdmin` instance:

```python
# Register with auto-config
admin = await engine.register_collection("users")

# Or with custom config
from monglo.core.config import CollectionConfig

admin = await engine.register_collection("products", config=CollectionConfig(
    display_name="Product Catalog",
    list_fields=["name", "price", "stock"],
    search_fields=["name", "description"],
    sortable_fields=["name", "price", "created_at"]
))
```

---

## API Reference

### MongloEngine

Main engine class for managing MongoDB admin.

```python
class MongloEngine:
    def __init__(
        self,
        database: AsyncIOMotorDatabase,
        auto_discover: bool = True,
        relationship_detection: Literal["auto", "manual", "off"] = "auto"
    )
    
    async def initialize() -> None
    async def register_collection(name: str, config: CollectionConfig | None = None) -> CollectionAdmin
    def get_adapter(framework: str) -> BaseAdapter
```

### CRUD Operations

```python
from monglo.operations.crud import CRUDOperations

crud = CRUDOperations(collection_admin)

# List with pagination, search, filters
result = await crud.list(
    page=1,
    per_page=20,
    search="query",
    filters={"status": "active", "price__gte": 100},
    sort=[("created_at", -1)]
)

# CRUD operations
document = await crud.get(id)
created = await crud.create(data)
updated = await crud.update(id, data)
deleted = await crud.delete(id)
```

### Views

```python
from monglo.views import TableView, DocumentView

# Table view config
table = TableView(collection_admin)
config = table.render_config()

# Document view config
doc = DocumentView(collection_admin)
config = doc.render_config()
```

---

## Configuration

### Collection Config

```python
from monglo.core.config import CollectionConfig, TableViewConfig

config = CollectionConfig(
    display_name="Users",
    list_fields=["name", "email", "created_at"],
    search_fields=["name", "email"],
    sortable_fields=["name", "created_at"],
    
    table_view=TableViewConfig(
        per_page=50,
        enable_bulk_actions=True,
        enable_export=True
    )
)
```

### Permissions

```python
config = CollectionConfig(
    permissions={
        "can_create": True,
        "can_read": True,
        "can_update": True,
        "can_delete": False  # Prevent deletions
    }
)
```

---

## Examples

### FastAPI

See [quickstart/fastapi.md](quickstart/fastapi.md)

### Flask

See [quickstart/flask.md](quickstart/flask.md)

### Django

See [quickstart/django.md](quickstart/django.md)

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](../CONTRIBUTING.md)

---

## License

MIT - See [LICENSE](../LICENSE)

---

## Links

- **Documentation**: https://monglo.readthedocs.io
- **GitHub**: https://github.com/yourusername/monglo
- **PyPI**: https://pypi.org/project/monglo
- **Issues**: https://github.com/yourusername/monglo/issues
