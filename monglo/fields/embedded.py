"""
Embedded and array field types for nested documents.

Handles embedded documents and array fields in MongoDB.
"""

from __future__ import annotations

from typing import Any

from .base import BaseField


class EmbeddedField(BaseField):
    """
    Field type for embedded (nested) documents.
    
    Example:
        >>> # In your document:
        >>> {
        ...     "address": {
        ...         "street": "123 Main St",
        ...         "city": "NYC",
        ...         "zip": "10001"
        ...     }
        ... }
        >>> 
        >>> field = EmbeddedField(schema={
        ...     "street": StringField(),
        ...     "city": StringField(),
        ...     "zip": StringField()
        ... })
    """
    
    def __init__(
        self,
        schema: dict[str, BaseField] | None = None,
        **kwargs
    ):
        """
        Initialize embedded field.
        
        Args:
            schema: Optional schema defining nested fields
            **kwargs: Additional field options
        """
        super().__init__(**kwargs)
        self.schema = schema or {}
    
    def validate(self, value: Any) -> bool:
        """Validate embedded document."""
        if not isinstance(value, dict):
            return False
        
        # If schema provided, validate each field
        if self.schema:
            for field_name, field_def in self.schema.items():
                if field_name in value:
                    if not field_def.validate(value[field_name]):
                        return False
        
        return True
    
    def serialize(self, value: dict | None) -> dict | None:
        """Serialize embedded document."""
        if value is None:
            return None
        
        if not isinstance(value, dict):
            return value
        
        # Serialize each nested field if schema provided
        if self.schema:
            result = {}
            for field_name, field_value in value.items():
                if field_name in self.schema:
                    result[field_name] = self.schema[field_name].serialize(field_value)
                else:
                    result[field_name] = field_value
            return result
        
        return value
    
    def get_widget_config(self) -> dict[str, Any]:
        """Get widget configuration for UI."""
        return {
            "type": "embedded",
            "schema": {
                name: field.get_widget_config()
                for name, field in self.schema.items()
            } if self.schema else {}
        }


class ArrayField(BaseField):
    """
    Field type for arrays/lists.
    
    Example:
        >>> # Simple array
        >>> field = ArrayField(item_type=StringField())
        >>> 
        >>> # Array of embedded documents
        >>> field = ArrayField(item_type=EmbeddedField(schema={
        ...     "name": StringField(),
        ...     "quantity": NumberField()
        ... }))
    """
    
    def __init__(
        self,
        item_type: BaseField | None = None,
        min_items: int | None = None,
        max_items: int | None = None,
        **kwargs
    ):
        """
        Initialize array field.
        
        Args:
            item_type: Optional field type for array items
            min_items: Minimum number of items
            max_items: Maximum number of items
            **kwargs: Additional field options
        """
        super().__init__(**kwargs)
        self.item_type = item_type
        self.min_items = min_items
        self.max_items = max_items
    
    def validate(self, value: Any) -> bool:
        """Validate array."""
        if not isinstance(value, list):
            return False
        
        # Check length constraints
        if self.min_items is not None and len(value) < self.min_items:
            return False
        
        if self.max_items is not None and len(value) > self.max_items:
            return False
        
        # Validate each item if item_type provided
        if self.item_type:
            for item in value:
                if not self.item_type.validate(item):
                    return False
        
        return True
    
    def serialize(self, value: list | None) -> list | None:
        """Serialize array."""
        if value is None:
            return None
        
        if not isinstance(value, list):
            return value
        
        # Serialize each item if item_type provided
        if self.item_type:
            return [self.item_type.serialize(item) for item in value]
        
        return value
    
    def get_widget_config(self) -> dict[str, Any]:
        """Get widget configuration for UI."""
        config = {
            "type": "array",
            "min_items": self.min_items,
            "max_items": self.max_items
        }
        
        if self.item_type:
            config["item_type"] = self.item_type.get_widget_config()
        
        return config
