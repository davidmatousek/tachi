# Security Analyst — Next.js + Supabase Supplement

## Stack Context

Next.js 15+ App Router with Server Components and Server Actions, Supabase Auth (JWT-based sessions), Supabase Row Level Security (RLS), Prisma ORM (parameterized queries), Zod for input validation, middleware-based route protection, Vercel deployment with environment variables, Content Security Policy headers in next.config.js.

## Conventions

OWASP Top 10 mapped to Next.js + Supabase + Prisma + Vercel:

- **A01 Broken Access Control**: ALWAYS enforce auth in `middleware.ts` for all `/dashboard/*` and protected routes. ALWAYS configure Supabase RLS policies on every table with user data. ALWAYS wrap every Server Action mutation with `withAuth()` before any logic. ALWAYS verify resource ownership server-side (`WHERE userId = currentUser.id`). ALWAYS use route groups `(auth)` vs `(public)` to enforce layout-level protection.
- **A02 Cryptographic Failures**: ALWAYS delegate password hashing to Supabase Auth (bcrypt). ALWAYS use HTTPS (enforced by Vercel). ALWAYS store secrets in Vercel environment variables, never in code or `.env` committed to git. ALWAYS use `NEXT_PUBLIC_` prefix only for non-sensitive, client-safe values.
- **A03 Injection**: ALWAYS use Prisma parameterized queries; NEVER use `$queryRawUnsafe()` or string-interpolated SQL. ALWAYS validate all inputs with Zod schemas before processing in Server Actions. ALWAYS use Prisma query builder for dynamic filters and sorting. ALWAYS sanitize user-generated HTML with DOMPurify before rendering with `dangerouslySetInnerHTML`.
- **A04 Insecure Design**: ALWAYS implement rate limiting on signup, signin, password reset, and email verification endpoints. ALWAYS rely on Server Actions' built-in CSRF protection. ALWAYS enforce least privilege in RLS policies (deny by default, allow explicitly). ALWAYS use Zod `.transform()` and `.refine()` for business rule validation.
- **A05 Security Misconfiguration**: ALWAYS set secure cookie options (`httpOnly`, `secure`, `sameSite: 'lax'`). ALWAYS configure Content Security Policy, X-Frame-Options, and Permissions-Policy headers in `next.config.js`. NEVER expose stack traces or internal error details to clients; return safe error messages only. ALWAYS disable Supabase REST API public access for tables without RLS.
- **A06 Vulnerable Components**: ALWAYS audit dependencies with `npm audit` before merging PRs. ALWAYS pin exact dependency versions in `package.json`. ALWAYS review Supabase client library changelogs for security patches. ALWAYS update critical vulnerabilities within 48 hours.
- **A07 Auth Failures**: ALWAYS use Supabase Auth for session management; NEVER implement custom JWT logic. ALWAYS validate the session on every protected Server Component render and Server Action. ALWAYS implement session timeout and refresh token rotation via Supabase config. ALWAYS use `getUser()` (verifies with Supabase server) instead of `getSession()` (reads local JWT only) for auth checks.
- **A08 Data Integrity**: ALWAYS validate Server Action inputs with Zod before any database write. ALWAYS use Prisma transactions for multi-step mutations. NEVER trust client-side form data without server-side re-validation.
- **A09 Logging & Monitoring**: ALWAYS log auth failures, access denials, and RLS policy violations server-side. NEVER log passwords, tokens, PII, or Supabase service role keys. ALWAYS use structured logging with request IDs for traceability.
- **A10 SSRF**: ALWAYS validate and allowlist URLs before making server-side fetch requests. NEVER pass user-supplied URLs directly to `fetch()` in Server Components or API routes.

## Anti-Patterns

- NEVER skip Zod validation on any Server Action or API route handler
- NEVER use `$queryRawUnsafe()` or raw SQL string interpolation; use Prisma parameterized queries exclusively
- NEVER trust client-side auth checks alone; ALWAYS verify server-side with `getUser()`
- NEVER expose `SUPABASE_SERVICE_ROLE_KEY` or database connection strings to client bundles
- NEVER disable RLS policies for convenience; fix the policy or create a new scoped policy
- NEVER commit `.env.local` or any file containing secrets to git
- NEVER return full error objects or stack traces to the client
- NEVER use HTTP for external API calls; HTTPS only
- NEVER use `dangerouslySetInnerHTML` without sanitization
- NEVER store session tokens in localStorage; use httpOnly cookies via Supabase Auth

## Guardrails

- PR security review checklist: input validation, auth wrapping, RLS policies, no raw SQL, no exposed secrets, CSP headers
- All Supabase tables MUST have RLS policies enabled and tested before deployment
- All Server Actions MUST follow this order: (1) `withAuth()` (2) Zod validation (3) business logic
- Rate limiting MUST be configured on: signup, signin, password reset, email verification
- CSP, X-Frame-Options, and Permissions-Policy headers MUST be configured in `next.config.js`
- `npm audit` MUST pass with zero critical/high vulnerabilities before merge
- Every `middleware.ts` change MUST be reviewed for auth bypass regressions
- Supabase RLS policies MUST be tested with both authenticated and unauthenticated roles
