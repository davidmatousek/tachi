# Code Reviewer — Next.js + Supabase Supplement

## Stack Context

Next.js 15+ App Router with React Server Components and Server Actions, TypeScript strict mode, Prisma ORM (parameterized queries), Supabase Auth and RLS, Tailwind CSS v4, shadcn/ui (Radix-based), Biome (linting + formatting), npm, Vitest + React Testing Library, Vercel deployment.

## Conventions

- ALWAYS verify Server Components are used by default; flag every `'use client'` directive and confirm the component genuinely requires useState, useEffect, event handlers, or browser APIs
- ALWAYS check that data fetching happens in Server Components via async/await; flag any `useEffect` + `fetch` pattern that could be a Server Component
- ALWAYS verify all Server Actions follow the exact pattern: `withAuth()` -> Zod validation -> business logic -> typed return; flag any deviation in ordering or omission
- ALWAYS check Prisma usage: parameterized queries only, no `$queryRawUnsafe()`, no string-interpolated SQL, proper `include`/`select` to avoid over-fetching, no N+1 query patterns
- ALWAYS verify TypeScript strict mode compliance: no `any` type anywhere, explicit return types on all exported functions, proper null checks with narrowing (not non-null assertions)
- ALWAYS check import ordering: React/Next.js -> third-party -> `@/lib` -> `@/components` -> types
- ALWAYS verify Tailwind utility usage exclusively; flag CSS modules, styled-components, CSS-in-JS, or inline `style` objects
- ALWAYS check named exports are used for all components, hooks, and utilities; default exports only for `page.tsx` and `layout.tsx`
- ALWAYS verify `error.tsx` boundaries exist for every route segment that performs data fetching or Server Action calls
- ALWAYS check that Zod schemas live in `lib/validations/` and are shared between client forms and Server Actions
- ALWAYS verify environment variables: `NEXT_PUBLIC_` prefix only for non-sensitive client-safe values; no secrets in client-accessible code
- ALWAYS check that `Suspense` boundaries with meaningful loading states wrap async Server Components
- ALWAYS verify `cn()` utility is used for conditional class composition; flag string concatenation for classNames
- ALWAYS check that Supabase client access goes through `@/lib/supabase` server-side helpers, never direct client imports in components

## Anti-Patterns

Flag these as findings in every review:

- Client-side data fetching (`useEffect` + `fetch`) when Server Components could handle it — CRITICAL
- Raw SQL queries or string interpolation in Prisma (`$queryRawUnsafe()`, template literals) — CRITICAL
- Missing `withAuth()` on any Server Action that reads or mutates protected data — CRITICAL
- Missing Zod validation on any Server Action or API route input — CRITICAL
- Secrets or API keys accessible in client bundles (missing or wrong `NEXT_PUBLIC_` usage) — CRITICAL
- `any` type usage anywhere in the codebase — WARNING
- CSS modules, styled-components, CSS-in-JS, or inline `style` objects — WARNING
- Pages Router patterns (`getServerSideProps`, `getStaticProps`, `_app.tsx`, `_document.tsx`) — WARNING
- Default exports on non-page/layout files — WARNING
- Direct database access from components bypassing Server Actions or service layer — WARNING
- `className` string concatenation instead of `cn()` utility — WARNING
- `useRouter` from `next/router` instead of `next/navigation` — WARNING
- Missing `error.tsx` in route segments that fetch data — WARNING
- N+1 query patterns in Prisma (queries inside loops, missing `include`/`select`) — WARNING
- Non-null assertions (`!`) instead of proper type narrowing — SUGGESTION
- Inline Zod schemas instead of shared schemas from `lib/validations/` — SUGGESTION
- Missing `Suspense` boundaries around async Server Components — SUGGESTION

## Guardrails

- Review priority: Security (auth/injection/secrets) > Data integrity (validation/queries) > Architecture (Server/Client boundary) > Convention compliance > Style
- Every PR touching Server Actions: verify (1) `withAuth()` (2) Zod validation (3) typed error handling (4) no leaked internals in responses
- Every PR touching Prisma: verify no raw SQL, proper `select`/`include`, no N+1 patterns, transactions for multi-step mutations
- Every PR touching components: verify Server/Client boundary is correct and `'use client'` is justified
- Every PR touching `middleware.ts`: verify auth route protection has not regressed
- Every PR touching environment variables: verify no secrets leak to client bundles
- File naming compliance: PascalCase components (`UserProfile.tsx`), camelCase utils (`formatDate.ts`), kebab-case routes (`user-settings/`)
- Biome must pass with zero errors and zero warnings before approval
- `npm audit` must report zero critical or high vulnerabilities before approval
