# Dockerfile
# Use a lightweight official Python image
FROM python:3.9-slim

# Set environment variable for version (for the app to use)
ENV APP_VERSION=1.0.0

# Set the working directory in the container
WORKDIR /app

# Copy the dependency file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]