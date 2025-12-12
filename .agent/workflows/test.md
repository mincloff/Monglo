---
description: Run all tests
---

# Run Tests

## 1. Activate virtual environment (if not already)
```bash
source .venv/bin/activate
```

## 2. Run unit tests
// turbo
```bash
pytest tests/unit -v
```

## 3. Run integration tests
// turbo
```bash
pytest tests/integration -v
```

## 4. Run all tests with coverage
// turbo
```bash
pytest --cov=monglo --cov-report=html --cov-report=term
```

## 5. View coverage report
```bash
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```
