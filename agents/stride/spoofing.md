---
agent_name: spoofing
category: stride
threat_class: S
dfd_targets: [External Entity, Process]
owasp_references:
  - "OWASP Top 10 2021 A07:2021 — Identification and Authentication Failures"
  - "CWE-287: Improper Authentication"
  - "CWE-290: Authentication Bypass by Spoofing"
  - "CWE-384: Session Fixation"
  - "MITRE ATT&CK T1078: Valid Accounts"
  - "MITRE ATT&CK T1556: Modify Authentication Process"
output_schema: schemas/finding.yaml
---

# Spoofing Threat Agent

## Purpose

Detects threats where an attacker assumes the identity of another entity — user, service, or system component. Spoofing undermines authentication guarantees, enabling an adversary to perform actions under a trusted identity. This agent targets External Entities (where attackers impersonate legitimate users or upstream systems) and Processes (where attackers forge inter-service identity to bypass trust assumptions).

## Detection Scope

### Targeted DFD Element Types

- **External Entity**: Users, API clients, upstream services, third-party integrations, federated identity providers
- **Process**: Backend services, microservices, API gateways, authentication middleware, token issuers

### Patterns and Indicators

**Authentication Bypass**
- Missing or weak authentication on entry points (no MFA, password-only)
- Default or hard-coded credentials in service accounts
- Authentication decisions made client-side without server validation
- Missing mutual TLS between services in zero-trust boundaries

**Credential Theft and Replay**
- Tokens transmitted over unencrypted channels (HTTP instead of HTTPS)
- Long-lived tokens without rotation or revocation mechanisms
- Credentials stored in plaintext or weakly hashed (MD5, SHA-1 without salt)
- Bearer tokens without audience or issuer validation

**Session Hijacking**
- Session identifiers predictable or sequentially generated
- Session tokens exposed in URLs, logs, or error messages
- Missing session binding to client fingerprint (IP, user-agent)
- No session invalidation on privilege changes (login, role change)

**Service Impersonation**
- Missing service-to-service authentication in internal networks
- DNS spoofing enabling traffic redirection to attacker-controlled endpoints
- Unsigned or unverified webhooks and callbacks from external services
- Missing certificate pinning for critical upstream dependencies

**Federated Identity Attacks**
- OAuth/OIDC misconfiguration (missing state parameter, open redirects)
- SAML assertion replay or signature bypass
- JWT signature algorithm confusion (accepting "none" or HS256 when RS256 expected)
- Missing issuer validation on identity tokens from external providers

## Finding Template

Each finding produced by this agent conforms to `schemas/finding.yaml` with the following field guidance:

| Field | Description | Example |
|-------|-------------|---------|
| `id` | Sequential identifier with S prefix | `S-1` |
| `category` | Always `spoofing` | `spoofing` |
| `component` | Name of the External Entity or Process under analysis | `OAuth Login Service` |
| `threat` | Specific spoofing threat description — what the attacker does and what trust assumption they violate | `Attacker replays expired JWT tokens to the API Gateway because token revocation checks are not performed on each request` |
| `likelihood` | Assessed using OWASP factors: attacker skill level, availability of tools, opportunity window, detection difficulty | `HIGH` |
| `impact` | Assessed using OWASP factors: loss of confidentiality, integrity, accountability; financial and reputation damage | `HIGH` |
| `risk_level` | Computed from OWASP 3x3 matrix (likelihood x impact) | `Critical` |
| `mitigation` | Actionable countermeasure — specific technology or configuration, not generic advice | `Implement JWT validation with RS256 signature verification, audience claim checks, and token revocation via a deny-list checked on every request` |
| `references` | OWASP, CWE, MITRE ATT&CK, or CVE identifiers supporting the finding | `["CWE-287", "OWASP A07:2021"]` |
| `dfd_element_type` | DFD classification of the target component | `External Entity` or `Process` |

### Risk Level Computation

Apply the OWASP 3x3 matrix to determine `risk_level` from `likelihood` and `impact`:

|  | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |
|---|---|---|---|
| **HIGH Impact** | Medium | High | Critical |
| **MEDIUM Impact** | Low | Medium | High |
| **LOW Impact** | Note | Low | Medium |

## References

- OWASP Top 10 2021 — A07: Identification and Authentication Failures
- OWASP Authentication Cheat Sheet
- OWASP Session Management Cheat Sheet
- CWE-287: Improper Authentication
- CWE-290: Authentication Bypass by Spoofing
- CWE-384: Session Fixation
- CWE-613: Insufficient Session Expiration
- MITRE ATT&CK T1078: Valid Accounts
- MITRE ATT&CK T1556: Modify Authentication Process
- MITRE ATT&CK T1550: Use Alternate Authentication Material
- NIST SP 800-63B: Digital Identity Guidelines — Authentication and Lifecycle Management
