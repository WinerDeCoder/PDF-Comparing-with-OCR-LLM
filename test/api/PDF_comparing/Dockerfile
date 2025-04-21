# Use an official Python image
#!/bin/bash
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# RUN apt-get update --fix-missing && apt-get install -y --fix-missing build-essential

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend files
COPY . .

# Expose the port that FastAPI will run on (default: 8000)
EXPOSE 8000

# Command to run the FastAPI application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
