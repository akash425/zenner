import logging
from pathlib import Path


REQUIRED_FIELDS = ['device_id', 'gateway_id', 'timestamp', 'rssi', 'snr']


def setup_logger(log_file_path):
    Path(log_file_path).parent.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger('ingestion.validator')
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


def validate_row(row, log_file_path='./logs/ingestion.log'):
    logger = setup_logger(log_file_path)
    
    device_id = row.get('device_id', 'unknown')
    timestamp = row.get('timestamp', 'unknown')
    row_id = f"device_id={device_id}, timestamp={timestamp}"
    
    # Check for missing required fields
    missing_fields = [field for field in REQUIRED_FIELDS if field not in row]
    if missing_fields:
        error_msg = f"Validation failed for row [{row_id}]: Missing required fields: {', '.join(missing_fields)}"
        logger.warning(error_msg)
        return (False, error_msg)
    
    # Check for empty values in required fields
    empty_fields = []
    for field in REQUIRED_FIELDS:
        value = row.get(field)
        if value is None or (isinstance(value, str) and value.strip() == ''):
            empty_fields.append(field)
    
    if empty_fields:
        error_msg = f"Validation failed for row [{row_id}]: Empty values in required fields: {', '.join(empty_fields)}"
        logger.warning(error_msg)
        return (False, error_msg)
    
    # Clean row - strip strings
    cleaned = {}
    for key, value in row.items():
        if isinstance(value, str):
            cleaned[key] = value.strip()
        elif value is None:
            cleaned[key] = ''
        else:
            cleaned[key] = str(value)
    
    return (True, cleaned)
