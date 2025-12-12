---
description: Setup development environment
---

# Development Environment Setup

## 1. Create virtual environment
```bash
python3 -m venv .venv
```

## 2. Activate virtual environment
```bash
source .venv/bin/activate
```

## 3. Install development dependencies
//turbo
```bash
pip install -e ".[dev]"
```

## 4. Verify installation
// turbo
```bash
pytest --version
ruff --version
mypy --version
```

Your development environment is now ready!
