# whisper-api

HTTP API + Celery worker for audio transcription using OpenAI Whisper (plus optional diarization / LLM post-processing depending on configuration).

## Quickstart (Docker Compose)

### 1) Configure environment

```bash
cp .env.example .env
# edit .env as needed (ports, secrets, etc.)
```

### 2) Start services

```bash
docker compose up --build
```

This starts:
- `whisper-api` (Flask dev server)
- `celery-worker`
- `redis`

API will be exposed on `${APP_PORT}`.

### 3) Stop

```bash
docker compose down
```

## Local development (no Docker)

### Prereqs
- Python 3.x
- Redis (running locally or reachable remotely)

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env
```

### Run the API

`run.py` loads `.env` and runs the Flask app.

```bash
python -m run
```

### Run the worker

```bash
celery -A run.celery worker --loglevel=info --concurrency=1
```

## Configuration

- Environment variables are loaded from `.env` (see `.env.example`).
- Docker Compose also injects `WHISPER_MODEL=large` by default (see `docker-compose.yml`).

More details: see [`docs/ENVIRONMENT.md`](docs/ENVIRONMENT.md).

## Notes on production

The current compose setup runs the Flask development server. For production deployments you’ll typically want a production WSGI server (e.g., gunicorn) and to review:
- concurrency settings for Celery
- volume/cache strategy (`../whisper-cache:/root/.cache`)
- secrets management (do not commit `.env`)

## Repository layout (current)

- `app/api`: HTTP resources/actions/requests
- `app/services`: service layer / business logic
- `app/tasks`: Celery tasks
- `app/extensions`: Flask/Celery/JWT/Socket.IO extensions
- `app/config`: configuration objects

A larger Clean Architecture re-organization is tracked in #1 and is best done incrementally after agreeing on a target `docs/ARCHITECTURE.md`.
