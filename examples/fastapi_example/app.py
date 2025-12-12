"""
FastAPI Example Application with Monglo.

Demonstrates auto-generated admin API for MongoDB collections.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from monglo import MongloEngine
from monglo.adapters.fastapi import create_fastapi_router

# Initialize FastAPI app
app = FastAPI(
    title="Monglo FastAPI Example",
    description="Auto-generated MongoDB Admin API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection (will be initialized on startup)
client = None
engine = None


@app.on_event("startup")
async def startup():
    """Initialize MongoDB connection and Monglo engine."""
    global client, engine
    
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.example_db
    
    # Initialize Monglo engine with auto-discovery
    engine = MongloEngine(database=db, auto_discover=True)
    await engine.initialize()
    
    # Create and mount admin router
    admin_router = create_fastapi_router(engine, prefix="/api/admin")
    app.include_router(admin_router)
    
    print("✓ Monglo admin routes mounted at /api/admin")
    print(f"✓ Discovered {len(engine.registry._collections)} collections")


@app.on_event("shutdown")
async def shutdown():
    """Close MongoDB connection."""
    if client:
        client.close()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Monglo FastAPI Example",
        "admin_api": "/api/admin",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
