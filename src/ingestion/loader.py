import configparser
import logging
import os
import sys
import time
from pathlib import Path

try:
    from pymongo import MongoClient, InsertOne
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout, BulkWriteError
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False


CONFIG_FILE_PATH = './config.ini'
MAX_RETRIES = 3
RETRY_DELAY = 2

# Indexes to create
INDEXES = [
    {'keys': [('device_id', 1)], 'name': 'device_id_1'},
    {'keys': [('gateway_id', 1)], 'name': 'gateway_id_1'},
    {'keys': [('timestamp', 1)], 'name': 'timestamp_1'},
    {'keys': [('device_id', 1), ('timestamp', 1)], 'name': 'device_id_1_timestamp_1'},
]


def setup_logger(log_file_path):
    Path(log_file_path).parent.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger('ingestion.loader')
    logger.setLevel(logging.INFO)
    
    if logger.handlers:
        return logger
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_mongo_client(mongo_uri, logger):
    if not PYMONGO_AVAILABLE:
        logger.error("pymongo is not installed")
        return None
    
    try:
        client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=30000,
        )
        client.admin.command('ping')
        logger.info("Connected to MongoDB")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        return None


def ensure_indexes(collection, logger):
    try:
        existing_indexes = {idx['name'] for idx in collection.list_indexes()}
        
        for index_def in INDEXES:
            if index_def['name'] not in existing_indexes:
                try:
                    collection.create_index(index_def['keys'], name=index_def['name'], background=True)
                    logger.info(f"Created index: {index_def['name']}")
                except Exception as e:
                    logger.warning(f"Failed to create index {index_def['name']}: {str(e)}")
    except Exception as e:
        logger.error(f"Error ensuring indexes: {str(e)}")


def bulk_insert(collection, documents, logger):
    if not documents:
        return (0, 0)
    
    operations = [InsertOne(doc) for doc in documents]
    
    for attempt in range(MAX_RETRIES + 1):
        try:
            result = collection.bulk_write(operations, ordered=False)
            inserted = result.inserted_count
            skipped = len(documents) - inserted
            
            if attempt > 0:
                logger.info(f"Bulk insert succeeded on attempt {attempt + 1}. Inserted: {inserted}, Skipped: {skipped}")
            
            return (inserted, skipped)
        
        except BulkWriteError as e:
            inserted = e.details.get('nInserted', 0)
            write_errors = e.details.get('writeErrors', [])
            skipped = len(write_errors)
            
            # Filter out successfully inserted documents
            error_indices = {err['index'] for err in write_errors}
            operations = [op for i, op in enumerate(operations) if i not in error_indices]
            
            if not operations:
                logger.warning(f"Bulk insert completed with errors. Inserted: {inserted}, Skipped: {skipped}")
                return (inserted, skipped)
            
            if attempt < MAX_RETRIES:
                logger.warning(f"Bulk insert partial failure (attempt {attempt + 1}). Inserted: {inserted}, Errors: {skipped}. Retrying...")
                time.sleep(RETRY_DELAY)
                continue
            else:
                logger.error(f"Bulk insert failed after {MAX_RETRIES + 1} attempts. Inserted: {inserted}, Skipped: {skipped}")
                return (inserted, skipped)
        
        except (ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout) as e:
            if attempt < MAX_RETRIES:
                logger.warning(f"Transient error during bulk insert (attempt {attempt + 1}): {str(e)}. Retrying...")
                time.sleep(RETRY_DELAY)
                continue
            else:
                logger.error(f"Bulk insert failed: {str(e)}")
                return (0, len(documents))
        
        except Exception as e:
            logger.error(f"Bulk insert failed: {str(e)}")
            return (0, len(documents))
    
    return (0, len(documents))


def load_rows(rows, mongo_uri=None, log_file_path='./logs/ingestion.log'):
    logger = setup_logger(log_file_path)
    
    # Load config once
    config = configparser.RawConfigParser()
    config_path = Path(CONFIG_FILE_PATH)
    
    if not config_path.exists():
        print(f"ERROR: Configuration file not found: {CONFIG_FILE_PATH}")
        sys.exit(1)
    
    config.read(config_path)
    
    # Get MongoDB URI
    if mongo_uri is None:
        mongo_uri = config.get('mongodb', 'uri', fallback='').strip()
        
        if not mongo_uri:
            mongo_uri = os.getenv('MONGO_URI', '').strip()
        
        if not mongo_uri:
            error_msg = "MongoDB URI not provided. Set it in config.ini [mongodb] uri or MONGO_URI environment variable"
            logger.error(error_msg)
            print(f"ERROR: {error_msg}")
            sys.exit(1)
    
    # Get database and collection settings
    db_name = config.get('database', 'name', fallback='').strip()
    if not db_name:
        error_msg = "Database name not configured in config.ini"
        logger.error(error_msg)
        print(f"ERROR: {error_msg}")
        sys.exit(1)
    
    collection_name = config.get('database', 'collection', fallback='').strip()
    if not collection_name:
        error_msg = "Collection name not configured in config.ini"
        logger.error(error_msg)
        print(f"ERROR: {error_msg}")
        sys.exit(1)
    
    try:
        batch_size = config.getint('ingestion', 'batch_size', fallback=1000)
    except (ValueError, configparser.NoOptionError):
        batch_size = 1000
    
    # Connect to MongoDB
    client = get_mongo_client(mongo_uri, logger)
    if client is None:
        logger.error("Cannot proceed without MongoDB connection")
        return (0, 0)
    
    try:
        db = client[db_name]
        collection = db[collection_name]
        
        logger.info(f"Loading rows into MongoDB. Database: {db_name}, Collection: {collection_name}")
        
        # Ensure indexes
        ensure_indexes(collection, logger)
        
        # Batch and insert rows
        batch = []
        total_inserted = 0
        total_skipped = 0
        total_processed = 0
        
        for row in rows:
            batch.append(row)
            total_processed += 1
            
            if len(batch) >= batch_size:
                inserted, skipped = bulk_insert(collection, batch, logger)
                total_inserted += inserted
                total_skipped += skipped
                batch = []
        
        # Insert remaining rows
        if batch:
            inserted, skipped = bulk_insert(collection, batch, logger)
            total_inserted += inserted
            total_skipped += skipped
        
        logger.info(f"Finished loading rows. Total processed: {total_processed}, Inserted: {total_inserted}, Skipped: {total_skipped}")
        
        return (total_inserted, total_skipped)
    
    except Exception as e:
        logger.error(f"Error during load operation: {str(e)}")
        raise
    finally:
        client.close()
