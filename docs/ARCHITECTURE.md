# Architecture

Canonical status: actual technical architecture as implemented today.
Last reviewed against code: 2026-04-03.

## System Overview

The repository is one monolithic FastAPI application with a built-in frontend.

Major runtime layers:

1. settings and environment loading
2. SQLAlchemy data model and sessions
3. FastAPI routes
4. deterministic calculation helpers
5. AI service layer for OpenAI-backed analysis and ingest
6. static SPA assets
7. Alembic migrations

## Core Application Structure

### Backend Core

- `app/main.py`: primary FastAPI app, route definitions, startup, file upload logic, and AI route wiring
- `app/models.py`: SQLAlchemy ORM model definitions
- `app/schemas.py`: Pydantic request/response schemas
- `app/calculations.py`: deterministic summary, housing, scenario, and helper math
- `app/ai_services.py`: OpenAI call wrapper, compact context building, ingest validation, and draft-promotion helpers
- `app/database.py`: engine, session factory, `Base`, optional schema bootstrap
- `app/settings.py`: environment-backed settings

### Frontend Core

- `app/static/index.html`: shell, sidebar, top bar, page mount points
- `app/static/app.js`: SPA state, routing, rendering, form submission, API calls
- `app/static/styles.css`: visual language and responsive layout

### Operations and Schema

- `alembic/`: migration environment and baseline schema revision
- `Dockerfile`: container runtime path
- `docker-compose.yml`: local container orchestration
- `scripts/start_app.sh`: preferred local start path with migration step and port fallback
- `tests/test_smoke.py`: backend smoke coverage

## Data Model Shape

The current data model groups into these layers:

### Household Core

- household
- person

### Income, Liability, Cost, and Asset Records

- income source
- loan
- recurring cost
- subscription contract
- insurance policy
- vehicle
- asset

### Planning and Evaluation Records

- housing scenario
- scenario
- scenario result
- report snapshot

### Document and AI-Adjacent Workflow Records

- document
- extraction draft
- optimization opportunity

## Runtime Flows

### App Startup

1. settings are loaded from environment
2. upload root is created if missing
3. `database.init_db()` runs
4. if `AUTO_CREATE_SCHEMA=true`, `create_all()` may create missing tables

### Frontend Request Flow

1. browser requests `/`
2. FastAPI returns `app/static/index.html`
3. SPA loads `app.js` and `styles.css`
4. SPA fetches JSON from same-origin API routes
5. unknown non-asset frontend GET paths fall back to the SPA shell

### Document Flow

1. frontend or client sends `POST /documents/upload`
2. backend writes the uploaded file under `uploaded_files/{household_id}/...`
3. backend stores a `Document` row with checksum and storage path
4. `GET /documents/{id}/download` serves the file back from disk

### Data-In AI Flow

1. client sends raw text to `POST /households/{id}/ingest_ai/analyze`
2. backend passes only relevant household scope and raw text to `app/ai_services.py`
3. OpenAI returns structured output through the Responses API
4. backend validates each suggestion against typed create schemas
5. client can explicitly call `POST /households/{id}/ingest_ai/promote`
6. backend stores one `Document` plus one or more `ExtractionDraft` rows
7. canonical finance tables remain untouched until a later explicit `extraction_drafts/{id}/apply`

### Household Summary Flow

1. backend loads household-scoped records
2. amounts are normalized to monthly and yearly forms
3. deterministic totals are computed
4. summary JSON is returned

### Optimization Flow

1. backend scans subscriptions and recurring costs
2. heuristics create or reuse `OptimizationOpportunity` rows
3. frontend surfaces those as improvement suggestions

### Scenario Flow

1. a `Scenario` stores JSON adjustments
2. scenario execution loads current household records
3. adjustments are applied in memory
4. baseline and projected summaries are computed
5. a `ScenarioResult` row is stored

### Report Flow

1. backend computes current household summary
2. summary is stored as `result_json` in `ReportSnapshot`
3. frontend can list, open, and delete saved snapshots

### Assistant Flow

1. client sends a prompt to `POST /households/{id}/assistant/respond`
2. backend builds a compact read model from household records and summary
3. `app/ai_services.py` calls the OpenAI Responses API
4. response is returned as answer text plus provider/model/usage metadata

## Current Architectural Truth

The current system is best understood as a planning layer over structured household facts.

It is not:

- a transaction ledger
- a bank sync engine
- an event-sourced finance kernel
- an AI orchestration platform

## Planning Layer vs Possible Future Finance Core

There is no implemented `finance_core`, transaction kernel, or bank-ingest subsystem in this repo today.

If such a layer is introduced later, the clean architectural fit would be:

- a lower layer for normalized transactions, balances, adapters, and reconciliation
- the current household planning entities above or beside it as a planning/application layer

That is only a possible future fit. It is not a current repo commitment.

## Architectural Debt

- `app/main.py` is large and owns almost all route logic
- `app/static/app.js` contains both older and newer UI strata in one file
- `app/ai_services.py` is directly coupled to OpenAI rather than a provider abstraction
- the active frontend now exposes recurring costs, but the file still contains duplicated legacy and active handlers
- `app/static/server.py` and `app/system_docs.py` exist as side artifacts, not as the primary architecture
