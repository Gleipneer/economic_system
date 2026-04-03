# Household Economics Backend

## Read This First

For the current, AI-readable handoff, start with:

1. [`docs/HANDOFF_MASTER.md`](docs/HANDOFF_MASTER.md)
2. [`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md)
3. [`docs/LOCKED_DECISIONS.md`](docs/LOCKED_DECISIONS.md)

## Overview

For AI continuation, start with [`AI_START_HERE.md`](AI_START_HERE.md).

This repository contains a runnable household economics system with a
**FastAPI backend** and a lightweight **built-in frontend**. It acts as the
single source of truth for financial data used by a household, including
income sources, loans, recurring costs, subscription contracts, insurance
policies, vehicles, assets, housing scenarios, documents, scenarios and
derived reports.

The architecture separates concerns into layers:

| Layer                | Responsibility                                                      |
|----------------------|--------------------------------------------------------------------|
| Database (SQL)       | Persist domain entities in a relational model                       |
| Backend (FastAPI)    | Provide CRUD operations, workflows and deterministic calculations   |
| Document Ingestion   | Store raw documents (PDF, images) and create extraction drafts      |
| Assistant / AI layer | Deterministic household assistant exists today; external AI remains future direction |
| Frontend (included)  | Present UI forms, dashboard actions and drive user workflows       |

The included frontend is intentionally lightweight and same-origin. It is
good enough for household use, validation, mobile access over Tailscale and
backend iteration. A separate document (`docs/frontend_schema.md`) describes
the API endpoints and data schema for frontend developers who want to build
another client.

## Features

* **Robust Data Model** – SQLAlchemy models cover the full range of domain
  concepts: households, persons, incomes, loans, recurring costs,
  subscription contracts, insurance policies, vehicles, assets, housing
  scenarios, documents, drafts, optimisation opportunities, scenarios,
  scenario results and report snapshots.
* **CRUD API** – Each entity exposes REST endpoints for listing,
  creating, retrieving, updating and deleting records. The API returns
  Pydantic schemas for type safety and validation.
* **Integrated Web UI** – The backend serves a mobile-friendly frontend
  at `/` for household operation from laptop or phone.
* **Deterministic Summaries** – Household summary, housing evaluation,
  scenario execution and report snapshot generation are implemented on
  the backend.
* **Document Uploads** – Documents can be uploaded and downloaded using
  the API and are stored locally by default.
* **Workflow Utilities** – Optimisation scans, extraction draft
  application, scenario execution and report snapshots are available
  for validation and daily use.
* **Household Assistant** – A built-in assistant endpoint can explain
  the current household state from stored data. It is deterministic and
  does not call an external model provider.
* **SQLite by Default** – A local SQLite database is used by default so
  the backend works out of the box. The `DATABASE_URL` environment
  variable allows migration to PostgreSQL or another RDBMS without code
  changes.
* **OpenAPI Documentation** – Run the app and visit `/docs` to see
  interactive API documentation generated automatically by FastAPI.
* **Dockerised Deployment** – Use the provided `Dockerfile` and
  `docker‑compose.yml` to build and run the backend in a self‑contained
  container, ideal for deployment on Ubuntu or within a Tailscale network.

## Quick Start

### Prerequisites

* [Python 3.11](https://www.python.org/) or later installed locally, **or**
* [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)

### Running with Docker

```bash
git clone <repository-url>
cd economic_system
docker-compose up -d --build
```

This builds a Docker image, starts a container and exposes the API on
`http://localhost:8000`. You can override the database location via
`DATABASE_URL`. For example, to use a PostgreSQL container instead of
SQLite, extend `docker-compose.yml` accordingly.

If the host machine is connected to Tailscale and the service binds to
`0.0.0.0`, the UI and API are also reachable at
`http://<tailscale-ip>:8000`.

### Running Locally without Docker

```bash
git clone <repository-url>
cd economic_system
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

By default the application writes its SQLite database to `database.db` in
the project root. Set `DATABASE_URL` in your shell to point at another
database if needed.

Open the UI at `http://localhost:8000/` and the API docs at
`http://localhost:8000/docs`.
The system validation spec is available at
`docs/SYSTEM_VALIDATION.md`.

### Database Migrations

Alembic is now configured for schema evolution. For a fresh database or
after pulling schema changes, run:

```bash
alembic upgrade head
```

If you already have an existing local database created before Alembic was
introduced, the baseline migration is idempotent and can be applied
directly. Future schema changes should be added as new Alembic revisions
instead of relying on deleting `database.db`.

### API Usage

Once the server is running, navigate to
`http://localhost:8000/docs` to explore the API using the interactive
Swagger UI. Each route corresponds to a domain entity defined in
`app/models.py` and described in more detail in
`docs/frontend_schema.md`.

#### Example: Creating a Household

```bash
curl -X POST http://localhost:8000/households \
  -H "Content-Type: application/json" \
  -d '{"name": "Andersson Household", "currency": "SEK", "primary_country": "SE"}'
```

The response will include the created household with its assigned ID and
creation timestamp.

## Environment Variables

| Variable           | Default                  | Description                                                       |
|--------------------|--------------------------|-------------------------------------------------------------------|
| DATABASE_URL       | sqlite:///./database.db  | SQLAlchemy database URL                                           |
| APP_HOST           | 0.0.0.0                  | Host used by `python -m app.main`                                 |
| APP_PORT           | 8000                     | Port that the FastAPI server listens on                           |
| UPLOAD_DIR         | ./uploaded_files         | Root directory for uploaded documents                             |
| CORS_ALLOW_ORIGINS | *                        | Comma-separated allowed origins for CORS                          |
| AUTO_CREATE_SCHEMA | true                     | Keeps local/test bootstrap via `create_all`; production should migrate |

## Project Structure

```
economic_system/
├── app/
│   ├── __init__.py
│   ├── main.py        # FastAPI application and routers
│   ├── models.py      # SQLAlchemy ORM models
│   ├── schemas.py     # Pydantic schemas for API IO
│   └── database.py    # Database engine/session configuration
├── docs/
│   ├── HANDOFF_MASTER.md      # Read this first
│   ├── CURRENT_STATE.md       # Strict current implementation truth
│   ├── ARCHITECTURE.md        # Canonical technical architecture
│   ├── FRONTEND_DIRECTION.md  # Frontend product direction
│   └── frontend_schema.md     # API and data schema supplement
├── tests/
│   └── test_smoke.py          # Runtime smoke and workflow verification
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Frontend Integration

Frontend developers should start with `docs/HANDOFF_MASTER.md`,
`docs/CURRENT_STATE.md` and `docs/FRONTEND_DIRECTION.md`, then use
`docs/frontend_schema.md` as the API contract supplement.

## Further Work

* Add authentication and per‑user access control if the deployment moves
  beyond a trusted private network.
* Tighten migration discipline now that Alembic exists and
  `AUTO_CREATE_SCHEMA` still remains available as a local fallback.
* Integrate external AI providers for automatic extraction and
  optimisation generation.
* Add background jobs for reminders and periodic processing.
* Add production logging/metrics if you deploy beyond household scale.

## License

This project is provided as‑is under the MIT license. You are free to
modify and adapt it for your household or organisation. Contributions
are welcome!
