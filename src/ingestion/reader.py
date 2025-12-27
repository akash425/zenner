import configparser
import csv
import logging
import sys
from pathlib import Path


CONFIG_FILE_PATH = './config.ini'


def setup_logger(log_file_path):
    Path(log_file_path).parent.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger('ingestion.reader')
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


def read_csv_file(file_path, log_file_path='./logs/ingestion.log'):
    logger = setup_logger(log_file_path)
    
    csv_path = Path(file_path)
    if not csv_path.exists():
        error_msg = f"CSV file not found: {file_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    logger.info(f"Reading CSV file: {file_path}")
    
    row_count = 0
    
    try:
        # Try UTF-8 first
        try:
            with open(csv_path, 'r', encoding='utf-8', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                
                if reader.fieldnames is None:
                    logger.warning("CSV file appears to be empty")
                    return
                
                logger.info(f"CSV headers: {reader.fieldnames}")
                
                for row in reader:
                    row_count += 1
                    yield dict(row)
        
        except UnicodeDecodeError:
            # Try with error handling
            logger.warning("UTF-8 decoding error, trying with error handling")
            with open(csv_path, 'r', encoding='utf-8', errors='replace', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                
                if reader.fieldnames is None:
                    logger.warning("CSV file appears to be empty")
                    return
                
                logger.info(f"CSV headers: {reader.fieldnames}")
                
                for row in reader:
                    row_count += 1
                    yield dict(row)
    
    except Exception as e:
        logger.error(f"Error reading CSV: {type(e).__name__}: {str(e)}")
        raise
    
    finally:
        logger.info(f"Finished reading CSV. Total rows: {row_count}")


def read_lorawan_uplink_devices():
    config = configparser.RawConfigParser()
    config_path = Path(CONFIG_FILE_PATH)
    
    if not config_path.exists():
        print(f"ERROR: Configuration file not found: {CONFIG_FILE_PATH}")
        sys.exit(1)
    
    config.read(config_path)
    
    csv_path = config.get('ingestion', 'csv_file_path', fallback='').strip()
    if not csv_path:
        print("ERROR: CSV file path not configured in config.ini")
        sys.exit(1)
    
    log_path = config.get('ingestion', 'log_file_path', fallback='./logs/ingestion.log').strip() or './logs/ingestion.log'
    
    return read_csv_file(csv_path, log_path)
