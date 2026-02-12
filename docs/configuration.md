# Configuration

Configuration is provided primarily through environment variables.

## `.env` file
Create your local `.env` by copying the template:

```bash
cp .env.example .env
```

## Variables (from `.env.example`)

### App
- `APP_URL`: public URL of the API (if applicable)
- `APP_ENV`: environment name (e.g. `dev`, `prod`) — also used in compose container names
- `APP_PORT`: port Flask binds to and compose exposes

### Whisper
- `WHISPER_SIZE`: model size selector (repo also sets `WHISPER_MODEL=large` in compose)

### Security
- `SECRET_KEY`: Flask secret key
- `ADMIN_USER`, `ADMIN_PASSWORD`: admin credentials (if used by the API)
- `APP_BASIC_AUTH_USERNAME`, `APP_BASIC_AUTH_PASSWORD`: HTTP basic auth (if enabled)
- `WEBHOOK_SECRET_KEY`: shared secret for webhook verification (if enabled)

### Google
- `GOOGLE_CREDENTIAL`: path or encoded credentials (implementation-defined)

### Database (if enabled)
- `DB_USER`, `DB_PASSWORD`, `DB_PORT`, `DB_NAME`, `DB_HOST`

### Autocollect backend (if used)
- `AUTOCOLLECT_URL`, `AUTOCOLLECT_USERNAME`, `AUTOCOLLECT_PASSWORD`

### Redis / Celery
- `REDIS_URL`: full redis URL (alternative to host/port)
- `REDIS_HOST`: redis host (compose service name is `redis`)
- `REDIS_PORT`: redis port

### Audio file server (if used)
- `AUDIO_FILE_SERVER_URL`, `AUDIO_FILE_SERVER_USERNAME`, `AUDIO_FILE_SERVER_PASSWORD`

### Conda
- `CONDA_DEFAULT_ENV`: conda env name (optional)

### LLM
- `LLM_MODEL`: model identifier
- `LLM_API_URL`: base URL
- `LLM_API_KEY`: auth key
- `LLM_CLIENT`: client selector

## Notes
- In `docker-compose.yml`, the API service sets `WHISPER_MODEL=large` directly, and also loads `.env`. If both are set, the behavior depends on how the app reads config.
- If any variables are unused, we can prune the template after verifying `app/config*.py` usage.
