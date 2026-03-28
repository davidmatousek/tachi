# SARIF Template Validation Report (T018)

**File**: `templates/compensating-controls.sarif`
**Validated against**: SARIF 2.1.0 schema requirements
**Date**: 2026-03-28
**Result**: **72/72 PASS** -- all checks passed

---

## 1. JSON Structure

- [x] PASS -- 1.1 Valid JSON: File parsed without errors

## 2. Top-Level Fields

- [x] PASS -- 2.1 `$schema` references SARIF 2.1.0 schema URL (`https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json`)
- [x] PASS -- 2.2 `version` is `"2.1.0"`
- [x] PASS -- 2.3 `runs` is a non-empty array (length: 1)

## 3. Tool Driver

- [x] PASS -- 3.1 `runs[0].tool.driver.name` is `"tachi-control-analyzer"`
- [x] PASS -- 3.2 `runs[0].tool.driver.version` is `"1.0"`
- [x] PASS -- 3.3 `rules` array exists with exactly 8 rules (6 STRIDE + 2 AI)

## 4. Rule IDs

All 8 expected rule IDs are present in the `rules` array:

- [x] PASS -- 4.1 `tachi/stride/spoofing`
- [x] PASS -- 4.2 `tachi/stride/tampering`
- [x] PASS -- 4.3 `tachi/stride/repudiation`
- [x] PASS -- 4.4 `tachi/stride/information-disclosure`
- [x] PASS -- 4.5 `tachi/stride/denial-of-service`
- [x] PASS -- 4.6 `tachi/stride/elevation-of-privilege`
- [x] PASS -- 4.7 `tachi/ai/agentic-threats`
- [x] PASS -- 4.8 `tachi/ai/llm-threats`

## 5. Taxonomies

- [x] PASS -- 5.1 OWASP taxonomy declared (version: 2021)
- [x] PASS -- 5.2 CWE taxonomy declared (version: 4.13)

## 6. Example Results

5 example results present, covering all required scenarios:

- [x] PASS -- 6.0 Results array has 5 examples (minimum required: 5)
- [x] PASS -- 6.1 "found" control example exists (count: 2 -- results[0] spoofing, results[3] agentic)
- [x] PASS -- 6.2 "found" control has `relatedLocations` with control evidence entries
- [x] PASS -- 6.3 "partial" control example exists (count: 2 -- results[1] tampering, results[4] information-disclosure)
- [x] PASS -- 6.4 "partial" control has non-empty `recommendation` field
- [x] PASS -- 6.5 "missing" control example exists (count: 1 -- results[2] denial-of-service)
- [x] PASS -- 6.6 "missing" control has no `relatedLocations` (omitted entirely)
- [x] PASS -- 6.7 AI category result exists (ruleId: `tachi/ai/agentic-threats`)
- [x] PASS -- 6.8 Correlated finding group example exists (results[4] with `correlationGroup: CG-1`)
- [x] PASS -- 6.9 Correlated group contains peer reference via `logicalLocations`-only entry in `relatedLocations`

### Example Result Summary

| Index | ruleId | control-status | Key Feature |
|-------|--------|----------------|-------------|
| 0 | tachi/stride/spoofing | found | 2 relatedLocations with control evidence |
| 1 | tachi/stride/tampering | partial | Recommendation with hardening guidance |
| 2 | tachi/stride/denial-of-service | missing | No relatedLocations, full remediation guidance |
| 3 | tachi/ai/agentic-threats | found | AI category with CWE-only taxonomy |
| 4 | tachi/stride/information-disclosure | partial | correlationGroup with dual-purpose relatedLocations |

## 7. Property Bag Fields

All 8 required properties verified across all 5 example results (40 checks total):

### Result[0] -- spoofing / found
- [x] PASS -- 7.1.1 `security-severity`
- [x] PASS -- 7.1.2 `control-status`
- [x] PASS -- 7.1.3 `control-evidence`
- [x] PASS -- 7.1.4 `control-effectiveness`
- [x] PASS -- 7.1.5 `inherent-risk`
- [x] PASS -- 7.1.6 `residual-risk`
- [x] PASS -- 7.1.7 `recommendation`
- [x] PASS -- 7.1.8 `effort-estimate`

### Result[1] -- tampering / partial
- [x] PASS -- 7.2.1 `security-severity`
- [x] PASS -- 7.2.2 `control-status`
- [x] PASS -- 7.2.3 `control-evidence`
- [x] PASS -- 7.2.4 `control-effectiveness`
- [x] PASS -- 7.2.5 `inherent-risk`
- [x] PASS -- 7.2.6 `residual-risk`
- [x] PASS -- 7.2.7 `recommendation`
- [x] PASS -- 7.2.8 `effort-estimate`

### Result[2] -- denial-of-service / missing
- [x] PASS -- 7.3.1 `security-severity`
- [x] PASS -- 7.3.2 `control-status`
- [x] PASS -- 7.3.3 `control-evidence`
- [x] PASS -- 7.3.4 `control-effectiveness`
- [x] PASS -- 7.3.5 `inherent-risk`
- [x] PASS -- 7.3.6 `residual-risk`
- [x] PASS -- 7.3.7 `recommendation`
- [x] PASS -- 7.3.8 `effort-estimate`

### Result[3] -- agentic-threats / found
- [x] PASS -- 7.4.1 `security-severity`
- [x] PASS -- 7.4.2 `control-status`
- [x] PASS -- 7.4.3 `control-evidence`
- [x] PASS -- 7.4.4 `control-effectiveness`
- [x] PASS -- 7.4.5 `inherent-risk`
- [x] PASS -- 7.4.6 `residual-risk`
- [x] PASS -- 7.4.7 `recommendation`
- [x] PASS -- 7.4.8 `effort-estimate`

### Result[4] -- information-disclosure / partial (correlated)
- [x] PASS -- 7.5.1 `security-severity`
- [x] PASS -- 7.5.2 `control-status`
- [x] PASS -- 7.5.3 `control-evidence`
- [x] PASS -- 7.5.4 `control-effectiveness`
- [x] PASS -- 7.5.5 `inherent-risk`
- [x] PASS -- 7.5.6 `residual-risk`
- [x] PASS -- 7.5.7 `recommendation`
- [x] PASS -- 7.5.8 `effort-estimate`

## 8. Fingerprint Preservation

All 5 example results contain `partialFingerprints` with `findingId/v1`:

- [x] PASS -- 8.1 Result[0] `findingId/v1`: `S-1`
- [x] PASS -- 8.2 Result[1] `findingId/v1`: `T-2`
- [x] PASS -- 8.3 Result[2] `findingId/v1`: `D-1`
- [x] PASS -- 8.4 Result[3] `findingId/v1`: `AG-1`
- [x] PASS -- 8.5 Result[4] `findingId/v1`: `I-3`

---

## Validation Verdict

**PASS** -- The SARIF template `templates/compensating-controls.sarif` satisfies all 72 validation checks across 8 requirement categories. The template is structurally valid SARIF 2.1.0 with correct tool driver metadata, complete rule coverage (6 STRIDE + 2 AI), both OWASP and CWE taxonomies, representative examples for all control statuses (found/partial/missing), AI-category results, correlated finding groups, complete property bags, and preserved fingerprints for supersession chain continuity.
