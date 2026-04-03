# Handoff Master

Canonical status: read this first.
Last reviewed against code: 2026-04-03.

## Project in Short

This repo is a Swedish household economics system built as one FastAPI app with a built-in same-origin SPA frontend.

It already has:

- structured household finance CRUD
- deterministic summaries and housing calculations
- scenario execution
- report snapshots
- document upload/download
- extraction drafts and optimization opportunities
- a real assistant endpoint

It is still a planning/snapshot system, not a bank-ingest or finance-core system.

## What Is Locked

- The product is a Swedish household app, not a generic admin panel.
- The main runtime is `app.main:app`.
- Core finance calculations stay backend-owned.
- AI-like behavior must remain explicit and non-silent relative to canonical data.
- Do not claim missing features such as `POST /demo/seed`, bank ingest, or external AI integration.

## What Exists

- same-origin SPA with routed household pages
- backend CRUD for current domain entities
- summary, optimization, housing evaluation, scenario, report, document, draft, and assistant flows
- Alembic baseline migration
- Docker and local runtime paths

## What Is Missing

- auth
- external AI provider integration
- bank adapters and transaction ingest
- background jobs
- observability beyond a basic health check
- first-class active frontend support for recurring costs

## Exact Read Order

1. `docs/HANDOFF_MASTER.md`
2. `docs/CURRENT_STATE.md`
3. `docs/LOCKED_DECISIONS.md`
4. `docs/ARCHITECTURE.md`
5. `docs/NEXT_ACTION.md`
6. `docs/FRONTEND_DIRECTION.md`
7. `docs/AI_DIRECTION.md`
8. `docs/RUNTIME_AND_OPERATIONS.md`
9. `docs/KNOWN_GAPS_AND_RISKS.md`
10. `docs/REPO_MAP.md`
11. `docs/TERMS_AND_MODEL.md`
12. `docs/PROJECT_CONTEXT.md`

## Next Recommended Task

Make recurring costs reachable and fully operable in the active frontend without destabilizing the current routed shell.

See:

- `docs/NEXT_ACTION.md`

## Final Truth Rule

If any older doc conflicts with these canonical docs or with code, trust:

1. current code
2. this canonical docs set
3. older compatibility docs last
