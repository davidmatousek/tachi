# SARIF Supersession Chain Validation

**Task**: T019
**Date**: 2026-03-28
**Scope**: Verify `threats.sarif` -> `risk-scores.sarif` -> `compensating-controls.sarif` chain integrity

---

## 1. Fingerprint Continuity

### 1a. threats.sarif -> risk-scores.sarif findingId/v1 Preservation

**PASS** -- All 34 findingId/v1 values in `threats.sarif` are preserved identically in `risk-scores.sarif`. No additions, no removals, no modifications.

| threats.sarif Count | risk-scores.sarif Count | Sets Match |
|---------------------|-------------------------|------------|
| 34                  | 34                      | Yes        |

### 1b. compensating-controls.sarif Template Documents Fingerprint Preservation

**PASS** -- The template at `templates/compensating-controls.sarif` explicitly documents fingerprint preservation in three ways:

1. **Top-level `_comment`** (line 2): States "Fingerprints (findingId/v1) are preserved unchanged through all three files for GitHub Code Scanning alert continuity."
2. **Top-level `_supersession_chain`** (line 3): States "partialFingerprints are preserved" to enable supersession without duplicates.
3. **Example results** (lines 328-331, 396-399, 443-446, 500-503, 578-582): All five example results include `partialFingerprints` with `findingId/v1` and `primaryLocationLineHash` marked as `"<preserved-from-source-risk-scores-sarif>"`.

### 1c. Agent File Documents Fingerprint Preservation

**PASS** -- The control-analyzer agent (`/.claude/agents/tachi/control-analyzer.md`) enforces fingerprint preservation at multiple points:

1. **Phase 1 parsing** (line 180): "When parsing from SARIF, capture ALL `partialFingerprints` fields -- these MUST be preserved unchanged in the output `compensating-controls.sarif`"
2. **Phase 6c `partialFingerprints`** (lines 1267-1272): Explicit requirement that `findingId/v1` "MUST match the upstream `risk-scores.sarif` fingerprint exactly" and that "The `partialFingerprints` object for each result MUST be identical to the corresponding result in `risk-scores.sarif`. Do not recompute, modify, or add fingerprint fields."

---

## 2. Tool Driver Chain

| File | Expected | Actual | Status |
|------|----------|--------|--------|
| `threats.sarif` | `"tachi"` | `"Tachi"` | **FAIL** -- Capitalized |
| `risk-scores.sarif` | `"tachi-risk-scorer"` | `"tachi-risk-scorer"` | **PASS** |
| `compensating-controls.sarif` template | `"tachi-control-analyzer"` | `"tachi-control-analyzer"` | **PASS** |

### Issue: threats.sarif tool.driver.name Casing

The `threats.sarif` sample file uses `"Tachi"` (PascalCase) instead of `"tachi"` (lowercase). The downstream files use lowercase-kebab convention (`tachi-risk-scorer`, `tachi-control-analyzer`). This casing inconsistency does not break the supersession chain (GitHub Code Scanning uses `partialFingerprints` for alert identity, not tool names), but it is a cosmetic inconsistency in the chain. The threat-modeler agent or its template is the owner of this value, not feature 036.

**Impact**: Cosmetic only. Does not affect supersession behavior. Out of scope for feature 036 -- the `threats.sarif` template is owned by the `/threat-model` command.

---

## 3. Security-Severity Semantics Shift

| File | Severity Semantics | Rule-Level | Per-Finding | Status |
|------|-------------------|------------|-------------|--------|
| `threats.sarif` | Static category-level | Yes (e.g., spoofing: `"9.0"`) | No (results have no `properties.security-severity`) | **PASS** |
| `risk-scores.sarif` | Per-finding composite (inherent) score | Yes (max composite per rule) | Yes (e.g., LLM-1: `"8.3"`, S-1: `"7.9"`) | **PASS** |
| `compensating-controls.sarif` template | Per-finding RESIDUAL score | Yes (placeholder: `"<max-residual-score-for-*-findings>"`) | Yes (placeholder: `"<residual-score-as-numeric-string>"`) | **PASS** |

### Verification Details

- **threats.sarif**: Confirmed that results contain NO `properties` key at all. Security-severity exists only at `rules[].properties.security-severity` with static values (8.0 or 9.0 per STRIDE category). This is the correct static category-level semantic.
- **risk-scores.sarif**: Confirmed that every result has `properties.security-severity` set to its individual composite score (ranging from 4.3 to 8.3). Rule-level values reflect the max composite among that rule's findings (e.g., spoofing rule: `"7.9"` = max of S-1 through S-4).
- **compensating-controls.sarif template**: Confirmed via `_comment` (line 2) that "security-severity in risk-scores.sarif is the per-finding composite (inherent) score; in compensating-controls.sarif it is the per-finding RESIDUAL score." Template result properties use `"<residual-score-as-numeric-string>"` placeholders, not inherent score placeholders.

### Agent File Verification

**PASS** -- The control-analyzer agent (Phase 6c, line 1277) explicitly maps:

| Property | Value |
|----------|-------|
| `security-severity` | `residual_score` as a numeric string (e.g., `"3.9"`) |
| `inherent-risk` | `composite_score` as a numeric string (e.g., `"7.8"`) |
| `residual-risk` | `residual_score` as a numeric string (e.g., `"3.9"`) |

This confirms the agent sets `security-severity` to `residual_score` (not `composite_score`), which is the correct semantic shift for the third link in the chain.

---

## 4. Complete findingId/v1 Inventory (from risk-scores.sarif)

34 findings that MUST be preserved in compensating-controls.sarif output:

| ID | STRIDE Category | Composite Score (Inherent) |
|----|----------------|---------------------------|
| AG-1 | Agentic | 7.6 |
| AG-2 | Agentic | 5.2 |
| AG-3 | Agentic | 7.0 |
| AG-4 | Agentic | 6.4 |
| D-1 | Denial of Service | 7.4 |
| D-2 | Denial of Service | 7.3 |
| D-3 | Denial of Service | 6.4 |
| D-4 | Denial of Service | 6.0 |
| D-5 | Denial of Service | 5.3 |
| E-1 | Elevation of Privilege | 6.6 |
| E-2 | Elevation of Privilege | 7.6 |
| E-3 | Elevation of Privilege | 7.5 |
| I-1 | Information Disclosure | 6.2 |
| I-2 | Information Disclosure | 5.5 |
| I-3 | Information Disclosure | 5.6 |
| I-4 | Information Disclosure | 5.9 |
| I-5 | Information Disclosure | 5.1 |
| LLM-1 | LLM | 8.3 |
| LLM-2 | LLM | 6.3 |
| LLM-3 | LLM | 5.0 |
| R-1 | Repudiation | 4.8 |
| R-2 | Repudiation | 4.5 |
| R-3 | Repudiation | 5.2 |
| R-4 | Repudiation | 4.3 |
| R-5 | Repudiation | 4.6 |
| S-1 | Spoofing | 7.9 |
| S-2 | Spoofing | 6.7 |
| S-3 | Spoofing | 7.2 |
| S-4 | Spoofing | 5.7 |
| T-1 | Tampering | 5.8 |
| T-2 | Tampering | 6.1 |
| T-3 | Tampering | 7.1 |
| T-4 | Tampering | 6.3 |
| T-5 | Tampering | 5.4 |

---

## 5. Summary

| Check | Result |
|-------|--------|
| Fingerprint continuity: threats -> risk-scores | **PASS** |
| Fingerprint preservation documented in template | **PASS** |
| Fingerprint preservation enforced in agent | **PASS** |
| Tool driver: threats.sarif = `"tachi"` | **FAIL** (actual: `"Tachi"`) |
| Tool driver: risk-scores.sarif = `"tachi-risk-scorer"` | **PASS** |
| Tool driver: compensating-controls.sarif = `"tachi-control-analyzer"` | **PASS** |
| Severity semantics: threats = static category | **PASS** |
| Severity semantics: risk-scores = per-finding composite | **PASS** |
| Severity semantics: compensating-controls = per-finding residual | **PASS** |
| Agent sets security-severity to residual_score | **PASS** |
| All 34 finding IDs accounted for | **PASS** |

**Overall**: 10 PASS, 1 FAIL (cosmetic, out of scope for feature 036)

The single FAIL is the `"Tachi"` vs `"tachi"` casing in `threats.sarif`, which is owned by the `/threat-model` command (not feature 036). It does not affect supersession chain behavior because GitHub Code Scanning uses `partialFingerprints` for alert identity tracking, not tool driver names.
