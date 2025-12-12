"""
Flask Example Application with Monglo.

Demonstrates admin Blueprint for MongoDB collections.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from flask import Flask, jsonify
from flask_cors import CORS

from monglo import MongloEngine
from monglo.adapters.flask import create_flask_blueprint

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# MongoDB connection
client = None
engine = None


def init_monglo():
    """Initialize Monglo engine."""
    global client, engine
    
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.example_db
    
    # Initialize Monglo engine
    engine = MongloEngine(database=db, auto_discover=True)
    # Note: In production, call await engine.initialize() in async context
    
    # Create and register admin blueprint
    admin_bp = create_flask_blueprint(engine, url_prefix="/api/admin")
    app.register_blueprint(admin_bp)
    
    print("✓ Monglo admin routes mounted at /api/admin")


@app.route("/")
def root():
    """Root endpoint."""
    return jsonify({
        "message": "Monglo Flask Example",
        "admin_api": "/api/admin"
    })


@app.route("/health")
def health():
    """Health check."""
    return jsonify({"status": "healthy"})


# Initialize on first request
@app.before_first_request
def setup():
    """Setup before first request."""
    init_monglo()


if __name__ == "__main__":
    init_monglo()
    app.run(host="0.0.0.0", port=5000, debug=True)
