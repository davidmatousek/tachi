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
