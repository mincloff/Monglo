# Flask Example

Flask application with Monglo admin Blueprint.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
# Start MongoDB
# mongod

# Run the app
python app.py

# Or with flask CLI
export FLASK_APP=app.py
flask run
```

## Endpoints

Visit http://localhost:5000/api/admin/ for the admin API.

Same endpoint structure as FastAPI example.
