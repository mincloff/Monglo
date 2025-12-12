"""
Aggregation operations for MongoDB collections.

Provides aggregation pipeline builders and common aggregation patterns.
"""

from typing import Any
from motor.motor_asyncio import AsyncIOMotorCollection


class AggregationOperations:
    """MongoDB aggregation pipeline operations.
    
    Provides helpers for building and executing aggregation pipelines
    with common patterns.
    
    Example:
        >>> agg = AggregationOperations(collection)
        >>> stats = await agg.get_field_stats("price")
        >>> grouped = await agg.group_by("category", count=True, avg_field="price")
    """
    
    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        """Initialize aggregation operations.
        
        Args:
            collection: MongoDB collection instance
        """
        self.collection = collection
    
    async def aggregate(self, pipeline: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Execute an aggregation pipeline.
        
        Args:
            pipeline: Aggregation pipeline stages
            
        Returns:
            List of aggregation results
            
        Example:
            >>> pipeline = [
            ...     {"$match": {"status": "active"}},
            ...     {"$group": {"_id": "$category", "count": {"$sum": 1}}}
            ... ]
            >>> results = await agg.aggregate(pipeline)
        """
        cursor = self.collection.aggregate(pipeline)
        return await cursor.to_list(None)
    
    async def get_field_stats(
        self,
        field: str,
        *,
        query: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Get statistical information about a numeric field.
        
        Args:
            field: Field name to analyze
            query: Optional filter query
            
        Returns:
            Dictionary with min, max, avg, sum, count
            
        Example:
            >>> stats = await agg.get_field_stats("price")
            >>> print(f"Average price: ${stats['avg']:.2f}")
        """
        pipeline: list[dict[str, Any]] = []
        
        if query:
            pipeline.append({"$match": query})
        
        pipeline.append({
            "$group": {
                "_id": None,
                "min": {"$min": f"${field}"},
                "max": {"$max": f"${field}"},
                "avg": {"$avg": f"${field}"},
                "sum": {"$sum": f"${field}"},
                "count": {"$sum": 1}
            }
        })
        
        results = await self.aggregate(pipeline)
        
        if results:
            stats = results[0]
            stats.pop("_id", None)
            return stats
        
        return {"min": None, "max": None, "avg": None, "sum": None, "count": 0}
    
    async def group_by(
        self,
        field: str,
        *,
        count: bool = True,
        sum_field: str | None = None,
        avg_field: str | None = None,
        query: dict[str, Any] | None = None,
        limit: int | None = None
    ) -> list[dict[str, Any]]:
        """Group documents by a field with optional aggregations.
        
        Args:
            field: Field to group by
            count: Include document count per group
            sum_field: Field to sum per group
            avg_field: Field to average per group
            query: Optional filter query
            limit: Limit number of groups returned
            
        Returns:
            List of grouped results
            
        Example:
            >>> # Count by category
            >>> by_category = await agg.group_by("category")
            >>> 
            >>> # Average price by category
            >>> by_category = await agg.group_by(
            ...     "category",
            ...     avg_field="price"
            ... )
        """
        pipeline: list[dict[str, Any]] = []
        
        if query:
            pipeline.append({"$match": query})
        
        # Build group stage
        group_stage: dict[str, Any] = {"_id": f"${field}"}
        
        if count:
            group_stage["count"] = {"$sum": 1}
        
        if sum_field:
            group_stage["total"] = {"$sum": f"${sum_field}"}
        
        if avg_field:
            group_stage["average"] = {"$avg": f"${avg_field}"}
        
        pipeline.append({"$group": group_stage})
        
        # Sort by count descending
        if count:
            pipeline.append({"$sort": {"count": -1}})
        
        # Limit results
        if limit:
            pipeline.append({"$limit": limit})
        
        results = await self.aggregate(pipeline)
        
        # Rename _id to the field name for clarity
        for result in results:
            result[field] = result.pop("_id")
        
        return results
    
    async def get_distinct_counts(
        self,
        field: str,
        *,
        query: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Get count of distinct values for a field.
        
        Args:
            field: Field to analyze
            query: Optional filter query
            
        Returns:
            Dictionary with distinct count and sample values
            
        Example:
            >>> stats = await agg.get_distinct_counts("status")
            >>> print(f"Found {stats['distinct_count']} statuses")
        """
        # Get distinct values
        distinct = await self.collection.distinct(field, query or {})
        
        # Get total documents
        total = await self.collection.count_documents(query or {})
        
        return {
            "field": field,
            "distinct_count": len(distinct),
            "total_documents": total,
            "cardinality_ratio": len(distinct) / total if total > 0 else 0,
            "sample_values": distinct[:10] if len(distinct) <= 100 else []
        }
    
    async def get_date_histogram(
        self,
        date_field: str,
        *,
        interval: str = "day",
        query: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Get document counts grouped by date intervals.
        
        Args:
            date_field: Date field to group by
            interval: "day", "week", "month", or "year"
            query: Optional filter query
            
        Returns:
            List of date buckets with counts
            
        Example:
            >>> # Documents created per day
            >>> histogram = await agg.get_date_histogram("created_at", interval="day")
            >>> for bucket in histogram:
            ...     print(f"{bucket['date']}: {bucket['count']} documents")
        """
        interval_formats = {
            "day": "%Y-%m-%d",
            "week": "%Y-W%V",
            "month": "%Y-%m",
            "year": "%Y"
        }
        
        format_str = interval_formats.get(interval, "%Y-%m-%d")
        
        pipeline: list[dict[str, Any]] = []
        
        if query:
            pipeline.append({"$match": query})
        
        pipeline.extend([
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": format_str,
                            "date": f"${date_field}"
                        }
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}},
            {
                "$project": {
                    "_id": 0,
                    "date": "$_id",
                    "count": 1
                }
            }
        ])
        
        return await self.aggregate(pipeline)
    
    async def get_top_values(
        self,
        field: str,
        *,
        limit: int = 10,
        query: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Get most common values for a field.
        
        Args:
            field: Field to analyze
            limit: Number of top values to return
            query: Optional filter query
            
        Returns:
            List of top values with counts
            
        Example:
            >>> # Top 10 categories
            >>> top_categories = await agg.get_top_values("category", limit=10)
            >>> for item in top_categories:
            ...     print(f"{item['value']}: {item['count']}")
        """
        return await self.group_by(field, query=query, limit=limit)
