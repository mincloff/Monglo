"""
Input widgets for form fields.

Provides text inputs, number inputs, date pickers, and other form controls.
"""

from typing import Any

from .base import BaseWidget


class TextInput(BaseWidget):
    """Single-line text input widget.
    
    Example:
        >>> widget = TextInput(placeholder="Enter name", maxlength=100)
        >>> config = widget.render_config()
    """
    
    def render_config(self) -> dict[str, Any]:
        return {
            "type": "text",
            "placeholder": self.options.get("placeholder", ""),
            "maxlength": self.options.get("maxlength"),
            "pattern": self.options.get("pattern"),
            "autocomplete": self.options.get("autocomplete", "off")
        }


class TextArea(BaseWidget):
    """Multi-line text input widget.
    
    Example:
        >>> widget = TextArea(rows=5, placeholder="Enter description")
    """
    
    def render_config(self) -> dict[str, Any]:
        return {
            "type": "textarea",
            "rows": self.options.get("rows", 4),
            "placeholder": self.options.get("placeholder", ""),
            "maxlength": self.options.get("maxlength")
        }


class NumberInput(BaseWidget):
    """Number input widget with optional min/max.
    
    Example:
        >>> widget = NumberInput(min=0, max=100, step=1)
    """
    
    def render_config(self) -> dict[str, Any]:
        return {
            "type": "number",
            "min": self.options.get("min"),
            "max": self.options.get("max"),
            "step": self.options.get("step", 1),
            "placeholder": self.options.get("placeholder", "0")
        }


class EmailInput(BaseWidget):
    """Email input widget with validation.
    
    Example:
        >>> widget = EmailInput(placeholder="user@example.com")
    """
    
    def render_config(self) -> dict[str, Any]:
        return {
            "type": "email",
            "placeholder": self.options.get("placeholder", "user@example.com"),
            "autocomplete": "email"
        }
    
    def validate(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, value))


class PasswordInput(BaseWidget):
    """Password input widget.
    
    Example:
        >>> widget = PasswordInput(minlength=8)
    """
    
    def render_config(self) -> dict[str, Any]:
        return {
            "type": "password",
            "minlength": self.options.get("minlength", 8),
            "autocomplete": self.options.get("autocomplete", "new-password")
        }


class DatePicker(BaseWidget):
    """Date picker widget.
    
    Example:
        >>> widget = DatePicker(format="YYYY-MM-DD")
    """
    
    def render_config(self) -> dict[str, Any]:
        return {
            "type": "date",
            "format": self.options.get("format", "YYYY-MM-DD"),
            "min": self.options.get("min"),
            "max": self.options.get("max")
        }


class DateTimePicker(BaseWidget):
    """DateTime picker widget.
    
    Example:
        >>> widget = DateTimePicker(format="YYYY-MM-DD HH:mm:ss")
    """
    
    def render_config(self) -> dict[str, Any]:
        return {
            "type": "datetime",
            "format": self.options.get("format", "YYYY-MM-DD HH:mm:ss"),
            "min": self.options.get("min"),
            "max": self.options.get("max")
        }


class CheckboxInput(BaseWidget):
    """Checkbox widget for boolean values.
    
    Example:
        >>> widget = CheckboxInput(label="Active")
    """
    
    def render_config(self) -> dict[str, Any]:
        return {
            "type": "checkbox",
            "label": self.options.get("label", ""),
            "checked": self.options.get("checked", False)
        }


class ColorPicker(BaseWidget):
    """Color picker widget.
    
    Example:
        >>> widget = ColorPicker(default="#000000")
    """
    
    def render_config(self) -> dict[str, Any]:
        return {
            "type": "color",
            "default": self.options.get("default", "#000000")
        }
