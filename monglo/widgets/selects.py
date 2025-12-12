"""
Select widgets for dropdown and multi-select fields.

Provides select dropdowns, multi-select, autocomplete, and radio buttons.
"""

from typing import Any
from .base import BaseWidget


class Select(BaseWidget):
    """Single-select dropdown widget.
    
    Example:
        >>> widget = Select(choices=[
        ...     ("active", "Active"),
        ...     ("inactive", "Inactive")
        ... ])
    """
    
    def render_config(self) -> dict[str, Any]:
        choices = self.options.get("choices", [])
        # Convert list of tuples to dict format
        if choices and isinstance(choices[0], (list, tuple)):
            choices = [{"value": v, "label": l} for v, l in choices]
        
        return {
            "type": "select",
            "choices": choices,
            "placeholder": self.options.get("placeholder", "Select an option"),
            "searchable": self.options.get("searchable", False)
        }


class MultiSelect(BaseWidget):
    """Multi-select dropdown widget.
    
    Example:
        >>> widget = MultiSelect(choices=[
        ...     ("electronics", "Electronics"),
        ...     ("books", "Books"),
        ...     ("clothing", "Clothing")
        ... ])
    """
    
    def render_config(self) -> dict[str, Any]:
        choices = self.options.get("choices", [])
        if choices and isinstance(choices[0], (list, tuple)):
            choices = [{"value": v, "label": l} for v, l in choices]
        
        return {
            "type": "multiselect",
            "choices": choices,
            "placeholder": self.options.get("placeholder", "Select options"),
            "searchable": self.options.get("searchable", True),
            "max_selections": self.options.get("max_selections")
        }


class Autocomplete(BaseWidget):
    """Autocomplete widget with async search.
    
    Example:
        >>> widget = Autocomplete(
        ...     source_url="/api/users",
        ...     min_chars=2
        ... )
    """
    
    def render_config(self) -> dict[str, Any]:
        return {
            "type": "autocomplete",
            "source_url": self.options.get("source_url", ""),
            "min_chars": self.options.get("min_chars", 2),
            "placeholder": self.options.get("placeholder", "Start typing..."),
            "display_field": self.options.get("display_field", "name"),
            "value_field": self.options.get("value_field", "_id")
        }


class RadioButtons(BaseWidget):
    """Radio button group widget.
    
    Example:
        >>> widget = RadioButtons(choices=[
        ...     ("male", "Male"),
        ...     ("female", "Female")
        ... ])
    """
    
    def render_config(self) -> dict[str, Any]:
        choices = self.options.get("choices", [])
        if choices and isinstance(choices[0], (list, tuple)):
            choices = [{"value": v, "label": l} for v, l in choices]
        
        return {
            "type": "radio",
            "choices": choices,
            "inline": self.options.get("inline", True)
        }


class ReferenceSelect(BaseWidget):
    """Select widget for MongoDB references.
    
    Automatically loads options from related collection.
    
    Example:
        >>> widget = ReferenceSelect(
        ...     collection="users",
        ...     display_field="name",
        ...     query={"status": "active"}
        ... )
    """
    
    def render_config(self) -> dict[str, Any]:
        return {
            "type": "reference_select",
            "collection": self.options.get("collection", ""),
            "display_field": self.options.get("display_field", "name"),
            "value_field": self.options.get("value_field", "_id"),
            "query": self.options.get("query", {}),
            "searchable": self.options.get("searchable", True),
            "placeholder": self.options.get("placeholder", "Select a reference")
        }
