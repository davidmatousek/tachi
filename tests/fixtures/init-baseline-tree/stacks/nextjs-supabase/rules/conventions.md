# Next.js + Supabase Conventions

<!-- Stack rules file — loaded by ALL agents when the nextjs-supabase pack is active -->
<!-- Copied to .claude/rules/stack/ at activation time -->

These rules apply to ALL agents when the nextjs-supabase stack pack is active.

---

## Always Use

### Framework & Runtime
- ALWAYS use Next.js App Router — never Pages Router
- ALWAYS use React Server Components by default — add `'use client'` only for interactivity (useState, useEffect, event handlers, browser APIs)
- ALWAYS use Server Actions for data mutations — never API routes for internal operations
- ALWAYS use TypeScript strict mode — never plain JavaScript

### Data & Validation
- ALWAYS use Prisma ORM for ALL database access — parameterized queries, type-safe
- ALWAYS validate ALL user inputs with Zod before processing
- ALWAYS wrap data mutations with `withAuth()` for authentication verification
- ALWAYS use Supabase Auth for authentication (not custom auth)
- ALWAYS use Supabase RLS (Row Level Security) per table as defense-in-depth

### Styling & Components
- ALWAYS use Tailwind CSS utility classes for styling
- ALWAYS use shadcn/ui as the component library (built on Radix UI)
- ALWAYS use the `cn()` utility (clsx + tailwind-merge) for conditional classes
- ALWAYS use `next/image` for images, `next/link` for navigation, `next/font` for fonts

### Tooling
- ALWAYS use npm as package manager (pnpm is also supported — delete `package-lock.json` and run `pnpm install` to switch)
- ALWAYS use Biome for linting and formatting
- ALWAYS use Vitest for unit/integration tests
- ALWAYS use Playwright for E2E tests
- ALWAYS use named exports (except `page.tsx` and `layout.tsx`)

---

## Never Use

### Framework
- NEVER use Pages Router patterns (`getServerSideProps`, `getStaticProps`, `_app.tsx`, `_document.tsx`)
- NEVER use client-side data fetching (`useEffect` + fetch) for data available at server render time
- NEVER use API routes for operations that should be Server Actions

### Styling
- NEVER use CSS modules, styled-components, Emotion, or any CSS-in-JS
- NEVER use inline style objects (`style={{ }}`)
- NEVER create custom CSS when a Tailwind utility exists

### Data
- NEVER use raw SQL queries — always Prisma query builder
- NEVER access database directly from components — use Server Actions or `lib/services/`
- NEVER skip Zod validation on any user input
- NEVER trust client-side data without server-side re-validation

### Tooling
- NEVER use yarn — use npm (or pnpm if the project has `pnpm-lock.yaml`)
- NEVER use ESLint + Prettier — use Biome
- NEVER use Jest — use Vitest
- NEVER use the `any` type — use proper TypeScript types or `unknown`
- NEVER use default exports (except Next.js `page.tsx` and `layout.tsx` conventions)

### Security
- NEVER store secrets in client-accessible code
- NEVER expose database connection strings to client
- NEVER skip auth wrapping (`withAuth`) on mutations
- NEVER disable Supabase RLS policies
