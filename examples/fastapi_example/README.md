# FastAPI Example

Complete working example of Monglo with FastAPI.

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Or install from parent directory
pip install -e ../..
```

## Run

```bash
# Start MongoDB (if not running)
# mongod

# Run the app
python app.py

# Or with uvicorn directly
uvicorn app:app --reload
```

## API Endpoints

Once running, visit:
- **API Docs**: http://localhost:8000/docs
- **Admin API**: http://localhost:8000/api/admin/
- **Collection List**: http://localhost:8000/api/admin/

### Auto-Generated Endpoints

For each collection (e.g., `users`):

```
GET    /api/admin/users              - List documents
GET    /api/admin/users/{id}         - Get document
POST   /api/admin/users              - Create document
PUT    /api/admin/users/{id}         - Update document
DELETE /api/admin/users/{id}         - Delete document
GET    /api/admin/users/config/table - Table view config
GET    /api/admin/users/config/document - Document view config
```

### Query Parameters

- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20, max: 100)
- `search`: Search term
- `sort`: Sort field (e.g., `created_at:desc`)

### Example Requests

```bash
# List users
curl http://localhost:8000/api/admin/users?page=1&per_page=10

# Search
curl http://localhost:8000/api/admin/users?search=john

# Create user
curl -X POST http://localhost:8000/api/admin/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com"}'

# Get table config
curl http://localhost:8000/api/admin/users/config/table
```

## Features

- ✅ Auto-discovery of MongoDB collections
- ✅ Auto-generated CRUD endpoints
- ✅ Pagination and filtering
- ✅ Search across configured fields
- ✅ View configuration endpoints
- ✅ Interactive API docs (Swagger UI)
- ✅ CORS enabled
