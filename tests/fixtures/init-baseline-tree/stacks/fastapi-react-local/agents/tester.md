# Tester — Python FastAPI + React (Local / SQLite) Supplement

## Stack-Specific E2E Conventions

- **Location**: E2E specs live at `frontend/e2e/*.spec.ts`; shared fixtures at `frontend/e2e/fixtures.ts`; adopter starter templates at `frontend/e2e/_templates/*.template.ts` (excluded from runs via `testIgnore: /\.template\.ts$/`).
- **Fixture pattern**: Playwright `webServer` array form — backend runs `bash -c "alembic upgrade head && uvicorn app.main:app --host 127.0.0.1 --port 8001"`; frontend runs `npm run dev -- --host 127.0.0.1 --port 5173`. Both bind `127.0.0.1` explicitly (not `localhost`) to avoid IPv6 drift on CI.
- **Query precedence**: prefer `getByRole(...)` first, `getByLabel(...)` when role is ambiguous, `getByText(...)` as last resort. Do not start with CSS selectors or `getByTestId`.
- **Flake tolerance**: `retries: 2` is set per the #130 declaration contract. Use Playwright's auto-waiting (`expect(...).toBeVisible()`) and `expect().toPass()` rather than `setTimeout`/`sleep`. Consistent two-retries-to-pass often signals a real race worth fixing upstream.
- **DB isolation**: NO env-var configuration is required. `playwright.config.ts` generates a per-run ephemeral SQLite file at `/tmp/e2e-<uuid>.db` and passes it to the backend as `DATABASE_URL=sqlite+aiosqlite:///${path}`. A fresh UUID per run prevents cross-run state pollution; `globalTeardown` deletes the file (best-effort).
- **Trace redaction**: `fixtures.ts` installs a `page.route()` hook that strips `Authorization` / `Cookie` from requests AND `Set-Cookie` from responses before the trace recorder captures them. PRESERVE this hook — removing it exposes JWTs and session cookies in CI trace artifacts.
- **Adopter templates**: `frontend/e2e/_templates/auth-crud.template.ts` is a copy-ready auth + CRUD reference. Rename the extension to `.spec.ts` and fill in the `TODO` placeholders once your app implements those flows.

## Stack Context

Backend testing with pytest + pytest-asyncio against in-memory SQLite (aiosqlite driver, StaticPool). Frontend testing with Vitest + React Testing Library in jsdom environment. All tests run locally with zero external dependencies -- no Docker, no PostgreSQL, no network services.

## Conventions

- ALWAYS use in-memory SQLite (`sqlite+aiosqlite://`) with `StaticPool` for backend test engines -- fast, auto-cleaned, no file I/O
- ALWAYS set `connect_args={"check_same_thread": False}` on in-memory SQLite test engines -- required for async access across tasks
- ALWAYS use the three-tier fixture pattern: engine (session-scoped) -> session (function-scoped with rollback) -> client (function-scoped with dep override)
- ALWAYS override `get_db` via `app.dependency_overrides` in test client fixtures and call `.clear()` after each test
- ALWAYS test both success and error paths for every endpoint -- include 404, 422, and invalid state transitions
- ALWAYS use `httpx.AsyncClient` with `ASGITransport(app=app)` for backend integration tests -- tests the full request pipeline
- ALWAYS use `asyncio_mode = "auto"` in pytest config -- avoids manual `@pytest.mark.asyncio` on every test
- ALWAYS query by accessible roles (`getByRole`), labels (`getByLabelText`), or text (`getByText`) in frontend tests
- ALWAYS use `userEvent` (not `fireEvent`) for simulating user interactions in React tests
- ALWAYS wrap TanStack Query hooks in `QueryClientProvider` with `retry: false` for frontend tests

## Anti-Patterns

- NEVER use file-backed SQLite for tests -- in-memory is faster and auto-cleans between test sessions
- NEVER use `NullPool` with in-memory SQLite -- in-memory databases are destroyed when the connection closes; use `StaticPool` to share one connection
- NEVER connect to a shared or production database in tests -- always use isolated in-memory fixtures
- NEVER test implementation details in frontend tests -- test behavior and user-visible outcomes
- NEVER query by CSS class or test ID unless no accessible query exists
- NEVER use `fireEvent` when `userEvent` is available -- `userEvent` simulates real browser behavior
- NEVER skip testing error paths -- API error handling is as important as success paths

## Guardrails

- Backend test config: `pyproject.toml` with `asyncio_mode = "auto"` and `asyncio_default_fixture_loop_scope = "function"`
- Backend fixtures: `tests/conftest.py` -- engine, session, client fixtures with in-memory SQLite
- Backend test organization: `tests/api/` (integration via AsyncClient), `tests/services/` (unit with mocked sessions)
- Frontend test config: `vite.config.ts` with `environment: "jsdom"`, `globals: true`, `setupFiles: ["./tests/setup.ts"]`
- Frontend test setup: `tests/setup.ts` imports `@testing-library/jest-dom` for DOM matchers
- Coverage targets: 80%+ on `app/services/` and `app/api/`; no mandatory frontend coverage thresholds
- Test commands: `cd backend && uv run pytest` (backend), `cd frontend && npm run test` (frontend)
