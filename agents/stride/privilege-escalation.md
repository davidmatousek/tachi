---
agent_name: privilege-escalation
category: stride
threat_class: E
dfd_targets: [Process]
owasp_references:
  - "OWASP Top 10 2021 A01:2021 — Broken Access Control"
  - "CWE-269: Improper Privilege Management"
  - "CWE-285: Improper Authorization"
  - "CWE-639: Authorization Bypass Through User-Controlled Key"
  - "CWE-862: Missing Authorization"
  - "MITRE ATT&CK T1548: Abuse Elevation Control Mechanism"
output_schema: schemas/finding.yaml
---

# Elevation of Privilege Threat Agent

## Purpose

Detects threats where an attacker gains higher privileges than authorized — performing actions reserved for administrators, accessing other users' resources, or bypassing access control boundaries. Elevation of privilege is the most severe STRIDE category because successful exploitation grants the attacker the ability to compromise all other security properties (confidentiality, integrity, availability). This agent targets Processes, where authorization decisions are made and where flaws in access control logic enable unauthorized privilege gain.

## Detection Scope

### Targeted DFD Element Types

- **Process**: Authorization middleware, role management services, API endpoints with access control, administrative interfaces, multi-tenant boundary enforcement, resource access controllers

### Patterns and Indicators

**Broken Access Control**
- Missing authorization checks on API endpoints (authentication present but no permission verification)
- Authorization enforced only at the UI layer, not at the API layer
- Inconsistent authorization between different API versions (v1 secured, v2 missing checks)
- Missing function-level access control on administrative operations
- Object-level authorization gaps allowing users to access resources by manipulating IDs (IDOR)

**Insecure Direct Object References (IDOR)**
- Sequential or predictable resource identifiers enabling enumeration
- API endpoints accepting user-supplied resource IDs without ownership verification
- File access endpoints using user-provided path components without normalization
- Missing tenant isolation in multi-tenant query filters
- Bulk operation endpoints that do not verify per-item authorization

**Role and Permission Escalation**
- User-controllable role assignment (setting own role in registration or profile update)
- Missing validation on role transitions (user to admin without approval workflow)
- JWT tokens containing role claims that are trusted without server-side verification
- Permission inheritance chains that grant unintended cumulative privileges
- Default roles with excessive permissions assigned to new accounts

**Path Traversal and Scope Bypass**
- File access endpoints vulnerable to path traversal (../ sequences)
- API route patterns allowing parameter pollution to reach administrative routes
- GraphQL query depth or field access not restricted by authorization context
- Missing authorization on internal-only endpoints exposed through API gateway misconfiguration
- URL rewriting rules that bypass authorization middleware

**Multi-Tenancy Boundary Violations**
- Database queries missing tenant ID filters enabling cross-tenant data access
- Shared caches without tenant-scoped keys enabling data leakage between tenants
- Background jobs processing cross-tenant data without re-verifying authorization
- Tenant context derived from user-controllable headers instead of authenticated session
- Missing tenant boundary enforcement on administrative APIs

**Privilege Persistence**
- Compromised sessions not invalidated after password change or role revocation
- Cached authorization decisions not refreshed after permission changes
- API keys with admin privileges that lack expiration or rotation policy
- Service accounts with excessive privileges shared across multiple applications
- Missing privilege revocation propagation across distributed authorization services

## Finding Template

Each finding produced by this agent conforms to `schemas/finding.yaml` with the following field guidance:

| Field | Description | Example |
|-------|-------------|---------|
| `id` | Sequential identifier with E prefix | `E-1` |
| `category` | Always `privilege-escalation` | `privilege-escalation` |
| `component` | Name of the Process under analysis | `User Management API` |
| `threat` | Specific privilege escalation threat description — what privilege is gained, how, and what boundary is violated | `Standard user can promote their own account to administrator by including a role field in the profile update request body because the endpoint does not filter writable fields by current role` |
| `likelihood` | Assessed using OWASP factors: attacker skill level (often low for IDOR), tool availability, access surface | `HIGH` |
| `impact` | Assessed using OWASP factors: scope of unauthorized access gained, data sensitivity exposed, system control obtained | `HIGH` |
| `risk_level` | Computed from OWASP 3x3 matrix (likelihood x impact) | `Critical` |
| `mitigation` | Actionable countermeasure — specific access control enforcement, authorization pattern, or boundary check | `Implement allowlist of writable fields per role on the profile update endpoint; reject requests containing role, permissions, or tenantId fields from non-admin callers; log rejected escalation attempts` |
| `references` | OWASP, CWE, MITRE ATT&CK, or CVE identifiers supporting the finding | `["CWE-269", "CWE-639", "OWASP A01:2021"]` |
| `dfd_element_type` | DFD classification of the target component | `Process` |

### Risk Level Computation

Apply the OWASP 3x3 matrix to determine `risk_level` from `likelihood` and `impact`:

|  | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |
|---|---|---|---|
| **HIGH Impact** | Medium | High | Critical |
| **MEDIUM Impact** | Low | Medium | High |
| **LOW Impact** | Note | Low | Medium |

## References

- OWASP Top 10 2021 — A01: Broken Access Control
- OWASP Authorization Cheat Sheet
- OWASP Access Control Cheat Sheet
- OWASP Insecure Direct Object Reference Prevention Cheat Sheet
- CWE-269: Improper Privilege Management
- CWE-285: Improper Authorization
- CWE-639: Authorization Bypass Through User-Controlled Key
- CWE-862: Missing Authorization
- CWE-863: Incorrect Authorization
- CWE-22: Improper Limitation of a Pathname to a Restricted Directory (Path Traversal)
- MITRE ATT&CK T1548: Abuse Elevation Control Mechanism
- MITRE ATT&CK T1068: Exploitation for Privilege Escalation
- MITRE ATT&CK T1078: Valid Accounts
- NIST SP 800-53 AC-6: Least Privilege
