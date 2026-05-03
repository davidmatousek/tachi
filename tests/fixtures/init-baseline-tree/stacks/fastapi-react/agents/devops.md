# DevOps — Python FastAPI + React Supplement

## Stack Context

Docker Compose for local development with three services: PostgreSQL 16 (database), FastAPI backend (uvicorn ASGI server), React frontend (Vite dev server). `uv` for Python dependency management, npm for frontend dependencies. Backend serves async REST API on uvicorn with `--reload` for development and `--workers N` for production. Frontend connects to backend via `VITE_API_URL` environment variable. Alembic for database migrations (async configuration). `.env.example` documents all required environment variables with development defaults.

## Conventions

- ALWAYS use multi-stage Dockerfiles: build stage installs dependencies, runtime stage copies only artifacts -- keeps production images minimal
- ALWAYS use `uv sync --no-dev --frozen` in production Dockerfiles -- deterministic installs without dev dependencies. NEVER use `pip install -r requirements.txt`
- ALWAYS run containers as a non-root user -- add `USER appuser` after creating the user in the Dockerfile
- ALWAYS define `depends_on` with health checks in `docker-compose.yml` -- backend waits for PostgreSQL, frontend waits for backend
- ALWAYS expose a `/health` endpoint on the backend that checks database connectivity -- used by Docker health checks and monitoring
- ALWAYS use `VITE_API_URL` to configure the frontend-to-backend connection -- set in `docker-compose.yml` environment or `.env`
- ALWAYS use uvicorn with `--reload` in development and `--workers N` (2x CPU cores + 1) in production -- never use `--reload` in production
- ALWAYS configure all services via environment variables loaded from `.env` -- use Pydantic `BaseSettings` on the backend
- ALWAYS use `npm ci` (not `npm install`) in Docker builds -- ensures reproducible installs from lockfile
- ALWAYS run `alembic upgrade head` as a container startup step or init container -- database schema must be current before the app serves traffic
- ALWAYS pin the Python base image to a specific minor version (e.g., `python:3.12-slim`) -- avoid `python:latest`
- ALWAYS include `.dockerignore` excluding `.git/`, `node_modules/`, `__pycache__/`, `.venv/`, `.env`

## Anti-Patterns

- NEVER use `pip install` or `pip freeze` in Dockerfiles -- use `uv sync --frozen` for deterministic, fast installs
- NEVER use single-stage Dockerfiles that include dev dependencies, test files, or build tools in the runtime image
- NEVER set `allow_origins=["*"]` with `allow_credentials=True` in CORS middleware -- specify explicit origins per environment
- NEVER hardcode database connection strings, secrets, or API URLs -- all configuration through environment variables
- NEVER run containers as root -- create and switch to a non-root user in the Dockerfile
- NEVER omit health checks from `docker-compose.yml` -- services must declare health check commands and dependents must use `condition: service_healthy`
- NEVER commit `.env` files to git -- commit `.env.example` with placeholder values as documentation
- NEVER use `docker-compose.yml` for production deployment -- it is strictly for local development. Production deployment is user-configured
- NEVER skip database migrations on container startup -- stale schemas cause silent data corruption or runtime errors
- NEVER use `PYTHONDONTWRITEBYTECODE=0` in containers -- always set `PYTHONDONTWRITEBYTECODE=1` to avoid `__pycache__` bloat

## Guardrails

- All configuration via environment variables: `DATABASE_URL`, `VITE_API_URL`, `JWT_SECRET`, `CORS_ORIGINS`, `NODE_ENV`
- `.env` files NEVER committed to git -- `.env.example` is the documentation contract
- `docker-compose.yml` is for local development only -- production deployment is outside this pack's scope
- All shell scripts in the project MUST be bash 3.2 compatible (macOS ships bash 3.2.57 due to GPLv3 licensing)
- Backend health check: `GET /health` returns `200` with database connectivity status
- Container startup order: PostgreSQL (healthy) -> backend (migrations + serve) -> frontend (dev server)
- Python base image: `python:3.12-slim` pinned to minor version
- Node base image: current LTS pinned to minor version
- Docker build context: `.dockerignore` must exclude `.git/`, `node_modules/`, `__pycache__/`, `.venv/`, `.env`
- Backend production command: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers N`
- Frontend production build: `npm run build` outputs static assets -- served by nginx or CDN, not Vite dev server
