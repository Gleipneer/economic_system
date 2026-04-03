# AGENTS.md

## Cursor Cloud specific instructions

### Overview

This is a **Household Economics Backend** — a single-service FastAPI monolith with an embedded vanilla HTML/CSS/JS frontend. It uses SQLite by default (zero config), so no external database is needed. See `README.md` for full documentation.

### Quick reference

| Action | Command |
|---|---|
| Install deps | `source venv/bin/activate && pip install -r requirements.txt` |
| Run migrations | `source venv/bin/activate && alembic upgrade head` |
| Run tests | `source venv/bin/activate && python -m pytest tests/ -v` |
| Start dev server | `source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload` |
| API docs | `http://localhost:8000/docs` |
| Frontend UI | `http://localhost:8000/` |

### Non-obvious caveats

- **`python3.12-venv`** must be installed at the system level (`apt install python3.12-venv`) before `python3 -m venv` works. The update script handles creating the venv.
- **Pydantic v1** (1.10.9) is used, not v2. Use `.dict()` not `.model_dump()`, and `class Config` not `model_config`.
- The test file `tests/test_smoke.py` reloads app modules via `importlib.reload` to get a fresh DB per test; this means module-level state (settings cache, engine) is reset between test functions. Call `get_settings.cache_clear()` if you need to change settings between reloads.
- The `.env` file is loaded via `python-dotenv`. Copy `.env.example` to `.env` before first run.
- `OPENAI_API_KEY` is optional. AI assistant and ingest routes return 503 gracefully when it is unset. To test live AI flows, set it in `.env`.
- SQLite DB lives at `./database.db` in the project root. Delete it to reset state; `alembic upgrade head` or `AUTO_CREATE_SCHEMA=true` will recreate tables.
- The start script `scripts/start_app.sh` auto-finds a free port if 8000 is occupied.
- **Data-In architecture**: raw input → AI classify/extract → schema validate → review groups → explicit promote → Document + ExtractionDraft. No silent writes to canonical tables. See `docs/AI_DIRECTION.md`.
- **Screenshot/OCR**: `OCRExtractor` protocol exists in `app/ingest_content.py` but is not implemented. `image_placeholder` returns 501.
