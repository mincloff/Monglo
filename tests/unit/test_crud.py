"""
Unit tests for CRUD operations.

Tests all CRUD functionality including bulk operations.
"""

import pytest
from bson import ObjectId
from monglo.operations.crud import CRUDOperations
from monglo.core.registry import CollectionAdmin
from monglo.core.config import CollectionConfig


@pytest.fixture
async def crud_ops(test_db):
    """Create CRUD operations instance."""
    collection = test_db.test_collection
    config = CollectionConfig(
        search_fields=["name", "email"],
        list_fields=["name", "email", "status"]
    )
    admin = CollectionAdmin("test_collection", test_db, config)
    return CRUDOperations(admin)


@pytest.fixture
async def sample_doc():
    """Sample document for testing."""
    return {
        "name": "John Doe",
        "email": "john@example.com",
        "status": "active",
        "age": 30
    }


class TestCRUDCreate:
    """Test create operations."""
    
    async def test_create_document(self, crud_ops, sample_doc):
        """Test creating a single document."""
        result = await crud_ops.create(sample_doc)
        
        assert "_id" in result
        assert result["name"] == "John Doe"
        assert result["email"] == "john@example.com"
    
    async def test_create_empty_fails(self, crud_ops):
        """Test that creating empty document fails."""
        with pytest.raises(ValueError):
            await crud_ops.create({})
    
    async def test_bulk_create(self, crud_ops):
        """Test bulk create operation."""
        docs = [
            {"name": f"User {i}", "email": f"user{i}@example.com"}
            for i in range(10)
        ]
        
        result = await crud_ops.bulk_create(docs)
        
        assert len(result) == 10
        assert all("_id" in doc for doc in result)


class TestCRUDRead:
    """Test read operations."""
    
    async def test_get_document(self, crud_ops, sample_doc):
        """Test getting a document by ID."""
        created = await crud_ops.create(sample_doc)
        doc_id = str(created["_id"])
        
        result = await crud_ops.get(doc_id)
        
        assert result["name"] == "John Doe"
        assert result["email"] == "john@example.com"
    
    async def test_get_nonexistent_fails(self, crud_ops):
        """Test that getting nonexistent document fails."""
        fake_id = str(ObjectId())
        
        with pytest.raises(KeyError):
            await crud_ops.get(fake_id)
    
    async def test_list_documents(self, crud_ops):
        """Test listing documents with pagination."""
        # Create test data
        docs = [{"name": f"User {i}"} for i in range(25)]
        await crud_ops.bulk_create(docs)
        
        # Test pagination
        result = await crud_ops.list(page=1, per_page=10)
        
        assert result["total"] == 25
        assert len(result["items"]) == 10
        assert result["pages"] == 3
        assert result["has_next"] is True
        assert result["has_prev"] is False
    
    async def test_list_with_search(self, crud_ops):
        """Test listing with search."""
        docs = [
            {"name": "Alice", "email": "alice@example.com"},
            {"name": "Bob", "email": "bob@example.com"},
            {"name": "Alice Cooper", "email": "cooper@example.com"}
        ]
        await crud_ops.bulk_create(docs)
        
        result = await crud_ops.list(search="Alice")
        
        assert result["total"] == 2
        assert all("Alice" in item["name"] for item in result["items"])
    
    async def test_count(self, crud_ops):
        """Test document count."""
        docs = [{"name": f"User {i}"} for i in range(15)]
        await crud_ops.bulk_create(docs)
        
        count = await crud_ops.count()
        assert count == 15
        
        count_filtered = await crud_ops.count({"name": "User 5"})
        assert count_filtered == 1
    
    async def test_exists(self, crud_ops, sample_doc):
        """Test document existence check."""
        created = await crud_ops.create(sample_doc)
        doc_id = str(created["_id"])
        
        assert await crud_ops.exists(doc_id) is True
        assert await crud_ops.exists(str(ObjectId())) is False


class TestCRUDUpdate:
    """Test update operations."""
    
    async def test_update_partial(self, crud_ops, sample_doc):
        """Test partial update."""
        created = await crud_ops.create(sample_doc)
        doc_id = str(created["_id"])
        
        result = await crud_ops.update(doc_id, {"status": "inactive"})
        
        assert result["status"] == "inactive"
        assert result["name"] == "John Doe"  # Other fields unchanged
    
    async def test_update_full_replacement(self, crud_ops, sample_doc):
        """Test full document replacement."""
        created = await crud_ops.create(sample_doc)
        doc_id = str(created["_id"])
        
        new_doc = {"name": "Jane Doe", "email": "jane@example.com"}
        result = await crud_ops.update(doc_id, new_doc, partial=False)
        
        assert result["name"] == "Jane Doe"
        assert "status" not in result  # Old field removed
    
    async def test_update_nonexistent_fails(self, crud_ops):
        """Test that updating nonexistent document fails."""
        fake_id = str(ObjectId())
        
        with pytest.raises(KeyError):
            await crud_ops.update(fake_id, {"name": "Test"})
    
    async def test_bulk_update(self, crud_ops):
        """Test bulk update operation."""
        # Create test data
        docs = [{"status": "pending"} for _ in range(5)]
        await crud_ops.bulk_create(docs)
        
        # Bulk update
        updates = [{
            "filter": {"status": "pending"},
            "update": {"$set": {"status": "active"}}
        }]
        
        result = await crud_ops.bulk_update(updates)
        
        assert result["matched"] == 5
        assert result["modified"] == 5


class TestCRUDDelete:
    """Test delete operations."""
    
    async def test_delete_document(self, crud_ops, sample_doc):
        """Test deleting a document."""
        created = await crud_ops.create(sample_doc)
        doc_id = str(created["_id"])
        
        deleted = await crud_ops.delete(doc_id)
        
        assert deleted is True
        assert await crud_ops.exists(doc_id) is False
    
    async def test_delete_nonexistent(self, crud_ops):
        """Test deleting nonexistent document."""
        fake_id = str(ObjectId())
        deleted = await crud_ops.delete(fake_id)
        
        assert deleted is False
    
    async def test_bulk_delete(self, crud_ops):
        """Test bulk delete operation."""
        # Create test data
        docs = [{"name": f"User {i}"} for i in range(10)]
        created = await crud_ops.bulk_create(docs)
        
        # Get IDs
        ids = [str(doc["_id"]) for doc in created[:5]]
        
        # Bulk delete
        deleted_count = await crud_ops.bulk_delete(ids)
        
        assert deleted_count == 5
        assert await crud_ops.count() == 5


class TestCRUDEdgeCases:
    """Test edge cases and error handling."""
    
    async def test_invalid_object_id(self, crud_ops):
        """Test handling invalid ObjectId."""
        with pytest.raises(ValueError):
            await crud_ops.get("invalid-id")
    
    async def test_empty_bulk_create(self, crud_ops):
        """Test bulk create with empty list."""
        result = await crud_ops.bulk_create([])
        assert result == []
    
    async def test_empty_bulk_delete(self, crud_ops):
        """Test bulk delete with empty list."""
        result = await crud_ops.bulk_delete([])
        assert result == 0
