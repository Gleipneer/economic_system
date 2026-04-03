# Current State

Canonical status: strict description of what exists in the code now.
Last reviewed against code: 2026-04-03.

## Runtime Shape

The primary runtime entrypoint is:

- `app.main:app`

Supported launch paths in the repo:

- `./scripts/start_app.sh`
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
- `POST /households/{id}/ingest_ai/analyze`
- `POST /households/{id}/ingest_ai/promote`
- `POST /documents/upload`
- `GET /documents/{id}/download`

### What Those Flows Actually Do

- `summary` builds a deterministic household summary from stored records
- `report_snapshots/generate` stores the current summary as JSON in a snapshot row
- `optimization_scan` generates heuristic savings suggestions from subscriptions and recurring costs
- `housing_scenarios/{id}/evaluate` computes housing cost fields from one housing scenario row
- `scenarios/{id}/run` applies JSON adjustments in memory and stores a scenario result
- `extraction_drafts/{id}/apply` creates a canonical entity from `proposed_json` and marks the draft as approved
- `assistant/respond` builds a compact household read model and calls OpenAI Responses API when provider config exists
- `ingest_ai/analyze` classifies raw text, returns validated structured suggestions, and does not write canonical data
- `ingest_ai/promote` stores the raw input as a `Document` row plus `ExtractionDraft` rows only after explicit user action

## What Exists in the Frontend

The active frontend is a vanilla-JS SPA served from FastAPI at `/`.

Active routed pages in the current SPA:

- `overview`
- `register`
- `household`
- `persons`
- `incomes`
- `loans`
- `costs`
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
- recurring costs are a first-class routed page at `/kostnader`
- documents page now includes Data-In AI with explicit promote-to-draft behavior

## What Is Actually Connected End-to-End

These flows are genuinely wired from UI to backend:

- overview -> `/households/{id}/summary`
- recurring costs CRUD -> `/recurring_costs`
- improvements scan -> `/households/{id}/optimization_scan`
- housing evaluation -> `/housing_scenarios/{id}/evaluate`
- report generation -> `/households/{id}/report_snapshots/generate`
- document upload -> `/documents/upload`
- document download -> `/documents/{id}/download`
- Data-In AI analyze -> `/households/{id}/ingest_ai/analyze`
- Data-In AI promote -> `/households/{id}/ingest_ai/promote`
- extraction draft apply/delete -> `/extraction_drafts/...`
- scenario run -> `/scenarios/{id}/run`
- assistant chat -> `/households/{id}/assistant/respond`
- subscription form submit -> `/subscription_contracts`

## Database and Storage

Current storage model:

- relational database via SQLAlchemy
- SQLite by default through `DATABASE_URL=sqlite:///./database.db`
- Alembic baseline migration exists
- local filesystem storage for uploaded documents under `UPLOAD_DIR`, default `./uploaded_files`
- direct OpenAI integration through `app/ai_services.py` when `OPENAI_API_KEY` is set

Important nuance:

- Alembic exists, but `AUTO_CREATE_SCHEMA` still defaults to `true`
- startup still calls `create_all()` when auto-bootstrap is enabled

## What Is Verified

Verified directly in code:

- the routes listed above exist
- Alembic config exists and points at the same `DATABASE_URL`
- document upload writes files to disk and stores metadata
- summary, scenario, housing, report, optimization, recurring-cost, ingest, and assistant flows are implemented in code

Verified in local runtime on 2026-04-03:

- `alembic upgrade head`
- `/`, `/docs`, and `/healthz`
- `./venv/bin/python -m pytest -q tests/test_smoke.py` -> `6 passed`
- recurring-cost create/edit/delete in the browser
- document upload and download in the browser
- Data-In AI analyze and promote in the browser
- assistant analysis in the browser with live OpenAI responses
- subscription form submit in the browser; the previously reported `502` in that flow was not reproduced locally
- `./scripts/start_app.sh` port fallback from `8000` to `8001`
- Tailscale URL output from `./scripts/start_app.sh`

Live OpenAI verification on 2026-04-03 used:

- `gpt-5.4-mini-2026-03-17` for analysis questions
- `gpt-5.4-mini-2026-03-17` for ingest test cases

## What Does Not Exist

These are not implemented in the current code:

- authentication
- authorization
- bank adapters
- transaction ingest
- finance core
- AI gateway
- background jobs
- metrics or readiness/liveness probes
- object storage
- `POST /demo/seed`
- provider abstraction beyond direct OpenAI calls

## Important Truths That Can Be Missed

- the assistant is backed by OpenAI only when provider env is configured; otherwise the route returns `503`
- the optimization scan is not AI; it is heuristic server logic
- Data-In AI analyze does not write canonical data
- Data-In AI promote writes `Document` and `ExtractionDraft` rows, not canonical household records
- the `conversation` field still exists on the assistant request schema, but the active frontend sends only `prompt`
- recurring costs now exist in both backend math and the active routed product surface
