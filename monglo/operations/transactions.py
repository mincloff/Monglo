"""
Transaction support for Monglo operations.

Provides ACID guarantees for multi-document operations.
"""

from __future__ import annotations

from typing import Any, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorClientSession


class TransactionManager:
    """
    Manages MongoDB transactions for atomic operations.
    
    Requires MongoDB 4.0+ with replica set or MongoDB 4.2+ with sharded cluster.
    
    Example:
        >>> manager = TransactionManager(client)
        >>> 
        >>> async with manager.transaction() as session:
        ...     # All operations in this block are atomic
        ...     await db.users.insert_one({"name": "Alice"}, session=session)
        ...     await db.orders.insert_one({"user": "Alice"}, session=session)
        ...     # Both succeed or both fail together
    """
    
    def __init__(self, client: AsyncIOMotorClient):
        """
        Initialize transaction manager.
        
        Args:
            client: Motor client instance (must be connected to replica set)
        """
        self.client = client
    
    async def transaction(self):
        """
        Context manager for transactions.
        
        Returns:
            Async context manager for transaction
        
        Example:
            >>> async with manager.transaction() as session:
            ...     await collection.insert_one(doc, session=session)
        """
        session = await self.client.start_session()
        
        try:
            async with session.start_transaction():
                yield session
        finally:
            await session.end_session()
    
    async def execute_in_transaction(
        self,
        operations: list[Callable],
        *args,
        **kwargs
    ) -> list[Any]:
        """
        Execute multiple operations in a single transaction.
        
        Args:
            operations: List of async functions to execute
            *args: Positional arguments for operations
            **kwargs: Keyword arguments for operations
        
        Returns:
            List of results from each operation
        
        Example:
            >>> results = await manager.execute_in_transaction([
            ...     lambda session: crud1.create(data1, session=session),
            ...     lambda session: crud2.update(id, data2, session=session)
            ... ])
        """
        async with await self.transaction() as session:
            results = []
            for operation in operations:
                result = await operation(session, *args, **kwargs)
                results.append(result)
            return results
    
    async def with_retry(
        self,
        operation: Callable,
        max_retries: int = 3
    ) -> Any:
        """
        Execute operation with automatic retry on transient errors.
        
        Args:
            operation: Async function to execute
            max_retries: Maximum number of retry attempts
        
        Returns:
            Result of operation
        
        Example:
            >>> result = await manager.with_retry(
            ...     lambda: crud.create(data)
            ... )
        """
        from pymongo.errors import PyMongoError
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                return await operation()
            except PyMongoError as e:
                last_error = e
                # Check if error is transient
                if not self._is_transient_error(e):
                    raise
                
                if attempt == max_retries - 1:
                    raise
                
                # Wait before retry (exponential backoff)
                import asyncio
                await asyncio.sleep(0.1 * (2 ** attempt))
        
        raise last_error
    
    def _is_transient_error(self, error: Exception) -> bool:
        """
        Check if error is transient and worth retrying.
        
        Args:
            error: Exception to check
        
        Returns:
            True if error is transient
        """
        # Check for common transient error codes
        error_codes = [
            112,  # WriteConflict
            117,  # CappedPositionLost  
            262,  # ExceededTimeLimit
            11600, # InterruptedAtShutdown
            11602, # InterruptedDueToReplStateChange
        ]
        
        if hasattr(error, 'code') and error.code in error_codes:
            return True
        
        # Check error message for transient indicators
        error_msg = str(error).lower()
        transient_keywords = [
            'transient',
            'temporary',
            'timeout',
            'interrupted'
        ]
        
        return any(keyword in error_msg for keyword in transient_keywords)
