# System Validation

This file is a compatibility-facing validation note for the current runtime.

Canonical operational truth lives in:

- `docs/CURRENT_STATE.md`
- `docs/RUNTIME_AND_OPERATIONS.md`

## Current Delivered Runtime

The repo currently contains one FastAPI app that serves:

- a same-origin SPA on `/`
- OpenAPI docs on `/docs`
- health check on `/healthz`
- CRUD routes for the current domain entities
- deterministic summary, housing, scenario, report, document, draft, and optimization flows
- OpenAI-backed assistant and Data-In flows when `OPENAI_API_KEY` is configured

## Manual Validation Checklist

### Core Runtime

1. Open `/`.
2. Open `/docs`.
3. Open `/healthz` and verify `{"status":"ok"}`.

### Household Data

1. Create a household through the UI or `POST /households`.
2. Add at least one person.
3. Add incomes, loans, subscriptions, or other data.
4. Verify `GET /households/{id}/summary` returns values.

### Documents

1. Upload a file with `POST /documents/upload`.
2. Verify a `Document` row exists.
3. Download it again through `GET /documents/{id}/download`.

### Scenarios and Reports

1. Create a `Scenario`.
2. Run it with `POST /scenarios/{id}/run`.
3. Create a `HousingScenario`.
4. Evaluate it with `GET /housing_scenarios/{id}/evaluate`.
5. Generate a report snapshot with `POST /households/{id}/report_snapshots/generate`.

### Draft and Assistant Flows

1. Create an `ExtractionDraft`.
2. Apply it with `POST /extraction_drafts/{id}/apply`.
3. Ask the assistant via `POST /households/{id}/assistant/respond`.
4. Analyse raw text via `POST /households/{id}/ingest_ai/analyze`.
5. Promote reviewed suggestions via `POST /households/{id}/ingest_ai/promote`.

## Automated Coverage Present in Repo

The smoke suite currently covers:

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
- AI routes fail cleanly with `503` when provider config is missing

## Current Known Validation Mismatch

As of 2026-04-03 there is no known local smoke mismatch left in `tests/test_smoke.py`.

## Explicit Non-Features

Do not validate for these as if they were delivered:

- `POST /demo/seed`
- auth
- bank ingest
- background workers
