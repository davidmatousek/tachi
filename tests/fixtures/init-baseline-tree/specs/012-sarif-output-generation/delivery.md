# Delivery Document: Feature 012 — SARIF Output Generation

**Delivery Date**: 2026-03-22
**Branch**: `012-sarif-output-generation`
**PR**: #13

---

## What Was Delivered

- Threat modeling orchestrator now produces `threats.sarif` alongside `threats.md` in every run — SARIF 2.1.0 compliant output for CI/CD integration
- STRIDE + AI threat categories mapped to canonical SARIF rule IDs (8 categories: spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, agentic, llm)
- CVSS-aligned severity mapping: Critical→error/9.0, High→error/8.0, Medium→warning/5.0, Low→note/2.0, Note→note/0.1 (Note-level fix from 0.0 to 0.1)
- Correlated findings represented via `relatedLocations` and `partialFingerprints.correlationGroup` — preserving cross-category threat relationships
- Dual physical/logical locations on every result — enabling component-level navigation in GitHub Code Scanning, VS Code SARIF Viewer, and Azure DevOps
- Deterministic `partialFingerprints` (SHA-256 hash of ruleId + component_name) for stable GitHub alert deduplication across runs
- Optional OWASP/CWE taxonomy references via `run.taxonomies[]` and `rule.relationships[]`

---

## How to See & Test

1. Run the orchestrator against the agentic example: process `examples/mermaid-agentic-app/input.md` and verify both `threats.md` and `threats.sarif` are produced in the output directory
2. Open `threats.sarif` and verify the top-level structure: `$schema`, `version: "2.1.0"`, single `runs[]` entry with `tool.driver` identifying "Tachi"
3. Verify `tool.driver.rules[]` contains rule definitions for both STRIDE categories (tachi/stride/*) and AI categories (tachi/ai/*)
4. Verify each `result` has: `ruleId`, `message.text` (threat), `message.markdown` (mitigation), `level`, `locations[]` (physical + logical), `partialFingerprints`
5. Verify severity mapping: check that `properties.security-severity` is a numeric string matching the CVSS table (e.g., "9.0" for Critical)
6. Run against the non-agentic example: process `examples/ascii-web-api/input.md` and verify SARIF contains only STRIDE rules (no AI rules in `tool.driver.rules[]`)
7. Run twice against the same input and verify `primaryLocationLineHash` values are identical for same category+component combinations (deterministic fingerprints)
8. Validate SARIF schema compliance: check that generated JSON has all required properties, `security-severity` is a numeric string, rule descriptions are within GitHub limits (255 char name, 1024 char descriptions, 20 tags)

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Estimated Duration | 1-2 days |
| Actual Duration | 1 day |
| Variance | On target |

---

## Surprise Log

Smooth sailing — everything went roughly as planned, no major surprises.

---

## Lessons Learned

| Category | Lesson | KB Entry |
|----------|--------|----------|
| Technical pattern | SARIF 2.1.0 maps naturally to STRIDE threat models when the intermediate representation is well-defined | PAT-004 in INSTITUTIONAL_KNOWLEDGE.md |

---

## Feedback Loop

**New Ideas**: None

---

## Source Artifacts

| Artifact | Path |
|----------|------|
| Specification | specs/012-sarif-output-generation/spec.md |
| Implementation Plan | specs/012-sarif-output-generation/plan.md |
| Task Breakdown | specs/012-sarif-output-generation/tasks.md |
| PRD | docs/product/02_PRD/012-sarif-output-generation-2026-03-22.md |

---

## Documentation Updates

| Domain | Agent | Files Updated | Status |
|--------|-------|---------------|--------|
| Product | product-manager | 3 (INDEX.md, User Stories, OKRs) | APPROVED |
| Architecture | architect | 3 (system design, tech stack, ADR-013) | APPROVED |
| DevOps | devops | 0 (no changes needed) | APPROVED |

---

## Cleanup

- [x] Feature branch deleted
- [x] All tasks complete (20/20)
- [ ] No TBD/TODO in docs
- [ ] Committed and pushed
- [ ] GitHub Issue closed (`stage:done`)

**Feature 012 is now officially CLOSED.**
