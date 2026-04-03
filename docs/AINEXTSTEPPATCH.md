# AI Next Step Patch

Canonical status: proposed next large patch after the 2026-04-03 runtime and AI pass.

## Patch Name

LF copy-paste ingest hardening.

## Why This Patch Comes Next

The repo now has:

- first-class recurring costs in the active frontend
- a working subscription submit flow
- real OpenAI-backed analysis AI
- real OpenAI-backed Data-In AI
- explicit promote-to-draft behavior

The highest-value remaining gap is practical household ingest from pasted bank/account text, especially LF-style exports.

## Problem Statement

Current Data-In AI is safe but still limited:

- it works well on simple contract-like text
- it can classify raw bank-like text conservatively
- it does not yet turn LF-style row dumps into useful batches of reviewable household insights

That means the user still carries too much manual interpretation load at the point where the app should start saving real time.

## Patch Goal

Support conservative intake of pasted account text with fields such as:

- `bokföringsdatum`
- `transaktionsdatum`
- `transaktionstext`
- `belopp`
- `saldo`

The output should stay inside the current planning/workflow model.

It must not pretend that the repo already has:

- bank sync
- transaction ledger
- reconciliation engine
- automatic canonical writes

## Required Outcome

After this patch, a user should be able to:

1. paste LF-style account text
2. get a conservative structured interpretation
3. review likely recurring payments, likely subscriptions, likely transfers/savings, and unclear rows
4. promote only the valid suggestions into workflow artifacts
5. keep canonical finance tables unchanged until a later explicit apply step

## Hard Invariants

- raw input != structured interpretation
- structured interpretation != canonical truth
- AI output must be schema-validated
- uncertainty must be visible
- no silent writes to canonical finance records
- backend remains owner of finance math

## Recommended Technical Shape

Preferred flow:

```text
[LF paste UI]
  -> [bank-like parser/pre-normalizer]
  -> [AI classify/extract]
  -> [schema validation]
  -> [review groups: recurring / subscription / transfer / unclear]
  -> [explicit promote]
  -> [Document + ExtractionDraft rows]
```

Recommended code focus:

- `app/ai_services.py`
- `app/main.py`
- `app/schemas.py`
- `app/static/app.js`
- `tests/test_smoke.py`
- `docs/AI_DIRECTION.md`
- `docs/CURRENT_STATE.md`

## Acceptance Criteria

- LF-like pasted text can be analysed in the product, not only via raw API calls
- the system extracts at least one conservative structured class beyond generic `financial_note`
- likely subscriptions and recurring costs can become validated suggestions
- unclear rows remain clearly marked as unclear
- promote still creates workflow artifacts only
- no canonical tables are changed without explicit later apply
- docs are updated truthfully

## What Must Not Be Included In This Patch

- bank-login integrations
- transaction ledger work
- finance-core refactor
- auth rollout
- full provider abstraction
- broad frontend redesign

## Verification Requirements

- browser test with realistic LF-style pasted input
- API test for analyse + promote
- live OpenAI test with cost-conscious model settings
- explicit documentation of what was still ambiguous after implementation
