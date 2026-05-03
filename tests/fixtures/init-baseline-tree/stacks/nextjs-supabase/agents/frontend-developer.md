# Frontend Developer — Next.js + Supabase Supplement

## Stack Context

Next.js 15+ App Router with React Server Components, TypeScript strict mode, Tailwind CSS v4, shadcn/ui (Radix-based), npm, Biome (linting + formatting), Vitest + React Testing Library for unit/integration tests. Supabase provides auth, database, and storage. Prisma is the ORM. Deployment targets Vercel.

## Conventions

- ALWAYS use Server Components by default; add `'use client'` only when the component needs useState, useEffect, event handlers, or browser APIs
- ALWAYS fetch data in Server Components using async/await; pass data down as props to Client Components
- ALWAYS use App Router file conventions: `page.tsx`, `layout.tsx`, `loading.tsx`, `error.tsx`, `not-found.tsx`
- ALWAYS use route groups `(auth)`, `(dashboard)`, `(marketing)` for layout segmentation
- ALWAYS use Server Actions for mutations; co-locate in a `actions.ts` file next to the route that uses them
- ALWAYS validate Server Action inputs with Zod before any data access
- ALWAYS use `next/image` for images, `next/link` for navigation, `next/font` for fonts
- ALWAYS use shadcn/ui as the component base; extend with Tailwind variants via `cva`
- ALWAYS use the `cn()` utility (clsx + tailwind-merge) for conditional class composition
- ALWAYS use named exports for components; use default exports only for `page.tsx` and `layout.tsx`
- ALWAYS use TypeScript strict mode with explicit return types on exported functions
- ALWAYS organize imports: React/Next.js → third-party → `@/lib` → `@/components` → types
- ALWAYS co-locate component tests as `ComponentName.test.tsx` in the same directory
- ALWAYS use the `@/` path alias for imports from the project root
- ALWAYS use `Suspense` boundaries with `loading.tsx` or inline fallbacks for async Server Components
- ALWAYS handle three UI states: loading (skeleton), error (error.tsx or boundary), empty (explicit empty state)

## Anti-Patterns

- NEVER use Pages Router patterns (`getServerSideProps`, `getStaticProps`, `getInitialProps`)
- NEVER use `useEffect` + `fetch` for data available at request time; fetch in Server Components instead
- NEVER use CSS modules, styled-components, CSS-in-JS, or inline `style` objects; use Tailwind utilities exclusively
- NEVER use string concatenation for classNames; use the `cn()` utility
- NEVER use default exports except where Next.js requires them (`page.tsx`, `layout.tsx`)
- NEVER import React in Server Components; it is available globally in the App Router
- NEVER create API route handlers for operations that can be Server Actions; reserve API routes for webhooks and third-party integrations
- NEVER use `useRouter` from `next/router`; use `next/navigation` exclusively
- NEVER use yarn; use npm (or pnpm if the project has `pnpm-lock.yaml`)
- NEVER use ESLint or Prettier; use Biome for linting and formatting
- NEVER bypass Zod validation in Server Actions; every action begins with `schema.safeParse()` and returns errors in the result object
- NEVER trust client-side auth checks for authorization decisions; ALWAYS verify server-side with `getUser()`
- NEVER fetch protected or authenticated data from Client Components; use Server Components or Server Actions exclusively
- NEVER access Supabase client directly in components; use server-side helpers from `@/lib/supabase`

## Guardrails

- Component files: PascalCase (`UserProfile.tsx`); utility files: camelCase (`formatDate.ts`)
- Route segment directories: kebab-case (`user-settings/`); route groups: parenthesized (`(dashboard)/`)
- Maximum component file size: 200 lines; extract sub-components or hooks when exceeded
- All component props must be defined as named TypeScript interfaces, not inline types
- No `any` type; use `unknown` with type narrowing when the type is uncertain
- All `'use client'` components must be leaf nodes or near-leaf nodes in the component tree
- Server Actions must live in files marked with `'use server'` at the top, or be inline with the `"use server"` directive
- Images must specify `width`, `height`, or `fill` on `next/image` to prevent layout shift
- Forms must use `useFormStatus` for pending states and `useActionState` for error handling
