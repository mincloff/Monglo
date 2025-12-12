"""
Base widget interface for field rendering.

Widgets define how fields should be rendered in the UI (forms, displays, inputs).
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseWidget(ABC):
    """Abstract base class for all widgets.
    
    Widgets provide configuration for how fields should be rendered
    in the admin interface. They generate JSON configuration that the
    frontend uses to render appropriate UI components.
    """
    
    def __init__(self, **options):
        """Initialize widget with options.
        
        Args:
            **options: Widget-specific configuration options
        """
        self.options = options
    
    @abstractmethod
    def render_config(self) -> dict[str, Any]:
        """Generate widget configuration for frontend.
        
        Returns:
            Dictionary with widget type and options
        """
        pass
    
    def validate(self, value: Any) -> bool:
        """Validate a value for this widget.
        
        Args:
            value: Value to validate
            
        Returns:
            True if valid, False otherwise
        """
        return True  # Override in subclasses for specific validation
