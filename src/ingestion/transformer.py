import logging
from datetime import datetime
from pathlib import Path

# Fields to convert to float
FLOAT_FIELDS = [
    'temperature', 'humidity', 'barometric_pressure', 'analog_in_1', 'analog_in_2',
    'rssi', 'snr', 'latitude', 'longitude', 'frequency', 'bandwidth',
]

# Fields to convert to int
INT_FIELDS = ['spreading_factor']

# Timestamp formats to try
TIMESTAMP_FORMATS = [
    '%Y-%m-%d %H:%M:%S',
    '%Y-%m-%d %H:%M:%S.%f',
    '%Y-%m-%dT%H:%M:%S',
    '%Y-%m-%dT%H:%M:%S.%f',
    '%Y-%m-%dT%H:%M:%SZ',
    '%Y-%m-%dT%H:%M:%S.%fZ',
    '%Y/%m/%d %H:%M:%S',
    '%Y/%m/%d %H:%M:%S.%f',
]


def setup_logger(log_file_path):
    Path(log_file_path).parent.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger('ingestion.transformer')
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


def convert_to_float(value, field_name, logger, row_id):
    if value is None:
        return None
    
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            logger.warning(f"Failed to convert {field_name} to float for row [{row_id}]: value='{value}'")
            return None
    
    if isinstance(value, (int, float)):
        return float(value)
    
    logger.warning(f"Unexpected type for {field_name} in row [{row_id}]: type={type(value).__name__}")
    return None


def convert_to_int(value, field_name, logger, row_id):
    if value is None:
        return None
    
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        try:
            float_val = float(value)
            if float_val.is_integer():
                return int(float_val)
            logger.warning(f"{field_name} is not a whole number in row [{row_id}]: value='{value}'")
            return None
        except ValueError:
            logger.warning(f"Failed to convert {field_name} to int for row [{row_id}]: value='{value}'")
            return None
    
    if isinstance(value, int):
        return value
    
    if isinstance(value, float):
        if value.is_integer():
            return int(value)
        logger.warning(f"{field_name} is not a whole number in row [{row_id}]: value={value}")
        return None
    
    return None


def parse_timestamp(value, logger, row_id):
    if value is None:
        return None
    
    if isinstance(value, datetime):
        return value
    
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        
        for fmt in TIMESTAMP_FORMATS:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        
        logger.warning(f"Failed to parse timestamp for row [{row_id}]: value='{value}'")
        return None
    
    return None


def validate_gps(value, coord_type, logger, row_id):
    if value is None:
        return None
    
    if coord_type == 'latitude':
        if not (-90.0 <= value <= 90.0):
            logger.warning(f"Invalid latitude for row [{row_id}]: {value}. Setting to None.")
            return None
    elif coord_type == 'longitude':
        if not (-180.0 <= value <= 180.0):
            logger.warning(f"Invalid longitude for row [{row_id}]: {value}. Setting to None.")
            return None
    
    return value


def transform_row(row, log_file_path='./logs/ingestion.log'):
    logger = setup_logger(log_file_path)
    
    device_id = row.get('device_id', 'unknown')
    timestamp = row.get('timestamp', 'unknown')
    row_id = f"device_id={device_id}, timestamp={timestamp}"
    
    transformed = {}
    
    for key, value in row.items():
        # Convert empty strings to None
        if isinstance(value, str) and value.strip() == '':
            value = None
        
        # Handle timestamp
        if key == 'timestamp':
            transformed[key] = parse_timestamp(value, logger, row_id)
            continue
        
        # Handle float fields
        if key in FLOAT_FIELDS:
            float_value = convert_to_float(value, key, logger, row_id)
            
            if key == 'latitude':
                transformed[key] = validate_gps(float_value, 'latitude', logger, row_id)
            elif key == 'longitude':
                transformed[key] = validate_gps(float_value, 'longitude', logger, row_id)
            else:
                transformed[key] = float_value
            continue
        
        # Handle int fields
        if key in INT_FIELDS:
            transformed[key] = convert_to_int(value, key, logger, row_id)
            continue
        
        # Keep other fields as-is
        transformed[key] = value
    
    return transformed
