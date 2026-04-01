# System Architecture

This document outlines the high‑level architecture of the household
economics backend. It explains the rationale for separating concerns,
describes the core components and their interactions, and lays the
groundwork for future extensions such as AI‑driven analysis.

## Layers

The system is organised into distinct layers, each with a clear
responsibility. Separating concerns in this way promotes
reproducibility, ease of maintenance and extensibility.

### 1. Database Layer

* Implemented via **SQLAlchemy** ORM on top of a relational database.
* Models (`app/models.py`) define the schema for each entity. See
  `docs/frontend_schema.md` for a description of each model.
* The `database.py` module initialises the engine, session factory
  and base class. On startup, tables are created automatically if
  missing.
* Uses SQLite by default; migrations to PostgreSQL or another RDBMS
  require only changing the `DATABASE_URL` environment variable.

### 2. API Layer

* Built with **FastAPI** and Pydantic. Exposes REST endpoints for
  Create/Read/Update/Delete operations on each model.
* Input and output are validated using Pydantic schemas defined in
  `app/schemas.py`.
* Each request obtains its own database session via dependency
  injection. Sessions are committed explicitly to ensure transaction
  boundaries are clear.
* CORS middleware allows access from any origin by default. Restrict
  this in production.

### 3. Document & Draft Layer

* Documents (e.g. PDF receipts, invoices, contracts) can be stored via
  the `Document` model. Files are not handled by the API in this
  repository; you are free to implement file storage locally or via
  object storage in the deployment environment.
* `ExtractionDraft` captures AI‑generated structured data awaiting
  human verification. Drafts must be approved or rejected before
  becoming canonical data in the core tables. This enforces that AI
  suggestions do not overwrite ground truth without review.

### 4. AI/Analysis Layer (Future)

* Not implemented in this repository. The architecture reserves space
  for AI services which will:
  - Parse documents and extract structured information according to
    strict JSON schemas.
  - Categorise costs and subscriptions.
  - Suggest optimisation opportunities (e.g. cancel, renegotiate,
    switch provider).
  - Simulate scenarios (e.g. rate changes, cost reductions).
  - Answer questions about the household's finances.
* AI components must never be a source of truth. They create
  *drafts* and *suggestions* that require human or rule‑based
  approval.

### 5. Frontend (External)

* Outside the scope of this repository. A frontend application
  (web/mobile/desktop) is expected to consume the API, present
  intuitive forms to the user, display dashboards and reports, and
  manage authentication and authorisation.
* The data model and endpoints described in
  `docs/frontend_schema.md` are intended to guide frontend
  implementation.

## Responsibilities & Boundaries

* **Deterministic Calculations** – All financial calculations (e.g.
  monthly net, loan service costs, stress tests) should be pure
  functions based on the stored data. Avoid embedding formulas in
  templates or the user interface.
* **Versioned Snapshots** – Reports intended for external parties
  (e.g. banks) should be produced from versioned snapshots (`ReportSnapshot`)
  to guarantee reproducibility even as underlying data changes.
* **Explicit Statuses** – Entities such as loans, documents and
  optimisation opportunities carry explicit status fields so that
  business workflows can be tracked over time.
* **Separation of Duties** – AI agents, if integrated, propose
  changes but must not persist them directly. Humans or deterministic
  rules validate and apply changes.

## Future Evolution

The current architecture intentionally leaves out several concerns which
should be addressed when building a production system:

* **Authentication & Authorisation** – Introduce user accounts and
  roles to protect sensitive financial data.
* **File Management** – Integrate persistent storage for uploaded
  documents (e.g. local filesystem, S3, Azure Blob).
* **Eventing & Background Jobs** – Use a task queue (e.g. Celery,
  Dramatiq) for long‑running tasks such as document parsing,
  optimisation scans and reminders before contract renewal.
* **Instrumentation & Monitoring** – Add logging, metrics and health
  checks to facilitate operation in production environments.
* **Test Suite** – Implement thorough unit and integration tests.

The architectural constraints defined here ensure that core data
remains deterministic, auditable and safe to build upon as more
sophisticated features are added.