# Frontend Direction

Canonical status: intended frontend product form, separated from backend truth.
Last reviewed against code: 2026-04-03.

## Core Product Form

This frontend should be treated as a Swedish household economics app.

It should not drift into:

- a generic CRUD admin panel
- a raw schema browser
- a finance-developer tool

## Current Active Information Architecture

The active SPA currently exposes these page-level concepts:

- overview
- guided registration
- household
- persons
- incomes
- loans
- subscriptions and contracts
- insurance
- vehicles
- assets
- housing calculation
- documents
- improvement suggestions
- scenarios
- saved reports
- assistant

This information architecture is already much more productized than the older docs in the repo imply.

## What Good Frontend Means Here

Good frontend for this system:

- starts from household tasks
- speaks Swedish and feels domestic, not enterprise
- keeps one active household context
- shows concrete next steps
- uses backend summaries and evaluation endpoints instead of duplicating core logic
- keeps documents, scenarios, reports, and assistant inside the same product language

Bad frontend for this system:

- exposes database fields without household framing
- makes the user think in IDs
- duplicates money math in the browser
- looks like an internal admin screen
- treats AI as a gimmick detached from real data

## Visual Language in the Current Code

The current frontend already encodes a specific visual direction:

- warm beige and green-gray palette
- rounded cards and panels
- serif heading accent with sans-serif body
- soft shadows, light surfaces, and calm contrast
- mobile-aware sidebar behavior

This should be preserved unless there is an explicit redesign decision.

## Most Important Frontend Modules

Highest-value modules in the current product shape:

- overview
- subscriptions and contracts
- loans
- housing calculation
- documents
- reports
- assistant

These carry most of the product identity today.

## Frontend Reality That Must Not Be Missed

- recurring costs still exist in the backend and in summary math
- the active SPA route set does not currently expose recurring costs as a first-class screen
- older V1 cost UI code still exists in `app/static/app.js`, but it is not part of the active routed product surface

That means the frontend is currently incomplete, not that recurring costs disappeared from the system.

## How the Current Frontend Should Be Preserved

Preserve:

- same-origin SPA deployment
- Swedish route naming and copy
- global household selector
- route-based page model
- overview-first experience
- assistant as a product feature, not a dev tool

Avoid:

- collapsing back to generic tables everywhere
- deleting the guided registration layer
- removing reports, scenarios, or assistant from the primary UX

## How the Assistant Fits In

The assistant belongs as a household-facing explanation and prioritization surface.

It should:

- explain existing data
- summarize risks and opportunities
- point the user toward concrete product modules

It should not:

- become a hidden write path
- replace the structured forms
- claim knowledge not present in the repo
