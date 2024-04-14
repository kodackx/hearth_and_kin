# Define a build argument for the Python version
ARG PYTHON_VERSION=3.12.0

# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:${PYTHON_VERSION}-slim

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.7.1 \
    MULTIDICT_NO_EXTENSIONS=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    VIRTUAL_ENVIRONMENT_PATH="/app/.venv"

ENV PATH="$VIRTUAL_ENVIRONMENT_PATH/bin:$PATH"

# Install Poetry
RUN pip install "poetry==$POETRY_VERSION"

# Set the working directory in the container
WORKDIR /app

# Copy the dependency files
COPY pyproject.toml poetry.lock* requirements.txt* /app/

# Install project dependencies
RUN poetry env use $PYTHON_VERSION
RUN poetry install --no-interaction --no-ansi --no-root --without dev
COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "src.main:app"]