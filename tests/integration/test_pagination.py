"""
Integration tests for pagination.

Tests cursor and offset pagination strategies.
"""

import pytest
from monglo.operations.pagination import PaginationHelper


@pytest.mark.integration
@pytest.mark.asyncio
async def test_offset_pagination(test_db):
    """Test offset-based pagination."""
    # Insert test data
    test_docs = [{"value": i} for i in range(100)]
    await test_db.items.insert_many(test_docs)
    
    pag = PaginationHelper(test_db.items)
    
    # Test first page
    page1 = await pag.paginate_offset(page=1, per_page=20)
    assert len(page1["items"]) == 20
    assert page1["total"] == 100
    assert page1["page"] == 1
    assert page1["pages"] == 5
    assert page1["has_next"] is True
    assert page1["has_prev"] is False
    
    # Test middle page
    page3 = await pag.paginate_offset(page=3, per_page=20)
    assert len(page3["items"]) == 20
    assert page3["page"] == 3
    assert page3["has_next"] is True
    assert page3["has_prev"] is True
    
    # Test last page
    page5 = await pag.paginate_offset(page=5, per_page=20)
    assert len(page5["items"]) == 20
    assert page5["page"] == 5
    assert page5["has_next"] is False
    assert page5["has_prev"] is True


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cursor_pagination(test_db):
    """Test cursor-based pagination."""
    from bson import ObjectId
    
    # Insert test data with known IDs
    test_ids = [ObjectId() for _ in range(50)]
    test_docs = [{"_id": test_ids[i], "value": i} for i in range(50)]
    await test_db.items.insert_many(test_docs)
    
    pag = PaginationHelper(test_db.items)
    
    # First page (no cursor)
    page1 = await pag.paginate_cursor(per_page=15)
    assert len(page1["items"]) == 15
    assert page1["has_next"] is True
    assert page1["next_cursor"] is not None
    
    # Second page using cursor
    page2 = await pag.paginate_cursor(
        per_page=15,
        cursor=page1["next_cursor"]
    )
    assert len(page2["items"]) == 15
    assert page2["has_next"] is True
    
    # Verify no overlap
    page1_ids = {doc["_id"] for doc in page1["items"]}
    page2_ids = {doc["_id"] for doc in page2["items"]}
    assert len(page1_ids & page2_ids) == 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pagination_with_filtering(test_db):
    """Test pagination combined with filters."""
    # Insert mixed data
    await test_db.items.insert_many([
        *[{"category": "A", "value": i} for i in range(30)],
        *[{"category": "B", "value": i} for i in range(30)]
    ])
    
    pag = PaginationHelper(test_db.items)
    
    # Paginate filtered results
    page1 = await pag.paginate_offset(
        page=1,
        per_page=10,
        query={"category": "A"}
    )
    
    assert page1["total"] == 30
    assert len(page1["items"]) == 10
    assert all(doc["category"] == "A" for doc in page1["items"])


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pagination_with_sorting(test_db):
    """Test pagination with custom sorting."""
    # Insert unsorted data
    import random
    values = list(range(50))
    random.shuffle(values)
    await test_db.items.insert_many([{"value": v} for v in values])
    
    pag = PaginationHelper(test_db.items)
    
    # Paginate with descending sort
    page1 = await pag.paginate_offset(
        page=1,
        per_page=10,
        sort=[("value", -1)]
    )
    
    # Should be sorted descending
    page1_values = [doc["value"] for doc in page1["items"]]
    assert page1_values == sorted(page1_values, reverse=True)
    
    # Continue to page 2
    page2 = await pag.paginate_offset(
        page=2,
        per_page=10,
        sort=[("value", -1)]
    )
    
    # Page 2 values should all be less than page 1's minimum
    page2_values = [doc["value"] for doc in page2["items"]]
    assert max(page2_values) < min(page1_values)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pagination_edge_cases(test_db):
    """Test pagination edge cases."""
    # Insert 25 documents
    await test_db.items.insert_many([{"value": i} for i in range(25)])
    
    pag = PaginationHelper(test_db.items)
    
    # Test requesting beyond last page
    page10 = await pag.paginate_offset(page=10, per_page=10)
    assert page10["items"] == []
    assert page10["page"] == 10
    assert page10["total"] == 25
    assert page10["has_next"] is False
    
    # Test per_page larger than total
    page1_big = await pag.paginate_offset(page=1, per_page=100)
    assert len(page1_big["items"]) == 25
    assert page1_big["pages"] == 1
    
    # Test per_page = 1
    page1_single = await pag.paginate_offset(page=1, per_page=1)
    assert len(page1_single["items"]) == 1
    assert page1_single["pages"] == 25


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pagination_metadata_accuracy(test_db):
    """Test pagination metadata calculations."""
    # Insert 47 documents (prime number for interesting division)
    await test_db.items.insert_many([{"value": i} for i in range(47)])
    
    pag = PaginationHelper(test_db.items)
    
    # Test with per_page=10
    page1 = await pag.paginate_offset(page=1, per_page=10)
    assert page1["total"] == 47
    assert page1["pages"] == 5  # Ceiling of 47/10
    assert page1["per_page"] == 10
    
    # Last page should have only 7 items
    page5 = await pag.paginate_offset(page=5, per_page=10)
    assert len(page5["items"]) == 7
    assert page5["has_next"] is False
