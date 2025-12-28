from datetime import datetime
from src.utils.logger import get_logger
from src.utils.mongo_client import get_manager
from src.utils.config import Config


def get_duplicate_devices(save_to_db=True):
    """
    Find devices that have duplicate records (more than one record).
    
    Returns a list of devices with their record counts.
    """
    config = Config()
    logger = get_logger('analytics.duplicates', log_file_path=config.get_analytics_log_path())
    
    try:
        # Get database collections
        manager = get_manager()
        collection = manager.get_collection(config.get_collection_name())
        analytics_collection = manager.get_collection(config.get_analytics_collection_name())
        
        # Find devices with more than one record
        pipeline = [
            {'$group': {'_id': '$device_id', 'count': {'$sum': 1}}},
            {'$match': {'count': {'$gt': 1}}},
            {'$project': {'_id': 0, 'device_id': '$_id', 'count': 1}}
        ]
        
        results = list(collection.aggregate(pipeline))
        logger.info(f"Found {len(results)} devices with duplicate records")
        
        # Save results to analytics collection
        if save_to_db:
            try:
                analytics_doc = {
                    'analytics_type': 'duplicate_devices',
                    'computed_at': datetime.utcnow(),
                    'results': results
                }
                analytics_collection.update_one(
                    {'analytics_type': 'duplicate_devices'},
                    {'$set': analytics_doc},
                    upsert=True
                )
            except Exception as e:
                logger.warning(f"Could not save to analytics collection: {str(e)}")
        
        return results
    
    except Exception as e:
        logger.error(f"Error finding duplicate devices: {str(e)}")
        return []

