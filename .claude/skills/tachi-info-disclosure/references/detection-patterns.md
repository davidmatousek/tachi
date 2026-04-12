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
