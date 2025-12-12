"""
Custom widget implementation support.

Allows users to create their own custom widgets by extending BaseWidget.
"""

from collections.abc import Callable
from typing import Any

from .base import BaseWidget


class CustomWidget(BaseWidget):
    """Custom widget for user-defined components.

    Allows complete customization of widget rendering and validation.

    Example:
        >>> def my_render(options):
        ...     return {"type": "custom_input", **options}
        ...
        >>> widget = CustomWidget(
        ...     render_func=my_render,
        ...     component_name="MyCustomInput",
        ...     props={"color": "primary"}
        ... )
    """

    def __init__(self, render_func: Callable | None = None, **options):
        """Initialize custom widget.

        Args:
            render_func: Optional function to generate config
            **options: Widget options including component_name, props, etc.
        """
        super().__init__(**options)
        self.render_func = render_func

    def render_config(self) -> dict[str, Any]:
        """Generate custom widget configuration.

        Returns:
            Custom widget configuration dict
        """
        if self.render_func:
            return self.render_func(self.options)

        return {
            "type": "custom",
            "component_name": self.options.get("component_name", "CustomWidget"),
            "props": self.options.get("props", {}),
            "events": self.options.get("events", {}),
        }


class WidgetGroup(BaseWidget):
    """Group multiple widgets together.

    Useful for composite fields or complex layouts.

    Example:
        >>> widget = WidgetGroup(
        ...     widgets=[
        ...         ("first_name", TextInput()),
        ...         ("last_name", TextInput())
        ...     ],
        ...     layout="horizontal"
        ... )
    """

    def render_config(self) -> dict[str, Any]:
        widgets_config = []
        for name, widget in self.options.get("widgets", []):
            widgets_config.append({"name": name, "config": widget.render_config()})

        return {
            "type": "widget_group",
            "widgets": widgets_config,
            "layout": self.options.get("layout", "vertical"),
            "label": self.options.get("label", ""),
        }


class ConditionalWidget(BaseWidget):
    """Widget that shows/hides based on conditions.

    Example:
        >>> widget = ConditionalWidget(
        ...     widget=TextInput(),
        ...     condition={"field": "status", "value": "active"}
        ... )
    """

    def render_config(self) -> dict[str, Any]:
        widget = self.options.get("widget")
        widget_config = widget.render_config() if widget else {}

        return {
            "type": "conditional",
            "widget": widget_config,
            "condition": self.options.get("condition", {}),
            "show_when": self.options.get("show_when", "equals"),
        }
