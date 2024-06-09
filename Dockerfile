# Define a build argument for the Python version
ARG PYTHON_VERSION=3.12.0


# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:${PYTHON_VERSION}-slim as requirements-stage

# Configure Python to not buffer "stdout" or create .pyc files
ENV PYTHONBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV POETRY_VERSION=1.2.2

# Initialize poetry
WORKDIR /tmp
RUN pip install poetry==${POETRY_VERSION}
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry env use ${PYTHON_VERSION}
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Install the app
FROM python:${PYTHON_VERSION}-slim

# add images to the container
WORKDIR /app
VOLUME /app/src

# Install dependencies
COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt
COPY ./gunicorn_config.py /app/gunicorn_config.py
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
COPY . /app
EXPOSE 8000

# Run the application:
CMD ["gunicorn", "-c", "/app/gunicorn_config.py", "-k", "uvicorn.workers.UvicornWorker", "src.main:app"]