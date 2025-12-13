# FastAPI Integration

Get your MongoDB admin interface running in under 5 minutes with FastAPI.

---

## Installation

```bash
# Install Monglo with FastAPI support
pip install monglo[fastapi]

# Or from source
git clone https://github.com/me-umar/monglo
cd monglo
pip install -e ".[fastapi]"
```

---

## Quick Start (5 Lines!)

```python
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from monglo import MongloEngine
from monglo.adapters.fastapi import create_fastapi_router
from monglo.ui_helpers.fastapi import create_ui_router

# Setup
app = FastAPI()
client = AsyncIOMotorClient("mongodb://localhost:27017")
engine = MongloEngine(database=client.mydb, auto_discover=True)

@app.on_event("startup")
async def startup():
    await engine.initialize()
    app.include_router(create_fastapi_router(engine, prefix="/api/admin"))
    app.include_router(create_ui_router(engine, prefix="/admin"))

# Run: uvicorn app:app
```

Visit:
- **Admin UI**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/docs
- **Collections API**: http://localhost:8000/api/admin

---

## What You Get

### Automatic API Endpoints

For each collection, Monglo generates:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/` | List all collections |
| GET | `/api/admin/{collection}` | List documents (paginated) |
| GET | `/api/admin/{collection}/{id}` | Get single document |
| POST | `/api/admin/{collection}` | Create document |
| PUT | `/api/admin/{collection}/{id}` | Update document |
| DELETE | `/api/admin/{collection}/{id}` | Delete document |
| GET | `/api/admin/{collection}/config/table` | Table view config |
| GET | `/api/admin/{collection}/config/document` | Document view config |

### Automatic UI Routes

| Route | Description |
|-------|-------------|
| `/admin` | Collection list home |
| `/admin/{collection}/table` | Table view for collection |
| `/admin/{collection}/{id}` | Document detail view |

---

## customization

### Custom Collection Config

```python
from monglo.core.config import CollectionConfig, TableViewConfig

await engine.register_collection("products", config=CollectionConfig(
    display_name="Product Catalog",
    list_fields=["name", "price", "stock", "category"],
    search_fields=["name", "description", "sku"],
    sortable_fields=["name", "price", "created_at"],
    
    table_view=TableViewConfig(
        per_page=50,
        default_sort=[("created_at", -1)],
        enable_bulk_actions=True,
        enable_export=True
    )
))
```

### With Authentication

```python
from monglo.auth import SimpleAuthProvider
import hashlib

# Create auth provider
password_hash = hashlib.sha256("your_secure_password".encode()).hexdigest()
auth = SimpleAuthProvider(users={
    "admin": {"password": password_hash, "role": "admin"}
})

# Use with engine
engine = MongloEngine(
    database=db,
    auto_discover=True,
    auth_provider=auth
)
```

### Selective Auto-Discovery

```python
# Don't auto-discover everything
engine = MongloEngine(database=db, auto_discover=False)
await engine.initialize()

# Only register specific collections
await engine.register_collection("users")
await engine.register_collection("products")
await engine.register_collection("orders")
```

---

## API Usage Examples

### List Documents with Filters

```bash
# Basic list
curl "http://localhost:8000/api/admin/products?page=1&per_page=20"

# With search
curl "http://localhost:8000/api/admin/products?search=laptop"

# With sorting
curl "http://localhost:8000/api/admin/products?sort=price:desc"

# Combined
curl "http://localhost:8000/api/admin/products?search=laptop&sort=price:desc&page=1"
```

### Create Document

```bash
curl -X POST "http://localhost:8000/api/admin/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Product",
    "price": 99.99,
    "stock": 100
  }'
```

### Update Document

```bash
curl -X PUT "http://localhost:8000/api/admin/products/507f1f77bcf86cd799439011" \
  -H "Content-Type: application/json" \
  -d '{"price": 89.99}'
```

### Delete Document

```bash
curl -X DELETE "http://localhost:8000/api/admin/products/507f1f77bcf86cd799439011"
```

---

## Query Parameters

### List Endpoint

- `page` (int, default=1) - Page number
- `per_page` (int, default=20, max=100) - Results per page
- `search` (str) - Search query across configured fields
- `sort` (str) - Sort specification (e.g., `name:asc`, `price:desc`)

### Response Format

```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "pages": 8,
  "per_page": 20,
  "has_next": true,
  "has_prev": false
}
```

---

## Advanced Features

### Custom Relationships

```python
from monglo.core.relationships import Relationship, RelationshipType

await engine.register_collection("comments", config=CollectionConfig(
    relationships=[
        Relationship(
            source_collection="comments",
            source_field="post_id",
            target_collection="posts",
            type=RelationshipType.ONE_TO_ONE,
            reverse_name="comments"  # Bidirectional
        )
    ]
))
```

### Custom Widgets

```python
from monglo.widgets import Select, DatePicker
from monglo.fields import Field

config = CollectionConfig(
    fields=[
        Field(
            name="status",
            widget=Select(choices=[
                ("draft", "Draft"),
                ("published", "Published")
            ])
        ),
        Field(
            name="publish_date",
            widget=DatePicker(format="YYYY-MM-DD")
        )
    ]
)
```

### Export to CSV

```python
from monglo.operations.export import ExportOperations

export_ops = ExportOperations(collection_admin)
csv_data = await export_ops.to_csv(filters={"status": "active"})
```

---

## Production Deployment

### With Gunicorn + Uvicorn

```bash
# Install workers
pip install gunicorn uvicorn[standard]

# Run with multiple workers
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

```python
import os

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "myapp")

client = AsyncIOMotorClient(MONGODB_URI)
engine = MongloEngine(database=client[DATABASE_NAME])
```

---

## Complete Example

See [`examples/simple_fastapi_example/app.py`](../../examples/simple_fastapi_example/app.py) for a minimal working example.

See [`examples/fastapi_example/app.py`](../../examples/fastapi_example/app.py) for a full-featured example with:
- Data seeding
- Custom configurations
- Relationship detection demo
- All CRUD operations

---

## Next Steps

- [Core Concepts](../core-concepts/relationships.md) - Understanding relationships
- [Custom Fields](../guides/custom-fields.md) - Field types and widgets
- [Security](../guides/security.md) - Authentication and permissions
- [Deployment](../guides/deployment.md) - Production best practices
