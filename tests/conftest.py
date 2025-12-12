"""
Pytest configuration and shared fixtures for Monglo tests.

Provides database fixtures, sample data, and test utilities.
"""

import pytest
import asyncio
from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from bson import ObjectId

from monglo.core.engine import MongloEngine
from monglo.core.config import CollectionConfig


# Configure pytest-asyncio
@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def mongodb_client() -> AsyncGenerator[AsyncIOMotorClient, None]:
    """Create a MongoDB client for testing.

    Uses a test database to avoid affecting production data.
    Set MONGODB_TEST_URI environment variable to customize connection.
    """
    import os

    # Use test URI or default to localhost
    uri = os.getenv("MONGODB_TEST_URI", "mongodb://localhost:27017")

    client = AsyncIOMotorClient(uri)

    # Test connection
    try:
        await client.admin.command("ping")
    except Exception as e:
        pytest.skip(f"MongoDB not available: {e}")

    yield client

    client.close()


@pytest.fixture
async def test_db(mongodb_client: AsyncIOMotorClient) -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Create a clean test database for each test.

    Database is dropped after each test to ensure isolation.
    """
    db_name = f"monglo_test_{ObjectId()}"
    db = mongodb_client[db_name]

    yield db

    # Cleanup: drop the test database
    await mongodb_client.drop_database(db_name)


@pytest.fixture
async def sample_users(test_db: AsyncIOMotorDatabase) -> list[dict]:
    """Insert sample user documents into test database."""
    users = [
        {
            "_id": ObjectId(),
            "name": "Alice Smith",
            "email": "alice@example.com",
            "age": 30,
            "status": "active",
            "created_at": "2024-01-01T00:00:00Z",
        },
        {
            "_id": ObjectId(),
            "name": "Bob Johnson",
            "email": "bob@example.com",
            "age": 25,
            "status": "active",
            "created_at": "2024-01-02T00:00:00Z",
        },
        {
            "_id": ObjectId(),
            "name": "Charlie Brown",
            "email": "charlie@example.com",
            "age": 35,
            "status": "inactive",
            "created_at": "2024-01-03T00:00:00Z",
        },
    ]

    await test_db.users.insert_many(users)
    return users


@pytest.fixture
async def sample_orders(test_db: AsyncIOMotorDatabase, sample_users: list[dict]) -> list[dict]:
    """Insert sample order documents with references to users."""
    orders = [
        {
            "_id": ObjectId(),
            "user_id": sample_users[0]["_id"],
            "total": 100.50,
            "status": "completed",
            "items": ["item1", "item2"],
        },
        {
            "_id": ObjectId(),
            "user_id": sample_users[0]["_id"],
            "total": 250.00,
            "status": "pending",
            "items": ["item3"],
        },
        {
            "_id": ObjectId(),
            "user_id": sample_users[1]["_id"],
            "total": 75.25,
            "status": "completed",
            "items": ["item4", "item5", "item6"],
        },
    ]

    await test_db.orders.insert_many(orders)
    return orders


@pytest.fixture
async def sample_products(test_db: AsyncIOMotorDatabase) -> list[dict]:
    """Insert sample product documents."""
    products = [
        {
            "_id": ObjectId(),
            "name": "Widget",
            "price": 19.99,
            "stock": 100,
            "category": "electronics",
            "tags": ["gadget", "popular"],
        },
        {
            "_id": ObjectId(),
            "name": "Gadget",
            "price": 29.99,
            "stock": 50,
            "category": "electronics",
            "tags": ["gadget", "new"],
        },
        {
            "_id": ObjectId(),
            "name": "Book",
            "price": 14.99,
            "stock": 200,
            "category": "books",
            "tags": ["bestseller"],
        },
    ]

    await test_db.products.insert_many(products)
    return products


@pytest.fixture
async def monglo_engine(test_db: AsyncIOMotorDatabase) -> MongloEngine:
    """Create a Monglo engine instance for testing."""
    engine = MongloEngine(
        database=test_db,
        auto_discover=False,  # Manual registration for controlled tests
        relationship_detection="auto",
    )

    await engine.initialize()
    return engine


@pytest.fixture
async def registered_engine(
    monglo_engine: MongloEngine,
    sample_users: list[dict],
    sample_orders: list[dict],
    sample_products: list[dict],
) -> MongloEngine:
    """Create engine with collections registered.

    Depends on sample data fixtures to ensure collections exist.
    """
    # Register collections
    await monglo_engine.register_collection("users")
    await monglo_engine.register_collection("orders")
    await monglo_engine.register_collection("products")

    return monglo_engine


# Test utilities


class TestDataFactory:
    """Factory for creating test data."""

    @staticmethod
    def create_user(**kwargs) -> dict:
        """Create a user document with default values."""
        defaults = {
            "_id": ObjectId(),
            "name": "Test User",
            "email": "test@example.com",
            "age": 25,
            "status": "active",
        }
        defaults.update(kwargs)
        return defaults

    @staticmethod
    def create_order(user_id: ObjectId | None = None, **kwargs) -> dict:
        """Create an order document with default values."""
        defaults = {
            "_id": ObjectId(),
            "user_id": user_id or ObjectId(),
            "total": 100.00,
            "status": "pending",
            "items": [],
        }
        defaults.update(kwargs)
        return defaults

    @staticmethod
    def create_product(**kwargs) -> dict:
        """Create a product document with default values."""
        defaults = {
            "_id": ObjectId(),
            "name": "Test Product",
            "price": 19.99,
            "stock": 100,
            "category": "test",
        }
        defaults.update(kwargs)
        return defaults


@pytest.fixture
def test_data_factory() -> TestDataFactory:
    """Provide test data factory."""
    return TestDataFactory()


# Markers for test categorization


def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test (fast, no external dependencies)"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test (requires MongoDB)"
    )
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line(
        "markers", "requires_mongodb: mark test as requiring MongoDB connection"
    )
