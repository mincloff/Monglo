# Monglo Examples

Complete working examples for all supported frameworks.

## Available Examples

### [FastAPI](./fastapi_example/)
Full-featured async API with auto-generated docs.

```bash
cd fastapi_example
pip install -r requirements.txt
python app.py
```

Visit: http://localhost:8000/docs

### [Flask](./flask_example/)
Blueprint-based Flask application.

```bash
cd flask_example
pip install -r requirements.txt
python app.py
```

Visit: http://localhost:5000/api/admin/

### [Django](./django_example/)
Django project with Monglo views.

```bash
cd django_example
pip install -r requirements.txt
python manage.py runserver
```

Visit: http://localhost:8000/api/admin/

## Prerequisites

- Python 3.10+
- MongoDB running on localhost:27017

## Common Commands

```bash
# Start MongoDB (if using Docker)
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or with MongoDB installed locally
mongod
```

## Testing the APIs

```bash
# List collections
curl http://localhost:8000/api/admin/

# List documents in a collection
curl http://localhost:8000/api/admin/users?page=1&per_page=10

# Create a document
curl -X POST http://localhost:8000/api/admin/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com"}'
```
