# Repo Map

Canonical status: quick structural map for future humans and AI agents.
Last reviewed: 2026-04-03.

## Read These First

1. `docs/HANDOFF_MASTER.md`
2. `docs/CURRENT_STATE.md`
3. `docs/LOCKED_DECISIONS.md`
4. `docs/ARCHITECTURE.md`
5. `docs/NEXT_ACTION.md`
6. `docs/AINEXTSTEPPATCH.md`

## Top-Level Directories

- `app/`: backend app code and built-in frontend assets
- `alembic/`: database migration environment and revisions
- `docs/`: canonical handoff and architecture documents
- `tests/`: smoke verification
- `uploaded_files/`: local uploaded document storage

## Core Backend Files

- `app/main.py`: primary runtime app and route logic
- `app/models.py`: ORM schema
- `app/schemas.py`: request/response schema
- `app/calculations.py`: deterministic finance math
- `app/ai_services.py`: OpenAI-backed analysis and ingest orchestration
- `app/database.py`: engine/session/bootstrap
- `app/settings.py`: environment-backed configuration

## Core Frontend Files

- `app/static/index.html`: SPA shell
- `app/static/app.js`: active frontend routing, rendering, and API calls
- `app/static/styles.css`: design system and layout

## Schema and Operations Files

- `alembic/env.py`: Alembic environment
- `alembic/versions/20260402_000001_baseline.py`: current baseline migration
- `Dockerfile`: container runtime
- `docker-compose.yml`: local Docker orchestration
- `.env.example`: example runtime and OpenAI configuration
- `scripts/start_app.sh`: preferred local start script
- `requirements.txt`: Python dependencies

## Documentation Files

Canonical docs:

- `docs/HANDOFF_MASTER.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/CURRENT_STATE.md`
- `docs/LOCKED_DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/FRONTEND_DIRECTION.md`
- `docs/AI_DIRECTION.md`
- `docs/RUNTIME_AND_OPERATIONS.md`
- `docs/KNOWN_GAPS_AND_RISKS.md`
- `docs/NEXT_ACTION.md`
- `docs/AINEXTSTEPPATCH.md`
- `docs/REPO_MAP.md`
- `docs/TERMS_AND_MODEL.md`

Supplemental and compatibility docs:

- `docs/frontend_schema.md`
- `docs/SYSTEM_VALIDATION.md`
- lower-case legacy filenames retained as pointers

## Test and Verification Files

- `tests/test_smoke.py`: current smoke suite
- `app/static/system_validation.md`: lightweight frontend-facing pointer to validation markdown

## Files to Read Carefully Before Making Changes

- `app/main.py`
- `app/ai_services.py`
- `app/static/app.js`
- `app/models.py`
- `app/schemas.py`
- `tests/test_smoke.py`

## Files That Can Mislead If Read Alone

- `app/static/server.py`: not the primary runtime path
- `app/system_docs.py`: auxiliary artifact, not the main validation source
- older lower-case docs: retained for compatibility, not the primary handoff source
