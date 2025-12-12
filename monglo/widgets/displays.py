"""
Display widgets for read-only field presentation.

Provides labels, badges, links, and other display-only components.
"""

from typing import Any

from .base import BaseWidget


class Label(BaseWidget):
    """Simple text label widget for display.
    
    Example:
        >>> widget = Label(format="bold")
    """
    
    def render_config(self) -> dict[str, Any]:
        return {
            "type": "label",
            "format": self.options.get("format", "normal"),  # normal, bold, italic
            "color": self.options.get("color")
        }


class Badge(BaseWidget):
    """Badge widget for status/tag display.
    
    Example:
        >>> widget = Badge(variant="success")  # success, warning, danger, info
    """
    
    def render_config(self) -> dict[str, Any]:
        return {
            "type": "badge",
            "variant": self.options.get("variant", "default"),
            "color": self.options.get("color"),
            "rounded": self.options.get("rounded", True)
        }


class Link(BaseWidget):
    """Hyperlink widget.
    
    Example:
        >>> widget = Link(target="_blank", format="url")
    """
    
    def render_config(self) -> dict[str, Any]:
        return {
            "type": "link",
            "target": self.options.get("target", "_self"),
            "format": self.options.get("format", "url"),  # url, email
            "show_icon": self.options.get("show_icon", True)
        }


class Image(BaseWidget):
    """Image display widget.
    
    Example:
        >>> widget = Image(width=200, height=200, thumbnail=True)
    """
    
    def render_config(self) -> dict[str, Any]:
        return {
            "type": "image",
            "width": self.options.get("width"),
            "height": self.options.get("height"),
            "thumbnail": self.options.get("thumbnail", True),
            "alt": self.options.get("alt", "Image"),
            "lazy_load": self.options.get("lazy_load", True)
        }


class JSONDisplay(BaseWidget):
    """JSON tree display widget.
    
    Example:
        >>> widget = JSONDisplay(expanded=True, highlight=True)
    """
    
    def render_config(self) -> dict[str, Any]:
        return {
            "type": "json",
            "expanded": self.options.get("expanded", False),
            "highlight": self.options.get("highlight", True),
            "line_numbers": self.options.get("line_numbers", True)
        }


class CodeDisplay(BaseWidget):
    """Code block display widget with syntax highlighting.
    
    Example:
        >>> widget = CodeDisplay(language="python", theme="monokai")
    """
    
    def render_config(self) -> dict[str, Any]:
        return {
            "type": "code",
            "language": self.options.get("language", "text"),
            "theme": self.options.get("theme", "github"),
            "line_numbers": self.options.get("line_numbers", True),
            "copy_button": self.options.get("copy_button", True)
        }


class ProgressBar(BaseWidget):
    """Progress bar widget for numeric values.
    
    Example:
        >>> widget = ProgressBar(min=0, max=100, show_value=True)
    """
    
    def render_config(self) -> dict[str, Any]:
        return {
            "type": "progress",
            "min": self.options.get("min", 0),
            "max": self.options.get("max", 100),
            "show_value": self.options.get("show_value", True),
            "variant": self.options.get("variant", "default")
        }
