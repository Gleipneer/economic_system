# Runtime And Operations

Canonical status: startup, verification, and operating guidance for the current repo.
Last reviewed against code: 2026-04-03.

## Primary Runtime

Primary runtime target:

- `app.main:app`

Use this for normal local and Docker operation.

## Local Start

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Alternative module start:

```bash
python -m app.main
```

## Docker Start

```bash
docker-compose up -d --build
```

Container runtime command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Important URLs

- frontend: `http://localhost:8000/`
- Swagger/OpenAPI: `http://localhost:8000/docs`
- health check: `http://localhost:8000/healthz`
- validation markdown passthrough: `http://localhost:8000/system/validation_markdown`

## Tailscale

The repo is Tailscale-friendly only in the basic sense that the app binds to `0.0.0.0`.

There is no repo-specific Tailscale automation, ACL setup, or service discovery.

## Environment Variables

- `DATABASE_URL`: database connection string, default SQLite file in repo root
- `APP_HOST`: host for `python -m app.main`
- `APP_PORT`: port for `python -m app.main`
- `UPLOAD_DIR`: upload root for stored document files
- `CORS_ALLOW_ORIGINS`: allowed origins
- `AUTO_CREATE_SCHEMA`: whether startup can still call `create_all()`

## Database and Schema Operations

Apply migrations:

```bash
alembic upgrade head
```

Important nuance:

- Alembic is present and should be the migration path
- startup auto-bootstrap still exists and can mask migration discipline in local environments

## File Upload and Storage

Current document storage model:

- metadata in the database
- files on local disk under `uploaded_files/{household_id}/`
- checksum stored on upload
- absolute storage path persisted in the `Document` row

## Quick Verification Commands

Health:

```bash
curl http://localhost:8000/healthz
```

Households:

```bash
curl http://localhost:8000/households
```

Local smoke suite:

```bash
./venv/bin/pytest -q tests/test_smoke.py
```

## How To Tell the System Is Alive

Minimum signals:

- `/healthz` returns `{"status":"ok"}`
- `/` serves the SPA shell
- `/docs` loads Swagger UI
- household list route responds
- uploads create files under `uploaded_files/`

## Restart

Local:

- stop the current process
- rerun `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

Docker:

```bash
docker-compose restart
```

## Common Errors

### Smoke test failure on homepage branding

Current known failure:

- `tests/test_smoke.py` still expects `Hushållsekonomi`
- current frontend branding says `Ekonomi`

### Missing route assumptions from old docs

Current old docs in the repo previously claimed `POST /demo/seed`, but that route does not exist in `app.main`.

### Migration ambiguity

If the schema appears to exist locally without running Alembic, check whether `AUTO_CREATE_SCHEMA=true` masked the missing migration step.

### Upload path confusion

If document download fails, verify:

- the `Document.storage_path` points to a real file
- the upload directory exists
- the container or local process has write access

## Non-Primary Runtime Artifacts

`app/static/server.py` exists, but it is not the documented main runtime.

It serves only:

- `/`
- `/assets`
- `/healthz`

It does not provide the full backend API or the SPA catch-all routing shape used by `app.main:app`.
