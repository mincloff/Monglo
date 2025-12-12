"""
Monglo - A framework-agnostic MongoDB admin library.

Monglo provides intelligent schema introspection, relationship detection,
and dual views (table + document) for MongoDB databases. Works with FastAPI,
Flask, Django, Starlette, or any Python web framework.

Key Features:
    - Framework-agnostic core engine
    - Auto-discovery of MongoDB schemas
    - Intelligent relationship detection
    - Dual view system (table & document views)
    - Async-first with Motor support
    - Extensible fields, widgets, and views
    - Optional authentication system

Example:
    >>> from motor.motor_asyncio import AsyncIOMotorClient
    >>> from monglo import MongloEngine
    >>>
    >>> client = AsyncIOMotorClient("mongodb://localhost:27017")
    >>> db = client.mydb
    >>>
    >>> admin = MongloEngine(database=db, auto_discover=True)
    >>> # Mount to your web framework...

License:
    MIT License - Copyright (c) 2024 Mehar Umar
"""

__version__ = "0.1.0"
__author__ = "Mehar Umar"
__email__ = "contact@meharumar.codes"
__license__ = "MIT"

# Core exports
from .core.config import (
    CollectionConfig,
    DocumentViewConfig,
    FilterConfig,
    TableViewConfig,
)
from .core.engine import MongloEngine
from .core.introspection import SchemaIntrospector
from .core.query_builder import QueryBuilder
from .core.registry import CollectionAdmin, CollectionRegistry
from .core.relationships import (
    Relationship,
    RelationshipDetector,
    RelationshipResolver,
    RelationshipType,
)

# Fields exports
from .fields import (
    BaseField,
    BooleanField,
    DateField,
    DateTimeField,
    DBRefField,
    NumberField,
    ObjectIdField,
    StringField,
)
from .operations.aggregations import AggregationOperations

# Operations exports
from .operations.crud import CRUDOperations
from .operations.export import ExportFormat, ExportOperations, export_collection
from .operations.pagination import PaginationHandler, PaginationStrategy

# Serializers exports
from .serializers import DocumentSerializer, JSONSerializer, TableSerializer

# Views exports
from .views import BaseView, DocumentView, TableView, ViewType

# Adapters (optional - require framework dependencies)
# from .adapters.fastapi import FastAPIAdapter, create_fastapi_router
# from .adapters.flask import FlaskAdapter, create_flask_blueprint
# from .adapters.django import CollectionView, create_django_urls

__all__ = [
    # Metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    # Main engine
    "MongloEngine",
    # Configuration
    "CollectionConfig",
    "TableViewConfig",
    "DocumentViewConfig",
    "FilterConfig",
    # Relationships
    "Relationship",
    "RelationshipType",
    "RelationshipDetector",
    "RelationshipResolver",
    # Registry
    "CollectionAdmin",
    "CollectionRegistry",
    # Utilities
    "SchemaIntrospector",
    "QueryBuilder",
    # Operations
    "CRUDOperations",
    "PaginationHandler",
    "PaginationStrategy",
    "ExportOperations",
    "ExportFormat",
    "export_collection",
    "AggregationOperations",
    # Views
    "BaseView",
    "ViewType",
    "TableView",
    "DocumentView",
    # Serializers
    "JSONSerializer",
    "TableSerializer",
    "DocumentSerializer",
    # Fields
    "BaseField",
    "StringField",
    "NumberField",
    "BooleanField",
    "DateField",
    "DateTimeField",
    "ObjectIdField",
    "DBRefField",
]

