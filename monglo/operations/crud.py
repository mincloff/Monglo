"""
CRUD operations for MongoDB collections.

Provides create, read, update, delete operations with proper error handling,
validation, and integration with the Monglo core components.
"""

from __future__ import annotations

from typing import Any
from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorCollection

from ..core.registry import CollectionAdmin
from ..core.query_builder import QueryBuilder


class CRUDOperations:
    """CRUD operations handler for MongoDB collections.
    
    Provides high-level operations for creating, reading, updating, and
    deleting documents in a collection, with built-in validation and
    error handling.
    
    Attributes:
        admin: CollectionAdmin instance for the collection
        collection: MongoDB collection instance
    
    Example:
        >>> crud = CRUDOperations(collection_admin)
        >>> result = await crud.list(page=1, per_page=20, filters={"status": "active"})
        >>> document = await crud.get("507f1f77bcf86cd799439011")
    """
    
    def __init__(self, admin: CollectionAdmin) -> None:
        """Initialize CRUD operations for a collection.
        
        Args:
            admin: CollectionAdmin instance
        """
        self.admin = admin
        self.collection: AsyncIOMotorCollection = admin.collection
    
    async def list(
        self,
        *,
        page: int = 1,
        per_page: int = 20,
        filters: dict[str, Any] | None = None,
        sort: list[tuple[str, int]] | None = None,
        search: str | None = None,
        projection: dict[str, int] | None = None
    ) -> dict[str, Any]:
        """List documents with filtering, sorting, and pagination.
        
        Args:
            page: Page number (1-indexed)
            per_page: Items per page
            filters: Filter criteria (supports operators like __gte, __in)
            sort: Sort specification as [(field, direction), ...]
            search: Search term to match across search_fields
            projection: Fields to include/exclude
            
        Returns:
            Dictionary with items, pagination info, and metadata
            
        Example:
            >>> result = await crud.list(
            ...     page=1,
            ...     per_page=20,
            ...     filters={"status": "active", "age__gte": 18},
            ...     sort=[("created_at", -1)],
            ...     search="john"
            ... )
            >>> print(f"Found {result['total']} items")
            >>> for item in result['items']:
            ...     print(item['name'])
        """
        # Build query
        query_parts = []
        
        # Add filter query
        if filters:
            filter_query = QueryBuilder.build_filter(filters)
            if filter_query:
                query_parts.append(filter_query)
        
        # Add search query
        if search and self.admin.config.search_fields:
            search_query = QueryBuilder.build_search_query(
                search,
                self.admin.config.search_fields
            )
            if search_query:
                query_parts.append(search_query)
        
        # Combine queries
        final_query = QueryBuilder.combine_queries(*query_parts)
        
        # Get total count
        total = await self.collection.count_documents(final_query)
        
        # Calculate pagination
        skip, limit = QueryBuilder.build_pagination_query(
            page=page,
            per_page=per_page,
            max_per_page=self.admin.config.pagination_config.get("max_per_page", 100)
        )
        
        # Build sort
        sort_spec = QueryBuilder.build_sort(sort or self.admin.config.table_view.default_sort)
        
        # Query documents
        cursor = self.collection.find(final_query, projection or {})
        
        if sort_spec:
            cursor = cursor.sort(sort_spec)
        
        items = await cursor.skip(skip).limit(limit).to_list(limit)
        
        # Calculate pagination metadata
        total_pages = (total + per_page - 1) // per_page if per_page > 0 else 1
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    
    async def get(self, id: str | ObjectId) -> dict[str, Any]:
        """Get a single document by ID.
        
        Args:
            id: Document ID (ObjectId or string)
            
        Returns:
            Document dictionary
            
        Raises:
            ValueError: If ID is invalid
            KeyError: If document not found
            
        Example:
            >>> doc = await crud.get("507f1f77bcf86cd799439011")
            >>> print(doc['name'])
        """
        # Convert string to ObjectId
        if isinstance(id, str):
            try:
                id = ObjectId(id)
            except InvalidId as e:
                raise ValueError(f"Invalid ObjectId: {id}") from e
        
        document = await self.collection.find_one({"_id": id})
        
        if document is None:
            raise KeyError(f"Document with _id={id} not found in {self.admin.name}")
        
        return document
    
    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new document.
        
        Args:
            data: Document data (without _id, or with custom _id)
            
        Returns:
            Created document with _id
            
        Raises:
            ValueError: If data is invalid
            
        Example:
            >>> new_doc = await crud.create({
            ...     "name": "John Doe",
            ...     "email": "john@example.com"
            ... })
            >>> print(f"Created with ID: {new_doc['_id']}")
        """
        if not data:
            raise ValueError("Document data cannot be empty")
        
        # Ensure _id is ObjectId or let MongoDB generate it
        if "_id" in data and isinstance(data["_id"], str):
            try:
                data["_id"] = ObjectId(data["_id"])
            except InvalidId as e:
                raise ValueError(f"Invalid _id: {data['_id']}") from e
        
        # Insert document
        result = await self.collection.insert_one(data)
        
        # Fetch and return the created document
        created = await self.collection.find_one({"_id": result.inserted_id})
        return created
    
    async def update(
        self,
        id: str | ObjectId,
        data: dict[str, Any],
        *,
        partial: bool = True
    ) -> dict[str, Any]:
        """Update an existing document.
        
        Args:
            id: Document ID
            data: Update data
            partial: If True, use $set (partial update). If False, replace document.
            
        Returns:
            Updated document
            
        Raises:
            ValueError: If ID or data is invalid
            KeyError: If document not found
            
        Example:
            >>> # Partial update (default)
            >>> updated = await crud.update(
            ...     "507f1f77bcf86cd799439011",
            ...     {"status": "active"}
            ... )
            >>> 
            >>> # Full replacement
            >>> replaced = await crud.update(
            ...     "507f1f77bcf86cd799439011",
            ...     {"name": "New Name", "email": "new@example.com"},
            ...     partial=False
            ... )
        """
        if not data:
            raise ValueError("Update data cannot be empty")
        
        # Convert string to ObjectId
        if isinstance(id, str):
            try:
                id = ObjectId(id)
            except InvalidId as e:
                raise ValueError(f"Invalid ObjectId: {id}") from e
        
        # Don't allow updating _id
        if "_id" in data:
            data = data.copy()
            del data["_id"]
        
        # Perform update
        if partial:
            result = await self.collection.update_one(
                {"_id": id},
                {"$set": data}
            )
        else:
            result = await self.collection.replace_one(
                {"_id": id},
                data
            )
        
        if result.matched_count == 0:
            raise KeyError(f"Document with _id={id} not found in {self.admin.name}")
        
        # Fetch and return updated document
        updated = await self.collection.find_one({"_id": id})
        return updated
    
    async def delete(self, id: str | ObjectId) -> bool:
        """Delete a document by ID.
        
        Args:
            id: Document ID
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            ValueError: If ID is invalid
            
        Example:
            >>> deleted = await crud.delete("507f1f77bcf86cd799439011")
            >>> if deleted:
            ...     print("Document deleted")
        """
        # Convert string to ObjectId
        if isinstance(id, str):
            try:
                id = ObjectId(id)
            except InvalidId as e:
                raise ValueError(f"Invalid ObjectId: {id}") from e
        
        result = await self.collection.delete_one({"_id": id})
        return result.deleted_count > 0
    
    async def bulk_delete(self, ids: list[str | ObjectId]) -> dict[str, Any]:
        """Delete multiple documents by IDs.
        
        Args:
            ids: List of document IDs
            
        Returns:
            Dictionary with deletion results
            
        Example:
            >>> result = await crud.bulk_delete([
            ...     "507f1f77bcf86cd799439011",
            ...     "507f1f77bcf86cd799439012"
            ... ])
            >>> print(f"Deleted {result['deleted_count']} documents")
        """
        # Convert string IDs to ObjectId
        object_ids = []
        for id in ids:
            if isinstance(id, str):
                try:
                    object_ids.append(ObjectId(id))
                except InvalidId:
                    continue  # Skip invalid IDs
            else:
                object_ids.append(id)
        
        if not object_ids:
            return {"deleted_count": 0, "success": True}
        
        result = await self.collection.delete_many({"_id": {"$in": object_ids}})
        
        return {
            "deleted_count": result.deleted_count,
            "requested_count": len(ids),
            "success": True
        }
    
    async def count(self, filters: dict[str, Any] | None = None) -> int:
        """Count documents matching filters.
        
        Args:
            filters: Filter criteria
            
        Returns:
            Document count
            
        Example:
            >>> active_count = await crud.count({"status": "active"})
        """
        query = QueryBuilder.build_filter(filters) if filters else {}
        return await self.collection.count_documents(query)
    
    async def exists(self, id: str | ObjectId) -> bool:
        """Check if a document exists.
        
        Args:
            id: Document ID
            
        Returns:
            True if exists, False otherwise
            
        Example:
            >>> if await crud.exists("507f1f77bcf86cd799439011"):
            ...     print("Document exists")
        """
        try:
            await self.get(id)
            return True
        except (ValueError, KeyError):
            return False
