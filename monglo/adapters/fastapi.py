"""
FastAPI adapter for Monglo.

Auto-generates REST API endpoints for MongoDB collections.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from ..core.engine import MongloEngine
from ..core.registry import CollectionAdmin
from ..operations.crud import CRUDOperations
from ..serializers.json import JSONSerializer
from ..views.document_view import DocumentView
from ..views.table_view import TableView


class FastAPIAdapter:
    """FastAPI adapter for Monglo.

    Automatically generates REST endpoints for all registered collections.

    Example:
        >>> from fastapi import FastAPI
        >>> app = FastAPI()
        >>> adapter = FastAPIAdapter(engine)
        >>> app.include_router(adapter.router, prefix="/admin")
    """

    def __init__(self, engine: MongloEngine, prefix: str = "/api/admin") -> None:
        """Initialize FastAPI adapter.

        Args:
            engine: MongloEngine instance
            prefix: URL prefix for admin routes
        """
        self.engine = engine
        self.prefix = prefix
        self.router = APIRouter(prefix=prefix, tags=["monglo-admin"])
        self.serializer = JSONSerializer()

        # Generate routes for all collections
        self._generate_routes()

    def _generate_routes(self) -> None:
        """Generate routes for all registered collections."""

        # Index route
        @self.router.get("/")
        async def list_collections():
            """List all available collections."""
            collections = []
            for name, admin in self.engine.registry._collections.items():
                collections.append(
                    {
                        "name": name,
                        "display_name": admin.display_name,
                        "count": await admin.collection.count_documents({}),
                    }
                )
            return {"collections": collections}

        # Generate collection-specific routes
        for name, admin in self.engine.registry._collections.items():
            self._add_collection_routes(name, admin)

    def _add_collection_routes(self, collection_name: str, admin: CollectionAdmin) -> None:
        """Add routes for a specific collection.

        Args:
            collection_name: Collection name
            admin: CollectionAdmin instance
        """
        crud = CRUDOperations(admin)

        # List documents
        @self.router.get(f"/{collection_name}")
        async def list_documents(
            page: int = Query(1, ge=1),
            per_page: int = Query(20, ge=1, le=100),
            search: str | None = None,
            sort: str | None = None,
        ):
            """List documents with pagination and filtering."""
            # Parse sort
            sort_list = None
            if sort:
                parts = sort.split(":")
                if len(parts) == 2:
                    sort_list = [(parts[0], -1 if parts[1] == "desc" else 1)]

            result = await crud.list(page=page, per_page=per_page, search=search, sort=sort_list)

            # Serialize items
            result["items"] = [self._serialize_doc(doc) for doc in result["items"]]

            return result

        # Get single document
        @self.router.get(f"/{collection_name}/{{id}}")
        async def get_document(id: str):
            """Get a single document by ID."""
            try:
                doc = await crud.get(id)
                return self._serialize_doc(doc)
            except (ValueError, KeyError) as e:
                raise HTTPException(status_code=404, detail=str(e)) from e

        # Create document
        @self.router.post(f"/{collection_name}")
        async def create_document(data: dict[str, Any]):
            """Create a new document."""
            try:
                doc = await crud.create(data)
                return self._serialize_doc(doc)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e)) from e

        # Update document
        @self.router.put(f"/{collection_name}/{{id}}")
        async def update_document(id: str, data: dict[str, Any]):
            """Update an existing document."""
            try:
                doc = await crud.update(id, data)
                return self._serialize_doc(doc)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e)) from e
            except KeyError as e:
                raise HTTPException(status_code=404, detail=str(e)) from e

        # Delete document
        @self.router.delete(f"/{collection_name}/{{id}}")
        async def delete_document(id: str):
            """Delete a document."""
            try:
                deleted = await crud.delete(id)
                if not deleted:
                    raise HTTPException(status_code=404, detail="Document not found")
                return {"success": True, "id": id}
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e)) from e

        # Table view config
        @self.router.get(f"/{collection_name}/config/table")
        async def get_table_config():
            """Get table view configuration."""
            table_view = TableView(admin)
            return table_view.render_config()

        # Document view config
        @self.router.get(f"/{collection_name}/config/document")
        async def get_document_config():
            """Get document view configuration."""
            doc_view = DocumentView(admin)
            # Would use schema from introspection in real usage
            return doc_view.render_config()

    def _serialize_doc(self, doc: dict[str, Any]) -> dict[str, Any]:
        """Serialize a document for JSON response.

        Args:
            doc: Document to serialize

        Returns:
            Serialized document
        """
        # Use the serializer's internal method
        return self.serializer._serialize_value(doc)


def create_fastapi_router(engine: MongloEngine, prefix: str = "/api/admin") -> APIRouter:
    """Create FastAPI router for Monglo admin.

    Convenience function for quick setup.

    Args:
        engine: MongloEngine instance
        prefix: URL prefix

    Returns:
        Configured APIRouter

    Example:
        >>> from fastapi import FastAPI
        >>> app = FastAPI()
        >>> router = create_fastapi_router(engine)
        >>> app.include_router(router)
    """
    adapter = FastAPIAdapter(engine, prefix=prefix)
    return adapter.router
