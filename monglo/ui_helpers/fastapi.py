"""
UI helpers for framework adapters.

Provides built-in UI rendering capabilities for Monglo admin interface.
"""

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Get monglo_ui directory
UI_DIR = Path(__file__).parent.parent.parent / "monglo_ui"
TEMPLATES_DIR = UI_DIR / "templates"
STATIC_DIR = UI_DIR / "static"


class UIHelper:
    """Helper class for rendering Monglo admin UI.

    Automatically handles template rendering, static files, and custom filters.
    """

    def __init__(self):
        """Initialize UI helper with templates and custom filters."""
        self.templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

        # Add custom Jinja2 filters
        self._register_filters()

    def _register_filters(self):
        """Register custom Jinja2 filters for MongoDB types."""
        from datetime import datetime

        from bson import ObjectId

        @self.templates.env.filters.register
        def format_objectid(value: Any) -> str:
            """Format ObjectId as string."""
            if isinstance(value, ObjectId):
                return str(value)
            return str(value) if value else ""

        @self.templates.env.filters.register
        def format_datetime(value: Any) -> str:
            """Format datetime with fallback."""
            if isinstance(value, datetime):
                return value.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(value, str):
                try:
                    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                    return dt.strftime("%Y-%m-%d %H:%M:%S")
                except (ValueError, AttributeError):
                    return value
            return str(value) if value else ""

        @self.templates.env.filters.register
        def to_json(value: Any) -> str:
            """Convert value to JSON string."""
            import json

            from ..serializers.json import JSONSerializer

            serializer = JSONSerializer()
            serialized = serializer._serialize_value(value)
            return json.dumps(serialized, indent=2)

    def render_home(self, request: Request, collections: list[dict]) -> HTMLResponse:
        """Render admin home page.

        Args:
            request: FastAPI request
            collections: List of collection metadata

        Returns:
            Rendered HTML response
        """
        return self.templates.TemplateResponse(
            "admin_home.html", {"request": request, "collections": collections}
        )

    def render_table_view(
        self,
        request: Request,
        collection_name: str,
        documents: list[dict],
        page: int,
        total: int,
        per_page: int,
    ) -> HTMLResponse:
        """Render table view for a collection.

        Args:
            request: FastAPI request
            collection_name: Name of the collection
            documents: List of documents to display
            page: Current page number
            total: Total document count
            per_page: Documents per page

        Returns:
            Rendered HTML response
        """
        pages = (total + per_page - 1) // per_page

        return self.templates.TemplateResponse(
            "table_view.html",
            {
                "request": request,
                "collection_name": collection_name,
                "documents": documents,
                "page": page,
                "total": total,
                "per_page": per_page,
                "pages": pages,
            },
        )

    def render_document_view(
        self, request: Request, collection_name: str, document: dict
    ) -> HTMLResponse:
        """Render document detail view.

        Args:
            request: FastAPI request
            collection_name: Name of the collection
            document: Document to display

        Returns:
            Rendered HTML response
        """
        return self.templates.TemplateResponse(
            "document_view.html",
            {"request": request, "collection_name": collection_name, "document": document},
        )


def create_ui_router(engine: Any, prefix: str = "/admin") -> APIRouter:
    """Create FastAPI router with UI routes.

    Provides ready-to-use admin UI with minimal configuration.

    Args:
        engine: MongloEngine instance
        prefix: URL prefix for UI routes

    Returns:
        Configured APIRouter with UI routes

    Example:
        >>> from fastapi import FastAPI
        >>> from monglo.ui_helpers.fastapi import create_ui_router
        >>>
        >>> app = FastAPI()
        >>> ui_router = create_ui_router(engine, prefix="/admin")
        >>> app.include_router(ui_router)
        >>> # That's it! UI is ready at /admin
    """
    from ..operations.crud import CRUDOperations

    router = APIRouter(prefix=prefix, tags=["monglo-ui"])
    ui = UIHelper()

    # Mount static files
    router.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    # Admin home
    @router.get("/", response_class=HTMLResponse)
    async def admin_home(request: Request):
        """Render admin home page with collection list."""
        collections = []
        for name, admin in engine.registry._collections.items():
            collections.append(
                {
                    "name": name,
                    "display_name": admin.display_name,
                    "count": await admin.collection.count_documents({}),
                }
            )
        return ui.render_home(request, collections)

    # Collection table view
    @router.get("/{collection}/table", response_class=HTMLResponse)
    async def collection_table_view(
        request: Request, collection: str, page: int = 1, search: str | None = None
    ):
        """Render table view for a collection."""
        admin = engine.registry.get(collection)
        crud = CRUDOperations(admin)

        result = await crud.list(page=page, per_page=20, search=search)

        return ui.render_table_view(
            request, collection, result["items"], page, result["total"], result["per_page"]
        )

    # Document detail view
    @router.get("/{collection}/{id}", response_class=HTMLResponse)
    async def document_view(request: Request, collection: str, id: str):
        """Render document detail view."""
        admin = engine.registry.get(collection)
        crud = CRUDOperations(admin)

        document = await crud.get(id)
        return ui.render_document_view(request, collection, document)

    return router
