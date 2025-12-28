import sys
from pathlib import Path
from datetime import datetime

# Add shared to path
project_root = Path(__file__).parent.parent.parent.parent.parent
shared_path = project_root / 'shared'
if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))

from logger.logger import get_logger
from mongo.mongo_client import get_manager
from config.config import Config


def get_top_active_devices(limit=10, save_to_db=True):
    """
    Get the most active devices by counting how many uplinks each device has.
    
    Returns the top devices sorted by uplink count.
    """
    config = Config()
    logger = get_logger('analytics.device_stats', log_file_path=config.get_analytics_log_path())
    
    try:
        # Get database collections
        manager = get_manager()
        collection = manager.get_collection(config.get_collection_name())
        analytics_collection = manager.get_collection(config.get_analytics_collection_name())
        
        # Count uplinks per device and get top ones
        pipeline = [
            {'$group': {'_id': '$device_id', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': limit},
            {'$project': {'_id': 0, 'device_id': '$_id', 'count': 1}}
        ]
        
        results = list(collection.aggregate(pipeline))
        logger.info(f"Found top {len(results)} active devices")
        
        # Save results
        if save_to_db:
            try:
                analytics_doc = {
                    'analytics_type': 'top_active_devices',
                    'computed_at': datetime.utcnow(),
                    'parameters': {'limit': limit},
                    'results': results
                }
                analytics_collection.update_one(
                    {'analytics_type': 'top_active_devices'},
                    {'$set': analytics_doc},
                    upsert=True
                )
            except Exception as e:
                logger.warning(f"Could not save to analytics collection: {str(e)}")
        
        return results
    
    except Exception as e:
        logger.error(f"Error getting top active devices: {str(e)}")
        return []

