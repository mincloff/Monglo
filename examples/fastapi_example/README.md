# FastAPI Example with Professional UI

Complete working example of Monglo with **professional admin interface**.

## Features

✨ **Professional UI** with custom color palette
- Navy sidebar with gradient
- Green primary actions
- Cream backgrounds
- Modern animations

📊 **Complete Admin Interface**
- Table view with search, sort, filters
- Document view with JSON tree
- Relationship navigation
- CRUD operations

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Start MongoDB (required)
# Make sure MongoDB is running on localhost:27017
```

## Run

```bash
python app.py
```

The app will automatically:
- Connect to MongoDB
- Seed example data (users, products, orders)
- Initialize Monglo engine
- Start server on http://localhost:8000

## Access Points

- **Admin UI**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## What You'll See

### Collections
- **users** - 3 sample users
- **products** - 3 sample products  
- **orders** - 2 sample orders with relationships

### Features to Try
1. **Table View**: Browse collections with sorting and search
2. **Document View**: Click any row to see full document
3. **Relationships**: Orders link to users and products
4. **Search**: Try searching for "Alice" or "Laptop"
5. **Filters**: Use the filters in toolbar

## UI Customization

The UI uses templates from `../../monglo_ui/templates/` and styles from `../../monglo_ui/static/css/admin.css`.

You can customize:
- Colors in CSS variables
- Templates in Jinja2
- Add custom actions
- Modify layouts

## API Endpoints

All CRUD operations are available via REST API:

```bash
# List collections
curl http://localhost:8000/api/admin/

# List users
curl http://localhost:8000/api/admin/users?page=1&per_page=10

# Get specific user
curl http://localhost:8000/api/admin/users/{id}

# Create user
curl -X POST http://localhost:8000/api/admin/users \
  -H "Content-Type: application/json" \
  -d '{"name": "New User", "email": "new@example.com"}'
```

## Professional Design

The UI features:
- Navy sidebar (#002b60) with gradient
- Green primary buttons (#4DB33D)
- Orange accents (#f56400)
- Cream background (#E8E7D5)
- Professional shadows and animations
- Responsive layout

Enjoy exploring Monglo Admin! 🚀
