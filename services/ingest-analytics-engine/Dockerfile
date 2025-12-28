FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir -p /app/data /app/logs

# Copy shared code
COPY shared/ /app/shared/

# Copy service code
COPY services/ingest-analytics-engine/ /app/services/ingest-analytics-engine/

# Copy main entry point
COPY main.py /app/

# Copy configuration
COPY config.ini /app/

# Copy requirements
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set Python path
ENV PYTHONPATH=/app:/app/shared:/app/services/ingest-analytics-engine

# Default command - run the main pipeline
CMD ["python", "main.py"]

