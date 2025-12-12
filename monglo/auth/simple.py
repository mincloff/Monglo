"""
Simple authentication provider implementation.

Basic username/password authentication with in-memory or database storage.
"""

from __future__ import annotations

from typing import Any
import hashlib

from .base import BaseAuthProvider


class SimpleAuthProvider(BaseAuthProvider):
    """
    Simple authentication provider using username/password.
    
    Can work with:
    - In-memory user dict
    - MongoDB collection
    
    Example:
        >>> # In-memory users
        >>> auth = SimpleAuthProvider(users={
        ...     "admin": {
        ...         "password_hash": SimpleAuthProvider.hash_password("admin123"),
        ...         "role": "admin"
        ...     },
        ...     "viewer": {
        ...         "password_hash": SimpleAuthProvider.hash_password("view123"),
        ...         "role": "readonly"
        ...     }
        ... })
        >>> 
        >>> # Or MongoDB-backed
        >>> auth = SimpleAuthProvider(user_collection=db.admin_users)
    """
    
    def __init__(
        self,
        users: dict[str, dict[str, Any]] | None = None,
        user_collection=None
    ):
        """
        Initialize simple auth provider.
        
        Args:
            users: Optional dict of {username: {password_hash, role, ...}}
            user_collection: Optional Motor collection for user storage
        """
        self.users = users or {}
        self.user_collection = user_collection
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    async def authenticate(
        self,
        username: str,
        password: str
    ) -> dict[str, Any] | None:
        """
        Authenticate user with username and password.
        
        Args:
            username: Username
            password: Plain text password
        
        Returns:
            User dict if authenticated, None otherwise
        """
        password_hash = self.hash_password(password)
        
        # Check in-memory users first
        if username in self.users:
            user_data = self.users[username]
            if user_data.get("password_hash") == password_hash:
                return {
                    "id": username,
                    "username": username,
                    "role": user_data.get("role", "user"),
                    **{k: v for k, v in user_data.items() 
                       if k not in ["password_hash"]}
                }
        
        # Check database if collection provided
        if self.user_collection:
            user = await self.user_collection.find_one({
                "username": username,
                "password_hash": password_hash
            })
            
            if user:
                return {
                    "id": str(user["_id"]),
                    "username": username,
                    "role": user.get("role", "user"),
                    **{k: v for k, v in user.items() 
                       if k not in ["_id", "password_hash"]}
                }
        
        return None
    
    async def authorize(
        self,
        user: dict[str, Any],
        action: str,
        collection: str | None = None
    ) -> bool:
        """
        Check if user is authorized for an action.
        
        Simple role-based authorization:
        - admin: full access
        - user: read, create, update
        - readonly: read only
        
        Args:
            user: User dict from authenticate()
            action: Action (read, create, update, delete)
            collection: Optional collection name
        
        Returns:
            True if authorized
        """
        role = user.get("role", "readonly")
        
        if role == "admin":
            return True
        
        if role == "user":
            return action in ["read", "create", "update"]
        
        if role == "readonly":
            return action == "read"
        
        return False
    
    async def get_user_info(self, user_id: str) -> dict[str, Any] | None:
        """Get user information by ID."""
        # Check in-memory users
        if user_id in self.users:
            user_data = self.users[user_id]
            return {
                "id": user_id,
                "username": user_id,
                "role": user_data.get("role", "user")
            }
        
        # Check database
        if self.user_collection:
            from bson import ObjectId
            try:
                user = await self.user_collection.find_one({"_id": ObjectId(user_id)})
                if user:
                    return {
                        "id": str(user["_id"]),
                        "username": user.get("username"),
                        "role": user.get("role", "user")
                    }
            except:
                pass
        
        return None
