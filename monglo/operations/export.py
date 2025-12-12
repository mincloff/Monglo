"""
Export operations for MongoDB collections.

Provides data export functionality in various formats (JSON, CSV).
"""

from __future__ import annotations

import csv
import json
from typing import Any, Literal
from io import StringIO
from datetime import datetime, date
from bson import ObjectId


class ExportOperations:
    """Handle data export in various formats.
    
    Supports JSON and CSV export with proper type serialization
    for MongoDB-specific types.
    
    Example:
        >>> exporter = ExportOperations()
        >>> json_data = exporter.to_json(documents)
        >>> csv_data = exporter.to_csv(documents, fields=["name", "email"])
    """
    
    def to_json(
        self,
        documents: list[dict[str, Any]],
        *,
        pretty: bool = False,
        ensure_ascii: bool = False
    ) -> str:
        """Export documents to JSON format.
        
        Automatically serializes MongoDB types (ObjectId, datetime).
        
        Args:
            documents: List of documents to export
            pretty: If True, format with indentation
            ensure_ascii: If True, escape non-ASCII characters
            
        Returns:
            JSON string
            
        Example:
            >>> json_str = exporter.to_json(documents, pretty=True)
            >>> # Save to file
            >>> with open("export.json", "w") as f:
            ...     f.write(json_str)
        """
        # Serialize documents
        serialized = [self._serialize_document(doc) for doc in documents]
        
        indent = 2 if pretty else None
        return json.dumps(
            serialized,
            indent=indent,
            ensure_ascii=ensure_ascii,
            default=str
        )
    
    def to_csv(
        self,
        documents: list[dict[str, Any]],
        *,
        fields: list[str] | None = None,
        include_headers: bool = True
    ) -> str:
        """Export documents to CSV format.
        
        Args:
            documents: List of documents to export
            fields: Fields to include (None = all fields from first doc)
            include_headers: Whether to include header row
            
        Returns:
            CSV string
            
        Example:
            >>> csv_str = exporter.to_csv(
            ...     documents,
            ...     fields=["name", "email", "created_at"]
            ... )
            >>> # Save to file
            >>> with open("export.csv", "w") as f:
            ...     f.write(csv_str)
        """
        if not documents:
            return ""
        
        # Determine fields
        if fields is None:
            fields = list(documents[0].keys())
        
        # Create CSV in memory
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=fields)
        
        if include_headers:
            writer.writeheader()
        
        # Write rows
        for doc in documents:
            # Serialize and filter fields
            serialized = self._serialize_document(doc)
            row = {field: serialized.get(field, "") for field in fields}
            writer.writerow(row)
        
        return output.getvalue()
    
    def to_ndjson(self, documents: list[dict[str, Any]]) -> str:
        """Export documents to NDJSON (newline-delimited JSON) format.
        
        Each line is a complete JSON object. Good for streaming and
        large datasets.
        
        Args:
            documents: List of documents to export
            
        Returns:
            NDJSON string
            
        Example:
            >>> ndjson = exporter.to_ndjson(documents)
        """
        lines = []
        for doc in documents:
            serialized = self._serialize_document(doc)
            lines.append(json.dumps(serialized, default=str))
        
        return "\n".join(lines)
    
    def _serialize_document(self, doc: dict[str, Any]) -> dict[str, Any]:
        """Serialize a document for export.
        
        Converts MongoDB-specific types to JSON-serializable types.
        
        Args:
            doc: Document to serialize
            
        Returns:
            Serialized document
        """
        serialized = {}
        
        for key, value in doc.items():
            serialized[key] = self._serialize_value(value)
        
        return serialized
    
    def _serialize_value(self, value: Any) -> Any:
        """Serialize a single value.
        
        Args:
            value: Value to serialize
            
        Returns:
            Serialized value
        """
        if isinstance(value, ObjectId):
            return str(value)
        elif isinstance(value, (datetime, date)):
            return value.isoformat()
        elif isinstance(value, dict):
            return self._serialize_document(value)
        elif isinstance(value, list):
            return [self._serialize_value(v) for v in value]
        elif isinstance(value, bytes):
            return value.hex()  # Convert binary to hex string
        else:
            return value


class ExportFormat:
    """Export format options."""
    
    JSON = "json"
    CSV = "csv"
    NDJSON = "ndjson"


async def export_collection(
    collection,
    *,
    format: Literal["json", "csv", "ndjson"] = "json",
    query: dict[str, Any] | None = None,
    fields: list[str] | None = None,
    limit: int | None = None,
    **kwargs
) -> str:
    """Export an entire collection or filtered subset.
    
    Convenience function for exporting directly from a collection.
    
    Args:
        collection: MongoDB collection instance
        format: Export format ("json", "csv", "ndjson")
        query: Filter query (None = all documents)
        fields: Fields to include (for CSV)
        limit: Maximum documents to export
        **kwargs: Additional format-specific arguments
        
    Returns:
        Exported data as string
        
    Example:
        >>> # Export all active users as JSON
        >>> json_data = await export_collection(
        ...     db.users,
        ...     format="json",
        ...     query={"status": "active"},
        ...     pretty=True
        ... )
        >>> 
        >>> # Export specific fields as CSV
        >>> csv_data = await export_collection(
        ...     db.users,
        ...     format="csv",
        ...     fields=["name", "email"],
        ...     limit=1000
        ... )
    """
    # Query documents
    cursor = collection.find(query or {})
    
    if limit:
        cursor = cursor.limit(limit)
    
    documents = await cursor.to_list(limit or 0)
    
    # Export
    exporter = ExportOperations()
    
    if format == "json":
        return exporter.to_json(documents, **kwargs)
    elif format == "csv":
        return exporter.to_csv(documents, fields=fields, **kwargs)
    elif format == "ndjson":
        return exporter.to_ndjson(documents)
    else:
        raise ValueError(f"Unsupported export format: {format}")
