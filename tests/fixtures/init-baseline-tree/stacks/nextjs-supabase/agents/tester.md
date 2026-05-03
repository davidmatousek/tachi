# Tester — Next.js + Supabase Supplement

## Stack Context

Vitest as the test runner (not Jest). Testing Library (`@testing-library/react`) for component tests. Playwright for E2E tests. MSW (Mock Service Worker) for API mocking. TypeScript strict mode. Server Components and Server Actions require specific testing patterns — Server Components are tested via integration/E2E, Server Actions are tested by direct invocation with mocked dependencies. Prisma is mocked at the module level for unit tests. Supabase auth is always mocked in unit/integration tests.

## Conventions

- ALWAYS use Vitest as the test runner — configure in `vitest.config.ts` with `@vitejs/plugin-react`
- ALWAYS use Testing Library for React component tests — test what the user sees and does, not component internals
- ALWAYS use Playwright for E2E tests covering critical user journeys: auth flows, CRUD operations, protected routes
- ALWAYS co-locate unit/component test files: `ComponentName.test.tsx` next to `ComponentName.tsx`
- ALWAYS co-locate Server Action tests: `actions.test.ts` next to `actions.ts`
- ALWAYS place E2E tests in `e2e/` at project root with `*.test.ts` naming
- ALWAYS mock Prisma at module level: `vi.mock('@/lib/prisma')` — never hit real database in unit tests
- ALWAYS mock Supabase auth helpers: `vi.mock('@/lib/supabase/server')` — never hit real auth in unit tests
- ALWAYS use MSW for API route handler tests — intercept at the network level, not the function level
- ALWAYS test Server Actions by: (1) mock Prisma/Supabase (2) call the action function directly (3) assert return value and side effects
- ALWAYS test Client Components by: (1) render with Testing Library (2) simulate user events (3) assert visible DOM output
- ALWAYS prefer accessibility-first queries: `screen.getByRole()`, `screen.getByLabelText()`, `screen.getByText()`
- ALWAYS test three states per component: loading (Suspense fallback), error (error boundary), and success (rendered data)
- ALWAYS test empty states explicitly — lists with zero items, dashboards with no data
- ALWAYS use `vi.fn()` for function mocks, `vi.spyOn()` for method spies, `vi.mocked()` for type-safe mock access
- ALWAYS wrap Server Action tests with mocked `cookies()` and `headers()` from `next/headers`
- ALWAYS test Zod validation in Server Actions — assert rejection of invalid input before database access
- ALWAYS test that Server Actions reject unauthenticated requests — call without valid session and assert auth failure
- ALWAYS use `userEvent` from `@testing-library/user-event` over `fireEvent` for realistic interaction simulation
- ALWAYS clean up test data in E2E `afterEach`/`afterAll` hooks — tests must be idempotent

## Anti-Patterns

- NEVER use Jest — Vitest is the runner (API-compatible, faster with Vite, native ESM/TypeScript)
- NEVER use snapshot tests as primary strategy — test behavior and visible output
- NEVER test implementation details: internal state, hook return values, component instance methods
- NEVER use `getByTestId()` as first-choice query — exhaust role/label/text queries first
- NEVER test third-party library behavior (shadcn/ui internals, Supabase SDK logic) — test YOUR integration with them
- NEVER mock everything — mock external boundaries (Prisma, Supabase, fetch), test business logic directly
- NEVER write E2E tests for every feature — reserve for critical paths (auth, payments, data mutations)
- NEVER use `waitFor` with hardcoded timeouts — use `findBy*` queries or Playwright auto-waiting
- NEVER import from `next/router` in tests — use `next/navigation` mocks exclusively
- NEVER test Server Components with `render()` — they are async and cannot be rendered client-side; test via E2E or by testing the data-fetching logic in isolation
- NEVER call real Supabase endpoints in unit/integration tests — use mocks or MSW
- NEVER use `act()` manually — Testing Library wraps interactions in `act()` automatically

## Stack-Specific E2E Conventions

- Test directory: `e2e/*.test.ts` at the repo root; one spec file per user flow
- Fixture pattern: reuse `storageState` JSON for authenticated runs — sign in once in a setup project, then load state in dependent specs
- Fixture pattern: encapsulate repeated screen interactions as page object classes under `e2e/pages/` (constructor takes `page: Page`)
- Query precedence (highest first): `getByRole()` → `getByLabel()` → `getByTestId()` → CSS selectors (last resort)
- Prefer `page.getByRole('button', { name: /submit/i })` over raw selectors so tests double as accessibility checks

## Guardrails

- Unit/component test naming: `*.test.ts` (utilities), `*.test.tsx` (components)
- E2E test naming: `e2e/*.test.ts`
- Describe blocks: `describe('ComponentName')` or `describe('actionName')` with `it('should {behavior}')` format
- Minimum coverage targets: 80% for business logic (`lib/`, `services/`, `actions.ts`), 60% for components
- Server Action tests must verify four concerns: (1) auth check (2) input validation (3) database operation (4) return value
- E2E tests must run against a seeded test database — never share state between test files
- All Playwright tests must use `test.describe` for grouping and `test.beforeEach` for page navigation
- Mock files live in `__mocks__/` directories co-located with the module they mock
- Test utilities and custom render functions live in `tests/utils/` with a `render.tsx` wrapper that provides required providers (ThemeProvider, etc.)
