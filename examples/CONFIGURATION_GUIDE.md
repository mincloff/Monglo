# High-Level Configuration

Shows how to customize Monglo at a high level WITHOUT writing boilerplate.

## What You CAN Customize (High-Level)

### 1. Branding
```python
create_ui_router(
    engine,
    title="My Company Admin",
    logo="https://mycompany.com/logo.png",
    brand_color="#ff6b6b"  # Your brand color
)
```

### 2. Collection Display
```python
from monglo import CollectionConfig

await engine.register_collection(
    "products",
    config=CollectionConfig(
        display_name="Products",  # Human-readable name
        list_fields=["name", "price", "stock"],  # Which fields to show in table
        search_fields=["name", "description", "sku"],  # Which fields are searchable
    )
)
```

### 3. Authentication
```python
from monglo.auth import SimpleAuthProvider

auth = SimpleAuthProvider(users={
    "admin": {"password_hash": "...", "role": "admin"},
    "viewer": {"password_hash": "...", "role": "readonly"}
})

engine = MongloEngine(database=db, auth_provider=auth)
```

### 4. Field Customization
```python
from monglo.fields import StringField, NumberField

config = CollectionConfig(
    fields={
        "email": StringField(required=True),
        "age": NumberField(min_value=0, max_value=150)
    }
)
```

## What You DON'T Need to Touch (Library Handles)

❌ Routing - Auto-generated  
❌ Templates - Built-in  
❌ Serialization - Automatic  
❌ Validation - Built-in  
❌ Error handling - Included  
❌ UI components - Pre-built  
❌ API endpoints - Auto-created  

## Philosophy

**High-level configuration**: Logo, colors, field lists  
**Low-level automation**: Everything else

You customize **what** to show, library handles **how** to show it.

## Example: Complete Customization

```python
from monglo import MongloEngine, CollectionConfig
from monglo.auth import SimpleAuthProvider

# Your preferences (high-level)
engine = MongloEngine(
    database=db,
    auto_discover=True,
    auth_provider=SimpleAuthProvider(users=my_users)
)

await engine.register_collection(
    "products",
    config=CollectionConfig(
        display_name="Product Catalog",
        list_fields=["name", "price", "stock", "category"],
        search_fields=["name", "description", "sku"]
    )
)

# Library handles the rest (routing, UI, CRUD, etc.)
app.include_router(create_ui_router(
    engine,
    title="My Store Admin",
    brand_color="#2563eb"
))
```

**Result**: Professional admin interface customized to your needs, zero boilerplate!
