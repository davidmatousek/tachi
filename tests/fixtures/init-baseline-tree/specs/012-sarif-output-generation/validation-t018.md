# T018 Validation: SARIF Schema Compliance

**Date**: 2026-03-22
**Validator**: tester (BDD agent)
**Scope**: Validate that orchestrator prompt instructions, reference template, and examples correctly describe SARIF 2.1.0 schema requirements.

## Files Reviewed

- `agents/orchestrator.md` — SARIF Output Generation section (lines 1185-1677)
- `templates/threats.sarif` — Reference template (142 lines)
- `specs/012-sarif-output-generation/spec.md` — Feature specification

---

## Schema Compliance Checklist

### Top-level Structure

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | `$schema` URI is correct | PASS | Template and orchestrator both use `https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json` |
| 2 | `version` is `"2.1.0"` | PASS | Template: `"2.1.0"`. Orchestrator SARIF Schema Compliance Structure section (line 1634): `"2.1.0"` |
| 3 | Single `runs[]` entry | PASS | Template has exactly 1 run entry. Orchestrator states "exactly one `runs` entry" (line 1656) |

### Tool Metadata

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 4 | `tool.driver.name` is "Tachi" | PASS | Template: `"Tachi"`. Orchestrator line 1230: `"Tachi"` |
| 5 | `tool.driver.semanticVersion` references output.yaml | PASS | Template: `"1.1"`. Orchestrator line 1231 references `schema_version` from `schemas/output.yaml`. Confirmed `output.yaml` has `schema_version: "1.1"` |
| 6 | `tool.driver.rules[]` contains reportingDescriptor objects | PASS | Template has 2 rules with full reportingDescriptor structure. Orchestrator defines rule template (lines 1241-1258) |

### Result Objects

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 7 | Every result has `ruleId`, `message.text`, `level` | PASS | Both template results have all three fields. Self-check (line 1669) validates these |
| 8 | `locations[]` with `physicalLocation` on every result | PASS | Both template results include `physicalLocation` with `artifactLocation.uri` and `region.startLine`. Orchestrator mandates this (lines 1413-1416) |
| 9 | `partialFingerprints` present on every result | PASS | Result 0 has `primaryLocationLineHash`, `findingId/v1`, `correlationGroup`. Result 1 has `primaryLocationLineHash`, `findingId/v1` (correctly omits `correlationGroup` for uncorrelated finding) |

### Rule Definitions (reportingDescriptor)

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 10 | `shortDescription.text` max 255 chars constraint stated | PASS | Orchestrator line 1245: `"max 255 characters"`. Template values: 25 and 36 chars respectively |
| 11 | `fullDescription.text` max 1024 chars constraint stated | PASS | Orchestrator line 1248: `"max 1024 characters"`. Template values: 194 and 188 chars respectively |
| 12 | `help.text` and `help.markdown` present | PASS | Both template rules include `help.text` and `help.markdown`. Orchestrator lines 1250-1252 mandate both |
| 13 | `properties.tags` with max 20 tags constraint stated | PASS | Orchestrator line 1261: `"Maximum 20 tags per rule"`. Template tags: 4 and 5 tags respectively |
| 14 | `properties.security-severity` is a numeric string | PASS | Template values are `"8.0"` (string type confirmed programmatically). Orchestrator line 1214 explicitly states `"8.0"`, not `8.0` |

### GitHub Code Scanning Compatibility

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 15 | `security-severity` described as numeric string throughout | PASS | Orchestrator uses `"numeric string"` phrasing at lines 1214, 1216, 1256, 1671. Self-check (line 1671) validates format |
| 16 | `physicalLocation` with `artifactLocation.uri` and `region.startLine` on every result | PASS | Both template results have complete physicalLocation. Orchestrator Dual-Location section (lines 1409-1427) mandates both fields |
| 17 | Rule names within GitHub limits (255 shortDesc, 1024 fullDesc, 20 tags) | PASS | Constraints are stated in orchestrator. Template values are within all limits |

### Template Validation

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 18 | `templates/threats.sarif` is valid JSON | PASS | Validated with Python `json.load()` — no parse errors |
| 19 | Template structure matches orchestrator instructions | PASS | Template top-level structure matches SARIF Schema Compliance Structure (lines 1627-1652). All required fields present |
| 20 | Template includes examples of all key fields | PASS | Template includes: 2 results, 2 rules, relatedLocations (on result 0), partialFingerprints (both variants: correlated and uncorrelated), physicalLocation, logicalLocations |

---

## Issues Found

### Issue 1: Taxonomy Rule ID Inconsistency (Severity: Medium)

**Location**: `agents/orchestrator.md` line 1611

**Problem**: The taxonomy example for Agentic Threats uses rule ID `"tachi/ai/agentic"` but the canonical Category to Rule ID Mapping Table (line 1203) defines the rule ID as `"tachi/ai/agentic-threats"`.

**Evidence**:
- Line 1203 (mapping table): `tachi/ai/agentic-threats`
- Line 1611 (taxonomy example): `tachi/ai/agentic`
- Template file: `tachi/ai/agentic-threats`

**Impact**: An LLM following the taxonomy example could produce a rule ID that does not match the canonical mapping, causing orphan rule references and failing the JSON structural self-check (rule-result consistency check, line 1670).

**Recommendation**: Change line 1611 from `"tachi/ai/agentic"` to `"tachi/ai/agentic-threats"`.

### Issue 2: Spoofing shortDescription Inconsistency in Taxonomy Example (Severity: Low)

**Location**: `agents/orchestrator.md` line 1586

**Problem**: The taxonomy example for Spoofing uses `"Spoofing identity threats"` but the canonical mapping table (line 1197) and reference examples (line 1268) both use `"Identity spoofing threats"`.

**Evidence**:
- Line 1197 (mapping table): `Identity spoofing threats`
- Line 1268 (reference example): `Identity spoofing threats`
- Line 1586 (taxonomy example): `Spoofing identity threats`
- Template file: `Identity spoofing threats`

**Impact**: Minor. An LLM may use either phrasing. Both are within 255 chars. However, the inconsistency could lead to unstable shortDescription text across runs.

**Recommendation**: Change line 1586 from `"Spoofing identity threats"` to `"Identity spoofing threats"` for consistency.

### Issue 3: Self-Check References `security-severity` on Results (Severity: Low)

**Location**: `agents/orchestrator.md` line 1671

**Problem**: The JSON Structural Self-Check states: "Every `security-severity` value (in both rules and results) is a numeric string". However, the SARIF 2.1.0 specification and the orchestrator's own result mapping (lines 1282-1322) place `security-severity` only in rule `properties`, not on individual result objects. No result example in the orchestrator or template includes a `security-severity` field.

**Impact**: Low. The phrasing "in both rules and results" may confuse an LLM into adding `security-severity` to result objects, which would add non-standard fields. In practice, the detailed result mapping instructions do not include it, so the LLM is unlikely to add it.

**Recommendation**: Clarify line 1671 to say "Every `security-severity` value in `tool.driver.rules[].properties`" to match the actual SARIF structure.

### Issue 4: Template Missing Taxonomies (Severity: Informational)

**Location**: `templates/threats.sarif`

**Problem**: The template does not include `taxonomies`, `supportedTaxonomies`, or `relationships` fields. The orchestrator describes these as P1 and "enabled by default" (line 1506).

**Impact**: Informational. The template is described as a "structural reference" (line 1662). The taxonomy instructions are comprehensive in the orchestrator text with full JSON examples. An LLM can follow the text instructions without a template example. However, having a complete template would reduce the chance of structural errors in taxonomy output.

**Recommendation**: Consider adding taxonomy fields to the template for completeness. Not blocking since the orchestrator instructions are detailed.

---

## Summary

| Category | Pass | Fail | Total |
|----------|------|------|-------|
| Top-level Structure | 3 | 0 | 3 |
| Tool Metadata | 3 | 0 | 3 |
| Result Objects | 3 | 0 | 3 |
| Rule Definitions | 5 | 0 | 5 |
| GitHub Code Scanning | 3 | 0 | 3 |
| Template Validation | 3 | 0 | 3 |
| **Total** | **20** | **0** | **20** |

**Issues**: 2 Medium, 1 Low, 1 Informational

**Overall Status**: **PASS** (all 20 checklist items pass; 2 non-blocking issues identified for correction)

The SARIF schema compliance instructions in `agents/orchestrator.md` correctly describe SARIF 2.1.0 requirements. The `templates/threats.sarif` reference template is valid JSON and structurally matches the orchestrator instructions. The two medium/low issues are inconsistencies within the orchestrator text examples (not in the normative instructions or template) and should be corrected to prevent LLM confusion.
