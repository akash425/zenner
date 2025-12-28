# Zenner - LoRaWAN Data Ingestion and Analytics Platform

A comprehensive data pipeline system for ingesting, processing, and analyzing LoRaWAN uplink device data. The platform provides automated data ingestion, validation, transformation, and analytics capabilities with a RESTful API for accessing results.

## Overview

Zenner is a microservices-based platform that processes LoRaWAN device data from CSV files, stores it in MongoDB, and provides analytics insights including:
- Top active devices
- Weak signal device detection
- Gateway environment statistics
- Duplicate device identification
- High temperature record tracking

## Architecture

The project consists of multiple services:

- **ingest-analytics-engine**: Core data processing service that handles CSV ingestion, validation, transformation, and analytics computation
- **api-service**: Flask-based REST API that serves analytics results
- **ui-service**: User interface for visualizing analytics (see service-specific README)
- **shared**: Common utilities and configurations used across services

## Features

- **Incremental Data Processing**: Checkpoint-based system allows resuming from the last processed line
- **Data Validation**: Comprehensive validation of CSV rows before insertion
- **Data Transformation**: Automatic type conversion and data cleaning
- **Analytics Engine**: Multiple analytics modules for device and gateway insights
- **Scheduled Processing**: Automated job scheduling using APScheduler
- **RESTful API**: HTTP endpoints for accessing analytics results
- **Docker Support**: Containerized services with Docker Compose orchestration

## Prerequisites

- Python 3.11+
- Docker and Docker Compose
- MongoDB (local or MongoDB Atlas)
- `.env` file with MongoDB connection string

## Project Structure

```
zenner/
├── config.ini                 # Configuration file
├── docker-compose.yml         # Docker Compose configuration
├── Dockerfile                 # Base Dockerfile
├── main.py                    # Main entry point for ingestion
├── requirements.txt           # Python dependencies
├── data/                      # Data directory (CSV files, checkpoints)
├── logs/                      # Log files
├── services/
│   ├── ingest-analytics-engine/  # Data ingestion and analytics service
│   ├── api-service/              # REST API service
│   └── ui-service/               # User interface service
└── shared/                    # Shared utilities and configurations
```

## Configuration

### config.ini

The main configuration file contains settings for:

- **Database**: MongoDB database and collection names
- **Ingestion**: CSV file path, batch size, checkpoint location
- **Scheduler**: Cron expression for scheduled jobs

### Environment Variables

Create a `.env` file in the project root with:

```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
```

## Installation

### Using Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd zenner
```

2. Create a `.env` file with your MongoDB connection string:
```bash
echo "MONGO_URI=your_mongodb_connection_string" > .env
```

3. Ensure your CSV data file is in the `data/` directory:
```bash
# Place your CSV file at: ./data/lorawan_uplink_devices.csv
```

4. Start all services:
```bash
docker-compose up -d
```

5. View logs:
```bash
docker-compose logs -f
```

### Manual Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Configure `config.ini` with your settings

3. Set up environment variables (`.env` file or export)

4. Run the ingestion pipeline:
```bash
python main.py
```

## Usage

### Data Ingestion

The ingestion engine processes CSV files in the following stages:

1. **Read**: Reads CSV rows starting from the last checkpoint
2. **Validate**: Validates each row for required fields and data quality
3. **Transform**: Converts data types and cleans values
4. **Load**: Bulk inserts valid rows into MongoDB
5. **Analytics**: Computes analytics and stores results

### Running Analytics

Analytics are automatically computed after each ingestion run. You can also access them via the API:

```bash
# Get top active devices
curl http://localhost:5000/analytics/top-devices

# Get weak signal devices
curl http://localhost:5000/analytics/weak-devices

# Get gateway statistics
curl http://localhost:5000/analytics/gateway-stats

# Get duplicate devices
curl http://localhost:5000/analytics/duplicates

# Get high temperature records
curl http://localhost:5000/analytics/high-temperature
```

### Scheduled Jobs

The scheduler runs ingestion and analytics jobs based on the cron expression in `config.ini` (default: daily at midnight).

## API Endpoints

The API service provides the following endpoints:

- `GET /health` - Health check
- `GET /analytics/top-devices` - Top active devices
- `GET /analytics/weak-devices` - Devices with weak signals
- `GET /analytics/gateway-stats` - Gateway environment statistics
- `GET /analytics/duplicates` - Devices with duplicate records
- `GET /analytics/high-temperature` - High temperature records

All analytics endpoints return JSON with the following structure:
```json
{
  "success": true,
  "data": [...],
  "computed_at": "2024-01-01T00:00:00Z"
}
```

## Data Format

The system expects CSV files with LoRaWAN uplink device data. Required fields include:
- Device identifiers
- Signal strength (RSSI)
- Signal-to-noise ratio (SNR)
- Gateway information
- Environmental data (temperature, humidity)
- Location data (latitude, longitude)
- Timestamps

See the service-specific READMEs for detailed field requirements.

## Logging

Logs are written to the `logs/` directory:
- `logs/ingestion.log` - Ingestion process logs
- `logs/analytics.log` - Analytics computation logs

## Development

### Running Services Individually

Each service can be run independently:

```bash
# Run ingestion engine
cd services/ingest-analytics-engine
python src/scheduler.py

# Run API service
cd services/api-service
python app.py
```

### Testing

Check service health:
```bash
curl http://localhost:5000/health
```

## Troubleshooting

### Common Issues

1. **MongoDB Connection Errors**: Verify your `MONGO_URI` in the `.env` file
2. **CSV File Not Found**: Ensure the CSV file path in `config.ini` is correct
3. **Permission Errors**: Check file permissions for `data/` and `logs/` directories
4. **Port Conflicts**: Ensure port 5000 is available for the API service

### Check Logs

```bash
# Docker logs
docker-compose logs ingest-analytics-engine
docker-compose logs api-service

# Application logs
tail -f logs/ingestion.log
tail -f logs/analytics.log
```

## Contributing

1. Follow the existing code structure and patterns
2. Ensure all services have proper error handling
3. Update relevant README files when adding features
4. Test changes with sample data before committing

## License

[Add your license information here]

## Support

For issues and questions, please refer to the service-specific README files:
- [Ingest Analytics Engine README](services/ingest-analytics-engine/README.md)
- [API Service README](services/api-service/README.md)
- [UI Service README](services/ui-service/README.md)
- [Shared Components README](shared/README.md)

