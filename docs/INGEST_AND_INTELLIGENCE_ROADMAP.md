# Ingest & Intelligence Roadmap

Last updated: 2026-04-04.

This roadmap covers the five new capability tracks identified for the next evolution of the household economics system. It complements the existing `ECONOMIC_SYSTEM_MASTER_ROADMAP.md`.

## Priority Order

| # | Track | Priority | Rationale |
|---|---|---|---|
| 1 | Bank-ready PDF export | **NU** | Highest immediate user value; data already exists |
| 2 | OCR/PDF robustness | **NU** | Already partially done; needs verification + ocrmypdf |
| 3 | Normalization/rules engine | **SNART** | Reduces variation, improves ingest quality over time |
| 4 | External research module | **SNART** | Subscription comparison requires careful truth separation |
| 5 | Playwright watchdog | **SNART** | Regression safety for all the above |

---

## Track 1: Bank-Ready PDF Export

### Goal
A first-class "Exportera bankkalkyl" button that generates a premium PDF suitable for showing a bank officer when applying for a mortgage.

### What the PDF must contain
- Household name + date stamp
- Persons in household
- Income summary (net + gross breakdown)
- Fixed costs (recurring costs, subscriptions, insurance, vehicle costs)
- Loan/debt obligations (monthly payments, remaining balance)
- Housing scenario evaluation (if one exists)
- Monthly margin before/after housing
- Asset summary
- Source status: what is canonical data vs review draft vs uncertain
- Clean, professional, Swedish layout

### Technical approach
- Backend: `GET /households/{id}/export/bank_pdf` endpoint
- Uses `app/calculations.py` (same deterministic math as summary)
- PDF generation via `reportlab` or `weasyprint`
- No fake data; only real household records
- Frontend: button on reports page or overview

### Status
- [ ] Install PDF library (reportlab)
- [ ] Create `app/pdf_export.py` module
- [ ] Implement `GET /households/{id}/export/bank_pdf`
- [ ] Professional layout with Swedish typography
- [ ] Frontend button wired
- [ ] Runtime verified: PDF opens, content matches data
- [ ] Test added

---

## Track 2: OCR/PDF Robustness

### Current state
- Tesseract OCR (swe+eng) implemented for images and scanned PDFs
- PDF text extraction via pypdf
- Scanned PDFs fall back to page-image OCR

### Remaining work
- [ ] Evaluate ocrmypdf for better scanned PDF preprocessing
- [ ] Add ocrmypdf if it measurably improves output
- [ ] Verify with real scanned invoice PDF
- [ ] Verify with real photo of document
- [ ] Confirm OCR text always marked as non-canonical

---

## Track 3: Normalization & Rules Engine

### Goal
Allow the system to learn approved patterns over time, reducing AI dependency and improving data quality.

### First iteration scope
- [ ] Merchant normalization table (alias → canonical name)
- [ ] API: list/create/delete merchant aliases
- [ ] Apply merchant normalization during ingest pre-processing
- [ ] Ownership suggestion (private/shared/unclear) in draft review
- [ ] Duplicate indicator when same provider+amount exists in recent drafts/docs

### Not in first iteration
- Full rules engine
- Automatic rule creation
- Complex pattern matching

---

## Track 4: External Research Module

### Goal
Allow the analysis AI to suggest cheaper alternatives for subscriptions and household services, with clear source attribution and uncertainty.

### Design principles
- External facts are NEVER mixed with internal household data as if they were the same type of truth
- Sources, dates, and uncertainty must be explicit
- Start simple: web search for Swedish prices, not broad API integrations

### First iteration scope
- [ ] `app/research.py` module with clear interface
- [ ] Function: `research_subscription_alternatives(provider, product, category)` → list of alternatives with source+date
- [ ] Integration with analysis AI: assistant can mention alternatives when asked
- [ ] Clear UI separation: "extern research" vs "hushållsdata"

### Not in first iteration
- Automated price monitoring
- Broad provider database
- Scraping infrastructure

---

## Track 5: Playwright Watchdog

### Goal
Browser-based regression tests for core flows to catch real runtime errors.

### Flows to cover
- [ ] Data-In: paste text → analyze → review → promote
- [ ] Document upload → OCR extraction
- [ ] Recurring cost CRUD
- [ ] Subscription CRUD
- [ ] Report generation
- [ ] Assistant chat
- [ ] PDF export download

### Technical approach
- Playwright with Python
- Run against local dev server
- Separate test file: `tests/test_e2e.py`
- Not required in CI initially; manual regression tool

---

## Hard Invariants (all tracks)

- AI never writes silently to canonical data
- External research data is always labeled as external
- PDF export uses only real deterministic calculations
- OCR text is always marked as raw extraction, not truth
- Promote creates only workflow artifacts
- Apply remains separate and explicit
