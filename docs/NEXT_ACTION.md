# Next Action

Canonical status: single recommended next task for the next agent pass.
Last reviewed: 2026-04-03.

## Next Task

Restore recurring costs as a first-class module in the active frontend.

## Why This Comes Next

This is the highest-value gap directly visible in the current product:

- recurring costs are part of the backend model
- recurring costs affect the summary calculations
- optimization scan reads recurring costs
- the active routed frontend does not expose them cleanly

That means an important household concept exists in the system but is not fully operable from the product surface.

## What Must Stay Stable

- Keep `app.main:app` as the runtime entrypoint.
- Keep the current Swedish route-based frontend shell.
- Keep the global active-household selector.
- Keep backend API contracts unchanged unless there is a strong reason.
- Keep summary, reports, scenarios, documents, and assistant flows working as they do now.

## What Not To Touch In That Pass

- Do not start auth work.
- Do not start external AI integration.
- Do not start bank-ingest or finance-core work.
- Do not split the whole backend into routers/services in the same pass.
- Do not redesign the whole visual language.

## Acceptance Criteria

- The active SPA has a reachable recurring-cost page or equivalent product surface.
- Existing recurring costs for the selected household can be listed.
- Users can create, edit, and delete recurring costs through the active frontend.
- The frontend submission and deletion handlers are wired for recurring costs.
- The UI keeps the Swedish household-product framing rather than falling back to raw CRUD.
- Existing backend summary behavior remains unchanged.
- Documentation is updated if route names or navigation change.

## Useful Starting Files

- `app/static/app.js`
- `app/static/styles.css`
- `app/main.py`
- `app/schemas.py`
- `docs/FRONTEND_DIRECTION.md`
- `docs/CURRENT_STATE.md`
