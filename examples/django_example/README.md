# Django Example - Truly Minimal Setup

## What You're Looking At

**Django + Monglo** = Full MongoDB admin interface with minimal code

## Installation

```bash
pip install monglo[django]
# or manually:
pip install monglo motor django uvicorn
```

## The Code

Look at [`monglo_admin/urls.py`](./monglo_admin/urls.py) - it's just:

```python
client = AsyncIOMotorClient("mongodb://localhost:27017")
engine = MongloEngine(database=db, auto_discover=True)
await engine.initialize()

urlpatterns = [
    *create_ui_urlpatterns(engine, prefix="admin"),
    *create_django_urls(engine, prefix="api"),
]
```

**That's it. Seriously.**

## What the Library Does Automatically

### 🔍 Auto-Discovery
✅ Scans all collections  
✅ Infers field types  
✅ Detects relationships  
✅ Generates schemas

### 🎨 Complete UI
✅ Professional admin interface  
✅ Table view (sortable, filterable, searchable)  
✅ Document view (JSON tree)  
✅ Complete URL patterns

### 📡 REST API
✅ All CRUD endpoints auto-generated  
✅ Class-based views  
✅ Async support  
✅ JSON responses

### ⚙️ All the Hard Stuff
✅ Templates (bundled)  
✅ Views (auto-generated)  
✅ URL patterns (auto-generated)  
✅ Serialization  
✅ Error handling

## Run It

```bash
cd examples/django_example

# Run with uvicorn (ASGI server for async support)
uvicorn monglo_admin.asgi:application --reload

# Or use Django's development server
python manage.py runserver
```

Open your browser:
- **Admin UI**: http://localhost:8000/admin
- **API**: http://localhost:8000/api

## Project Structure

```
django_example/
├── monglo_admin/
│   ├── __init__.py
│   ├── settings.py    # Minimal Django settings
│   ├── urls.py        # THIS is where Monglo magic happens!
│   └── asgi.py        # ASGI config for async
├── manage.py
└── README.md
```

## Comparison

### ❌ Without Monglo (Typical Django)

```python
# Define models for every collection
class User(models.Model):
    name = models.CharField(...)
    # ... 30 more lines

# Register with admin
admin.site.register(User, UserAdmin)

# Or create custom views
class UserViewSet(viewsets.ModelViewSet):
    # ... 50 more lines

# URLs
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]

# And still no MongoDB support!
```

**Total: 200+ lines + Django admin limitations**

### ✅ With Monglo

```python
engine = MongloEngine(database=db, auto_discover=True)
await engine.initialize()

urlpatterns = [
    *create_ui_urlpatterns(engine),
]
```

**Total: 3 lines + Full MongoDB support**

## Features

All these work out of the box:
- ✅ MongoDB collections (not SQL models!)
- ✅ Async operations  
- ✅ Relationship detection  
- ✅ Auto-generated views  
- ✅ Search, filter, sort  
- ✅ Professional UI  
- ✅ Complete REST API  

## Customization (Optional!)

```python
# Custom branding
urlpatterns = [
    *create_ui_urlpatterns(
        engine,
        title="My Admin Panel",
        brand_color="#ff6b6b"
    ),
]

# Custom collection config
await engine.register_collection(
    "products",
    config=CollectionConfig(
        list_fields=["name", "price", "stock"]
    )
)
```

## Why Django + Monglo?

- **Django Admin** doesn't support MongoDB natively
- **MongoEngine** requires model definitions
- **Monglo** just works with your existing MongoDB

## Next Steps

- See [FastAPI Example](../fastapi_example/) for comparison  
- Check [Advanced Example](../advanced_example/) for auth, audit logging
- Read [Full Documentation](../../docs/)

## Note on Async

Django has async support (since 3.1), but Monglo uses Motor which is fully async.  
We recommend using an ASGI server like `uvicorn` or `daphne` for best performance.

```bash
# Best performance (recommended)
uvicorn monglo_admin.asgi:application --reload

# Standard Django (works but may be slower)
python manage.py runserver
```
