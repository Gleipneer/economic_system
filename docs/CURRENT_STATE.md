# Current State

Canonical status: strict description of what exists in the code now.
Last reviewed against code: 2026-04-03.

## Runtime Shape

The primary runtime entrypoint is:

- `app.main:app`

Supported launch paths in the repo:

- `uvicorn app.main:app --reload`
- `python -m app.main`
- Docker `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]`

There is also a separate `app/static/server.py`, but it is not the documented or containerized runtime path.

## What Exists in the Backend

### Core CRUD

The backend exposes CRUD routes for these persisted entities:

- household
- person
- income source
- loan
- recurring cost
- subscription contract
- insurance policy
- vehicle
- asset
- housing scenario
- document
- extraction draft
- optimization opportunity
- scenario
- scenario result
- report snapshot

### Real Workflow Endpoints

These non-CRUD flows are implemented:

- `GET /healthz`
- `GET /households/{id}/summary`
- `POST /households/{id}/report_snapshots/generate`
- `POST /households/{id}/optimization_scan`
- `GET /housing_scenarios/{id}/evaluate`
- `POST /scenarios/{id}/run`
- `POST /extraction_drafts/{id}/apply`
- `POST /households/{id}/assistant/respond`
- `POST /documents/upload`
- `GET /documents/{id}/download`

### What Those Flows Actually Do

- `summary` builds a deterministic household summary from stored records
- `report_snapshots/generate` stores the current summary as JSON in a snapshot row
- `optimization_scan` generates heuristic savings suggestions from subscriptions and recurring costs
- `housing_scenarios/{id}/evaluate` computes housing cost fields from one housing scenario row
- `scenarios/{id}/run` applies JSON adjustments in memory and stores a scenario result
- `extraction_drafts/{id}/apply` creates a canonical entity from `proposed_json` and marks the draft as approved
- `assistant/respond` returns a templated Swedish answer based on current household data and keyword routing

## What Exists in the Frontend

The active frontend is a vanilla-JS SPA served from FastAPI at `/`.

Active routed pages in the current SPA:

- `overview`
- `register`
- `household`
- `persons`
- `incomes`
- `loans`
- `subscriptions`
- `insurance`
- `vehicles`
- `assets`
- `housing`
- `documents`
- `improvements`
- `scenarios`
- `reports`
- `assistant`

Shared frontend behaviors:

- one global active-household selector in the top bar
- route-based navigation with browser history support
- same-origin API calls
- Swedish UI copy throughout
- report, draft, scenario, and assistant views are real

## What Is Actually Connected End-to-End

These flows are genuinely wired from UI to backend:

- overview -> `/households/{id}/summary`
- improvements scan -> `/households/{id}/optimization_scan`
- housing evaluation -> `/housing_scenarios/{id}/evaluate`
- report generation -> `/households/{id}/report_snapshots/generate`
- document upload -> `/documents/upload`
- document download -> `/documents/{id}/download`
- extraction draft apply/delete -> `/extraction_drafts/...`
- scenario run -> `/scenarios/{id}/run`
- assistant chat -> `/households/{id}/assistant/respond`

## Database and Storage

Current storage model:

- relational database via SQLAlchemy
- SQLite by default through `DATABASE_URL=sqlite:///./database.db`
- Alembic baseline migration exists
- local filesystem storage for uploaded documents under `UPLOAD_DIR`, default `./uploaded_files`

Important nuance:

- Alembic exists, but `AUTO_CREATE_SCHEMA` still defaults to `true`
- startup still calls `create_all()` when auto-bootstrap is enabled

## What Is Verified

Verified directly in code:

- the routes listed above exist
- Alembic config exists and points at the same `DATABASE_URL`
- document upload writes files to disk and stores metadata
- summary, scenario, housing, report, optimization, and assistant flows are implemented in code

Verified by the local smoke test suite structure:

- home route
- health check
- Alembic upgrade
- household CRUD partial update
- document upload/download
- household summary
- housing scenario evaluation
- scenario run
- report generation
- optimization scan
- calculation helpers

Current local verification note:

- the smoke suite currently fails one assertion because the test expects `Hushållsekonomi` while the current frontend branding says `Ekonomi`

## What Does Not Exist

These are not implemented in the current code:

- authentication
- authorization
- bank adapters
- transaction ingest
- finance core
- external AI provider integration
- AI gateway
- background jobs
- metrics or readiness/liveness probes
- object storage
- `POST /demo/seed`

## Important Truths That Can Be Missed

- the assistant is not backed by an external model today
- the optimization scan is not AI; it is heuristic server logic
- document upload exists, but automatic extraction does not
- extraction draft application is explicit, but there is no separate approve/reject endpoint
- recurring costs exist in the backend and summary math, but the active frontend does not currently expose them as a first-class reachable screen
