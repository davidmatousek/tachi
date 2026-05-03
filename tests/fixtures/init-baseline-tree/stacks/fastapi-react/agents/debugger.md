# Debugger — Python FastAPI + React Supplement

## Stack Context

Backend — FastAPI 0.115+ on uvicorn async event loop, SQLAlchemy 2.0 async ORM with asyncpg driver, Pydantic v2 for validation, pytest + pytest-asyncio for test execution, Alembic for migrations. Frontend — React 19 SPA with Vite 6 HMR, TanStack Query v5 with DevTools, TypeScript 5.5+ strict mode. Two separate processes: uvicorn (backend) and Vite dev server (frontend) communicating over REST at `/api/v1/`.

## Conventions

### Backend Debugging

- ALWAYS check the simplest cause first: missing env vars in `.env`, wrong import paths, dependency version mismatches in `uv.lock`
- ALWAYS use `breakpoint()` (Python 3.7+ built-in) for interactive debugging — never `import pdb; pdb.set_trace()`
- ALWAYS be aware that `breakpoint()` pauses the entire uvicorn event loop — set breakpoints in service layer, not in route handlers serving concurrent requests
- ALWAYS use `pytest -x --tb=short` for fail-fast debugging with concise tracebacks — add `-v` only when test names are ambiguous
- ALWAYS enable SQL logging with `echo=True` on `create_async_engine` when diagnosing query issues — remove before committing
- ALWAYS check `expire_on_commit=False` on `async_sessionmaker` FIRST when encountering `MissingGreenlet` errors — this is the cause 90% of the time
- ALWAYS check `NullPool` is set on test engines when encountering connection pool exhaustion or hanging tests
- ALWAYS check session scope (function vs module) when encountering `Session is already closed` or `detached instance` errors
- ALWAYS use `pytest --fixtures` to inspect available fixtures when test setup is unclear
- ALWAYS use `httpx.AsyncClient` with `app=app` for debugging integration tests — never `requests` or synchronous `TestClient` in async test suites

### Frontend Debugging

- ALWAYS use React DevTools Components tab to inspect component tree, props, and state before reading source code
- ALWAYS use TanStack Query DevTools to inspect cache state, query status, and stale/fresh timing before assuming a fetch bug
- ALWAYS use browser Network tab filtered to `Fetch/XHR` to verify actual API request/response payloads and status codes
- ALWAYS use Vite's error overlay for build and transform errors — it shows the exact file and line
- ALWAYS add React error boundaries (`ErrorBoundary` components) to isolate rendering crashes to the failing subtree
- ALWAYS check the browser console for TypeScript runtime errors and React strict mode double-render warnings
- ALWAYS verify `VITE_API_URL` is set correctly in `.env` when API calls return network errors or CORS failures

### Cross-Stack Debugging

- ALWAYS check CORS configuration (`allow_origins`, `allow_credentials`, `allow_methods`) when the frontend receives opaque responses or preflight failures
- ALWAYS compare the Pydantic response schema with the TypeScript interface when data appears missing or malformed in the frontend
- ALWAYS verify cookie attributes (`httpOnly`, `SameSite`, `Secure`, `Path`, `Domain`) in the browser Application tab when auth tokens are not sent

## Anti-Patterns

- NEVER use synchronous `pdb` commands (`next`, `step`) in async coroutines without understanding you are stepping through the event loop, not just your code
- NEVER leave `print()`, `console.log()`, `echo=True`, or `breakpoint()` statements in committed code — use structured logging (`loguru`/`logging`) instead
- NEVER catch broad `except Exception` during debugging — it hides the root cause; catch specific exceptions or use `except Exception as e: logger.exception(e); raise`
- NEVER ignore TypeScript type errors as "not runtime relevant" — strict mode errors frequently predict runtime `undefined` access and missing property bugs
- NEVER mock away the bug instead of fixing it — if a test passes only because you mocked the failing dependency, the bug still exists in production
- NEVER assume a 500 error is a backend bug without checking the uvicorn logs — it may be a database connection issue, missing migration, or env var
- NEVER debug CORS issues by setting `allow_origins=["*"]` — find and fix the actual origin mismatch

## Guardrails

### Async Pitfall Checklist (check in this order)

1. **MissingGreenlet** — check `expire_on_commit=False` on `async_sessionmaker`, then check for synchronous attribute access on expired ORM instances
2. **Connection pool exhaustion** — check `NullPool` on test engines, check `pool_size` and `max_overflow` on production engines, check for unclosed sessions
3. **Session already closed** — check fixture scope matches test expectations, check `async with session` context manager usage
4. **CORS errors** — check `allow_origins` contains the exact frontend origin (scheme + host + port), check `allow_credentials=True` if using cookies
5. **422 Unprocessable Entity** — check Pydantic schema field names and types match the request payload exactly; check `extra="forbid"` rejection

### Diagnostic Order of Operations

1. Read the full error message and traceback — do not skip lines
2. Check environment: env vars loaded, database running, migrations applied, both servers started
3. Reproduce with the smallest possible input
4. Isolate: backend or frontend? Use Network tab to determine which side owns the bug
5. Add targeted logging or breakpoints at the boundary where behavior diverges from expectation
6. Fix, verify, remove debug instrumentation, run full test suite
