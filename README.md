# Monglo - Framework-Agnostic MongoDB Admin Library

**The MongoDB admin interface that's actually magical to use.**

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## ✨ Why Monglo?

❌ **Other MongoDB admin tools**:
- Require tons of boilerplate code
- Manual template setup, routing, serialization
- Framework-locked or ORM-dependent  
- Complex configuration

✅ **Monglo**:
- **10 lines of code** - that's it!
- Library handles EVERYTHING automatically
- Works with FastAPI, Flask, Django
- Auto-detects collections, schemas, relationships
- Production-ready UI included

---

## 🚀 Quick Start (< 5 minutes)

### Installation

```bash
pip install monglo motor fastapi  # or flask, or django
```

### Setup (Literally 10 lines!)

```python
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from monglo import MongloEngine
from monglo.ui_helpers.fastapi import create_ui_router

# 1. Connect to MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017")

# 2. Create FastAPI app
app = FastAPI()

# 3. Initialize Monglo
engine = MongloEngine(database=client.mydb, auto_discover=True)

@app.on_event("startup")
async def startup():
    await engine.initialize()
    app.include_router(create_ui_router(engine))

# That's it! 🎉
```

**Run it:**
```bash
uvicorn app:app --reload
```

**Visit:** `http://localhost:8000/admin`

You now have a **full-featured admin interface** with:
- ✅ Collection browsing
- ✅ Document viewing/editing
- ✅ Search and filtering
- ✅ Relationship navigation
- ✅ Auto-detected schemas
- ✅ Professional UI

---

## 🎯 Features

### 🔮 Magical Auto-Detection

```python
# Just initialize - Monglo does the rest
engine = MongloEngine(database=db, auto_discover=True)
await engine.initialize()

# Automatically discovers:
# - All collections
# - Field types and schemas
# - Relationships (user_id → users collection)
# - Indexes
```

### 🔗 Intelligent Relationships

```python
# Your MongoDB document:
{
    "user_id": ObjectId("..."),      # → Automatically links to users collection
    "tags": [ObjectId("...")],       # → Automatically links to tags collection  
    "category": "electronics"
}

# Monglo automatically:
# - Detects these relationships
# - Creates clickable navigation
# - Resolves related documents
# - Shows relationship graphs
```

### 📊 Dual Views

**Table View** - Browse and filter thousands of documents
- Sortable columns
- Advanced filtering
- Global search
- Bulk operations
- Export (CSV, JSON)

**Document View** - Inspect and edit individual documents
- Full JSON tree structure
- Relationship navigation
- Field validation
- Nested document support

### 🎨 Production-Ready UI

- Modern, responsive design
- Dark/light modes
- Customizable branding
- Mobile-friendly
- Professional aesthetics

---

## 📚 Framework Support

### FastAPI (Recommended)

```python
from monglo.ui_helpers.fastapi import create_ui_router

app.include_router(create_ui_router(engine))
```

### Flask

```python
from monglo.ui_helpers.flask import create_ui_blueprint

app.register_blueprint(create_ui_blueprint(engine))
```

### Django

```python
# In urls.py
from monglo.ui_helpers.django import create_ui_urlpatterns

urlpatterns = [
    *create_ui_urlpatterns(engine, prefix="admin"),
]
```

---

## 🛠️ Customization (Optional!)

Everything works out of the box, but you can customize:

### Branding

```python
create_ui_router(
    engine,
    title="My Admin Panel",
    logo="https://example.com/logo.png",
    brand_color="#ff6b6b"
)
```

### Collection Configuration

```python
from monglo import CollectionConfig, TableViewConfig

await engine.register_collection(
    "products",
    config=CollectionConfig(
        list_fields=["name", "price", "stock"],
        search_fields=["name", "description"],
        table_view=TableViewConfig(
            per_page=50,
            default_sort=[("created_at", -1)]
        )
    )
)
```

### Authentication

```python
from monglo.auth import SimpleAuthProvider

engine = MongloEngine(
    database=db,
    auth_provider=SimpleAuthProvider(users={
        "admin": {
            "password_hash": SimpleAuthProvider.hash_password("admin123"),
            "role": "admin"
        }
    })
)
```

---

## 📖 Documentation

- [5-Minute Quickstart](docs/quickstart/index.md)
- [Core Concepts](docs/core-concepts/engine.md)
- [Configuration Guide](docs/guides/configuration.md)
- [API Reference](docs/api-reference/engine.md)

---

## 🎓 Examples

Check out [`examples/`](examples/) for complete working examples:

- **[simple_fastapi_example](examples/simple_fastapi_example/)** - Minimal FastAPI setup (10 lines)
- **[flask_minimal](examples/flask_minimal/)** - Minimal Flask setup
- **[fastapi_example](examples/fastapi_example/)** - Full-featured FastAPI app
- **[relationships_demo](examples/relationships_demo/)** - Complex relationships example

---

## 💻 Development

### Setup

```bash
# Clone the repo
git clone https://github.com/yourusername/monglo.git
cd monglo

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install development dependencies
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/ --cov=monglo --cov-report=html
```

### Run Linters

```bash
ruff check monglo/
black monglo/ tests/
mypy monglo/ --strict
```

### Run Examples

```bash
cd examples/simple_fastapi_example
uvicorn app:app --reload
```

---

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📝 License

MIT © 2025

---

## ⭐ Star History

If Monglo saves you time, give it a star! ⭐

---

## 🙏 Acknowledgments

Built with:
- [Motor](https://motor.readthedocs.io/) - Async MongoDB driver
- [FastAPI](https://fastapi.tiangolo.com/) / [Flask](https://flask.palletsprojects.com/) / [Django](https://www.djangoproject.com/)
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation

---

**Before Monglo:** 380 lines of boilerplate (templates, routing, serialization, filters...)

**After Monglo:** 10 lines. Everything just works. ✨
