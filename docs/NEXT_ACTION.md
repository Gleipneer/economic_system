# Next Action

Canonical status: single recommended next task for the next agent pass.
Last reviewed: 2026-04-04 (post-sanitization and verified main parity).

## Next Task

Stabilize intelligence layer V1 quality by adding provenance and stricter duplicate matching against canonical tables.

## Why This Comes Next

The branch/main sanitization pass is now complete (merge done, migration added, tests and runtime checks green), so the highest-value remaining risk is data traceability and duplicate precision in intelligence outputs:

- duplicate indicator currently checks drafts and should also compare canonical subscriptions/costs
- review suggestions need explicit provenance links (document -> draft -> applied entity)
- ownership and why-engine are already useful, but evidence chain is still implicit

This keeps momentum on correctness without opening any new major feature track.

## What Must Stay Stable

- Keep `app.main:app` as the runtime entrypoint.
- Keep the current Swedish route-based frontend shell.
- Keep the global active-household selector.
- Keep the current recurring-cost, documents, and assistant flows working as they do now.
- Keep backend-owned money math out of the model output.
- Keep AI writes limited to workflow artifacts unless the user explicitly applies a draft later.

## What Not To Touch In That Pass

- Do not start auth work.
- Do not start bank sync, bank adapters, or finance core work.
- Do not split the whole backend into routers/services in the same pass.
- Do not redesign the whole visual language.
- Do not collapse Data-In AI and analysis AI into one generic chat.

## Acceptance Criteria

- every applied draft can be traced deterministically to source document + draft payload
- duplicate indicator checks both pending/deferred drafts and canonical rows
- no silent writes to canonical tables from analyze/promote endpoints
- existing full verification remains green:
  - `alembic upgrade head`
  - `python -m pytest tests/ -v`
  - app startup + `/`, `/docs`, `/healthz`
- docs updated with verified behavior and constraints

## Useful Starting Files

- `app/static/app.js`
- `app/ai_services.py`
- `app/static/styles.css`
- `app/main.py`
- `app/schemas.py`
- `docs/AI_DIRECTION.md`
- `docs/CURRENT_STATE.md`
- `docs/AINEXTSTEPPATCH.md`
