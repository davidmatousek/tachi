# Security Analyst — FastAPI + React Supplement

## Stack Context

FastAPI with async endpoints, React 18+ SPA served separately, PostgreSQL via asyncpg with parameterized queries, Pydantic v2 for request/response validation, JWT authentication with httpOnly/SameSite/Secure cookies, Argon2 password hashing via passlib[argon2], explicit CORS origins, structured JSON logging, Alembic for migrations.

## Conventions

OWASP Top 10 mapped to FastAPI + React + asyncpg + Pydantic v2:

- **A01 Broken Access Control**: ALWAYS enforce auth via `Depends(get_current_user)` on every protected endpoint. ALWAYS verify resource ownership server-side (`WHERE owner_id = $1`). ALWAYS use FastAPI dependency injection for role-based access control. ALWAYS define separate router groups for public vs authenticated endpoints.
- **A02 Cryptographic Failures**: ALWAYS hash passwords with Argon2 via `passlib[argon2]`. NEVER use bcrypt, MD5, or SHA for password hashing. ALWAYS issue JWTs with RS256 or HS256 with a high-entropy secret (>=256 bits). ALWAYS set httpOnly, Secure, and SameSite=Lax on auth cookies. ALWAYS store secrets in environment variables, never in code.
- **A03 Injection**: ALWAYS use Pydantic v2 models to validate all request bodies, query params, and path params at the API boundary. ALWAYS use asyncpg parameterized queries (`$1`, `$2` placeholders); NEVER use f-strings or `.format()` with `connection.execute()` or `text()`. ALWAYS use SQLAlchemy ORM query builder for dynamic filters.
- **A04 Insecure Design**: ALWAYS rate-limit `/auth/login`, `/auth/register`, `/auth/reset-password`, and `/auth/token-refresh` endpoints. ALWAYS return identical error messages for wrong email and wrong password to prevent user enumeration. ALWAYS enforce least privilege on database roles.
- **A05 Security Misconfiguration**: ALWAYS set `extra="forbid"` on Pydantic request models to reject unexpected fields. ALWAYS configure explicit CORS origins; NEVER use `allow_origins=["*"]` when `allow_credentials=True`. ALWAYS set security response headers: X-Content-Type-Options (nosniff), X-Frame-Options (DENY), Content-Security-Policy, Strict-Transport-Security. NEVER expose stack traces in production; use custom exception handlers.
- **A06 Vulnerable Components**: ALWAYS audit dependencies with `pip audit` or `safety check` before merging. ALWAYS pin exact versions in `requirements.txt` or `pyproject.toml`. ALWAYS update critical CVEs within 48 hours.
- **A07 Auth Failures**: ALWAYS validate JWT signature and expiration server-side on every protected request. ALWAYS implement token refresh rotation (invalidate old refresh token on use). ALWAYS set reasonable JWT expiry (access: 15min, refresh: 7d max).
- **A08 Data Integrity**: ALWAYS validate request payloads with Pydantic before any database write. ALWAYS use database transactions for multi-step mutations. NEVER trust client-side computed values for pricing, permissions, or ownership.
- **A09 Logging & Monitoring**: ALWAYS log auth events (login, logout, failure, token refresh) as structured JSON with request IDs. NEVER log passwords, tokens, PII, or database connection strings. ALWAYS include user ID and IP in auth failure logs for forensic traceability.
- **A10 SSRF**: ALWAYS validate and allowlist URLs before making server-side HTTP requests with `httpx` or `aiohttp`. NEVER pass user-supplied URLs directly to server-side HTTP clients.

## Anti-Patterns

- NEVER store JWT tokens in localStorage or sessionStorage; use httpOnly cookies exclusively
- NEVER use `text()` with f-strings or string concatenation for SQL; use parameterized queries
- NEVER set `allow_origins=["*"]` with `allow_credentials=True` in CORSMiddleware
- NEVER log passwords, tokens, PII, or connection strings
- NEVER use `dangerouslySetInnerHTML` with user-supplied content in React components
- NEVER return different error messages for invalid email vs invalid password (user enumeration)
- NEVER use bcrypt, MD5, or SHA for password hashing; use Argon2 exclusively
- NEVER use HS256 with a weak or short secret for JWT signing
- NEVER skip Pydantic validation on any endpoint; raw `Request.json()` is forbidden
- NEVER commit `.env` files or secrets to git

## Guardrails

- React escapes JSX by default; this neutralizes most reflected XSS without extra work
- SPA + httpOnly SameSite cookies provide natural CSRF protection; do not weaken with `SameSite=None`
- PR security checklist: Pydantic validation on all inputs, `Depends(get_current_user)` on protected routes, no raw SQL, no exposed secrets, CORS explicit origins, security headers present
- All auth endpoints MUST be rate-limited before deployment
- Every FastAPI endpoint with side effects MUST follow: (1) auth dependency (2) Pydantic validation (3) business logic
- `pip audit` MUST pass with zero critical/high vulnerabilities before merge
- JWT validation MUST occur server-side on every protected request; never trust client-decoded claims
- All server-side outbound HTTP requests MUST validate destination URLs against an allowlist
