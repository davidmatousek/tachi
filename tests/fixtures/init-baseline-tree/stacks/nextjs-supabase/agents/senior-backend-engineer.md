# Senior Backend Engineer — Next.js + Supabase Supplement

## Stack Context

Supabase (PostgreSQL + Auth + Storage + Realtime), Prisma ORM for type-safe data access, Server Actions for mutations, API routes for webhooks/external integrations only, Zod for input validation, TypeScript strict mode.

## Conventions

- ALWAYS use Server Actions for data mutations (create, update, delete) -- never API routes for internal mutations
- ALWAYS validate ALL inputs with Zod schemas before any data processing
- ALWAYS wrap every mutation Server Action with withAuth() to verify authentication before execution
- ALWAYS use Prisma for ALL database access -- parameterized queries, type-safe, no raw SQL
- ALWAYS define Prisma models with explicit relations, indexes, and `@@map` for table naming
- ALWAYS use Supabase Auth helpers (createServerClient) for server-side session verification
- ALWAYS return structured responses from Server Actions: `{ success: boolean, data?: T, error?: string }`
- ALWAYS use database transactions (`prisma.$transaction`) for multi-step mutations
- ALWAYS handle errors with try/catch in every Server Action -- never let exceptions propagate to client
- ALWAYS use Supabase RLS as defense-in-depth alongside application-level auth checks
- ALWAYS place business logic in `lib/services/` -- Server Actions are thin orchestrators that validate, authorize, delegate, and return
- ALWAYS access environment variables through `process.env` -- validate required values at startup with Zod and fail fast on missing configuration
- ALWAYS co-locate Server Actions in `app/{route}/actions.ts` with their consuming route
- ALWAYS type Server Action return values with Prisma's generated types -- no `any`

## Anti-Patterns

- NEVER use raw SQL queries -- always use Prisma's query builder or `prisma.$queryRaw` with tagged template literals only when absolutely necessary
- NEVER skip input validation -- every Server Action starts with `schema.safeParse(input)` and returns errors in the result object
- NEVER access the database directly from components -- go through Server Actions or `lib/services/`
- NEVER store secrets in client-accessible code or commit `.env` / `.env.local` to git
- NEVER use API routes (`app/api/`) for operations that should be Server Actions -- API routes are for webhooks, cron jobs, and external service callbacks only
- NEVER trust client-side data -- always re-validate and re-authorize on the server
- NEVER use Supabase JS client for data mutations in Server Actions -- use Prisma for data, Supabase for auth and storage only
- NEVER skip error handling in async operations -- unhandled rejections crash Server Actions silently
- NEVER use `prisma.$executeRawUnsafe` or `prisma.$queryRawUnsafe` -- these bypass parameterization
- NEVER return full Prisma objects with sensitive fields to the client -- use `select` or `omit` to shape responses

## Guardrails

- Service files: `lib/services/{domain}.ts` (e.g., `lib/services/user.ts`, `lib/services/billing.ts`)
- Validation schemas: `lib/validations/{domain}.ts` (e.g., `lib/validations/user.ts`)
- Server Actions: `app/{route}/actions.ts` (co-located with the route that consumes them)
- Prisma schema: `prisma/schema.prisma` (single source of truth for data model)
- API routes: `app/api/` (webhooks and external integrations ONLY -- never internal mutations)
- Auth helpers: `lib/auth/withAuth.ts` (withAuth wrapper), `lib/auth/guards.ts` (route protection)
- Database operations must always have error handling and return typed results
- Migrations: `npx prisma migrate dev --name {description}` -- never edit migration files after creation
- No `any` type -- use Prisma generated types and Zod inferred types for all data shapes
