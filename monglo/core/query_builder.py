"""
MongoDB query builder utilities for Monglo.

This module provides helpers for constructing MongoDB queries from
filter specifications, search terms, and sort orders.
"""

import re
from typing import Any

from bson import ObjectId
from bson import errors as bson_errors


class QueryBuilder:
    """Build MongoDB queries from high-level specifications.
    
    Constructs MongoDB find queries, aggregation pipelines, and sort
    specifications from user-friendly filter and search inputs.
    
    Example:
        >>> builder = QueryBuilder()
        >>> query = builder.build_filter({"status": "active", "age__gte": 18})
        >>> # Returns: {"status": "active", "age": {"$gte": 18}}
    """
    
    @staticmethod
    def build_filter(filters: dict[str, Any] | None = None) -> dict[str, Any]:
        """Build MongoDB filter query from filter specifications.
        
        Supports field-level filters with operators:
        - Direct match: `{"field": "value"}`
        - Greater than: `{"field__gt": 10}`
        - Less than: `{"field__lt": 10}`
        - In list: `{"field__in": [1, 2, 3]}`
        - Range: `{"field__range": [1,10]}`
        - Regex: `{"field__regex": "pattern"}`
        
        Args:
            filters: Dictionary of filter specifications
            
        Returns:
            MongoDB query document
            
        Example:
            >>> query = QueryBuilder.build_filter({
            ...     "status": "active",
            ...     "age__gte": 18,
            ...     "tags__in": ["python", "mongodb"]
            ... })
            >>> # {"status": "active", "age": {"$gte": 18}, "tags": {"$in": [...]}}
        """
        if not filters:
            return {}
        
        query: dict[str, Any] = {}
        
        for key, value in filters.items():
            # Parse operator from key
            if "__" in key:
                field, operator = key.rsplit("__", 1)
            else:
                field = key
                operator = "eq"
            
            # Build query based on operator
            if operator == "eq":
                query[field] = QueryBuilder._convert_value(value, field)
            elif operator == "ne":
                query[field] = {"$ne": QueryBuilder._convert_value(value, field)}
            elif operator == "gt":
                query[field] = {"$gt": QueryBuilder._convert_value(value, field)}
            elif operator == "gte":
                query[field] = {"$gte": QueryBuilder._convert_value(value, field)}
            elif operator == "lt":
                query[field] = {"$lt": QueryBuilder._convert_value(value, field)}
            elif operator == "lte":
                query[field] = {"$lte": QueryBuilder._convert_value(value, field)}
            elif operator == "in":
                query[field] = {           "$in": [QueryBuilder._convert_value(v, field) for v in value]
                }
            elif operator == "nin":
                query[field] = {
                    "$nin": [QueryBuilder._convert_value(v, field) for v in value]
                }
            elif operator == "regex":
                query[field] = {"$regex": value, "$options": "i"}  # Case-insensitive
            elif operator == "range":
                if len(value) == 2:
                    query[field] = {
                        "$gte": QueryBuilder._convert_value(value[0], field),
                        "$lte": QueryBuilder._convert_value(value[1], field)
                    }
            elif operator == "exists":
                query[field] = {"$exists": bool(value)}
        
        return query
    
    @staticmethod
    def build_search_query(
        search: str,
        fields: list[str]
    ) -> dict[str, Any]:
        """Build text search query across multiple fields.
        
        Creates a case-insensitive regex search across specified fields.
        
        Args:
            search: Search term
            fields: List of field names to search
            
        Returns:
            MongoDB query with $or condition
            
        Example:
            >>> query = QueryBuilder.build_search_query(
            ...     "john",
            ...     ["name", "email"]
            ... )
            >>> # {"$or": [{"name": {"$regex": "john", ...}}, {"email": ...}]}
        """
        if not search or not fields:
            return {}
        
        # Escape special regex characters
        escaped_search = re.escape(search)
        
        or_conditions = [
            {field: {"$regex": escaped_search, "$options": "i"}}
            for field in fields
        ]
        
        return {"$or": or_conditions}
    
    @staticmethod
    def build_sort(sort: list[tuple[str, int]] | None = None) -> list[tuple[str, int]]:
        """Build MongoDB sort specification.
        
        Args:
            sort: List of (field, direction) tuples where direction is 1 or -1
            
        Returns:
            MongoDB sort specification
            
        Example:
            >>> sort = QueryBuilder.build_sort([("created_at", -1), ("name", 1)])
            >>> # [("created_at", -1), ("name", 1)]
        """
        if not sort:
            return [("_id", 1)]  # Default sort by _id
        
        return sort
    
    @staticmethod
    def combine_queries(*queries: dict[str, Any]) -> dict[str, Any]:
        """Combine multiple query conditions with $and.
        
        Args:
            *queries: Multiple query dictionaries
            
        Returns:
            Combined query
            
        Example:
            >>> q1 = {"status": "active"}
            >>> q2 = {"age": {"$gte": 18}}
            >>> combined = QueryBuilder.combine_queries(q1, q2)
            >>> # {"$and": [{"status": "active"}, {"age": {"$gte": 18}}]}
        """
        # Filter out empty queries
        non_empty = [q for q in queries if q]
        
        if not non_empty:
            return {}
        
        if len(non_empty) == 1:
            return non_empty[0]
        
        return {"$and": non_empty}
    
    @staticmethod
    def _convert_value(value: Any, field: str) -> Any:
        """Convert string values to appropriate types.
        
        Attempts to convert ObjectId strings for *_id fields.
        
        Args:
            value: Value to convert
            field: Field name (used to detect ObjectId fields)
            
        Returns:
            Converted value
        """
        # Try to convert to ObjectId if field ends with _id
        if field.endswith("_id") or field == "_id":
            if isinstance(value, str):
                try:
                    return ObjectId(value)
                except (bson_errors.InvalidId, TypeError):
                    pass
        
        return value
    
    @staticmethod
    def build_pagination_query(
        page: int = 1,
        per_page: int = 20,
        max_per_page: int = 100
    ) -> tuple[int, int]:
        """Calculate skip and limit for pagination.
        
        Args:
            page: Page number (1-indexed)
            per_page: Items per page
            max_per_page: Maximum allowed items per page
            
        Returns:
            Tuple of (skip, limit) values
            
        Example:
            >>> skip, limit = QueryBuilder.build_pagination_query(page=2, per_page=20)
            >>> # (20, 20) - skip first 20, return next 20
        """
        # Validate and clamp inputs
        page = max(1, page)
        per_page = max(1, min(per_page, max_per_page))
        
        skip = (page - 1) * per_page
        limit = per_page
        
        return skip, limit
    
    @staticmethod
    def build_projection(
        fields: list[str] | None = None,
        exclude_fields: list[str] | None = None
    ) -> dict[str, int] | None:
        """Build MongoDB projection specification.
        
        Args:
            fields: Fields to include (None = all fields)
            exclude_fields: Fields to exclude
            
        Returns:
            MongoDB projection document or None
            
        Example:
            >>> proj = QueryBuilder.build_projection(["name", "email"])
            >>> # {"name": 1, "email": 1}
            >>> proj = QueryBuilder.build_projection(exclude_fields=["password"])
            >>> # {"password": 0}
        """
        if fields:
            # Include specific fields (always include _id unless explicitly excluded)
            projection = {field: 1 for field in fields}
            if "_id" not in fields and exclude_fields and "_id" in exclude_fields:
                projection["_id"] = 0
            return projection
        
        if exclude_fields:
            # Exclude specific fields
            return {field: 0 for field in exclude_fields}
        
        return None  # Return all fields
