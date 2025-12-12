---
description: Run linters and formatters
---

# Code Quality Checks

## 1. Activate virtual environment
```bash
source .venv/bin/activate
```

## 2. Run Ruff linter
// turbo
```bash
ruff check monglo/
```

## 3. Auto-fix with Ruff
// turbo
```bash
ruff check --fix monglo/
```

## 4. Format with Black
// turbo
```bash
black monglo/ tests/
```

## 5. Type check with MyPy
// turbo
```bash
mypy monglo/ --strict
```

## 6. Run all checks at once
// turbo
```bash
ruff check monglo/ && black --check monglo/ tests/ && mypy monglo/ --strict
```
