# Next.js + Supabase Security Rules

<!-- Stack rules file — loaded by ALL agents when the nextjs-supabase pack is active -->
<!-- Copied to .claude/rules/stack/ at activation time -->
<!-- OWASP Top 10 mapped — zero-exceptions enforcement -->

These security rules apply to ALL agents when the nextjs-supabase stack pack is active.
Security patterns are non-optional defaults — agents MUST apply them without explicit request.

---

## Input Validation (OWASP A03: Injection)

- ALWAYS validate ALL user inputs with Zod schemas before any processing — in Server Actions, API Route Handlers, and middleware — no exceptions
- ALWAYS define Zod schemas in `lib/validations/` and share between client and server
- ALWAYS use Prisma parameterized queries for ALL database access — NEVER raw SQL
- ALWAYS sanitize user-generated HTML content with DOMPurify before rendering
- NEVER use `$queryRawUnsafe()` or `$executeRawUnsafe()` under any circumstances
- NEVER use `$queryRaw` or `$executeRaw` unless no Prisma Client API alternative exists — when required, ALWAYS use tagged template literals for parameterization
- NEVER interpolate user input into query strings, URLs, or shell commands

---

## Authentication (OWASP A07: Identification and Authentication Failures)

- ALWAYS wrap every data-mutating Server Action with `withAuth()` as the FIRST operation — no exceptions
- ALWAYS verify authentication in every API Route Handler that performs a data mutation — NEVER allow unauthenticated writes
- ALWAYS use Supabase Auth for authentication — NEVER custom auth implementations
- ALWAYS verify sessions server-side with `getUser()` — NEVER rely on `getSession()` alone (local JWT may be stale)
- ALWAYS implement session timeout and refresh token rotation via Supabase config
- ALWAYS rate-limit authentication endpoints (signup, signin, password reset)

---

## Authorization (OWASP A01: Broken Access Control)

- ALWAYS enforce authentication in `middleware.ts` for ALL protected routes — every route group serving authenticated content MUST be covered, not just `/dashboard/*`
- ALWAYS configure Supabase RLS policies on EVERY table — no exceptions
- ALWAYS verify resource ownership in queries (`WHERE userId = currentUser.id`)
- ALWAYS apply principle of least privilege in RLS policies — deny by default, allow explicitly
- NEVER disable RLS policies for convenience — fix the policy instead
- NEVER trust client-side authorization checks — always verify server-side

---

## Data Protection (OWASP A02: Cryptographic Failures)

- ALWAYS use HTTPS for all connections (enforced by Vercel)
- ALWAYS manage secrets through Vercel environment variables — NEVER in code or committed `.env` files
- ALWAYS use `NEXT_PUBLIC_` prefix ONLY for values safe for client exposure
- NEVER expose `SUPABASE_SERVICE_ROLE_KEY`, `DATABASE_URL`, or any secret to client-side code
- NEVER log sensitive data (passwords, tokens, PII, credit card numbers)
- NEVER return full database records with sensitive fields to client — select only needed fields

---

## Security Headers (OWASP A05: Security Misconfiguration)

- ALWAYS configure Content-Security-Policy headers in `next.config.js`
- ALWAYS set `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy` headers
- ALWAYS use secure cookie options: `httpOnly`, `secure`, `sameSite: 'lax'`
- NEVER expose stack traces or internal error details to clients — return safe error messages
- NEVER disable CORS protections

---

## Server Action and Route Handler Security

- ALWAYS follow this order in every Server Action: (1) `withAuth()` (2) Zod `.parse()` (3) business logic (4) typed response
- ALWAYS follow this order in every API Route Handler: (1) verify caller identity (signature/key/session) (2) Zod `.parse()` (3) business logic (4) typed response
- ALWAYS verify webhook signatures before processing webhook payloads — NEVER trust unverified webhook requests
- ALWAYS use try/catch — never let exceptions propagate to client
- ALWAYS return structured responses: `{ success: boolean, data?: T, error?: string }`
- NEVER pass unsanitized user input to external APIs or services

---

## Dependency Security (OWASP A06: Vulnerable and Outdated Components)

- ALWAYS run `npm audit` before merging PRs — zero critical/high vulnerabilities allowed
- ALWAYS update critical vulnerability patches within 48 hours
- NEVER add dependencies without reviewing their security posture and maintenance status
