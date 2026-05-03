# Next.js + Supabase Stack

**Target**: Solo developers and small teams building SaaS web applications
**Stack**: Next.js 15+ · TypeScript 5.5+ · Supabase · Prisma 7+ · Tailwind CSS 4+ · shadcn/ui · Biome 2+ · Vercel
**Use Case**: Full-stack web applications with authentication, database, and deployment
**Deployment**: Vercel (production), local dev server (development)
**Philosophy**: Server-first rendering, type-safe data access, security by default, convention over configuration

---

## Architecture Pattern

### Rendering Strategy

ALWAYS use Server Components by default. ONLY add `'use client'` when the component requires browser APIs, event handlers, or React hooks (`useState`, `useEffect`, `useContext`). Client boundaries are inherited — marking a parent `'use client'` makes all its children client components, expanding the client bundle unnecessarily.

### Data Flow

- **Reads**: Fetch data in Server Components using Prisma queries directly. NEVER create API route wrappers for data that Server Components can fetch — the extra network hop adds latency for no benefit.
- **Mutations**: Use Server Actions (`'use server'`) for all data mutations. Colocate actions in `app/` route directories or extract shared actions to `lib/actions/`.
- **API Routes**: Reserve `app/api/` EXCLUSIVELY for webhook receivers and external service integrations. NEVER use API routes for internal data fetching or mutations.
- **Realtime**: Use Supabase Realtime subscriptions in client components for live data (chat, notifications, presence).

### State Management

- **Server state**: Server Components + Prisma queries. No client cache layer needed for initial page loads.
- **Client state**: React `useState` / `useReducer` for component-local state. Lift shared client state to the nearest common layout.
- **URL state**: Use `searchParams` for filterable/shareable UI state (pagination, sort, filters). NEVER store URL-representable state in `useState`.
- **Form state**: Use `useActionState` (React 19+) with Server Actions for form submissions and optimistic updates.

### Component Model

- **Server Components**: Data fetching, layout, static content, SEO metadata.
- **Client Components**: Interactive elements, form inputs, event handlers, browser API access.
- **Composition pattern**: Pass Server Component output as `children` to Client Components. NEVER fetch data inside a client component when a server component can pass it as props.

### Error Handling

- **Error boundaries**: ALWAYS provide `error.tsx` at the root layout level. Add route-segment-level `error.tsx` ONLY when a segment requires a distinct recovery UI (e.g., dashboard vs. marketing pages). Do NOT create `error.tsx` for every route segment by default.
- **Server Actions**: ALWAYS return a typed result object `{ success: boolean; error?: string; data?: T }` from Server Actions. NEVER throw errors from Server Actions for expected failures (validation, auth, not-found). ONLY let unexpected errors (database down, network failure) propagate to the error boundary.
- **Try/catch in Server Actions**: ALWAYS wrap Prisma calls and external service calls in try/catch. Return the error message in the result object. Let the `useActionState` hook surface the error to the UI.
- **`not-found.tsx`**: ALWAYS provide a root `not-found.tsx`. Call `notFound()` from `next/navigation` in Server Components when a resource lookup returns null.

---

## File Structure

```
app/                          # App Router — pages, layouts, route handlers
  (auth)/                     # Route group — login, signup, forgot-password
    login/page.tsx
    signup/page.tsx
    layout.tsx                # Auth-specific layout (no sidebar)
  (dashboard)/                # Route group — protected routes
    dashboard/page.tsx
    settings/page.tsx
    layout.tsx                # Dashboard layout (sidebar, nav)
  api/                        # API routes — webhooks and external integrations ONLY
    webhooks/
      stripe/route.ts
  layout.tsx                  # Root layout — providers, fonts, metadata
  page.tsx                    # Landing page
  loading.tsx                 # Root loading state
  error.tsx                   # Root error boundary
  not-found.tsx               # 404 page
components/                   # Shared UI components
  ui/                         # shadcn/ui primitives (Button, Dialog, Input)
  layouts/                    # Layout partials (Sidebar, Header, Footer)
  forms/                      # Form components with validation
lib/                          # Shared utilities and configuration
  supabase/
    client.ts                 # Browser Supabase client factory
    server.ts                 # Server Supabase client factory
    middleware.ts              # Supabase auth middleware helper
  auth/
    withAuth.ts               # Server Action auth wrapper
    guards.ts                 # Route protection utilities
  validations/                # Zod schemas — shared client and server
    auth.ts
    user.ts
  hooks/                      # Custom React hooks ('use client')
    useMediaQuery.ts
  services/                   # Business logic — domain services called by Server Actions
    user.ts
    billing.ts
  utils.ts                    # General utility functions (cn, formatDate)
prisma/                       # Prisma ORM
  schema.prisma               # Database schema (single source of truth)
  migrations/                 # Migration history (committed to git)
  seed.ts                     # Database seed script
public/                       # Static assets (favicon, og-images)
middleware.ts                 # Next.js middleware — auth redirect, CSP headers
next.config.ts                # Next.js configuration — CSP headers, redirects, image domains
biome.json                    # Biome linter and formatter configuration
tailwind.config.ts            # Tailwind CSS configuration (if customization needed)
tsconfig.json                 # TypeScript strict mode configuration
.env.local                    # Local environment variables (gitignored)
```

---

## Naming Conventions

| Category | Convention | Example |
|----------|-----------|---------|
| React components | PascalCase `.tsx` | `UserProfile.tsx` |
| Utility modules | camelCase `.ts` | `formatDate.ts` |
| Route directories | kebab-case | `forgot-password/` |
| Route files | Next.js convention | `page.tsx`, `layout.tsx`, `loading.tsx`, `error.tsx` |
| API route files | `route.ts` | `app/api/webhooks/stripe/route.ts` |
| Server Actions | camelCase, verb-first | `createUser`, `updateProfile` |
| Test files | Co-located, `.test` suffix | `UserProfile.test.tsx`, `formatDate.test.ts` |
| Zod schemas | camelCase, `Schema` suffix | `loginSchema`, `userUpdateSchema` |
| Custom hooks | `use` prefix, camelCase `.ts` | `useAuth.ts`, `useMediaQuery.ts` |
| Context providers | PascalCase, `Provider` suffix `.tsx` | `ThemeProvider.tsx`, `AuthProvider.tsx` |
| Constants | camelCase `.ts`, `UPPER_SNAKE_CASE` values | `lib/constants.ts` → `export const MAX_RETRIES = 3` |
| Type files | `types.ts` per domain | `lib/validations/types.ts` |
| Config files | `*.config.ts` | `tailwind.config.ts`, `vitest.config.ts` |
| Environment variables | `UPPER_SNAKE_CASE` | `NEXT_PUBLIC_SUPABASE_URL` |
| Database tables | snake_case, plural | `user_profiles`, `team_members` |
| Prisma models | PascalCase, singular | `UserProfile`, `TeamMember` |

---

## Security Patterns

### Input Validation

- ALWAYS validate ALL user inputs with Zod before processing — in Server Actions, API routes, and middleware. No exceptions.
- ALWAYS define Zod schemas in `lib/validations/` and share them between client-side forms and server-side actions.
- ALWAYS use `.safeParse()` inside Server Actions and return validation errors in the result object (`{ success: false; error: string }`). Use `.parse()` (throws on failure) ONLY in API route handlers where the error boundary should catch invalid input.
- NEVER trust data from `request.json()`, `formData()`, or `searchParams` without Zod validation.

### Authentication and Authorization

- ALWAYS wrap every data-mutating Server Action with `withAuth()` as the FIRST operation — no exceptions.
- ALWAYS verify authentication in every API Route Handler that performs a data mutation — NEVER allow unauthenticated writes.
- ALWAYS enforce authentication in `middleware.ts` for ALL protected routes — every route group serving authenticated content MUST be covered, not just `/dashboard/*`.
- ALWAYS use `@supabase/ssr` for cookie-based auth in Next.js. ONLY use `getAll` and `setAll` for cookie management — `get`, `set`, `remove` are deprecated.
- NEVER trust client-side auth checks as the sole protection. Server-side verification is mandatory.
- NEVER store the Supabase `service_role` key in client-accessible code or environment variables prefixed with `NEXT_PUBLIC_`.

### Data Access

- ALWAYS use Prisma parameterized queries for all database operations. Prisma prevents SQL injection by design.
- ALWAYS configure Supabase Row Level Security (RLS) policies on every table. RLS is opt-in — tables without policies are exposed through the REST API.
- ALWAYS create both SELECT and INSERT policies when a table allows inserts — PostgreSQL SELECTs inserted rows to return them, which fails without a SELECT policy.
- NEVER use `$queryRawUnsafe()` or `$executeRawUnsafe()` under any circumstances.
- NEVER use `$queryRaw` or `$executeRaw` unless no Prisma Client API alternative exists — when required, ALWAYS use tagged template literals for parameterization.
- NEVER expose database connection strings in client code or public environment variables.

### Secrets Management

- ALWAYS store secrets in environment variables configured through Vercel Dashboard (production) or `.env.local` (development).
- ALWAYS prefix client-accessible environment variables with `NEXT_PUBLIC_`. ONLY the Supabase URL and anon key should use this prefix.
- NEVER commit `.env.local` or any file containing secrets to version control.
- NEVER log secrets, tokens, or connection strings — even in development.

---

## Coding Standards

### Always Use

- **Functional components exclusively** — NEVER use class components. All components are function declarations or arrow functions.
- **Server Components by default** — add `'use client'` only when the component needs browser APIs or React hooks.
- **App Router** with file-based routing (`page.tsx`, `layout.tsx`, `loading.tsx`, `error.tsx`, `not-found.tsx`).
- **npm** as the default package manager (ships with Node.js, zero-install). Lock file (`package-lock.json`) MUST be committed. pnpm is also supported — delete `package-lock.json` and run `pnpm install` to switch.
- **Biome** for linting and formatting. Single tool replaces ESLint + Prettier with 10-100x faster performance. Configure Biome's `organizeImports` to enforce import ordering automatically.
- **Import order** — ALWAYS follow this exact sequence, separated by blank lines: (1) `react` / `react-dom`, (2) `next/*` imports, (3) third-party packages, (4) `@/lib/*` local utilities, (5) `@/components/*` local components, (6) type-only imports (`import type`).
- **TypeScript strict mode** — `"strict": true` in `tsconfig.json`. ALWAYS define explicit return types for Server Actions and exported functions. ALWAYS use `type` for object shapes, unions, and intersections. ONLY use `interface` when declaration merging is required (e.g., extending third-party types). ALWAYS use string union types (`type Role = 'admin' | 'user'`) instead of `enum`.
- **Prisma** for all database reads and writes. Generate the client after every schema change (`npx prisma generate`).
- **Tailwind CSS utility classes** directly in JSX. Use the `cn()` helper (from `lib/utils.ts`) for conditional classes.
- **shadcn/ui** for UI primitives. Install components via CLI (`npx shadcn add`), customize in `components/ui/`.
- **Named exports** for all modules EXCEPT route files (`page.tsx`, `layout.tsx`, `route.ts`) which use default exports per Next.js convention.
- **Server Actions** (`'use server'`) for all data mutations. Validate inputs with Zod, wrap with `withAuth()`.
- **Zod schemas** for all validation — shared between client forms and server actions.
- **`@supabase/ssr`** for Supabase client creation in Next.js. Separate client and server factories in `lib/supabase/`.
- **Async Server Components** for data fetching. Fetch at the component level, not in parent layouts (enables streaming).
- **Suspense boundaries** with `loading.tsx` or inline `<Suspense>` for async component streaming.
- **`useActionState`** (React 19+) for form submission state and server action responses.
- **Custom hooks** — extract reusable client-side logic into `use`-prefixed functions in `lib/hooks/` (e.g., `useMediaQuery.ts`). ALWAYS mark hook files `'use client'`. NEVER create hooks that only wrap a single `useState` — inline trivial state in the consuming component.
- **`next/image`** for all images — ALWAYS use `<Image>` with explicit `width`, `height` (or `fill`) and `alt` props. NEVER use raw `<img>` tags.
- **`next/link`** for all internal navigation — ALWAYS use `<Link>` for internal routes. NEVER use `<a>` tags for internal links or `window.location` for navigation.
- **`next/navigation`** for programmatic routing — use `useRouter`, `usePathname`, `useSearchParams` from `next/navigation`. NEVER import from `next/router` (Pages Router).
- **Uncontrolled form inputs** with `FormData` — let the browser manage form state. Use `name` attributes on inputs and extract values from `FormData` in Server Actions. NEVER use controlled inputs (`useState` per field) unless the component requires real-time validation or derived state between fields.

### Never Use

- **Pages Router** — all routing through App Router exclusively.
- **CSS Modules or styled-components** — Tailwind utilities only.
- **yarn** — use npm (or pnpm if the project has `pnpm-lock.yaml`).
- **ESLint + Prettier** — Biome only.
- **Any ORM besides Prisma** — no Drizzle, Knex, or raw SQL.
- **Inline styles** — use Tailwind classes.
- **Default exports** — except `page.tsx`, `layout.tsx`, `route.ts`, `loading.tsx`, `error.tsx`, `not-found.tsx`.
- **Client-side data fetching for initial page loads** — fetch in Server Components. Reserve `useEffect` for realtime subscriptions and browser-only side effects.
- **`any` type** — use `unknown` and narrow with type guards. The only exception is third-party library types that require `any`.
- **`useEffect` for data fetching** — use Server Components or Server Actions.
- **Route Handlers for internal data** — fetch directly in Server Components. Route Handlers are for webhooks and external integrations only.
- **Context API across server/client boundary** — React Context does not work in Server Components. Use composition (props/children) instead.
- **Barrel files (`index.ts`)** in large directories — they defeat tree-shaking and slow builds. Import directly from the source module.
- **Class components** — ALWAYS use function components. Class components are incompatible with Server Components and hooks.
- **`useLayoutEffect`** — causes SSR warnings in Next.js. Use `useEffect` for all side effects.
- **Raw `<img>` tags** — ALWAYS use `next/image` for automatic optimization, lazy loading, and responsive sizing.
- **`<a>` tags for internal links** — ALWAYS use `next/link` for client-side navigation. `<a>` tags trigger full page reloads.
- **TypeScript `enum`** — use string union types (`type Status = 'active' | 'inactive'`) instead. Enums produce runtime code and have known pitfalls with tree-shaking.
- **Global client state libraries** (Zustand, Jotai, Redux) — use Server Components for server state, `useState`/`useReducer` for component-local state, and `searchParams` for URL state. If shared client state is unavoidable, lift it to the nearest common layout with React Context. NEVER add an external state management library.
- **`useMemo` / `useCallback` by default** — ONLY add memoization when a measurable performance problem exists. Premature memoization adds complexity without benefit.

---

## Testing Conventions

<!-- BEGIN: aod-test-contract -->
```yaml
test_command: "npm run test"
e2e_command: "npx playwright test"
test_paths:
  - "tests/"
  - "e2e/"
  - "**/*.test.ts"
  - "**/*.spec.ts"
```
<!-- END: aod-test-contract -->

### Framework Stack

| Level | Framework | Purpose |
|-------|-----------|---------|
| Unit | Vitest 4+ | Pure functions, utilities, Zod schemas, Server Action logic |
| Component | Vitest + Testing Library | React component rendering, user interactions |
| Integration | Vitest | Server Actions with mocked Prisma, API route handlers |
| E2E | Playwright 1.50+ | Critical user journeys across the full stack |

### File Conventions

- Co-locate test files with source: `UserProfile.test.tsx` beside `UserProfile.tsx`.
- ALWAYS use the `.test.ts` or `.test.tsx` suffix. NEVER use `.spec.ts`.
- Place E2E tests in a top-level `e2e/` directory: `e2e/auth.test.ts`, `e2e/dashboard.test.ts`.
- Place test utilities and shared mocks in `tests/` directory: `tests/mocks/prisma.ts`, `tests/helpers/`.

### Unit Tests

- Test pure functions, Zod schema validation, and business logic extracted from Server Actions.
- Mock Prisma client using `vitest.mock()` — NEVER connect to a real database in unit tests.
- ALWAYS test both success and failure paths for validation schemas.

### Component Tests

- Use Testing Library — test user interactions and rendered output, NEVER test implementation details.
- ALWAYS query by accessible roles (`getByRole`), labels (`getByLabelText`), or text (`getByText`). NEVER query by CSS class or test ID unless no accessible query exists.
- Mock Server Actions and Supabase client in component tests.

### Integration Tests

- Test Server Actions with mocked Prisma and Supabase auth.
- Verify that `withAuth()` correctly rejects unauthenticated requests.
- Test API route handlers (webhooks) with mocked request/response objects.

### E2E Tests

- Cover critical user journeys: signup, login, CRUD operations, logout.
- Use Playwright fixtures for authenticated state — NEVER repeat login flows in every test.
- Run against a local Supabase instance (`supabase start`) with seeded test data.
- ALWAYS clean up test data after each test run.

### Coverage

- Enforce minimum 80% line coverage on `lib/` and Server Action files.
- Do NOT enforce coverage thresholds on UI components — test critical interactions, not markup.

---

## Deployment

### Production (Vercel)

- Deploy to Vercel via Git push to `main`. NEVER deploy from local machine.
- Configure ALL secrets via Vercel Dashboard environment variables. NEVER hardcode secrets.
- Run `npx prisma migrate deploy` in the Vercel build step for database migrations.
- Enable Vercel Edge Middleware for auth redirects and CSP header injection.
- Set `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` as Vercel environment variables.

### Preview Environments

- Vercel creates preview deployments for every PR. Use Supabase branching or a shared staging project for preview database access.
- NEVER point preview deployments at the production Supabase project.

### Local Development

- Run `supabase start` for local Supabase (auth, storage, database, realtime).
- Run `npx prisma migrate dev` for local schema migrations.
- Run `npm run dev` for the Next.js development server with Turbopack.
- Copy `.env.local.example` to `.env.local` and populate with local Supabase credentials.

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `next` | `>=15.0.0` | React framework with App Router |
| `react` / `react-dom` | `>=19.0.0` | UI library (Server Components, `useActionState`) |
| `typescript` | `>=5.5.0` | Type safety |
| `@supabase/supabase-js` | `>=2.45.0` | Supabase client |
| `@supabase/ssr` | `>=0.5.0` | Supabase cookie-based auth for Next.js |
| `@prisma/client` | `>=7.0.0` | Type-safe database client |
| `prisma` | `>=7.0.0` | Schema management and migrations (devDependency) |
| `zod` | `>=3.23.0` | Runtime validation |
| `tailwindcss` | `>=4.0.0` | Utility-first CSS |
| `@biomejs/biome` | `>=2.0.0` | Linting and formatting (devDependency) |
| `vitest` | `>=4.0.0` | Unit and integration testing (devDependency) |
| `@testing-library/react` | `>=16.0.0` | Component testing (devDependency) |
| `playwright` | `>=1.50.0` | E2E testing (devDependency) |
