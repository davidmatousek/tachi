# Code Reviewer — Python FastAPI + React Supplement

## Stack Context

Dual-language stack: Python 3.12+ backend, TypeScript 5.5+ frontend. Backend: FastAPI 0.115+, SQLAlchemy 2.0 async with asyncpg, Pydantic v2, Alembic migrations, uv package manager, Ruff linting/formatting, pytest + pytest-asyncio. Frontend: React 19, Vite 6, TanStack Query v5, Tailwind CSS v4 (CSS-first config), Biome linting/formatting. REST API with `/api/v1/` prefix. Docker Compose for local development.

## Conventions

### Python Review Checklist

- ALWAYS verify every route handler is `async def`; flag synchronous `def` handlers as they block the uvicorn event loop
- ALWAYS verify `Depends()` usage for database sessions (`get_db`), authentication (`get_current_user`), and shared resources; flag direct instantiation
- ALWAYS verify business logic lives in `app/services/`; flag any business logic in route handlers
- ALWAYS verify schema-per-lifecycle pattern: `Base -> Create -> Update -> Response`; flag single schemas used for both request and response
- ALWAYS verify `expire_on_commit=False` on `async_sessionmaker`; missing this causes `MissingGreenlet` errors in async contexts
- ALWAYS verify SQLAlchemy 2.0 `select()` syntax; flag any `session.query()` usage
- ALWAYS verify `from_attributes=True` on response schemas for ORM-to-Pydantic conversion
- ALWAYS verify `selectinload()` for collections and `joinedload()` for scalar relationships; flag `lazy="select"` in async context
- ALWAYS verify Pydantic `BaseSettings` for configuration; flag hardcoded config values
- ALWAYS verify Ruff passes with zero errors before approval
- ALWAYS verify `NullPool` in test engine fixtures; connection pooling breaks function-scoped test isolation

### React/TypeScript Review Checklist

- ALWAYS verify TypeScript strict mode (`"strict": true`); flag any `any` type as WARNING
- ALWAYS verify explicit prop interfaces per component; flag `React.FC<>` usage
- ALWAYS verify TanStack Query v5 for all server state with query key factories; flag `useEffect` for data fetching
- ALWAYS verify `gcTime` (not `cacheTime`); v5 renamed this option
- ALWAYS verify Tailwind v4 patterns: `@theme` directive (not `tailwind.config.js`), `bg-linear-to-*` (not `bg-gradient-to-*`), `bg-(--var)` (not `bg-[--var]`)
- ALWAYS verify named exports for all modules; flag default exports
- ALWAYS verify path aliases `@/` for imports from `src/`; flag relative path traversals (`../../`)
- ALWAYS verify Biome passes with zero errors before approval
- ALWAYS verify `userEvent` (not `fireEvent`) in tests; verify accessible queries (`getByRole`, `getByLabelText`)

## Anti-Patterns

Flag these as findings in every review:

- Synchronous route handlers (`def` instead of `async def`) in FastAPI — CRITICAL
- Missing `Depends(get_current_user)` on routes handling protected data — CRITICAL
- `text()` with f-strings or `.format()` for SQL (injection risk) — CRITICAL
- `allow_origins=["*"]` with `allow_credentials=True` in CORS config — CRITICAL
- Tokens stored in `localStorage` or `sessionStorage` — CRITICAL
- Missing Pydantic validation on request inputs — CRITICAL
- Legacy `session.query()` syntax (SQLAlchemy 1.x) — WARNING
- Business logic in route handlers instead of service layer — WARNING
- Missing `expire_on_commit=False` on async session maker — WARNING
- `any` type usage anywhere in TypeScript code — WARNING
- `useEffect` for data fetching instead of TanStack Query — WARNING
- CSS Modules, styled-components, or inline styles instead of Tailwind — WARNING
- `tailwind.config.js` instead of CSS-first `@theme` directive — WARNING
- Barrel files (`index.ts`) in large directories — WARNING
- `pip install` or `poetry` instead of `uv` — WARNING
- `enum` in TypeScript instead of string union types — WARNING
- `cacheTime` instead of `gcTime` in TanStack Query v5 — SUGGESTION
- `bg-gradient-to-*` instead of `bg-linear-to-*` (Tailwind v4) — SUGGESTION
- Missing `extra="forbid"` on Pydantic input schemas — SUGGESTION

## Guardrails

- Review priority: Security (auth/injection/CORS/tokens) > Data integrity (async safety/validation/queries) > Architecture (route-service-model separation) > Convention compliance > Style
- Every PR touching routes: verify (1) `async def` (2) `Depends()` for auth/db (3) Pydantic input validation (4) service layer delegation
- Every PR touching models/db: verify (1) 2.0 `select()` syntax (2) `expire_on_commit=False` (3) eager loading strategy (4) no `lazy="select"` in async
- Every PR touching schemas: verify (1) schema-per-lifecycle (2) `from_attributes=True` on responses (3) `extra="forbid"` on inputs
- Every PR touching frontend components: verify (1) strict TypeScript (2) no `React.FC` (3) TanStack Query for server state (4) Tailwind v4 syntax
- Every PR touching tests: verify (1) `NullPool` on backend engines (2) `dependency_overrides.clear()` after each test (3) `QueryClientProvider` with `retry: false` on frontend
- Ruff (backend) and Biome (frontend) must both pass with zero errors before approval
- `uv audit` and `npm audit` must report zero critical or high vulnerabilities before approval
