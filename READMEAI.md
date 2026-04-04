# READMEAI.md — Handoff to Next AI Agent

Last updated: 2026-04-04.

## What This Agent Read

All canonical docs (HANDOFF_MASTER, CURRENT_STATE, LOCKED_DECISIONS, AI_DIRECTION, NEXT_ACTION, AINEXTSTEPPATCH, ECONOMIC_SYSTEM_MASTER_ROADMAP, INGEST_AND_INTELLIGENCE_ROADMAP, README, previous READMEAI). Full source of key files: `app/main.py`, `app/ai_services.py`, `app/schemas.py`, `app/models.py`, `app/calculations.py`, `app/pdf_export.py`, `app/ingest_content.py`, `app/static/app.js`. Full tests: `tests/test_smoke.py`.

## What This Agent Did (in order)

### 1. Baseline verification
- Verified 22 tests pass, git state clean, runtime healthy

### 2. Fixed master roadmap truth
- `insurance_policy` and `loan_or_credit` were already implemented but marked unchecked → fixed
- `Bättre visuell status per utkast` was already done (rich draft cards) → fixed
- Added `1.7 Bank-Ready PDF Export` section with all items checked

### 3. Completed Phase 1 Review Queue (last 2 items)
- **Inline draft editing**: JSON editor with save/cancel for extraction drafts before apply
- **Defer function**: "Skjut upp" button sets draft status to `deferred`
- Both wired with event handlers and state management in frontend

### 4. Started Phase 2: Merchant Normalization
- **MerchantAlias model**: `merchant_aliases` table with household_id, alias (lowercase), canonical_name, category_hint
- **API**: `GET/POST/DELETE /households/{id}/merchant_aliases`
- **Ingest integration**: `_load_merchant_aliases()` + `_apply_merchant_normalization()` run on ingest text before AI classification
- Runtime verified: alias creation, listing, normalization in ingest pipeline

### 5. Updated docs
- `docs/ECONOMIC_SYSTEM_MASTER_ROADMAP.md`: Phase 1 fully checked, Phase 2.1 partially checked
- `docs/CURRENT_STATE.md`: PDF export endpoint, merchant alias endpoints, 9 classification types documented
- `docs/INGEST_AND_INTELLIGENCE_ROADMAP.md`: Track 1 (PDF) fully checked

## What Was Verified

- 22 pytest tests pass
- `alembic upgrade head`: clean
- `/healthz`: ok
- `/`, `/docs`: load correctly
- PDF export: generates valid 2-page PDF (verified in previous session)
- Merchant alias API: create, list, delete all work
- Draft edit API (PUT proposed_json): works
- Draft defer API (PUT status=deferred): works

## What Was NOT Verified

- Browser UI test of draft editing and defer (computerUse agent limit hit in previous sessions)
- Live OpenAI test with merchant normalization applied
- OCR with real scanned document (previous agent verified with generated image only)

## Phase Status

| Phase | Status |
|---|---|
| FAS 1: Ingest quality | ✅ **Complete** — all items checked |
| FAS 1.7: PDF export | ✅ **Complete** |
| FAS 2.1: Merchant normalization | 🟡 **Backend done** — needs frontend UI |
| FAS 2.2: Duplicate detection | Not started |
| FAS 2.3: Ownership suggestions | Not started |
| FAS 3+: Time, analysis, AI | Not started |

## Exact Next Steps (in order)

1. **Frontend for merchant aliases** — UI to list/create/delete aliases on the documents page or a settings section
2. **Duplicate indicator** — warn when same provider+amount appears in recent drafts/documents
3. **Live OpenAI verification** — test all input types with current code
4. **Playwright watchdog** — browser regression tests for core flows
5. **External research module** — stub for subscription alternative lookup

## Most Relevant Files

| File | Why |
|---|---|
| `docs/ECONOMIC_SYSTEM_MASTER_ROADMAP.md` | Phase tracking with checkboxes |
| `docs/INGEST_AND_INTELLIGENCE_ROADMAP.md` | 5-track capability roadmap |
| `app/main.py` | All endpoints including PDF, aliases, ingest |
| `app/ai_services.py` | AI ingest + merchant normalization |
| `app/models.py` | MerchantAlias model (new) |
| `app/schemas.py` | MerchantAlias schemas (new) |
| `app/pdf_export.py` | Bank-ready PDF generation |
| `app/static/app.js` | Frontend SPA with draft edit/defer |
| `tests/test_smoke.py` | 22 tests |

## What Next AI Must NOT Misunderstand

- Phase 1 is FULLY complete — do not re-implement draft editing or defer
- `MerchantAlias` model exists but the table may not exist in old databases — `_load_merchant_aliases` handles this gracefully
- The PDF export is a real working feature, not a stub
- Pydantic v1 (1.10.9), not v2
- 9 document classification types are in both schemas and AI models
- `image_placeholder` was replaced by `image` — not a future item
- Bank paste already works and has been live-tested against OpenAI

## Git State

- Branch: `cursor/development-environment-setup-a192`
- Latest commit: `35b6f8d` (merchant normalization)
- All changes committed and pushed
- PR #1: https://github.com/Gleipneer/economic_system/pull/1
