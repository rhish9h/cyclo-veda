"""Repositories package for Cyclo Veda application.

Repositories encapsulate all database CRUD operations, keeping
SQL/ORM logic out of service and router layers.

Naming convention:
- repositories/  → Database access layer (SQLAlchemy queries)
- services/      → Business logic layer (uses repositories)
- routers/       → HTTP layer (uses services)
"""
