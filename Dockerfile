# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED True
ENV FLASK_APP app.py
ENV FLASK_ENV production
ENV PORT 8080

# Set the working directory in the container
WORKDIR /app

# Copy only the necessary files
# Consider using a .dockerignore file to exclude unnecessary files
COPY . /app

# Install any needed packages specified in requirements.txt
# Ensure versions are pinned in requirements.txt for consistent builds
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8080 available to the world outside this container
EXPOSE $PORT

# Use a non-root user for running the application (create one if necessary)
# RUN useradd -m myuser
# USER myuser

# Run the application
# Use environment variables for configurable parameters like workers and threads
CMD exec gunicorn --certfile=selfsigned.crt --keyfile=selfsigned.key --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 0 app:app

# Optional: Add a health check (customize the command as needed)
# HEALTHCHECK CMD curl --fail http://localhost:$PORT/ || exit 1
