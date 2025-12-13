"""
ModelAdmin - Base class for custom admin configurations
Allows defining custom display, search, fields, and other admin options
"""

from typing import Any, Dict, List, Optional, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase

from .registry import CollectionAdmin
from .config import CollectionConfig
from ..fields import BaseField


class ModelAdmin:
    """
    Base class for defining custom admin configurations
    
    Subclass this to customize how collections are displayed and managed:
    
    Example:
        class UserAdmin(ModelAdmin):
            display_name = "👤 Users"
            list_display = ["email", "name", "is_active"]
            search_fields = ["email", "name"]
            default_sort = [("created_at", -1)]
    """
    
    # Collection name (automatically set from registry)
    collection_name: Optional[str] = None
    
    # Display customization
    display_name: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    
    # List view configuration
    list_display: List[str] = []  # Fields to show in table
    search_fields: List[str] = []  # Fields to search
    default_sort: List[Tuple[str, int]] = []  # Default sorting
    per_page: int = 20  # Items per page
    
    # Field definitions for forms
    fields: Dict[str, BaseField] = {}
    
    # Filters and actions (for future)
    list_filters: List[str] = []
    actions: List[str] = []
    
    def __init__(self, database: AsyncIOMotorDatabase, name: str):
        """Initialize with database and collection name"""
        self.database = database
        self.collection_name = name
        
        # Create TableViewConfig with custom settings
        from .config import TableViewConfig
        table_view_config = TableViewConfig(
            default_sort=self.default_sort or [],
            per_page=self.per_page or 20
        )
        
        # Create CollectionConfig from class attributes
        self.config = CollectionConfig(
            display_name=self.display_name or name.replace("_", " ").title(),
            description=self.description,
            icon=self.icon,
            list_fields=self.list_display or None,  # USE list_display here!
            search_fields=self.search_fields or None,
            table_view=table_view_config
        )
        
        # Store as CollectionAdmin instance
        self._admin = CollectionAdmin(
            name=name,
            database=database,
            config=self.config
        )
    
    def to_collection_admin(self) -> CollectionAdmin:
        """Convert to CollectionAdmin instance"""
        return self._admin
    
    @property
    def collection(self):
        """Get MongoDB collection"""
        return self.database[self.collection_name]
    
    # Methods that can be overridden
    
    def get_list_display(self) -> List[str]:
        """Get fields to display in list view"""
        return self.list_display or []
    
    def get_search_fields(self) -> List[str]:
        """Get fields to search"""
        return self.search_fields or []
    
    def get_default_sort(self) -> List[Tuple[str, int]]:
        """Get default sort order"""
        return self.default_sort or []
    
    def get_fields(self) -> Dict[str, BaseField]:
        """Get field definitions"""
        return self.fields or {}
    
    def get_queryset(self, filters: Optional[Dict[str, Any]] = None):
        """
        Get queryset for list view (can be overridden)
        Returns find() cursor
        """
        query = filters or {}
        return self.collection.find(query)
