# Use the official Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app.py .

# Set the environment variables
ENV APP_VERSION="1.0"
ENV PORT 8080

# Expose the port used by the container (matches the service YAML targetPort)
EXPOSE 8080

# Run the application using Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
