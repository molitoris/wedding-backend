FROM python:3.10-slim

ARG PUID=1000
ARG GUID=1000

RUN pip install poetry==1.6.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Create a group with GUID
RUN groupadd -g $GUID api

# Create a user with PUID
RUN useradd -u $PUID -g api -ms /bin/bash api

# Create necessary directories
RUN mkdir -p /input/guest_list && chown -R api:api /input \
    && mkdir -p /data/qr_codes && chown -R api:api /data \
    && mkdir -p /config && chown -R api:api /config \
    && mkdir -p /workspaces/wedding-api && chown -R api:api /workspaces

# Change to user
USER api

WORKDIR /workspaces/wedding-api/

COPY ./pyproject.toml ./poetry.lock ./
RUN poetry install --without dev --no-root \
    && rm -rf $POETRY_CACHE_DIR

COPY ./app ./app

RUN poetry install --without dev

CMD ["poetry", "run", "uvicorn", "app.src.main:app_v1", "--host", "0.0.0.0", "--port", "8000"]
