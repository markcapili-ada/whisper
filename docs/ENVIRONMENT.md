# Environment variables

This service is configured primarily via environment variables loaded from a `.env` file.

## Setup

```bash
cp .env.example .env
# then edit .env
```

Docker Compose uses:

- `env_file: .env`
- `ports: "${APP_PORT}:${APP_PORT}"`
- Redis port: `"${REDIS_PORT}:${REDIS_PORT}"`

## Common variables

The canonical list is in `.env.example`. Some key variables used by entrypoints/compose:

### Runtime
- `APP_ENV`: used in container naming (`${APP_ENV}-whisper-api`, `${APP_ENV}-celery-worker`, `${APP_ENV}-redis`).
- `APP_PORT`: Flask binds to this port (`run.py`) and compose publishes it.

### Redis / Celery
- `REDIS_PORT`: port exposed by the `redis` service in compose.

Celery worker is started as:

```bash
celery -A run.celery worker --loglevel=info --concurrency=1
```

### Whisper model
- `WHISPER_MODEL`: in `docker-compose.yml` it is set to `large` by default under the API service.

## Notes
- Do not commit `.env` (keep secrets out of git).
- If you run without Docker, you must ensure Redis is reachable and that your `.env` points to it.
