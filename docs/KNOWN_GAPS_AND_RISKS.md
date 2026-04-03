# Known Gaps And Risks

Canonical status: explicit risk and gap register for the current repo.
Last reviewed: 2026-04-03.

## Technical Gaps

- No authentication or authorization exists.
- No bank adapters or transaction ingest exist.
- No background jobs exist.
- No metrics, readiness probe, or liveness probe exist beyond `/healthz`.
- No object storage abstraction exists; document storage is local filesystem only.
- The primary FastAPI app is still monolithic in `app/main.py`.
- The primary frontend file `app/static/app.js` contains both older and newer UI strata in one file.
- `AUTO_CREATE_SCHEMA=true` remains the default even though Alembic now exists.

## Product Gaps

- The active frontend does not currently expose recurring costs as a first-class reachable module, even though the backend and summary logic support them.
- There is no demo-seed route, despite older docs historically implying one.
- There is no dedicated approve/reject workflow for extraction drafts before apply.
- The assistant does not maintain meaningful conversation state.
- There is no user account model or privacy boundary beyond deployment trust.

## Integration Risks

- Local file paths are persisted in document metadata.
- Docker Compose bind-mounts the whole repo into `/app`, so runtime state lives in the repo working tree.
- There is no stable versioned API export or compatibility policy for frontend consumers.
- There is no provider abstraction implemented yet for future external AI integration.

## Architectural Debt

- The repo still carries stale or compatibility-layer docs and artifacts from earlier shapes.
- `app/static/server.py` is a side runtime artifact that can confuse future readers.
- `app/system_docs.py` is not the primary runtime source of validation truth.
- Report snapshots currently store summary-style JSON, not a richer reporting document system.
- Scenario execution uses JSON adjustments against loaded records, not a lower-level financial model.

## Validation Risk

Current local validation is not fully green:

- the smoke suite currently fails one assertion tied to old frontend branding text

This is not a backend failure, but it is a real repo inconsistency and should not be ignored.

## Things That Must Not Be Misread As Complete

- The assistant is not an external-model AI assistant.
- Optimization suggestions are not market-integrated recommendations.
- Document upload is not document extraction.
- Draft apply is not a full approval workflow.
- Alembic existence does not mean operational migration discipline is finished.
- Same-origin frontend existence does not mean the frontend is feature-complete.

## Where Extra Caution Is Required

- When changing schema behavior, because startup auto-bootstrap can hide migration mistakes
- When changing frontend routing, because the SPA relies on FastAPI catch-all behavior
- When touching document storage, because files are currently local and path-based
- When touching assistant behavior, because old docs already overstated AI-related scope once
