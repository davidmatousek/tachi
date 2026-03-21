---
agent_name: info-disclosure
category: stride
threat_class: I
dfd_targets: [Process, Data Store, Data Flow]
owasp_references:
  - "OWASP Top 10 2021 A01:2021 — Broken Access Control"
  - "OWASP Top 10 2021 A02:2021 — Cryptographic Failures"
  - "CWE-200: Exposure of Sensitive Information to an Unauthorized Actor"
  - "CWE-209: Generation of Error Message Containing Sensitive Information"
  - "CWE-532: Insertion of Sensitive Information into Log File"
  - "MITRE ATT&CK T1005: Data from Local System"
output_schema: schemas/finding.yaml
---

# Information Disclosure Threat Agent

## Purpose

Detects threats where sensitive information is exposed to unauthorized parties — whether through direct data leaks, verbose error messages, side-channel observations, or insufficient access controls on stored data. Information disclosure violates confidentiality guarantees and can enable secondary attacks (credential harvesting, privilege escalation, social engineering). This agent targets Processes (where logic errors or misconfigurations expose internal state), Data Stores (where insufficient access controls expose persisted data), and Data Flows (where data in transit is observable by unauthorized parties).

## Detection Scope

### Targeted DFD Element Types

- **Process**: API endpoints, error handlers, search services, reporting engines, debug interfaces, health check endpoints
- **Data Store**: Databases, file storage, caches, session stores, backup systems, log aggregators
- **Data Flow**: API responses, inter-service messages, file transfers, email notifications, webhook payloads

### Patterns and Indicators

**Error Message Exposure**
- Stack traces returned in API error responses (production environments)
- Database error messages revealing table names, column names, or query structure
- Framework version information in error pages or server headers
- File path disclosure in error messages exposing server directory structure
- Detailed validation errors revealing business rule internals

**Excessive Data in Responses**
- API responses returning full database records when only specific fields are needed
- User profile endpoints exposing internal IDs, email addresses, or phone numbers to unauthorized callers
- List endpoints returning records the requesting user should not have access to
- Search results including data from access-restricted records
- Pagination metadata revealing total record counts that should be confidential

**Data at Rest Exposure**
- Sensitive data stored unencrypted (PII, financial data, credentials)
- Database backups accessible without authentication
- Log files containing sensitive request/response bodies
- Cache stores holding sensitive data without TTL or access controls
- Temporary files containing sensitive data not cleaned up after processing

**Data in Transit Exposure**
- Sensitive fields transmitted over unencrypted connections (HTTP, unencrypted SMTP)
- API keys or tokens included in URL query parameters (visible in logs and browser history)
- Sensitive data in HTTP headers observable by intermediary proxies
- Webhook payloads containing sensitive data sent to unverified endpoints
- Inter-service communication without encryption within cloud VPCs

**Side-Channel Information Leakage**
- Timing differences revealing whether a user account exists (login enumeration)
- Response size differences indicating presence or absence of data
- HTTP status code variations enabling resource enumeration (200 vs 404 patterns)
- Rate limiting responses revealing valid vs invalid input patterns
- DNS query patterns leaking internal service topology

**Debug and Diagnostic Exposure**
- Debug endpoints enabled in production (/debug, /metrics, /env, /health with internals)
- Source maps or development artifacts deployed to production
- API documentation endpoints exposing internal-only routes
- Profiling or monitoring data accessible without authentication
- Version control metadata (.git directory) accessible via web server

## Finding Template

Each finding produced by this agent conforms to `schemas/finding.yaml` with the following field guidance:

| Field | Description | Example |
|-------|-------------|---------|
| `id` | Sequential identifier with I prefix | `I-1` |
| `category` | Always `info-disclosure` | `info-disclosure` |
| `component` | Name of the Process, Data Store, or Data Flow under analysis | `User Profile API` |
| `threat` | Specific information disclosure threat description — what data is exposed, to whom, and through what mechanism | `API error responses include full stack traces in production, exposing internal class names, database connection strings, and framework version to unauthenticated callers` |
| `likelihood` | Assessed using OWASP factors: ease of discovery, ease of exploit, attacker awareness, intrusion detection capability | `HIGH` |
| `impact` | Assessed using OWASP factors: confidentiality loss scope, data sensitivity classification, secondary attack enablement | `MEDIUM` |
| `risk_level` | Computed from OWASP 3x3 matrix (likelihood x impact) | `High` |
| `mitigation` | Actionable countermeasure — specific configuration, filtering, or encryption mechanism | `Configure production error handler to return generic error codes with correlation IDs; log full stack traces server-side only; strip Server and X-Powered-By headers` |
| `references` | OWASP, CWE, MITRE ATT&CK, or CVE identifiers supporting the finding | `["CWE-209", "OWASP A02:2021"]` |
| `dfd_element_type` | DFD classification of the target component | `Process`, `Data Store`, or `Data Flow` |

### Risk Level Computation

Apply the OWASP 3x3 matrix to determine `risk_level` from `likelihood` and `impact`:

|  | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |
|---|---|---|---|
| **HIGH Impact** | Medium | High | Critical |
| **MEDIUM Impact** | Low | Medium | High |
| **LOW Impact** | Note | Low | Medium |

## References

- OWASP Top 10 2021 — A01: Broken Access Control
- OWASP Top 10 2021 — A02: Cryptographic Failures
- OWASP Error Handling Cheat Sheet
- OWASP Information Disclosure Prevention Cheat Sheet
- CWE-200: Exposure of Sensitive Information to an Unauthorized Actor
- CWE-209: Generation of Error Message Containing Sensitive Information
- CWE-215: Insertion of Sensitive Information Into Debugging Code
- CWE-532: Insertion of Sensitive Information into Log File
- CWE-538: Insertion of Sensitive Information into Externally-Accessible File or Directory
- MITRE ATT&CK T1005: Data from Local System
- MITRE ATT&CK T1039: Data from Network Shared Drive
- MITRE ATT&CK T1530: Data from Cloud Storage
- NIST SP 800-122: Guide to Protecting the Confidentiality of Personally Identifiable Information (PII)
