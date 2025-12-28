"""Shared MongoDB client utilities."""
from .mongo_client import (
    MongoClientManager,
    get_manager,
    get_mongo_client,
    get_db_and_collection,
    get_mongo_context
)

__all__ = [
    'MongoClientManager',
    'get_manager',
    'get_mongo_client',
    'get_db_and_collection',
    'get_mongo_context'
]

