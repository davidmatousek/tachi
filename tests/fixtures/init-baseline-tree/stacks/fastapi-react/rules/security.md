# Security Rules — FastAPI + React

Stack-specific OWASP Top 10 mitigations for Python FastAPI backend and React frontend.

---

## A01 — Broken Access Control

- ALWAYS use `Depends(get_current_user)` on every authenticated route.
- ALWAYS verify resource ownership in the endpoint before returning data.
- NEVER rely on frontend-only route guards for access control.

## A02 — Cryptographic Failures

- ALWAYS hash passwords with Argon2 via `passlib[argon2]`.
- ALWAYS store JWT access tokens in httpOnly, Secure, SameSite cookies.
- NEVER store tokens in localStorage or sessionStorage.
- ALWAYS use short-lived access tokens (15 min) with refresh token rotation.
- NEVER log tokens, passwords, or PII to any log sink.

## A03 — Injection

- ALWAYS use SQLAlchemy ORM queries or `select()` with bound parameters via asyncpg.
- NEVER use `text()` with f-strings or `.format()` interpolation.
- ALWAYS validate all request inputs through Pydantic schemas at the API boundary.

## A04 — Insecure Design

- ALWAYS separate public routes (`/auth`, `/health`) from authenticated routes.
- ALWAYS rate-limit authentication endpoints with `slowapi` or middleware.

## A05 — Security Misconfiguration

- ALWAYS set `model_config = ConfigDict(extra="forbid")` on Pydantic models.
- ALWAYS specify explicit CORS origins in `CORSMiddleware`.
- NEVER use `allow_origins=["*"]` when `allow_credentials=True`.
- ALWAYS add security headers via middleware: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Strict-Transport-Security`, `Content-Security-Policy`.

## A06 — Vulnerable Components

- ALWAYS pin dependency versions in `pyproject.toml` and `package.json`.
- ALWAYS run `uv audit` (backend) and `npm audit` (frontend) before releases.

## A07 — Authentication Failures

- NEVER reveal whether a username or email exists during login or registration.
- ALWAYS return a generic "Invalid credentials" message on auth failure.

## A08 — Data Integrity Failures

- ALWAYS validate JWT signatures server-side using `python-jose[cryptography]`.
- NEVER trust unsigned or client-modified tokens.

## A09 — Logging & Monitoring

- ALWAYS emit structured JSON logs for auth events (login, logout, failed attempts).
- NEVER log passwords, tokens, or secrets in any log level.

## A10 — SSRF

- ALWAYS validate and allowlist URLs before making server-side HTTP requests with httpx.
- NEVER pass user-supplied URLs directly to `httpx.get()` or `httpx.post()`.

---

## Frontend Security (React)

- React escapes JSX by default — preserve this behavior.
- NEVER use `dangerouslySetInnerHTML` with user-supplied content.
- ALWAYS set `SameSite=Strict` (or `Lax`) and `Secure` flags on cookies.
- ALWAYS enforce CSP headers from the backend to restrict inline scripts.
