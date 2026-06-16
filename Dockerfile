# Copy the application code
COPY . .

# Fix line endings and make the script executable
RUN sed -i 's/\r$//' start.sh && chmod +x start.sh

# Expose web GUI port
EXPOSE 5000

# Start the system using the startup script
CMD ["./start.sh"]
