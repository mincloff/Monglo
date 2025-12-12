# Monglo Examples - Overview

All examples demonstrate how **the library does the heavy lifting** while you write minimal code.

## ⚡ Quick Start Examples (5 Minutes)

### 1. [FastAPI Minimal](simple_fastapi_example/) - **RECOMMENDED**
**10 lines of code** → Full admin interface

```python
engine = MongloEngine(database=db, auto_discover=True)
await engine.initialize()
app.include_router(create_ui_router(engine))
```

**What you get:**
- Complete REST API
- Professional admin UI
- Auto-detected schemas
- Relationship navigation
- Search, filter, sort
- CRUD operations

### 2. [Flask Minimal](flask_minimal/)
Same features as FastAPI, Flask version.

### 3. [Starlette Minimal](starlette_minimal/)
Lightweight Starlette version.

## 🚀 Advanced Examples

### 4. [Advanced Features](advanced_example/)
Shows the clear separation between library and application:

**Library Handles (Automatic):**
- All routing
- All UI
- All serialization
- Schema detection
- CRUD operations

**You Write (Business Logic):**
- Auth rules
- Custom validations
- Business logic
- Custom actions

## 📖 Guides

### [Configuration Guide](CONFIGURATION_GUIDE.md)
High-level customization without boilerplate:
- Branding (logo, colors)
- Collection display settings
- Authentication setup
- Field customization

## Key Philosophy

### ❌ Traditional Approach
```
Developer writes: Routes + Templates + Serialization + Forms + Validation + UI
Library provides: ORM wrapper
Result: 300+ lines of boilerplate
```

### ✅ Monglo Approach
```
Developer writes: Business logic only (10 lines)
Library provides: Everything else
Result: Professional admin in 5 minutes
```

## Feature Comparison

| Feature | Without Monglo | With Monglo |
|---------|---------------|-------------|
| Routes | Manual (50+ lines) | Auto-generated |
| UI | Build from scratch | Professional built-in |
| Serialization | Manual code | Automatic |
| Relationships | Manual config | Auto-detected |
| Search | Implement yourself | Built-in |
| Validation | Write validators | Built-in |
| Auth | Roll your own | Simple config |
| **Total Time** | **Hours/Days** | **5 Minutes** |

## Running Examples

Each example has its own README with instructions. General pattern:

```bash
cd examples/[example-name]
pip install -e "../../[framework]"
python app.py
```

Visit `http://localhost:8000/admin` (or :5000 for Flask)

## What Makes Monglo Different?

1. **Auto-Discovery** - Scans your database, no manual schemas
2. **Smart Relationships** - Detects `user_id` → `users` automatically  
3. **Complete UI** - Professional interface included, not just API
4. **Framework Agnostic** - Works with FastAPI, Flask, Django, Starlette
5. **Production Ready** - ACID transactions, audit logs, validation

## Next Steps

Start with [FastAPI Minimal](simple_fastapi_example/) → See it work → Customize as needed!
