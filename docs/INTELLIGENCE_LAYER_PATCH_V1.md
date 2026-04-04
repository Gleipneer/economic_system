# Intelligence Layer Patch V1

Patch plan for adding intelligence layers under the hood to the household economics system.

Last updated: 2026-04-04.

## Current State

Phase 1 (ingest) and 2.1 (merchant normalization) are complete. PDF export exists. 22 tests pass. All live-verified.

## This Patch Scope

Build real intelligence layers that make the system smarter without becoming brittle.

### What this patch delivers (prioritized)

| # | Feature | Priority |
|---|---|---|
| 1 | Duplicate & similarity indicator on drafts | **NOW** |
| 2 | Ownership candidate (private/shared/unclear) on suggestions | **NOW** |
| 3 | Why-engine (rationale metadata on every suggestion) | **NOW** |
| 4 | Risk/readiness signals on household summary | **NOW** |
| 5 | Enhanced PDF export with risk signals + source status | **NOW** |
| 6 | Evidence chain metadata on drafts | **SOON** |
| 7 | External research hooks | **SOON** |

### What this patch does NOT include

- Auth, bank sync, finance core, ledger
- Full rules engine with complex pattern matching
- Playwright watchdog (deferred to next patch — needs browser agent)
- Broad frontend redesign

## Acceptance Criteria

- Duplicate indicator works for at least 3 real test cases
- Ownership candidate appears on suggestions
- Why-engine rationale is visible in review UI
- Risk signals appear on overview/summary
- PDF export includes risk signals and source notes
- All 22+ tests pass
- Zero canonical writes from AI

## Verification

- Runtime: alembic, healthz, frontend, docs
- Tests: full suite + new tests
- Live OpenAI: at least 2 real ingest calls verified
- PDF: generates, opens, content correct
