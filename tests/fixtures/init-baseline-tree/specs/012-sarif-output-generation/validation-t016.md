# T016 Validation: SARIF Output Generation vs Mermaid-Agentic-App Example

**Validator**: tester agent
**Date**: 2026-03-22
**Input reviewed**: `examples/mermaid-agentic-app/input.md`
**Orchestrator section**: `agents/orchestrator.md` lines 1185-1553 (SARIF Output Generation)
**Template**: `templates/threats.sarif`
**Schema**: `schemas/output.yaml`

---

## Validation Checklist

### 1. Produces `threats.sarif` alongside `threats.md`
**Status**: PASS

Line 1187 explicitly instructs: "produce a `threats.sarif` file in the same output directory." Line 1553 confirms: "write the `threats.sarif` file to the output directory alongside `threats.md`." The instruction is unambiguous.

---

### 2. References both STRIDE AND AI threat categories
**Status**: PASS

The Category to Rule ID Mapping Table (lines 1195-1204) defines all 6 STRIDE categories plus both AI categories (agentic, llm). The mermaid-agentic-app input contains AI components: "LLM Agent Orchestrator" (dual-dispatch: LLM + AG) and "MCP Tool Server" (AG dispatch). The orchestrator instructions would correctly include AI rules when processing this input because line 1210 states: "Only include rules for categories that produced findings in the current run." Since the agentic-app input triggers both LLM and AG dispatch, both AI rule types would be included.

---

### 3. Category to Rule ID mapping covers all 8 categories
**Status**: PASS

The mapping table at lines 1195-1204 covers exactly 8 categories:

| Category | Rule ID | Verified |
|----------|---------|----------|
| spoofing | tachi/stride/spoofing | Yes |
| tampering | tachi/stride/tampering | Yes |
| repudiation | tachi/stride/repudiation | Yes |
| info-disclosure | tachi/stride/information-disclosure | Yes |
| denial-of-service | tachi/stride/denial-of-service | Yes |
| privilege-escalation | tachi/stride/elevation-of-privilege | Yes |
| agentic | tachi/ai/agentic-threats | Yes |
| llm | tachi/ai/llm-threats | Yes |

Naming normalization is documented (lines 1206-1208): `info-disclosure` expands to `information-disclosure`, `privilege-escalation` maps to `elevation-of-privilege`.

---

### 4. Severity mapping covers all 5 levels
**Status**: PASS

The Severity Mapping Table (lines 1216-1222) covers all 5 levels:

| Risk Level | SARIF level | security-severity | Verified |
|-----------|-------------|-------------------|----------|
| Critical | error | "9.0" | Yes |
| High | error | "8.0" | Yes |
| Medium | warning | "5.0" | Yes |
| Low | note | "2.0" | Yes |
| Note | note | "0.1" | Yes |

This matches the SARIF Severity Mapping comment in `schemas/output.yaml` (lines 156-164). The output.yaml uses CVSS ranges (e.g., Critical = 9.0-10.0), while the orchestrator assigns fixed representative values within those ranges. The orchestrator's fixed values (9.0, 8.0, 5.0, 2.0, 0.1) fall within the output.yaml ranges. This is consistent.

Note-level rationale is documented at line 1224: maps to note/0.1 (not none/0.0) to keep findings visible in GitHub Code Scanning.

---

### 5. Tool metadata: name="Tachi", semanticVersion from output.yaml
**Status**: PASS

Lines 1230-1232 specify:
- `name`: "Tachi"
- `semanticVersion`: "Use the `schema_version` value from `schemas/output.yaml` (currently `"1.1"`)"
- `informationUri`: repository URL

The template `threats.sarif` confirms this structure (lines 8-9): `"name": "Tachi"`, `"semanticVersion": "1.1"`. The `schemas/output.yaml` declares `schema_version: "1.1"` at line 12. All three sources are consistent.

---

### 6. Results include dual locations (physicalLocation + logicalLocations)
**Status**: PASS

The Dual-Location Instructions section (lines 1409-1454) explicitly requires both:
- `physicalLocation` with `artifactLocation.uri` (input file path) and `region.startLine` (always 1)
- `logicalLocations[]` with `name` (component), `fullyQualifiedName` (trust_zone/component), `kind` (DFD element type mapped to lowercase-hyphenated)

The self-check at line 1546 enforces this: "Every result has ... `locations[]` (with both `physicalLocation` and `logicalLocations`)."

For the mermaid-agentic-app input, the trust zones are "User Zone", "Application Zone", and "External Services", so findings would produce logical locations like "Application Zone/LLM Agent Orchestrator" with kind "process". The DFD element type mapping (line 1302) covers all four types.

---

### 7. Results include partialFingerprints (primaryLocationLineHash + findingId/v1)
**Status**: PASS

The Fingerprint Computation section (lines 1456-1502) specifies:
- `primaryLocationLineHash`: SHA-256 hash of `"{ruleId}|{component_name}"`, truncated to first 16 hex characters
- `findingId/v1`: The finding IR `id` value (e.g., "S-1", "AG-2")

Determinism requirement is documented (lines 1458, 1466): "Same inputs MUST produce same outputs." The self-check at line 1546 enforces presence of `partialFingerprints` on every result.

---

### 8. Correlated findings use relatedLocations (not duplicate results)
**Status**: PASS

The Correlated Finding Mapping section (lines 1324-1407) specifies:
- Primary finding gets a full SARIF result with `relatedLocations[]` (line 1332-1334)
- Each correlated peer is an entry in `relatedLocations[]` with `id`, `message.text`, and `logicalLocations[]` (lines 1335-1340)
- `correlationGroup` is stored in `partialFingerprints` (line 1342)
- Line 1344: "Do NOT create separate top-level results for correlated peers"

The template `threats.sarif` demonstrates this pattern (lines 87-106): the first result has `relatedLocations` with peer info and `correlationGroup` in fingerprints.

---

### 9. Zero-correlation case handled (no relatedLocations, no correlationGroup)
**Status**: PASS

Line 1346 explicitly addresses this: "If a finding is not part of any correlation group (has no correlations), skip `relatedLocations` entirely -- do not include an empty array. Do NOT include a `correlationGroup` key in `partialFingerprints` for uncorrelated findings."

The template `threats.sarif` demonstrates both cases: the first result (lines 61-107) has `relatedLocations` and `correlationGroup`, while the second result (lines 108-138) has neither.

---

### 10. JSON structural self-check validates all required properties
**Status**: PASS (with 1 concern noted below)

The JSON Structural Self-Check (lines 1541-1551) validates 5 items:
1. Required properties: `$schema`, `version`, `runs`, `tool`, `results`
2. Result completeness: `ruleId`, `message.text`, `level`, `locations[]`, `partialFingerprints`
3. Rule-result consistency: no orphan rule IDs
4. Security-severity format: numeric strings
5. Result count: matches deduplicated finding count

**Concern**: Self-check item 4 (line 1548) states: "Every `security-severity` value (in both rules **and results**)" -- however, the Finding IR to SARIF Result Mapping (lines 1286-1322) does NOT instruct placing `security-severity` on individual result objects. The `security-severity` property is only specified on rule `properties` (line 1256). In SARIF 2.1.0, `security-severity` is a property of `reportingDescriptor.properties` (rules), not `result.properties`. The "and results" phrasing in the self-check is misleading -- if interpreted literally, the LLM would attempt to add `security-severity` to each result object, which is not part of the SARIF spec for results. In practice, since no instruction tells the LLM to put `security-severity` on results, the check would simply find nothing to validate on the result side and pass vacuously. This is a documentation clarity issue, not a correctness failure, since no instruction actually produces the incorrect structure.

---

## Summary

| # | Checklist Item | Status |
|---|---------------|--------|
| 1 | Produces threats.sarif alongside threats.md | PASS |
| 2 | References both STRIDE AND AI categories | PASS |
| 3 | Category to Rule ID covers all 8 categories | PASS |
| 4 | Severity mapping covers all 5 levels | PASS |
| 5 | Tool metadata (name, semanticVersion) | PASS |
| 6 | Dual locations (physical + logical) | PASS |
| 7 | partialFingerprints (hash + findingId) | PASS |
| 8 | Correlated findings use relatedLocations | PASS |
| 9 | Zero-correlation case handled | PASS |
| 10 | JSON structural self-check | PASS |

**Issues found**: 1 (documentation clarity, non-blocking)

**Issue detail**: Self-check item 4 (line 1548) references `security-severity` "in both rules and results" but no instruction places `security-severity` on individual result objects. This is misleading but non-blocking because the result mapping instructions are correct and do not produce the incorrect structure.

---

## Overall Status: PASS

All 10 checklist items pass. The SARIF Output Generation section in `agents/orchestrator.md` contains complete, correct, and internally consistent instructions that would produce valid SARIF 2.1.0 output when run against `examples/mermaid-agentic-app/input.md`. The one documentation clarity concern (self-check referencing "results" for security-severity) is non-blocking.
