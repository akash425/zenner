import time
from typing import Iterator, Tuple

from pymongo import InsertOne
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout, BulkWriteError

import sys
from pathlib import Path

# Add shared to path
project_root = Path(__file__).parent.parent.parent.parent.parent
shared_path = project_root / 'shared'
if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))

from config.config import Config
from logger.logger import get_logger
from mongo.mongo_client import get_manager

# Database indexes for faster queries
INDEXES = [
    {'keys': [('device_id', 1)], 'name': 'device_id_1'},
    {'keys': [('gateway_id', 1)], 'name': 'gateway_id_1'},
    {'keys': [('timestamp', 1)], 'name': 'timestamp_1'},
    {'keys': [('device_id', 1), ('timestamp', 1)], 'name': 'device_id_1_timestamp_1'},
]

MAX_RETRIES = 3
RETRY_DELAY = 2


def ensure_indexes(collection, logger):
    """Create database indexes if they don't exist."""
    try:
        existing_indexes = {idx['name'] for idx in collection.list_indexes()}
        
        for index_def in INDEXES:
            if index_def['name'] not in existing_indexes:
                try:
                    collection.create_index(index_def['keys'], name=index_def['name'], background=True)
                    logger.info(f"Created index: {index_def['name']}")
                except Exception as e:
                    logger.warning(f"Could not create index {index_def['name']}: {str(e)}")
    except Exception as e:
        logger.error(f"Error checking indexes: {str(e)}")


def bulk_insert(collection, documents, logger):
    """Insert documents in bulk with retry logic."""
    if not documents:
        return (0, 0)
    
    operations = [InsertOne(doc) for doc in documents]
    
    for attempt in range(MAX_RETRIES + 1):
        try:
            result = collection.bulk_write(operations, ordered=False)
            inserted = result.inserted_count
            skipped = len(documents) - inserted
            
            if attempt > 0:
                logger.info(f"Insert succeeded on attempt {attempt + 1}. Inserted: {inserted}, Skipped: {skipped}")
            
            return (inserted, skipped)
        
        except BulkWriteError as e:
            # Some documents failed, but some may have succeeded
            inserted = e.details.get('nInserted', 0)
            write_errors = e.details.get('writeErrors', [])
            skipped = len(write_errors)
            
            # Remove successfully inserted documents from retry list
            error_indices = {err['index'] for err in write_errors}
            operations = [op for i, op in enumerate(operations) if i not in error_indices]
            
            if not operations:
                # All remaining documents were inserted
                logger.warning(f"Insert completed with some errors. Inserted: {inserted}, Skipped: {skipped}")
                return (inserted, skipped)
            
            if attempt < MAX_RETRIES:
                logger.warning(f"Partial failure (attempt {attempt + 1}). Inserted: {inserted}, Errors: {skipped}. Retrying...")
                time.sleep(RETRY_DELAY)
                continue
            else:
                logger.error(f"Insert failed after {MAX_RETRIES + 1} attempts. Inserted: {inserted}, Skipped: {skipped}")
                return (inserted, skipped)
        
        except (ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout) as e:
            # Network error - retry
            if attempt < MAX_RETRIES:
                logger.warning(f"Network error (attempt {attempt + 1}): {str(e)}. Retrying...")
                time.sleep(RETRY_DELAY)
                continue
            else:
                logger.error(f"Insert failed after retries: {str(e)}")
                return (0, len(documents))
        
        except Exception as e:
            logger.error(f"Insert failed: {str(e)}")
            return (0, len(documents))
    
    return (0, len(documents))


def load_rows(rows: Iterator[dict]) -> Tuple[int, int]:
    """Save rows to MongoDB in batches."""
    config = Config()
    logger = get_logger('ingestion.loader', log_file_path=config.get_log_file_path())
    
    db_name = config.get_database_name()
    collection_name = config.get_collection_name()
    batch_size = config.get_batch_size()
    
    try:
        manager = get_manager()
        collection = manager.get_collection(collection_name, db_name)
    except Exception as e:
        logger.error(f"Cannot connect to MongoDB: {str(e)}")
        return (0, 0)
    
    try:
        logger.info(f"Loading rows into {db_name}.{collection_name}")
        
        # Create indexes for faster queries
        ensure_indexes(collection, logger)
        
        # Process rows in batches
        batch = []
        total_inserted = 0
        total_skipped = 0
        total_processed = 0
        
        for row in rows:
            batch.append(row)
            total_processed += 1
            
            # Insert when batch is full
            if len(batch) >= batch_size:
                inserted, skipped = bulk_insert(collection, batch, logger)
                total_inserted += inserted
                total_skipped += skipped
                batch = []
        
        # Insert any remaining rows
        if batch:
            inserted, skipped = bulk_insert(collection, batch, logger)
            total_inserted += inserted
            total_skipped += skipped
        
        logger.info(f"Finished loading. Processed: {total_processed}, Inserted: {total_inserted}, Skipped: {total_skipped}")
        
        return (total_inserted, total_skipped)
    
    except Exception as e:
        logger.error(f"Error loading rows: {str(e)}")
        raise
