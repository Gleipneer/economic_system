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

- There is no demo-seed route, despite older docs historically implying one.
- The assistant does not maintain meaningful conversation state.
- LF-style bank copy-paste is only lightly handled today; current ingest is useful for simple text cases, not a mature bank-row workflow.
- Data-In AI is currently embedded in the documents page rather than a dedicated high-throughput ingest workspace.
- There is no user account model or privacy boundary beyond deployment trust.

## Integration Risks

- Local file paths are persisted in document metadata.
- Docker Compose bind-mounts the whole repo into `/app`, so runtime state lives in the repo working tree.
- There is no stable versioned API export or compatibility policy for frontend consumers.
- OpenAI integration is implemented directly, without a provider abstraction or gateway layer.
- AI depends on outbound network access and valid provider credentials.

## Architectural Debt

- The repo still carries stale or compatibility-layer docs and artifacts from earlier shapes.
- `app/static/server.py` is a side runtime artifact that can confuse future readers.
- `app/system_docs.py` is not the primary runtime source of validation truth.
- Report snapshots currently store summary-style JSON, not a richer reporting document system.
- Scenario execution uses JSON adjustments against loaded records, not a lower-level financial model.

## Validation Risk

Current local validation is materially better than the old docs implied:

- the smoke suite is green locally
- the historical contract-flow `502` report was not reproduced locally

But one risk remains:

- the `502` report came from a live mobile/Tailscale context and may still hide an environment-specific issue

This is not a reproduced local backend failure, but it is still an unresolved field report and should not be ignored.

## Things That Must Not Be Misread As Complete

- OpenAI integration existing does not mean AI is production-hardened.
- Optimization suggestions are not market-integrated recommendations.
- Document upload plus Data-In AI is not a bank-ingest ledger.
- Draft promote plus apply is not a full audit workflow.
- Alembic existence does not mean operational migration discipline is finished.
- Same-origin frontend existence does not mean the frontend is feature-complete.

## Where Extra Caution Is Required

- When changing schema behavior, because startup auto-bootstrap can hide migration mistakes
- When changing frontend routing, because the SPA relies on FastAPI catch-all behavior
- When touching document storage, because files are currently local and path-based
- When touching `app/static/app.js`, because the file still contains duplicated legacy and active handler blocks
- When touching AI behavior, because old docs already overstated scope once and the current code now has live-provider consequences
