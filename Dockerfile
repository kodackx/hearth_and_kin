# Define a build argument for the Python version
ARG PYTHON_VERSION=3.12.0

# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:${PYTHON_VERSION}-slim as requirements-stage

# Configure Python to not buffer "stdout" or create .pyc files
ENV PYTHONBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Initialize poetry
WORKDIR /tmp
RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry env use ${PYTHON_VERSION}
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes


FROM python:${PYTHON_VERSION}-slim

# add images to the container
WORKDIR /app
VOLUME /app/src
VOLUME /app/db

# Install dependencies
COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "src.main:app"]