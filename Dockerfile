# Use the official Python image as the base image
FROM python:3.9-slim


# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Set the working directory in the container
WORKDIR /app-docker
# Install required system packages
# Install necessary build tools and compilers
# RUN apt-get  update && apt-get install -y \
#     build-essential \
#     gcc \
#     g++ \
#     make \
#     libmagic-dev \
#     && rm -rf /var/lib/apt/lists/*

# RUN g++ --version

# Copy the requirements file to the container
COPY requirements.txt .

# Install the required dependencies
RUN pip install --upgrade pip &&  pip install --no-cache-dir -r requirements.txt

# Copy the entire FastAPI app code into the container
COPY . .

# Expose the port that FastAPI and Dash will run on
EXPOSE 8000

# Run the FastAPI app with Uvicorn
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" , "--reload"]

