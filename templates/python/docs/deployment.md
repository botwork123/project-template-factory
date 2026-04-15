# Deployment Guide

## Shared runtime contract

This project uses `src/__PROJECT_NAME__/settings.py` as the single settings contract for:
- local execution
- Docker container runtime
- Prefect deployments

Regenerate `.env.example` from schema:

```bash
python scripts/generate_env_example.py
```

## Local run

```bash
python -m __PROJECT_NAME__.main
```

## Docker run

```bash
docker build -t __PROJECT_NAME__:local .
docker run --rm --env-file .env.example __PROJECT_NAME__:local
```

## Prefect image-based deploy (optional)

Prefect is optional for local dev. If you use Prefect:

```bash
IMAGE_TAG=dev ./scripts/prefect/deploy.sh dev app
```

Set `IMAGE_NAME`, `PREFECT_WORK_POOL`, and `PREFECT_WORK_QUEUE` as needed.
