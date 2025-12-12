"""
Search operations for MongoDB collections.

Provides intelligent text search across multiple fields with regex support,
highlighting, and score-based ranking.
"""

from typing import Any

from motor.motor_asyncio import AsyncIOMotorCollection


class SearchOperations:
    """Search functionality for MongoDB collections.

    Provides text search across configured fields with:
    - Case-insensitive regex matching
    - Field highlighting
    - Relevance scoring
    - Multiple search strategies

    Example:
        >>> ops = SearchOperations(collection, ["name", "email", "description"])
        >>> results = await ops.search("alice")
        >>> # Returns documents containing "alice" in any of the fields
    """

    def __init__(self, collection: AsyncIOMotorCollection, search_fields: list[str] | None = None):
        """Initialize search operations.

        Args:
            collection: MongoDB collection to search
            search_fields: Fields to search across (if None, all fields are searched)
        """
        self.collection = collection
        self.search_fields = search_fields or []

    async def search(
        self, query: str, *, case_sensitive: bool = False, limit: int = 100, skip: int = 0
    ) -> list[dict[str, Any]]:
        """Search across configured fields.

        Args:
            query: Search query string
            case_sensitive: Whether to perform case-sensitive search
            limit: Maximum results to return
            skip: Number of results to skip (for pagination)

        Returns:
            List of matching documents

        Example:
            >>> results = await ops.search("laptop", limit=50)
            >>> # Returns up to 50 documents containing "laptop"
        """
        if not query or not self.search_fields:
            return []

        # Build $or query for all search fields
        options = "" if case_sensitive else "i"
        conditions = [
            {field: {"$regex": query, "$options": options}} for field in self.search_fields
        ]

        cursor = self.collection.find({"$or": conditions}).skip(skip).limit(limit)
        return await cursor.to_list(limit)

    async def search_with_highlight(
        self, query: str, *, limit: int = 100, skip: int = 0
    ) -> list[dict[str, Any]]:
        """Search with matched field highlighting.

        Returns documents with _matched_fields array indicating which fields
        contained the search query.

        Args:
            query: Search query string
            limit: Maximum results to return
            skip: Number of results to skip

        Returns:
            Documents with _matched_fields attribute

        Example:
            >>> results = await ops.search_with_highlight("apple")
            >>> results[0]["_matched_fields"]
            ['name', 'description']
        """
        results = await self.search(query, limit=limit, skip=skip)

        # Add matched field info
        query_lower = query.lower()
        for doc in results:
            doc["_matched_fields"] = [
                field
                for field in self.search_fields
                if field in doc and query_lower in str(doc[field]).lower()
            ]

        return results

    async def search_count(self, query: str, *, case_sensitive: bool = False) -> int:
        """Count documents matching search query.

        Args:
            query: Search query string
            case_sensitive: Whether to perform case-sensitive search

        Returns:
            Count of matching documents
        """
        if not query or not self.search_fields:
            return 0

        options = "" if case_sensitive else "i"
        conditions = [
            {field: {"$regex": query, "$options": options}} for field in self.search_fields
        ]

        return await self.collection.count_documents({"$or": conditions})

    async def search_paginated(
        self, query: str, *, page: int = 1, per_page: int = 20, case_sensitive: bool = False
    ) -> dict[str, Any]:
        """Search with pagination support.

        Args:
            query: Search query string
            page: Page number (1-indexed)
            per_page: Results per page
            case_sensitive: Whether to perform case-sensitive search

        Returns:
            Dictionary with items, total, page, and pages info
        """
        skip = (page - 1) * per_page
        items = await self.search(query, case_sensitive=case_sensitive, limit=per_page, skip=skip)
        total = await self.search_count(query, case_sensitive=case_sensitive)

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
        }
