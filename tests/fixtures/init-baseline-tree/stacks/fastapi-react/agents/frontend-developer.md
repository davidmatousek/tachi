# Frontend Developer — Python FastAPI + React Supplement

## Stack Context

React 19 SPA with Vite 6 build tooling, TypeScript 5.5+ in strict mode, TanStack Query v5 for server state, Tailwind CSS v4 (CSS-first configuration), Biome for linting and formatting. Backend is a FastAPI async REST API at `/api/v1/`. Path alias `@/` maps to `src/`. Environment variable `VITE_API_URL` provides the API base URL. Vitest + React Testing Library for testing.

## Conventions

- ALWAYS use functional components with explicitly typed props interfaces; define `interface Props` per component
- ALWAYS use named exports for all modules; never default exports
- ALWAYS use TanStack Query v5 for all server state; define query key factories in `@/api/queryKeys.ts` with hierarchical invalidation
- ALWAYS use `gcTime` for garbage collection timing; `cacheTime` was renamed in v5
- ALWAYS use Tailwind CSS v4 with `@import "tailwindcss"` and `@theme` directive in `app.css`; no `tailwind.config.js`
- ALWAYS use `bg-linear-to-*` for gradients; `bg-gradient-to-*` was renamed in v4
- ALWAYS use CSS variable parenthesis syntax `bg-(--var)` not bracket syntax `bg-[--var]` for Tailwind v4
- ALWAYS use the `@/` path alias for imports from `src/`; configure in both `vite.config.ts` and `tsconfig.json`
- ALWAYS use `VITE_API_URL` from environment for the API base; wire through `@/api/client.ts`
- ALWAYS use Biome for linting and formatting; never ESLint or Prettier
- ALWAYS handle loading, error, and empty states in every component that fetches data
- ALWAYS use `unknown` with type narrowing when the type is uncertain
- ALWAYS use string union types (`type Status = 'active' | 'inactive'`) instead of `enum`
- ALWAYS store auth tokens in `httpOnly` cookies set by the backend; never manage tokens in frontend code

## Anti-Patterns

- NEVER use `React.FC<Props>`; use explicit function signatures with typed props
- NEVER use `any` type; use `unknown` with runtime narrowing
- NEVER use `useEffect` for data fetching; use TanStack Query hooks (`useQuery`, `useMutation`)
- NEVER use class components
- NEVER use CSS Modules, styled-components, or inline `style` objects; use Tailwind utilities exclusively
- NEVER create barrel files (`index.ts`) in large directories; import from source modules directly
- NEVER use `localStorage` or `sessionStorage` for auth tokens; rely on `httpOnly` cookies
- NEVER use `tailwind.config.js`; use CSS-first `@theme` directive in Tailwind v4
- NEVER use `bg-gradient-to-*`; use `bg-linear-to-*` (v4 rename)
- NEVER use `cacheTime` in TanStack Query options; use `gcTime` (v5 rename)
- NEVER hardcode API base URLs; read from `VITE_API_URL`
- NEVER use `dangerouslySetInnerHTML` with user-provided content

## Guardrails

- TypeScript strict mode (`"strict": true` in `tsconfig.json`) is non-negotiable; never disable or weaken it
- Component files: PascalCase `.tsx` (`UserProfile.tsx`); hooks: `use` prefix camelCase `.ts` (`useAuth.ts`); utilities: camelCase `.ts` (`client.ts`)
- Maximum component file size: 200 lines; extract sub-components or custom hooks when exceeded
- All component props must be defined as named TypeScript interfaces, not inline object types
- ALWAYS test behavior and user interactions, NEVER test implementation details
- ALWAYS query by accessible roles (`getByRole`), labels (`getByLabelText`), or text (`getByText`); avoid test IDs unless no accessible query exists
- ALWAYS wrap components using TanStack Query hooks in `QueryClientProvider` with `retry: false` for tests
- ALWAYS use `userEvent` from `@testing-library/user-event` for simulating interactions; never `fireEvent`
- ALWAYS co-locate component tests as `ComponentName.test.tsx` in the same directory
- No `any` escape hatches in test files; test utilities and mocks must be fully typed
