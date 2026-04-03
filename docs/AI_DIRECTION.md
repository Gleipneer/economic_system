# AI Direction

Canonical status: AI-specific truth and direction, without mixing current fact and future plan.
Last reviewed against code: 2026-04-03.

## What AI Does Today

AI-adjacent behavior currently implemented in the repo:

- `POST /households/{id}/assistant/respond` returns a household-aware answer in Swedish
- `POST /households/{id}/ingest_ai/analyze` returns classified raw-input analysis plus validated structured suggestions
- `POST /households/{id}/ingest_ai/promote` turns reviewed suggestions into workflow artifacts only
- `ExtractionDraft` exists as a workflow table for proposed structured data
- `OptimizationOpportunity` exists as a workflow table for improvement suggestions

Important truth:

- the assistant and Data-In AI are real OpenAI calls when provider config exists
- missing provider config returns explicit `503`, not fake fallback text
- the optimization scan is heuristic backend logic, not an AI provider integration

## What AI Does Not Do Today

The repo does not currently implement:

- any provider abstraction beyond direct OpenAI integration
- an AI gateway
- prompt logging
- model version tracking for live model calls
- embeddings or retrieval
- background AI jobs
- autonomous document extraction
- autonomous writes to canonical tables

## Current Assistant Contract

The current assistant:

- takes a prompt plus optional conversation payload
- loads a compact household read model built from current backend data
- calls the OpenAI Responses API through `app/ai_services.py`
- returns answer text plus `provider`, `model`, and token `usage`

Current limitation:

- the `conversation` field is still accepted by schema but is not used meaningfully in the current implementation
- the active frontend intentionally sends only `prompt` to keep token use down

## Read-Only Principle

The analysis assistant should be treated as read-only relative to canonical data.

That principle already holds today because:

- it only reads household data
- it returns text
- it does not mutate tables

## Draft and Promotion Principle

AI-like proposal flows should follow this boundary:

- proposals go into draft or opportunity records
- canonical entities change only through explicit promotion or explicit user action

Current nuance:

- `ingest_ai/promote` creates `Document` and `ExtractionDraft` rows only
- `extraction_drafts/{id}/apply` is still a separate, explicit user-triggered write into canonical tables
- there is no autonomous AI write into canonical finance records

## Tool-Contract Principles for Future AI

If external AI is added later, keep these rules:

- always scope requests to one household context
- validate model output against strict schemas
- keep deterministic finance calculations on the backend
- never let model output silently become canonical truth
- record enough metadata to audit model behavior if writes are ever proposed

## Desired Future Role

Future AI could reasonably do all of the following:

- propose structured extraction from uploaded documents and pasted raw bank text
- draft optimization opportunities with stronger reasoning
- explain household state in more natural language
- help compare scenarios or reports
- act as a safer question-answer layer over household data
- identify likely subscriptions, recurring costs, transfers, and unclear rows from LF-style copy-paste without claiming a bank-ledger backend already exists

## What Future AI Must Not Be Mistaken For

Future AI direction is not current implementation.

Do not state as fact that the repo already has:

- an AI gateway
- bank-adapter tooling
- autonomous bank reconciliation
- autonomous writes to canonical tables

## Current Live Validation Note

The current OpenAI integration was validated live on 2026-04-03.

Verified live:

- assistant analysis questions returned real responses from `gpt-5.4-mini-2026-03-17`
- Data-In AI handled four test inputs: LF-style bank copy-paste, subscription text, invoice text, and messy free text
- structured suggestions were validated before being returned
- promote required a separate explicit step and created workflow artifacts only

Observed token shape during validation:

- analysis prompts: about `969-996` total tokens
- ingest prompts: about `860-1006` total tokens

## Data-In Improvements (2026-04-03 second pass)

Changes made to improve Data-In for invoices, subscriptions, and PDF-paste:

- The AI prompt now gives explicit classification rules for invoices and subscriptions
- Input text is pre-analyzed for structural hints (invoice keywords, subscription keywords, Swedish amounts, dates, monthly cost patterns)
- Text normalization handles PDF-paste artifacts: NBSP, zero-width spaces, form feeds
- The frontend now shows document classification with color-coded badges, confidence percentages, and separated confirmed vs uncertain fields
- Screenshot/image OCR remains explicitly not implemented; the `OCRExtractor` protocol and `image_placeholder` rejection are in place as the prepared interface

Live OpenAI verification on 2026-04-03 (second pass) used `gpt-5.4-mini-2026-03-17`:

- Subscription text (Telia bredband): classified as `subscription_contract`, confidence 0.98, all key fields confirmed, 1661 tokens
- Invoice text (Stockholms Stad avfall): classified as `invoice`, confidence 0.98, quarterly→yearly frequency conversion with explicit note, 1843 tokens
- PDF-pasted text with NBSP (Halebop): classified as `invoice`, confidence 0.96, two valid suggestions (subscription + recurring_cost), 1899 tokens
- Messy uncertain text (Försäkringskassan): classified as `financial_note`, confidence 0.63, clear uncertainty reasons, suggestion correctly marked invalid, 1844 tokens
- Full browser promote flow: gym membership invoice analyzed, promoted to workflow draft, verified zero canonical writes

The frequency constraint fix (explicit enum values in field guides) resolved validation errors from the initial invoice test where the model used unsupported `"quarterly"` and `"low"` values.

## If an OpenAI Gateway Is Added Later

That would belong as a future integration layer, likely behind a backend service boundary.

It should be documented later as:

- a separate runtime concern
- explicit configuration
- explicit provider/model selection
- explicit auditing rules

It is not present now. The current code calls OpenAI directly.
