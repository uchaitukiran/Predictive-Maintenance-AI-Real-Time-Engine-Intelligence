# Use Python 3.10 Slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for PostgreSQL and ML
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
# Prevents Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED 1

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project (src, webapp, artifacts, etc.)
COPY . .

# Expose port 8000 (matching your app)
EXPOSE 8000

# Run Gunicorn
# We point to 'src.api.app:app' because app.py is inside src/api
CMD ["gunicorn", "-b", "0.0.0.0:8000", "src.api.app:app"]