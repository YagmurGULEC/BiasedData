#!/bin/bash

# Define the service name
service_name="fastapi-data-app"

# Get the container ID
container_id=$(docker ps --filter "name=$service_name" --format "{{.ID}}")

# Check if the container ID was found
if [[ -n "$container_id" ]]; then
    echo "Running tests inside container ID: $container_id"
    docker exec -it "$container_id" /bin/bash -c "pytest -s -v tests/"
else
    echo "No running container found for service '$service_name'"
fi
