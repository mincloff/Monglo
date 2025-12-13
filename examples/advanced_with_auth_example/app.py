"""
Advanced Example with Session Authentication
Demonstrates Monglo Admin with session-based authentication and cookies
"""

from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import RedirectResponse
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.middleware.base import BaseHTTPMiddleware

from monglo import MongloEngine
from monglo.ui_helpers.fastapi import setup_ui
from monglo.adapters.fastapi import create_fastapi_router

# Import our modules
from db import seed_database
from admin_setup import setup_admin
from auth import require_auth, create_session, delete_session


# APP CONFIGURATION

app = FastAPI(
    title="Monglo with Auth",
    description="Advanced admin panel with session authentication",
    version="1.0.0"
)

# MongoDB connection
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.monglo_auth_example

# Initialize Monglo engine
engine = MongloEngine(
    database=db,
    auto_discover=False
)

# Admin credentials (in production, store in database)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"  # In production: hash and store in DB


# MIDDLEWARE TO REDIRECT 401 -> LOGIN

class AuthRedirectMiddleware(BaseHTTPMiddleware):
    """Redirect 401 errors to login page"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # If 401 and it's a browser request (not API), redirect to login
        if response.status_code == 401:
            if request.url.path.startswith("/admin"):
                # Check if it's not already the login page
                if "/login" not in request.url.path:
                    return RedirectResponse(url="/admin/login", status_code=303)
        
        return response


# Add middleware
app.add_middleware(AuthRedirectMiddleware)


# AUTHENTICATION ENDPOINTS

@app.post("/admin/login", include_in_schema=False)
async def handle_login(
    response: Response,
    username: str = Form(...),
    password: str = Form(...)
):
    """
    Handle login form submission
    """
    # Verify credentials
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        # Create session
        session_id = create_session(username)
        
        # Redirect to admin with session cookie
        redirect_response = RedirectResponse(url="/admin", status_code=303)
        redirect_response.set_cookie(
            key="monglo_session",
            value=session_id,
            httponly=True,
            max_age=86400,  # 24 hours
            samesite="lax"
        )
        return redirect_response
    
    # Failed login - redirect back with error
    return RedirectResponse(
        url="/admin/login?error=Invalid+credentials",
        status_code=303
    )


# STARTUP & SHUTDOWN

@app.on_event("startup")
async def startup():
    """Initialize application"""
    
    print("🚀 Starting Monglo Auth Example...")
    
    # Seed database
    await seed_database(db)
    
    # Setup custom admin configurations
    await setup_admin(engine)
    
    # Initialize Monglo engine
    await engine.initialize()
    
    # Setup admin UI with session auth protection
    setup_ui(
        app,
        engine,
        prefix="/admin",
        title="Secured Admin Panel",
        brand_color="#6366f1",
        auth_dependency=require_auth  # Protect with sessions
    )
    
    # Setup REST API (unprotected for demo)
    app.include_router(
        create_fastapi_router(engine, prefix="/api"),
        prefix="/api",
        tags=["API"]
    )
    
    print("✅ Application started successfully!")
    print(f"   🔐 Login: http://localhost:8000/admin/login")
    print(f"   📊 Admin Panel: http://localhost:8000/admin")
    print(f"   🔌 API Docs: http://localhost:8000/docs")
    print(f"\n   Credentials: admin / admin123")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup"""
    client.close()
    print("👋 Application shut down")


# HEALTH CHECK

@app.get("/", tags=["Health"])
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "app": "Monglo Auth Example",
        "version": "1.0.0",
        "auth": "Session-based",
        "endpoints": {
            "login": "/admin/login",
            "admin": "/admin",
            "api": "/api",
            "docs": "/docs"
        }
    }
