# Runbook & AI Handover Instructions

This runbook provides operational guidance for maintaining and extending
the household economics backend. It is intended for the next AI agent
or human operator who will work on this codebase. Follow the steps
below to ensure continuity of service and smooth integration of new
features.

## 1. Prerequisites

* **Environment:** Ubuntu 22.04 or later (tested), Python 3.11,
  Docker and Docker Compose (for containerised deployment).
* **Network:** The backend is expected to run inside a private
  network (e.g. via [Tailscale](https://tailscale.com/)). The host
  machine should have access to this network and a stable internet
  connection if external services (e.g. AI APIs, benchmarking data)
  are used.

## 2. Starting the Service

### Local Development

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd economic_system
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Set environment variables (if needed):
   ```bash
   export DATABASE_URL=sqlite:///./database.db
   ```
4. Start the FastAPI server:
   ```bash
   uvicorn economic_system.app.main:app --reload
   ```
5. Access the interactive API docs at `http://localhost:8000/docs`.

### Docker Deployment

1. Build and run the container using Docker Compose:
   ```bash
   docker-compose up -d --build
   ```
2. Verify that the container is running:
   ```bash
   docker ps
   ```
3. Access the API via the host port (default `8000`). If the
   service is exposed over Tailscale, use the machine's Tailscale IP
   instead of `localhost`.

### Tailscale Exposure

To expose the backend on your Tailscale network:

1. Install Tailscale on the host machine and authenticate it. See
   [Tailscale docs](https://tailscale.com/kb/1029/install/) for
   instructions.
2. Run `tailscale up` and note the assigned Tailscale IP address.
3. When running the backend (via Docker or locally), bind it to
   `0.0.0.0` (already configured in the Dockerfile). The service will
   then be reachable at `http://<tailscale-ip>:8000` from other nodes
   on your Tailscale network.

## 3. Database Operations

### Initialisation

Tables are created automatically at application startup via
`database.init_db()`. No manual migration is required for the initial
schema. To reset the database during development, delete `database.db`
and restart the server.

### Migrations

If you need to alter the schema (e.g. add a column), consider
introducing a migration tool such as [Alembic](https://alembic.sqlalchemy.org/).
Outline the migration steps in this runbook and update the
README accordingly.

### Backup & Restore

Backing up the SQLite database is as simple as copying the
`database.db` file. For example:

```bash
cp database.db backup_$(date +%Y%m%d_%H%M%S).db
```

To restore, stop the server, replace `database.db` with your backup,
and restart the server. When using PostgreSQL or another RDBMS, use
the respective database's backup tools (`pg_dump`, `mysqldump`, etc.).

## 4. AI Integration

While the current repository does not include AI functionality, it is
designed to accommodate it. Follow these guidelines when adding AI:

1. **Module Structure:** Create a new package, e.g.
   `economic_system/ai`, to house AI-related code. Keep it isolated
   from core models and API routes.
2. **Function Calling:** If using OpenAI's function calling features,
   define strict JSON schemas and validate all responses before
   persisting any data. Only write to ``ExtractionDraft`` or
   ``OptimizationOpportunity`` tables automatically.
3. **Draft Approval Workflow:** Implement endpoints and UI flows for
   users to approve, revise or reject AI proposals. Data should be
   copied into canonical tables only upon approval.
4. **External Benchmarks:** Load benchmarking data (e.g. from
   Konsumentverket or Elpriskollen) into separate reference tables or
   cache them in memory. Do not hard‑code external values.
5. **Model Selection:** Choose appropriate OpenAI models (e.g.
   `gpt-5.4` for complex tasks, `gpt-5.4-mini` for high volume) and
   document your decisions in a dedicated AI design doc.

## 5. Testing

Testing is critical for reliability and regression prevention. A
`tests/` directory is provided for your convenience but is currently
empty. To get started:

1. Install `pytest` in your virtual environment (`pip install pytest`).
2. Create test modules under `tests/` (e.g. `test_models.py`, `test_api.py`).
3. Use FastAPI's `TestClient` to simulate requests against the API.
4. Run tests via `pytest` and ensure they pass before deploying changes.

## 6. Updating & Contributing

When modifying the codebase:

* Follow the existing project structure. Add new models and schemas
  alongside the existing ones and wire them into `main.py`.
* Update the documentation in `docs/` to reflect schema or API
  changes.
* Increment the application version in `main.py` if you make
  backwards‑incompatible changes.
* Ensure migrations are created when changing the database schema.
* Run tests and update/add new ones as necessary.

## 7. Troubleshooting

| Problem                           | Solution                                                          |
|----------------------------------|--------------------------------------------------------------------|
| API returns 500 errors            | Check server logs for stack traces. Validate request payloads.     |
| Changes not persisted             | Verify that `db.commit()` is called and that the DB file is
                                      writable.                                                         |
| Unable to connect over Tailscale | Ensure the service binds to `0.0.0.0` and firewall rules allow
                                      inbound traffic on the port. Check Tailscale ACLs.                |
| Docker build fails                | Verify that `requirements.txt` is valid and that there is network
                                      connectivity to download dependencies.                           |
| Tables missing                    | Confirm that `init_db()` runs on startup. Delete `database.db`
                                      and restart if schema changes require a reset.                    |

## 8. Handover Checklist

Before handing over to another AI agent or developer, ensure that:

1. All code changes are committed and pushed to version control.
2. The database is backed up if it contains important data.
3. The README and documentation are up to date.
4. All tests (if any) pass successfully.
5. There is a clear next step or TODO list describing outstanding
   tasks or feature requests.

By following this runbook, the next operator will be able to start,
maintain and extend the household economics backend with minimal
friction. Good luck!