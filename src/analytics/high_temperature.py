import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from src.utils.logger import get_logger
from src.utils.mongo_client import get_manager
from src.utils.config import Config


def export_high_temperature_records(output_file_path=None, temperature_threshold=35.0, save_to_db=True):
    """
    Find and export records where temperature is above the threshold.
    
    Saves results to a JSON file and optionally to the analytics collection.
    """
    config = Config()
    logger = get_logger('analytics.high_temperature', log_file_path=config.get_analytics_log_path())
    
    if output_file_path is None:
        output_file_path = './data/high_temperature_records.json'
    
    try:
        # Get database collections
        manager = get_manager()
        collection = manager.get_collection(config.get_collection_name())
        analytics_collection = manager.get_collection(config.get_analytics_collection_name())
        
        # Find records with high temperature
        query = {'temperature': {'$gt': temperature_threshold}}
        projection = {
            '_id': 0,
            'device_id': 1,
            'latitude': 1,
            'longitude': 1,
            'temperature': 1
        }
        
        results = list(collection.find(query, projection))
        logger.info(f"Found {len(results)} records with temperature > {temperature_threshold}°C")
        
        # Save to JSON file
        output_path = Path(output_file_path)
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"Exported {len(results)} records to {output_file_path}")
        except Exception as e:
            logger.error(f"Could not write JSON file: {str(e)}")
        
        # Save metadata to analytics collection
        if save_to_db:
            try:
                analytics_doc = {
                    'analytics_type': 'high_temperature_records',
                    'computed_at': datetime.utcnow(),
                    'parameters': {
                        'temperature_threshold': temperature_threshold,
                        'output_file_path': str(output_file_path)
                    },
                    'result_count': len(results),
                    'output_file': str(output_file_path)
                }
                analytics_collection.update_one(
                    {'analytics_type': 'high_temperature_records'},
                    {'$set': analytics_doc},
                    upsert=True
                )
            except Exception as e:
                logger.warning(f"Could not save to analytics collection: {str(e)}")
        
        return results
    
    except Exception as e:
        logger.error(f"Error finding high temperature records: {str(e)}")
        return []

