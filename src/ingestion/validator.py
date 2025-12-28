from src.utils.logger import get_logger
from src.utils.config import Config

# Fields that must be present and not empty
REQUIRED_FIELDS = ['device_id', 'gateway_id', 'timestamp', 'rssi', 'snr']


def validate_row(row):
    """Check if a row has all required fields and clean it up."""
    config = Config()
    logger = get_logger('ingestion.validator', log_file_path=config.get_log_file_path())
    
    device_id = row.get('device_id', 'unknown')
    timestamp = row.get('timestamp', 'unknown')
    row_id = f"device_id={device_id}, timestamp={timestamp}"
    
    # Check if all required fields are present
    missing_fields = [field for field in REQUIRED_FIELDS if field not in row]
    if missing_fields:
        logger.warning(f"Missing required fields for {row_id}: {', '.join(missing_fields)}")
        return (False, f"Missing fields: {', '.join(missing_fields)}")
    
    # Check if required fields have values
    empty_fields = []
    for field in REQUIRED_FIELDS:
        value = row.get(field)
        if value is None or (isinstance(value, str) and value.strip() == ''):
            empty_fields.append(field)
    
    if empty_fields:
        logger.warning(f"Empty required fields for {row_id}: {', '.join(empty_fields)}")
        return (False, f"Empty fields: {', '.join(empty_fields)}")
    
    # Clean up the row - strip whitespace from strings
    cleaned = {}
    for key, value in row.items():
        if isinstance(value, str):
            cleaned[key] = value.strip()
        elif value is None:
            cleaned[key] = ''
        else:
            cleaned[key] = str(value)
    
    return (True, cleaned)
