"""
Base adapter interface for framework integration.

Defines the contract that all framework adapters must implement.
"""

from abc import ABC, abstractmethod
from typing import Any

from ..core.engine import MongloEngine


class BaseAdapter(ABC):
    """Abstract base class for framework adapters.

    All framework adapters (FastAPI, Flask, Django, Starlette) must
    inherit from this class and implement the required methods.

    Attributes:
        engine: MongloEngine instance
        prefix: URL prefix for admin routes
    """

    def __init__(self, engine: MongloEngine, prefix: str = "/api/admin"):
        """Initialize adapter.

        Args:
            engine: MongloEngine instance
            prefix: URL prefix for admin routes
        """
        self.engine = engine
        self.prefix = prefix

    @abstractmethod
    def create_routes(self) -> Any:
        """Create framework-specific routes/views.

        Returns:
            Framework-specific router/blueprint/urlconf object
        """
        pass

    @abstractmethod
    async def list_collections_handler(self) -> dict[str, Any]:
        """Handle listing all collections.

        Returns:
            List of collections with metadata
        """
        pass

    @abstractmethod
    async def list_documents_handler(
        self,
        collection: str,
        page: int,
        per_page: int,
        search: str | None,
        sort: str | None,
        filters: dict | None,
    ) -> dict[str, Any]:
        """Handle listing documents in a collection.

        Args:
            collection: Collection name
            page: Page number
            per_page: Results per page
            search: Search query
            sort: Sort specification
            filters: Filter criteria

        Returns:
            Paginated list of documents
        """
        pass

    @abstractmethod
    async def get_document_handler(self, collection: str, id: str) -> dict[str, Any]:
        """Handle getting a single document.

        Args:
            collection: Collection name
            id: Document ID

        Returns:
            Document data
        """
        pass

    @abstractmethod
    async def create_document_handler(
        self, collection: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle creating a document.

        Args:
            collection: Collection name
            data: Document data

        Returns:
            Created document
        """
        pass

    @abstractmethod
    async def update_document_handler(
        self, collection: str, id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle updating a document.

        Args:
            collection: Collection name
            id: Document ID
            data: Update data

        Returns:
            Updated document
        """
        pass

    @abstractmethod
    async def delete_document_handler(self, collection: str, id: str) -> dict[str, Any]:
        """Handle deleting a document.

        Args:
            collection: Collection name
            id: Document ID

        Returns:
            Deletion confirmation
        """
        pass

    def _serialize_document(self, doc: dict[str, Any]) -> dict[str, Any]:
        """Serialize document for JSON response.

        Common utility for all adapters to handle ObjectId, datetime, etc.

        Args:
            doc: Document to serialize

        Returns:
            Serialized document
        """
        from ..serializers.json import JSONSerializer

        serializer = JSONSerializer()
        return serializer._serialize_value(doc)

    def _parse_sort(self, sort: str | None) -> list[tuple[str, int]] | None:
        """Parse sort string into MongoDB sort specification.

        Args:
            sort: Sort string (e.g., "name:asc", "created_at:desc")

        Returns:
            MongoDB sort specification or None
        """
        if not sort:
            return None

        parts = sort.split(":")
        if len(parts) != 2:
            return None

        field, direction = parts
        return [(field, -1 if direction == "desc" else 1)]
