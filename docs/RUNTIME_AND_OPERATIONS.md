# Runtime And Operations

Canonical status: startup, verification, and operating guidance for the current repo.
Last reviewed against code: 2026-04-03.

## Primary Runtime

Primary runtime target:

- `app.main:app`

Use this for normal local and Docker operation.

## Local Start

```bash
./scripts/start_app.sh
```

What `./scripts/start_app.sh` does:

- creates or reuses `venv/`
- installs dependencies
- runs `alembic upgrade head`
- checks whether `APP_PORT` is occupied
- moves to the next free port if needed
- prints local and Tailscale URLs before starting Uvicorn

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

The repo is Tailscale-friendly in two concrete senses:

- the app binds to `0.0.0.0`
- `./scripts/start_app.sh` prints a Tailscale URL when the `tailscale` CLI is available

There is still no repo-specific ACL setup or service discovery beyond that.

## Environment Variables

- `DATABASE_URL`: database connection string, default SQLite file in repo root
- `APP_HOST`: host for `python -m app.main`
- `APP_PORT`: port for `python -m app.main`
- `UPLOAD_DIR`: upload root for stored document files
- `CORS_ALLOW_ORIGINS`: allowed origins
- `AUTO_CREATE_SCHEMA`: whether startup can still call `create_all()`
- `OPENAI_API_KEY`: enables live OpenAI-backed assistant and Data-In AI
- `OPENAI_MODEL`: shared fallback model
- `OPENAI_ANALYSIS_MODEL`: optional assistant-specific model
- `OPENAI_INGEST_MODEL`: optional ingest-specific model
- `OPENAI_BASE_URL`: optional compatible base URL override
- `OPENAI_TIMEOUT_SECONDS`: request timeout for OpenAI calls

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

Live AI smoke:

```bash
curl -X POST http://localhost:8000/households/1/assistant/respond \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Hur ser vår månatliga situation ut?"}'
```

## How To Tell the System Is Alive

Minimum signals:

- `/healthz` returns `{"status":"ok"}`
- `/` serves the SPA shell
- `/docs` loads Swagger UI
- household list route responds
- uploads create files under `uploaded_files/`
- assistant and ingest routes return `503` with an explicit provider message when `OPENAI_API_KEY` is missing
- assistant and ingest routes return real model output when `OPENAI_API_KEY` is set

## Restart

Local:

- stop the current process
- rerun `./scripts/start_app.sh`

Docker:

```bash
docker-compose restart
```

## Common Errors

### Missing OpenAI provider

Current AI failure mode:

- if `OPENAI_API_KEY` is missing, AI routes return `503`
- this is expected and preferable to fake local fallback output

### Upstream AI validation or provider failure

Current AI failure mode:

- if the OpenAI call or structured-output validation fails, AI routes return `502` with the provider error in `detail`

### Missing route assumptions from old docs

Current old docs in the repo previously claimed `POST /demo/seed`, but that route does not exist in `app.main`.

### Migration ambiguity

If the schema appears to exist locally without running Alembic, check whether `AUTO_CREATE_SCHEMA=true` masked the missing migration step.

### Upload path confusion

If document download fails, verify:

- the `Document.storage_path` points to a real file
- the upload directory exists
- the container or local process has write access

### Historical `502` in contract flow

One historical report said mobile live submit in the contract flow showed `502`.

Local truth as of 2026-04-03:

- browser submit on `/abonnemang` was reproduced locally
- the request returned `201 Created`
- no local `502` reproduction was found

Treat that report as unresolved in production-like environments until reproduced there, but not as a current locally reproduced bug.

## Non-Primary Runtime Artifacts

`app/static/server.py` exists, but it is not the documented main runtime.

It serves only:

- `/`
- `/assets`
- `/healthz`

It does not provide the full backend API or the SPA catch-all routing shape used by `app.main:app`.
