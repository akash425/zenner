import configparser
import logging
import sys
from pathlib import Path

from src.ingestion.reader import read_lorawan_uplink_devices
from src.ingestion.validator import validate_row
from src.ingestion.transformer import transform_row
from src.ingestion.loader import load_rows

# Load config
config = configparser.RawConfigParser()
config_path = Path('./config.ini')
if not config_path.exists():
    print(f"ERROR: Configuration file not found: ./config.ini")
    sys.exit(1)

config.read(config_path)
LOG_FILE_PATH = config.get('ingestion', 'log_file_path', fallback='./logs/ingestion.log').strip() or './logs/ingestion.log'


def setup_logger(log_file_path):
    Path(log_file_path).parent.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger('ingestion.main')
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


def main():
    logger = setup_logger(LOG_FILE_PATH)
    
    try:
        logger.info("=" * 60)
        logger.info("Starting LoRaWAN Uplink Data Ingestion Pipeline")
        logger.info("=" * 60)
        
        # Read and process rows
        logger.info("Reading CSV file")
        rows = read_lorawan_uplink_devices()
        
        transformed_rows = []
        total_rows = 0
        
        for row in rows:
            total_rows += 1
            
            is_valid, result = validate_row(row, LOG_FILE_PATH)
            if not is_valid:
                continue
            
            transformed_row = transform_row(result, LOG_FILE_PATH)
            transformed_rows.append(transformed_row)
        
        valid_rows = len(transformed_rows)
        
        # Load into MongoDB
        logger.info("Loading rows into MongoDB")
        try:
            inserted_rows, skipped_rows = load_rows(iter(transformed_rows), log_file_path=LOG_FILE_PATH)
        except Exception as e:
            logger.error(f"Failed to load rows: {str(e)}")
            print(f"ERROR: Failed to load rows: {str(e)}")
            inserted_rows = 0
            skipped_rows = 0
        
        # Print summary
        print("\n" + "=" * 60)
        print("INGESTION PIPELINE SUMMARY")
        print("=" * 60)
        print(f"Total rows read:        {total_rows:,}")
        print(f"Valid rows:             {valid_rows:,}")
        print(f"Rows inserted:          {inserted_rows:,}")
        print(f"Rows skipped:           {skipped_rows:,}")
        
        if total_rows > 0:
            print(f"Validation success rate: {(valid_rows / total_rows) * 100:.2f}%")
        if valid_rows > 0:
            print(f"Insertion success rate:  {(inserted_rows / valid_rows) * 100:.2f}%")
        print("=" * 60 + "\n")
        
        logger.info("Ingestion pipeline completed successfully")
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"CSV file not found: {str(e)}")
        print(f"ERROR: CSV file not found: {str(e)}")
        return 1
    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user")
        print("\nWARNING: Pipeline interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}: {str(e)}", exc_info=True)
        print(f"ERROR: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

