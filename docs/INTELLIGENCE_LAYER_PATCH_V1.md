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

## Completion Status

| Feature | Status | Verified |
|---|---|---|
| Duplicate indicator | ✅ Done | Live-tested: Netflix detected as duplicate of existing draft |
| Ownership candidate | ✅ Done | Live-tested: Netflix→private, broadband→shared |
| Why-engine | ✅ Done | Rationale on every suggestion |
| Risk signals (summary) | ✅ Done | 8 signal types, tested with heavy costs |
| Risk signals (overview UI) | ✅ Done | Severity-coded badges |
| Risk signals (PDF export) | ✅ Done | 4910 bytes PDF with signals section |
| Evidence chain metadata | Not started | Deferred to next patch |
| External research hooks | Not started | Deferred |

## Verification

- 24 pytest tests pass
- Live OpenAI: subscription analyzed, duplicate detected, ownership assigned
- PDF: generates with risk signals, 4910 bytes
- Risk signals: fires correctly on high fixed ratio (87%)
- Zero canonical writes confirmed
