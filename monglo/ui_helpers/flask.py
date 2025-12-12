"""
Flask UI Helper - Automatic Admin Interface Setup.

Provides a complete, ready-to-use admin UI with zero configuration

.
Developers just call create_ui_blueprint() and everything works.

Example:
    >>> from monglo.ui_helpers.flask import create_ui_blueprint
    >>> from monglo import MongloEngine
    >>> 
    >>> engine = MongloEngine(database=db, auto_discover=True)
    >>> await engine.initialize()
    >>> 
    >>> # Full UI with templates, static files, routing!
    >>> app.register_blueprint(create_ui_blueprint(engine))
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from flask import Blueprint, render_template, request, redirect, url_for, jsonify

if TYPE_CHECKING:
    from ..core.engine import MongloEngine

# Get paths to UI assets
UI_DIR = Path(__file__).parent.parent.parent / "monglo_ui"


def create_ui_blueprint(
    engine: MongloEngine,
    name: str = "monglo_admin",
    url_prefix: str = "/admin",
    title: str = "Monglo Admin",
    logo: str | None = None,
    brand_color: str = "#10b981",
) -> Blueprint:
    """
    Create a complete admin UI blueprint with zero configuration.
    
    This handles everything:
    - Static file serving
    - Template rendering with filters
    - All UI routes
    - Serialization
    
    Args:
        engine: Initialized MongloEngine instance
        name: Blueprint name
        url_prefix: URL prefix for admin
        title: Admin interface title
        logo: Optional logo URL
        brand_color: Primary brand color
    
    Returns:
        Flask blueprint ready to register
    
    Example:
        >>> engine = MongloEngine(database=db, auto_discover=True)
        >>> await engine.initialize()
        >>> 
        >>> app.register_blueprint(create_ui_blueprint(engine))
        >>> # Visit http://localhost:5000/admin
    """
    bp = Blueprint(
        name,
        __name__,
        url_prefix=url_prefix,
        template_folder=str(UI_DIR / "templates"),
        static_folder=str(UI_DIR / "static"),
        static_url_path="/static"
    )
    
    # Register template filters
    _register_filters(bp)
    
    # Add context processor for common variables
    @bp.context_processor
    def inject_globals():
        return {
            "title": title,
            "logo": logo,
            "brand_color": brand_color
        }
    
    # ==================== UI ROUTES ====================
    
    @bp.route("/")
    async def admin_home():
        """Admin home page with collection list."""
        collections = []
        
        for name, admin in engine.registry._collections.items():
            count = await admin.collection.count_documents({})
            collections.append({
                "name": name,
                "display_name": admin.display_name,
                "count": count,
                "relationships": len(admin.relationships)
            })
        
        return render_template(
            "admin_home.html",
            collections=collections,
            current_collection=None
        )
    
    @bp.route("/<collection>")
    async def table_view(collection: str):
        """Table view for a collection."""
        from ..views.table_view import TableView
        from ..operations.crud import CRUDOperations
        
        # Get query params
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
        search = request.args.get("search", "")
        sort = request.args.get("sort", "")
        
        # Get collection admin
        admin = engine.registry.get(collection)
        
        # Parse sort
        sort_list = None
        if sort:
            field, direction = sort.split(":")
            sort_list = [(field, -1 if direction == "desc" else 1)]
        
        # Get data
        crud = CRUDOperations(admin)
        data = await crud.list(
            page=page,
            per_page=per_page,
            search=search if search else None,
            sort=sort_list
        )
        
        # Get view config
        table_view_obj = TableView(admin)
        config = table_view_obj.render_config()
        
        # Get all collections for sidebar
        collections = await _get_all_collections(engine)
        
        return render_template(
            "table_view.html",
            collection=admin,
            config=config,
            data=data,
            collections=collections,
            current_collection=collection
        )
    
    @bp.route("/<collection>/document/<id>")
    async def document_view(collection: str, id: str):
        """Document detail view."""
        from ..views.document_view import DocumentView
        from ..operations.crud import CRUDOperations
        from ..serializers.json import JSONSerializer
        
        # Get collection admin
        admin = engine.registry.get(collection)
        
        # Get document
        crud = CRUDOperations(admin)
        try:
            document = await crud.get(id)
        except KeyError:
            return redirect(url_for(f"{name}.table_view", collection=collection))
        
        # Serialize for template safety
        serializer = JSONSerializer()
        serialized_doc = serializer._serialize_value(document)
        
        # Get view config
        doc_view = DocumentView(admin)
        config = doc_view.render_config()
        
        # Get all collections for sidebar
        collections = await _get_all_collections(engine)
        
        return render_template(
            "document_view.html",
            collection=admin,
            document=serialized_doc,
            config=config,
            relationships=admin.relationships,
            collections=collections,
            current_collection=collection
        )
    
    # ==================== API ROUTES ====================
    
    @bp.route("/<collection>/<id>", methods=["DELETE"])
    async def delete_document(collection: str, id: str):
        """Delete a document."""
        from ..operations.crud import CRUDOperations
        
        admin = engine.registry.get(collection)
        crud = CRUDOperations(admin)
        
        await crud.delete(id)
        return jsonify({"success": True, "message": "Document deleted"})
    
    @bp.route("/<collection>/<id>", methods=["PUT"])
    async def update_document(collection: str, id: str):
        """Update a document."""
        from ..operations.crud import CRUDOperations
        from ..serializers.json import JSONSerializer
        
        data = request.get_json()
        
        admin = engine.registry.get(collection)
        crud = CRUDOperations(admin)
        
        updated = await crud.update(id, data)
        
        # Serialize for JSON response
        serializer = JSONSerializer()
        serialized = serializer._serialize_value(updated)
        
        return jsonify({"success": True, "document": serialized})
    
    @bp.route("/<collection>", methods=["POST"])
    async def create_document(collection: str):
        """Create a new document."""
        from ..operations.crud import CRUDOperations
        from ..serializers.json import JSONSerializer
        
        data = request.get_json()
        
        admin = engine.registry.get(collection)
        crud = CRUDOperations(admin)
        
        created = await crud.create(data)
        
        # Serialize for JSON response
        serializer = JSONSerializer()
        serialized = serializer._serialize_value(created)
        
        return jsonify({"success": True, "document": serialized})
    
    return bp


def _register_filters(bp: Blueprint):
    """Register Jinja2 filters on blueprint."""
    
    @bp.app_template_filter("format_datetime")
    def format_datetime(value):
        """Format datetime for display."""
        if value is None:
            return ""
        from datetime import datetime
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return str(value)
    
    @bp.app_template_filter("type_class")
    def type_class(value):
        """Get CSS class for value type."""
        if isinstance(value, str):
            return "string"
        elif isinstance(value, (int, float)):
            return "number"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, dict):
            return "object"
        elif isinstance(value, list):
            return "array"
        return ""
    
    @bp.app_template_filter("truncate")
    def truncate(s, length=50):
        """Truncate string to length."""
        if not isinstance(s, str):
            s = str(s)
        return s[:length] + '...' if len(s) > length else s


async def _get_all_collections(engine: MongloEngine) -> list[dict[str, Any]]:
    """Get all collections with counts for sidebar."""
    collections = []
    for name, admin in engine.registry._collections.items():
        count = await admin.collection.count_documents({})
        collections.append({
            "name": name,
            "display_name": admin.display_name,
            "count": count
        })
    return collections
