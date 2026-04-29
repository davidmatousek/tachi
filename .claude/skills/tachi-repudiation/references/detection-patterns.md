---
name: repudiation-detection-patterns
description: Externalized detection pattern catalog for STRIDE repudiation — missing audit trails, insufficient log detail, log tampering, timestamp manipulation
consumers: [tachi-repudiation]
last_updated: 2026-04-11
---

# Repudiation Detection Patterns

## Overview

Detection vocabulary for the STRIDE Repudiation threat category. Loaded at detection start by `tachi-repudiation` agent via a single `**MANDATORY**: Read` directive. Covers the six pre-existing pattern categories carried forward verbatim from the pre-refactor agent file plus two enriched categories sourced from OWASP A09:2021 and MITRE ATT&CK T1070.

## Targeted DFD Element Types

- **External Entity**: End users, API consumers, third-party integrations, administrative users, automated clients
- **Process**: Application services, payment processors, authorization services, data export services, administrative interfaces

## Missing Audit Trails

- Security-sensitive operations (login, logout, permission changes) not logged
- Financial transactions without immutable audit records
- Data deletion operations without pre-deletion snapshots or tombstone records
- Administrative actions (user creation, role assignment) missing from audit logs
- API calls that modify state without recording the authenticated caller identity

## Insufficient Log Detail

- Logs missing actor identity (who performed the action)
- Logs missing timestamp with sufficient precision (sub-second for high-frequency systems)
- Logs missing source context (IP address, session ID, request correlation ID)
- Logs missing the before-and-after state for data modifications
- Generic log messages that cannot distinguish between different operation types

## Log Tampering Vulnerability

- Application logs stored in locations writable by the application itself
- Missing log integrity protection (no append-only storage, no cryptographic chaining)
- Log rotation that deletes entries before compliance retention period expires
- Database audit tables modifiable through the same connection as application data
- Missing log forwarding to immutable external storage (SIEM, write-once bucket)

## Deniable Actions

- Anonymous or unauthenticated operations that modify system state
- Shared credentials or service accounts where individual accountability is impossible
- Operations completed through side channels not covered by primary audit system
- Batch operations logged as a single entry without individual item attribution
- Missing non-repudiation controls on legally binding transactions (e-signatures, notarization)

## Timestamp Manipulation

- System clocks not synchronized via NTP, enabling clock skew between services to create ambiguous event ordering
- Timestamps generated client-side or by untrusted sources without server-side validation
- Log timestamps using local time instead of UTC, creating ambiguity across time zones
- Missing monotonic or logical clocks for ordering events in distributed systems
- Timestamp precision insufficient to distinguish rapid sequential operations (coarse granularity enabling plausible deniability)

## Log Injection and Evasion

- User-controlled data written to logs without sanitization (log injection)
- Log entries constructable by attackers to create false audit trails
- Missing correlation between distributed service logs (gaps in tracing)
- Log level configuration that suppresses security events in production

## Pattern Category 7: Security Logging and Monitoring Coverage Gaps

OWASP A09:2021 unified the historically under-documented repudiation surface into a canonical pattern: privileged operations performed without declared audit event emission, or with event emission that fails to reach an aggregation/retention tier capable of surviving the actor that produced them. This category detects architectures where the audit path is incomplete — emission missing, transport missing, aggregation missing, or retention horizon shorter than the incident-response window — such that a privileged action cannot be reconstructed after the fact.

**Indicators**:

- Process performs privileged operations (authentication decisions, authorization grants, financial transactions, configuration changes, PII access, export/download of sensitive data) without declared audit event emission at the decision point
- Audit events written only to local filesystem or local syslog with no central aggregation (SIEM, log lake, append-only bucket)
- Audit log schema missing any of: actor identity, action type, precise timestamp, request correlation ID, outcome/decision, target resource
- Retention window declared shorter than the applicable compliance or incident-response horizon (e.g., 7 days for systems subject to 90-day investigation requirements)
- High-volume or batch operations logged with coarse aggregation (one entry per batch, not per item) such that individual actions cannot be attributed
- Critical business events (payment capture, refund issuance, role elevation, secret rotation) not surfaced to a real-time alerting path
- Application emits logs but the architecture does not declare the log-processing pipeline (producer → transport → aggregator → retention store)

**Primary source**:

- OWASP Top 10 2021 A09: Security Logging and Monitoring Failures: https://owasp.org/Top10/A09_2021-Security_Logging_and_Monitoring_Failures/
- CWE-778: Insufficient Logging: https://cwe.mitre.org/data/definitions/778.html
- CWE-223: Omission of Security-Relevant Information: https://cwe.mitre.org/data/definitions/223.html
- OWASP Application Logging Vocabulary Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Application_Logging_Vocabulary_Cheat_Sheet.html

**Example**: A SaaS platform's admin console issues organization-scoped role grants via an HTTP POST that updates a PostgreSQL `memberships` table and returns 200. The architecture declares RBAC enforcement on the endpoint but does not declare any audit event emission on the grant path. A support engineer elevates a customer account to `owner`, performs a sensitive action under that role, and reverts the elevation ninety minutes later. Ninety days later the customer files a dispute over the action. The engineer denies having performed it. The only evidence of the elevation is a transient row in the `memberships` table — since overwritten — and application logs retained for seven days that showed only endpoint latency, not the role change decision. The platform cannot attribute the action to any actor and has no evidence to contest the dispute.

**Mitigation**:

- Instrument every privileged decision point with a structured audit event emitted synchronously before the decision takes effect; fail the operation if emission fails
- Standardize the audit event schema on actor identity, action type, UTC timestamp with microsecond precision, request correlation ID, target resource URN, decision outcome, and the authorizing rule
- Forward audit events to an append-only aggregation tier (SIEM, write-once bucket with object-lock, immutable log service) within 60 seconds; retention horizon set to the longer of regulatory requirement or incident-response window (typically 12 months minimum)
- Declare the audit pipeline explicitly in the architecture: producer component, transport mechanism, aggregator, retention store, alerting rules
- Separate audit-event emission from general-purpose application logging so retention and alerting policies can diverge

## Pattern Category 8: Indicator Removal and Timestomping (ATT&CK T1070)

Post-compromise log destruction is a distinct repudiation vector from the absence of logs: the attacker has already acted, the events were captured, and now the attacker removes or alters the evidence. MITRE ATT&CK T1070 catalogs the technique family — clearing platform event logs (T1070.001/.002), mailbox clearing (T1070.008), file deletion (T1070.004), and timestomping (T1070.006). This category detects architectures where the log store is within the same trust zone as the component being audited, or where log immutability enforcement is absent, such that a compromised identity can obliterate its own trail.

**Indicators**:

- Log store is writable by the same identity, service account, or container that produces audit events (no separation of duty between producer and writer)
- No immutable-store backing declared: S3 without Object Lock, Azure Storage without Immutable Blob, GCS without retention lock, local syslog without remote forwarder
- Logs stored in the same trust zone as the component being audited — no off-box, off-account, or off-network forwarding to a dedicated logging tier
- Timestamp source is attacker-controllable: system local clock with no NTP enforcement, no signed timestamps (RFC 3161 or equivalent), no cryptographic chaining (hash-linked log entries)
- Log rotation, truncation, or retention reduction can be triggered from the same privilege context as log production
- Windows event logs, Linux journald/syslog, macOS unified log, or cloud-platform audit trails configured but not forwarded to an external aggregator
- Mailbox audit clearing permissions (Exchange `Set-MailboxAuditLog`, M365 unified audit log purge) granted to administrative identities without separation
- File modification times mutable by the identity that created the file (no secure timestamp service, no hash-chained immutable log)

**Primary source**:

- MITRE ATT&CK T1070: Indicator Removal: https://attack.mitre.org/techniques/T1070/
- MITRE ATT&CK T1070.001: Clear Windows Event Logs: https://attack.mitre.org/techniques/T1070/001/
- MITRE ATT&CK T1070.002: Clear Linux or Mac System Logs: https://attack.mitre.org/techniques/T1070/002/
- MITRE ATT&CK T1070.006: Timestomp: https://attack.mitre.org/techniques/T1070/006/
- MITRE ATT&CK TA0005: Defense Evasion (tactic): https://attack.mitre.org/tactics/TA0005/
- NIST SP 800-92: Guide to Computer Security Log Management

**Example**: A payment-processing microservice runs in a Kubernetes pod with a service account that has PutObject and DeleteObject on the S3 bucket containing its own audit logs. The bucket has no Object Lock configured and no versioning. The pod is compromised via a deserialization vulnerability; the attacker invokes the AWS SDK from within the process to list and delete the most recent audit log objects covering the window of the compromise. The SIEM ingestion pipeline is fed from the same bucket and has already rotated through its local cache. Three weeks later a dispute surfaces a payment that was captured but never fulfilled. Forensics can determine the payment capture succeeded from the payment processor side but has no record of what the microservice did — the evidence has been deleted by the compromised identity.

**Mitigation**:

- Write audit logs to a target where the producing identity has append-only permission and no delete permission: S3 with Object Lock in compliance mode, Azure Immutable Blob Storage with legal hold, or a dedicated logging account with cross-account write-only grant
- Forward logs out-of-process and off-box to a dedicated logging tier under a separate trust boundary before retention clocks start; the log producer should not be able to reach the log store after emission
- Use a secure, external timestamp source (NTP with authenticated servers, RFC 3161 signed timestamps, or a hash-chained append-only log such as AWS CloudTrail Lake with file integrity validation) for every audit entry
- Enable platform-native immutability controls on any file-based log store: chattr +a on Linux append-only files, Windows EventLog access control separation, macOS Secure Enclave-backed logging
- Separate mailbox audit log configuration and purge rights from operational administrative identities; require just-in-time privileged access with its own audit trail for audit administration

## Pattern Category 9: M8 Accountability-Loss Variant — Mobile Security Misconfiguration

OWASP M8:2024 (Security Misconfiguration) names mobile-tier configuration weaknesses as a distinct attack class from generic server-side audit-log gaps and log-tampering vulnerabilities (Pattern Categories 1-8 above). Where the pre-existing categories cover server-side accountability failures (missing audit trails, insufficient log detail, log tampering vulnerability, deniable actions, timestamp manipulation, log injection and evasion, security logging and monitoring coverage gaps, indicator removal and timestomping), **Pattern Category 9 targets the mobile-platform misconfiguration surface that enables accountability loss** — missing audit logging on auth state transitions (no event emission on login / logout / step-up / token-refresh decision points); missing audit logging on biometric prompt outcomes (no event emission on biometric prompt success / failure / cancellation, removing forensic evidence of step-up authentication on sensitive operations); disabled crash reporting in production (Firebase Crashlytics / Sentry / Bugsnag explicitly disabled in release builds, or PII-scrubbed so aggressively that the crash channel emits no actionable signal — destroying the post-incident reconstruction surface that crash dumps would otherwise provide); debug logs leaking sensitive data via `Log.d` / `NSLog` in release builds (no `BuildConfig.DEBUG` gating on Android `Log.d`/`Log.v` calls; no `#if DEBUG` gating on iOS `NSLog` calls — the leakage and the missing audit trail are interlocking consequences: sensitive data appears in attacker-readable on-device logs while the security-relevant audit channel emits nothing); missing tamper-evident timestamping on transaction logs (no server-attested timestamps on transaction audit records, no client-side continuity verification — a compromised mobile client can rewrite or backdate local audit records to fabricate or hide transactions); audit log writers with no integrity protection (mobile audit log file is writable by the same identity that produces audit events, no off-device forwarding to an immutable store before retention clocks start, no cryptographic chaining of audit entries — the same compromised app identity that generated the events can erase or rewrite them). The attacker's goal is to exploit one or more of these misconfigurations to defeat post-incident accountability — when a customer disputes a transaction sixty days later, when a regulator audits the platform, when a forensic investigator reconstructs an attack path. MASTG-CODE and MASVS-CODE describe the mobile platform-code requirements at section-level granularity. **MITRE ATT&CK Mobile T1398 (Boot or Logon Initialization Scripts — Mobile sub-technique)** is cited as supporting context for the boot-time / login-time accountability surface, but is **NOT catalog-resolvable** in `schemas/taxonomy/mitre-attack.yaml` per ADR-036 D-7 catalog-gap rule and therefore appears in mitigation prose only — the catalog-resolvable primary citation for this Pattern Category is OWASP M8:2024.

**Indicators**:

- Mobile client component declared — primary mobile-platform topology indicator on the security-misconfiguration accountability-loss surface
- Missing audit logging on auth state transitions (login / logout / step-up / token-refresh) — no event emission at the decision point on the mobile client; the server-side authn API may log the request, but the mobile-side outcome (was step-up biometric required? did the user cancel? was the refresh-token rotation successful from the client's perspective?) is not captured, removing client-attributable audit evidence
- Missing audit logging on biometric prompt outcomes — `BiometricPrompt.AuthenticationCallback` (Android) / `LAContext.evaluatePolicy` (iOS) outcomes (success / failure / cancellation / lockout) not captured in any audit channel; the client cannot prove the biometric step-up was presented to the user, only that the server-side privileged operation eventually succeeded
- Disabled crash reporting in production — Firebase Crashlytics / Sentry / Bugsnag explicitly disabled in the release build configuration (e.g., `Crashlytics.setCrashlyticsCollectionEnabled(false)` shipped in release flavor), OR PII-scrubbed so aggressively (custom `setCustomKeys` filters that strip every contextual field) that the crash channel is operationally useless — destroying the post-incident reconstruction surface for crashes that occur during privileged operations
- Debug logs leaking sensitive data via `Log.d` / `NSLog` in release builds — no `if (BuildConfig.DEBUG) Log.d(...)` gating on Android; no `#if DEBUG NSLog(...) #endif` gating on iOS; `Log.d`/`Log.v` calls in transaction-confirmation paths log full PAN / cardholder names / OAuth tokens / OTP codes to the on-device logcat / NSLog buffer, accessible to any installed app with `READ_LOGS` permission on older Android or via attached debugger / `idevicesyslog` on iOS — the leakage AND the missing audit trail interlock: sensitive data is in attacker-readable channels while the security-relevant audit channel emits nothing
- Missing tamper-evident timestamping on transaction logs — no server-attested timestamps on transaction audit records; the mobile client uses the device's local clock (attacker-controllable on a rooted handset), no signed timestamp from the server-side transaction-confirmation response is captured into the client-side audit trail, no client-side continuity verification (no hash-chained audit entries) — a compromised mobile client can rewrite or backdate local audit records
- Audit log writers with no integrity protection — the mobile app's audit log file is writable by the same app identity that produces the audit events (no separation of duty; the same process can create AND destroy entries), no off-device forwarding to an immutable backend store before retention clocks start, no cryptographic chaining (no hash-linked log entries that would expose deletion / rewriting), no append-only filesystem flag

**Primary source**:

- OWASP M8:2024 — Security Misconfiguration: https://owasp.org/www-project-mobile-top-10/2023-risks/m8-security-misconfiguration
- CWE-778: Insufficient Logging (cross-references the pre-existing Pattern Category Primary Sources list above): https://cwe.mitre.org/data/definitions/778.html
- CWE-223: Omission of Security-Relevant Information (cross-references the pre-existing Pattern Category Primary Sources list above): https://cwe.mitre.org/data/definitions/223.html
- OWASP MASVS-CODE — Mobile Application Security Verification Standard, Code Quality Requirements (section-level granularity)
- OWASP MASTG-CODE — Mobile Application Security Testing Guide, Code Quality Test Cases (section-level granularity)

**Example**: A mobile money-transfer Android app ships with Firebase Crashlytics disabled in the release build configuration because an early release-flavor Gradle task added `Crashlytics.setCrashlyticsCollectionEnabled(false)` to suppress beta-period false-positive crash spam, and the disable was never reversed for general availability. The same release build retains `Log.d("TransferConfirm", "user=" + user.email + " amount=" + amount + " payee=" + payee.account + " pan=" + card.fullPan)` calls in the transaction-confirmation path, with no `BuildConfig.DEBUG` gating — the team intended to strip these via R8 / ProGuard rules but the obfuscation pass that would have removed them was excluded from the release build flavor due to a build-time symbol-mapping conflict. The audit log writer for the in-app transaction history persists records to a local file in the app's private data partition, writable by the same app identity that produces the events, with no cryptographic chaining and no off-device forwarding to a backend immutable store. Sixty days after a money-transfer event, a customer disputes the transfer, claiming the device was lost in a hotel room and the transfer was unauthorized. Forensics has zero evidence: Crashlytics was disabled (no crash trail on any anomalous behavior during the disputed window), the `Log.d` entries with the transaction context were on-device-only and rotated out of the logcat ring buffer days ago, the local audit log records the transfer as completed but the same compromised app identity that may have produced the unauthorized transfer also has write access to the audit log (so the local audit record cannot be trusted as tamper-evident evidence), and there is no server-attested timestamp continuity proving the transfer record was not retroactively manipulated. The platform cannot rebut the customer's repudiation; the dispute is resolved against the platform with full chargeback. MITRE ATT&CK Mobile T1398 (Boot or Logon Initialization Scripts — Mobile sub-technique) describes a related accountability-loss surface where boot-time / login-time scripts run before audit-event emission begins and therefore evade the audit channel entirely; the same architectural-tell pattern (audit emission gate not engaged at the relevant lifecycle moment) generalizes from boot-time to release-build crash-reporting and `Log.*` configuration.

**Mitigation**:

- Emit structured audit log entries on every auth state transition — login (success / failure / lockout), logout (user-initiated / token-expiry / forced), step-up authentication (challenge issued / succeeded / failed / cancelled), token-refresh (rotation succeeded / refused / detected anomalous); forward to a backend audit pipeline with server-side persistence before the client-side flow proceeds; fail the operation if emission fails on a security-critical path
- Emit structured audit log entries on every biometric prompt outcome — `BiometricPrompt.AuthenticationCallback` `onAuthenticationSucceeded` / `onAuthenticationFailed` / `onAuthenticationError` on Android; `LAContext.evaluatePolicy` reply handler outcomes on iOS; capture lockout / cancellation as distinct outcome categories so absence-of-success does not collapse to a single ambiguous "authentication did not complete" bucket
- Enable Firebase Crashlytics / Sentry / Bugsnag in release builds with PII scrubbing (NOT disabled) — set explicit `setCustomKeys` policies that include sufficient context (component name, build version, anonymized session ID) without leaking PII (no email, no PAN, no OTP); validate at release-build time that the crash collection toggle is `true` in the shipped binary
- Gate every `Log.d` / `Log.v` / `NSLog` call on `BuildConfig.DEBUG` (Android) / `#if DEBUG` (iOS), OR migrate sensitive-context logs to `Log.i` / `OSLog` with explicit redaction of PII fields and structured field tagging — never let a release build emit sensitive raw values into logcat / NSLog / OSLog channels readable by attached tools or other apps
- Add server-attested timestamps to every transaction audit record — the transaction-confirmation API response carries a signed server timestamp (e.g., RFC 3161 timestamp token, JWT-signed timestamp claim); the mobile client persists the signed timestamp into the local audit record alongside the transaction details; client-side continuity verification (hash-chained audit entries with a per-entry hash including the previous entry's hash) detects rewriting / backdating / deletion by exposing a chain break
- Forward audit log entries off-device to an immutable backend store before retention clocks start — the mobile client posts audit records to an audit-pipeline endpoint with append-only semantics on the backend (S3 with Object Lock, write-once bucket, dedicated logging account); the local on-device audit log is treated as a transient transmission queue, NOT as the canonical audit store
- MITRE ATT&CK Mobile T1398 (Boot or Logon Initialization Scripts — Mobile sub-technique) describes accountability-loss surfaces where the audit emission gate is not engaged at the relevant lifecycle moment; defenders should monitor for audit-emission gaps at boot-time, login-time, and release-build crash-reporting initialization paths — anomalies indicate either a misconfigured release build or active exploitation that has bypassed the audit channel by exploiting a not-yet-engaged emission gate

## Pattern Category Disambiguation

Pattern Category 9 (M8 Accountability-Loss Variant — Mobile Security Misconfiguration / OWASP M8:2024) and the pre-existing Pattern Categories 1–8 (generic repudiation signal class — missing audit trails, insufficient log detail, log tampering vulnerability, deniable actions, timestamp manipulation, log injection and evasion, security logging and monitoring coverage gaps, indicator removal and timestomping) share the OWASP A09:2021 Security Logging and Monitoring Failures / CWE-778 Insufficient Logging family at the OWASP framework level but address distinct architectural-tells and mitigation surfaces:

- **Pattern Categories 1–8** (Missing Audit Trails, Insufficient Log Detail, Log Tampering Vulnerability, Deniable Actions, Timestamp Manipulation, Log Injection and Evasion, Security Logging and Monitoring Coverage Gaps, Indicator Removal and Timestomping — pre-existing) detect generic server-side repudiation gaps at any client/server architecture — server-side audit-log gaps in the application layer, missing transaction signing on legally binding operations, log tampering vulnerabilities at the centralized SIEM / write-once bucket / log-rotation policy layer, server-clock timestamp manipulation, log injection at the structured-logging library layer. The architectural-tell is a server-side audit infrastructure component — a centralized SIEM, a write-once bucket with object-lock, a server-side log rotation policy, a database audit table, a server-side timestamp source — NOT a mobile-platform topology.
- **Pattern Category 9** (M8 Accountability-Loss Variant — Mobile Security Misconfiguration — F-7) detects mobile-platform misconfiguration enabling accountability loss on declared mobile clients — `Log.d` / `NSLog` leakage in release builds (no `BuildConfig.DEBUG` / `#if DEBUG` gating), disabled Crashlytics in production builds (or aggressive PII scrubbing rendering the channel useless), missing audit logging on auth state transitions and biometric prompt outcomes specific to the mobile lifecycle, missing tamper-evident timestamping on mobile-emitted transaction logs, audit log writers with no off-device forwarding before retention clocks start. The architectural-tell is a declared mobile client component with manifest-level configuration handling, mobile build-flavor handling (release vs debug build configuration), mobile logging API usage (`Log.*` family / `NSLog` / `OSLog` with subsystem categorization), and mobile crash-reporting SDK integration (Firebase Crashlytics / Sentry / Bugsnag enablement and PII-scrub configuration).

**Disambiguation hinge**: server-side audit-log gaps are inspected via server log infrastructure (centralized SIEM, write-once buckets, server log rotation policies, database audit tables, server-clock NTP enforcement); mobile audit-log gaps are inspected via mobile logging instrumentation (Android `Log.*` family / iOS `NSLog` / `OSLog` with subsystem categorization) and the mobile crash-reporting integration (Firebase Crashlytics / Sentry / Bugsnag enablement and PII-scrub configuration). The mobile-specific tells are orthogonal to server-side tells; same architecture exhibiting BOTH a Cat 1-8 server-side finding AND a Cat 9 mobile finding does not constitute duplicate emission — the architectural-tells are disjoint and the mitigations target different infrastructure layers (server log pipeline vs mobile logging API + crash-reporting SDK).

**Worked example — hybrid web+mobile fintech architecture**: a fintech platform with both a server-side admin panel (centralized SIEM ingesting all admin-action audit events; write-once S3 bucket with Object Lock for compliance retention; server-side NTP-synchronized timestamps on every audit record) and an Android/iOS client (mobile binary distribution; on-device transaction-confirmation flows; biometric step-up; in-app audit log of recent transactions surfaced via the account-history screen) may legitimately surface BOTH a pre-existing Cat 7 finding on the server-side admin panel (e.g., a `/api/v2/admin/users/:id/elevate` endpoint missing structured audit-event emission at the elevation decision point — security logging and monitoring coverage gap at the server-side route handler) AND a new Cat 9 finding on the mobile client (e.g., the release-build APK ships with `Crashlytics.setCrashlyticsCollectionEnabled(false)` and retains `Log.d` calls in the transaction-confirmation path that log full PAN + OTP without `BuildConfig.DEBUG` gating; the in-app audit log is a local file writable by the same app identity that produced the events with no off-device forwarding). Two findings, two disjoint architectural-tells, zero duplication. The Cat 1-8 mitigation (instrument every server-side privileged decision point with synchronous structured audit emission, forward to append-only SIEM / write-once bucket, enforce server-side NTP) is orthogonal to the Cat 9 mitigation (enable Crashlytics in release with PII scrubbing, gate `Log.d` calls on `BuildConfig.DEBUG`, add server-attested timestamps to mobile-emitted audit records, forward off-device to the audit pipeline before retention clocks start). Architect formalizes this carve in ADR-036 Decision 9 (Pattern Category Disambiguation requirement on the F-7 repudiation companion).

**M8 dual-host disjoint architectural-tells**: Cat 9 (this category, accountability-loss variant) and Cat 11 in `tachi-privilege-escalation/references/detection-patterns.md` (privilege-gain variant) are dual hosts of the same OWASP M8:2024 entry per ADR-036 D-4. The architectural-tells are disjoint: Cat 11 detects misconfiguration enabling unauthorized privilege gain (debug ContentProvider exports, missing app-attestation, missing root-detection, default-permissive intent filters); Cat 9 detects misconfiguration enabling accountability loss (missing audit logging, disabled crash reporting, Log.d/NSLog leakage, missing tamper-evident timestamping). Same architecture exhibiting BOTH variants legitimately surfaces both findings — the architectural-tells do not overlap and the mitigation vocabularies are different (authorization-gating + attestation integration vs audit-trail completeness + crash-reporting configuration).

## Primary Sources

- OWASP Top 10 2021 — A09: Security Logging and Monitoring Failures: https://owasp.org/Top10/A09_2021-Security_Logging_and_Monitoring_Failures/
- OWASP API Security Top 10 2023 — API9: Improper Inventory Management
- OWASP Logging Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
- OWASP Application Logging Vocabulary Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Application_Logging_Vocabulary_Cheat_Sheet.html
- CWE-778: Insufficient Logging: https://cwe.mitre.org/data/definitions/778.html
- CWE-223: Omission of Security-Relevant Information: https://cwe.mitre.org/data/definitions/223.html
- CWE-117: Improper Output Neutralization for Logs: https://cwe.mitre.org/data/definitions/117.html
- CWE-779: Logging of Excessive Data: https://cwe.mitre.org/data/definitions/779.html
- MITRE ATT&CK T1070: Indicator Removal: https://attack.mitre.org/techniques/T1070/
- MITRE ATT&CK T1070.001: Clear Windows Event Logs: https://attack.mitre.org/techniques/T1070/001/
- MITRE ATT&CK T1070.002: Clear Linux or Mac System Logs: https://attack.mitre.org/techniques/T1070/002/
- MITRE ATT&CK T1070.006: Timestomp: https://attack.mitre.org/techniques/T1070/006/
- MITRE ATT&CK T1562.006: Indicator Blocking: https://attack.mitre.org/techniques/T1562/006/
- MITRE ATT&CK TA0005: Defense Evasion (tactic): https://attack.mitre.org/tactics/TA0005/
- NIST SP 800-92: Guide to Computer Security Log Management
- PCI DSS Requirement 10: Track and Monitor All Access to Network Resources and Cardholder Data
- OWASP M8:2024 Security Misconfiguration: https://owasp.org/www-project-mobile-top-10/2023-risks/m8-security-misconfiguration
- OWASP MASVS-CODE: https://mas.owasp.org/MASVS/07-MASVS-CODE/
