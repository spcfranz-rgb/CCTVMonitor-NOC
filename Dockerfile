# Use a lightweight Python base image
FROM python:3.9-slim

# Install system dependencies, fetch the Ookla repository, install speedtest, and clean up
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        iputils-ping \
        ffmpeg \
        sqlite3 \
        curl \
        gnupg2 \
        ca-certificates && \
    curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | bash && \
    apt-get install -y --no-install-recommends speedtest && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
# We append Gunicorn here so you don't have to manually edit requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn==21.2.0

# Copy the rest of your application code into the container
COPY . .

# Sanitize the startup script (removes Windows line-endings if copy-pasted) and make it executable
RUN sed -i 's/\r$//' start.sh && chmod +x start.sh

# Expose the port the web GUI will run on
EXPOSE 5000

# Boot the container using our custom startup script
CMD ["./start.sh"]
