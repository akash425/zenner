"""
MongoDB connection management.

Manages database connections efficiently by reusing a single connection.
"""
from typing import Optional, Tuple
from contextlib import contextmanager

try:
    from pymongo import MongoClient
    from pymongo.database import Database
    from pymongo.collection import Collection
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    import certifi
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False
    MongoClient = None
    Database = None
    Collection = None
    ConnectionFailure = Exception
    ServerSelectionTimeoutError = Exception
    certifi = None


class MongoClientManager:
    """
    Manages MongoDB connections.
    
    Creates one connection and reuses it for better performance.
    """
    
    _instance: Optional['MongoClientManager'] = None
    _client: Optional[MongoClient] = None
    _mongo_uri: Optional[str] = None
    
    def __new__(cls):
        """Create only one instance (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the manager."""
        pass
    
    def _initialize_client(self) -> None:
        """Create the MongoDB connection."""
        import sys
        from pathlib import Path
        
        # Import Config from shared
        project_root = Path(__file__).parent.parent.parent
        shared_path = project_root / 'shared'
        if str(shared_path) not in sys.path:
            sys.path.insert(0, str(shared_path))
        
        from config.config import Config
        config = Config()
        self._mongo_uri = config.get_mongo_uri()
        
        if not self._mongo_uri:
            raise ValueError("MongoDB URI not configured")
        
        try:
            self._client = MongoClient(
                self._mongo_uri,
                serverSelectionTimeoutMS=30000,
                connectTimeoutMS=30000,
                socketTimeoutMS=30000,
                maxPoolSize=50,
                minPoolSize=10,
                tlsCAFile=certifi.where() if certifi else None,
                tlsAllowInvalidCertificates=False,
                retryWrites=True
            )
            # Test the connection
            self._client.admin.command('ping')
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {str(e)}") from e
        except Exception as e:
            raise RuntimeError(f"Error connecting to MongoDB: {str(e)}") from e
    
    def get_client(self) -> MongoClient:
        """Get the MongoDB client, creating it if needed."""
        if not PYMONGO_AVAILABLE:
            raise RuntimeError("pymongo is not installed")
        
        if self._client is None:
            self._initialize_client()
        
        return self._client
    
    def get_database(self, db_name: Optional[str] = None) -> Database:
        """Get a database instance."""
        import sys
        from pathlib import Path
        
        if db_name is None:
            # Import Config from shared
            project_root = Path(__file__).parent.parent.parent
            shared_path = project_root / 'shared'
            if str(shared_path) not in sys.path:
                sys.path.insert(0, str(shared_path))
            
            from config.config import Config
            config = Config()
            db_name = config.get_database_name()
        
        client = self.get_client()
        return client[db_name]
    
    def get_collection(
        self, 
        collection_name: Optional[str] = None,
        db_name: Optional[str] = None
    ) -> Collection:
        """Get a collection instance."""
        import sys
        from pathlib import Path
        
        if collection_name is None or db_name is None:
            # Import Config from shared
            project_root = Path(__file__).parent.parent.parent
            shared_path = project_root / 'shared'
            if str(shared_path) not in sys.path:
                sys.path.insert(0, str(shared_path))
            
            from config.config import Config
            config = Config()
            if collection_name is None:
                collection_name = config.get_collection_name()
            if db_name is None:
                db_name = config.get_database_name()
        
        db = self.get_database(db_name)
        return db[collection_name]
    
    def close(self) -> None:
        """Close the MongoDB connection."""
        if self._client is not None:
            self._client.close()
            self._client = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # Don't close - we want to reuse the connection
        return False


# Global manager instance
_manager: Optional[MongoClientManager] = None


def get_manager() -> MongoClientManager:
    """Get or create the MongoDB manager."""
    global _manager
    if _manager is None:
        _manager = MongoClientManager()
    return _manager


def get_mongo_client(mongo_uri: Optional[str] = None) -> Optional[MongoClient]:
    """Get MongoDB client (for backward compatibility)."""
    try:
        manager = get_manager()
        return manager.get_client()
    except Exception:
        return None


def get_db_and_collection(
    db_name: Optional[str] = None,
    collection_name: Optional[str] = None,
    mongo_uri: Optional[str] = None
) -> Tuple[Optional[MongoClient], Optional[Database], Optional[Collection]]:
    """Get database and collection (for backward compatibility)."""
    try:
        manager = get_manager()
        client = manager.get_client()
        db = manager.get_database(db_name)
        collection = manager.get_collection(collection_name, db_name)
        return (client, db, collection)
    except Exception:
        return (None, None, None)


@contextmanager
def get_mongo_context(
    db_name: Optional[str] = None,
    collection_name: Optional[str] = None
):
    """Context manager for MongoDB operations."""
    try:
        manager = get_manager()
        client = manager.get_client()
        db = manager.get_database(db_name)
        collection = manager.get_collection(collection_name, db_name)
        yield (client, db, collection)
    except Exception as e:
        raise RuntimeError(f"MongoDB error: {str(e)}") from e
