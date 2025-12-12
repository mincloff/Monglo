"""
Django adapter for Monglo.

AUTO-CREATES ALL URL PATTERNS - Developers never touch routing!

Example:
    >>> # In urls.py
    >>> from monglo.adapters.django import create_django_urls
    >>> from monglo import MongloEngine
    >>> 
    >>> engine = MongloEngine(database=db, auto_discover=True)
    >>> await engine.initialize()
    >>> 
    >>> urlpatterns = [
    ...     *create_django_urls(engine, prefix="api/admin"),
    ... ]
"""

from __future__ import annotations

from typing import TYPE_CHECKING
import json

from django.http import JsonResponse
from django.urls import path
from django.views import View

if TYPE_CHECKING:
    from ..core.engine import MongloEngine


def create_django_urls(engine: MongloEngine, prefix: str = "api/admin"):
    """
    Create Django URL patterns with ALL routes automatically.
    
    This creates a complete REST API for all registered collections.
    Developers NEVER need to define routes manually.
    
    Args:
        engine: Initialized MongloEngine instance
        prefix: URL prefix for API
    
    Returns:
        List of URL patterns ready to include
    
    Example:
        >>> engine = MongloEngine(database=db, auto_discover=True)
        >>> await engine.initialize()
        >>> 
        >>> # That's it - full API with all routes!
       >>> urlpatterns = [*create_django_urls(engine)]
    """
    
    # Collections list view
    class CollectionsListView(View):
        async def get(self, request):
            """List all collections."""
            collections = []
            
            for name, admin in engine.registry._collections.items():
                count = await admin.collection.count_documents({})
                collections.append({
                    "name": name,
                    "display_name": admin.display_name,
                    "count": count,
                    "relationships": len(admin.relationships)
                })
            
            return JsonResponse({"collections": collections})
    
    # Collection operations view
    class CollectionListCreateView(View):
        async def get(self, request, collection):
            """List documents with pagination, search, filters."""
            from ..operations.crud import CRUDOperations
            from ..serializers.json import JSONSerializer
            
            # Get query params
            page = int(request.GET.get("page", 1))
            per_page = int(request.GET.get("per_page", 20))
            search = request.GET.get("search", "")
            sort_by = request.GET.get("sort_by", "")
            sort_dir = request.GET.get("sort_dir", "asc")
            
            # Get collection admin
            admin = engine.registry.get(collection)
            
            # Build sort
            sort_list = None
            if sort_by:
                sort_list = [(sort_by, -1 if sort_dir == "desc" else 1)]
            
            # Get data
            crud = CRUDOperations(admin)
            data = await crud.list(
                page=page,
                per_page=per_page,
                search=search if search else None,
                sort=sort_list
            )
            
            # Serialize
            serializer = JSONSerializer()
            serialized_items = [serializer._serialize_value(item) for item in data["items"]]
            
            return JsonResponse({
                **data,
                "items": serialized_items
            })
        
        async def post(self, request, collection):
            """Create new document."""
            from ..operations.crud import CRUDOperations
            from ..serializers.json import JSONSerializer
            
            data = json.loads(request.body)
            
            admin = engine.registry.get(collection)
            crud = CRUDOperations(admin)
            
            created = await crud.create(data)
            
            # Serialize
            serializer = JSONSerializer()
            serialized = serializer._serialize_value(created)
            
            return JsonResponse({"success": True, "document": serialized}, status=201)
    
    # Document operations view
    class DocumentDetailView(View):
        async def get(self, request, collection, id):
            """Get single document."""
            from ..operations.crud import CRUDOperations
            from ..serializers.json import JSONSerializer
            
            admin = engine.registry.get(collection)
            crud = CRUDOperations(admin)
            
            try:
                document = await crud.get(id)
            except KeyError:
                return JsonResponse({"error": "Document not found"}, status=404)
            
            # Serialize
            serializer = JSONSerializer()
            serialized = serializer._serialize_value(document)
            
            return JsonResponse({"document": serialized})
        
        async def put(self, request, collection, id):
            """Update document."""
            from ..operations.crud import CRUDOperations
            from ..serializers.json import JSONSerializer
            
            data = json.loads(request.body)
            
            admin = engine.registry.get(collection)
            crud = CRUDOperations(admin)
            
            try:
                updated = await crud.update(id, data)
            except KeyError:
               return JsonResponse({"error": "Document not found"}, status=404)
            
            # Serialize
            serializer = JSONSerializer()
            serialized = serializer._serialize_value(updated)
            
            return JsonResponse({"success": True, "document": serialized})
        
        async def delete(self, request, collection, id):
            """Delete document."""
            from ..operations.crud import CRUDOperations
            
            admin = engine.registry.get(collection)
            crud = CRUDOperations(admin)
            
            try:
                await crud.delete(id)
            except KeyError:
                return JsonResponse({"error": "Document not found"}, status=404)
            
            return JsonResponse({"success": True, "message": "Document deleted"})
    
    # View configuration views
    class TableConfigView(View):
        async def get(self, request, collection):
            """Get table view configuration."""
            from ..views.table_view import TableView
            
            admin = engine.registry.get(collection)
            view = TableView(admin)
            config = view.render_config()
            
            return JsonResponse({"config": config})
    
    class DocumentConfigView(View):
        async def get(self, request, collection):
            """Get document view configuration."""
            from ..views.document_view import DocumentView
            
            admin = engine.registry.get(collection)
            view = DocumentView(admin)
            config = view.render_config()
            
            return JsonResponse({"config": config})
    
    class RelationshipsView(View):
        async def get(self, request, collection):
            """Get collection relationships."""
            admin = engine.registry.get(collection)
            
            relationships = [
                {
                    "source_field": rel.source_field,
                    "target_collection": rel.target_collection,
                    "type": rel.type.value
                }
                for rel in admin.relationships
            ]
            
            return JsonResponse({"relationships": relationships})
    
    # Auto-generate all URL patterns
    return [
        path(f"{prefix}/", CollectionsListView.as_view(), name="monglo_collections_list"),
        path(f"{prefix}/<str:collection>/", CollectionListCreateView.as_view(), name="monglo_collection_list"),
        path(f"{prefix}/<str:collection>/<str:id>/", DocumentDetailView.as_view(), name="monglo_document_detail"),
        path(f"{prefix}/<str:collection>/config/table/", TableConfigView.as_view(), name="monglo_table_config"),
        path(f"{prefix}/<str:collection>/config/document/", DocumentConfigView.as_view(), name="monglo_document_config"),
        path(f"{prefix}/<str:collection>/relationships/", RelationshipsView.as_view(), name="monglo_relationships"),
    ]
