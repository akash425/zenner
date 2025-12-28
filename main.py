import sys

from src.utils.config import Config
from src.utils.logger import setup_ingestion_logger, setup_analytics_logger
from src.utils.checkpoint import read_checkpoint, write_checkpoint
from src.ingestion.reader import read_lorawan_uplink_devices
from src.ingestion.validator import validate_row
from src.ingestion.transformer import transform_row
from src.ingestion.loader import load_rows
from src.analytics.device_stats import get_top_active_devices
from src.analytics.weak_signal import get_weak_devices
from src.analytics.gateway_stats import get_gateway_environment_stats
from src.analytics.duplicates import get_duplicate_devices
from src.analytics.high_temperature import export_high_temperature_records

# Initialize configuration
try:
    config = Config()
except FileNotFoundError as e:
    print(f"ERROR: {str(e)}")
    sys.exit(1)


def format_number(value, decimals=2):
    """Format a number for display, handling None values."""
    if value is None:
        return 'N/A'
    if isinstance(value, (int, float)):
        return f"{value:.{decimals}f}"
    return str(value)


def run_analytics():
    """Run all analytics and show the results."""
    logger = setup_analytics_logger()
    logger.info("Starting analytics")
    
    print("\n" + "=" * 60)
    print("ANALYTICS RESULTS")
    print("=" * 60)
    
    # Top active devices
    try:
        devices = get_top_active_devices(limit=10)
        print("\nTop 10 Active Devices:")
        print("-" * 60)
        if devices:
            for i, device in enumerate(devices, 1):
                print(f"{i:2d}. Device: {device['device_id']:20s} | Uplinks: {device['count']:,}")
        else:
            print("No active devices found.")
    except Exception as e:
        logger.error(f"Error getting top devices: {str(e)}")
        print("\nTop Active Devices: ERROR")
    
    # Weak signal devices
    try:
        devices = get_weak_devices(limit=20)
        print("\nTop 20 Weak Signal Devices:")
        print("-" * 60)
        if devices:
            for i, device in enumerate(devices, 1):
                rssi = format_number(device.get('avg_rssi'))
                snr = format_number(device.get('avg_snr'))
                print(f"{i:2d}. Device: {device['device_id']:20s} | RSSI: {rssi:>8s} | SNR: {snr:>8s}")
        else:
            print("No weak signal devices found.")
    except Exception as e:
        logger.error(f"Error getting weak devices: {str(e)}")
        print("\nWeak Signal Devices: ERROR")
    
    # Gateway stats
    try:
        gateways = get_gateway_environment_stats()
        print("\nGateway Environment Statistics:")
        print("-" * 60)
        if gateways:
            for i, gateway in enumerate(gateways, 1):
                temp = format_number(gateway.get('avg_temperature'))
                humidity = format_number(gateway.get('avg_humidity'))
                print(f"{i:2d}. Gateway: {gateway['gateway_id']:20s} | Temp: {temp:>8s}°C | Humidity: {humidity:>8s}%")
        else:
            print("No gateway statistics found.")
    except Exception as e:
        logger.error(f"Error getting gateway stats: {str(e)}")
        print("\nGateway Stats: ERROR")
    
    # Duplicate devices
    try:
        devices = get_duplicate_devices()
        print("\nDevices with Duplicate Records:")
        print("-" * 60)
        if devices:
            for i, device in enumerate(devices, 1):
                print(f"{i:2d}. Device: {device['device_id']:20s} | Records: {device['count']:,}")
        else:
            print("No duplicate devices found.")
    except Exception as e:
        logger.error(f"Error getting duplicates: {str(e)}")
        print("\nDuplicate Devices: ERROR")
    
    # High temperature records
    try:
        records = export_high_temperature_records()
        print("\nHigh Temperature Records:")
        print("-" * 60)
        if records:
            print(f"Found {len(records)} records with temperature > 35°C")
            print(f"Exported to: ./data/high_temperature_records.json")
            print("\nFirst 5 records:")
            for i, record in enumerate(records[:5], 1):
                device_id = record.get('device_id', 'N/A')
                temp = format_number(record.get('temperature'))
                lat = format_number(record.get('latitude'), 6)
                lon = format_number(record.get('longitude'), 6)
                print(f"  {i}. Device: {device_id:20s} | Temp: {temp:>6s}°C | Lat: {lat:>10s} | Lon: {lon:>10s}")
            if len(records) > 5:
                print(f"  ... and {len(records) - 5} more records")
        else:
            print("No records found with temperature > 35°C")
    except Exception as e:
        logger.error(f"Error exporting high temp records: {str(e)}")
        print("\nHigh Temperature Export: ERROR")
    
    logger.info("Analytics completed")
    print("\n" + "=" * 60 + "\n")


def main():
    """Main function that runs the data ingestion and analytics pipeline."""
    logger = setup_ingestion_logger()
    
    try:
        logger.info("Starting data ingestion pipeline")
        
        # Read where we left off
        start_line = read_checkpoint()
        logger.info(f"Starting from line {start_line}")
        
        # Read and process CSV rows
        rows = read_lorawan_uplink_devices(start_line=start_line)
        
        valid_rows = []
        total_rows = 0
        
        for row in rows:
            total_rows += 1
            
            # Validate the row
            is_valid, cleaned_row = validate_row(row)
            if not is_valid:
                continue
            
            # Transform data types
            transformed_row = transform_row(cleaned_row)
            valid_rows.append(transformed_row)
        
        # Save to database
        logger.info("Saving rows to database")
        try:
            inserted_count, skipped_count = load_rows(iter(valid_rows))
        except Exception as e:
            logger.error(f"Failed to save rows: {str(e)}")
            print(f"ERROR: Failed to save rows: {str(e)}")
            inserted_count = 0
            skipped_count = 0
        
        # Update checkpoint
        if total_rows > 0:
            effective_start = max(1, start_line)
            last_line = effective_start + total_rows - 1
            try:
                write_checkpoint(last_line)
                logger.info(f"Checkpoint updated to line {last_line}")
            except Exception as e:
                logger.error(f"Could not update checkpoint: {str(e)}")
        
        # Show summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Starting from line:      {start_line:,}")
        print(f"Total rows read:         {total_rows:,}")
        print(f"Valid rows:              {len(valid_rows):,}")
        print(f"Rows inserted:           {inserted_count:,}")
        print(f"Rows skipped:            {skipped_count:,}")
        
        if total_rows > 0:
            print(f"Validation success rate: {(len(valid_rows) / total_rows) * 100:.2f}%")
        if valid_rows:
            print(f"Insertion success rate:  {(inserted_count / len(valid_rows)) * 100:.2f}%")
        print("=" * 60 + "\n")
        
        logger.info("Ingestion completed successfully")
        
        # Run analytics
        try:
            run_analytics()
        except Exception as e:
            logger.warning(f"Analytics error: {str(e)}")
            print(f"\nWARNING: Analytics error: {str(e)}")
        
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"CSV file not found: {str(e)}")
        print(f"ERROR: CSV file not found: {str(e)}")
        return 1
    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        print("\nWARNING: Interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        print(f"ERROR: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

