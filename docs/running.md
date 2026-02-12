# Running

This project is typically run as a 3-container stack:
- API (Flask)
- Worker (Celery)
- Redis

## Docker (recommended)

### Prerequisites
- Docker + Docker Compose
- NVIDIA GPU runtime if you want GPU acceleration (the image is based on `nvidia/cuda`)

### Steps

1) Create a `.env` file:

```bash
cp .env.example .env
```

2) Start the stack:

```bash
docker compose up --build
```

3) Stop:

```bash
docker compose down
```

## Local (without Docker)

### Prerequisites
- Python 3
- System packages like `ffmpeg`
- A Redis instance reachable at `REDIS_HOST:REDIS_PORT`

### Steps

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env

python -m run
```

In another terminal (same venv):

```bash
celery -A run.celery worker --loglevel=info --concurrency=1
```

## Production notes

The current `run.py` starts Flask with `debug=True`. For production, switch to a WSGI server (gunicorn) and disable debug.

Example (to be wired via compose profile or deployment manifests):

```bash
gunicorn -w 1 -b 0.0.0.0:${APP_PORT} 'app:create_app()'
```

(Exact gunicorn entrypoint may need a small tweak because `create_app()` returns `(app, celery)`.)
