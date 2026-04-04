# READMEAI.md — Handoff to Next AI Agent

Last updated: 2026-04-04.

## What This Agent Read

All canonical docs + key source files. Full context from previous handoffs.

## What This Agent Did

### Intelligence Layer Patch V1

Built and verified 5 intelligence features under the hood:

1. **Risk signals on household summary** (8 signal types)
   - low_margin, negative_cashflow, high_fixed_ratio, high_subscription_cost
   - high_debt_ratio, elevated_debt_ratio, unverified_income, pending_reviews, no_income
   - Displayed on overview page with severity badges
   - Included in PDF export with risk section
   - Deterministic (no AI) — based on real household math

2. **Duplicate indicator on suggestions**
   - Checks existing pending_review/deferred drafts for same provider+amount
   - Shows warning in review UI: "Möjlig dubblett: liknande utkast #1"
   - Live-tested: Netflix duplicate correctly detected

3. **Ownership candidate per suggestion**
   - Heuristic: shared (mat, boende, transport, broadband) vs private (gym, streaming, software)
   - Displayed as color-coded badge in review UI
   - Live-tested: Netflix→private, broadband→shared

4. **Why-engine rationale**
   - AI rationale or auto-generated explanation on every suggestion
   - Shows classification, provider, amount, confidence in human-readable Swedish
   - Displayed in review UI

5. **Enhanced PDF export with risk signals**
   - Risk signals section added before source notes
   - Critical/warning/info severity prefixes

### Also created
- `docs/INTELLIGENCE_LAYER_PATCH_V1.md` — patch plan with completion status

## What Was Verified

- 24 pytest tests pass (22 existing + 2 new)
- `alembic upgrade head`: clean
- `/healthz`, `/`, `/docs`: all ok
- Live OpenAI: Netflix subscription analyzed with duplicate detection + ownership + why-engine (1606 tokens)
- Risk signals: fires correctly on high fixed ratio (87% of income → warning)
- PDF export: 4910 bytes with risk signals section
- Zero canonical writes confirmed after promote

## Phase Status

| Phase | Status |
|---|---|
| FAS 1: Ingest + review | ✅ Complete |
| FAS 1.7: PDF export | ✅ Complete (with risk signals) |
| FAS 2.1: Merchant normalization | ✅ Complete |
| FAS 2.2: Duplicate detection | ✅ V1 done (drafts check) |
| FAS 2.3: Ownership suggestions | ✅ V1 done (heuristic) |
| FAS 2.4: Why-engine | ✅ V1 done |
| FAS 2.5: Risk signals | ✅ V1 done (8 signal types) |
| FAS 2.6: Rule engine | Not started |
| FAS 3+: Time, analysis, research | Not started |

## Exact Next Steps

1. **Evidence chain** — link Document → ExtractionDraft → applied entity with provenance metadata
2. **Duplicate detection vs canonical data** — check subscriptions/costs tables, not just drafts
3. **Editable ownership field** on draft cards
4. **Playwright watchdog** — browser regression tests for core flows
5. **External research hooks** — subscription price comparison interface
6. **Rule engine** — user-approved pattern matching

## Key Files

| File | Why |
|---|---|
| `app/calculations.py` | Risk signals (_build_risk_signals) |
| `app/ai_services.py` | Duplicate check, ownership, why-engine |
| `app/schemas.py` | RiskSignalRead, intelligence fields on IngestSuggestionRead |
| `app/pdf_export.py` | PDF with risk signals |
| `app/static/app.js` | Risk signals on overview, intelligence on suggestion cards |
| `docs/INTELLIGENCE_LAYER_PATCH_V1.md` | Patch plan + status |
| `docs/ECONOMIC_SYSTEM_MASTER_ROADMAP.md` | Phase tracking |

## Critical Truths

- Risk signals are DETERMINISTIC (no AI) — pure backend math in calculations.py
- Duplicate check queries the DB (not AI) — graceful fallback on missing tables
- Ownership is a HEURISTIC based on category mapping — not AI
- Why-engine uses AI rationale when available, falls back to generated description
- All intelligence is advisory — no silent canonical writes
- Pydantic v1 (1.10.9), 9 classification types, bank paste works

## Git State

- Branch: `cursor/development-environment-setup-a192`
- Latest commit: `29367c9`
- All changes committed and pushed
- PR #1: https://github.com/Gleipneer/economic_system/pull/1
