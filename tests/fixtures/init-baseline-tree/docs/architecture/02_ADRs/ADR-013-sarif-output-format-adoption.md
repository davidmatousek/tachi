# ADR-013: SARIF 2.1.0 Output Format Adoption

**Status**: Accepted
**Date**: 2026-03-22
**Deciders**: Architect
**Feature**: 012 (SARIF Output Generation)

---

## Context

Tachi produces threat model findings as a human-readable markdown document (`threats.md`). Security teams need to integrate these findings into automated security pipelines -- GitHub Code Scanning, Azure DevOps, VS Code SARIF Viewer, and other SAST aggregation dashboards. Without a machine-readable output format, tachi findings exist in isolation from the broader security toolchain.

Key constraints:
- The output format must be a recognized industry standard consumed by major security platforms.
- Findings must retain their full semantic context: threat category, component targeting, severity, mitigation, and cross-agent correlations.
- Finding identity must be stable across runs so that security dashboards track persistent alerts rather than creating duplicates on each execution.
- The format must support tachi's unique features: 8 threat categories (6 STRIDE + 2 AI), dual physical/logical locations, and correlation groups from Feature 010.
- No runtime dependencies -- the orchestrator prompt must produce the output directly without external tooling.

---

## Decision

We will adopt **SARIF 2.1.0** (Static Analysis Results Interchange Format) as the machine-readable output format, producing `threats.sarif` alongside `threats.md` during Phase 4 of the orchestrator workflow. SARIF 2.1.0 is the OASIS open standard (approved 2020) for expressing static analysis results.

**Key design choices**:

1. **Co-generation**: Both outputs are produced from the same finding IR data in a single Phase 4 pass. No separate export step or conversion tool.

2. **8 rule IDs**: One `reportingDescriptor` per threat category (`tachi/stride/*` for 6 STRIDE categories, `tachi/ai/*` for 2 AI categories). Only rules with findings in the current run are included.

3. **CVSS-aligned severity**: Risk levels map to SARIF levels and `security-severity` numeric strings for GitHub Code Scanning display: Critical=error/9.0, High=error/8.0, Medium=warning/5.0, Low=note/2.0, Note=note/0.1.

4. **Deterministic fingerprints**: `partialFingerprints.primaryLocationLineHash` uses SHA-256(ruleId + component_name) truncated to 16 hex characters. Same input produces identical fingerprints across runs.

5. **Correlation via relatedLocations**: Feature 010 correlation groups are represented using SARIF's native `relatedLocations[]` array and `partialFingerprints.correlationGroup`, avoiding custom extensions.

6. **Dual-location strategy**: Every result includes `physicalLocation` (required by GitHub Code Scanning) pointing to the architecture input file with `startLine: 1`, plus `logicalLocations[]` with component name, trust zone path, and DFD element type for semantic navigation.

---

## Rationale

**Reasons**:
1. **Industry standard**: SARIF 2.1.0 is an OASIS-approved standard consumed by GitHub Code Scanning, Azure DevOps, VS Code SARIF Viewer, and other security tools. No proprietary format achieves comparable reach.
2. **Native GitHub integration**: GitHub's `codeql/upload-sarif@v3` action accepts SARIF directly. Findings appear as security alerts with severity, rule descriptions, and fingerprint-based deduplication -- no custom integration needed.
3. **Semantic richness**: SARIF's `reportingDescriptor` (rules), `logicalLocations`, `relatedLocations`, and `partialFingerprints` objects map cleanly to tachi's finding IR without lossy compression or custom extensions.
4. **Stable tracking**: The `partialFingerprints` mechanism provides deterministic finding identity. GitHub uses these to track alerts across runs, preventing duplicate alert noise on re-analysis.
5. **Zero runtime dependencies**: SARIF is JSON. The orchestrator prompt generates it directly alongside `threats.md` with no external tooling, libraries, or runtime requirements.
6. **Forward compatibility**: SARIF 2.1.0 is the current stable version. Draft 2.2 is backward-compatible. Adopting 2.1.0 provides a stable foundation that will not require migration.

---

## Alternatives Considered

### Alternative 1: Custom JSON Format

Define a tachi-specific JSON schema for machine-readable output.

**Pros**:
- Full control over structure and semantics
- Could mirror the finding IR schema exactly

**Cons**:
- No ecosystem support -- consumers would need custom parsers
- No GitHub Code Scanning integration without a SARIF conversion layer
- Maintenance burden of a proprietary format specification

**Why Not Chosen**: The primary integration target (GitHub Code Scanning) requires SARIF. A custom format would need a SARIF converter anyway, doubling the work with no additional value.

### Alternative 2: SARIF 2.0

Use the older SARIF 2.0 specification.

**Pros**:
- Slightly simpler schema
- Broader legacy tool support

**Cons**:
- Missing `partialFingerprints` (added in 2.1.0) -- no stable finding tracking
- Missing `logicalLocations` enhancements needed for component navigation
- GitHub Code Scanning targets 2.1.0 specifically

**Why Not Chosen**: SARIF 2.1.0 provides critical features (`partialFingerprints`, enhanced `logicalLocations`) that 2.0 lacks. GitHub recommends 2.1.0 for Code Scanning uploads.

### Alternative 3: CycloneDX SBOM with Vulnerabilities

Encode findings as vulnerability entries in a CycloneDX SBOM document.

**Pros**:
- Growing adoption in supply chain security
- Rich vulnerability metadata support

**Cons**:
- Designed for software composition analysis, not static/threat analysis
- No native GitHub Code Scanning integration
- Semantic mismatch: SBOM vulnerabilities describe known CVEs in dependencies, not architecture-level threat findings

**Why Not Chosen**: CycloneDX solves a different problem (dependency vulnerabilities). Tachi produces architecture-level threat findings that map naturally to SARIF's static analysis model.

---

## Consequences

### Positive
- Tachi findings integrate into GitHub Code Scanning with zero custom tooling
- Deterministic fingerprints enable persistent alert tracking across architecture revisions
- Feature 010 correlation groups are preserved in SARIF via native `relatedLocations`
- SARIF viewers (VS Code, Azure DevOps) provide component-level navigation via `logicalLocations`
- Output schema (`schemas/output.yaml`) includes SARIF severity mapping as a formal reference

### Negative
- SARIF JSON is verbose compared to the finding IR -- a 20-finding model produces a larger SARIF file than the equivalent markdown
- `physicalLocation` requires a synthetic `startLine: 1` since tachi analyzes architecture descriptions, not source code -- some SARIF viewers may display this awkwardly
- JSON structural self-check adds orchestrator prompt length (~50 lines of validation instructions)

### Mitigation
- File size is negligible for typical threat models (<100 findings)
- `logicalLocations` provide meaningful navigation context even when `physicalLocation` is synthetic
- Self-check prevents malformed JSON that would fail GitHub upload, catching errors before output

---

## Related Decisions

- ADR-003: STRIDE-per-Element Dispatch (produces the findings that SARIF maps)
- ADR-012: Cross-Agent Correlation Detection (correlation groups represented via `relatedLocations`)

---

## References

- SARIF 2.1.0 OASIS Standard: https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html
- GitHub Code Scanning SARIF support: https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning
- Feature 012 spec: `specs/012-sarif-output-generation/spec.md`
- Feature 012 plan: `specs/012-sarif-output-generation/plan.md`
- SARIF reference template: `templates/tachi/output-schemas/threats.sarif`
- Output schema (severity mapping): `schemas/output.yaml`
