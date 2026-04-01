FROM python:3.11-slim

# Install system dependencies needed by Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies first (to leverage Docker cache)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the repository
COPY . .

# Expose port 8000 for the FastAPI service
EXPOSE 8000

# Run the application with uvicorn. The host and port can be overridden
# via environment variables at runtime. The reload flag should not be used
# in production but can be enabled during development.
CMD ["uvicorn", "economic_system.app.main:app", "--host", "0.0.0.0", "--port", "8000"]