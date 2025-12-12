# FastAPI Minimal Example

The absolute minimum code needed to get a full MongoDB admin interface with FastAPI.

## What You Get

With just **10 lines of code**, you get:
- ✅ Complete REST API for all collections
- ✅ Full admin UI with table & document views
- ✅ Auto-detected relationships
- ✅ Search, filtering, sorting
- ✅ CRUD operations
- ✅ Professional UI

## Installation

```bash
pip install monglo motor fastapi uvicorn
```

## The Code (10 lines!)

```python
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from monglo import MongloEngine
from monglo.adapters.fastapi import create_fastapi_router
from monglo.ui_helpers.fastapi import create_ui_router

client = AsyncIOMotorClient("mongodb://localhost:27017")
app = FastAPI()
engine = MongloEngine(database=client.mydb, auto_discover=True)

@app.on_event("startup")
async def startup():
    await engine.initialize()
    app.include_router(create_fastapi_router(engine))  # API
    app.include_router(create_ui_router(engine))       # UI
```

## Run

```bash
uvicorn app:app --reload
```

## Access

- **Admin UI**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/docs
- **API**: http://localhost:8000/api/admin

## What the Library Does (Automatically)

### 🔍 Auto-Discovery
- Scans all collections in your database
- Infers schemas from sample documents
- Detects field types automatically

### 🔗 Smart Relationships
- Detects `user_id` → `users` collection
- Detects `tags: [ObjectId]` → `tags` collection
- Creates clickable navigation

### 🎨 Complete UI
- Professional admin interface
- Table view with sorting, filtering, search
- Document view with JSON tree
- Relationship graph visualization

### 📡 REST API
- GET `/api/admin/` - List collections
- GET `/api/admin/{collection}` - List documents
- GET `/api/admin/{collection}/{id}` - Get document
- POST `/api/admin/{collection}` - Create document
- PUT `/api/admin/{collection}/{id}` - Update document
- DELETE `/api/admin/{collection}/{id}` - Delete document

### ⚙️ All Features
- Pagination (offset & cursor-based)
- Full-text search
- Advanced filtering
- Sorting
- Data validation
- Error handling
- Serialization (ObjectId, datetime, etc.)

## Customization (Optional)

If you want to customize anything:

```python
# Custom branding
create_ui_router(
    engine,
    title="My Admin Panel",
    logo="https://example.com/logo.png",
    brand_color="#ff6b6b"
)

# Custom collection config
from monglo import CollectionConfig

await engine.register_collection(
    "products",
    config=CollectionConfig(
        list_fields=["name", "price", "stock"],
        search_fields=["name", "description"]
    )
)
```

But you don't need any of this to get started!

## Comparison

**Without Monglo** (typical setup):
- ✗ 200+ lines of route definitions
- ✗ Manual serialization code
- ✗ Template setup
- ✗ Form handling
- ✗ Validation logic
- ✗ UI development
- ⏱️ Hours/days of work

**With Monglo**:
- ✅ 10 lines of code
- ✅ Everything works automatically
- ⏱️ 5 minutes

## Next Steps

- Check out the [full example](../fastapi_example/) for advanced features
- Read the [documentation](../../docs/)
- See [customization options](../../docs/guides/configuration.md)
