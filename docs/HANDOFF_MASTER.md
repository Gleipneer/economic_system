# Handoff Master

Canonical status: read this first.
Last reviewed against code: 2026-04-03.

## Project in Short

This repo is a Swedish household economics system built as one FastAPI app with a built-in same-origin SPA frontend.

It already has:

- structured household finance CRUD
- deterministic summaries and housing calculations
- first-class recurring-cost UX in the active SPA
- scenario execution
- report snapshots
- document upload/download
- extraction drafts and optimization opportunities
- a real assistant endpoint
- a real Data-In AI flow for raw text -> validated suggestions -> explicit draft promotion

It is still a planning/snapshot system, not a bank-ingest or finance-core system.

## What Is Locked

- The product is a Swedish household app, not a generic admin panel.
- The main runtime is `app.main:app`.
- Core finance calculations stay backend-owned.
- AI-like behavior must remain explicit and non-silent relative to canonical data.
- Analysis AI and Data-In AI are separate surfaces.
- Do not claim missing features such as `POST /demo/seed`, bank ingest, or finance core.

## What Exists

- same-origin SPA with routed household pages
- backend CRUD for current domain entities
- summary, optimization, housing evaluation, scenario, report, document, draft, and assistant flows
- OpenAI-backed analysis AI when provider env is configured
- OpenAI-backed Data-In AI plus explicit promote-to-draft flow when provider env is configured
- Alembic baseline migration
- Docker and local runtime paths
- `scripts/start_app.sh` with migration step, port fallback, and Tailscale URL output

## What Is Missing

- auth
- bank adapters and transaction ingest
- background jobs
- observability beyond a basic health check
- provider abstraction beyond the direct OpenAI integration
- LF-style bank copy-paste ingest that produces genuinely useful review drafts

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

Harden LF-style bank copy-paste ingest so raw pasted account data can become conservative, reviewable workflow drafts without pretending the app already has a transaction ledger.

See:

- `docs/NEXT_ACTION.md`
- `docs/AINEXTSTEPPATCH.md`

## Final Truth Rule

If any older doc conflicts with these canonical docs or with code, trust:

1. current code
2. this canonical docs set
3. older compatibility docs last
