---
description: Run example application
---

# Run Example Application

## Choose your framework:

### FastAPI (Recommended)

1. Activate environment
```bash
source .venv/bin/activate
```

2. Install FastAPI dependencies
// turbo
```bash
pip install -e ".[fastapi]"
```

3. Start MongoDB (if not running)
```bash
# Using Docker
docker run -d -p 27017:27017 mongo:latest
```

4. Run the example
// turbo
```bash
cd examples/simple_fastapi_example
uvicorn app:app --reload
```

5. Open browser
```
http://localhost:8000/admin
```

### Flask

1. Activate environment
```bash
source .venv/bin/activate
```

2. Install Flask dependencies
```bash
pip install -e ".[flask]"
```

3. Run the example
```bash
cd examples/flask_minimal
python app.py
```

4. Open browser
```
http://localhost:5000/admin
```
