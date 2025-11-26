FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for couchbase SDK
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY cos/ cos/

# Install dependencies
RUN pip install --no-cache-dir .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "cos.main:app", "--host", "0.0.0.0", "--port", "8000"]
