"""
Pagination handlers for MongoDB collections.

Provides offset-based and cursor-based pagination strategies.
"""

from typing import Any, Literal
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection


class PaginationHandler:
    """Base pagination handler with multiple strategies.
    
    Supports both offset-based (skip/limit) and cursor-based pagination
    for different use cases and performance requirements.
    
    Example:
        >>> handler = PaginationHandler(collection)
        >>> result = await handler.paginate_offset(query, page=1, per_page=20)
        >>> result = await handler.paginate_cursor(query, cursor=None, per_page=20)
    """
    
    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        """Initialize pagination handler.
        
        Args:
            collection: MongoDB collection instance
        """
        self.collection = collection
    
    async def paginate_offset(
        self,
        query: dict[str, Any],
        *,
        page: int = 1,
        per_page: int = 20,
        sort: list[tuple[str, int]]  | None = None,
        projection: dict[str, int] | None = None
    ) -> dict[str, Any]:
        """Paginate using offset-based strategy (skip/limit).
        
        Good for: Small to medium collections, random page access
        Not ideal for: Very large collections, real-time data
        
        Args:
            query: MongoDB query filter
            page: Page number (1-indexed)
            per_page: Items per page
            sort: Sort specification
            projection: Fields to include/exclude
            
        Returns:
            Dictionary with items and pagination metadata
            
        Example:
            >>> result = await handler.paginate_offset(
            ...     {"status": "active"},
            ...     page=2,
            ...     per_page=20,
            ...     sort=[("created_at", -1)]
            ... )
        """
        # Validate inputs
        page = max(1, page)
        per_page = max(1, min(per_page, 100))
        
        # Calculate skip/limit
        skip = (page - 1) * per_page
        
        # Get total count
        total = await self.collection.count_documents(query)
        
        # Build cursor
        cursor = self.collection.find(query, projection or {})
        
        if sort:
            cursor = cursor.sort(sort)
        
        # Get items
        items = await cursor.skip(skip).limit(per_page).to_list(per_page)
        
        # Calculate metadata
        total_pages = (total + per_page - 1) // per_page if per_page > 0 else 1
        
        return {
            "items": items,
            "pagination": {
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
                "strategy": "offset"
            }
        }
    
    async def paginate_cursor(
        self,
        query: dict[str, Any],
        *,
        cursor: str | None = None,
        per_page: int = 20,
        sort_field: str = "_id",
        sort_direction: int = 1,
        projection: dict[str, int] | None = None
    ) -> dict[str, Any]:
        """Paginate using cursor-based strategy.
        
        Good for: Large collections, real-time data, infinite scroll
        Not ideal for: Random page access, page numbers
        
        Args:
            query: MongoDB query filter
            cursor: Cursor value (last item's sort field value)
            per_page: Items per page
            sort_field: Field to use for cursor (must be indexed)
            sort_direction: 1 for ascending, -1 for descending
            projection: Fields to include/exclude
            
        Returns:
            Dictionary with items, next cursor, and metadata
            
        Example:
            >>> # First page
            >>> result = await handler.paginate_cursor(
            ...     {"status": "active"},
            ...     cursor=None,
            ...     per_page=20
            ... )
            >>> 
            >>> # Next page
            >>> next_result = await handler.paginate_cursor(
            ...     {"status": "active"},
            ...     cursor=result["pagination"]["next_cursor"],
            ...     per_page=20
            ... )
        """
        # Validate inputs
        per_page = max(1, min(per_page, 100))
        
        # Build cursor query
        cursor_query = query.copy()
        
        if cursor:
            # Parse cursor (could be ObjectId or other types)
            try:
                cursor_value = ObjectId(cursor)
            except Exception:
                cursor_value = cursor
            
            # Add cursor condition
            if sort_direction >= 0:
                cursor_query[sort_field] = {"$gt": cursor_value}
            else:
                cursor_query[sort_field] = {"$lt": cursor_value}
        
        # Query with limit + 1 to check if there are more items
        cursor_obj = self.collection.find(cursor_query, projection or {})
        cursor_obj = cursor_obj.sort(sort_field, sort_direction)
        items = await cursor_obj.limit(per_page + 1).to_list(per_page + 1)
        
        # Check if there are more items
        has_next = len(items) > per_page
        if has_next:
            items = items[:per_page]
        
        # Get next cursor
        next_cursor = None
        if has_next and items:
            last_item = items[-1]
            next_cursor_value = last_item.get(sort_field)
            if isinstance(next_cursor_value, ObjectId):
                next_cursor = str(next_cursor_value)
            else:
                next_cursor = next_cursor_value
        
        return {
            "items": items,
            "pagination": {
                "per_page": per_page,
                "has_next": has_next,
                "next_cursor": next_cursor,
                "strategy": "cursor",
                "sort_field": sort_field
            }
        }
    
    async def get_page_info(
        self,
        query: dict[str, Any],
        per_page: int = 20
    ) -> dict[str, int]:
        """Get pagination information without fetching items.
        
        Args:
            query: MongoDB query filter
            per_page: Items per page
            
        Returns:
            Dictionary with total count and page count
            
        Example:
            >>> info = await handler.get_page_info({"status": "active"}, per_page=20)
            >>> print(f"Total pages: {info['total_pages']}")
        """
        total = await self.collection.count_documents(query)
        total_pages = (total + per_page - 1) // per_page if per_page > 0 else 1
        
        return {
            "total": total,
            "per_page": per_page,
            "total_pages": total_pages
        }


class PaginationStrategy:
    """Factory for creating pagination strategies."""
    
    @staticmethod
    def create(
        collection: AsyncIOMotorCollection,
        strategy: Literal["offset", "cursor"] = "offset"
    ) -> PaginationHandler:
        """Create a pagination handler with the specified strategy.
        
        Args:
            collection: MongoDB collection
            strategy: "offset" or "cursor"
            
        Returns:
            PaginationHandler instance
            
        Example:
            >>> handler = PaginationStrategy.create(collection, "offset")
        """
        return PaginationHandler(collection)
