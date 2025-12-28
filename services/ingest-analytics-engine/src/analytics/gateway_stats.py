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


def get_gateway_environment_stats(save_to_db=True):
    """
    Calculate average temperature and humidity for each gateway.
    
    Returns statistics for all gateways.
    """
    config = Config()
    logger = get_logger('analytics.gateway_stats', log_file_path=config.get_analytics_log_path())
    
    try:
        # Get database collections
        manager = get_manager()
        collection = manager.get_collection(config.get_collection_name())
        analytics_collection = manager.get_collection(config.get_analytics_collection_name())
        
        # Calculate average temperature and humidity per gateway
        pipeline = [
            {'$group': {
                '_id': '$gateway_id',
                'avg_temperature': {'$avg': '$temperature'},
                'avg_humidity': {'$avg': '$humidity'}
            }},
            {'$project': {
                '_id': 0,
                'gateway_id': '$_id',
                'avg_temperature': 1,
                'avg_humidity': 1
            }}
        ]
        
        results = list(collection.aggregate(pipeline))
        logger.info(f"Calculated stats for {len(results)} gateways")
        
        # Save results
        if save_to_db:
            try:
                analytics_doc = {
                    'analytics_type': 'gateway_environment_stats',
                    'computed_at': datetime.utcnow(),
                    'results': results
                }
                analytics_collection.update_one(
                    {'analytics_type': 'gateway_environment_stats'},
                    {'$set': analytics_doc},
                    upsert=True
                )
            except Exception as e:
                logger.warning(f"Could not save to analytics collection: {str(e)}")
        
        return results
    
    except Exception as e:
        logger.error(f"Error calculating gateway stats: {str(e)}")
        return []

