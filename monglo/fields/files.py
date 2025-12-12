"""
File field types with GridFS support.

Handles file uploads and storage using MongoDB GridFS.
"""

from __future__ import annotations

from typing import Any, BinaryIO
from io import BytesIO

from .base import BaseField


class FileField(BaseField):
    """
    Field type for file uploads with GridFS storage.
    
    Example:
        >>> field = FileField(
        ...     allowed_extensions=['.jpg', '.png', '.pdf'],
        ...     max_size_mb=10
        ... )
    """
    
    def __init__(
        self,
        allowed_extensions: list[str] | None = None,
        max_size_mb: float | None = None,
        **kwargs
    ):
        """
        Initialize file field.
        
        Args:
            allowed_extensions: List of allowed file extensions (e.g., ['.jpg', '.pdf'])
            max_size_mb: Maximum file size in megabytes
            **kwargs: Additional field options
        """
        super().__init__(**kwargs)
        self.allowed_extensions = allowed_extensions or []
        self.max_size_mb = max_size_mb
    
    def validate(self, value: Any) -> bool:
        """Validate file."""
        # Value should be a file-like object or file metadata
        if value is None:
            return not self.required
        
        # Check if it's file metadata (from GridFS)
        if isinstance(value, dict):
            if "filename" in value and "file_id" in value:
                return True
        
        # Check if it's a file object
        if hasattr(value, 'read'):
            return True
        
        return False
    
    def serialize(self, value: Any) -> dict | None:
        """Serialize file metadata."""
        if value is None:
            return None
        
        # If already serialized metadata
        if isinstance(value, dict) and "filename" in value:
            return value
        
        # Return basic info
        return {
            "type": "file",
            "uploaded": True
        }
    
    def get_widget_config(self) -> dict[str, Any]:
        """Get widget configuration for UI."""
        return {
            "type": "file",
            "allowed_extensions": self.allowed_extensions,
            "max_size_mb": self.max_size_mb,
            "accept": ",".join(self.allowed_extensions) if self.allowed_extensions else "*"
        }


class ImageField(FileField):
    """
    Specialized field for image uploads.
    
    Example:
        >>> field = ImageField(
        ...     max_size_mb=5,
        ...     max_width=2000,
        ...     max_height=2000
        ... )
    """
    
    def __init__(
        self,
        max_width: int | None = None,
        max_height: int | None = None,
        **kwargs
    ):
        """
        Initialize image field.
        
        Args:
            max_width: Maximum image width in pixels
            max_height: Maximum image height in pixels
            **kwargs: Additional field options
        """
        # Default to common image formats
        if 'allowed_extensions' not in kwargs:
            kwargs['allowed_extensions'] = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        
        super().__init__(**kwargs)
        self.max_width = max_width
        self.max_height = max_height
    
    def get_widget_config(self) -> dict[str, Any]:
        """Get widget configuration for UI."""
        config = super().get_widget_config()
        config.update({
            "type": "image",
            "max_width": self.max_width,
            "max_height": self.max_height,
            "preview": True
        })
        return config


class GridFSHelper:
    """
    Helper class for GridFS operations.
    
    Provides utilities for storing and retrieving files from MongoDB GridFS.
    """
    
    def __init__(self, database):
        """
        Initialize GridFS helper.
        
        Args:
            database: Motor database instance
        """
        from motor.motor_asyncio import AsyncIOMotorGridFSBucket
        self.fs = AsyncIOMotorGridFSBucket(database)
    
    async def upload_file(
        self,
        file_data: bytes | BinaryIO,
        filename: str,
        content_type: str | None = None,
        metadata: dict | None = None
    ) -> str:
        """
        Upload file to GridFS.
        
        Args:
            file_data: File data as bytes or file-like object
            filename: Filename
            content_type: MIME content type
            metadata: Additional metadata
        
        Returns:
            File ID as string
        """
        # Convert to BytesIO if bytes
        if isinstance(file_data, bytes):
            file_data = BytesIO(file_data)
        
        # Upload to GridFS
        file_id = await self.fs.upload_from_stream(
            filename,
            file_data,
            metadata={
                "content_type": content_type,
                **(metadata or {})
            }
        )
        
        return str(file_id)
    
    async def download_file(self, file_id: str) -> bytes:
        """
        Download file from GridFS.
        
        Args:
            file_id: File ID
        
        Returns:
            File data as bytes
        """
        from bson import ObjectId
        
        grid_out = await self.fs.open_download_stream(ObjectId(file_id))
        data = await grid_out.read()
        return data
    
    async def delete_file(self, file_id: str) -> None:
        """
        Delete file from GridFS.
        
        Args:
            file_id: File ID
        """
        from bson import ObjectId
        await self.fs.delete(ObjectId(file_id))
    
    async def get_file_metadata(self, file_id: str) -> dict:
        """
        Get file metadata.
        
        Args:
            file_id: File ID
        
        Returns:
            File metadata dict
        """
        from bson import ObjectId
        
        grid_out = await self.fs.open_download_stream(ObjectId(file_id))
        
        return {
            "file_id": str(file_id),
            "filename": grid_out.filename,
            "length": grid_out.length,
            "upload_date": grid_out.upload_date,
            "content_type": grid_out.metadata.get("content_type") if grid_out.metadata else None,
            "metadata": grid_out.metadata
        }
