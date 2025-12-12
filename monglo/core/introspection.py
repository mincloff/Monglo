"""
Schema introspection for MongoDB collections.

This module provides automatic schema discovery by sampling and analyzing
documents to infer field types and structure.
"""

from typing import Any
from collections import defaultdict
from datetime import datetime, date
from bson import ObjectId, DBRef
from motor.motor_asyncio import AsyncIOMotorDatabase


class SchemaIntrospector:
    """Automatic schema introspection for MongoDB collections.
    
    Analyzes sample documents to discover field types, nested structures,
    and data patterns without requiring explicit schema definitions.
    
    Attributes:
        db: MongoDB database instance
    
    Example:
        >>> introspector = SchemaIntrospector(db)
        >>> schema = await introspector.introspect("users", sample_size=100)
        >>> assert schema["email"]["type"] == "string"
    """
    
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        """Initialize the schema introspector.
        
        Args:
            database: Motor database instance
        """
        self.db = database
    
    async def introspect(
        self,
        collection_name: str,
        sample_size: int = 100
    ) -> dict[str, dict[str, Any]]:
        """Introspect a collection's schema.
        
        Analyzes sample documents to determine field types, frequencies,
        and nested structures.
        
        Args:
            collection_name: Name of the collection to analyze
            sample_size: Number of documents to sample
            
        Returns:
            Schema dictionary mapping field paths to type information
            
        Example:
            >>> schema = await introspector.introspect("products")
            >>> schema["price"]["type"]  # "number"
            >>> schema["tags"]["type"]  # "array"
        """
        collection = self.db[collection_name]
        
        # Sample documents
        documents = await collection.find().limit(sample_size).to_list(sample_size)
        
        if not documents:
            return {}
        
        # Analyze fields across all documents
        field_info: dict[str, dict[str, Any]] = defaultdict(lambda: {
            "types": defaultdict(int),
            "count": 0,
            "null_count": 0,
            "sample_values": []
        })
        
        for doc in documents:
            self._analyze_document(doc, field_info, prefix="")
        
        # Convert analysis to final schema
        schema: dict[str, dict[str, Any]] = {}
        total_docs = len(documents)
        
        for field_path, info in field_info.items():
            # Determine primary type (most common)
            primary_type = max(info["types"].items(), key=lambda x: x[1])[0]
            
            schema[field_path] = {
                "type": primary_type,
                "frequency": info["count"] / total_docs,
                "nullable": info["null_count"] > 0,
                "sample_values": info["sample_values"][:5]  # First 5 samples
            }
            
            # Add array item type if present
            if "array_item_type" in info:
                schema[field_path]["array_item_type"] = info["array_item_type"]
            
            # Add additional type info if field has multiple types
            if len(info["types"]) > 1:
                schema[field_path]["alternative_types"] = list(info["types"].keys())
        
        return  schema
    
    def _analyze_document(
        self,
        doc: dict[str, Any],
        field_info: dict[str, dict[str, Any]],
        prefix: str
    ) -> None:
        """Recursively analyze a document's fields.
        
        Args:
            doc: Document or nested object to analyze
            field_info: Accumulator for field statistics
            prefix: Field path prefix for nested fields
        """
        for key, value in doc.items():
            field_path = f"{prefix}{key}" if prefix else key
            
            # Update field count
            field_info[field_path]["count"] += 1
            
            # Detect type
            field_type = self._detect_type(value)
            field_info[field_path]["types"][field_type] += 1
            
            # Track nulls
            if value is None:
                field_info[field_path]["null_count"] += 1
            
            # Store sample value
            if len(field_info[field_path]["sample_values"]) < 5:
                field_info[field_path]["sample_values"].append(value)
            
            # Recurse into nested documents
            if isinstance(value, dict) and not isinstance(value, (DBRef,)):
                field_info[field_path]["types"]["embedded"] += 1
                self._analyze_document(value, field_info, prefix=f"{field_path}.")
            
            # Analyze array elements
            elif isinstance(value, list) and value:
                field_info[field_path]["types"]["array"] += 1
                # Sample first element to determine array item type
                first_elem = value[0]
                if isinstance(first_elem, dict):
                    field_info[field_path]["array_item_type"] = "embedded"
                    self._analyze_document(first_elem, field_info, prefix=f"{field_path}.[].")
                else:
                    field_info[field_path]["array_item_type"] = self._detect_type(first_elem)
    
    def _detect_type(self, value: Any) -> str:
        """Detect the type of a value.
        
        Args:
            value: Value to analyze
            
        Returns:
            Type name as string
            
        Example:
            >>> introspector._detect_type(ObjectId())
            'objectid'
            >>> introspector._detect_type("hello")
            'string'
        """
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "number"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, datetime):
            return "datetime"
        elif isinstance(value, date):
            return "date"
        elif isinstance(value, ObjectId):
            return "objectid"
        elif isinstance(value, DBRef):
            return "dbref"
        elif isinstance(value, dict):
            return "embedded"
        elif isinstance(value, list):
            return "array"
        elif isinstance(value, bytes):
            return "binary"
        else:
            return "unknown"
    
    async def get_indexes(self, collection_name: str) -> list[dict[str, Any]]:
        """Get index information for a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            List of index specifications
            
        Example:
            >>> indexes = await introspector.get_indexes("users")
            >>> for idx in indexes:
            ...     print(idx["name"])
        """
        collection = self.db[collection_name]
        indexes = await collection.list_indexes().to_list(100)
        return indexes
    
    async def analyze_field_cardinality(
        self,
        collection_name: str,
        field: str
    ) -> dict[str, Any]:
        """Analyze the cardinality (distinct values) of a field.
        
        Useful for determining if a field is a good candidate for indexing
        or for creating select filters.
        
        Args:
            collection_name: Name of the collection
            field: Field name to analyze
            
        Returns:
             Dictionary with cardinality statistics
            
        Example:
            >>> stats = await introspector.analyze_field_cardinality("users", "status")
            >>> stats["distinct_count"]  # Number of unique values
        """
        collection = self.db[collection_name]
        
        # Get total document count
        total = await collection.count_documents({})
        
        # Get distinct values (limited to 1000 for performance)
        distinct_values = await collection.distinct(field)
        distinct_count = len(distinct_values)
        
        return {
            "field": field,
            "total_documents": total,
            "distinct_count": distinct_count,
            "cardinality_ratio": distinct_count / total if total > 0 else 0,
            "is_unique": distinct_count == total,
            "is_low_cardinality": distinct_count < 50,  # Good for filters
            "sample_values": distinct_values[:10] if distinct_count <= 100 else []
        }
