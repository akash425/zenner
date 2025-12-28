FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir -p /app/logs

# Copy shared code
COPY shared/ /app/shared/

# Copy service code
COPY services/api-service/ /app/services/api-service/

# Copy configuration
COPY config.ini /app/

# Copy requirements
COPY requirements.txt /app/

# Install Python dependencies including Flask
RUN pip install --no-cache-dir -r requirements.txt flask==2.3.3

# Set Python path
ENV PYTHONPATH=/app:/app/shared

# Expose Flask port
EXPOSE 5000

# Set working directory to service
WORKDIR /app/services/api-service

# Run the Flask app
CMD ["python", "app.py"]

