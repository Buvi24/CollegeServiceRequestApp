
# Defines reusable FastAPI dependencies (functions used with Depends()).
# Routers import these instead of accessing app/database.py directly.

from pymongo.collection import Collection
from pymongo.database import Database
from fastapi import Depends

from app.database import database


def get_db() -> Database:
    """
    Provides the shared MongoDB database object.
    """
    return database


# ---------------------------------------------------------------------------
# Collection dependencies
# Each function returns the MongoDB collection required by a router.
# ---------------------------------------------------------------------------


def get_users_collection(db: Database = Depends(get_db)) -> Collection:
    """Provides access to the users collection."""
    return db["users"]


def get_service_categories_collection(
    db: Database = Depends(get_db)
) -> Collection:
    """Provides access to the service_categories collection."""
    return db["service_categories"]


def get_service_requests_collection(
    db: Database = Depends(get_db)
) -> Collection:
    """Provides access to the service_requests collection."""
    return db["service_requests"]


def get_comments_collection(db: Database = Depends(get_db)) -> Collection:
    """Provides access to the comments collection."""
    return db["comments"]


def get_attachments_collection(db: Database = Depends(get_db)) -> Collection:
    """Provides access to the attachments collection."""
    return db["attachments"]


def get_audit_logs_collection(db: Database = Depends(get_db)) -> Collection:
    """Provides access to the audit_logs collection."""
    return db["audit_logs"]