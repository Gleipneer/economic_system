# Household Economics Backend

## Overview

This repository contains the **backend** component for a modular household
economics system. It is designed to act as the single source of truth for
financial data used by a household, including income sources, loans, recurring
costs, subscription contracts, insurance policies, vehicles, assets,
housing scenarios and various derived reports. The backend exposes a
RESTful API built with **FastAPI** and persists data using **SQLAlchemy**
to a relational database (SQLite by default). A modern frontend can
consume this API to present forms, dashboards and reports to end users.

The architecture separates concerns into layers:

| Layer                | Responsibility                                                      |
|----------------------|--------------------------------------------------------------------|
| Database (SQL)       | Persist domain entities in a relational model                       |
| Backend (FastAPI)    | Provide CRUD operations and deterministic calculations              |
| Document Ingestion   | Store raw documents (PDF, images) and create extraction drafts      |
| AI Analysis (future) | Extract structured data, suggest optimisations, simulate scenarios |
| Frontend (external)  | Present UI forms, dashboards and drive user workflows              |

This repository deliberately **excludes** any UI/frontend implementation so
that different teams can build a web, mobile or desktop client of their
choice. A separate document (`docs/frontend_schema.md`) describes the
available API endpoints and data schema for use by frontend developers.

## Features

* **Robust Data Model** – SQLAlchemy models cover the full range of domain
  concepts: households, persons, incomes, loans, recurring costs,
  subscription contracts, insurance policies, vehicles, assets, housing
  scenarios, documents, drafts, optimisation opportunities, scenarios,
  scenario results and report snapshots.
* **CRUD API** – Each entity exposes REST endpoints for listing,
  creating, retrieving, updating and deleting records. The API returns
  Pydantic schemas for type safety and validation.
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

### Running Locally without Docker

```bash
git clone <repository-url>
cd economic_system
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn economic_system.app.main:app --reload
```

By default the application writes its SQLite database to `database.db` in
the project root. Set `DATABASE_URL` in your shell to point at another
database if needed.

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

| Variable       | Default                | Description                                                     |
|----------------|------------------------|-----------------------------------------------------------------|
| DATABASE_URL   | sqlite:///./database.db | SQLAlchemy database URL                                        |
| APP_PORT       | 8000                   | Port that the FastAPI server listens on (via Dockerfile)        |

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
│   ├── architecture.md     # High‑level system architecture
│   ├── frontend_schema.md  # API and data schema for frontend integration
│   └── runbook.md          # Operational runbook and AI handover instructions
├── tests/ (optional)       # Space for backend unit tests (not populated)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Frontend Integration

Frontend developers should consult `docs/frontend_schema.md` for a
detailed description of the API contracts. The backend enforces
validation of incoming data and returns well‑defined JSON responses.
Authentication, authorisation and UI logic are intentionally not
implemented here; they belong in the frontend and deployment layers.

## Further Work

* Implement authentication and per‑user access control.
* Add business logic for calculations (e.g. monthly net, stress tests).
* Integrate document parsing and AI components for automatic data
  extraction and optimisation suggestions.
* Write unit and integration tests (see the `tests` directory).
* Implement background jobs for reminders and periodic tasks.

## License

This project is provided as‑is under the MIT license. You are free to
modify and adapt it for your household or organisation. Contributions
are welcome!
