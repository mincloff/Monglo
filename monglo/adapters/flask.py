"""
Flask adapter for Monglo.

Generates Blueprint with admin routes for MongoDB collections.
"""

from __future__ import annotations

from typing import Any
from flask import Blueprint, request, jsonify

from ..core.engine import MongloEngine
from ..core.registry import CollectionAdmin
from ..operations.crud import CRUDOperations
from ..serializers.json import JSONSerializer
from ..views.table_view import TableView
from ..views.document_view import DocumentView


class FlaskAdapter:
    """Flask adapter for Monglo.
    
    Generates a Blueprint with REST endpoints for collections.
    
    Example:
        >>> from flask import Flask
        >>> app = Flask(__name__)
        >>> adapter = FlaskAdapter(engine)
        >>> app.register_blueprint(adapter.blueprint)
    """
    
    def __init__(self, engine: MongloEngine, url_prefix: str = "/api/admin") -> None:
        """Initialize Flask adapter.
        
        Args:
            engine: MongloEngine instance
            url_prefix: URL prefix for routes
        """
        self.engine = engine
        self.blueprint = Blueprint("monglo_admin", __name__, url_prefix=url_prefix)
        self.serializer = JSONSerializer()
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self) -> None:
        """Register all routes."""
        # Index route
        @self.blueprint.route("/", methods=["GET"])
        async def list_collections():
            """List all collections."""
            collections = []
            for name, admin in self.engine.registry._collections.items():
                collections.append({
                    "name": name,
                    "display_name": admin.display_name,
                    "count": await admin.collection.count_documents({})
                })
            return jsonify({"collections": collections})
        
        # Generate collection routes
        for name, admin in self.engine.registry._collections.items():
            self._add_collection_routes(name, admin)
    
    def _add_collection_routes(self, collection_name: str, admin: CollectionAdmin) -> None:
        """Add routes for a collection.
        
        Args:
            collection_name: Collection name
            admin: CollectionAdmin instance
        """
        crud = CRUDOperations(admin)
        
        # List
        @self.blueprint.route(f"/{collection_name}", methods=["GET"])
        async def list_docs():
            page = int(request.args.get("page", 1))
            per_page = int(request.args.get("per_page", 20))
            search = request.args.get("search")
            
            result = await crud.list(page=page, per_page=per_page, search=search)
            result["items"] = [self._serialize_doc(d) for d in result["items"]]
            return jsonify(result)
        
        # Get
        @self.blueprint.route(f"/{collection_name}/<id>", methods=["GET"])
        async def get_doc(id: str):
            try:
                doc = await crud.get(id)
                return jsonify(self._serialize_doc(doc))
            except (ValueError, KeyError) as e:
                return jsonify({"error": str(e)}), 404
        
        # Create
        @self.blueprint.route(f"/{collection_name}", methods=["POST"])
        async def create_doc():
            try:
                data = request.get_json()
                doc = await crud.create(data)
                return jsonify(self._serialize_doc(doc)), 201
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
        
        # Update
        @self.blueprint.route(f"/{collection_name}/<id>", methods=["PUT"])
        async def update_doc(id: str):
            try:
                data = request.get_json()
                doc = await crud.update(id, data)
                return jsonify(self._serialize_doc(doc))
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
            except KeyError as e:
                return jsonify({"error": str(e)}), 404
        
        # Delete
        @self.blueprint.route(f"/{collection_name}/<id>", methods=["DELETE"])
        async def delete_doc(id: str):
            try:
                deleted = await crud.delete(id)
                if not deleted:
                    return jsonify({"error": "Not found"}), 404
                return jsonify({"success": True, "id": id})
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
        
        # Config routes
        @self.blueprint.route(f"/{collection_name}/config/table", methods=["GET"])
        async def table_config():
            table_view = TableView(admin)
            return jsonify(table_view.render_config())
        
        @self.blueprint.route(f"/{collection_name}/config/document", methods=["GET"])
        async def doc_config():
            doc_view = DocumentView(admin)
            return jsonify(doc_view.render_config())
    
    def _serialize_doc(self, doc: dict[str, Any]) -> dict[str, Any]:
        """Serialize document."""
        return self.serializer._serialize_value(doc)


def create_flask_blueprint(engine: MongloEngine, url_prefix: str = "/api/admin") -> Blueprint:
    """Create Flask Blueprint for Monglo.
    
    Args:
        engine: MongloEngine instance
        url_prefix: URL prefix
        
    Returns:
        Configured Blueprint
        
    Example:
        >>> app = Flask(__name__)
        >>> bp = create_flask_blueprint(engine)
        >>> app.register_blueprint(bp)
    """
    adapter = FlaskAdapter(engine, url_prefix=url_prefix)
    return adapter.blueprint
