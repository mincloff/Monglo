"""
Django adapter for Monglo.

Provides ViewSet and URL patterns for MongoDB collections.
"""

from __future__ import annotations

from typing import Any
from django.http import JsonResponse
from django.views import View
from django.urls import path

from ..core.engine import MongloEngine
from ..core.registry import CollectionAdmin
from ..operations.crud import CRUDOperations
from ..serializers.json import JSONSerializer
from ..views.table_view import TableView
from ..views.document_view import DocumentView


class CollectionView(View):
    """Base view for collection operations."""
    
    def __init__(self, admin: CollectionAdmin, **kwargs):
        super().__init__(**kwargs)
        self.admin = admin
        self.crud = CRUDOperations(admin)
        self.serializer = JSONSerializer()
    
    async def get(self, request, id=None):
        """GET handler."""
        try:
            if id:
                # Get single document
                doc = await self.crud.get(id)
                return JsonResponse(self._serialize_doc(doc))
            else:
                # List documents
                page = int(request.GET.get("page", 1))
                per_page = int(request.GET.get("per_page", 20))
                search = request.GET.get("search")
                
                result = await self.crud.list(page=page, per_page=per_page, search=search)
                result["items"] = [self._serialize_doc(d) for d in result["items"]]
                return JsonResponse(result)
        except (ValueError, KeyError) as e:
            return JsonResponse({"error": str(e)}, status=404)
    
    async def post(self, request):
        """POST handler - create document."""
        try:
            import json
            data = json.loads(request.body)
            doc = await self.crud.create(data)
            return JsonResponse(self._serialize_doc(doc), status=201)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)
    
    async def put(self, request, id):
        """PUT handler - update document."""
        try:
            import json
            data = json.loads(request.body)
            doc = await self.crud.update(id, data)
            return JsonResponse(self._serialize_doc(doc))
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except KeyError as e:
            return JsonResponse({"error": str(e)}, status=404)
    
    async def delete(self, request, id):
        """DELETE handler."""
        try:
            deleted = await self.crud.delete(id)
            if not deleted:
                return JsonResponse({"error": "Not found"}, status=404)
            return JsonResponse({"success": True, "id": id})
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)
    
    def _serialize_doc(self, doc: dict[str, Any]) -> dict[str, Any]:
        """Serialize document."""
        return self.serializer._serialize_value(doc)


def create_django_urls(engine: MongloEngine, prefix: str = "admin/api"):
    """Create Django URL patterns for Monglo.
    
    Args:
        engine: MongloEngine instance
        prefix: URL prefix
        
    Returns:
        List of URL patterns
        
    Example:
        >>> urlpatterns = [
        ...     path('', include(create_django_urls(engine)))
        ... ]
    """
    urlpatterns = []
    
    for name, admin in engine.registry._collections.items():
        view = CollectionView.as_view(admin=admin)
        
        # Collection routes
        urlpatterns.extend([
            path(f"{prefix}/{name}/", view, name=f"monglo_{name}_list"),
            path(f"{prefix}/{name}/<str:id>/", view, name=f"monglo_{name}_detail"),
        ])
    
    return urlpatterns
