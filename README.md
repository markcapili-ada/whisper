# whisper-api

Flask + Celery API wrapper around Whisper/WhisperX, intended to run via Docker Compose (API + worker + Redis).

## Quick start (Docker)

### 1) Create a `.env`
Copy the example and fill in required values:

```bash
cp .env.example .env
```

At minimum you’ll need:
- `APP_ENV` (e.g. `dev`)
- `APP_PORT` (e.g. `5000`)
- `REDIS_HOST` + `REDIS_PORT` (for the worker)
- `SECRET_KEY` (Flask)

See **[docs/configuration.md](docs/configuration.md)** for the full list.

### 2) Build + run

```bash
docker compose up --build
```

This starts:
- `whisper-api` (runs `python -m run`)
- `celery-worker` (runs `celery -A run.celery worker ...`)
- `redis`

The API binds to `0.0.0.0:${APP_PORT}`.

## Development vs Production

### Development
- Current entrypoint is Flask dev server (`run.py` uses `debug=True`).
- Recommended workflow is Docker Compose with the source mounted into the container (already configured in `docker-compose.yml`).

### Production (recommended follow-up)
For production deployments, it’s recommended to:
- run the HTTP app under **gunicorn** (already in `requirements.txt`)
- disable Flask debug
- remove the bind-mount volume and rely on an image build

A follow-up change can add compose profiles (dev/prod) so production uses gunicorn while dev stays on the debug server.

## Docs
- Running instructions: **[docs/running.md](docs/running.md)**
- Environment/configuration: **[docs/configuration.md](docs/configuration.md)**

## Clean Architecture note
The current structure already has clear separation (API resources / services / tasks). A larger “Clean Architecture” refactor is best done incrementally to avoid breaking the `run.py` and compose entrypoints.

A suggested target layering:
- `app/domain/` – entities/value objects (framework-free)
- `app/use_cases/` – application workflows
- `app/adapters/` – integrations (Whisper/LLM/Webhooks/DB/Redis)
- `app/framework/` – Flask/Celery wiring
