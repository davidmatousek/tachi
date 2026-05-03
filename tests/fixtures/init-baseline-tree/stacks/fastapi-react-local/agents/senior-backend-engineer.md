# Senior Backend Engineer — Python FastAPI + React (Local / SQLite) Supplement

## Stack Context

FastAPI 0.115+ async REST API, SQLAlchemy 2.0 async ORM with aiosqlite driver, Pydantic v2 for request/response schemas and settings, Alembic for async migrations (batch mode), uv package manager, Ruff for linting/formatting, pytest + pytest-asyncio for testing, httpx AsyncClient for integration tests. SQLite with WAL mode for local-first development.

## Conventions

- ALWAYS use `async def` for every FastAPI route handler -- synchronous handlers block the entire uvicorn event loop
- ALWAYS inject dependencies via `Depends()` -- database sessions (`get_db`), auth (`get_current_user`), and shared resources
- ALWAYS follow the layered pattern: routes call services, services call ORM -- routes NEVER import SQLAlchemy directly
- ALWAYS use schema-per-lifecycle for Pydantic models: `Base` (shared fields) -> `Create` (input) -> `Update` (partial input) -> `Response` (output with `from_attributes=True`)
- ALWAYS set `expire_on_commit=False` on `async_sessionmaker` -- without this, attribute access after commit raises `MissingGreenlet`
- ALWAYS use SQLAlchemy 2.0 query syntax: `select()`, `insert()`, `update()`, `delete()` with `await session.execute()`
- ALWAYS use `selectinload()` for eager loading collections and `joinedload()` for scalar relationships
- ALWAYS use `sqlite+aiosqlite:///` as the connection string scheme -- never `sqlite://` or `sqlite+pysqlite://`
- ALWAYS enable WAL mode, foreign keys, and busy_timeout via SQLite PRAGMAs on every connection
- ALWAYS use `render_as_batch=True` in Alembic `context.configure()` -- SQLite does not support ALTER COLUMN or DROP COLUMN natively
- ALWAYS use `JSON` column type for structured data -- SQLite stores it as text but SQLAlchemy handles serialization
- ALWAYS set `extra="forbid"` on Pydantic request models to reject unknown fields at the API boundary
- ALWAYS use Pydantic `BaseSettings` with `SettingsConfigDict(env_file=".env")` for configuration -- never read `os.environ` directly
- ALWAYS use `uv sync`, `uv run`, `uv add` for dependency management -- commit `uv.lock` to version control
- ALWAYS run Alembic migrations with async configuration using `run_sync()` in `env.py`
- ALWAYS use typed return annotations on all service functions
- ALWAYS hash passwords with Argon2 via `passlib[argon2]` -- never bcrypt, MD5, or SHA
- ALWAYS store JWT tokens in `httpOnly` cookies with `SameSite=Strict` and `Secure` flags -- never `localStorage`
- ALWAYS use `StaticPool` with `connect_args={"check_same_thread": False}` for in-memory SQLite test engines
- ALWAYS override `get_db` via `app.dependency_overrides` in tests and call `.clear()` after each test

## Anti-Patterns

- NEVER use synchronous `def` route handlers -- they block the async event loop
- NEVER use `session.query()` (SQLAlchemy 1.x syntax) -- use `select()` statements exclusively
- NEVER set `lazy="select"` on relationships in async context -- triggers blocking implicit IO and `MissingGreenlet` errors
- NEVER put business logic in route handlers -- extract to `app/services/` modules that have no FastAPI or HTTP imports
- NEVER import `from sqlalchemy.orm import Session` -- use `AsyncSession` from `sqlalchemy.ext.asyncio` exclusively
- NEVER use `pip install` or `poetry` -- use `uv` exclusively for package management
- NEVER use `text()` with f-strings or `.format()` for SQL queries -- use bound parameters: `text("... WHERE id = :id").bindparams(id=val)`
- NEVER use global mutable state in service modules -- pass state through function arguments or dependency injection
- NEVER expose ORM models directly in API responses -- always serialize through Pydantic response schemas
- NEVER use `allow_origins=["*"]` with `allow_credentials=True` in CORS configuration
- NEVER return different error messages for "wrong email" vs "wrong password" -- always "Invalid credentials"
- NEVER use native `ARRAY` column types -- SQLite does not support them; use `JSON` instead
- NEVER use `ALTER COLUMN` or `DROP COLUMN` in Alembic without batch mode -- SQLite requires `render_as_batch=True`

## Guardrails

- Route handlers: `app/api/v1/` with `APIRouter` per domain (e.g., `users.py`, `auth.py`)
- Service layer: `app/services/{domain}.py` -- no HTTP imports, typed inputs and returns
- ORM models: `app/models/{domain}.py` -- SQLAlchemy `DeclarativeBase` subclasses
- Pydantic schemas: `app/schemas/{domain}.py` -- Base/Create/Update/Response per entity
- Database session: `app/db/session.py` -- `create_async_engine` + `async_sessionmaker` + SQLite PRAGMAs via event listener
- Dependencies: `app/api/deps.py` -- `get_db()`, `get_current_user()`, shared `Depends()` callables
- Configuration: `app/config.py` -- single `Settings(BaseSettings)` class with SQLite default, never scattered `os.getenv()` calls
- Migrations: `alembic/versions/` -- generate with `uv run alembic revision --autogenerate -m "{description}"`
- Tests: `tests/conftest.py` (async fixtures with in-memory SQLite), `tests/api/` (integration), `tests/services/` (unit)
- File organization: file-type based (`models/`, `schemas/`, `services/`), not domain-based directories
- Context budget: this supplement is <=100 lines; defer to STACK.md for architecture and security details
