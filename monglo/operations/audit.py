"""
Audit logging for Monglo admin operations.

Tracks all data modifications for compliance and security.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from motor.motor_asyncio import AsyncIOMotorDatabase


class AuditLogger:
    """
    Audit logger for tracking all admin operations.
    
    Logs create, update, delete operations with:
    - Timestamp
    - User (if authenticated)
    - Action type
    - Collection name
    - Document ID
    - Changes (before/after for updates)
    
    Example:
        >>> logger = AuditLogger(database=db, collection_name="admin_audit_log")
        >>> await logger.log_create(
        ...     collection="users",
        ...     document={"name": "Alice"},
        ...     user={"id": "admin", "role": "admin"}
        ... )
    """
    
    def __init__(
        self,
        database: AsyncIOMotorDatabase,
        collection_name: str = "monglo_audit_log"
    ):
        """
        Initialize audit logger.
        
        Args:
            database: Motor database instance
            collection_name: Name of audit log collection
        """
        self.db = database
        self.collection = database[collection_name]
    
    async def log_create(
        self,
        collection: str,
        document: dict[str, Any],
        user: dict[str, Any] | None = None
    ) -> None:
        """
        Log document creation.
        
        Args:
            collection: Collection name
            document: Created document
            user: User who performed the action
        """
        await self._log_action(
            action="create",
            collection=collection,
            document_id=str(document.get("_id")),
            user=user,
            data=document
        )
    
    async def log_update(
        self,
        collection: str,
        document_id: str,
        before: dict[str, Any],
        after: dict[str, Any],
        user: dict[str, Any] | None = None
    ) -> None:
        """
        Log document update.
        
        Args:
            collection: Collection name
            document_id: Document ID
            before: Document state before update
            after: Document state after update
            user: User who performed the action
        """
        # Calculate changes
        changes = self._calculate_changes(before, after)
        
        await self._log_action(
            action="update",
            collection=collection,
            document_id=document_id,
            user=user,
            changes=changes,
            before=before,
            after=after
        )
    
    async def log_delete(
        self,
        collection: str,
        document_id: str,
        document: dict[str, Any],
        user: dict[str, Any] | None = None
    ) -> None:
        """
        Log document deletion.
        
        Args:
            collection: Collection name
            document_id: Document ID
            document: Deleted document
            user: User who performed the action
        """
        await self._log_action(
            action="delete",
            collection=collection,
            document_id=document_id,
            user=user,
            data=document
        )
    
    async def log_bulk_operation(
        self,
        collection: str,
        action: str,
        count: int,
        user: dict[str, Any] | None = None,
        details: dict[str, Any] | None = None
    ) -> None:
        """
        Log bulk operation.
        
        Args:
            collection: Collection name
            action: Action type (bulk_create, bulk_update, bulk_delete)
            count: Number of documents affected
            user: User who performed the action
            details: Additional details about the operation
        """
        await self._log_action(
            action=action,
            collection=collection,
            user=user,
            count=count,
            details=details
        )
    
    async def _log_action(
        self,
        action: str,
        collection: str,
        user: dict[str, Any] | None = None,
        **kwargs
    ) -> None:
        """
        Internal method to log an action.
        
        Args:
            action: Action type
            collection: Collection name
            user: User who performed the action  
            **kwargs: Additional data to log
        """
        log_entry = {
            "timestamp": datetime.utcnow(),
            "action": action,
            "collection": collection,
            "user": {
                "id": user.get("id") if user else "anonymous",
                "role": user.get("role") if user else None
            } if user else None,
            **kwargs
        }
        
        await self.collection.insert_one(log_entry)
    
    def _calculate_changes(
        self,
        before: dict[str, Any],
        after: dict[str, Any]
    ) -> dict[str, dict[str, Any]]:
        """
        Calculate changes between before and after states.
        
        Args:
            before: Document before update
            after: Document after update
        
        Returns:
            Dict of changes with old and new values
        """
        changes = {}
        
        # Find changed fields
        all_keys = set(before.keys()) | set(after.keys())
        
        for key in all_keys:
            old_value = before.get(key)
            new_value = after.get(key)
            
            if old_value != new_value:
                changes[key] = {
                    "old": old_value,
                    "new": new_value
                }
        
        return changes
    
    async def get_document_history(
        self,
        collection: str,
        document_id: str,
        limit: int = 50
    ) -> list[dict[str, Any]]:
        """
        Get audit history for a specific document.
        
        Args:
            collection: Collection name
            document_id: Document ID
            limit: Maximum number of entries to return
        
        Returns:
            List of audit log entries
        """
        cursor = self.collection.find({
            "collection": collection,
            "document_id": document_id
        }).sort("timestamp", -1).limit(limit)
        
        return await cursor.to_list(length=limit)
    
    async def get_user_activity(
        self,
        user_id: str,
        limit: int = 100
    ) -> list[dict[str, Any]]:
        """
        Get audit history for a specific user.
        
        Args:
            user_id: User ID
            limit: Maximum number of entries to return
        
        Returns:
            List of audit log entries
        """
        cursor = self.collection.find({
            "user.id": user_id
        }).sort("timestamp", -1).limit(limit)
        
        return await cursor.to_list(length=limit)
