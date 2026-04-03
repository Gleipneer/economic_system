# Project Context

Canonical status: current source of truth for project identity and direction.
Last reviewed against code: 2026-04-03.

## What This System Is

This repository contains a Swedish household economics application built as one FastAPI deployment.

Today it combines:

- a relational backend for structured household finance data
- a same-origin web frontend served from the backend
- deterministic calculations for summaries, housing scenarios, reports, and scenario comparisons
- document upload and draft/opportunity workflow objects
- a lightweight assistant endpoint that summarizes existing household data

## What Problem It Solves

The system is trying to give a household one operational place for:

- incomes
- loans
- subscriptions and contracts
- insurance
- vehicles
- assets
- housing calculations
- documents
- scenario planning
- snapshot-style reports

This is not a bank-ingest ledger today. It is a planning and operating layer over structured household facts and estimates.

## Who It Is For

Primary target user:

- a Swedish household that wants a practical overview of its economy

Secondary target user:

- a future developer or AI agent that must continue work without rediscovering the repo

## How It Should Feel

The frontend code expresses a product that should feel:

- Swedish rather than generic SaaS
- calm, warm, and domestic rather than corporate
- operational and practical rather than analytical for its own sake
- guided by real household tasks rather than by raw table names

## Current Product Character

The current product is:

- one deployable FastAPI app
- same-origin backend + frontend
- SQLite-first and filesystem-first
- structured around household planning objects, not transactions
- partially productized in the frontend, but still form-heavy in parts

The current frontend is not a pure CRUD admin panel, but it is also not yet a finished consumer-grade household app. It sits between those states.

## Current System vs Future Vision

### Current System

- manual data entry is the main source of truth
- deterministic backend calculations are real and connected
- document upload/download is real
- extraction drafts and optimization opportunities exist as workflow objects
- report snapshots and scenarios are real
- the assistant endpoint is real, but deterministic and local-data-driven

### Future Vision

Likely direction, but not implemented as a committed runtime fact:

- stronger AI-assisted document understanding
- better assistant behavior
- safer approval workflows around AI outputs
- stronger operational hardening
- richer frontend flows
- possibly a lower-level finance core or transaction ingest layer

## Explicit Boundaries

The repo does not currently implement:

- bank integrations
- bank transaction ingest
- a finance core ledger
- authentication or authorization
- background jobs
- external AI provider integration
- object storage

## Source-of-Truth Rule

If prose and code disagree, trust the code. This documentation set exists to reduce rediscovery, not to replace direct code reading.
