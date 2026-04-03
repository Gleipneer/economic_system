# AI Direction

Canonical status: AI-specific truth and direction, without mixing current fact and future plan.
Last reviewed against code: 2026-04-03.

## What AI Does Today

AI-adjacent behavior currently implemented in the repo:

- `POST /households/{id}/assistant/respond` returns a household-aware answer in Swedish
- `ExtractionDraft` exists as a workflow table for proposed structured data
- `OptimizationOpportunity` exists as a workflow table for improvement suggestions

Important truth:

- the assistant is currently deterministic server logic, not an external model call
- the optimization scan is heuristic backend logic, not an AI provider integration

## What AI Does Not Do Today

The repo does not currently implement:

- OpenAI integration
- any other model provider integration
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
- loads the selected household's current records
- builds an answer from summary data and prompt keywords
- returns text only

Current limitation:

- the `conversation` field is accepted by schema but not used meaningfully in the current response logic

## Read-Only Principle

The assistant should be treated as read-only relative to canonical data.

That principle already holds today because:

- it only reads household data
- it returns text
- it does not mutate tables

## Draft and Promotion Principle

AI-like proposal flows should follow this boundary:

- proposals go into draft or opportunity records
- canonical entities change only through explicit promotion or explicit user action

Current nuance:

- `extraction_drafts/{id}/apply` is explicit and user-triggered
- there is not yet a separate approve/reject API flow before promotion

## Tool-Contract Principles for Future AI

If external AI is added later, keep these rules:

- always scope requests to one household context
- validate model output against strict schemas
- keep deterministic finance calculations on the backend
- never let model output silently become canonical truth
- record enough metadata to audit model behavior if writes are ever proposed

## Desired Future Role

Future AI could reasonably do all of the following:

- propose structured extraction from uploaded documents
- draft optimization opportunities with stronger reasoning
- explain household state in more natural language
- help compare scenarios or reports
- act as a safer question-answer layer over household data

## What Future AI Must Not Be Mistaken For

Future AI direction is not current implementation.

Do not state as fact that the repo already has:

- an OpenAI-backed assistant
- an AI gateway
- bank-adapter tooling
- automated document parsing
- autonomous cost categorization

## If an OpenAI Gateway Is Added Later

That would belong as a future integration layer, likely behind a backend service boundary.

It should be documented later as:

- a separate runtime concern
- explicit configuration
- explicit provider/model selection
- explicit auditing rules

It is not present now.
