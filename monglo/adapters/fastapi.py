"""
FastAPI adapter for Monglo.

AUTO-CREATES ALL API ROUTES - Developers never touch routing!

Example:
    >>> from monglo.adapters.fastapi import create_fastapi_router
    >>> from monglo import MongloEngine
    >>> 
    >>> engine = MongloEngine(database=db, auto_discover=True)
    >>> await engine.initialize()
    >>> 
    >>> # Get complete API router with ALL routes
    >>> api_router = create_fastapi_router(engine, prefix="/api/admin")
    >>> app.include_router(api_router)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from fastapi import APIRouter, Query, HTTPException, status

if TYPE_CHECKING:
    from ..core.engine import MongloEngine


def create_fastapi_router(
    engine: MongloEngine,
    prefix: str = "/api/admin",
    tags: list[str] | None = None
) -> APIRouter:
    """
    Create FastAPI router with ALL API routes automatically.
    
    This creates a complete REST API for all registered collections.
    Developers NEVER need to define routes manually.
    
    Args:
        engine: Initialized MongloEngine instance
        prefix: URL prefix for API
        tags: Optional API tags for documentation
    
    Returns:
        FastAPI router with all routes configured
    
    Example:
        >>> engine = MongloEngine(database=db, auto_discover=True)
        >>> await engine.initialize()
        >>> 
        >>> # That's it - full API with all routes!
        >>> app.include_router(create_fastapi_router(engine))
    """
    router = APIRouter(prefix=prefix, tags=tags or ["Monglo Admin API"])
    
    # ==================== COLLECTIONS LIST ====================
    
    @router.get("/", summary="List all collections")
    async def list_collections():
        """List all registered collections with stats."""
        collections = []
        
        for name, admin in engine.registry._collections.items():
            count = await admin.collection.count_documents({})
            collections.append({
                "name": name,
                "display_name": admin.display_name,
                "count": count,
                "relationships": len(admin.relationships)
            })
        
        return {"collections": collections}
    
    # ==================== COLLECTION ROUTES ====================
    
    @router.get("/{collection}", summary="List documents")
    async def list_documents(
        collection: str,
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(20, ge=1, le=100, description="Items per page"),
        search: Optional[str] = Query(None, description="Search query"),
        sort_by: Optional[str] = Query(None, description="Field to sort by"),
        sort_dir: str = Query("asc", regex="^(asc|desc)$", description="Sort direction")
    ):
        """List documents in collection with pagination, search, and sorting."""
        from ..operations.crud import CRUDOperations
        from ..serializers.json import JSONSerializer
        
        # Get collection admin
        try:
            admin = engine.registry.get(collection)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{collection}' not found"
            )
        
        # Build sort
        sort_list = None
        if sort_by:
            sort_list = [(sort_by, -1 if sort_dir == "desc" else 1)]
        
        # Get data
        crud = CRUDOperations(admin)
        data = await crud.list(
            page=page,
            per_page=per_page,
            search=search,
            sort=sort_list
        )
        
        # Serialize
        serializer = JSONSerializer()
        serialized_items = [serializer._serialize_value(item) for item in data["items"]]
        
        return {
            **data,
            "items": serialized_items
        }
    
    @router.get("/{collection}/{id}", summary="Get document")
    async def get_document(collection: str, id: str):
        """Get single document by ID."""
        from ..operations.crud import CRUDOperations
        from ..serializers.json import JSONSerializer
        
        try:
            admin = engine.registry.get(collection)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{collection}' not found"
            )
        
        crud = CRUDOperations(admin)
        
        try:
            document = await crud.get(id)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID '{id}' not found"
            )
        
        # Serialize
        serializer = JSONSerializer()
        serialized = serializer._serialize_value(document)
        
        return {"document": serialized}
    
    @router.post("/{collection}", summary="Create document", status_code=status.HTTP_201_CREATED)
    async def create_document(collection: str, data: dict):
        """Create new document."""
        from ..operations.crud import CRUDOperations
        from ..serializers.json import JSONSerializer
        
        try:
            admin = engine.registry.get(collection)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{collection}' not found"
            )
        
        crud = CRUDOperations(admin)
        created = await crud.create(data)
        
        # Serialize
        serializer = JSONSerializer()
        serialized = serializer._serialize_value(created)
        
        return {"success": True, "document": serialized}
    
    @router.put("/{collection}/{id}", summary="Update document")
    async def update_document(collection: str, id: str, data: dict):
        """Update document."""
        from ..operations.crud import CRUDOperations
        from ..serializers.json import JSONSerializer
        
        try:
            admin = engine.registry.get(collection)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{collection}' not found"
            )
        
        crud = CRUDOperations(admin)
        
        try:
            updated = await crud.update(id, data)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID '{id}' not found"
            )
        
        # Serialize
        serializer = JSONSerializer()
        serialized = serializer._serialize_value(updated)
        
        return {"success": True, "document": serialized}
    
    @router.delete("/{collection}/{id}", summary="Delete document")
    async def delete_document(collection: str, id: str):
        """Delete document."""
        from ..operations.crud import CRUDOperations
        
        try:
            admin = engine.registry.get(collection)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{collection}' not found"
            )
        
        crud = CRUDOperations(admin)
        
        try:
            await crud.delete(id)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID '{id}' not found"
            )
        
        return {"success": True, "message": "Document deleted"}
    
    # ==================== VIEW CONFIGURATION ROUTES ====================
    
    @router.get("/{collection}/config/table", summary="Get table view config")
    async def get_table_config(collection: str):
        """Get table view configuration."""
        from ..views.table_view import TableView
        
        try:
            admin = engine.registry.get(collection)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{collection}' not found"
            )
        
        view = TableView(admin)
        config = view.render_config()
        
        return {"config": config}
    
    @router.get("/{collection}/config/document", summary="Get document view config")
    async def get_document_config(collection: str):
        """Get document view configuration."""
        from ..views.document_view import DocumentView
        
        try:
            admin = engine.registry.get(collection)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{collection}' not found"
            )
        
        view = DocumentView(admin)
        config = view.render_config()
        
        return {"config": config}
    
    @router.get("/{collection}/relationships", summary="Get relationships")
    async def get_relationships(collection: str):
        """Get collection relationships."""
        try:
            admin = engine.registry.get(collection)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{collection}' not found"
            )
        
        relationships = [
            {
                "source_field": rel.source_field,
                "target_collection": rel.target_collection,
                "type": rel.type.value
            }
            for rel in admin.relationships
        ]
        
        return {"relationships": relationships}
    
    return router
