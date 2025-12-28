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


def get_weak_devices(limit=20, save_to_db=True):
    """
    Find devices with the weakest signal strength (lowest average RSSI).
    
    Returns devices sorted by signal strength, weakest first.
    """
    config = Config()
    logger = get_logger('analytics.weak_signal', log_file_path=config.get_analytics_log_path())
    
    try:
        # Get database collections
        manager = get_manager()
        collection = manager.get_collection(config.get_collection_name())
        analytics_collection = manager.get_collection(config.get_analytics_collection_name())
        
        # Calculate average signal strength per device
        pipeline = [
            {'$group': {
                '_id': '$device_id',
                'avg_rssi': {'$avg': '$rssi'},
                'avg_snr': {'$avg': '$snr'}
            }},
            {'$sort': {'avg_rssi': 1}},  # Sort by RSSI ascending (weakest first)
            {'$limit': limit},
            {'$project': {'_id': 0, 'device_id': '$_id', 'avg_rssi': 1, 'avg_snr': 1}}
        ]
        
        results = list(collection.aggregate(pipeline))
        logger.info(f"Found {len(results)} devices with weak signals")
        
        # Save results
        if save_to_db:
            try:
                analytics_doc = {
                    'analytics_type': 'weak_signal_devices',
                    'computed_at': datetime.utcnow(),
                    'parameters': {'limit': limit},
                    'results': results
                }
                analytics_collection.update_one(
                    {'analytics_type': 'weak_signal_devices'},
                    {'$set': analytics_doc},
                    upsert=True
                )
            except Exception as e:
                logger.warning(f"Could not save to analytics collection: {str(e)}")
        
        return results
    
    except Exception as e:
        logger.error(f"Error finding weak signal devices: {str(e)}")
        return []

