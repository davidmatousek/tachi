# DevOps — Python FastAPI + React (Local / SQLite) Supplement

## Stack Context

Local-first development with zero external dependencies. FastAPI backend (uvicorn ASGI server) with SQLite database (WAL mode), React frontend (Vite dev server). `uv` for Python dependency management, npm for frontend dependencies. No Docker required for development. Backend serves async REST API on uvicorn with `--reload` for development. Frontend connects to backend via `VITE_API_URL` environment variable. Alembic for database migrations (async configuration, batch mode for SQLite). `.env.example` documents all required environment variables with development defaults.

## Conventions

- ALWAYS ensure the SQLite data directory exists before starting the backend -- `mkdir -p data/`
- ALWAYS use `uv sync` to install backend dependencies and `npm install` for frontend -- no Docker needed
- ALWAYS run `cp .env.example .env` before first start -- the app has sensible defaults but `.env` documents the contract
- ALWAYS run `uv run alembic upgrade head` before starting the backend -- ensures schema is current
- ALWAYS use `uv run uvicorn app.main:app --reload` for local development -- `--reload` watches for file changes
- ALWAYS use uvicorn with `--workers N` (2x CPU cores + 1) for production-like environments -- never use `--reload` in production
- ALWAYS configure all services via environment variables loaded from `.env` -- use Pydantic `BaseSettings` on the backend
- ALWAYS expose a `/health` endpoint on the backend that checks database connectivity -- used by monitoring and uptime checks
- ALWAYS use `VITE_API_URL` to configure the frontend-to-backend connection
- ALWAYS back up the SQLite database file before destructive operations -- `cp data/app.db data/app.db.bak`
- ALWAYS set appropriate file permissions on the SQLite database (0600) in shared environments
- ALWAYS include `data/` in `.gitignore` -- database files should never be committed

## Anti-Patterns

- NEVER require Docker for basic local development -- SQLite eliminates the PostgreSQL dependency
- NEVER use `pip install` or `pip freeze` -- use `uv sync --frozen` for deterministic installs
- NEVER hardcode database paths, secrets, or API URLs -- all configuration through environment variables
- NEVER commit `.env` files to git -- commit `.env.example` with placeholder values as documentation
- NEVER skip database migrations before starting the app -- stale schemas cause silent data corruption
- NEVER delete the SQLite database file without running `alembic downgrade base` first -- prefer clean migration reversal
- NEVER use `docker-compose.yml` for production deployment -- it is strictly for local development if used at all
- NEVER ignore `SQLITE_BUSY` errors -- they indicate the busy_timeout is too low or a long-running write lock exists

## Guardrails

- All configuration via environment variables: `DATABASE_URL`, `VITE_API_URL`, `SECRET_KEY`, `CORS_ORIGINS`
- `.env` files NEVER committed to git -- `.env.example` is the documentation contract
- Backend startup: `cd backend && uv run alembic upgrade head && uv run uvicorn app.main:app --reload`
- Frontend startup: `cd frontend && npm run dev`
- Database file location: `data/app.db` (relative to backend working directory)
- All shell scripts in the project MUST be bash 3.2 compatible (macOS ships bash 3.2.57 due to GPLv3 licensing)
- Backend health check: `GET /health` returns `200` with database connectivity status
- SQLite PRAGMAs (WAL mode, foreign keys, busy_timeout) are set automatically via engine event listener
- Backend production command: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers N`
- Frontend production build: `npm run build` outputs static assets -- served by nginx or CDN, not Vite dev server
