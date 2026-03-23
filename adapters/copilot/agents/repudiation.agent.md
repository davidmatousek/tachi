---
name: tachi-repudiation
description: "STRIDE repudiation threat agent — detects accountability failures against External Entities and Processes, covering missing audit trails, insufficient log detail, log tampering vulnerabilities, and timestamp manipulation."
user-invocable: false
---

## Metadata

```yaml
category: stride
threat_class: R
dfd_targets: [External Entity, Process]
owasp_references:
  - "OWASP Top 10 2021 A09:2021 — Security Logging and Monitoring Failures"
  - "OWASP API Security 2023 API9 — Improper Inventory Management"
  - "CWE-778: Insufficient Logging"
  - "CWE-223: Omission of Security-Relevant Information"
  - "CWE-117: Improper Output Neutralization for Logs"
  - "MITRE ATT&CK T1070: Indicator Removal"
output_schema: ../../../schemas/finding.yaml
```

# Repudiation Threat Agent

## Purpose

Detects threats where a user or system can deny having performed an action, and the system lacks sufficient evidence to prove otherwise. Repudiation failures undermine accountability, forensic investigation, and compliance obligations. This agent targets External Entities (where users can deny actions they performed) and Processes (where services fail to produce tamper-evident audit trails of their operations).

## Detection Scope

### Targeted DFD Element Types

- **External Entity**: End users, API consumers, third-party integrations, administrative users, automated clients
- **Process**: Application services, payment processors, authorization services, data export services, administrative interfaces

### Patterns and Indicators

**Missing Audit Trails**
- Security-sensitive operations (login, logout, permission changes) not logged
- Financial transactions without immutable audit records
- Data deletion operations without pre-deletion snapshots or tombstone records
- Administrative actions (user creation, role assignment) missing from audit logs
- API calls that modify state without recording the authenticated caller identity

**Insufficient Log Detail**
- Logs missing actor identity (who performed the action)
- Logs missing timestamp with sufficient precision (sub-second for high-frequency systems)
- Logs missing source context (IP address, session ID, request correlation ID)
- Logs missing the before-and-after state for data modifications
- Generic log messages that cannot distinguish between different operation types

**Log Tampering Vulnerability**
- Application logs stored in locations writable by the application itself
- Missing log integrity protection (no append-only storage, no cryptographic chaining)
- Log rotation that deletes entries before compliance retention period expires
- Database audit tables modifiable through the same connection as application data
- Missing log forwarding to immutable external storage (SIEM, write-once bucket)

**Deniable Actions**
- Anonymous or unauthenticated operations that modify system state
- Shared credentials or service accounts where individual accountability is impossible
- Operations completed through side channels not covered by primary audit system
- Batch operations logged as a single entry without individual item attribution
- Missing non-repudiation controls on legally binding transactions (e-signatures, notarization)

**Timestamp Manipulation**
- System clocks not synchronized via NTP, enabling clock skew between services to create ambiguous event ordering
- Timestamps generated client-side or by untrusted sources without server-side validation
- Log timestamps using local time instead of UTC, creating ambiguity across time zones
- Missing monotonic or logical clocks for ordering events in distributed systems
- Timestamp precision insufficient to distinguish rapid sequential operations (coarse granularity enabling plausible deniability)

**Log Injection and Evasion**
- User-controlled data written to logs without sanitization (log injection)
- Log entries constructable by attackers to create false audit trails
- Missing correlation between distributed service logs (gaps in tracing)
- Log level configuration that suppresses security events in production

## Finding Template

Each finding produced by this agent conforms to `../../../schemas/finding.yaml` with the following field guidance:

| Field | Description | Example |
|-------|-------------|---------|
| `id` | Sequential identifier with R prefix | `R-1` |
| `category` | Always `repudiation` | `repudiation` |
| `component` | Name of the External Entity or Process under analysis | `LLM Agent Orchestrator` |
| `threat` | Specific repudiation threat description — what action is deniable and why the system cannot prove it occurred | `LLM Agent Orchestrator executes tool calls to MCP Tool Server without logging the originating user request, selected tool, parameters, or tool response — an operator can deny having triggered a destructive action and the system lacks evidence to attribute it` |
| `likelihood` | Assessed using OWASP factors: attacker motivation to deny actions, log coverage gaps, detection difficulty | `MEDIUM` |
| `impact` | Assessed using OWASP factors: accountability loss, compliance violations, financial dispute exposure, forensic investigation capability | `HIGH` |
| `risk_level` | Computed from OWASP 3x3 matrix (likelihood x impact) | `High` |
| `mitigation` | Actionable countermeasure — specific logging enhancement, integrity control, or non-repudiation mechanism | `Instrument the LLM Agent Orchestrator to emit structured audit events for every tool dispatch: record authenticated user ID, tool name, input parameters, response summary, and UTC timestamp; forward events to append-only SIEM within 60 seconds` |
| `references` | OWASP, CWE, MITRE ATT&CK, or CVE identifiers supporting the finding | `["CWE-778", "OWASP A09:2021", "ATT&CK T1070"]` |
| `dfd_element_type` | DFD classification of the target component | `External Entity` or `Process` |

### Risk Level Computation

Apply the OWASP 3x3 matrix to determine `risk_level` from `likelihood` and `impact`:

|  | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |
|---|---|---|---|
| **HIGH Impact** | Medium | High | Critical |
| **MEDIUM Impact** | Low | Medium | High |
| **LOW Impact** | Note | Low | Medium |

## References

- OWASP Top 10 2021 — A09: Security Logging and Monitoring Failures
- OWASP API Security Top 10 2023 — API9: Improper Inventory Management
- OWASP Logging Cheat Sheet
- OWASP Application Logging Vocabulary Cheat Sheet
- CWE-778: Insufficient Logging
- CWE-223: Omission of Security-Relevant Information
- CWE-117: Improper Output Neutralization for Logs
- CWE-779: Logging of Excessive Data
- MITRE ATT&CK T1070: Indicator Removal
- MITRE ATT&CK T1070.001: Clear Windows Event Logs
- MITRE ATT&CK T1562.006: Indicator Blocking
- NIST SP 800-92: Guide to Computer Security Log Management
- PCI DSS Requirement 10: Track and Monitor All Access to Network Resources and Cardholder Data
