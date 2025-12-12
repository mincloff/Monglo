"""
Custom field type support.

Allows users to create their own field types by extending BaseField.
"""

from __future__ import annotations

from typing import Any, Callable

from .base import BaseField


class CustomField(BaseField):
    """
    Base class for creating custom field types.
    
    Extend this class to create your own field types with custom
    validation, serialization, and widget configuration.
    
    Example:
        >>> class EmailField(CustomField):
        ...     def validate(self, value):
        ...         import re
        ...         pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
        ...         return bool(re.match(pattern, value))
        ...     
        ...     def get_widget_config(self):
        ...         return {
        ...             "type": "email",
        ...             "placeholder": "user@example.com"
        ...         }
    """
    
    def __init__(
        self,
        validator: Callable[[Any], bool] | None = None,
        serializer: Callable[[Any], Any] | None = None,
        widget_config: dict[str, Any] | None = None,
        **kwargs
    ):
        """
        Initialize custom field.
        
        Args:
            validator: Optional custom validation function
            serializer: Optional custom serialization function  
            widget_config: Optional widget configuration dict
            **kwargs: Additional field options
        """
        super().__init__(**kwargs)
        self._custom_validator = validator
        self._custom_serializer = serializer
        self._widget_config = widget_config or {}
    
    def validate(self, value: Any) -> bool:
        """
        Validate field value.
        
        Override this method or provide validator function in __init__.
        """
        if self._custom_validator:
            return self._custom_validator(value)
        return True  # Default: accept any value
    
    def serialize(self, value: Any) -> Any:
        """
        Serialize field value.
        
        Override this method or provide serializer function in __init__.
        """
        if self._custom_serializer:
            return self._custom_serializer(value)
        return value  # Default: return as-is
    
    def get_widget_config(self) -> dict[str, Any]:
        """
        Get widget configuration for UI.
        
        Override this method or provide widget_config dict in __init__.
        """
        return self._widget_config


class EnumField(CustomField):
    """
    Field for enumerated values (choices).
    
    Example:
        >>> field = EnumField(choices=["active", "inactive", "pending"])
    """
    
    def __init__(self, choices: list[str], **kwargs):
        """
        Initialize enum field.
        
        Args:
            choices: List of allowed values
            **kwargs: Additional field options
        """
        self.choices = choices
        super().__init__(
            validator=lambda v: v in choices,
            widget_config={
                "type": "select",
                "choices": [{"value": c, "label": c.title()} for c in choices]
            },
            **kwargs
        )


class URLField(CustomField):
    """
    Field for URL validation.
    
    Example:
        >>> field = URLField(require_https=True)
    """
    
    def __init__(self, require_https: bool = False, **kwargs):
        """
        Initialize URL field.
        
        Args:
            require_https: Whether to require HTTPS
            **kwargs: Additional field options
        """
        self.require_https = require_https
        
        def validate_url(value: str) -> bool:
            import re
            if not isinstance(value, str):
                return False
            
            pattern = r'^https?://[^\s/$.?#].[^\s]*$'
            if not re.match(pattern, value):
                return False
            
            if self.require_https and not value.startswith('https://'):
                return False
            
            return True
        
        super().__init__(
            validator=validate_url,
            widget_config={
                "type": "url",
                "placeholder": "https://example.com"
            },
            **kwargs
        )


class ColorField(CustomField):
    """
    Field for color values (hex format).
    
    Example:
        >>> field = ColorField()
    """
    
    def __init__(self, **kwargs):
        """Initialize color field."""
        def validate_color(value: str) -> bool:
            import re
            if not isinstance(value, str):
                return False
            return bool(re.match(r'^#[0-9A-Fa-f]{6}$', value))
        
        super().__init__(
            validator=validate_color,
            widget_config={
                "type": "color",
                "default": "#000000"
            },
            **kwargs
        )


class JSONField(CustomField):
    """
    Field for JSON data.
    
    Example:
        >>> field = JSONField(schema={"type": "object"})
    """
    
    def __init__(self, schema: dict | None = None, **kwargs):
        """
        Initialize JSON field.
        
        Args:
            schema: Optional JSON schema for validation
            **kwargs: Additional field options
        """
        self.schema = schema
        
        def validate_json(value: Any) -> bool:
            # Allow dict or list (JSON-serializable types)
            if isinstance(value, (dict, list)):
                return True
            
            # Try parsing if string
            if isinstance(value, str):
                try:
                    import json
                    json.loads(value)
                    return True
                except:
                    return False
            
            return False
        
        super().__init__(
            validator=validate_json,
            widget_config={
                "type": "json",
                "schema": schema
            },
            **kwargs
        )
