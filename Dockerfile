# Use the official Python image from the Docker Hub
FROM python:3.8-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update  \
    && apt-get install -y build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python -m venv /opt/venv

# Ensure venv is used for everything
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install dependencies
COPY setup.py /app/
COPY src /app/src
RUN pip install --upgrade pip && pip install -e .

# Copy the rest of the application code
COPY . /app/

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.web_app.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
