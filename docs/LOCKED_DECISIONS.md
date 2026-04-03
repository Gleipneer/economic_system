# Locked Decisions

Canonical status: these decisions should be treated as fixed until explicitly changed.
Last reviewed: 2026-04-03.

## Scope of This File

This file captures decisions that the current repo shape depends on. They are not permanent laws, but they should not drift silently.

## Product and UX Decisions

- The product is a Swedish household economics app, not a back-office admin tool.
- The frontend should organize work around household tasks, not around database internals.
- One active household is selected globally in the UI and reused across flows.
- Users should not have to type raw `household_id` values in normal frontend flows.
- Reports are snapshot objects, not merely live views.
- The assistant belongs inside the household workflow, not as a detached developer console.

## Architecture Decisions

- The primary deployment shape is one FastAPI app serving both API and frontend.
- Deterministic financial calculations belong on the backend.
- The current domain model is planning-oriented and snapshot-oriented, not transaction-ledger-oriented.
- SQLite-first and filesystem-first are acceptable current defaults.
- Alembic is the supported schema migration path, even though auto-bootstrap still exists for local convenience.

## AI and Data-Safety Decisions

- Canonical household data must not be silently overwritten by AI behavior.
- Any future AI write path must remain explicit and reviewable.
- The current assistant must remain read-only relative to canonical finance tables.
- Future AI extraction should continue to land in workflow objects such as drafts or opportunities before promotion.
- Deterministic calculations remain the source of truth for money math even if AI is added later.

## Integration Decisions

- Uploaded documents are stored locally unless storage strategy is explicitly changed.
- Same-origin frontend + backend is the current integration model.
- Household summary, housing evaluation, scenario execution, report generation, and assistant response are backend-owned contracts.

## Explicit "Do Not Let This Drift"

- Do not claim `POST /demo/seed` exists unless it is implemented again.
- Do not describe the current assistant as external-model-backed AI.
- Do not describe the current system as transaction ingest or finance core.
- Do not reframe the current frontend as a generic CRUD dashboard.
- Do not reimplement core summary or housing calculations in the frontend.

## Explicit "Do Not Do"

- Do not introduce silent AI writes into canonical tables.
- Do not add documentation that treats future AI gateway, bank ingest, or finance core as present-day facts.
- Do not remove the Swedish household framing from the frontend without an explicit product decision.
