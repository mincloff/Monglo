"""
Flask adapter for Monglo.

AUTO-CREATES ALL API ROUTES - Developers never touch routing!

Example:
    >>> from monglo.adapters.flask import create_flask_blueprint
    >>> from monglo import MongloEngine
    >>> 
    >>> engine = Monglo Engine(database=db, auto_discover=True)
    >>> await engine.initialize()
    >>> 
    >>> # Get complete API blueprint with ALL routes
    >>> api_bp = create_flask_blueprint(engine, url_prefix="/api/admin")
    >>> app.register_blueprint(api_bp)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flask import Blueprint, jsonify, request

if TYPE_CHECKING:
    from ..core.engine import MongloEngine


def create_flask_blueprint(
    engine: MongloEngine,
    name: str = "monglo_api",
    url_prefix: str = "/api/admin"
) -> Blueprint:
    """
    Create Flask blueprint with ALL API routes automatically.
    
    This creates a complete REST API for all registered collections.
    Developers NEVER need to define routes manually.
    
    Args:
        engine: Initialized MongloEngine instance
        name: Blueprint name
        url_prefix: URL prefix for API
    
    Returns:
        Flask blueprint with all routes configured
    
    Example:
        >>> engine = MongloEngine(database=db, auto_discover=True)
        >>> await engine.initialize()
        >>> 
        >>> # That's it - full API with all routes!
        >>> app.register_blueprint(create_flask_blueprint(engine))
    """
    bp = Blueprint(name, __name__, url_prefix=url_prefix)
    
    # ==================== COLLECTIONS LIST ====================
    
    @bp.route("/", methods=["GET"])
    async def list_collections():
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
        
        return jsonify({"collections": collections})
    
    # ==================== COLLECTION ROUTES (Auto-generated for each) ====================
    
    @bp.route("/<collection>", methods=["GET"])
    async def list_documents(collection: str):
        """List documents in collection with pagination, search, filters."""
        from ..operations.crud import CRUDOperations
        from ..serializers.json import JSONSerializer
        
        # Get query params
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
        search = request.args.get("search", "")
        sort_by = request.args.get("sort_by", "")
        sort_dir = request.args.get("sort_dir", "asc")
        
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
        
        return jsonify({
            **data,
            "items": serialized_items
        })
    
    @bp.route("/<collection>/<id>", methods=["GET"])
    async def get_document(collection: str, id: str):
        """Get single document by ID."""
        from ..operations.crud import CRUDOperations
        from ..serializers.json import JSONSerializer
        
        admin = engine.registry.get(collection)
        crud = CRUDOperations(admin)
        
        try:
            document = await crud.get(id)
        except KeyError:
            return jsonify({"error": "Document not found"}), 404
        
        # Serialize
        serializer = JSONSerializer()
        serialized = serializer._serialize_value(document)
        
        return jsonify({"document": serialized})
    
    @bp.route("/<collection>", methods=["POST"])
    async def create_document(collection: str):
        """Create new document."""
        from ..operations.crud import CRUDOperations
        from ..serializers.json import JSONSerializer
        
        data = request.get_json()
        
        admin = engine.registry.get(collection)
        crud = CRUDOperations(admin)
        
        created = await crud.create(data)
        
        # Serialize
        serializer = JSONSerializer()
        serialized = serializer._serialize_value(created)
        
        return jsonify({"success": True, "document": serialized}), 201
    
    @bp.route("/<collection>/<id>", methods=["PUT"])
    async def update_document(collection: str, id: str):
        """Update document."""
        from ..operations.crud import CRUDOperations
        from ..serializers.json import JSONSerializer
        
        data = request.get_json()
        
        admin = engine.registry.get(collection)
        crud = CRUDOperations(admin)
        
        try:
            updated = await crud.update(id, data)
        except KeyError:
            return jsonify({"error": "Document not found"}), 404
        
        # Serialize
        serializer = JSONSerializer()
        serialized = serializer._serialize_value(updated)
        
        return jsonify({"success": True, "document": serialized})
    
    @bp.route("/<collection>/<id>", methods=["DELETE"])
    async def delete_document(collection: str, id: str):
        """Delete document."""
        from ..operations.crud import CRUDOperations
        
        admin = engine.registry.get(collection)
        crud = CRUDOperations(admin)
        
        try:
            await crud.delete(id)
        except KeyError:
            return jsonify({"error": "Document not found"}), 404
        
        return jsonify({"success": True, "message": "Document deleted"})
    
    # ==================== VIEW CONFIGURATION ROUTES ====================
    
    @bp.route("/<collection>/config/table", methods=["GET"])
    async def get_table_config(collection: str):
        """Get table view configuration."""
        from ..views.table_view import TableView
        
        admin = engine.registry.get(collection)
        view = TableView(admin)
        config = view.render_config()
        
        return jsonify({"config": config})
    
    @bp.route("/<collection>/config/document", methods=["GET"])
    async def get_document_config(collection: str):
        """Get document view configuration."""
        from ..views.document_view import DocumentView
        
        admin = engine.registry.get(collection)
        view = DocumentView(admin)
        config = view.render_config()
        
        return jsonify({"config": config})
    
    @bp.route("/<collection>/relationships", methods=["GET"])
    async def get_relationships(collection: str):
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
        
        return jsonify({"relationships": relationships})
    
    return bp
