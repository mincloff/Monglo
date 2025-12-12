"""
Relationship graph view for visualizing collection relationships.

Provides D3.js-compatible graph data structures for relationship visualization.
"""

from typing import Any
from ..core.registry import CollectionAdmin
from .base import BaseView


class RelationshipView(BaseView):
    """Relationship graph visualization view.
    
    Generates configuration for D3.js force-directed graph visualization
    of collection relationships.
    
    Example output format:
        {
            "type": "graph",
            "nodes": [
                {"id": "users", "label": "Users", "type": "collection"},
                {"id": "orders", "label": "Orders", "type": "collection"}
            ],
            "edges": [
                {
                    "source": "orders",
                    "target": "users",
                    "label": "user_id",
                    "type": "one_to_one"
                }
            ],
            "layout": "force-directed"
        }
    """
    
    def __init__(self, collection_admin: CollectionAdmin):
        """Initialize relationship view.
        
        Args:
            collection_admin: Collection admin instance
        """
        self.collection = collection_admin
        self.engine = None  # Will be set by adapter if needed
    
    def render_config(self) -> dict[str, Any]:
        """Generate relationship graph configuration.
        
        Returns:
            D3.js-compatible graph structure
        """
        return {
            "type": "graph",
            "collection": self.collection.name,
            "nodes": self._build_nodes(),
            "edges": self._build_edges(),
            "layout": "force-directed",
            "options": {
                "nodeRadius": 30,
                "linkDistance": 150,
                "charge": -300,
                "gravity": 0.1
            }
        }
    
    def _build_nodes(self) -> list[dict[str, Any]]:
        """Build graph nodes from collection and its relationships.
        
        Returns:
            List of node objects
        """
        nodes = []
        
        # Add current collection as primary node
        nodes.append({
            "id": self.collection.name,
            "label": self.collection.display_name,
            "type": "collection",
            "primary": True,
            "relationshipCount": len(self.collection.relationships)
        })
        
        # Add related collections as secondary nodes
        related_collections = set()
        for rel in self.collection.relationships:
            if rel.target_collection not in related_collections:
                related_collections.add(rel.target_collection)
                nodes.append({
                    "id": rel.target_collection,
                    "label": rel.target_collection.replace("_", " ").title(),
                    "type": "collection",
                    "primary": False
                })
        
        return nodes
    
    def _build_edges(self) -> list[dict[str, Any]]:
        """Build graph edges from relationships.
        
        Returns:
            List of edge objects
        """
        edges = []
        
        for rel in self.collection.relationships:
            edges.append({
                "source": rel.source_collection,
                "target": rel.target_collection,
                "label": rel.source_field,
                "type": rel.type.value,
                "bidirectional": rel.reverse_name is not None,
                "reverseName": rel.reverse_name
            })
        
        return edges
    
    def render_full_graph(self, all_collections: dict[str, CollectionAdmin]) -> dict[str, Any]:
        """Generate full database relationship graph.
        
        Args:
            all_collections: Dictionary of all collection admins
            
        Returns:
            Complete graph of all collections and relationships
        """
        all_nodes = []
        all_edges = []
        seen_edges = set()
        
        # Build nodes for all collections
        for name, admin in all_collections.items():
            all_nodes.append({
                "id": name,
                "label": admin.display_name,
                "type": "collection",
                "relationshipCount": len(admin.relationships)
            })
        
        # Build edges from all relationships
        for name, admin in all_collections.items():
            for rel in admin.relationships:
                # Create unique edge identifier
                edge_id = f"{rel.source_collection}:{rel.source_field}:{rel.target_collection}"
                
                if edge_id not in seen_edges:
                    seen_edges.add(edge_id)
                    all_edges.append({
                        "source": rel.source_collection,
                        "target": rel.target_collection,
                        "label": rel.source_field,
                        "type": rel.type.value,
                        "bidirectional": rel.reverse_name is not None
                    })
        
        return {
            "type": "graph",
            "scope": "database",
            "nodes": all_nodes,
            "edges": all_edges,
            "layout": "force-directed",
            "options": {
                "nodeRadius": 40,
                "linkDistance": 200,
                "charge": -500,
                "gravity": 0.05
            }
        }
