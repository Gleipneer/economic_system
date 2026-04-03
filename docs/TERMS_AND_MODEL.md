# Terms And Model

Canonical status: shared vocabulary for future AI and human work.
Last reviewed: 2026-04-03.

## Household

The top-level container for nearly all financial data in the repo.

Model: `Household`

## Person

A household member. Income is attached to people. Some other records may optionally point to a person.

Model: `Person`

## Private vs Shared

This is not a first-class accounting model in the repo.

Current representation is indirect:

- household-level records represent shared context
- optional `person_id`, `owner_person_id`, or similar fields represent person-linked records

There is no stronger private/shared ledger separation yet.

## Income

A structured income source attached to a person.

Model: `IncomeSource`

Important nuance:

- net or gross can be stored
- summary math will use gross where net is missing

## Loan

A liability row for mortgage, car loan, CSN, personal loan, credit card, or similar debt.

Model: `Loan`

## Subscription / Contract

A recurring household agreement such as mobile, broadband, electricity, streaming, gym, software, or similar.

Model: `SubscriptionContract`

## Recurring Cost

A non-subscription recurring cost such as food, transport, childcare, or other repeated spending.

Model: `RecurringCost`

Current product note:

- it exists in the backend and calculations
- it is not currently a first-class active frontend page

## Asset

A stored asset such as account, savings, fund, vehicle value, house value, or other owned value.

Model: `Asset`

## Housing Calculation / Boendekalkyl

The repo's housing-planning concept for testing one candidate home cost profile.

Model: `HousingScenario`

Evaluation endpoint:

- `GET /housing_scenarios/{id}/evaluate`

## Document

A document metadata row, optionally backed by a locally stored uploaded file.

Model: `Document`

## Extraction Draft

A proposed structured payload linked to a document and a target entity type.

Model: `ExtractionDraft`

Important nuance:

- drafts are proposal objects
- apply creates a canonical entity from `proposed_json`

## Optimization Opportunity

A suggested action to improve the household's finances.

Model: `OptimizationOpportunity`

Current source:

- heuristic backend scan, not external AI

## Scenario

A planning object that stores JSON adjustments to household records.

Model: `Scenario`

## Scenario Result

A stored comparison between baseline and projected summary after running a scenario.

Model: `ScenarioResult`

## Snapshot / Report Snapshot

A frozen summary output stored with an `as_of_date`.

Model: `ReportSnapshot`

This is a persisted summary artifact, not a transaction ledger snapshot.

## Planning Layer

The current repo is best described as a planning layer:

- structured household facts
- recurring commitments
- planning scenarios
- snapshot reports

It does not yet include lower-level transaction ingestion or reconciliation.

## Finance Core

Not implemented in this repo.

If introduced later, it would likely mean a lower-level ledger or normalized transaction/balance layer beneath the current planning layer.

## Transaction Kernel / Bank Adapter

Not implemented in this repo.

These are future-concept terms only, not current code concepts.
