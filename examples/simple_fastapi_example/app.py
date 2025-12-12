"""
Simplified FastAPI Example - Perfect Developer Experience

This example shows how minimal the setup can be with Monglo.
The library handles everything - templates, serialization, routing!
"""

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from monglo import MongloEngine
from monglo.adapters.fastapi import create_fastapi_router
from monglo.ui_helpers.fastapi import create_ui_router

# MongoDB connection
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.monglo_simple_demo

# Create FastAPI app
app = FastAPI(title="Monglo Admin - Simple Example")

# Monglo engine
engine = MongloEngine(database=db, auto_discover=True)


@app.on_event("startup")
async def startup():
    """Initialize Monglo on startup."""
    await engine.initialize()
    
    # That's it for setup! Now add the routes:
    
    # API routes (for programmatic access)
    api_router = create_fastapi_router(engine, prefix="/api/admin")
    app.include_router(api_router)
    
    # UI routes (for browser-based admin)
    ui_router = create_ui_router(engine, prefix="/admin")
    app.include_router(ui_router)
    
    print("✅ Monglo Admin ready!")
    print("📊 API: http://localhost:8000/api/admin")
    print("🖥️  UI:  http://localhost:8000/admin")
    print("📚 Docs: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    client.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
