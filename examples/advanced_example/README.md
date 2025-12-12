# Advanced Features Example

This example shows advanced Monglo features:
- Custom authentication
- Audit logging
- Bulk operations
- Transactions
- Data validation
- Custom fields

## Clear Separation: Library vs Application

### What the LIBRARY Does (Automatic)
✅ All routing  
✅ All serialization  
✅ All UI rendering  
✅ Schema detection  
✅ Relationship detection  
✅ CRUD operations  
✅ Error handling  

### What YOU Write (Application Logic)
📝 Business logic  
📝 Custom auth rules  
📝 Specific validations  
📝 Custom actions  

## Example: Custom Authentication

```python
from monglo.auth import SimpleAuthProvider

# APPLICATION CODE - You define who can access
auth = SimpleAuthProvider(users={
    "admin": {
        "password_hash": SimpleAuthProvider.hash_password("admin123"),
        "role": "admin"
    },
    "viewer": {
        "password_hash": SimpleAuthProvider.hash_password("view123"),
        "role": "readonly"
    }
})

# LIBRARY CODE - Monglo handles the rest
engine = MongloEngine(database=db, auth_provider=auth)
```

## Example: Audit Logging

```python
from monglo.operations.audit import AuditLogger

# APPLICATION CODE - Initialize logger
logger = AuditLogger(database=db)

# LIBRARY CODE - Monglo logs automatically
# Every create, update, delete is logged with:
# - Timestamp
# - User
# - Action
# - Before/after state
```

## Example: Bulk Operations

```python
# APPLICATION CODE - Your business logic
new_users = [
    {"name": f"User {i}", "email": f"user{i}@example.com"}
    for i in range(100)
]

# LIBRARY CODE - Efficient bulk insert
created = await crud.bulk_create(new_users)
# All 100 users inserted in one operation!
```

## Example: Transactions

```python
from monglo.operations.transactions import TransactionManager

# APPLICATION CODE - Your transaction logic
manager = TransactionManager(client)

async with manager.transaction() as session:
    # LIBRARY CODE - Monglo ensures ACID
    user = await users_crud.create(user_data, session=session)
    order = await orders_crud.create(order_data, session=session)
    # Both succeed or both fail - atomic!
```

## Example: Custom Validation

```python
from monglo.operations.validation import DataValidator

# APPLICATION CODE - Your validation rules
validator = DataValidator(collection_admin)

# Before creating
errors = await validator.validate(data)
if errors:
    return {"errors": errors}  # Your error handling

# LIBRARY CODE - Monglo creates if valid
created = await crud.create(data)
```

## Running This Example

```bash
cd examples/advanced_example
pip install -e "../../[dev]"
python app.py
```

## Key Takeaway

**YOU write**: Business logic, auth rules, custom validations  
**LIBRARY handles**: Everything else (routing, UI, serialization, CRUD, etc.)

This is the power of Monglo - you focus on your domain logic, we handle the infrastructure!
