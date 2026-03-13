#!/bin/bash

# Ensure the virtual environment is activated
source venv/bin/activate

echo "Building Docker image..."
docker build -t todo_printer --platform linux/arm64/v8 .

echo "Running Docker container..."
docker run -p 8333:8333 -d --name todo_printer_container todo_printer

echo "Docker container started in the background. Services are accessible on localhost:8333 (CORE)"

# You can add commands here to check logs or interact with the container if needed
# For example: docker logs -f todo_printer_container

# To stop and remove the container later:
# docker stop todo_printer_container
# docker rm todo_printer_container
