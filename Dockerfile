FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends iputils-ping ffmpeg sqlite3 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies and Gunicorn
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn==21.2.0

# Copy the application code
COPY . .

# Expose web GUI port
EXPOSE 5000

# Start Gunicorn server with 4 worker threads instead of Flask's dev server
CMD ["gunicorn", "-w", "4", "--threads", "2", "-b", "0.0.0.0:5000", "app:app"]
