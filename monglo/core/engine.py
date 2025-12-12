"""
Monglo Engine - The core framework-agnostic MongoDB admin engine.

This module provides the main MongloEngine class that orchestrates
schema introspection, relationship detection, and collection management.
"""

from __future__ import annotations

from typing import Any, Literal

from motor.motor_asyncio import AsyncIOMotorDatabase

from .config import CollectionConfig
from .introspection import SchemaIntrospector
from .registry import CollectionAdmin, CollectionRegistry
from .relationships import RelationshipDetector


class MongloEngine:
    """Framework-agnostic MongoDB administration engine.

    The MongloEngine is the central component of Monglo. It provides:
    - Automatic collection discovery
    - Schema introspection
    - Intelligent relationship detection
    - Collection registry management
    - Framework adapter integration

    This class has no web framework dependencies and can be used standalone
    or integrated with FastAPI, Flask, Django, or any Python web framework.

    Attributes:
        db: Motor database instance
        registry: Collection registry
        introspector: Schema introspector
        relationship_detector: Relationship detector

    Example:
        >>> from motor.motor_asyncio import AsyncIOMotorClient
        >>> client = AsyncIOMotorClient("mongodb://localhost:27017")
        >>> db = client.myapp
        >>>
        >>> engine = MongloEngine(database=db, auto_discover=True)
        >>> await engine.initialize()
        >>>
        >>> # Access collections
        >>> users_admin = engine.registry.get("users")
    """

    def __init__(
        self,
        database: AsyncIOMotorDatabase,
        *,
        auto_discover: bool = False,
        relationship_detection: Literal["auto", "manual", "off"] = "auto",
        excluded_collections: list[str] | None = None,
    ) -> None:
        """Initialize the Monglo engine.

        Args:
            database: Motor async database instance
            auto_discover: Automatically discover and register all collections
            relationship_detection: Relationship detection mode:
                - "auto": Automatically detect relationships
                - "manual": Only use manually configured relationships
                - "off": Disable relationship detection
            excluded_collections: Collection names to exclude from auto-discovery

        Example:
            >>> engine = MongloEngine(
            ...     database=db,
            ...     auto_discover=True,
            ...     excluded_collections=["migrations", "sessions"]
            ... )
        """
        self.db = database
        self._auto_discover = auto_discover
        self._relationship_detection = relationship_detection
        self._excluded_collections = set(excluded_collections or [])

        # Core components
        self.registry = CollectionRegistry()
        self.introspector = SchemaIntrospector(database)
        self.relationship_detector = RelationshipDetector(database)

        # Track if engine is initialized
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the engine and perform auto-discovery if enabled.

        This should be called once after engine creation, typically at
        application startup.

        Example:
            >>> engine = MongloEngine(database=db, auto_discover=True)
            >>> await engine.initialize()
        """
        if self._initialized:
            return

        if self._auto_discover:
            await self._discover_collections()

        self._initialized = True

    async def register_collection(
        self, name: str, *, config: CollectionConfig | None = None
    ) -> CollectionAdmin:
        """Register a collection with the engine.

        If no configuration is provided, the engine will automatically
        introspect the collection's schema and detect relationships.

        Args:
            name: Collection name
            config: Optional collection configuration

        Returns:
            CollectionAdmin instance for the registered collection

        Raises:
            ValueError: If collection is already registered

        Example:
            >>> # Auto-configuration
            >>> admin = await engine.register_collection("users")
            >>>
            >>> # Manual configuration
            >>> admin = await engine.register_collection(
            ...     "products",
            ...     config=CollectionConfig(
            ...         list_fields=["name", "price", "stock"],
            ...         search_fields=["name", "description"]
            ...     )
            ... )
        """
        # Check if already registered
        if name in self.registry:
            raise ValueError(f"Collection '{name}' is already registered")

        # Auto-introspect if no config provided
        if config is None:
            schema = await self.introspector.introspect(name)
            config = CollectionConfig.from_schema(schema)
            config.name = name

        # Set config name if not already set
        if not config.name:
            config.name = name

        # Detect relationships
        relationships = []
        if self._relationship_detection in ["auto", "manual"]:
            if self._relationship_detection == "auto":
                relationships = await self.relationship_detector.detect(name, config)
            elif self._relationship_detection == "manual" and config.relationships:
                relationships = config.relationships

        # Create collection admin
        collection_admin = CollectionAdmin(
            name=name, database=self.db, config=config, relationships=relationships
        )

        # Register
        self.registry.register(collection_admin)

        return collection_admin

    async def unregister_collection(self, name: str) -> None:
        """Remove a collection from the registry.

        Args:
            name: Collection name to unregister

        Example:
            >>> await engine.unregister_collection("temp_collection")
        """
        self.registry.unregister(name)

    async def _discover_collections(self) -> None:
        """Discover and auto-register all collections in the database.

        Internal method called during initialization if auto_discover is True.
        """
        # Get all collection names
        collection_names = await self.db.list_collection_names()

        # Filter out system collections and excluded collections
        system_prefixes = ("system.",)
        collections_to_register = [
            name
            for name in collection_names
            if not name.startswith(system_prefixes) and name not in self._excluded_collections
        ]

        # Register each collection
        for name in collections_to_register:
            try:
                await self.register_collection(name)
            except Exception as e:
                # Log error but continue with other collections
                print(f"Warning: Failed to register collection '{name}': {e}")

    def get_adapter(self, framework: str):
        """Get a framework adapter for web integration.

        Args:
            framework: Framework name ("fastapi", "flask", "django", "starlette")

        Returns:
            Framework-specific adapter instance

        Raises:
            ValueError: If framework is not supported

        Example:
            >>> # FastAPI
            >>> from fastapi import FastAPI
            >>> app = FastAPI()
            >>> adapter = engine.get_adapter("fastapi")
            >>> router = adapter.create_app()
            >>> app.include_router(router)
            >>>
            >>> # Flask
            >>> from flask import Flask
            >>> app = Flask(__name__)
            >>> adapter = engine.get_adapter("flask")
            >>> blueprint = adapter.create_blueprint()
            >>> app.register_blueprint(blueprint)
        """
        framework = framework.lower()

        if framework == "fastapi":
            from ..adapters.fastapi import FastAPIAdapter

            return FastAPIAdapter(self)
        elif framework == "flask":
            from ..adapters.flask import FlaskAdapter

            return FlaskAdapter(self)
        elif framework == "django":
            from ..adapters.django import DjangoAdapter

            return DjangoAdapter(self)
        elif framework == "starlette":
            from ..adapters.starlette import StarletteAdapter

            return StarletteAdapter(self)
        else:
            raise ValueError(
                f"Unsupported framework: {framework}. "
                f"Supported frameworks: fastapi, flask, django, starlette"
            )

    async def get_collection_stats(self) -> dict[str, Any]:
        """Get statistics for all registered collections.

        Returns:
            Dictionary with collection statistics

        Example:
            >>> stats = await engine.get_collection_stats()
            >>> print(f"Total collections: {stats['total_collections']}")
            >>> for coll in stats['collections']:
            ...     print(f"{coll['name']}: {coll['count']} documents")
        """
        stats = {"total_collections": len(self.registry), "collections": []}

        for name, admin in self.registry.items():
            count = await admin.collection.count_documents({})
            stats["collections"].append(
                {
                    "name": name,
                    "display_name": admin.display_name,
                    "document_count": count,
                    "relationship_count": len(admin.relationships),
                }
            )

        return stats

    async def refresh_collection(self, name: str) -> None:
        """Refresh a collection's schema and relationships.

        Re-introspects the schema and re-detects relationships for
        a registered collection. Useful when the collection structure changes.

        Args:
            name: Collection name to   refresh

        Example:
            >>> # After schema changes
            >>> await engine.refresh_collection("users")
        """
        if name not in self.registry:
            raise KeyError(f"Collection '{name}' is not registered")

        # Unregister and re-register
        await self.unregister_collection(name)
        await self.register_collection(name)
