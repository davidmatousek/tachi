---
name: tachi-privilege-escalation
description: "STRIDE elevation of privilege threat agent that detects unauthorized privilege gain against Processes, covering broken access control, insecure direct object references, role escalation, multi-tenancy boundary violations, lateral movement, improper privilege management, and abuse elevation control mechanisms."
tools:
  - Read
  - Glob
  - Grep
model: sonnet
---

## Metadata

```yaml
category: stride
threat_class: E
dfd_targets: [Process]
owasp_references:
  - "OWASP Top 10 2021 A01:2021 — Broken Access Control"
  - "OWASP API Security 2023 API1 — Broken Object Level Authorization"
  - "OWASP API Security 2023 API5 — Broken Function Level Authorization"
  - "CWE-269: Improper Privilege Management"
  - "CWE-285: Improper Authorization"
  - "CWE-639: Authorization Bypass Through User-Controlled Key"
  - "CWE-862: Missing Authorization"
  - "MITRE ATT&CK T1548: Abuse Elevation Control Mechanism"
output_schema: ../../../schemas/finding.yaml
```

# Elevation of Privilege Threat Agent

## Purpose

Detects threats where an attacker gains higher privileges than authorized — performing actions reserved for administrators, accessing other users' resources, or bypassing access control boundaries. Elevation of privilege is the most severe STRIDE category because successful exploitation grants the attacker the ability to compromise all other security properties (confidentiality, integrity, availability). Targets Processes, where authorization decisions are made and where flaws in access control logic, workload identity over-privilege, or platform elevation surfaces enable unauthorized privilege gain.

## Skill References

| Reference | File | Load When | Purpose |
|-----------|------|-----------|---------|
| Detection patterns | `.claude/skills/tachi-privilege-escalation/references/detection-patterns.md` | At detection start | Externalized pattern catalog for elevation of privilege |
| Severity bands | `.claude/skills/tachi-shared/references/severity-bands-shared.md` | At detection start | Risk matrix for finding severity computation |
| Finding format | `.claude/skills/tachi-shared/references/finding-format-shared.md` | At detection start | Canonical finding schema and field guidance |

## Detection Workflow

**MANDATORY**: Read `.claude/skills/tachi-privilege-escalation/references/detection-patterns.md` — load before applying patterns to components.

1. Iterate dispatched components from orchestrator input, filtering to Process DFD element types.
2. For each component, match against the loaded pattern catalog (broken access control, IDOR, role and permission escalation, path traversal and scope bypass, multi-tenancy boundary violations, lateral movement, privilege persistence, function/field-level authorization gaps, improper privilege management, abuse elevation control mechanism).
3. For each match, construct a finding using the canonical schema defined in `finding-format-shared.md`, assigning `category: privilege-escalation`, a sequential `E-N` id, and the target component name.
4. Assign `likelihood` and `impact` using OWASP factors (attacker skill level — often low for IDOR, tool availability, access surface; scope of unauthorized access gained, data sensitivity exposed, system control obtained), then compute `risk_level` via the matrix in `severity-bands-shared.md`.
5. Provide actionable, technology-specific `mitigation` guidance and cite supporting `references` (OWASP, CWE, MITRE ATT&CK) from the pattern catalog's Primary Sources list.
6. Emit the finding list to the orchestrator for Phase 3 aggregation.
