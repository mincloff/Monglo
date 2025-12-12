# FastAPI Example - Truly Minimal Setup

## What You're Looking At

**5 lines of application code** = Full MongoDB admin interface

## Installation

```bash
pip install monglo[fastapi]
# or manually:
pip install monglo motor fastapi uvicorn
```

## The Code

Look at [`app.py`](./app.py) - it's just:

```python
client = AsyncIOMotorClient("mongodb://localhost:27017")
engine = MongloEngine(database=db, auto_discover=True)
await engine.initialize()
app.include_router(create_ui_router(engine))
```

**That's it. Seriously.**

## What the Library Does Automatically

### 🔍 Auto-Discovery
✅ Scans all collections  
✅ Infers field types  
✅ Detects relationships (`user_id` → `users`)  
✅ Generates schemas

### 🎨 Complete UI
✅ Professional admin interface  
✅ Table view (sortable, filterable, searchable)  
✅ Document view (JSON tree, nested docs)  
✅ Sidebar navigation  
✅ Dark mode toggle

### 📡 REST API
✅ `GET /api/{collection}` - List documents  
✅ `GET /api/{collection}/{id}` - Get document  
✅ `POST /api/{collection}` - Create document  
✅ `PUT /api/{collection}/{id}` - Update document  
✅ `DELETE /api/{collection}/{id}` - Delete document

### ⚙️ All the Hard Stuff
✅ Templates (bundled in library)  
✅ Static files (CSS, JS)  
✅ Jinja2 filters (datetime, truncate, etc.)  
✅ Serialization (ObjectId, datetime, etc.)  
✅ Routing (all UI and API routes)  
✅ Error handling  
✅ Pagination  
✅ Search  

## Run It

```bash
cd examples/fastapi_example
python app.py
```

Open your browser:
- **Admin UI**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/docs

## Comparison

### ❌ Without Monglo (Typical Setup)

```python
# Define Pydantic models for every collection
class User(BaseModel):
    name: str
    email: str
    # ... 50 more lines

# Define routes for every operation
@app.get("/users")
async def list_users(...):
    # ... 30 lines

@app.post("/users")
async def create_user(...):
    # ... 40 lines

# Setup templates
templates = Jinja2Templates(...)
# Add filters
templates.env.filters['format_datetime'] = ...
# ... 100 more lines

# Create UI routes
@app.get("/admin/users")
async def users_page(...):
    # ... 50 lines

# And on and on...
```

**Total: 500+ lines of boilerplate**

### ✅ With Monglo

```python
engine = MongloEngine(database=db, auto_discover=True)
await engine.initialize()
app.include_router(create_ui_router(engine))
```

**Total: 3 lines**

## What Makes This Possible?

1. **Auto-Detection**: Library scans your database and understands structure
2. **Bundled UI**: Templates and assets are packaged with the library
3. **Smart Defaults**: Everything works out of the box
4. **Convention Over Configuration**: Follows MongoDB best practices

## Customization (Optional!)

You don't need to customize anything, but if you want to:

```python
# Custom branding
app.include_router(create_ui_router(
    engine,
    title="My Admin Panel",
    logo="https://example.com/logo.png",
    brand_color="#ff6b6b"
))

# Custom collection config
await engine.register_collection(
    "products",
    config=CollectionConfig(
        list_fields=["name", "price", "stock"],
        search_fields=["name", "description"]
    )
)
```

But you don't have to! The defaults work perfectly.

## This Is The Library's Promise

**You write**: Business logic  
**Library handles**: Everything else

No templates. No serialization. No routing. No configuration.  
Just instantiate and go.

## Next Steps

- See [Advanced Example](../advanced_example/) for auth, audit logging, transactions
- Read [Configuration Guide](../CONFIGURATION_GUIDE.md)
- Check [Full Documentation](../../docs/)
