# T017 Validation: SARIF Output Against ascii-web-api Example

**Task**: Validate orchestrator SARIF instructions against `examples/ascii-web-api/input.md`
**Date**: 2026-03-22
**Validator**: tester agent
**Input**: Traditional web API architecture (STRIDE-only, no AI components)

## Input Architecture Summary

The `examples/ascii-web-api/input.md` describes a web API with authentication:
- **Components**: External User (External Entity), API Gateway/NGINX/Kong (Process), Auth Service/Node.js (Process), User Database/PostgreSQL (Data Store)
- **Trust Zones**: External Zone (External User), Internal Zone (API Gateway, Auth Service, User Database)
- **Data Flows**: HTTPS credentials, JWT tokens, SQL credential lookups, API responses
- **AI Components**: None -- this is a traditional web API architecture

## Validation Checklist

### 1. Orchestrator produces `threats.sarif` alongside `threats.md`
**Status**: PASS

Line 1187 states: "produce a `threats.sarif` file in the same output directory." Line 1553 confirms: "write the `threats.sarif` file to the output directory alongside `threats.md`." The instruction is explicit and unconditional -- it applies to every run, not conditionally based on input type.

### 2. For STRIDE-only inputs, only STRIDE rules appear in `tool.driver.rules[]`
**Status**: PASS

Line 1210 states: "Only include rules for categories that produced findings in the current run. If the architecture has no AI components and only STRIDE findings were generated, omit AI rules from `tool.driver.rules[]`." This directly addresses the ascii-web-api scenario, which has no AI components.

### 3. Instructions explicitly state: "Only include rules for categories that produced findings in the current run"
**Status**: PASS

The exact phrase appears at line 1210: "Only include rules for categories that produced findings in the current run." Additionally, line 1237 reinforces: "For each threat category that produced at least one finding, create a `reportingDescriptor` object."

### 4. If no AI findings exist, `tachi/ai/agentic-threats` and `tachi/ai/llm-threats` are NOT included in rules
**Status**: PASS

Lines 1210 explicitly covers this: "If the architecture has no AI components and only STRIDE findings were generated, omit AI rules from `tool.driver.rules[]`." Since the rule inclusion is conditioned on "categories that produced findings," and the ascii-web-api input would produce no AI findings, the AI rules (`tachi/ai/agentic-threats`, `tachi/ai/llm-threats`) would be correctly excluded.

### 5. STRIDE category mappings are complete
**Status**: PASS

All six STRIDE categories are present in the mapping table at lines 1197-1202:
- `spoofing` -> `tachi/stride/spoofing` (prefix S)
- `tampering` -> `tachi/stride/tampering` (prefix T)
- `repudiation` -> `tachi/stride/repudiation` (prefix R)
- `info-disclosure` -> `tachi/stride/information-disclosure` (prefix I)
- `denial-of-service` -> `tachi/stride/denial-of-service` (prefix D)
- `privilege-escalation` -> `tachi/stride/elevation-of-privilege` (prefix E)

The naming normalization note at lines 1206-1208 correctly documents the two IR-to-SARIF name differences (`info-disclosure` to `information-disclosure`, `privilege-escalation` to `elevation-of-privilege`).

### 6. Severity mapping applies correctly to all levels
**Status**: PASS

The severity mapping table at lines 1217-1222 covers all five risk levels:
- Critical -> `error` / `"9.0"`
- High -> `error` / `"8.0"`
- Medium -> `warning` / `"5.0"`
- Low -> `note` / `"2.0"`
- Note -> `note` / `"0.1"`

Line 1224 provides rationale for the Note-level mapping to `"0.1"` rather than `"0.0"`, ensuring visibility in GitHub Code Scanning. Line 1214 requires security-severity to be a numeric string for GitHub compatibility.

### 7. Dual-location instructions apply regardless of input type
**Status**: PASS

Line 1411 states: "Every SARIF result MUST include both a `physicalLocation` and a `logicalLocations[]` array in its `locations[]` entry." This is an unconditional requirement -- there is no condition checking for AI vs STRIDE-only or any input type qualifier. Line 1428 further reinforces: "Include it on every result regardless of the target consumer." The ascii-web-api results would correctly receive both location types.

### 8. Fingerprint computation applies regardless of input type
**Status**: PASS

Line 1458 states: "Every SARIF result MUST include a `partialFingerprints` object with deterministic values." This is unconditional -- no input-type conditions. The fingerprint computation at lines 1461-1466 (SHA-256 of `ruleId|component_name`, truncated to 16 hex characters) and the `findingId/v1` cross-reference at lines 1468-1471 apply to all findings regardless of category or input type.

### 9. Zero-findings edge case is handled
**Status**: PASS

Line 1537 states: "Empty findings: If the threat model produces zero findings, `results` is an empty array `[]` and `rules` is an empty array `[]`." This is explicit and handles both arrays correctly -- no orphan rules when there are no findings, and no missing structural elements.

### 10. Instructions produce valid SARIF for traditional (non-AI) architecture inputs
**Status**: PASS

The SARIF Schema Compliance Structure (lines 1504-1539) defines the exact top-level JSON structure with `$schema`, `version`, and `runs` entries. The JSON Structural Self-Check (lines 1541-1551) provides five validation points that must pass before output. None of these structural requirements are conditional on AI presence. For the ascii-web-api input specifically:
- Rules array would contain only STRIDE categories that produced findings (e.g., spoofing, tampering, etc.)
- Results would map to those STRIDE rules only
- Dual-location would reference Internal/External zone components
- Fingerprints would use STRIDE rule IDs (e.g., `tachi/stride/spoofing|API Gateway`)
- The self-check at line 1547 ("every `ruleId` referenced by a result has a corresponding entry in `tool.driver.rules[]`") ensures consistency

## Issues Found

None. All checklist items pass.

## Overall Status: PASS

The orchestrator SARIF instructions at `agents/orchestrator.md` (lines 1185-1553) correctly handle STRIDE-only architecture inputs like `examples/ascii-web-api/input.md`. The instructions are explicit about conditional rule inclusion, unconditional dual-location and fingerprint requirements, and zero-findings edge cases. A traditional web API with no AI components would produce a valid SARIF 2.1.0 file containing only STRIDE rules and results.
