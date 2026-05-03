---
name: privilege-escalation-detection-patterns
description: Externalized detection pattern catalog for STRIDE elevation of privilege — broken access control, IDOR, role escalation, multi-tenancy boundary violations, lateral movement, improper privilege management, and abuse elevation control mechanisms
consumers: [tachi-privilege-escalation]
last_updated: 2026-04-11
---

# Privilege Escalation Detection Patterns

## Overview

Detection vocabulary for the STRIDE Elevation of Privilege threat category. Loaded at detection start by the `tachi-privilege-escalation` agent via a single `**MANDATORY**: Read` directive. Covers authorization bypass against Processes — broken access control, insecure direct object references (IDOR), role and permission escalation, path traversal and scope bypass, multi-tenancy boundary violations, lateral movement, privilege persistence, plus authoritative coverage of OWASP A01:2021 Broken Access Control as the #1 ranked OWASP risk, CWE-269 Improper Privilege Management from the CWE Top 25 2024, and MITRE ATT&CK T1548 Abuse Elevation Control Mechanism (Setuid/Setgid, Sudo Caching, Bypass UAC, Temporary Elevated Cloud Access).

## Targeted DFD Element Types

- **Process**: Authorization middleware, role management services, API endpoints with access control, administrative interfaces, multi-tenant boundary enforcement, resource access controllers

## Trigger Keywords

This agent activates when a DFD element name or description matches any of the following patterns (case-insensitive): `auth`, `authorization`, `RBAC`, `ABAC`, `permission`, `role`, `admin`, `tenant`, `multi-tenant`, `policy`, `access control`, `IAM`, `service account`, `privileged`.

## Pattern Category 1: Broken Access Control

- Missing authorization checks on API endpoints (authentication present but no permission verification)
- Authorization enforced only at the UI layer, not at the API layer
- Inconsistent authorization between different API versions (v1 secured, v2 missing checks)
- Missing function-level access control on administrative operations
- Object-level authorization gaps allowing users to access resources by manipulating IDs (IDOR)

## Pattern Category 2: Insecure Direct Object References (IDOR)

- Sequential or predictable resource identifiers enabling enumeration
- API endpoints accepting user-supplied resource IDs without ownership verification
- File access endpoints using user-provided path components without normalization
- Missing tenant isolation in multi-tenant query filters
- Bulk operation endpoints that do not verify per-item authorization

## Pattern Category 3: Role and Permission Escalation

- User-controllable role assignment (setting own role in registration or profile update)
- Missing validation on role transitions (user to admin without approval workflow)
- JWT tokens containing role claims that are trusted without server-side verification
- Permission inheritance chains that grant unintended cumulative privileges
- Default roles with excessive permissions assigned to new accounts

## Pattern Category 4: Path Traversal and Scope Bypass

- File access endpoints vulnerable to path traversal (../ sequences)
- API route patterns allowing parameter pollution to reach administrative routes
- GraphQL query depth or field access not restricted by authorization context
- Missing authorization on internal-only endpoints exposed through API gateway misconfiguration
- URL rewriting rules that bypass authorization middleware

## Pattern Category 5: Multi-Tenancy Boundary Violations

- Database queries missing tenant ID filters enabling cross-tenant data access
- Shared caches without tenant-scoped keys enabling data leakage between tenants
- Background jobs processing cross-tenant data without re-verifying authorization
- Tenant context derived from user-controllable headers instead of authenticated session
- Missing tenant boundary enforcement on administrative APIs

## Pattern Category 6: Lateral Movement

- Compromised service credentials used to access adjacent services in the same trust zone
- Shared database credentials across microservices enabling cross-service data access
- Internal APIs without authentication enabling pivot from one compromised service to others
- Overly broad network policies allowing unrestricted east-west traffic between services
- Service mesh configurations missing per-service authorization policies enabling unauthorized inter-service calls

## Pattern Category 7: Privilege Persistence

- Compromised sessions not invalidated after password change or role revocation
- Cached authorization decisions not refreshed after permission changes
- API keys with admin privileges that lack expiration or rotation policy
- Service accounts with excessive privileges shared across multiple applications
- Missing privilege revocation propagation across distributed authorization services

## Pattern Category 8: Broken Access Control — Function-Level and Field-Level (OWASP A01:2021)

OWASP Top 10 2021 ranked Broken Access Control as the **#1 risk** (up from #5 in 2017), surpassing injection for the first time in OWASP history. The category aggregates 34 CWEs and was the most-tested vulnerability class in OWASP's contributor data set, with 94% of tested applications exhibiting at least one form of broken access control. The pre-existing Pattern Categories 1 and 2 above cover endpoint-level missing checks and object-level IDOR, but A01 also explicitly calls out function-level and field-level authorization failures that warrant their own detection signals: an API endpoint may correctly authorize the *call* yet still leak admin-only fields, and an administrative function may be reachable through a guessable URL even when its sibling endpoints are properly protected.

**Indicators**:

- API endpoint accepts resource identifiers (IDs, slugs, UUIDs) in URL path or query string without a declared per-request authorization check that validates the caller's relationship to the resource
- Administrative or high-privilege function reachable via guessable URL path (`/admin`, `/api/v1/users/:id/delete`, `/internal/*`) without declared RBAC/ABAC enforcement at the route handler
- GraphQL mutation or REST endpoint returns response fields without field-level authorization — admin-only fields (`role`, `internal_notes`, `audit_trail`, `salary`) leak to regular users on shared response shapes
- REST endpoint uses `PUT`/`PATCH`/`DELETE` without ownership verification on the target resource — the request is authenticated but the caller is not validated as the resource owner
- Authorization decisions are made client-side (UI hides admin buttons) without corresponding server-side enforcement on the API
- CORS misconfiguration trusts arbitrary origins, enabling cross-origin authenticated requests that bypass same-origin authorization assumptions
- Force-browsing to authenticated pages as an unauthenticated user, or to privileged pages as a standard user, succeeds because route protection is configured per-route rather than via a default-deny policy

**Primary source**:

- OWASP Top 10 2021 A01:2021 Broken Access Control: https://owasp.org/Top10/A01_2021-Broken_Access_Control/
- CWE-639 Authorization Bypass Through User-Controlled Key: https://cwe.mitre.org/data/definitions/639.html
- CWE-862 Missing Authorization (rank 11 on 2024 CWE Top 25): https://cwe.mitre.org/data/definitions/862.html
- CWE-863 Incorrect Authorization: https://cwe.mitre.org/data/definitions/863.html
- OWASP API Security Top 10 2023 API3 Broken Object Property Level Authorization: https://owasp.org/API-Security/editions/2023/en/0xa3-broken-object-property-level-authorization/
- OWASP Authorization Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html

**Example**: A SaaS HR application exposes `GET /api/v2/employees/:id`. The endpoint correctly validates a JWT and rejects unauthenticated callers, but the response shape includes `salary`, `performance_review_notes`, and `manager_internal_comments` fields that are intended for HR users only. A regular employee discovers they can fetch their own record and observe that `manager_internal_comments` is populated. They iterate the `:id` parameter through the predictable employee ID range (1..N) and recover the salary and review notes for every employee in the company in ten minutes. The endpoint had call-level authorization but no field-level authorization, so the same response shape was served to every authenticated caller regardless of role.

**Mitigation**:

- Implement default-deny authorization at the framework level: every route requires an explicit policy declaration; missing declarations fail closed rather than open
- Enforce field-level authorization at the serialization layer: response shapes are filtered against the caller's role before serialization, so admin-only fields are stripped from non-admin responses
- Use opaque, unguessable resource identifiers (UUIDv4 minimum) instead of sequential integers for any resource that must not be enumerated — combine with ownership checks rather than relying on opacity alone
- Enforce ownership verification on all `PUT`/`PATCH`/`DELETE` operations: the handler must look up the resource and confirm the authenticated caller is the owner (or has explicit shared-access grants) before mutating
- Centralize authorization decisions in a policy engine (OPA, Cedar, custom RBAC service) rather than scattering checks throughout route handlers — easier to audit for missing checks
- Add authorization assertions to integration tests: every endpoint must have a "regular user cannot access admin route" test case that fails CI if the endpoint becomes reachable

## Pattern Category 9: Improper Privilege Management — Excessive Service Account and Container Privileges (CWE-269)

CWE-269 Improper Privilege Management is one of the foundational privilege weaknesses in the CWE catalog and underpins many real-world cloud and container compromises. It addresses the case where a process operates with more privileges than its function requires — service accounts with wildcard IAM grants, containers running as root, long-lived admin credentials used for routine operations, missing privilege-drop steps after privileged initialization. The closely related CWE-250 Execution with Unnecessary Privileges and CWE-266 Incorrect Privilege Assignment fall under the same root cause: failing to apply least privilege at the workload-identity layer. Unlike the inline patterns above that target endpoint and request-level authorization, this category targets the *identity under which a Process runs*, which is the upstream root cause that makes endpoint-level escalation catastrophic when it occurs.

**Indicators**:

- Container declared to run as root (UID 0) or without an explicit non-root `USER` directive in its base image declaration
- Service account or workload identity has wildcard permissions (AWS `*:*` on `Resource: *`, Kubernetes `cluster-admin` ClusterRoleBinding, GCP `roles/owner` or `roles/editor` at project scope) on a declared scope larger than necessary
- Privilege-dropping step missing after privileged initialization — process binds a privileged port (< 1024), opens a raw socket, or mounts a filesystem and then continues running as root rather than dropping to an unprivileged user via `setuid`/`setgid`/`capset`
- Long-lived privileged credentials (database root account, admin API key, master IAM access key) used for routine application operations rather than scoped-down per-function accounts
- Shared service account across multiple applications or microservices, so a compromise of any one service grants the attacker the union of all services' permissions
- Database connections use a single application-wide superuser role rather than per-tenant or per-feature roles with narrowed grants
- IAM roles attached to compute resources include `iam:PassRole` or `sts:AssumeRole` without `Condition` constraints, enabling privilege chaining via role-assumption escalation
- Build/CI service account has production deploy permissions during routine builds rather than time-bounded just-in-time elevation

**Primary source**:

- CWE-269 Improper Privilege Management: https://cwe.mitre.org/data/definitions/269.html
- CWE-250 Execution with Unnecessary Privileges: https://cwe.mitre.org/data/definitions/250.html
- CWE-266 Incorrect Privilege Assignment: https://cwe.mitre.org/data/definitions/266.html
- CWE Top 25 Most Dangerous Software Weaknesses 2024: https://cwe.mitre.org/top25/archive/2024/2024_cwe_top25.html
- NIST SP 800-53 AC-6 Least Privilege: https://csrc.nist.gov/projects/risk-management/sp800-53-controls/release-search
- AWS IAM least-privilege guidance: https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html

**Example**: A microservices platform deploys an image-resize worker as a Kubernetes Deployment. The Helm chart inherits the cluster's default ServiceAccount, which has been bound to `cluster-admin` ClusterRole "temporarily" during a past incident and never narrowed. The container image is built `FROM alpine` with no `USER` directive, so the resize process runs as root inside the container. An attacker exploits a known ImageMagick command-injection vulnerability in the resize worker, gaining shell-as-root inside the container. From there: the in-pod service account token at `/var/run/secrets/kubernetes.io/serviceaccount/token` grants `cluster-admin`, which the attacker uses to `kubectl exec` into every pod in every namespace including the production database pod, exfiltrating the entire customer dataset. The original vulnerability was a single CVE in ImageMagick — the catastrophic blast radius came from running root-in-container with cluster-admin service account access, both least-privilege violations.

**Mitigation**:

- Set `runAsNonRoot: true` and an explicit `runAsUser` (not 0) in every Pod SecurityContext; reject Pods that omit it via an admission controller (OPA Gatekeeper, Kyverno, Pod Security Admission `restricted` profile)
- Bind every workload to a dedicated ServiceAccount with the minimum RBAC grants needed for its declared function; never use the `default` ServiceAccount
- Audit all wildcard IAM grants quarterly: every `*:*` policy is treated as an exception that must be justified or removed; replace with explicit action lists
- Implement time-bounded just-in-time elevation for privileged operations: production deploys, schema migrations, and incident response use short-lived elevated credentials that auto-expire
- Drop privileges immediately after binding privileged ports — use systemd's `User=`/`Group=` directives, init container patterns, or `capsh --drop=all --user=...` to release elevated capabilities the moment they are no longer needed
- Per-feature database roles: each application feature gets a dedicated database user with grants limited to the tables and operations it touches, instead of sharing one application-wide role with full schema access
- Segment build/CI permissions from production deploy permissions: builds run as a low-privilege identity, deploys require a separate identity with explicit human or workflow approval

## Pattern Category 10: Abuse Elevation Control Mechanism (MITRE ATT&CK T1548)

MITRE ATT&CK T1548 Abuse Elevation Control Mechanism is the canonical post-authentication privilege-escalation tactic family in the Enterprise matrix. It captures the case where an adversary already holds a foothold (via stolen credentials, exploited application, or compromised CI pipeline) and uses operating-system or cloud-platform elevation primitives — `setuid`/`setgid` binaries, `sudo` and sudo caching, Windows UAC bypass, temporary cloud credential elevation — to escalate from their initial low-privilege context to administrator. The related T1068 Exploitation for Privilege Escalation captures the kernel/driver exploit variant. These mechanisms are not authentication or authorization failures per se: the OS or cloud platform is functioning as designed, but the elevation surface is over-broad or under-monitored. The pre-existing Pattern Categories above target application-layer authorization; this category targets the *underlying platform elevation surface* exposed to a compromised workload.

**Indicators**:

- DFD component declares `sudo` access for its workload identity, or runs setuid binaries (`find / -perm -4000` reveals SUID binaries inside the deployment artifact), without a constraint on which commands may be run
- Cloud workload uses temporary privilege elevation (AWS `sts:AssumeRole`, GCP just-in-time access, Azure PIM eligible roles) without `Condition` constraints requiring MFA, source-IP restrictions, or session-tagging
- Container declared with `CAP_SYS_ADMIN`, `CAP_SYS_PTRACE`, `CAP_NET_RAW`, `CAP_DAC_OVERRIDE`, or other dangerous Linux capabilities beyond the minimum set needed for the workload's function
- Kubernetes Pod declared with `securityContext.privileged: true`, `hostNetwork: true`, `hostPID: true`, `hostIPC: true`, or host-path mounts that expose `/`, `/etc`, `/var/run/docker.sock`, or `/proc` from the host
- `sudo` configuration permits passwordless sudo (`NOPASSWD:`) for broad command sets, or `sudo` cached credentials extend longer than the standard 15-minute timeout
- Windows workload runs as a member of the `Administrators` group with UAC disabled or set to "Never notify"
- Cloud audit log does not record assume-role events with the originating session ID, so post-hoc detection of unauthorized elevation chains is impossible
- Service mesh or workload identity federation allows token-exchange flows that elevate from a compute-tier identity to a control-plane identity without explicit policy

**Primary source**:

- MITRE ATT&CK T1548 Abuse Elevation Control Mechanism: https://attack.mitre.org/techniques/T1548/
- MITRE ATT&CK T1548.001 Setuid and Setgid: https://attack.mitre.org/techniques/T1548/001/
- MITRE ATT&CK T1548.003 Sudo and Sudo Caching: https://attack.mitre.org/techniques/T1548/003/
- MITRE ATT&CK T1548.005 Temporary Elevated Cloud Access: https://attack.mitre.org/techniques/T1548/005/
- MITRE ATT&CK T1068 Exploitation for Privilege Escalation: https://attack.mitre.org/techniques/T1068/
- MITRE ATT&CK TA0004 Privilege Escalation tactic: https://attack.mitre.org/tactics/TA0004/
- Kubernetes Pod Security Standards: https://kubernetes.io/docs/concepts/security/pod-security-standards/

**Example**: A data-engineering team operates an Airflow worker fleet on EC2. Each worker runs an unprivileged `airflow` OS user, but the AMI ships with a setuid `pg_dump` wrapper installed for an unrelated legacy backup job. The Airflow workers also assume an EC2 instance role that has `sts:AssumeRole` permission to a `data-export-prod` role with no MFA or session-tag conditions. An attacker compromises one Airflow DAG via a malicious Python dependency, gaining code execution as the `airflow` user. They invoke the setuid `pg_dump` wrapper to read the local PostgreSQL database, then call `sts:AssumeRole` against the `data-export-prod` role using the worker's instance metadata credentials. The cloud audit log records the AssumeRole event but does not bind it to the originating Airflow DAG run. The attacker now operates as the production data-export role for an hour and exfiltrates customer datasets. Two T1548 sub-techniques chained: the local setuid binary (.001) for reading the database, and the unconditioned cloud assume-role (.005) for cloud lateral movement.

**Mitigation**:

- Audit setuid/setgid binaries in every container image and base AMI; remove any not strictly needed for workload function (find `/` `-perm` `-4000` `-o` `-perm` `-2000`)
- Drop all Linux capabilities by default and add back only those required: container `securityContext.capabilities.drop: [ALL]` then add back specific capabilities like `NET_BIND_SERVICE` if needed
- Forbid `privileged: true`, `hostNetwork: true`, and host-path mounts in non-system namespaces via Pod Security Admission `restricted` profile or admission controller (OPA Gatekeeper, Kyverno)
- Add `Condition` clauses to every cloud `sts:AssumeRole` policy: require `aws:MultiFactorAuthPresent`, `aws:SourceIp`, and `aws:RequestTag` constraints so workloads cannot freely chain into higher-privilege roles
- Enable cloud audit log enrichment that binds assume-role events back to the originating session, instance, or pod identity; alert on assume-role from compute identities to high-privilege roles
- Replace passwordless `sudo` with explicit per-command allowlists in `/etc/sudoers.d/`, or replace `sudo` entirely with capability-based execution for daemon processes
- For Windows workloads, enforce UAC at the highest setting and require split-token administrators; deny interactive logon for service accounts
- Apply Kubernetes Pod Security Admission `restricted` profile to all application namespaces; reserve `privileged` only for system namespaces (`kube-system`, CNI, CSI) and audit those quarterly

## Pattern Category 11: Security Misconfiguration Privilege-Gain Variant — Mobile (OWASP M8:2024), Server-Side (OWASP A05:2021), and API-Specific (OWASP API8:2023)

OWASP M8:2024 (Security Misconfiguration) names mobile-tier configuration weaknesses as a distinct attack class from generic server-side broken access control (Pattern Categories 1-10 above). Where the pre-existing categories cover endpoint-level authorization gaps, workload-identity over-privilege, and platform elevation surfaces at server tier, **Pattern Category 11 targets the mobile-platform misconfiguration surface that enables privilege gain** — exposed debug endpoints retained in release builds (e.g., `/debug` HTTP route reachable from a release-signed APK, debug ContentProvider with `android:exported="true"`); default permissive ContentProvider/Service exports without permission gating (`android:exported="true"` declared without an `android:permission` attribute, allowing any installed app to invoke the component); missing app-attestation on transaction-confirmation paths (no Play Integrity API on Android / DeviceCheck on iOS, leaving the security-critical operation unable to verify whether the calling client binary is the legitimate signed build running on a non-tampered device); missing root-detection on security-critical features (no SafetyNet attestation / iOS jailbreak detection, allowing a rooted device to execute privileged in-app flows that would normally degrade or refuse on tampered platforms); default-permissive intent filters allowing untrusted callers to invoke privileged components (broad `<intent-filter>` declarations on Activities / Services that handle privileged operations without explicit caller verification). The attacker's goal is to exploit one of these mobile-tier misconfigurations to invoke privileged operations from an unprivileged context — a malicious app on the same device, a phishing-installed companion app, or a remote attacker who has obtained the user's APK and analyzed it. MASTG-RESILIENCE and MASVS-RESILIENCE describe the mobile platform-resilience requirements at section-level granularity. **MITRE ATT&CK Mobile T1626 (Abuse Elevation Control Mechanism — Mobile sub-technique)** describes the abuse pattern at attack-pattern granularity, but is **NOT catalog-resolvable** in `schemas/taxonomy/mitre-attack.yaml` per ADR-036 D-7 catalog-gap rule and therefore appears in mitigation prose only — the catalog-resolvable primary citation for this mobile sub-variant is OWASP M8:2024.

**Server-side variant (OWASP A05:2021)**: This Pattern Category also covers server-side security misconfiguration that enables privilege gain on non-mobile architectures — admin and management endpoints exposed without authentication on the production network (Spring Boot Actuator endpoints at `/actuator/{env,beans,heapdump,threaddump}` reachable without auth, Kubernetes dashboard reachable from the public internet, RabbitMQ / Redis / Memcached management UIs on default ports, database management consoles like phpMyAdmin or Adminer shipped with default-permissive configuration); default credentials retained in production (admin/admin or root with default password from quickstart guides, framework-shipped credentials not rotated post-deployment, cloud sample-app credentials hardcoded in repository); unnecessary management features enabled in production (verbose error pages exposing stack traces and internal architecture, debug toolbars retained, sample applications shipped with framework default install); default-permissive cloud IAM policies (compute service accounts attached with broader permissions than required, S3 bucket policies with `Principal: "*"` and `Effect: "Allow"`, IAM roles with `Resource: "*"` wildcard, Kubernetes ClusterRoleBindings binding `cluster-admin` to default service accounts); disabled or weak controls on management surfaces (TLS optional or downgrade-tolerant on internal admin APIs, mTLS not enforced on Kubernetes API server, basic-auth retained on health-check endpoints reachable externally). The OWASP A05:2021 architectural-tell is the deployment / configuration / hardening posture itself, distinct from the Pattern Categories 1–10 surface (authorization decision logic on application routes and IAM policy structure). Both can chain (default Spring Actuator at `/actuator/env` exposes credentials → broken access control on internal admin endpoint → privilege escalation), but the architectural-tells and mitigations are disjoint, so a single architecture surfacing BOTH a Cat 11 server-side A05 finding AND a Cat 1/2/8 broken-access-control finding does not constitute duplicate emission.

**Indicators (mobile / OWASP M8:2024)**:

- Mobile client component declared — primary mobile-platform topology indicator on the security-misconfiguration privilege-gain surface
- Exposed debug endpoint on release build — `/debug` HTTP route reachable from a release-signed APK / IPA, debug ContentProvider with `android:exported="true"` retained from development build, `adb shell` access points retained in production binary, debug-only Activities exported via `<intent-filter>` declarations not stripped during release-flavor compilation
- Default permissive ContentProvider / Service exports without permission gate — `android:exported="true"` declared without an accompanying `android:permission` attribute, allowing any installed app on the device to invoke the component without signature-level or runtime-permission verification
- Missing app-attestation on transaction-confirmation paths — no Play Integrity API integration (Android) / DeviceCheck integration (iOS) on security-critical operations such as money-transfer confirmation, biometric step-up, or sensitive-data export, leaving the privileged operation unable to verify whether the calling client is a legitimate signed build running on a non-tampered platform
- Missing root-detection on security-critical features — no SafetyNet attestation (Android) / iOS jailbreak detection on privileged in-app flows, allowing a rooted / jailbroken device to execute the privileged operation without the platform-integrity guarantee that the operation would otherwise depend on
- Default-permissive intent filters on Activities / Services handling privileged operations — broad `<intent-filter>` declarations matching action / category / data patterns that allow arbitrary local apps to invoke the privileged component, without explicit caller-verification (calling-package check, signature-level permission, signed deep-link payload)
- R8 / ProGuard mapping protection absent or weak — release binary ships with full debug symbols, no obfuscation pass, or with a `mapping.txt` exposed in the production artifact, enabling an attacker to reverse-engineer the privileged code paths and identify the exact intent / ContentProvider / debug-route surfaces to abuse

**Indicators (server-side / OWASP A05:2021)**:

- Admin or management endpoint exposed without authentication on the production network — Spring Boot Actuator endpoints at `/actuator/{env,beans,heapdump,threaddump}` reachable without auth, Kubernetes dashboard reachable from public internet, RabbitMQ / Redis / Memcached management UIs on default ports, database management consoles (phpMyAdmin, Adminer) shipped with default-permissive configuration
- Default credentials retained in production — admin/admin or root with default password from quickstart guides, framework-shipped credentials (e.g., default Tomcat manager password) not rotated post-deployment, cloud sample-app credentials hardcoded in repository
- Unnecessary management features enabled in production — verbose error pages exposing stack traces and internal architecture, debug toolbars (`Django Debug Toolbar`, `Flask-DebugToolbar`), sample applications shipped with framework default install (e.g., Tomcat ROOT.war, default Wordpress themes), CMS plugin admin panels enabled at default URLs
- Default-permissive cloud IAM policies — compute service accounts attached with broader permissions than required (e.g., EC2 instance role with `s3:*` instead of `s3:GetObject` on a single bucket), S3 bucket policies with `Principal: "*"` and `Effect: "Allow"`, IAM roles with `Resource: "*"` wildcard, Kubernetes ClusterRoleBindings binding `cluster-admin` to default service accounts
- Disabled or weak controls on management surfaces — TLS optional or downgrade-tolerant on internal admin APIs, mTLS not enforced on Kubernetes API server, basic-auth retained on health-check endpoints reachable externally, default permissive CORS allowing arbitrary origins on admin endpoints
- Default-permissive feature flags or experimental flags enabled in production — debug-only feature flags (`enable_admin_bypass`, `skip_authz_check`) retained in production, experimental authentication backends (`development_auth`) configured as fallback, internal-only API routes accidentally registered on the public router

**Indicators (API-specific / OWASP API8:2023)**:

- API documentation auto-generation publicly exposed in production — Swagger UI / OpenAPI spec / GraphQL Voyager reachable on the production API host without authentication, exposing the full API surface inventory to attackers including admin-only endpoints, deprecated routes, and internal-only operations
- GraphQL introspection enabled in production — `__schema` and `__type` queries return the complete schema graph, allowing attackers to enumerate every query, mutation, type, and field including admin-only operations and field-level authorization gaps
- Verbose error responses on API endpoints — production API returns full stack traces, framework version banners, ORM query traces, or internal request-correlation metadata in error response bodies, accelerating reconnaissance for follow-on attacks
- Missing or weak security headers on API responses — absent HSTS, CSP, X-Content-Type-Options, X-Frame-Options, Referrer-Policy on API responses; or default-permissive CORS allowing arbitrary origins (`Access-Control-Allow-Origin: *` paired with `Access-Control-Allow-Credentials: true`)
- Default JWT signing keys retained in production — JWT secret default-shipped from a quickstart guide (e.g., literal "secret", "your-256-bit-secret"), framework-default signing key not rotated post-deployment, or asymmetric signing key pair generated once and committed to repository
- API gateway without per-route configuration hardening — default mock-response endpoints retained, default-permissive throttling tier applied to admin routes, debug routes (`/debug`, `/internal`, `/_admin`) not stripped from production deployment, undocumented "preview" endpoints reachable without auth gating
- Insufficient TLS or weak cipher configuration on the API edge — TLS 1.0 / 1.1 enabled, weak ciphers retained (RC4, 3DES, export-grade), missing OCSP stapling, self-signed or expired certificates in production, mTLS not enforced on internal service-to-service calls
- Sample applications or testing endpoints reachable on production API hosts — Postman mock servers exposed, OpenAPI sandbox endpoints not stripped, tutorial-shipped `/api/example` or `/api/echo` endpoints retained, framework-default `/health/secret` endpoints exposing internal config

**Primary source**:

- OWASP M8:2024 — Security Misconfiguration: https://owasp.org/www-project-mobile-top-10/2023-risks/m8-security-misconfiguration
- OWASP Top 10 2021 A05:2021 — Security Misconfiguration: https://owasp.org/Top10/A05_2021-Security_Misconfiguration/
- OWASP API Security Top 10 2023 API8:2023 — Security Misconfiguration: https://owasp.org/API-Security/editions/2023/en/0xa8-security-misconfiguration/
- CWE-732 — Incorrect Permission Assignment for Critical Resource: https://cwe.mitre.org/data/definitions/732.html
- CWE-1188 — Insecure Default Initialization of Resource: https://cwe.mitre.org/data/definitions/1188.html
- CWE-1004 — Sensitive Cookie Without HttpOnly Flag: https://cwe.mitre.org/data/definitions/1004.html
- CWE-16 — Configuration: https://cwe.mitre.org/data/definitions/16.html
- OWASP MASVS-PLATFORM — Mobile Application Security Verification Standard, Platform Interaction Requirements (section-level granularity)
- OWASP MASTG-RESILIENCE — Mobile Application Security Testing Guide, Resilience Test Cases (section-level granularity)

**Example**: A mobile money-transfer Android app retains a debug-only `MoneyTransferDebugProvider` ContentProvider in its release build because the release-flavor build configuration was not migrated when the team added the provider for QA acceptance testing. The provider declares `android:exported="true"` without an `android:permission` attribute, intended (in development) for the QA harness to seed transfer state. The app also has no Play Integrity API integration on its `confirmMoneyTransfer()` server-side call path, which trusts the client's signed JWT for caller-identity but does not verify the calling client's binary integrity or device-platform integrity. An attacker on a rooted device installs a malicious companion app from a third-party app store; the malicious app invokes `MoneyTransferDebugProvider` via `ContentResolver.query(...)` and reads pending-transfer state including session tokens that the QA harness needed for test seeding. The malicious app then issues a `confirmMoneyTransfer()` request to the production banking API using the harvested session token. The server accepts the call because the JWT is valid and there is no Play Integrity attestation header to reject; the transfer completes. Two interlocking misconfigurations chained: the exposed debug ContentProvider for token harvest (CWE-732 incorrect permission assignment), and the missing app-attestation for binary-integrity verification (OWASP M8:2024 misconfiguration on the security-critical path). MITRE ATT&CK Mobile T1626 (Abuse Elevation Control Mechanism — Mobile sub-technique) describes the abuse pattern: the attacker abuses a misconfigured platform-elevation surface (debug ContentProvider export) to escalate from unprivileged-app context to authenticated-banking-session context, bypassing the server-side authorization model the app relied on.

**Mitigation**:

- Strip debug routes / debug ContentProviders / debug Activities from release builds via build-flavor configuration — Android Gradle `buildTypes.release { ... }` blocks excluding debug-only AndroidManifest entries; iOS conditional compilation flags excluding debug-only URL schemes; build-time validation that asserts no `*Debug*` named components ship in release artifacts
- Enforce permission-gated ContentProvider / Service exports — set `android:exported="false"` on all components NOT requiring cross-app invocation; for components that DO require cross-app invocation, declare `android:permission` with a signature-level permission (only apps signed by the same key can invoke) or a runtime permission with appropriate `protectionLevel`
- Integrate Play Integrity API (Android) / DeviceCheck (iOS) on transaction-confirmation paths and other security-critical operations — generate an attestation token client-side, attach it to the privileged-operation request, verify the attestation server-side BEFORE executing the privileged operation; reject requests with absent / expired / failed-attestation tokens
- Integrate root-detection on security-critical features — SafetyNet (deprecated; migrate to Play Integrity API) / Play Integrity API attestation as the primary signal on Android; iOS jailbreak-detection libraries cross-checked against multiple signals (filesystem checks, sandbox-violation tests, dynamic-loader checks); degrade UX or block the privileged feature on rooted / jailbroken devices per the threat-model risk acceptance
- Audit `<intent-filter>` declarations across the AndroidManifest — for every Activity / Service / Receiver that handles a privileged operation, verify either `android:exported="false"` OR explicit caller-verification (calling-package check via `getCallingPackage()`, signature-level permission, signed deep-link payload with HMAC verification at intent-receipt time)
- Enable R8 (Android) / Bitcode + LLVM optimization (iOS) on release builds with full obfuscation; protect the `mapping.txt` (Android) / `dSYM` (iOS) symbol files in private artifact storage NOT shipped to production; treat the symbol files as a build-time secret with restricted access, used only for crash-report symbolication
- MITRE ATT&CK Mobile T1626 (Abuse Elevation Control Mechanism — Mobile sub-technique) describes this abuse pattern; defenders should monitor for in-app intent invocations from unexpected calling packages and emit telemetry events on debug-component invocations (which should be zero in production) — anomalies indicate either misconfigured release builds or active exploitation
- For the OWASP A05:2021 server-side variant, enforce hardened-by-default deployment posture — disable management endpoints (Spring Actuator `management.endpoints.web.exposure.exclude=*` then explicitly include only `health,info`) on the production network; rotate all default credentials at deployment time via secrets-management automation (HashiCorp Vault, AWS Secrets Manager); strip sample apps and verbose error pages via build-time profile activation (`SPRING_PROFILES_ACTIVE=prod` with explicit prod-only application.yaml that disables debug toolbars); apply least-privilege cloud IAM policies via policy-as-code (e.g., AWS IAM Access Analyzer to detect `*:*` wildcards; Kubernetes Pod Security Standards baseline-or-restricted); enforce mTLS on internal management surfaces (Istio mesh-wide STRICT mode; Kubernetes API server `--client-ca-file` enforcement); audit feature flags with a CI gate that fails the build when debug-only flags are enabled in the production profile
- For the OWASP API8:2023 API-specific variant, enforce hardened-by-default API-edge posture — disable GraphQL introspection in production (`graphql-yoga` `disableIntrospection: true`, `apollo-server` `introspection: false` on production builds); strip auto-generated API documentation from production (Swagger UI / OpenAPI spec served only on internal-network or developer-portal hosts, never on the public production API); enforce strict CORS allowlists derived from a centralized origin registry (no wildcard `*` Origin paired with `Allow-Credentials`); rotate JWT signing keys at deployment via secrets-management automation; apply per-route configuration policy at the API gateway (default-deny on undocumented routes; per-route throttling tiers tied to operation-sensitivity classification); enforce TLS 1.2+ with modern cipher suites and OCSP stapling at the API edge; integrate API-specification-driven tests in CI that reject any non-documented endpoint reaching production

## Pattern Category Disambiguation

Pattern Category 11 (M8 Privilege-Gain Variant — Mobile Security Misconfiguration / OWASP M8:2024) and the pre-existing Pattern Categories 1–10 (generic privilege-escalation signal class — broken access control, IDOR, role and permission escalation, path traversal and scope bypass, multi-tenancy boundary violations, lateral movement, privilege persistence, function/field-level authorization gaps, improper privilege management, and abuse elevation control mechanism) share the OWASP A01:2021 Broken Access Control / CWE-269 Improper Privilege Management family at the OWASP framework level but address distinct architectural-tells and mitigation surfaces:

- **Pattern Categories 1–10** (Broken Access Control, IDOR, Role and Permission Escalation, Path Traversal and Scope Bypass, Multi-Tenancy Boundary Violations, Lateral Movement, Privilege Persistence, Function-Level and Field-Level Authorization Gaps, Improper Privilege Management, Abuse Elevation Control Mechanism — pre-existing) detect generic server-side privilege-escalation gaps at any client/server architecture — server-side IDOR, role-confusion vulnerabilities at the API layer, broken access control at HTTP route handlers, IAM misconfiguration on cloud workload identities, multi-tenancy boundary failures in shared backends. The architectural-tell is a server-side authorization decision point — an API endpoint, a workload identity, a multi-tenant database query, a cloud IAM role, a Kubernetes RBAC binding — NOT a mobile-platform topology.
- **Pattern Category 11** (M8 Privilege-Gain Variant — Mobile Security Misconfiguration — F-7) detects mobile-platform misconfiguration enabling privilege gain on declared mobile clients — debug ContentProvider exports retained in release builds, missing Play Integrity / DeviceCheck attestation on security-critical operations, root-detection bypass on security-critical features, default-permissive intent filters allowing untrusted callers to invoke privileged components. The architectural-tell is a declared mobile client component with manifest-level export declarations, build-flavor configuration handling, and mobile-attestation surface.

**Disambiguation hinge**: server-side IDOR is generic to any client/server architecture and is detected by inspecting the server-side authorization decision point (route handler, query filter, IAM policy); mobile misconfiguration requires inspection of the mobile manifest (`AndroidManifest.xml` exported flags + `<intent-filter>` declarations + `android:permission` attributes on exported components), the mobile app build configuration (debug-flag handling, R8 / ProGuard mapping protection, build-flavor exclusions of debug-only components), and the mobile attestation surface (Play Integrity API / DeviceCheck integration on transaction-confirmation paths). Same architecture exhibiting BOTH a Cat 1–10 server-side finding AND a Cat 11 mobile finding does not constitute duplicate emission — the architectural-tells are disjoint and the mitigations are different (server-side authorization gating vs mobile manifest hardening + attestation integration).

**Worked example — hybrid web+mobile fintech architecture**: a fintech platform with both a server-side admin panel (web session cookies, server-side role-based authorization, multi-tenant database with tenant-ID filters) and an Android/iOS client (mobile binary distribution, deep-link intents for transfer-confirmation, biometric step-up flows) may legitimately surface BOTH a pre-existing Cat 1 / Cat 2 finding on the server-side admin panel (e.g., an `/api/v2/admin/users/:id` endpoint missing role-level authorization, allowing a regular user to enumerate admin records — broken access control at the server route handler) AND a new Cat 11 finding on the mobile client (e.g., a debug ContentProvider exposed in the release-build APK enabling a malicious companion app to read pending-transfer session tokens, paired with missing Play Integrity attestation on the `confirmMoneyTransfer()` server-side call path). Two findings, two disjoint architectural-tells, zero duplication. The Cat 1-10 mitigation (centralize authorization decisions in a policy engine, enforce default-deny at the framework level, add field-level authorization to API responses) is orthogonal to the Cat 11 mitigation (strip debug components from release builds, integrate Play Integrity attestation, enforce permission-gated ContentProvider exports). Architect formalizes this carve in ADR-036 Decision 9 (Pattern Category Disambiguation requirement on the F-7 privilege-escalation companion).

## Primary Sources

- OWASP Top 10 2021 A01:2021 Broken Access Control: https://owasp.org/Top10/A01_2021-Broken_Access_Control/
- OWASP API Security Top 10 2023 API1 Broken Object Level Authorization: https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/
- OWASP API Security Top 10 2023 API3 Broken Object Property Level Authorization: https://owasp.org/API-Security/editions/2023/en/0xa3-broken-object-property-level-authorization/
- OWASP API Security Top 10 2023 API5 Broken Function Level Authorization: https://owasp.org/API-Security/editions/2023/en/0xa5-broken-function-level-authorization/
- OWASP Authorization Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
- OWASP Access Control Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Access_Control_Cheat_Sheet.html
- OWASP Insecure Direct Object Reference Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html
- CWE-269 Improper Privilege Management: https://cwe.mitre.org/data/definitions/269.html
- CWE-285 Improper Authorization: https://cwe.mitre.org/data/definitions/285.html
- CWE-639 Authorization Bypass Through User-Controlled Key: https://cwe.mitre.org/data/definitions/639.html
- CWE-862 Missing Authorization: https://cwe.mitre.org/data/definitions/862.html
- CWE-863 Incorrect Authorization: https://cwe.mitre.org/data/definitions/863.html
- CWE-22 Improper Limitation of a Pathname to a Restricted Directory (Path Traversal): https://cwe.mitre.org/data/definitions/22.html
- CWE-250 Execution with Unnecessary Privileges: https://cwe.mitre.org/data/definitions/250.html
- CWE-266 Incorrect Privilege Assignment: https://cwe.mitre.org/data/definitions/266.html
- CWE Top 25 Most Dangerous Software Weaknesses 2024: https://cwe.mitre.org/top25/archive/2024/2024_cwe_top25.html
- MITRE ATT&CK T1548 Abuse Elevation Control Mechanism: https://attack.mitre.org/techniques/T1548/
- MITRE ATT&CK T1548.001 Setuid and Setgid: https://attack.mitre.org/techniques/T1548/001/
- MITRE ATT&CK T1548.003 Sudo and Sudo Caching: https://attack.mitre.org/techniques/T1548/003/
- MITRE ATT&CK T1548.005 Temporary Elevated Cloud Access: https://attack.mitre.org/techniques/T1548/005/
- MITRE ATT&CK T1068 Exploitation for Privilege Escalation: https://attack.mitre.org/techniques/T1068/
- MITRE ATT&CK T1078 Valid Accounts: https://attack.mitre.org/techniques/T1078/
- MITRE ATT&CK TA0004 Privilege Escalation tactic: https://attack.mitre.org/tactics/TA0004/
- NIST SP 800-53 AC-6 Least Privilege: https://csrc.nist.gov/projects/risk-management/sp800-53-controls/release-search
- Kubernetes Pod Security Standards: https://kubernetes.io/docs/concepts/security/pod-security-standards/
- AWS IAM least-privilege best practices: https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- OWASP M8:2024 Security Misconfiguration: https://owasp.org/www-project-mobile-top-10/2023-risks/m8-security-misconfiguration
- OWASP MASVS-PLATFORM: https://mas.owasp.org/MASVS/05-MASVS-PLATFORM/
- OWASP Top 10 2021 A05:2021 Security Misconfiguration: https://owasp.org/Top10/A05_2021-Security_Misconfiguration/
- CWE-1188 Insecure Default Initialization of Resource: https://cwe.mitre.org/data/definitions/1188.html
- CWE-1004 Sensitive Cookie Without HttpOnly Flag: https://cwe.mitre.org/data/definitions/1004.html
