# Define a build argument for the Python version
ARG PYTHON_VERSION=3.12.0

# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:${PYTHON_VERSION}-slim as builder

# Configure Python to not buffer "stdout" or create .pyc files
ENV PYTHONBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV POETRY_VERSION=1.2.2

# Install dependencies and build stage tools
WORKDIR /tmp
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && pip install --no-cache-dir "poetry==$POETRY_VERSION" \
    && rm -rf /var/lib/apt/lists/*

# Copy the project files and install dependencies
COPY pyproject.toml poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Final stage
FROM python:${PYTHON_VERSION}-slim

# Configure Python to not buffer "stdout" or create .pyc files
ENV PYTHONBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set up the working directory
WORKDIR /app

# Copy and install dependencies
COPY --from=builder /tmp/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copy application files
COPY . /app

# Expose the application port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "-c", "/app/gunicorn_config.py", "-k", "uvicorn.workers.UvicornWorker", "src.main:app"]