# Schema Validation Results (T042-T046)

**Validator**: tester (BDD)
**Date**: 2026-03-23
**Branch**: 024-example-threat-models
**Status**: FAIL (1 issue)

---

## Summary Table

| Check | web-app | agentic-app | microservices | Status |
|-------|---------|-------------|---------------|--------|
| T042: Mermaid diagrams | PASS | PASS | PASS | PASS |
| T043: YAML frontmatter | PASS | PASS | PASS | PASS |
| T044: Section order | PASS | PASS | PASS | PASS |
| T045: STRIDE-per-Element | PASS | FAIL (1 issue) | PASS | FAIL |
| T046: OWASP 3x3 risk levels | PASS | PASS | PASS | PASS |

**Overall**: 4 of 5 checks pass. 1 issue found.

---

## T042: Mermaid Diagram Validation

All three architecture.md files contain valid `flowchart TD` declarations, balanced subgraph blocks, and well-formed arrow syntax with no dangling references.

| File | flowchart TD | Subgraphs | Arrows | Nodes | Result |
|------|-------------|-----------|--------|-------|--------|
| web-app/architecture.md | Yes | 3 (balanced) | 10 | 6 | PASS |
| agentic-app/architecture.md | Yes | 3 (balanced) | 13 | 7 | PASS |
| microservices/architecture.md | Yes | 4 (balanced) | 15 | 10 | PASS |

---

## T043: YAML Frontmatter Validation

All three threats.md files begin with raw YAML frontmatter containing all 4 required fields with correct values.

| File | schema_version | date | input_format | classification | Result |
|------|---------------|------|-------------|----------------|--------|
| web-app/threats.md | "1.1" | "2026-03-23" | "mermaid" | "confidential" | PASS |
| agentic-app/threats.md | "1.1" | "2026-03-23" | "mermaid" | "confidential" | PASS |
| microservices/threats.md | "1.1" | "2026-03-23" | "mermaid" | "confidential" | PASS |

---

## T044: Section Order Validation

All three threats.md files contain all 8 required top-level sections in correct order, plus all 6 STRIDE subsections (3.1-3.6), both AI subsections (4.1-4.2), and the Appendix (OWASP Cross-References).

| File | H2 Sections (8) | STRIDE Subs (6) | AI Subs (2) | Appendix | Result |
|------|-----------------|-----------------|-------------|----------|--------|
| web-app/threats.md | 8/8 correct | 6/6 correct | 2/2 correct | Present | PASS |
| agentic-app/threats.md | 8/8 correct | 6/6 correct | 2/2 correct | Present | PASS |
| microservices/threats.md | 8/8 correct | 6/6 correct | 2/2 correct | Present | PASS |

---

## T045: STRIDE-per-Element Coverage Matrix Validation

STRIDE-per-Element dispatch rules applied:

| DFD Element Type | S | T | R | I | D | E |
|---|---|---|---|---|---|---|
| External Entity | Yes | n/a | Yes | n/a | n/a | n/a |
| Process | Yes | Yes | Yes | Yes | Yes | Yes |
| Data Store | n/a | Yes | n/a | Yes | Yes | n/a |

### web-app: PASS

All 6 components comply. External Entity (Web Client) has correct n/a for T, I, D, E. Processes (Static CDN, API Gateway, Auth Service) have no n/a in STRIDE columns. Data Stores (Session Store, User Database) have correct n/a for S, R, E.

### agentic-app: FAIL (1 issue)

**Issue**: Audit Logger is classified as "Data Store" in architecture.md. Per STRIDE-per-Element rules, Data Stores receive T, I, D analysis only (S, R, E are n/a). However, the coverage matrix shows R=1 for Audit Logger, and finding R-3 is assigned to the Audit Logger component in STRIDE table 3.3.

- **Finding**: R-3 (Audit Logger) - "Attacker deletes or corrupts audit log entries to enable repudiation of prior actions, exploiting insufficient log immutability controls"
- **Expected**: R column = `n/a` for Audit Logger (Data Store)
- **Actual**: R column = `1` (finding R-3 assigned)
- **Root cause**: The Repudiation category was dispatched to a Data Store component, violating STRIDE-per-Element dispatch rules

### microservices: PASS

All 10 components comply. External Entities (Client Application, External Payment Provider) have correct n/a for T, I, D, E. Processes (API Gateway, Service Registry, Order Service, Payment Service, Notification Service) have no n/a in STRIDE columns. Data Stores (Message Queue, Order Database, Inventory Database) have correct n/a for S, R, E.

### Em Dash Verification

All three files use the correct em dash character (U+2014) for analyzed-but-clean cells. No ASCII hyphens found in coverage matrix cells.

| File | Em dashes | ASCII hyphens | Result |
|------|-----------|---------------|--------|
| web-app | 10 | 0 | PASS |
| agentic-app | 15 | 0 | PASS |
| microservices | 21 | 0 | PASS |

---

## T046: OWASP 3x3 Risk Level Validation

Every finding in all three files was checked against the OWASP 3x3 risk matrix:

| | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |
|---|---|---|---|
| **HIGH Impact** | Medium | High | Critical |
| **MEDIUM Impact** | Low | Medium | High |
| **LOW Impact** | Note | Low | Medium |

| File | Findings checked | Mismatches | Result |
|------|-----------------|------------|--------|
| web-app/threats.md | 16 (STRIDE only) | 0 | PASS |
| agentic-app/threats.md | 23 (16 STRIDE + 7 AI) | 0 | PASS |
| microservices/threats.md | 23 (STRIDE only) | 0 | PASS |

All 62 findings across all three files compute risk levels correctly per the OWASP 3x3 matrix.

---

## Issue Register

| # | Check | File | Severity | Description |
|---|-------|------|----------|-------------|
| 1 | T045 | agentic-app/threats.md | Medium | Audit Logger (Data Store) has R-3 finding and R=1 in coverage matrix. Per STRIDE-per-Element rules, Repudiation does not apply to Data Stores (should be n/a). |

### Remediation Guidance

For issue 1, two approaches:

1. **Remove R-3 from Audit Logger**: Delete the R-3 finding from STRIDE table 3.3 and update the coverage matrix to show R=n/a for Audit Logger. Update Risk Summary counts and Recommended Actions table accordingly.

2. **Reclassify Audit Logger**: If the architecture intends the Audit Logger to receive Repudiation analysis (arguing it has process-like behavior for log integrity), reclassify it as a Process in architecture.md. This would require adding S, E analysis for the Audit Logger and removing n/a from those coverage matrix columns.

Option 1 is recommended as it preserves the architecture.md classification and enforces STRIDE-per-Element consistency.
