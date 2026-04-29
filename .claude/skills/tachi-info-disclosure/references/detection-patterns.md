---
name: info-disclosure-detection-patterns
description: Externalized detection pattern catalog for STRIDE information disclosure — error message exposure, excessive data in responses, data at rest / in transit exposure, side-channel leakage
consumers: [tachi-info-disclosure]
last_updated: 2026-04-11
---

# Information Disclosure Detection Patterns

## Overview

Detection vocabulary for the STRIDE Information Disclosure threat category. Loaded at detection start by the `tachi-info-disclosure` agent via a single `**MANDATORY**: Read` directive. Covers confidentiality violations against Processes, Data Stores, and Data Flows — including error message exposure, excessive data returned in API responses, data at rest and in transit exposure, side-channel leakage, debug artifact exposure, SSRF against cloud metadata, and data staging from internal information repositories.

## Targeted DFD Element Types

- **Process**: API endpoints, error handlers, search services, reporting engines, debug interfaces, health check endpoints
- **Data Store**: Databases, file storage, caches, session stores, backup systems, log aggregators
- **Data Flow**: API responses, inter-service messages, file transfers, email notifications, webhook payloads

## Error Message Exposure

- Stack traces returned in API error responses (production environments)
- Database error messages revealing table names, column names, or query structure
- Framework version information in error pages or server headers
- File path disclosure in error messages exposing server directory structure
- Detailed validation errors revealing business rule internals

## Excessive Data in Responses

- API responses returning full database records when only specific fields are needed
- User profile endpoints exposing internal IDs, email addresses, or phone numbers to unauthorized callers
- List endpoints returning records the requesting user should not have access to
- Search results including data from access-restricted records
- Pagination metadata revealing total record counts that should be confidential

## Data at Rest Exposure

- Sensitive data stored unencrypted (PII, financial data, credentials)
- Database backups accessible without authentication
- Log files containing sensitive request/response bodies
- Cache stores holding sensitive data without TTL or access controls
- Temporary files containing sensitive data not cleaned up after processing

## Data in Transit Exposure

- Sensitive fields transmitted over unencrypted connections (HTTP, unencrypted SMTP)
- API keys or tokens included in URL query parameters (visible in logs and browser history)
- Sensitive data in HTTP headers observable by intermediary proxies
- Webhook payloads containing sensitive data sent to unverified endpoints
- Inter-service communication without encryption within cloud VPCs

## Side-Channel Information Leakage

- Timing differences revealing whether a user account exists (login enumeration)
- Response size differences indicating presence or absence of data
- HTTP status code variations enabling resource enumeration (200 vs 404 patterns)
- Rate limiting responses revealing valid vs invalid input patterns
- DNS query patterns leaking internal service topology

## Debug and Diagnostic Exposure

- Debug endpoints enabled in production (/debug, /metrics, /env, /health with internals)
- Source maps or development artifacts deployed to production
- API documentation endpoints exposing internal-only routes
- Profiling or monitoring data accessible without authentication
- Version control metadata (.git directory) accessible via web server

## Pattern Category 7: SSRF to Cloud Metadata and Internal Services

Server-Side Request Forgery against cloud workload metadata endpoints is the most-reported cloud confidentiality breach pattern and gained its own OWASP Top 10 category in 2021 (A10). This category detects Processes that make outbound HTTP requests to URLs derived from user input — webhook dispatchers, URL preview services, image/PDF fetchers, RSS aggregators, screenshot services — running on cloud workloads whose instance metadata endpoint (AWS `169.254.169.254`, Azure IMDS, GCP metadata server) holds short-lived IAM credentials, environment variables, and user-data scripts. An unconstrained fetch against the metadata address exfiltrates the workload's role credentials in one request.

**Indicators**:

- DFD element makes outbound HTTP requests to URLs sourced from user input without an egress allowlist restricting destination hosts
- Cloud workload uses AWS IMDSv1 rather than IMDSv2 (IMDSv1 responds to GET without a session token, so any SSRF that reaches the link-local address succeeds)
- No declared denylist for RFC1918 (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`) and link-local (`169.254.0.0/16`, `::1`, `fe80::/10`) destinations in the fetch component
- Component proxies, fetches, or renders URLs on behalf of users (URL preview, PDF renderer via headless browser, image resize, webhook dispatch, RSS/feed aggregation, SVG rendering)
- Redirect-following enabled on user-controlled fetches without re-validating the redirect target against the egress policy
- DNS resolution performed client-side before the egress check (enabling DNS rebinding to cloud metadata)

**Primary source**:

- OWASP Top 10 2021 A10: Server-Side Request Forgery: https://owasp.org/Top10/A10_2021-Server-Side_Request_Forgery_%28SSRF%29/
- CWE-918: Server-Side Request Forgery: https://cwe.mitre.org/data/definitions/918.html
- OWASP SSRF Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- AWS IMDSv2 guidance: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html

**Example**: A document-preview microservice accepts a user-supplied URL and fetches it server-side to render a thumbnail. Input validation checks the URL is well-formed and has an `http`/`https` scheme but does not constrain the destination host. The service runs on an EC2 instance still configured for IMDSv1. An attacker submits `http://169.254.169.254/latest/meta-data/iam/security-credentials/preview-service-role/`. The fetch returns the role's temporary access key, secret key, and session token in the thumbnail pipeline; the attacker reads the response from the preview output and now holds workload-equivalent IAM credentials for the lifetime of the session, enabling lateral movement through every resource the preview service role can reach.

**Mitigation**:

- Enforce IMDSv2 on every cloud workload that performs user-driven outbound fetches — IMDSv2 requires a session token obtained via PUT, which SSRF payloads cannot construct through a simple GET
- Resolve the destination host DNS on the server (not client-side), then check the resolved IP against an RFC1918 + link-local denylist before making the actual request; reject if the resolved address is private/loopback/link-local
- Use an explicit egress allowlist of destination domains for components that legitimately proxy user-supplied URLs; default-deny all other destinations
- Disable redirect-following on user-controlled fetches, or re-apply the egress policy to every hop in the redirect chain
- Run URL-fetching workloads in a dedicated subnet with network-level blocks on the metadata service CIDR, ensuring defence in depth even when application controls fail
- Treat any component that fetches user-supplied URLs as high-risk and require explicit architecture review when added

## Pattern Category 8: Information Exposure Through Error Messages and Debug Output

This category detects the distinct class of disclosure caused by verbose error handling and debug artifacts leaking into production-accessible surfaces. The pre-existing Error Message Exposure indicators cover stack traces in API error responses, but the broader production-debug-mode problem spans framework default error pages shipped to external trust zones, source maps published alongside minified frontend bundles, and debug endpoints left enabled after deployment. CWE-200 (Exposure of Sensitive Information to an Unauthorized Actor) appears at rank 17 on the 2024 CWE Top 25 and is most frequently reported through error and debug channels.

**Indicators**:

- Component declares debug or verbose error mode enabled in production, or has no declared distinction between dev and prod error handling (single error handler for all environments)
- DFD element returns framework-default error pages to external trust zones — Django debug page, Flask interactive debugger, ASP.NET "Yellow Screen of Death", Rails better_errors page, Spring Boot Whitelabel error page with trace, Express.js default error middleware with stack
- Frontend bundle published with `.map` source maps to a public trust zone without access control, exposing original module structure, file paths, comments, and embedded secrets to anyone loading the bundle
- API returns detailed ORM, SQL, or query-builder error messages on query failure ("Unknown column 'users.ssn'", Prisma validation errors with schema excerpts, MongoDB `$oid` and internal field names)
- Debug/administrative endpoints accessible from the same trust zone as the main application without separate authentication — `/debug`, `/env`, `/metrics`, `/actuator/*`, `/_profiler`, `/rails/info/routes`, `/__debug__/`, `/.well-known/openapi.json` without auth
- Verbose logging middleware echoes request/response bodies into log streams that downstream components can read with broader access than the original request

**Primary source**:

- CWE-209: Generation of Error Message Containing Sensitive Information: https://cwe.mitre.org/data/definitions/209.html
- CWE-200: Exposure of Sensitive Information to an Unauthorized Actor: https://cwe.mitre.org/data/definitions/200.html
- CWE-215: Insertion of Sensitive Information into Debugging Code: https://cwe.mitre.org/data/definitions/215.html
- CWE Top 25 Most Dangerous Software Weaknesses 2024: https://cwe.mitre.org/top25/archive/2024/2024_cwe_top25.html
- OWASP Error Handling Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html

**Example**: A single-page application ships its production build with webpack source maps (`app.min.js.map`) uploaded to the CDN alongside the minified bundle. The JavaScript backend is a Flask service with `FLASK_DEBUG=1` accidentally set in the production image. A researcher requests the source map and recovers the original React module tree including a file named `utils/stripe.ts` containing a hardcoded Stripe test key; the researcher then sends a malformed JSON body to `/api/orders` and the Flask interactive debugger returns a full Python traceback disclosing the database connection string, the path to the service's `.env` file, and an in-memory PIN set in the error handler's frame locals. Two independent disclosure paths, both from debug-mode artifacts that production should never have shipped.

**Mitigation**:

- Enforce environment separation at build time: production builds MUST set framework debug flags to false (`FLASK_DEBUG=0`, `APP_DEBUG=false`, `NODE_ENV=production`, `RAILS_ENV=production`, `DEBUG=0`), and the build should fail closed if any debug flag is still on
- Strip or gate source maps at the CDN layer: either do not publish `.map` files to public buckets, or require authentication on the `.map` URL (source maps behind the same auth as internal dashboards)
- Wrap all database and ORM errors in an opaque application-level error type before returning to clients; the raw ORM message stays in server logs, the client sees a generic "invalid request" with a correlation ID
- Disable framework debug routes in production by default and assert in a startup health check that `/debug`, `/env`, `/actuator/env`, and equivalents return 404 or 403 from the external trust zone; fail service startup if any respond 200
- Review every framework's default error page rendering path and replace with a custom minimal error page that does not include stack, path, or configuration disclosure
- Use a linter or security-scan step in CI that greps for known debug-mode environment variables and default-error-page middleware references; block the deploy if found

## Pattern Category 9: Data Staging and Collection from Information Repositories

Modern architectures aggregate knowledge in internal repositories — Confluence, SharePoint, Notion, Slack/Teams, Jira, GitHub/GitLab — that become de facto sources of truth for design documents, credentials in incident notes, API keys in README files, and customer data in support threads. These repositories are under-represented as threat surfaces in traditional STRIDE implementations because they look like "productivity tools" rather than "data stores", yet MITRE ATT&CK catalogues them as T1213 "Data from Information Repositories" with dedicated sub-techniques for Confluence, SharePoint, and code repositories. An adversary with valid credentials (or a bot/service account with over-broad read permissions) can collect secrets, architectural intelligence, customer PII, and lateral-movement opportunities without ever touching the production data stores the threat model was built around.

**Indicators**:

- DFD element is an internal knowledge repository — wiki (Confluence, Notion, Wiki.js), collaboration platform (SharePoint, Google Workspace Shared Drives), chat (Slack, Teams, Mattermost), ticketing (Jira, ServiceNow), code host (GitHub, GitLab, Bitbucket) — with broad organizational read permissions
- Repository lacks declared data classification or sensitivity labeling; all content is accessible to all authenticated users regardless of sensitivity
- Search or indexing component (enterprise search, chat search, wiki search) has elevated read permissions spanning multiple trust zones and returns results across the full repository surface to any authenticated caller
- Bot or service account with read access to repositories for agentic assistance (LLM-backed assistants, automated summary bots, code review bots) — the bot's token can be harvested to access everything the bot sees
- Personal access tokens or API keys are copy-pasted into repository content (incident runbooks, onboarding documents, Slack DMs) and live there indefinitely with no scanning
- Archived content (closed Jira tickets, deleted Slack channels accessible through exports, old Confluence spaces) retains historical sensitive information with no retention/purge policy
- External collaborators (vendors, contractors) granted standing read access rather than time-bounded least-privilege access

**Primary source**:

- MITRE ATT&CK T1213: Data from Information Repositories: https://attack.mitre.org/techniques/T1213/
- MITRE ATT&CK T1213.001: Confluence: https://attack.mitre.org/techniques/T1213/001/
- MITRE ATT&CK T1213.002: SharePoint: https://attack.mitre.org/techniques/T1213/002/
- MITRE ATT&CK T1213.003: Code Repositories: https://attack.mitre.org/techniques/T1213/003/
- MITRE ATT&CK T1213.005: Messaging Applications: https://attack.mitre.org/techniques/T1213/005/
- NIST SP 800-53 AC-3: Access Enforcement: https://csrc.nist.gov/projects/risk-management/sp800-53-controls/release-search

**Example**: A mid-size SaaS company operates a Confluence instance where every employee has read access to every space except HR. A customer-success engineer leaves the company; their account is offboarded correctly from Okta but their Confluence session token (issued with a 30-day sliding window) is still valid on their personal laptop. The ex-employee searches Confluence for "aws", "prod", and "password" across the remaining spaces and recovers: a platform-team runbook containing a production-read IAM role assumable by anyone with the runbook's `aws sts assume-role` command; a Slack integration guide with a webhook signing secret pasted in plaintext; a customer onboarding page listing 40 enterprise customer tenant IDs with their contract terms. No malware, no exploit — just standing read access plus an archival search, the textbook T1213 collection pattern.

**Mitigation**:

- Apply least-privilege by default to every knowledge repository: authenticated does not mean authorized; require explicit per-space/per-channel/per-repo membership, with a default of "no access" for newly onboarded users
- Enforce data classification at content-creation time — wikis and collaboration platforms must require a sensitivity label (Public / Internal / Confidential / Restricted) before a page can be published; restrict search and indexing by classification level
- Run automated secret scanning across all knowledge repositories continuously (not just code repos); tools like gitleaks, trufflehog, and repository-specific scanners (Confluence-DLP, Slack-DLP) should alert on credential patterns and auto-redact
- Scope bot and service account access narrowly — an agentic assistant that reads Confluence should have per-space grants, not organization-wide read; audit bot tokens quarterly and rotate on access-pattern anomalies
- Enforce short-lived sessions with SSO-bound renewal: no standing sessions longer than 8 hours on knowledge platforms that hold sensitive content; revoke-on-offboarding must include session invalidation, not just account deletion
- Implement retention and purge policies for archived content — closed tickets, deleted channels, old wiki spaces should be destroyed on a schedule rather than retained indefinitely
- Require time-bounded, access-reviewed external collaborator access: every vendor grant has an expiry date, and a quarterly review confirms continued business need

## Pattern Category N+1 — Insecure Mobile Communication (M5)

OWASP M5:2024 (Insecure Communication) names mobile-specific transport-security weaknesses as a distinct attack class from generic web/API data-in-transit exposure (Pattern Category Data in Transit Exposure) and from generic SSRF against cloud metadata (Pattern Category 7). Where the pre-existing categories cover server-side and inter-service confidentiality on backend transport, **Pattern Category N+1 targets the mobile client-to-mobile-backend transport surface** — the outbound flows from a declared mobile client process to mobile-backend APIs and to third-party SDK egress endpoints. The attacker's goal is to MITM the mobile client's TLS session via a self-signed or compromised certificate, downgrade the connection to cleartext HTTP, or exploit weak cipher suites to recover session tokens, transaction payloads, or PII in motion. MASTG-NETWORK and MASVS-NETWORK describe the mobile transport-security requirements at section-level granularity.

**Indicators**:

- Mobile client to mobile-backend Data Flow declared — primary mobile-platform topology indicator on the transport surface
- Cleartext HTTP traffic enabled — no `usesCleartextTraffic="false"` declared on the Android `application` manifest entry; no `NSAppTransportSecurity` exception audit on the iOS `Info.plist` (mixed-content / partial ATS exceptions reach production builds)
- No TLS certificate pinning — no `OkHttp` `CertificatePinner` declared on the Android client; no `URLSession` pinning delegate on the iOS client; no Network Security Config pinning manifest declared at the app level
- HTTP-to-HTTPS downgrade attack path — mixed-content allowed on the mobile client; outbound redirects from HTTPS-to-HTTP not validated; user-driven scheme swaps reach trusted operations
- Weak TLS cipher acceptance — TLS 1.0 / TLS 1.1 permitted on the client transport stack; insecure cipher suites (RC4, 3DES, NULL ciphers) enabled on the platform-default TLS context
- Missing HSTS-equivalent enforcement at app-level — no preload list of pinned hosts; no Strict-Transport-Security parity (the mobile client trusts whatever certificate the platform CA store accepts, with no app-level continuous-pinning override)

**Primary source**:

- OWASP M5:2024 — Insecure Communication: https://owasp.org/www-project-mobile-top-10/2023-risks/m5-insecure-communication
- OWASP MASTG-NETWORK — Mobile Application Security Testing Guide, Network Communication Test Cases (section-level granularity)
- OWASP MASVS-NETWORK — Mobile Application Security Verification Standard, Network Communication Requirements (section-level granularity)

**Example**: A mobile-banking Android app's `network_security_config.xml` declares `cleartextTrafficPermitted="true"` for staging endpoints (`staging.api.bank.example`) and ships with no `<pin-set>` declarations on either staging or production. The build pipeline reuses session credentials between staging and production environments because the same OAuth issuer underlies both. An attacker on a public Wi-Fi hotspot intercepts the staging endpoint's TLS session via a self-signed certificate the production binary trusts (no pin configured on that host); the attacker captures the user's authentication token. Because staging-to-production credential reuse means the captured token authenticates against the production banking API, the attacker drains the victim's account before the victim notices the device joined the rogue Wi-Fi at all. The two architectural defects compound: cleartext-permitted staging plus missing certificate pinning across all environments equals a one-rogue-AP-away production breach.

**Mitigation**:

- Prohibit cleartext traffic across all environments via `usesCleartextTraffic="false"` on the Android `application` manifest and a fully-restrictive `network_security_config.xml` with no `cleartextTrafficPermitted` exceptions; mirror with iOS `NSAppTransportSecurity` set to `NSAllowsArbitraryLoads=false` and zero per-domain exceptions
- Enforce certificate pinning with backup-pin rotation across **all** environments (production, staging, sandbox); use `OkHttp` `CertificatePinner` on Android with at least one primary pin and one backup pin per host; use `URLSession` pinning delegate on iOS with the same primary/backup model; rotate pins on a planned cadence with a deprecation window
- Set the minimum TLS version to TLS 1.3 (or TLS 1.2 with strict cipher allowlist as the floor); reject TLS 1.0 / TLS 1.1; configure cipher allowlist to AEAD suites only (AES-GCM, ChaCha20-Poly1305) and reject RC4 / 3DES / NULL / EXPORT cipher suites
- Implement HSTS-equivalent enforcement at the app level — maintain a custom preload list of pinned hosts in the mobile binary; reject any unexpected HTTPS-to-HTTP redirect; treat a pin-mismatch event as a fatal connection error and log to the audit trail
- Document the mobile transport-security choices in mobile threat-modeling artifacts (MASTG-NETWORK / MASVS-NETWORK section-level cross-reference)

## Pattern Category N+2 — Inadequate Mobile Privacy Controls (M6)

OWASP M6:2024 (Inadequate Privacy Controls) names mobile-specific privacy weaknesses as a distinct attack class from generic data-at-rest exposure (Pattern Category Data at Rest Exposure) and from generic information-repository data staging (Pattern Category 9). Where the pre-existing categories cover broad-scope confidentiality on backend or repository surfaces, **Pattern Category N+2 targets the mobile-client privacy surface** — PII / PHI handling on declared mobile clients including local cache hygiene, telemetry consent gating, screenshot leakage on sensitive screens, clipboard exposure on credential or transaction fields, and over-broad permission requests at first launch. The attacker's goal is to recover personal information from app caches, recents-screen snapshots, or telemetry payloads that were never gated by user consent. MASTG-PRIVACY and MASVS-PRIVACY describe the mobile privacy-control requirements at section-level granularity.

**Indicators**:

- Mobile client component declared — primary mobile-platform topology indicator on the privacy surface
- PII / PHI persisted in device-local caches without TTL expiry — account snapshots, transaction history, health records, contact list snapshots, or derived PII fields cached indefinitely until app data is manually cleared
- Telemetry / analytics SDKs collecting personal data without disclosure or consent gating — embedded analytics SDKs (Firebase Analytics, Mixpanel, Segment, Amplitude) emitting user identifiers, screen views, or event metadata without a privacy-consent gate or opt-out toggle
- Clipboard exposure on sensitive fields — no `setExtraData(EXTRA_IS_SENSITIVE, true)` on `ClipData` for Android 13+; no `UIPasteboard.setItems(_:options:)` with `.localOnly` for iOS; sensitive fields (account number, PIN, OTP, password) reach the system pasteboard without sensitivity tagging
- Screenshot leakage on sensitive screens — no `FLAG_SECURE` declared on the Activity `Window` for Android (recents-screen snapshots and screen-recording capture sensitive content); no `obscureWhenInBackground` equivalent on iOS (snapshot taken on app-resign)
- Over-broad permission requests on first launch — camera, location, contacts, microphone, calendar, or other sensitive runtime permissions requested up-front rather than just-in-time when triggered by user action; no graceful denial path when permission is refused

**Primary source**:

- OWASP M6:2024 — Inadequate Privacy Controls: https://owasp.org/www-project-mobile-top-10/2023-risks/m6-inadequate-privacy-controls
- OWASP MASTG-PRIVACY — Mobile Application Security Testing Guide, Privacy Test Cases (section-level granularity)
- OWASP MASVS-PRIVACY — Mobile Application Security Verification Standard, Privacy Requirements (section-level granularity)

**Example**: A mobile-banking Android app caches account-balance data and recent-transaction records in `WellnessBankLocalDB` indefinitely with no TTL expiry — the cache survives until the user manually clears app data, even after long periods of inactivity. The transaction-history Activity ships without `FLAG_SECURE` declared on its `Window`. A user pulls down the recents-screen switcher in a public space (coffee shop, conference, family setting); the recents thumbnail snapshot persists the most recently rendered transaction-history screen including account balance, recipient names, and transfer amounts. Anyone with brief device access — a curious bystander, a partner glancing at the unlocked phone, a shoulder-surfer — captures financial data without ever bypassing the app lock. The same surface also leaves the OTP code visible to recents-screen capture during a pending money-movement confirmation, enabling a co-located adversary to harvest both the balance context and the OTP in a single recents-screen view.

**Mitigation**:

- Apply data-minimization on caches with TTL enforcement — set explicit expiry on each cached PII / PHI field (e.g., balance cache 60s TTL with refresh-on-demand, transaction cache 5-minute TTL, contact-list cache invalidated on app pause); evict cached data on app-lock transition
- Apply consent-gated telemetry with opt-out — gate every analytics emission behind a documented privacy-consent gate honored on first-launch and reachable in-app at any time; respect platform-tier opt-out signals (iOS App Tracking Transparency, Android Advertising-ID opt-out); honor end-user opt-out within the app's own UI before any telemetry SDK initialization
- Apply `FLAG_SECURE` (Android `WindowManager.LayoutParams.FLAG_SECURE`) on every Activity `Window` rendering PII / PHI — transaction history, account balance, OTP / 2FA challenge, health records, payment-card-data screens; mirror on iOS by replacing the foreground content with a privacy-blur view in `applicationWillResignActive(_:)` so recents-screen snapshots show no sensitive content
- Apply just-in-time permission prompts with graceful denial paths — request runtime permissions only when the user-driven flow that needs them begins (e.g., camera permission on the QR-scan flow start, not on app launch); supply graceful denial paths (text input fallback when camera denied, manual address entry when location denied) so a denied permission does not break the app
- Apply clipboard sensitivity tagging — set `EXTRA_IS_SENSITIVE=true` on `ClipData` for any clipboard write on Android 13+ to prevent clipboard-history capture; use `UIPasteboard` `.localOnly` option on iOS to keep clipboard payloads off the universal-clipboard sync surface
- Document the mobile privacy choices in mobile threat-modeling artifacts (MASTG-PRIVACY / MASVS-PRIVACY section-level cross-reference)

## Pattern Category N+3 — Insecure Mobile Data Storage (M9)

OWASP M9:2024 (Insecure Data Storage) names mobile-specific secure-storage weaknesses as a distinct attack class from generic data-at-rest exposure (Pattern Category Data at Rest Exposure) and from generic excessive-data-in-responses (Pattern Category Excessive Data in Responses). Where the pre-existing categories cover server-side or backend persistence, **Pattern Category N+3 targets device-resident data stores** on declared mobile clients — unencrypted SQLite / Realm / Room databases, plaintext SharedPreferences / NSUserDefaults stores, cloud-backup leakage to iCloud / Google Drive without exclusion, external-storage writes for sensitive files, and world-readable file permissions on internal storage. The attacker's goal is to recover device-resident sensitive data via root / jailbreak access, device-backup extraction, or cloud-backup-restore to a different device. MASTG-STORAGE and MASVS-STORAGE describe the mobile secure-storage requirements at section-level granularity.

**Indicators**:

- Mobile client component declared — primary mobile-platform topology indicator on the secure-storage surface
- Unencrypted SQLite / Realm / Room database on device — sensitive tables (transaction history, account snapshots, contact list, message archive) persisted to a Room or Realm database without SQLCipher integration or Realm encryption configuration
- Unencrypted KeyValue store — `SharedPreferences` (Android) / `NSUserDefaults` (iOS) holding tokens, session identifiers, PII fields, or feature flags relevant to security in plaintext rather than `EncryptedSharedPreferences` / Keychain-stored secrets
- Cloud-backup leakage — iCloud / Google Drive automatic-backup including sensitive app data without `excludeFromBackup` (iOS) / `allowBackup="false"` (Android) exclusion, or without per-table Backup Rules limiting which data partitions get backed up
- External SD-card writes for sensitive files — `Environment.getExternalStorageDirectory()` reachable from non-platform-protected code, sensitive files dropped to publicly-readable external storage rather than internal storage
- World-readable file permissions on Android internal storage — `MODE_WORLD_READABLE` / `MODE_WORLD_WRITEABLE` flags set on file output streams; sensitive files dropped to `Environment.getExternalStoragePublicDirectory(...)` without scoped-storage migration on Android 11+

**Primary source**:

- OWASP M9:2024 — Insecure Data Storage: https://owasp.org/www-project-mobile-top-10/2023-risks/m9-insecure-data-storage
- OWASP MASTG-STORAGE — Mobile Application Security Testing Guide, Data Storage Test Cases (section-level granularity)
- OWASP MASVS-STORAGE — Mobile Application Security Verification Standard, Data Storage and Privacy Requirements (section-level granularity)

**Example**: A mobile-banking Android app stores transaction history in an unencrypted SQLite database (`WellnessBankLocalDB`) within the app's internal-storage data partition, with `allowBackup="true"` declared on the application manifest (the platform default) and no per-table `BackupAgent` exclusion rules. The user enables Google Drive auto-backup on the device for normal continuity reasons. Months later, the user's device is lost; the user buys a new device and authenticates with the same Google account; Android's automatic-restore copies the entire `WellnessBankLocalDB` payload from Google Drive backup into the new device. An attacker who later compromises the user's Google account (credential-stuffing, password reuse from a separate breach) can trigger an automatic-restore on an attacker-controlled device and recover the full transaction history without ever bypassing the original device's lock screen, biometric, or app-tier authentication. The breach surface is the cloud-backup channel, not the original device — yet the data leakage is the same.

**Mitigation**:

- Encrypt all device-resident databases via SQLCipher (Android) / Realm encryption (cross-platform) / Core Data with NSFileProtectionComplete (iOS); derive the database key from platform-keyring-bound material (Android Keystore-backed AES wrapping; iOS Keychain with appropriate access-control protection class) rather than from a static or user-PIN-derived key alone
- Apply `EncryptedSharedPreferences` (Android Jetpack Security) for all KeyValue persistence of tokens, session identifiers, or other security-relevant fields; use Keychain-stored secrets on iOS with `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly` or stricter
- Set `allowBackup="false"` on Android with sensitive-data partitioning OR define explicit `<backup-rules>` (Android 12+) that exclude sensitive databases / preferences from cloud-backup; on iOS, set `URL.isExcludedFromBackupKey = true` on the file URLs of sensitive databases / preferences before first write
- Restrict sensitive file writes to internal storage only (`Context.getFilesDir()` / `Context.getNoBackupFilesDir()` on Android; `FileManager.default.urls(for: .documentDirectory, ...)` with explicit backup exclusion on iOS); reject any path resolution that resolves to external storage on sensitive files
- Migrate to scoped-storage on Android 11+ (`MediaStore` API or `SAF` for shareable files; private app-specific directories for per-app files); reject `MODE_WORLD_READABLE` / `MODE_WORLD_WRITEABLE` on file streams; reject world-readable POSIX permissions on internal-storage files
- Document the mobile secure-storage choices in mobile threat-modeling artifacts (MASTG-STORAGE / MASVS-STORAGE section-level cross-reference)

## Pattern Category N+4 — Insufficient Mobile Cryptography (M10)

OWASP M10:2024 (Insufficient Cryptography) names mobile-specific cryptographic-control weaknesses as a distinct attack class from generic data-at-rest exposure (Pattern Category Data at Rest Exposure) and from generic data-in-transit exposure (Pattern Category Data in Transit Exposure). Where the pre-existing categories cover broad-scope confidentiality at backend layers, **Pattern Category N+4 targets the mobile-tier cryptographic primitives** — key derivation from user PINs, custom-rolled crypto algorithms in mobile binaries, hardcoded symmetric keys in shipped binaries, insecure PRNG seeding for security-critical material, and deprecated cipher suites (DES / 3DES / RC4 / MD5 / SHA1) for sensitive operations on the mobile client. The attacker's goal is to brute-force a weak key, recover a hardcoded key from the binary, predict a weak PRNG output, or exploit a deprecated cipher to recover plaintext from ciphertext. MASTG-CRYPTO and MASVS-CRYPTO describe the mobile cryptographic-control requirements at section-level granularity.

**Indicators**:

- Mobile client component declared — primary mobile-platform topology indicator on the cryptographic-control surface
- Weak key derivation on user PINs — low PBKDF2 iteration counts (anything below the OWASP 600,000-iteration baseline for PBKDF2-HMAC-SHA256), no salting on the PIN-to-key derivation, no per-device entropy mixing into the derivation chain
- Custom-rolled crypto algorithms in mobile binaries — custom ciphers, non-standard hash functions, "obfuscation" routines mistaken for encryption, XOR-with-constant masquerading as confidentiality control
- Hardcoded symmetric keys in shipped binaries — AES keys, HMAC keys, signing keys visible via `strings` extraction or `objection` runtime introspection on the production APK / IPA
- Insecure PRNG seeding for security-critical material — `java.util.Random` (Java) used for cryptographic key generation or token issuance; non-`SecureRandom` paths into key material, IV generation, or salt generation
- Deprecated cipher suites for sensitive operations — DES / 3DES / RC4 / MD5 / SHA1 used for encryption, MAC, or signing of sensitive payloads (session tokens, transaction signatures, device-bound credentials)

**Primary source**:

- OWASP M10:2024 — Insufficient Cryptography: https://owasp.org/www-project-mobile-top-10/2023-risks/m10-insufficient-cryptography
- OWASP MASTG-CRYPTO — Mobile Application Security Testing Guide, Cryptography Test Cases (section-level granularity)
- OWASP MASVS-CRYPTO — Mobile Application Security Verification Standard, Cryptography Requirements (section-level granularity)

**Example**: A mobile-banking app derives the encryption key for its on-device credential vault from the user's 4-digit PIN via PBKDF2-HMAC-SHA1 with an iteration count of 1000 and no salting. The total PIN keyspace is 10,000 values. An attacker recovers a stolen device, dumps the encrypted credential vault from the app's data partition, and runs an offline brute-force against the encrypted vault: PBKDF2-HMAC-SHA1 at 1000 iterations costs roughly a microsecond per candidate on commodity GPU hardware, so the entire 10,000-PIN keyspace is exhausted in under a second. The attacker recovers the vault encryption key, decrypts the persisted refresh tokens, and authenticates against the production banking API as the legitimate user — defeating the entire app-tier credential protection without ever guessing the PIN at the device lock screen. The defect compounds with the unsalted derivation: a precomputed rainbow table for the 1000-iteration PBKDF2-HMAC-SHA1 over the 10,000-PIN space costs trivial storage and reduces the per-device attack to a single table lookup.

**Mitigation**:

- Use platform-provided key derivation primitives at adequate cost — Argon2id (preferred) or scrypt (acceptable) for password / PIN derivation, or PBKDF2-HMAC-SHA256 with at least 600,000 iterations as the floor; salt every derivation with a unique per-account / per-device random salt
- Use platform crypto APIs only — `AndroidKeyStore` (Android) for key storage and crypto operations bound to hardware-backed keystore where available; `CryptoKit` (iOS) for high-level primitives bound to Secure Enclave; reject any custom-rolled cipher, custom hash, or "obfuscation" routine as a substitute for platform-provided cryptography
- Derive sensitive keys from platform-keyring-bound material — `StrongBox` (Android Keystore-backed hardware key island) on supported devices; Secure Enclave-bound keys on iOS; combine the user-PIN-derived key with a hardware-bound key in an envelope-encryption scheme so the on-device vault key cannot be recovered offline without the device's hardware module
- Use `SecureRandom` (Android) / `SecRandomCopyBytes` (iOS) for all cryptographic randomness — keys, IVs, salts, nonces, session-token entropy, challenge-response material; reject any `java.util.Random` / `arc4random` shortcut on a security path
- Require AES-GCM (preferred) or AES-CCM as the symmetric-encryption baseline; require SHA-256 (preferred) or SHA-512 / SHA-3 as the hash baseline; reject DES / 3DES / RC4 / MD5 / SHA1 in any sensitive path; document the cipher / hash allowlist in mobile threat-modeling artifacts
- Document the mobile cryptographic-control choices in mobile threat-modeling artifacts (MASTG-CRYPTO / MASVS-CRYPTO section-level cross-reference)

## Pattern Category Disambiguation

Pattern Categories N+1 (Insecure Mobile Communication / OWASP M5:2024), N+2 (Inadequate Mobile Privacy Controls / OWASP M6:2024), N+3 (Insecure Mobile Data Storage / OWASP M9:2024), and N+4 (Insufficient Mobile Cryptography / OWASP M10:2024) and the pre-existing Pattern Categories 1–N (generic confidentiality-leakage signal class — error message exposure, excessive data in responses, data at rest exposure, data in transit exposure, side-channel information leakage, debug and diagnostic exposure, SSRF to cloud metadata, error / debug-output exposure, and data staging from information repositories) share the OWASP A02:2021 Cryptographic Failures / A01:2021 Broken Access Control family at the OWASP framework level but address distinct architectural-tells and mitigation surfaces:

- **Pattern Categories 1–N** (Error Message Exposure, Excessive Data in Responses, Data at Rest Exposure, Data in Transit Exposure, Side-Channel Information Leakage, Debug and Diagnostic Exposure, SSRF to Cloud Metadata and Internal Services, Information Exposure Through Error Messages and Debug Output, Data Staging and Collection from Information Repositories — pre-existing) detect generic web/API/general-software confidentiality gaps at any HTTP/API surface, backend data-store, server-to-server data flow, cloud workload metadata endpoint, or internal information repository. The architectural-tell is a generic API endpoint, server-side data store, backend transport, or productivity-tool repository — NOT a mobile-platform topology.
- **Pattern Category N+1** (Insecure Mobile Communication — F-7) detects mobile transport-security gaps on declared mobile clients — cleartext HTTP, missing certificate pinning, weak TLS cipher acceptance, HTTP-to-HTTPS downgrade, missing HSTS-equivalent enforcement at the app layer. The architectural-tell is a declared mobile client component with outbound flows to mobile-backend APIs or third-party SDK egress endpoints.
- **Pattern Category N+2** (Inadequate Mobile Privacy Controls — F-7) detects mobile privacy-control gaps on declared mobile clients — PII / PHI in unbounded local caches, telemetry without consent, screenshot leakage on sensitive screens, clipboard exposure on sensitive fields, over-broad permission requests at first launch. The architectural-tell is a declared mobile client component with PII / PHI handling, telemetry SDK integration, sensitive-screen rendering, or runtime-permission requests.
- **Pattern Category N+3** (Insecure Mobile Data Storage — F-7) detects mobile secure-storage gaps on declared mobile clients — unencrypted SQLite / Realm / Room, plaintext SharedPreferences / NSUserDefaults, cloud-backup leakage to iCloud / Google Drive without exclusion, external-storage writes for sensitive files, world-readable internal-storage permissions. The architectural-tell is a declared mobile client component with device-resident data persistence outside platform-managed encrypted storage.
- **Pattern Category N+4** (Insufficient Mobile Cryptography — F-7) detects mobile cryptographic-control gaps on declared mobile clients — weak key derivation on user PINs, custom-rolled crypto algorithms, hardcoded symmetric keys in shipped binaries, insecure PRNG seeding, deprecated cipher suites for sensitive operations. The architectural-tell is a declared mobile client component with cryptographic primitives applied to sensitive payloads outside platform-provided crypto APIs.

The same hybrid architecture (e.g., a web + mobile app sharing a backend, where the web frontend serves browser users and the mobile client serves app users against the same API) may legitimately surface BOTH pre-existing Cat 1–N findings (against the backend / web / cloud surface) AND new Cat N+1 / Cat N+2 / Cat N+3 / Cat N+4 findings (against the mobile-platform surface) without duplication, because they target different architectural surfaces. They are not duplicates and MUST NOT be merged in `threat-report.md`. Architect formalizes this carve in ADR-036 Decision 9 (Pattern Category Disambiguation requirement on the F-7 info-disclosure companion).

## Primary Sources

- OWASP Top 10 2021 — A01: Broken Access Control: https://owasp.org/Top10/A01_2021-Broken_Access_Control/
- OWASP Top 10 2021 — A02: Cryptographic Failures: https://owasp.org/Top10/A02_2021-Cryptographic_Failures/
- OWASP Top 10 2021 — A10: Server-Side Request Forgery (SSRF): https://owasp.org/Top10/A10_2021-Server-Side_Request_Forgery_%28SSRF%29/
- OWASP API Security Top 10 2023 — API3: Broken Object Property Level Authorization: https://owasp.org/API-Security/editions/2023/en/0xa3-broken-object-property-level-authorization/
- OWASP Error Handling Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html
- OWASP SSRF Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- OWASP Information Disclosure Prevention Cheat Sheet
- CWE-200: Exposure of Sensitive Information to an Unauthorized Actor: https://cwe.mitre.org/data/definitions/200.html
- CWE-209: Generation of Error Message Containing Sensitive Information: https://cwe.mitre.org/data/definitions/209.html
- CWE-215: Insertion of Sensitive Information Into Debugging Code: https://cwe.mitre.org/data/definitions/215.html
- CWE-532: Insertion of Sensitive Information into Log File: https://cwe.mitre.org/data/definitions/532.html
- CWE-538: Insertion of Sensitive Information into Externally-Accessible File or Directory: https://cwe.mitre.org/data/definitions/538.html
- CWE-918: Server-Side Request Forgery: https://cwe.mitre.org/data/definitions/918.html
- CWE Top 25 Most Dangerous Software Weaknesses 2024: https://cwe.mitre.org/top25/archive/2024/2024_cwe_top25.html
- MITRE ATT&CK T1005: Data from Local System: https://attack.mitre.org/techniques/T1005/
- MITRE ATT&CK T1039: Data from Network Shared Drive: https://attack.mitre.org/techniques/T1039/
- MITRE ATT&CK T1213: Data from Information Repositories: https://attack.mitre.org/techniques/T1213/
- MITRE ATT&CK T1213.001: Confluence: https://attack.mitre.org/techniques/T1213/001/
- MITRE ATT&CK T1213.002: SharePoint: https://attack.mitre.org/techniques/T1213/002/
- MITRE ATT&CK T1213.003: Code Repositories: https://attack.mitre.org/techniques/T1213/003/
- MITRE ATT&CK T1213.005: Messaging Applications: https://attack.mitre.org/techniques/T1213/005/
- MITRE ATT&CK T1530: Data from Cloud Storage: https://attack.mitre.org/techniques/T1530/
- NIST SP 800-53 AC-3: Access Enforcement
- NIST SP 800-122: Guide to Protecting the Confidentiality of Personally Identifiable Information (PII)
- AWS IMDSv2 guidance: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html
- OWASP M5:2024 — Insecure Communication: https://owasp.org/www-project-mobile-top-10/2023-risks/m5-insecure-communication
- OWASP M6:2024 — Inadequate Privacy Controls: https://owasp.org/www-project-mobile-top-10/2023-risks/m6-inadequate-privacy-controls
- OWASP M9:2024 — Insecure Data Storage: https://owasp.org/www-project-mobile-top-10/2023-risks/m9-insecure-data-storage
- OWASP M10:2024 — Insufficient Cryptography: https://owasp.org/www-project-mobile-top-10/2023-risks/m10-insufficient-cryptography
