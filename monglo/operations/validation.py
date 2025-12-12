"""
Data validation for Monglo operations.

Validates data before create/update operations.
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.registry import CollectionAdmin
    from ..fields.base import BaseField


class DataValidator:
    """
    Validates data against collection schema and field definitions.
    
    Example:
        >>> validator = DataValidator(collection_admin)
        >>> errors = await validator.validate({"name": "", "age": -5})
        >>> if errors:
        ...     print("Validation errors:", errors)
    """
    
    def __init__(self, collection_admin: CollectionAdmin):
        """
        Initialize data validator.
        
        Args:
            collection_admin: CollectionAdmin instance
        """
        self.collection_admin = collection_admin
        self.config = collection_admin.config
    
    async def validate(self, data: dict[str, Any], is_update: bool = False) -> list[dict[str, str]]:
        """
        Validate data against schema.
        
        Args:
            data: Data to validate
            is_update: Whether this is an update (allows partial data)
        
        Returns:
            List of validation errors, empty if valid
        
        Example:
            >>> errors = await validator.validate({"name": "John", "age": 25})
            >>> if not errors:
            ...     # Data is valid
            ...     await crud.create(data)
        """
        errors = []
        
       # Check required fields (only for create, not update)
        if not is_update:
            errors.extend(self._validate_required_fields(data))
        
        # Validate field types and values
        errors.extend(self._validate_field_values(data))
        
        # Custom validation rules
        errors.extend(await self._validate_custom_rules(data))
        
        return errors
    
    def _validate_required_fields(self, data: dict[str, Any]) -> list[dict[str, str]]:
        """
        Check that all required fields are present.
        
        Args:
            data: Data to validate
        
        Returns:
            List of errors for missing required fields
        """
        errors = []
        
        # Get required fields from config
        if hasattr(self.config, 'required_fields'):
            for field in self.config.required_fields:
                if field not in data or data[field] is None:
                    errors.append({
                        "field": field,
                        "error": "required",
                        "message": f"Field '{field}' is required"
                    })
        
        return errors
    
    def _validate_field_values(self, data: dict[str, Any]) -> list[dict[str, str]]:
        """
        Validate field values against field definitions.
        
        Args:
            data: Data to validate
        
        Returns:
            List of validation errors
        """
        errors = []
        
        # Get field definitions from config
        if hasattr(self.config, 'fields'):
            for field_name, field_def in self.config.fields.items():
                if field_name in data:
                    value = data[field_name]
                    
                    # Use field's validate method if available
                    if hasattr(field_def, 'validate'):
                        if not field_def.validate(value):
                            errors.append({
                                "field": field_name,
                                "error": "invalid_value",
                                "message": f"Invalid value for field '{field_name}'"
                            })
        
        return errors
    
    async def _validate_custom_rules(self, data: dict[str, Any]) -> list[dict[str, str]]:
        """
        Apply custom validation rules.
        
        Args:
            data: Data to validate
        
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check for unique constraints
        errors.extend(await self._validate_unique_constraints(data))
        
        # Add more custom rules as needed
        
        return errors
    
    async def _validate_unique_constraints(self, data: dict[str, Any]) -> list[dict[str, str]]:
        """
        Validate unique field constraints.
        
        Args:
            data: Data to validate
        
        Returns:
            List of errors for unique constraint violations
        """
        errors = []
        
        # Get unique fields from config
        if hasattr(self.config, 'unique_fields'):
            for field in self.config.unique_fields:
                if field in data:
                    # Check if value already exists
                    existing = await self.collection_admin.collection.find_one({
                        field: data[field]
                    })
                    
                    if existing:
                        errors.append({
                            "field": field,
                            "error": "duplicate",
                            "message": f"Value for '{field}' already exists"
                        })
        
        return errors
    
    def validate_sync(self, data: dict[str, Any]) -> list[dict[str, str]]:
        """
        Synchronous validation (for non-async contexts).
        
        Only validates field types, not unique constraints.
        
        Args:
            data: Data to validate
        
        Returns:
            List of validation errors
        """
        errors = []
        errors.extend(self._validate_required_fields(data))
        errors.extend(self._validate_field_values(data))
        return errors
