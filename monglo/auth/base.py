"""
Base authentication provider interface.

Defines the interface all auth providers must implement.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseAuthProvider(ABC):
    """
    Abstract base class for authentication providers.
    
    Implement this to create custom authentication for your admin panel.
    
    Example:
        >>> class MyAuthProvider(BaseAuthProvider):
        ...     async def authenticate(self, username, password):
        ...         # Your authentication logic
        ...         user = await db.users.find_one({"username": username})
        ...         if user and check_password(password, user["password_hash"]):
        ...             return {"id": str(user["_id"]), "role": user["role"]}
        ...         return None
        ...     
        ...     async def authorize(self, user, action, collection):
        ...         # Your authorization logic
        ...         if user["role"] == "admin":
        ...             return True
        ...         return action == "read"
    """
    
    @abstractmethod
    async def authenticate(
        self,
        username: str,
        password: str
    ) -> dict[str, Any] | None:
        """
        Authenticate a user with username and password.
        
        Args:
            username: Username
            password: Password (plain text - hash it in your implementation)
        
        Returns:
            User dict with at least {"id": str, "role": str} if authenticated,
            None if authentication failed
        """
        pass
    
    @abstractmethod
    async def authorize(
        self,
        user: dict[str, Any],
        action: str,
        collection: str | None = None
    ) -> bool:
        """
        Check if user is authorized to perform an action.
        
        Args:
            user: User dict from authenticate()
            action: Action to perform (read, create, update, delete)
            collection: Optional collection name
        
        Returns:
            True if authorized, False otherwise
        """
        pass
    
    async def get_user_info(self, user_id: str) -> dict[str, Any] | None:
        """
        Get user information by ID.
        
        Optional method - implement if needed.
        
        Args:
            user_id: User ID
        
        Returns:
            User info dict or None
        """
        return None
