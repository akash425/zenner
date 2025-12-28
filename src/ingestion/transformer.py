from datetime import datetime
from src.utils.logger import get_logger
from src.utils.config import Config

# Fields that should be converted to float
FLOAT_FIELDS = [
    'temperature', 'humidity', 'barometric_pressure', 'analog_in_1', 'analog_in_2',
    'rssi', 'snr', 'latitude', 'longitude', 'frequency', 'bandwidth',
]

# Fields that should be converted to int
INT_FIELDS = ['spreading_factor']

# Common timestamp formats to try
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


def convert_to_float(value, field_name, logger, row_id):
    """Convert a value to float, handling errors gracefully."""
    if value is None:
        return None
    
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            logger.warning(f"Cannot convert {field_name} to float for {row_id}: '{value}'")
            return None
    
    if isinstance(value, (int, float)):
        return float(value)
    
    logger.warning(f"Unexpected type for {field_name} in {row_id}: {type(value).__name__}")
    return None


def convert_to_int(value, field_name, logger, row_id):
    """Convert a value to int, handling errors gracefully."""
    if value is None:
        return None
    
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        try:
            num = float(value)
            if num.is_integer():
                return int(num)
            logger.warning(f"{field_name} is not a whole number in {row_id}: '{value}'")
            return None
        except ValueError:
            logger.warning(f"Cannot convert {field_name} to int for {row_id}: '{value}'")
            return None
    
    if isinstance(value, int):
        return value
    
    if isinstance(value, float):
        if value.is_integer():
            return int(value)
        logger.warning(f"{field_name} is not a whole number in {row_id}: {value}")
        return None
    
    return None


def parse_timestamp(value, logger, row_id):
    """Parse a timestamp string into a datetime object."""
    if value is None:
        return None
    
    if isinstance(value, datetime):
        return value
    
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        
        # Try each format until one works
        for fmt in TIMESTAMP_FORMATS:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        
        logger.warning(f"Cannot parse timestamp for {row_id}: '{value}'")
        return None
    
    return None


def validate_gps(value, coord_type, logger, row_id):
    """Validate GPS coordinates are within valid ranges."""
    if value is None:
        return None
    
    if coord_type == 'latitude':
        if not (-90.0 <= value <= 90.0):
            logger.warning(f"Invalid latitude for {row_id}: {value}")
            return None
    elif coord_type == 'longitude':
        if not (-180.0 <= value <= 180.0):
            logger.warning(f"Invalid longitude for {row_id}: {value}")
            return None
    
    return value


def transform_row(row):
    """Convert data types in a validated row."""
    config = Config()
    logger = get_logger('ingestion.transformer', log_file_path=config.get_log_file_path())
    
    device_id = row.get('device_id', 'unknown')
    timestamp = row.get('timestamp', 'unknown')
    row_id = f"device_id={device_id}, timestamp={timestamp}"
    
    transformed = {}
    
    for key, value in row.items():
        # Empty strings become None
        if isinstance(value, str) and value.strip() == '':
            value = None
        
        # Convert timestamp
        if key == 'timestamp':
            transformed[key] = parse_timestamp(value, logger, row_id)
            continue
        
        # Convert float fields
        if key in FLOAT_FIELDS:
            float_value = convert_to_float(value, key, logger, row_id)
            
            # Validate GPS coordinates
            if key == 'latitude':
                transformed[key] = validate_gps(float_value, 'latitude', logger, row_id)
            elif key == 'longitude':
                transformed[key] = validate_gps(float_value, 'longitude', logger, row_id)
            else:
                transformed[key] = float_value
            continue
        
        # Convert int fields
        if key in INT_FIELDS:
            transformed[key] = convert_to_int(value, key, logger, row_id)
            continue
        
        # Keep everything else as-is
        transformed[key] = value
    
    return transformed
