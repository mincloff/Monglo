# Monglo Tests

This directory contains comprehensive tests for Monglo.

## Test Structure

```
tests/
├── conftest.py           # Shared fixtures and configuration
├── unit/                 # Unit tests (fast, no external dependencies)
│   ├── test_config.py
│   ├── test_relationships.py
│   ├── test_introspection.py
│   ├── test_query_builder.py
│   └── test_serializers.py
├── integration/          # Integration tests (requires MongoDB)
│   ├── test_crud_operations.py
│   ├── test_search_filter.py
│   ├── test_pagination.py
│   └── test_relationship_resolution.py
├── adapters/             # Framework adapter tests
│   ├── test_fastapi_adapter.py
│   └── test_flask_adapter.py
└── e2e/                  # End-to-end tests
    ├── test_table_view_workflow.py
    └── test_document_view_workflow.py
```

## Running Tests

### All Tests
```bash
pytest
```

###  Unit Tests Only (fast)
```bash
pytest tests/unit -v
```

### Integration Tests (requires MongoDB)
```bash
pytest tests/integration -v
```

### With Coverage
```bash
pytest --cov=monglo --cov-report=html --cov-report=term
open htmlcov/index.html
```

### Specific Test File
```bash
pytest tests/unit/test_config.py -v
```

### Specific Test Function
```bash
pytest tests/unit/test_config.py::TestCollectionConfig::test_from_schema_factory -v
```

## Test Markers

- `@pytest.mark.unit` - Fast unit tests
- `@pytest.mark.integration` - Integration tests requiring MongoDB
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.requires_mongodb` - Tests that need MongoDB connection

Filter by marker:
```bash
pytest -m unit          # Run only unit tests
pytest -m integration   # Run only integration tests
pytest -m "not slow"    # Skip slow tests
```

## MongoDB Setup for Tests

Tests use a separate test database that is created and destroyed for each test.

### Default Connection
```bash
# Uses mongodb://localhost:27017 by default
pytest tests/integration
```

### Custom MongoDB URI
```bash
export MONGODB_TEST_URI="mongodb://localhost:27018"
pytest tests/integration
```

### Using Docker
```bash
# Start MongoDB in Docker
docker run -d -p 27017:27017 --name monglo-test mongo:7.0

# Run tests
pytest

# Cleanup
docker stop monglo-test && docker rm monglo-test
```

## Fixtures

### Database Fixtures
- `mongodb_client` - MongoDB client (session scope)
- `test_db` - Clean test database (function scope, auto-cleanup)

### Sample Data
- `sample_users` - 3 user documents
- `sample_orders` - 3 order documents (with user references)
- `sample_products` - 3 product documents

### Engine Fixtures
- `monglo_engine` - Basic engine instance
- `registered_engine` - Engine with collections registered

### Utilities
- `test_data_factory` - Factory for creating test documents

## Writing Tests

### Unit Test Example
```python
import pytest
from monglo.core.config import CollectionConfig

def test_collection_config_defaults():
    config = CollectionConfig()
    assert config.actions == ["create", "edit", "delete"]
```

### Integration Test Example
```python
import pytest
from bson import ObjectId

@pytest.mark.integration
@pytest.mark.requires_mongodb
async def test_user_crud(test_db, monglo_engine):
    await monglo_engine.register_collection("users")
    admin = monglo_engine.registry.get("users")
    
    # Create
    user_id = ObjectId()
    await admin.collection.insert_one({
        "_id": user_id,
        "name": "Test User"
    })
    
    # Read
    user = await admin.collection.find_one({"_id": user_id})
    assert user["name"] == "Test User"
```

### Using Fixtures
```python
@pytest.mark.integration
async def test_with_sample_data(registered_engine, sample_users):
    users_admin = registered_engine.registry.get("users")
    count = await users_admin.collection.count_documents({})
    assert count == len(sample_users)
```

## Coverage Goals

- **Unit Tests**: > 90% coverage
- **Integration Tests**: Cover critical paths
- **Overall**: > 85% coverage

Check current coverage:
```bash
pytest --cov=monglo --cov-report=term-missing
```
