import csv
from pathlib import Path
from typing import Optional
from src.utils.logger import get_logger
from src.utils.config import Config


def read_csv_file(file_path: str, start_line: Optional[int] = None):
    """
    Read CSV file and return rows as dictionaries.
    
    Can start from a specific line number to skip already processed rows.
    """
    config = Config()
    logger = get_logger('ingestion.reader', log_file_path=config.get_log_file_path())
    
    csv_path = Path(file_path)
    if not csv_path.exists():
        error_msg = f"CSV file not found: {file_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    # Adjust start line - line 0 is header, line 1 is first data row
    if start_line is None:
        start_line = 1
    elif start_line < 0:
        raise ValueError(f"start_line must be non-negative, got {start_line}")
    elif start_line == 0:
        logger.warning("start_line=0 means header row, adjusting to line 1")
        start_line = 1
    
    logger.info(f"Reading CSV file: {file_path} (starting from line {start_line})")
    
    row_count = 0
    skipped_count = 0
    
    try:
        # Try UTF-8 first
        try:
            with open(csv_path, 'r', encoding='utf-8', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                
                if reader.fieldnames is None:
                    logger.warning("CSV file appears to be empty")
                    return
                
                logger.info(f"CSV headers: {reader.fieldnames}")
                
                # Skip lines until we reach start_line
                current_line = 1
                for row in reader:
                    if current_line < start_line:
                        skipped_count += 1
                        current_line += 1
                        continue
                    
                    row_count += 1
                    current_line += 1
                    yield dict(row)
        
        except UnicodeDecodeError:
            # Try with error handling for encoding issues
            logger.warning("UTF-8 decoding error, trying with error handling")
            with open(csv_path, 'r', encoding='utf-8', errors='replace', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                
                if reader.fieldnames is None:
                    logger.warning("CSV file appears to be empty")
                    return
                
                logger.info(f"CSV headers: {reader.fieldnames}")
                
                current_line = 1
                for row in reader:
                    if current_line < start_line:
                        skipped_count += 1
                        current_line += 1
                        continue
                    
                    row_count += 1
                    current_line += 1
                    yield dict(row)
    
    except Exception as e:
        logger.error(f"Error reading CSV: {str(e)}")
        raise
    
    finally:
        if skipped_count > 0:
            logger.info(f"Finished reading CSV. Skipped {skipped_count} rows, read {row_count} new rows")
        else:
            logger.info(f"Finished reading CSV. Total rows: {row_count}")


def read_lorawan_uplink_devices(start_line: Optional[int] = None):
    """Read LoRaWAN uplink devices from the configured CSV file."""
    config = Config()
    csv_path = config.get_csv_file_path()
    return read_csv_file(csv_path, start_line=start_line)
