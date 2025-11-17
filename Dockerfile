FROM python:3.12-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Disable virtualenv creation
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_CACHE_DIR=/tmp/poetry_cache

# Configure Poetry
RUN poetry config virtualenvs.in-project false

# Copy full project first so Poetry sees everything (especially README.md)
COPY . /app

# Install all dependencies including the project itself
RUN poetry install --no-interaction --no-ansi --no-root

# Optionally remove cache
# RUN rm -rf $POETRY_CACHE_DIR

# Specify the entry point for your container
CMD ["python", "main.py"]