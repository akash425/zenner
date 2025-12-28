# Zenner - LoRaWAN Data Ingestion and Analytics Platform

A comprehensive data pipeline system for ingesting, processing, and analyzing LoRaWAN uplink device data. The platform provides automated data ingestion, validation, transformation, and analytics capabilities with a RESTful API and modern web interface for accessing results.

## Overview

Zenner is a microservices-based platform that processes LoRaWAN device data from CSV files, stores it in MongoDB, and provides analytics insights including:
- Top active devices
- Weak signal device detection
- Gateway environment statistics
- Duplicate device identification
- High temperature record tracking

## Quick Start

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd zenner
   echo "MONGO_URI=your_mongodb_connection_string" > .env
   ```

2. **Place your CSV data**:
   ```bash
   # Place your CSV file at: ./data/lorawan_uplink_devices.csv
   ```

3. **Start services**:
   ```bash
   docker-compose up -d
   ```

4. **Access the dashboard**:
   - Open [http://localhost:3000](http://localhost:3000) in your browser
   - API available at [http://localhost:5000](http://localhost:5000)

See the [Installation](#installation) section for detailed instructions.

## Architecture

The project consists of multiple services:

- **ingest-analytics-engine**: Core data processing service that handles CSV ingestion, validation, transformation, and analytics computation
- **api-service**: Flask-based REST API that serves analytics results with CORS support
- **ui-service**: React-based web interface with Tailwind CSS for visualizing analytics and device data
- **shared**: Common utilities and configurations used across services

## Tech Stack

### Backend
- **Python 3.11+**: Core language for data processing
- **Flask**: REST API framework
- **MongoDB**: Data storage and analytics
- **APScheduler**: Job scheduling for automated processing
- **Pandas**: Data manipulation and CSV processing

### Frontend
- **React 19**: Modern UI framework
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **Axios**: HTTP client for API communication
- **Nginx**: Web server for production deployment

## Features

### Data Processing
- **Incremental Data Processing**: Checkpoint-based system allows resuming from the last processed line
- **Data Validation**: Comprehensive validation of CSV rows before insertion
- **Data Transformation**: Automatic type conversion and data cleaning
- **Analytics Engine**: Multiple analytics modules for device and gateway insights
- **Scheduled Processing**: Automated job scheduling using APScheduler

### API & Services
- **RESTful API**: HTTP endpoints for accessing analytics results with CORS support
- **Web Dashboard**: Modern React-based UI for visualizing analytics and device data
- **Real-time Updates**: UI automatically fetches latest analytics data
- **Responsive Design**: Mobile-friendly interface built with Tailwind CSS

### Infrastructure
- **Docker Support**: Containerized services with Docker Compose orchestration
- **Microservices Architecture**: Independent, scalable services
- **Health Monitoring**: Health check endpoints for service monitoring

## Prerequisites

### For Docker Deployment (Recommended)
- Docker and Docker Compose
- MongoDB (local or MongoDB Atlas)
- `.env` file with MongoDB connection string

### For Local Development
- Python 3.11+
- Node.js 16+ and npm (for UI service development)
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

5. Access the services:
   - **Web UI**: [http://localhost:3000](http://localhost:3000)
   - **API Service**: [http://localhost:5000](http://localhost:5000)
   - **API Health Check**: [http://localhost:5000/api/health](http://localhost:5000/api/health)

6. View logs:
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f ingest-analytics-engine
docker-compose logs -f api-service
docker-compose logs -f ui-service
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

Analytics are automatically computed after each ingestion run. You can access them via:

1. **Web UI** (Recommended): Open [http://localhost:3000](http://localhost:3000) in your browser to view the dashboard with:
   - Overview dashboard with key metrics
   - Device analytics and statistics
   - Gateway information
   - Alert management
   - Interactive data tables

2. **REST API**: Access analytics programmatically:

```bash
# Get top active devices
curl http://localhost:5000/api/analytics/top-devices

# Get weak signal devices
curl http://localhost:5000/api/analytics/weak-devices

# Get gateway statistics
curl http://localhost:5000/api/analytics/gateway-stats

# Get duplicate devices
curl http://localhost:5000/api/analytics/duplicates

# Get high temperature records
curl http://localhost:5000/api/analytics/high-temperature

# Health check
curl http://localhost:5000/api/health
```

### Scheduled Jobs

The scheduler runs ingestion and analytics jobs based on the cron expression in `config.ini` (default: daily at midnight).

### Web Dashboard

The UI service provides a comprehensive web dashboard accessible at [http://localhost:3000](http://localhost:3000) with the following pages:

- **Overview Dashboard**: High-level metrics and statistics
- **Devices**: Device analytics, top active devices, and device details
- **Gateways**: Gateway statistics and environment data
- **Alerts**: High temperature alerts and device health notifications

The dashboard features:
- Interactive data tables with sorting and filtering
- Real-time data fetching from the API
- Health status indicators
- Responsive design for all screen sizes

## API Endpoints

The API service provides the following endpoints:

- `GET /api/health` - Health check
- `GET /api/analytics/top-devices` - Top active devices
- `GET /api/analytics/weak-devices` - Devices with weak signals
- `GET /api/analytics/gateway-stats` - Gateway environment statistics
- `GET /api/analytics/duplicates` - Devices with duplicate records
- `GET /api/analytics/high-temperature` - High temperature records

All analytics endpoints return JSON with the following structure:
```json
{
  "success": true,
  "data": [...],
  "computed_at": "2024-01-01T00:00:00Z"
}
```

**Note**: The API base URL is `/api` and CORS is enabled for cross-origin requests from the UI service.

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
# API will be available at http://localhost:5000

# Run UI service (development mode)
cd services/ui-service
npm install
npm start
# UI will be available at http://localhost:3000
```

### Environment Variables for UI Service

The UI service can be configured with environment variables:

```bash
# Create .env file in services/ui-service/
REACT_APP_API_BASE_URL=http://localhost:5000/api
```

If not set, it defaults to `http://localhost:5000/api` for development.

### Testing

Check service health:
```bash
# API health check
curl http://localhost:5000/api/health

# Test API endpoints
curl http://localhost:5000/api/analytics/top-devices
```

## Troubleshooting

### Common Issues

1. **MongoDB Connection Errors**: Verify your `MONGO_URI` in the `.env` file
2. **CSV File Not Found**: Ensure the CSV file path in `config.ini` is correct
3. **Permission Errors**: Check file permissions for `data/` and `logs/` directories
4. **Port Conflicts**: 
   - Ensure port 5000 is available for the API service
   - Ensure port 3000 is available for the UI service
5. **UI Service Not Loading**: 
   - Check if the API service is running and accessible
   - Verify `REACT_APP_API_BASE_URL` environment variable if running UI separately
   - Check browser console for CORS or network errors
6. **API Not Responding**: Check service health and logs for errors

### Check Logs

```bash
# Docker logs
docker-compose logs ingest-analytics-engine
docker-compose logs api-service
docker-compose logs ui-service

# Application logs
tail -f logs/ingestion.log
tail -f logs/analytics.log

# View real-time logs for all services
docker-compose logs -f
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

