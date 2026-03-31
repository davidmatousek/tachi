---
source_agent: control-analyzer
extracted_from: .claude/agents/tachi/control-analyzer.md
version: 1.0.0
---

# Control Categories and Detection Patterns

This reference defines the 8 compensating control categories, their STRIDE-to-control mapping, and detection patterns for Phase A scanning.

## STRIDE-to-Control-Category Mapping

This canonical mapping determines which control categories to search for when analyzing threats in each STRIDE/AI category. When a threat of a given category is being analyzed, search the component's files for controls in ALL mapped categories.

| STRIDE Category | Control Categories to Search | Rationale |
|----------------|----------------------------|-----------|
| **Spoofing** | Authentication, Access Control | Identity verification and access restriction prevent impersonation |
| **Tampering** | Input Validation | Schema enforcement, sanitization, and parameterized queries prevent unauthorized modification |
| **Repudiation** | Logging/Audit | Structured logging and audit trails provide accountability evidence |
| **Information Disclosure** | Encryption | TLS/SSL, at-rest encryption, and hashing prevent unauthorized data exposure |
| **Denial of Service** | Rate Limiting | Rate limiters, throttling, and circuit breakers prevent resource exhaustion |
| **Elevation of Privilege** | Access Control | RBAC/ABAC, permission checks, and role guards prevent unauthorized access escalation |
| **Agentic** (AI) | All 8 categories | Agentic threats span tool abuse, autonomy, and orchestration — check all control types |
| **LLM** (AI) | Input Validation, Logging/Audit | Prompt injection requires input sanitization; model behavior requires audit trails |

**Multi-category mapping**: When a STRIDE category maps to multiple control categories (e.g., Spoofing -> Authentication + Access Control), search for controls in ALL mapped categories. A threat is classified as "Control Found" when at least one mapped category has a detected control. It is "Partial Control" when some but not all relevant categories have controls. It is "No Control Found" only when no mapped categories have any detected controls.

**Agentic category special handling**: The "Agentic" AI category maps to all 8 control categories because agentic threats (tool abuse, excessive autonomy, cascading failures) can be mitigated by any combination of security controls. For Agentic threats, use the highest-effectiveness single control found across all categories — do not require all 8 categories to have controls.

## Detection Patterns by Control Category

For each of the 8 control categories, the following defines the pattern indicators to search for in Phase A, the evidence criteria for Phase B semantic analysis, and snippet guidance for evidence collection.

### Category 1: Authentication (`authentication`)

Verifies caller identity before granting access to protected resources.

**Pattern indicators**:
- Auth middleware: `authMiddleware`, `requireAuth`, `isAuthenticated`, `ensureAuth`, `authenticate`, `passport.authenticate`
- JWT verification: `jwt.verify`, `jsonwebtoken`, `jose`, `jwtVerify`, `decodeJwt`, `verifyToken`, `validateToken`
- OAuth/SSO providers: `auth0`, `cognito`, `firebase-admin/auth`, `passport-oauth`, `openid-connect`, `saml`
- Session management: `express-session`, `cookie-session`, `session.userId`, `req.session`, `session_store`
- Password hashing: `bcrypt`, `argon2`, `scrypt`, `pbkdf2`, `hashPassword`, `verifyPassword`, `comparePassword`
- API key verification: `x-api-key`, `apiKeyAuth`, `verifyApiKey`, `api_key_required`
- Bearer tokens: `Bearer `, `authorization?.split`, `extractBearerToken`, `getTokenFromHeader`

**Evidence criteria** (Phase B):
- KEEP: Middleware function that checks credentials and calls `next()` or returns 401/403
- KEEP: Route guard or decorator applied to endpoint definitions (`@Authenticated`, `@UseGuards(AuthGuard)`)
- KEEP: Token validation logic that extracts, decodes, and verifies a token before proceeding
- REJECT: Auth-related imports with no corresponding verification logic in the file
- REJECT: Type definitions for auth tokens or user sessions without enforcement
- REJECT: Test files that mock `req.user` or stub auth middleware
- REJECT: Commented-out authentication checks

**Common libraries/frameworks**: `jsonwebtoken`, `jose`, `passport`, `express-jwt`, `@nestjs/passport`, `auth0`, `firebase-admin`, `next-auth`, `django.contrib.auth`, `flask-login`, `spring-security`, `gorilla/sessions`

**Snippet guidance**: Capture the middleware function signature through the verification logic (e.g., token extraction + `jwt.verify` call + `next()` or error response). Prefer the function that enforces auth, not the route that applies it.

### Category 2: Input Validation (`input-validation`)

Validates, sanitizes, or constrains user-supplied input before processing.

**Pattern indicators**:
- Schema validation: `joi.object`, `z.object`, `yup.object`, `class-validator`, `@IsString`, `@IsEmail`, `validate()`, `validateSync`, `safeParse`
- Python validation: `pydantic.BaseModel`, `marshmallow.Schema`, `cerberus`, `voluptuous`, `@validator`, `field_validator`
- Sanitization: `DOMPurify.sanitize`, `sanitize-html`, `bleach.clean`, `xss()`, `escape()`, `stripTags`
- Parameterized queries: `$1`, `?` placeholders in SQL, `prepare()`, `parameterize`, ORM query builders (`prisma`, `sequelize`, `sqlalchemy`, `knex`)
- Content-type enforcement: `content-type`, `accepts()`, `type: 'json'` in body parser config
- Request validation middleware: `celebrate`, `express-validator`, `body()`, `param()`, `query()`, `validationResult`

**Evidence criteria** (Phase B):
- KEEP: Validation schema applied to request body, params, query, or headers at an endpoint
- KEEP: Sanitization function called on user input before storage or rendering
- KEEP: Parameterized query or ORM usage that prevents SQL injection
- KEEP: Middleware that rejects requests failing validation (returns 400/422)
- REJECT: Internal data transformation or type coercion not at an input boundary
- REJECT: Schema definitions in isolation (not wired to an endpoint or middleware chain)
- REJECT: Test assertions that validate response shapes
- REJECT: Validation only in client-side code (not a server-side control)

**Common libraries/frameworks**: `joi`, `zod`, `yup`, `class-validator`, `express-validator`, `celebrate`, `pydantic`, `marshmallow`, `cerberus`, `FluentValidation`, `Bean Validation` (JSR 380), `go-playground/validator`

**Snippet guidance**: Capture the schema definition and its application point (e.g., `const schema = z.object({...}); app.post('/api', validate(schema), handler)`). If schema and application are in separate files, prefer the application/middleware registration.

### Category 3: Rate Limiting (`rate-limiting`)

Constrains request throughput to prevent resource exhaustion and abuse.

**Pattern indicators**:
- Rate limiter middleware: `rateLimit`, `express-rate-limit`, `rate_limit`, `@throttle`, `@Throttle`, `RateLimiter`, `slowDown`
- Throttling libraries: `bottleneck`, `p-throttle`, `limiter`, `token-bucket`, `sliding-window`
- Circuit breakers: `opossum`, `cockatiel`, `CircuitBreaker`, `circuitBreaker`, `@CircuitBreaker`
- API gateway policies: `x-ratelimit`, `X-RateLimit-Limit`, `retry-after`, `429`, `Too Many Requests`
- Request quotas: `windowMs`, `max:`, `limit:`, `points:`, `duration:`, `keyGenerator`
- Python rate limiting: `flask-limiter`, `django-ratelimit`, `slowapi`, `limits`

**Evidence criteria** (Phase B):
- KEEP: Rate limiter middleware with configured thresholds (window, max requests) applied to routes or the application
- KEEP: Circuit breaker wrapping outgoing service calls with failure thresholds
- KEEP: API response headers setting rate limit values
- KEEP: Decorator or annotation applying rate limits to specific endpoints
- REJECT: Client-side retry logic or exponential backoff on outgoing requests (resilience pattern, not a server-side control)
- REJECT: Rate limiter imported but not mounted on any route or application
- REJECT: Rate limit configuration in comments or documentation only
- REJECT: Test files simulating rate limit responses

**Common libraries/frameworks**: `express-rate-limit`, `rate-limiter-flexible`, `bottleneck`, `opossum`, `cockatiel`, `flask-limiter`, `django-ratelimit`, `slowapi`, `resilience4j`, `go-rate`, `throttled`

**Snippet guidance**: Capture the rate limiter instantiation with its configuration (window, max, key generator) and the middleware registration line. Show the configured thresholds, not just the import.

### Category 4: Encryption (`encryption`)

Protects data confidentiality through encryption at rest, in transit, or via hashing of sensitive values.

**Pattern indicators**:
- TLS/SSL: `https.createServer`, `ssl_context`, `certfile`, `keyfile`, `tls.connect`, `HTTPS`, `force_ssl`, `ssl: true`
- HTTPS enforcement: `redirect_to_https`, `requireHTTPS`, `hsts`, `Strict-Transport-Security`
- Crypto operations: `crypto.createCipher`, `crypto.createHash`, `encrypt()`, `decrypt()`, `AES`, `RSA`, `createCipheriv`
- Password/token hashing: `bcrypt.hash`, `argon2.hash`, `scrypt`, `pbkdf2`, `hashSync`, `SHA-256`, `SHA-512` (with salt)
- Key management: `KMS`, `keyVault`, `secretManager`, `ENCRYPTION_KEY`, `process.env.*_KEY`, `getSecret`
- At-rest encryption: `encryptedField`, `@Encrypted`, `encrypt: true`, `columnEncrypt`, `pgcrypto`, `aes_encrypt`
- Secure random: `crypto.randomBytes`, `crypto.randomUUID`, `secrets.token_urlsafe`, `SecureRandom`

**Evidence criteria** (Phase B):
- KEEP: Encryption applied to sensitive data fields (passwords, tokens, PII, secrets) before storage or transmission
- KEEP: TLS/SSL configuration in production server setup
- KEEP: HTTPS enforcement middleware or redirect logic
- KEEP: Key management integration loading encryption keys from secure stores
- REJECT: Hash functions used for non-security purposes (ETags, cache keys, content deduplication, checksum verification)
- REJECT: TLS configuration in development-only files or local environment setup
- REJECT: Crypto imports with no corresponding encrypt/decrypt/hash calls
- REJECT: Encryption in test fixtures or mock data generators

**Common libraries/frameworks**: `crypto` (Node.js built-in), `bcrypt`, `argon2`, `tweetnacl`, `sodium-native`, `cryptography` (Python), `PyCryptodome`, `Bouncy Castle`, `Tink`, `golang.org/x/crypto`, `ring` (Rust)

**Snippet guidance**: Capture the encryption or hashing call with its algorithm and the data it protects (e.g., `bcrypt.hash(password, saltRounds)` or `crypto.createCipheriv('aes-256-gcm', key, iv)`). Show what data is being protected, not just that crypto exists.

### Category 5: Logging/Audit (`logging-audit`)

Records security-relevant events for accountability, forensics, and compliance.

**Pattern indicators**:
- Structured logging: `winston`, `pino`, `bunyan`, `log4j`, `logback`, `slog`, `loguru`, `structlog`, `zerolog`
- Audit-specific: `auditLog`, `audit_trail`, `logSecurityEvent`, `recordActivity`, `trackAction`, `auditEntry`
- Security event logging: `loginAttempt`, `authFailure`, `accessDenied`, `permissionDenied`, `unauthorizedAccess`, `dataAccess`
- Request logging middleware: `morgan`, `express-winston`, `requestLogger`, `accessLog`, `httpLogger`
- Compliance logging: `gdpr`, `hipaa`, `sox`, `complianceLog`, `dataRetention`
- Event tracking: `eventEmitter.emit('security'`, `securityEvent`, `incidentLog`

**Evidence criteria** (Phase B):
- KEEP: Logging of authentication attempts (success and failure) with user identifiers
- KEEP: Logging of authorization decisions (permission grants and denials)
- KEEP: Logging of data access events (who accessed what, when)
- KEEP: Logging of configuration or permission changes
- KEEP: Structured logging middleware capturing request metadata (IP, user agent, path, status code)
- REJECT: Generic `console.log` or `print` statements without security context
- REJECT: Debug-level logging that does not capture security-relevant events
- REJECT: Logging in test files or test utilities
- REJECT: Log configuration without actual log invocations in security-relevant code paths

**Common libraries/frameworks**: `winston`, `pino`, `bunyan`, `morgan`, `log4j2`, `logback`, `SLF4J`, `slog`, `zerolog`, `loguru`, `structlog`, `Serilog`, `NLog`, `tracing` (Rust)

**Snippet guidance**: Capture the log call that records a security event, showing the event type and the data being logged (e.g., `logger.info({ event: 'auth_failure', userId, ip }, 'Login failed')`). Prefer security event logging over generic request logging.

### Category 6: CSRF Protection (`csrf-protection`)

Prevents cross-site request forgery by validating request origin or embedding anti-forgery tokens.

**Pattern indicators**:
- CSRF middleware: `csurf`, `csrf-csrf`, `csrfProtection`, `@csrf_protect`, `CsrfViewMiddleware`, `csrf_exempt`
- Token patterns: `csrfToken`, `_csrf`, `antiForgery`, `__RequestVerificationToken`, `authenticity_token`
- Cookie attributes: `SameSite=Strict`, `SameSite=Lax`, `sameSite: 'strict'`, `sameSite: 'lax'`
- Origin validation: `origin`, `referer`, `allowedOrigins`, `checkOrigin`, `validateOrigin`
- Double-submit: `doubleCsrf`, `double-submit`, `csrfCookie`
- Custom header requirements: `X-Requested-With`, `X-CSRF-Token`, `x-xsrf-token`
- Framework built-ins: `@csrf_protect` (Django), `protect_from_forgery` (Rails), `@EnableCsrf` (Spring)

**Evidence criteria** (Phase B):
- KEEP: CSRF middleware applied to state-changing routes (POST, PUT, DELETE, PATCH)
- KEEP: Anti-forgery token generation AND validation both present
- KEEP: SameSite cookie attribute set to `Strict` or `Lax` on session cookies
- KEEP: Origin or referer header validation on state-changing endpoints
- REJECT: `SameSite=None` (weakens protection rather than providing it)
- REJECT: CSRF middleware imported but explicitly disabled (`csrf: false`, `csrf_exempt` on all routes)
- REJECT: Token generation without corresponding validation logic
- REJECT: CSRF protection only in test or development configuration

**Common libraries/frameworks**: `csurf`, `csrf-csrf`, `lusca`, `Django CSRF middleware`, `Rails CSRF protection`, `Spring Security CSRF`, `gorilla/csrf`, `Antiforgery` (.NET)

**Snippet guidance**: Capture the CSRF middleware registration on the application or router, showing it applied to state-changing endpoints. If token validation is the primary mechanism, show the validation check.

### Category 7: CSP/Security Headers (`csp-security-headers`)

Applies HTTP security headers to responses, reducing the attack surface for client-side vulnerabilities.

**Pattern indicators**:
- Header middleware: `helmet`, `helmet()`, `secure_headers`, `SecurityHeaders`, `@secure_headers`
- Content-Security-Policy: `Content-Security-Policy`, `contentSecurityPolicy`, `csp`, `CSP`, `script-src`, `style-src`, `default-src`
- Frame protection: `X-Frame-Options`, `frameguard`, `DENY`, `SAMEORIGIN`, `frame-ancestors`
- Content type: `X-Content-Type-Options`, `nosniff`, `noSniff`
- Transport security: `Strict-Transport-Security`, `hsts`, `max-age`, `includeSubDomains`
- Referrer policy: `Referrer-Policy`, `referrerPolicy`, `no-referrer`, `strict-origin`
- Permissions: `Permissions-Policy`, `permissionsPolicy`, `Feature-Policy`, `geolocation`, `camera`, `microphone`
- XSS filter: `X-XSS-Protection`, `xssFilter`

**Evidence criteria** (Phase B):
- KEEP: Security header middleware registered on the application (e.g., `app.use(helmet())`)
- KEEP: Individual security headers set on HTTP responses via middleware or response configuration
- KEEP: CSP directives that restrict script sources, style sources, or default sources
- KEEP: HSTS header with reasonable `max-age` (>= 31536000 recommended)
- REJECT: Security header constants defined but never applied to responses
- REJECT: Commented-out helmet or security header middleware
- REJECT: Headers set only in development or test configuration
- REJECT: Overly permissive CSP that effectively disables protection (`default-src *`, `script-src 'unsafe-inline' 'unsafe-eval' *`)

**Common libraries/frameworks**: `helmet`, `lusca`, `django-csp`, `secure` (Python), `Spring Security headers`, `Rack::Headers`, `gorilla/handlers`

**Snippet guidance**: Capture the middleware registration showing the header configuration (e.g., `app.use(helmet({ contentSecurityPolicy: { directives: { defaultSrc: ["'self'"] } } }))`). Show the directive values, not just that the middleware is used.

### Category 8: Access Control (`access-control`)

Enforces authorization rules to ensure users can only access resources and perform actions they are permitted to.

**Pattern indicators**:
- RBAC/ABAC: `rbac`, `abac`, `hasRole`, `hasPermission`, `checkPermission`, `requireRole`, `@Roles`, `@Permissions`
- Authorization middleware: `authorize`, `can()`, `ability`, `policy`, `guard`, `@UseGuards`, `@PreAuthorize`
- Libraries: `casl`, `casbin`, `oso`, `accesscontrol`, `node-casbin`
- ACL patterns: `acl`, `accessControlList`, `allowedRoles`, `permittedActions`
- Resource ownership: `req.user.id === resource.ownerId`, `isOwner`, `belongsTo`, `checkOwnership`
- Tenant isolation: `tenantId`, `organizationId`, `req.tenant`, `scope: 'tenant'`, `@TenantGuard`
- Scope checks: `scope`, `scopes`, `requiredScopes`, `hasScope`, `@Scopes`
- Framework decorators: `@Authorize`, `@PermissionRequired`, `@permission_required`, `@login_required`

**Evidence criteria** (Phase B):
- KEEP: Permission check executed before resource access (middleware, guard, or inline check)
- KEEP: Role-based guard or decorator applied to route or controller
- KEEP: Resource ownership validation comparing requesting user to resource owner
- KEEP: Tenant isolation logic filtering queries by tenant context
- KEEP: ABAC policy evaluation against user attributes and resource properties
- REJECT: Role enum or permission constant definitions without enforcement logic
- REJECT: User model with a `role` field but no guard that checks it
- REJECT: Authorization library imported but no policy or ability defined
- REJECT: Test mocks that stub authorization responses
- REJECT: Frontend-only route guards without corresponding server-side enforcement

**Common libraries/frameworks**: `casl`, `casbin`, `oso`, `accesscontrol`, `@nestjs/passport` (guards), `Spring Security`, `django-guardian`, `pundit`, `cancancan`, `go-casbin`

**Snippet guidance**: Capture the authorization check showing the permission or role being verified and the protected resource (e.g., `if (!user.hasPermission('documents:write')) return res.status(403)` or `@UseGuards(RolesGuard) @Roles('admin')`). Show the enforcement, not just the role definition.
