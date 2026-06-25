# Dockerfile
# Use a lightweight Python base image
FROM python:3.9-slim

# Install system dependencies, fetch the Ookla repository, install speedtest, and clean up
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        iputils-ping \
        traceroute \
        ffmpeg \
        sqlite3 \
        curl \
        gnupg2 \
        ca-certificates && \
    curl -s [https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh](https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh) | bash && \
    apt-get install -y --no-install-recommends speedtest && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Expose the port the web GUI will run on
EXPOSE 5000

# Boot the container using Gunicorn with Eventlet async workers
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "-b", "0.0.0.0:5000", "app:app"]
