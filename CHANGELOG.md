# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Flask adapter implementation
- Django adapter implementation
- Starlette adapter implementation
- GridFS file support
- Real-time collaboration features
- GraphQL API support
- Role-based access control (RBAC)
- Audit logging system
- Data migration tools

## [0.1.0] - 2025-12-13

**First production-ready release with full FastAPI support!** 🎉

### Added

#### Core Engine
- **Auto-discovery system** - Automatically detects all collections and schemas
- **Intelligent relationship detection** - Multiple strategies (naming conventions, ObjectId fields, DBRef, arrays)
- **Framework-agnostic engine** - Clean separation between core logic and framework adapters
- **Collection registry** - Centralized management of all registered collections
- **Schema introspection** - Automatic field type detection and validation
- **Query builder** - Fluent API for building MongoDB queries

#### Operations
- **Full CRUD operations** - Create, read, update, delete with proper error handling
- **Advanced search** - Multi-field search across configured fields
- **Pagination** - Efficient cursor-based pagination
- **Sorting & filtering** - Flexible query capabilities
- **Aggregation support** - Complex MongoDB aggregation pipelines
- **Export functionality** - Export to CSV and JSON formats
- **Bulk operations** - Batch create, update, and delete

#### Views System
- **Table view** - Spreadsheet-like interface with sorting and filtering
- **Document view** - JSON tree structure with syntax highlighting
- **Relationship view** - Navigate between related documents
- **Configurable columns** - Customize visible fields per collection
- **Responsive design** - Works on desktop and mobile

#### FastAPI Integration ⚡
- **Complete FastAPI adapter** - Production-ready integration
- **Auto-generated REST API** - Full CRUD endpoints for all collections
- **Interactive API docs** - Built-in Swagger/ReDoc documentation
- **Async/await support** - Fully asynchronous operations
- **Type hints** - Full Pydantic integration
- **UI helper** - Ready-to-use UI router

#### Field Types
- **Primitive fields** - String, Integer, Float, Boolean, Date, DateTime
- **Reference fields** - ObjectId references with auto-detection
- **Embedded documents** - Nested document support
- **Array fields** - Lists and embedded arrays
- **Custom fields** - Extensible field type system

#### Widgets
- **Input widgets** - Text, number, email, URL inputs
- **Select widgets** - Dropdown, multi-select, autocomplete
- **Date/time pickers** - Calendar and time selection
- **Custom widgets** - Extensible widget system

#### Authentication & Security
- **Simple auth provider** - Basic username/password authentication
- **MongoDB auth backend** - Authenticate against MongoDB users
- **Session management** - Secure session handling
- **Permission system** - Collection-level permissions

#### UI Package (`monglo_ui/`)
- **Modern, responsive interface** - Professional admin panel
- **Dark/light mode** - User preference saved
- **MongoDB green theme** - Beautiful color scheme
- **FontAwesome icons** - Rich icon set
- **Resizable sidebar** - Customizable layout
- **Mobile-friendly** - Responsive on all devices

#### Examples & Documentation
- **FastAPI examples** - Basic, advanced, and auth examples
- **Comprehensive documentation** - QuickStart guides and API reference
- **Code examples** - Real-world usage patterns
- **Configuration guides** - Detailed setup instructions

#### Testing & Quality
- **Unit tests** - Core functionality coverage
- **Integration tests** - End-to-end testing
- **Type checking** - Full mypy compliance
- **Code formatting** - Black and Ruff configured
- **CI/CD pipeline** - Automated testing and building

### Framework Support

- ✅ **FastAPI** - Fully supported and production-ready
- 🔜 **Django** - Planned for 0.2.0
- 🔜 **Flask** - Planned for 0.2.0
- 🔜 **Starlette** - Planned for 0.3.0

### Breaking Changes

This is the first functional release. Version 0.0.1 was a placeholder with empty directory structure only.

### Migration Guide

If upgrading from 0.0.1 (which had no code), simply install 0.1.0:

```bash
pip install --upgrade monglo[fastapi]
```

## [0.0.1] - 2025-11-20

### Added
- Initial project structure
- Core package layout (`monglo/`)
- Framework-agnostic core architecture
- Module structure for:
  - Core engine components (engine, registry, config, introspection, relationships, query_builder)
  - Operations (CRUD, search, aggregations, pagination, export)
  - Views system (base, table_view, document_view, relationship_view)
  - Framework adapters (FastAPI, Flask, Django, Starlette)
  - Field type system (primitives, references, embedded, files, custom)
  - Widget definitions (inputs, selects, displays, custom)
  - Serializers (JSON, table, document)
  - Authentication system (base, simple)
  - Utilities (validators, formatters, index_analyzer)
- UI package structure (`monglo_ui/`)
- Comprehensive test suite structure
  - Unit tests
  - Integration tests
  - Adapter tests
  - End-to-end tests
- Example projects for multiple frameworks
- Documentation structure
- Benchmarking setup
- GitHub workflows for CI/CD
- MIT License
- Professional README with project overview
- Development configuration files
  - pyproject.toml with build system setup
  - .gitignore for Python projects

### Documentation
- Project structure documentation
- README with installation and quick start guide
- LICENSE file (MIT)
- CHANGELOG file

[Unreleased]: https://github.com/me-umar/monglo/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/me-umar/monglo/releases/tag/v0.1.0
[0.0.1]: https://github.com/me-umar/monglo/releases/tag/v0.0.1