# Enrichment Brief — privilege-escalation

**Agent type**: STRIDE
**Primary threat category**: Elevation of Privilege (Authorization)
**Created**: 2026-04-11
**Feature**: 082 — Threat Agent Skill References

## Candidate New Pattern Categories

### Category 1 — Broken Access Control (IDOR, Function-Level, Field-Level)

- **Source**: OWASP Top 10 2021
- **Source citation**: `https://owasp.org/Top10/A01_2021-Broken_Access_Control/`
- **Source item**: A01:2021 Broken Access Control (#1 ranked risk in 2021); cross-references CWE-639 Authorization Bypass Through User-Controlled Key (IDOR), CWE-862 Missing Authorization, CWE-863 Incorrect Authorization
- **Why this category**: Broken access control is the #1 OWASP risk but inline patterns treat IDOR and missing-authorization as secondary concerns. The category deserves explicit coverage given its ranking.
- **Proposed detection signal**:
  - API endpoint accepts resource identifiers (IDs, slugs, UUIDs) in URL path or query string without declared per-request authorization check
  - Administrative or high-privilege function reachable via guessable URL path (`/admin`, `/api/v1/users/:id/delete`) without declared RBAC/ABAC enforcement
  - GraphQL mutation or API endpoint returns fields without field-level authorization (returning admin-only fields to regular users)
  - REST endpoint uses PUT/PATCH/DELETE without ownership verification
- **False-positive risk**: Medium — most architectures assume authorization is enforced; pattern flags absence of explicit declaration
- **Taxonomy alignment**: STRIDE Elevation of Privilege; OWASP A01:2021, CWE-639, CWE-862 (rank 11 on CWE Top 25 2024), CWE-863

### Category 2 — Improper Privilege Management and Sudo/SetUID Abuse

- **Source**: CWE Top 25 Most Dangerous Software Weaknesses 2024
- **Source citation**: `https://cwe.mitre.org/data/definitions/269.html`
- **Source item**: CWE-269 Improper Privilege Management; related CWE-250 Execution with Unnecessary Privileges; related CWE-266 Incorrect Privilege Assignment
- **Why this category**: Service accounts and container workloads often run with excessive privileges; CWE-269 provides the authoritative pattern language missing from inline patterns.
- **Proposed detection signal**:
  - Container declared to run as root (UID 0) or without explicit non-root user
  - Service account has wildcard permissions (AWS `*:*`, Kubernetes `cluster-admin`, GCP `roles/owner`) on declared scope
  - Privilege-dropping step missing after privileged initialization (e.g., process binds privileged port then should drop to unprivileged user)
  - Long-lived privileged credentials (root DB account, admin API key) used for normal operations rather than scoped-down accounts
- **False-positive risk**: Low — least-privilege violations are concrete when observed in architecture
- **Taxonomy alignment**: STRIDE Elevation of Privilege; CWE-269, CWE-250

### Category 3 — Abuse Elevation Control Mechanism (Post-Auth Privilege Escalation)

- **Source**: MITRE ATT&CK v15+ (Enterprise)
- **Source citation**: `https://attack.mitre.org/techniques/T1548/`
- **Source item**: T1548 Abuse Elevation Control Mechanism (.001 Setuid and Setgid, .002 Bypass User Account Control, .003 Sudo and Sudo Caching, .005 Temporary Elevated Cloud Access); related T1068 Exploitation for Privilege Escalation
- **Why this category**: Post-authentication escalation via OS or cloud elevation mechanisms is not represented in inline patterns; this is the canonical ATT&CK technique family.
- **Proposed detection signal**:
  - DFD component declared to have `sudo` or setuid-binary access without constraint
  - Cloud-workload architecture uses temporary privilege elevation (AWS `sts:AssumeRole` with no MFA condition, GCP just-in-time access without justification audit)
  - Container with `CAP_SYS_ADMIN` or other dangerous Linux capabilities
  - Kubernetes pod with `privileged: true` or host-path mounts
- **False-positive risk**: Low — explicit privileged capabilities are a concrete signal
- **Taxonomy alignment**: STRIDE Elevation of Privilege; ATT&CK TA0004 Privilege Escalation tactic

## Source Verification Notes

- OWASP A01 is the #1 risk in 2021 — pattern coverage should be comprehensive; this brief proposes three sub-patterns but Phase 3.2 may split further.
- CWE-862 Missing Authorization is at rank 11 on CWE Top 25 2024 — verify rank during Phase 3.2 extraction.
- ATT&CK T1548 has multiple sub-techniques; cite sub-technique when detection focus is narrow, parent technique when broad.
- Information-disclosure agent also cites OWASP A01 obliquely; this agent owns A01 directly — coordinate to avoid double-counting in orchestrator dispatch.
- Checked but NOT used: NIST SP 800-53 AC-family (Access Control) — controls reference, not detection source per approved set.
