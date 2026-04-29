---
name: tachi-repudiation
description: "STRIDE repudiation threat agent that detects accountability failures against External Entities and Processes, covering missing audit trails, insufficient log detail, log tampering vulnerabilities, and timestamp manipulation."
tools:
  - Read
  - Glob
  - Grep
model: sonnet
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
  - "OWASP M8:2024 — Security Misconfiguration"
output_schema: ../../../schemas/finding.yaml
```

# Repudiation Threat Agent

## Purpose

Detects threats where a user or system can deny having performed an action and the system lacks sufficient evidence to prove otherwise, undermining accountability, forensic investigation, and compliance obligations. Targets External Entities (where users can deny actions they performed) and Processes (where services fail to produce tamper-evident audit trails of their operations).

Extended for mobile-platform topologies, this agent additionally covers mobile-misconfiguration enabling accountability loss (missing audit logging on auth state transitions / biometric prompts / sensitive transactions, disabled crash reporting in production [Crashlytics / Sentry off or scrubbed too aggressively], debug logs leaking sensitive data via `Log.d` / `NSLog` in release builds, missing tamper-evident timestamping on transaction logs, audit log writers with no integrity protection) when the architecture exhibits mobile-platform topology indicators.

## Skill References

| Reference | File | Load When | Purpose |
|-----------|------|-----------|---------|
| Detection patterns | `.claude/skills/tachi-repudiation/references/detection-patterns.md` | At detection start | Externalized pattern catalog for repudiation |
| Severity bands | `.claude/skills/tachi-shared/references/severity-bands-shared.md` | At detection start | Risk matrix for finding severity computation |
| Finding format | `.claude/skills/tachi-shared/references/finding-format-shared.md` | At detection start | Canonical finding schema and field guidance |

## Detection Workflow

**MANDATORY**: Read `.claude/skills/tachi-repudiation/references/detection-patterns.md` — load before applying patterns to components.

1. Iterate dispatched components from orchestrator input, filtering to External Entity and Process DFD element types.
2. For each component, match against the loaded pattern catalog (missing audit trails, insufficient log detail, log tampering vulnerability, deniable actions, timestamp manipulation, log injection and evasion, security logging and monitoring coverage gaps, indicator removal and timestomping).
3. For each match, construct a finding using the canonical schema defined in `finding-format-shared.md`, assigning `category: repudiation`, a sequential `R-N` id, and the target component name.
4. Assign `likelihood` and `impact` using OWASP factors (attacker motivation to deny actions, log coverage gaps, detection difficulty; accountability loss, compliance violations, financial dispute exposure, forensic investigation capability), then compute `risk_level` via the matrix in `severity-bands-shared.md`.
5. Provide actionable, technology-specific `mitigation` guidance and cite supporting `references` (OWASP, CWE, MITRE ATT&CK, OWASP M8:2024, MASTG-CODE, MASVS-CODE) from the pattern catalog's Primary Sources list.
6. Emit the finding list to the orchestrator for Phase 3 aggregation.
