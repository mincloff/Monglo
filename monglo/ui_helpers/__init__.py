"""
UI Helpers - Framework-specific UI integration.

Provides automatic admin interface setup for different frameworks.
"""

from .fastapi import create_ui_router

__all__ = ["create_ui_router"]
