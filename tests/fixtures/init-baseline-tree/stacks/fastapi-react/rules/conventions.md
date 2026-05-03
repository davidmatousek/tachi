# Conventions — Python FastAPI + React

## Backend (Python)

### Always

- Use `async def` for every FastAPI route handler.
- Use Pydantic models for all I/O: request bodies, responses, and configuration.
- Inject dependencies via `Depends()` for DB sessions, auth, and shared resources.
- Route handlers call service functions; never call the ORM directly from routes.
- Follow schema-per-lifecycle: `Base`, `Create`, `Update`, `Response`.
- Set `from_attributes = True` on all response schemas.
- Set `expire_on_commit=False` on `async_sessionmaker` to prevent `MissingGreenlet`.
- Use SQLAlchemy 2.0 syntax: `select()`, `insert()`, `update()`, `delete()`.
- Use `selectinload()` for collection relationships, `joinedload()` for scalar relationships.
- Add typed return annotations to all service functions.
- Use `pydantic_settings.BaseSettings` for configuration.
- Use `uv` for package management.
- Use Ruff for linting and formatting.
- Use Alembic with async `run_sync()` for migrations.

### Never

- Use synchronous route handlers (`def` instead of `async def`).
- Use legacy `session.query()` syntax.
- Set `lazy="select"` on relationships in async context.
- Put business logic in route handlers.
- Import `from sqlalchemy.orm import Session`; use `AsyncSession`.
- Use `pip install` or `poetry`; use `uv`.
- Store global mutable state in service modules.
- Use `text()` with f-strings for SQL queries.

## Frontend (React / TypeScript)

### Always

- Enable TypeScript strict mode (`"strict": true` in `tsconfig.json`).
- Use functional components with a typed `interface Props`.
- Define explicit `interface Props`; destructure props in the function signature.
- Use TanStack Query v5 with query key factories.
- Use `gcTime` for cache duration (not `cacheTime`).
- Use Tailwind CSS v4: `@import "tailwindcss"` + `@theme` directive.
- Use `bg-linear-to-*` for gradients (v4 rename from `bg-gradient-to-*`).
- Use CSS variable syntax with parentheses: `bg-(--var)`.
- Use named exports for all components and utilities.
- Configure path aliases: `@/` maps to `src/`.
- Use Biome for linting and formatting.
- Set API base URL via `VITE_API_URL`.

### Never

- Use `React.FC<Props>`; define props interface and type the function directly.
- Use `any` type; use `unknown` with type narrowing.
- Use `useEffect` for data fetching; use TanStack Query.
- Use class components.
- Use CSS Modules, styled-components, or inline styles; use Tailwind CSS.
- Create barrel files (`index.ts`) in large directories.
- Use `enum`; use string union types instead.
- Store tokens in `localStorage`.
- Use `tailwind.config.js`; use CSS-based config with `@theme`.
- Use `bg-gradient-to-*`; use `bg-linear-to-*`.
- Use `cacheTime`; use `gcTime`.
