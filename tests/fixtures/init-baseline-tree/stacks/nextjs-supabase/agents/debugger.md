# Debugger — Next.js + Supabase Supplement

## Stack Context

Next.js 15+ App Router with Server/Client component boundary, Supabase (PostgreSQL + Auth + RLS), Prisma ORM with query logging, Server Actions (`'use server'`), TypeScript strict mode, Vitest for test reproduction, Vercel deployment logs, `middleware.ts` for auth routing, `@supabase/ssr` for cookie-based sessions, Zod for input validation.

## Conventions

- ALWAYS determine the Server/Client component boundary FIRST — most Next.js bugs stem from using client APIs in Server Components or server APIs in Client Components
- ALWAYS check `'use client'` directive presence when seeing "useState/useEffect is not defined", hydration mismatch, or "async Server Component" errors
- ALWAYS check Supabase RLS policies when queries return empty results unexpectedly — RLS silently filters rows rather than throwing errors
- ALWAYS verify auth with `getUser()` (server-verified against Supabase) not `getSession()` (reads local JWT, can be stale or tampered)
- ALWAYS enable Prisma query logging for database debugging: set `DEBUG="prisma:query"` env var or use `prisma.$on('query', handler)` in code
- ALWAYS run `prisma migrate status` when seeing schema-related or "column does not exist" errors before investigating further
- ALWAYS check environment variable availability: `NEXT_PUBLIC_*` for client bundles, plain names for server only — mismatches cause silent `undefined`
- ALWAYS check Vercel function logs for Server Action errors — the client only sees a generic "An error occurred" message
- ALWAYS inspect network tab for Server Action calls — they appear as POST to the current URL with a `Next-Action` header
- ALWAYS check `middleware.ts` execution order when auth redirects loop or behave unexpectedly — middleware runs before route handlers
- ALWAYS reproduce bugs with a minimal Vitest test case before attempting a fix — confirms root cause and prevents regression
- ALWAYS use `error.tsx` boundaries per route segment to capture and log errors rather than letting them bubble to the root
- ALWAYS check `@` alias resolution in `tsconfig.json` paths when seeing "Module not found" errors on internal imports

## Anti-Patterns

- NEVER disable Supabase RLS to "fix" empty query results — diagnose and fix the RLS policy instead
- NEVER debug by modifying `node_modules` — create a minimal reproduction case
- NEVER assume client and server share environment variables — verify the `NEXT_PUBLIC_` prefix
- NEVER add `any` types or `@ts-ignore` to suppress TypeScript errors during debugging — fix the underlying type issue
- NEVER debug Server Components with browser devtools alone — use server-side logging (Vercel logs, terminal output)
- NEVER leave `console.log` statements in production code after debugging — use structured logging or remove them
- NEVER use `getSession()` to debug auth issues — it reads stale local JWTs; always verify with `getUser()`
- NEVER comment out or bypass `withAuth()`, Zod validation, or RLS policies to isolate bugs — reproduce with security intact, then narrow the scope
- NEVER ignore Prisma migration drift warnings — run `prisma migrate dev` to reconcile before investigating query errors

## Guardrails

- Debugging priority order: (1) Reproduce reliably (2) Isolate boundary — server or client (3) Trace data flow (4) Verify auth and RLS (5) Fix root cause
- Next.js error pattern map:
  - "Hydration mismatch" -> Client component renders differently server vs client; check `Date`, `Math.random()`, `window`, `localStorage` usage
  - "Dynamic server usage" -> Server Component calls `cookies()`, `headers()`, or `searchParams` without dynamic route config
  - "Module not found" -> Check import paths and `@` alias in `tsconfig.json`; verify file extensions
  - "'use client' cannot be used in a Server Component" -> Component hierarchy mismatch; trace the import chain
  - "Functions cannot be passed directly to Client Components" -> Serialize data before crossing the server/client boundary
- Supabase error pattern map:
  - Empty results with no error -> RLS policy filtering; check policy conditions and user context (`auth.uid()`)
  - "JWT expired" or 401 -> Token refresh failed; check `@supabase/ssr` middleware cookie handling
  - Connection refused -> Check `DATABASE_URL` (pooled, for Prisma) vs `DIRECT_URL` (direct, for migrations)
  - "new row violates row-level security" -> INSERT policy missing or SELECT policy required for RETURNING clause
- Prisma error pattern map:
  - "Record to update not found" -> Verify WHERE clause and check RLS if using Supabase connection
  - "Unknown argument" -> Schema out of sync; run `prisma generate` then `prisma migrate dev`
  - Slow queries -> Enable query logging, check for N+1 patterns (queries inside loops), add `select`/`include` to limit fields
- Server Action debugging: verify call chain is (1) `withAuth()` (2) Zod `.parse()` (3) Prisma operation (4) typed return; errors at any step produce different failure modes
- Vercel-specific: check function timeout (default 10s for Hobby, 60s for Pro), cold start latency, and region configuration for Supabase connection proximity
