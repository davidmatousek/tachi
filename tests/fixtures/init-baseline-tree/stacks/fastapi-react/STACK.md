# Python FastAPI + React Stack

**Target**: Developers building async Python APIs with modern React frontends
**Stack**: FastAPI 0.115+ · SQLAlchemy 2.0+ · asyncpg · Pydantic v2 · React 19 · Vite 6 · TanStack Query 5 · Tailwind CSS 4 · TypeScript 5.5+
**Use Case**: Full-stack web applications with async REST API, PostgreSQL database, and SPA frontend
**Deployment**: Docker Compose (local development), production deployment user-configured
**Philosophy**: Async-first, type-safe at every boundary, security by default, convention over configuration

---

## Architecture Pattern

### Backend — Async REST API

ALWAYS use async route handlers. FastAPI runs on uvicorn's async event loop — synchronous handlers block the entire server.

**Layered architecture** (thin routes → services → ORM):

- **Routes** (`app/api/`): Accept requests, validate via Pydantic, call services, return responses. NEVER put business logic in route handlers.
- **Services** (`app/services/`): Business logic layer. Receives typed inputs, orchestrates ORM operations, returns typed results. NEVER import FastAPI or HTTP concepts.
- **Models** (`app/models/`): SQLAlchemy ORM models representing database tables. NEVER expose ORM models directly in API responses.
- **Schemas** (`app/schemas/`): Pydantic models for request/response serialization. Use schema-per-lifecycle: `Base → Create → Update → Response`.
- **Dependencies** (`app/api/deps.py`): FastAPI `Depends()` callables for shared resources (`get_db`, `get_current_user`).

### Database — SQLAlchemy 2.0 Async + asyncpg

ALWAYS use `create_async_engine` with `asyncpg` driver. Connection string format: `postgresql+asyncpg://user:pass@host/db`.

ALWAYS set `expire_on_commit=False` on `async_sessionmaker`. This is **CRITICAL** — without it, accessing model attributes after commit triggers `MissingGreenlet` errors in async contexts.

ALWAYS use SQLAlchemy 2.0 query syntax (`select()`, `insert()`, `update()`). NEVER use legacy `session.query()`.

**Relationship loading** (in preference order):
1. `selectinload()` — collections (runs a second query)
2. `joinedload()` — scalar relationships (single JOIN)
3. Explicit `await obj.awaitable_attrs.relationship` — when lazy loading is intentional

### Frontend — React SPA with REST API

ALWAYS use functional components with hooks. NEVER use class components.

ALWAYS use TypeScript strict mode. NEVER use `any` — use `unknown` with type narrowing.

**Data flow**:
- **Server state**: TanStack Query v5 for all API data. Use query key factories for type-safe cache management.
- **Client state**: `useState` / `useReducer` for component-local state. Lift shared state to nearest common parent.
- **URL state**: Use URL search params for filterable/shareable UI state.

### API Communication

- REST API with `/api/v1/` prefix. Version the API from the start.
- Frontend fetches via typed client (`src/api/client.ts`) using `VITE_API_URL` environment variable.
- NEVER hardcode API base URLs in frontend code.

---

## File Structure

### Backend

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app factory + lifespan handler
│   ├── config.py            # Pydantic BaseSettings (env vars)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py          # get_db(), get_current_user() dependencies
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── router.py    # APIRouter aggregation
│   ├── core/
│   │   ├── __init__.py
│   │   ├── middleware.py    # CORS, request timing, error handling
│   │   └── exceptions.py   # Custom HTTPException subclasses
│   ├── models/
│   │   └── __init__.py      # SQLAlchemy ORM models
│   ├── schemas/
│   │   └── __init__.py      # Pydantic request/response models
│   ├── services/
│   │   └── __init__.py      # Business logic (no HTTP concerns)
│   └── db/
│       ├── __init__.py
│       ├── session.py       # AsyncEngine + async_sessionmaker + get_db
│       └── base.py          # DeclarativeBase
├── alembic/
│   ├── env.py               # Async Alembic config with run_sync()
│   └── versions/            # Migration files
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Async fixtures (NullPool, rollback, AsyncClient)
│   └── api/
│       └── __init__.py
├── pyproject.toml            # uv config, dependencies, ruff, pytest
└── alembic.ini               # DATABASE_URL from environment
```

### Frontend

```
frontend/
├── src/
│   ├── main.tsx             # React root with QueryClientProvider
│   ├── App.tsx              # App shell with router placeholder
│   ├── app.css              # Tailwind v4 @import + @theme
│   ├── api/
│   │   └── client.ts        # Typed fetch wrapper (VITE_API_URL)
│   ├── components/          # Shared, reusable UI components
│   ├── hooks/               # Custom React hooks
│   ├── pages/               # Route-level components
│   └── types/               # Shared TypeScript types
├── tests/
│   └── setup.ts             # @testing-library/jest-dom import
├── index.html               # HTML entry point
├── vite.config.ts           # Tailwind v4 plugin, path alias, test config
├── tsconfig.json            # Strict mode, path aliases
└── package.json             # Dependencies and scripts
```

### Root

```
docker-compose.yml            # PostgreSQL 16, backend, frontend services
.env.example                  # All env vars with development defaults
```

---

## Naming Conventions

| Category | Convention | Example |
|----------|-----------|---------|
| Python modules | snake_case `.py` | `user_service.py` |
| Python classes | PascalCase | `UserCreate`, `AsyncSession` |
| Python functions/vars | snake_case | `get_current_user`, `db_session` |
| Python constants | UPPER_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_PAGE_SIZE` |
| React components | PascalCase `.tsx` | `UserProfile.tsx` |
| React hooks | `use` prefix, camelCase `.ts` | `useAuth.ts`, `useUsers.ts` |
| TypeScript modules | camelCase `.ts` | `client.ts`, `queryKeys.ts` |
| TypeScript types/interfaces | PascalCase | `UserResponse`, `ApiError` |
| TypeScript variables | camelCase | `currentUser`, `queryClient` |
| CSS files | kebab-case `.css` | `app.css` |
| Database tables | snake_case, plural | `users`, `user_profiles` |
| Database columns | snake_case | `created_at`, `is_active` |
| ORM models | PascalCase, singular | `User`, `UserProfile` |
| Pydantic schemas | PascalCase, lifecycle suffix | `UserBase`, `UserCreate`, `UserResponse` |
| API route prefixes | kebab-case, plural | `/api/v1/users`, `/api/v1/auth` |
| Environment variables | UPPER_SNAKE_CASE | `DATABASE_URL`, `VITE_API_URL` |
| Test files | same name + `.test` suffix | `test_user_service.py`, `App.test.tsx` |
| Alembic migrations | auto-generated with description | `001_create_users_table.py` |

---

## Security Patterns

### OWASP Top 10 Mitigations

**A01 — Broken Access Control**:
- ALWAYS use `Depends(get_current_user)` on every route that requires authentication.
- ALWAYS verify resource ownership before returning data (`user.id == resource.owner_id`).
- NEVER rely on frontend-only route guards for access control.

**A02 — Cryptographic Failures**:
- ALWAYS hash passwords with Argon2 via `passlib[argon2]`. NEVER use bcrypt, MD5, or SHA.
- ALWAYS store JWT tokens in `httpOnly` cookies. NEVER store tokens in `localStorage` or `sessionStorage`.
- ALWAYS use short-lived access tokens (15 min) with refresh token rotation.
- NEVER log tokens, passwords, or PII.

**A03 — Injection**:
- ALWAYS use SQLAlchemy ORM with parameterized queries via asyncpg. ORM prevents SQL injection by default.
- NEVER use `text()` with string interpolation. Use bound parameters: `text("SELECT ... WHERE id = :id").bindparams(id=val)`.
- ALWAYS validate all inputs through Pydantic models at the API boundary.

**A04 — Insecure Design**:
- ALWAYS separate public and authenticated route groups with explicit dependency chains.
- ALWAYS implement rate limiting on authentication endpoints.

**A05 — Security Misconfiguration**:
- ALWAYS set `extra="forbid"` on Pydantic models to reject unknown fields.
- ALWAYS configure CORS with explicit origins. NEVER use `allow_origins=["*"]` with `allow_credentials=True`.
- ALWAYS add security headers: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Strict-Transport-Security`.

**A06 — Vulnerable Components**:
- ALWAYS pin dependency versions in `pyproject.toml` and `package.json`.
- ALWAYS run `uv audit` and `npm audit` before releases.

**A07 — Authentication Failures**:
- NEVER expose user enumeration via different error messages for "wrong email" vs "wrong password".
- ALWAYS return generic "Invalid credentials" for all auth failures.

**A08 — Data Integrity Failures**:
- ALWAYS validate JWT signatures server-side. NEVER trust client-provided tokens without verification.
- ALWAYS use `python-jose[cryptography]` for JWT operations.

**A09 — Logging & Monitoring**:
- ALWAYS use structured logging (JSON) for authentication events and error responses.
- NEVER log request bodies containing passwords or tokens.

**A10 — Server-Side Request Forgery**:
- ALWAYS validate and allowlist URLs before making server-side HTTP requests.
- NEVER pass user-provided URLs directly to `httpx` without validation.

### Frontend Security

- React escapes JSX output by default. NEVER use `dangerouslySetInnerHTML` with user content.
- ALWAYS use `SameSite=Strict` or `SameSite=Lax` with `Secure` flag on auth cookies.
- ALWAYS configure Content-Security-Policy headers.

---

## Coding Standards

### Python — Always

- **Async route handlers** — every FastAPI route function MUST be `async def`.
- **Pydantic models for all I/O** — every request body, response, and config uses Pydantic.
- **Dependency injection** — use `Depends()` for database sessions, auth, and shared resources.
- **Service layer** — extract business logic into `services/`. Route handlers call services, never ORM directly.
- **Schema-per-lifecycle** — `Base → Create → Update → Response` pattern for Pydantic schemas.
- **`from_attributes=True`** on response schemas for ORM-to-Pydantic conversion.
- **`expire_on_commit=False`** on `async_sessionmaker` — prevents `MissingGreenlet` errors.
- **SQLAlchemy 2.0 syntax** — `select()`, `insert()`, `update()`, `delete()`. Never `session.query()`.
- **`selectinload()`** for eager loading collections. `joinedload()` for scalar relationships.
- **Typed returns** — all service functions have explicit return type annotations.
- **Pydantic BaseSettings** for configuration — loads from environment variables and `.env` files.
- **uv** for package management — `uv sync`, `uv run`, `uv add`.
- **Ruff** for linting and formatting — single tool, Rust-based, replaces Flake8 + Black + isort.
- **Alembic** for database migrations — async configuration with `run_sync()`.

### Python — Never

- Synchronous route handlers (`def` instead of `async def`).
- Legacy `session.query()` syntax (SQLAlchemy 1.x).
- `lazy="select"` on relationships in async context (triggers blocking implicit IO).
- Business logic in route handlers (violates separation of concerns).
- `from sqlalchemy.orm import Session` (use `AsyncSession` exclusively).
- `pip install` or `poetry` (use `uv` exclusively).
- Global mutable state in service modules.
- `text()` with f-strings or `.format()` for SQL queries.

### React/TypeScript — Always

- **TypeScript strict mode** — `"strict": true` in `tsconfig.json`.
- **Functional components** — arrow functions or function declarations with typed props.
- **Explicit prop types** — define `interface Props` per component. NEVER use `React.FC<>`.
- **TanStack Query v5** for all server state — query key factories with hierarchical invalidation.
- **`gcTime`** (not `cacheTime`) — v5 renamed this option.
- **Tailwind CSS v4** — use `@import "tailwindcss"` and `@theme` directive. No `tailwind.config.js`.
- **`bg-linear-to-*`** for gradients (v4 renamed from `bg-gradient-to-*`).
- **CSS variable syntax** — `bg-(--var)` not `bg-[--var]` (v4 parenthesis syntax).
- **Named exports** for all modules.
- **Path aliases** — `@/` maps to `src/` via Vite config and `tsconfig.json`.
- **Biome** for linting and formatting — replaces ESLint + Prettier.
- **`VITE_API_URL`** for API base URL — NEVER hardcode API URLs.

### React/TypeScript — Never

- `React.FC<Props>` — use explicit function signatures.
- `any` type — use `unknown` with type narrowing.
- `useEffect` for data fetching — use TanStack Query.
- Class components.
- CSS Modules, styled-components, or inline styles — Tailwind utilities only.
- Barrel files (`index.ts`) in large directories — import from source modules directly.
- `enum` — use string union types (`type Status = 'active' | 'inactive'`).
- `localStorage` for tokens — use `httpOnly` cookies.
- `tailwind.config.js` — use CSS-first `@theme` directive (Tailwind v4).
- `bg-gradient-to-*` — renamed to `bg-linear-to-*` in v4.
- `cacheTime` in TanStack Query — renamed to `gcTime` in v5.

---

## Testing Conventions

<!-- BEGIN: aod-test-contract -->
```yaml
test_command: "pytest && npm --prefix frontend run test"
e2e_command: "npm --prefix frontend run test:e2e"
test_paths:
  - "backend/tests/"
  - "frontend/e2e/"
  - "frontend/tests/"
  - "**/*.test.tsx"
  - "**/*.spec.tsx"
```
<!-- END: aod-test-contract -->

### Backend — pytest + pytest-asyncio

**Configuration** (`pyproject.toml`):
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
```

**Fixture pattern** (three-tier: engine → session → client):
1. **Engine**: `create_async_engine` with `NullPool` — prevents connection pool interference between tests.
2. **Session**: `async_sessionmaker` with transaction rollback — no test data persists.
3. **Client**: `httpx.AsyncClient` with `ASGITransport(app=app)` — tests the full request pipeline.

**Rules**:
- ALWAYS use `NullPool` for test engines — connection pooling breaks function-scoped fixtures.
- ALWAYS use `app.dependency_overrides` to swap `get_db` in tests. ALWAYS call `.clear()` after each test.
- ALWAYS test both success and error paths for every endpoint.
- NEVER connect to a shared database in tests — use function-scoped create/drop.

**Test organization**:
- `tests/conftest.py` — shared fixtures (engine, session, client).
- `tests/api/` — endpoint integration tests via `AsyncClient`.
- `tests/services/` — service layer unit tests with mocked sessions.

### Frontend — Vitest + React Testing Library

**Configuration** (`vite.config.ts`):
```typescript
test: {
  environment: "jsdom",
  globals: true,
  setupFiles: ["./tests/setup.ts"],
}
```

**Rules**:
- ALWAYS test behavior and user interactions, NEVER test implementation details.
- ALWAYS query by accessible roles (`getByRole`), labels (`getByLabelText`), or text (`getByText`).
- NEVER query by CSS class or test ID unless no accessible query exists.
- ALWAYS wrap TanStack Query hooks in `QueryClientProvider` with `retry: false` for tests.
- ALWAYS use `userEvent` (not `fireEvent`) for simulating user interactions.

**Hook testing**: Use `renderHook` from `@testing-library/react` for custom hook tests.

### Coverage

- Backend: enforce minimum 80% line coverage on `app/services/` and `app/api/`.
- Frontend: test critical interactions, not markup. No mandatory coverage thresholds on UI components.

---

## Dependencies

### Backend (pyproject.toml)

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | `>=0.115` | Async web framework |
| `sqlalchemy[asyncio]` | `>=2.0` | Async ORM |
| `asyncpg` | `>=0.30` | PostgreSQL async driver |
| `pydantic-settings` | `>=2.0` | Environment configuration |
| `alembic` | `>=1.13` | Database migrations |
| `passlib[argon2]` | `>=1.7` | Password hashing (Argon2) |
| `python-jose[cryptography]` | `>=3.3` | JWT operations |
| `httpx` | `>=0.27` | Async HTTP client + testing |

**Dev extras**: `pytest`, `pytest-asyncio`, `pytest-cov`, `ruff`, `mypy`

### Frontend (package.json)

| Package | Version | Purpose |
|---------|---------|---------|
| `react` / `react-dom` | `^19.0.0` | UI library |
| `@tanstack/react-query` | `^5.0.0` | Server state management |
| `tailwindcss` | `^4.0.0` | Utility-first CSS |
| `@tailwindcss/vite` | `^4.0.0` | Vite plugin for Tailwind v4 |
| `typescript` | `^5.5.0` | Type safety |

**Dev dependencies**: `vite`, `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/user-event`, `jsdom`, `@biomejs/biome`
