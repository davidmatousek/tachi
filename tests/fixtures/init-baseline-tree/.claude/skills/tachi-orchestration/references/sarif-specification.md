---
source_agent: orchestrator
extracted_from: .claude/agents/tachi/orchestrator.md
version: 1.0.0
---

# SARIF 2.1.0 Generation Specification

After the `threats.md` output is structurally validated, produce a `threats.sarif` file in the same output directory. The SARIF file contains the same findings in SARIF 2.1.0 format for integration with GitHub Code Scanning, VS Code SARIF Viewer, Azure DevOps, and other SARIF-compatible security tools.

Phase 4 already has all finding data from Phase 3. The SARIF generation step transforms that data into a JSON file — no additional analysis or agent invocation is needed. Follow the instructions below to produce the `threats.sarif` file.

## Category to Rule ID Mapping Table

Map each finding's `category` value (from the finding IR) to a SARIF `reportingDescriptor` rule ID using this canonical mapping. The mapping resolves naming differences between the finding IR enum values and SARIF rule ID conventions.

| Finding IR `category` | Finding ID Prefix | SARIF Rule ID | Short Description |
|----------------------|-------------------|---------------|-------------------|
| `spoofing` | S | `tachi/stride/spoofing` | Identity spoofing threats |
| `tampering` | T | `tachi/stride/tampering` | Data tampering threats |
| `repudiation` | R | `tachi/stride/repudiation` | Repudiation threats |
| `info-disclosure` | I | `tachi/stride/information-disclosure` | Information disclosure threats |
| `denial-of-service` | D | `tachi/stride/denial-of-service` | Denial of service threats |
| `privilege-escalation` | E | `tachi/stride/elevation-of-privilege` | Privilege escalation threats |
| `agentic` | AG | `tachi/ai/agentic-threats` | AI agent autonomy and misuse threats |
| `llm` | LLM | `tachi/ai/llm-threats` | LLM-specific threats |

**Naming normalization note**: Two categories use different names in SARIF rule IDs than in the finding IR:
- `info-disclosure` → `information-disclosure` (expanded form)
- `privilege-escalation` → `elevation-of-privilege` (STRIDE canonical term)

Only include rules for categories that produced findings in the current run. If the architecture has no AI components and only STRIDE findings were generated, omit AI rules from `tool.driver.rules[]`.

## Severity Mapping Table

Map each finding's `risk_level` to SARIF severity using this CVSS alignment table. The `security-severity` value MUST be a numeric string (e.g., `"8.0"`, not `8.0`) for GitHub Code Scanning compatibility.

| Tachi Risk Level | SARIF `level` | `security-severity` (numeric string) | GitHub Display |
|-----------------|---------------|--------------------------------------|----------------|
| Critical | `error` | `"9.0"` | Critical |
| High | `error` | `"8.0"` | High |
| Medium | `warning` | `"5.0"` | Medium |
| Low | `note` | `"2.0"` | Low |
| Note | `note` | `"0.1"` | Low (informational) |

**Note-level mapping**: The Note level maps to `note`/`"0.1"` (not `none`/`"0.0"`) to keep informational findings visible in GitHub Code Scanning within the Low severity band. A value of `"0.0"` would cause GitHub to hide the finding entirely.

## SARIF Tool Metadata

Populate the `tool.driver` object at the top of the SARIF file with the following fields:

- `name`: `"Tachi"`
- `semanticVersion`: Use the `schema_version` value from `../../../schemas/output.yaml` (currently `"1.1"`)
- `informationUri`: Use the repository URL (e.g., `"https://github.com/{owner}/{repo}"`)
- `rules`: An array of `reportingDescriptor` objects — one per threat category that produced findings in the current run. See Rule Definition Templates below.

## Rule Definition Templates

For each threat category that produced at least one finding, create a `reportingDescriptor` object in the `tool.driver.rules[]` array. Use the rule ID from the Category to Rule ID Mapping Table above.

Each `reportingDescriptor` MUST include these fields:

```json
{
  "id": "<rule-id-from-mapping-table>",
  "shortDescription": {
    "text": "<max 255 characters — category short description from mapping table>"
  },
  "fullDescription": {
    "text": "<max 1024 characters — expanded description of the threat category, what it covers, and why it matters>"
  },
  "help": {
    "text": "<plain text detection guidance — what to review to detect threats in this category>",
    "markdown": "<markdown with detection guidance AND framework references from the finding IR `references` field — include OWASP Top 10, CWE, and MITRE references where applicable>"
  },
  "properties": {
    "tags": ["security", "<category-family>", "<category-name>", "<additional-tags>"],
    "security-severity": "<numeric-string-from-severity-table>"
  }
}
```

**Tag constraints**: Maximum 20 tags per rule. Always include `"security"` as the first tag. Include the category family (`"stride"` or `"ai"`) and the specific category name. Add relevant framework identifiers (e.g., `"owasp"`, `"cwe"`, `"authentication"`) up to the 20-tag limit.

**`security-severity` on rules**: Set to the highest `security-severity` value among all findings in that category. For example, if a category has both High (`"8.0"`) and Medium (`"5.0"`) findings, set the rule's `security-severity` to `"8.0"`.

**Reference examples** for three categories:

**Spoofing** (`tachi/stride/spoofing`):
- `shortDescription.text`: `"Identity spoofing threats"`
- `help.markdown` references: OWASP A07 (Identification and Authentication Failures), CWE-287 (Improper Authentication)
- `tags`: `["security", "stride", "spoofing", "authentication"]`

**Information Disclosure** (`tachi/stride/information-disclosure`):
- `shortDescription.text`: `"Information disclosure threats"`
- `help.markdown` references: OWASP A01 (Broken Access Control), CWE-200 (Exposure of Sensitive Information)
- `tags`: `["security", "stride", "information-disclosure", "data-exposure"]`

**Agentic Threats** (`tachi/ai/agentic-threats`):
- `shortDescription.text`: `"AI agent autonomy and misuse threats"`
- `help.markdown` references: OWASP Agentic Security Initiative (ASI), MITRE ATLAS
- `tags`: `["security", "ai", "agentic", "autonomy", "tool-use"]`

## Finding IR to SARIF Result Mapping

For each finding collected in Phase 3, create a SARIF `result` object using this step-by-step mapping. Process every finding — zero findings may be lost in the translation from `threats.md` to `threats.sarif`.

**Step-by-step mapping for each finding**:

1. **`ruleId`**: Look up the finding's `category` in the Category to Rule ID Mapping Table. Set `ruleId` to the corresponding SARIF Rule ID.

2. **`message.text`**: Set to the finding's `threat` field value. Use probabilistic language ("may", "could") rather than certainty ("can", "will") since findings are generated by LLM analysis.

3. **`message.markdown`**: Set to the finding's `mitigation` field value. Format as markdown for rich display in SARIF viewers.

4. **`level`**: Look up the finding's `risk_level` in the Severity Mapping Table. Set `level` to the corresponding SARIF level (`error`, `warning`, or `note`).

5. **`locations[]`**: Create a single location entry with both physical and logical location (see Dual-Location structure below):
   - `physicalLocation.artifactLocation.uri`: Set to the input architecture file path
   - `physicalLocation.region.startLine`: Set to `1` (architecture-level analysis has no line-level granularity)
   - `logicalLocations[]`: Array with one entry:
     - `name`: The finding's `component` value
     - `fullyQualifiedName`: `"{trust_zone}/{component_name}"` — cross-reference the component's trust zone from Phase 1 Trust Boundaries data (Section 2 Trust Zones table)
     - `kind`: Map the finding's `dfd_element_type` to lowercase-hyphenated values: `External Entity` → `external-entity`, `Process` → `process`, `Data Store` → `data-store`, `Data Flow` → `data-flow`

6. **`partialFingerprints`**: See Fingerprint Computation below:
   - `primaryLocationLineHash`: Deterministic hash of `ruleId` + `component_name`
   - `findingId/v1`: The finding's `id` value (e.g., `"S-1"`, `"AG-2"`)

7. **`properties` (MAESTRO layer)**: Add MAESTRO layer metadata to the result's `properties` object:
   - Add `"maestro-layer:{layer-id}"` to the `properties.tags[]` array (e.g., `"maestro-layer:L3"`). Use the layer ID only (L1-L7) for tag brevity, or `"maestro-layer:Unclassified"` for unclassified findings.
   - Add `"maestro-layer"` key to `properties` with the full layer name as value (e.g., `"L3 — Agent Framework"`). Set to `"Unclassified"` when the finding's component matched no layer keywords.
   - These properties are **additive** — they occupy distinct keys from existing baseline properties (`delta_status`, `baselineState`) and existing tags (`security`, `stride`, `ai`). No conflict with any existing SARIF properties.

**Complete field mapping reference**:

| Finding IR Field | SARIF Object Path | Notes |
|-----------------|-------------------|-------|
| `id` | `result.partialFingerprints["findingId/v1"]` | Preserved for cross-reference to threats.md |
| `category` | `result.ruleId` | Via Category to Rule ID Mapping Table |
| `component` | `result.locations[].logicalLocations[].name` | Component name |
| `component` + trust zone | `result.locations[].logicalLocations[].fullyQualifiedName` | `"{trust_zone}/{component_name}"` |
| `threat` | `result.message.text` | Threat description |
| `mitigation` | `result.message.markdown` | Mitigation as markdown |
| `risk_level` | `result.level` + rule `properties.security-severity` | Via Severity Mapping Table |
| `dfd_element_type` | `result.locations[].logicalLocations[].kind` | Custom kinds: `external-entity`, `process`, `data-store`, `data-flow` |
| `references` | Rule `help.markdown` + `properties.tags` | OWASP, CWE, MITRE framework identifiers |
| `maestro_layer` | `result.properties.tags[]` + `result.properties["maestro-layer"]` | Tag: `"maestro-layer:{layer-id}"`, Property: full layer name |
| Input file | `result.locations[].physicalLocation.artifactLocation.uri` | Architecture input file path |
| (fixed) | `result.locations[].physicalLocation.region.startLine` | Always `1` |

## Correlated Finding Mapping

For each correlation group produced in Section 4a (Correlated Findings), map the group to SARIF results using these rules. Correlation groups represent related findings across threat categories targeting the same component — they must not produce duplicate top-level results.

**Step-by-step mapping for each correlation group**:

1. **Identify the primary finding**: The first finding listed in the correlation group is the primary. All other findings in the group are correlated peers.

2. **Create a full SARIF `result` for the primary finding only**: Map the primary finding using the complete Finding IR to SARIF Result Mapping above (ruleId, message, level, locations, partialFingerprints).

3. **Add correlated peers to `relatedLocations[]`**: For each correlated peer in the group, add an entry to the primary result's `relatedLocations[]` array:
   - `id`: Integer index starting at `0`, incrementing for each peer
   - `message.text`: `"{peer_finding_id}: {peer_threat_summary}"` — the peer's finding ID and a brief summary of its threat
   - `logicalLocations[]`: Array with one entry:
     - `name`: The peer's component name from finding IR
     - `fullyQualifiedName`: `"{trust_zone}/{peer_component_name}"` — cross-reference the peer component's trust zone from Phase 1 Trust Boundaries data
     - `kind`: The peer's DFD element type mapped to lowercase-hyphenated values (same mapping as step 5 in Finding IR to SARIF Result Mapping)

4. **Store the correlation group ID**: Set `partialFingerprints["correlationGroup"]` to the group identifier (e.g., `"CG-1"`).

5. **Do NOT create separate top-level results for correlated peers**: Peers are already represented via the primary result's `relatedLocations[]`. Creating separate results would produce duplicate alerts in GitHub Code Scanning.

6. **Zero-correlation case**: If a finding is not part of any correlation group (has no correlations), skip `relatedLocations` entirely — do not include an empty array. Do NOT include a `correlationGroup` key in `partialFingerprints` for uncorrelated findings.

**Example — correlated result with relatedLocations**:

```json
{
  "ruleId": "tachi/stride/spoofing",
  "message": {
    "text": "API Gateway may be vulnerable to token replay attacks due to missing token binding validation.",
    "markdown": "Implement token binding (DPoP or certificate-bound tokens) to prevent replay of stolen access tokens."
  },
  "level": "error",
  "locations": [
    {
      "physicalLocation": {
        "artifactLocation": { "uri": "architecture/input.md" },
        "region": { "startLine": 1 }
      },
      "logicalLocations": [
        {
          "name": "API Gateway",
          "fullyQualifiedName": "DMZ/API Gateway",
          "kind": "process"
        }
      ]
    }
  ],
  "relatedLocations": [
    {
      "id": 0,
      "message": {
        "text": "T-3: API Gateway session data may be tampered with in transit"
      },
      "logicalLocations": [
        {
          "name": "API Gateway",
          "fullyQualifiedName": "DMZ/API Gateway",
          "kind": "process"
        }
      ]
    },
    {
      "id": 1,
      "message": {
        "text": "I-2: API Gateway may leak authentication tokens in error responses"
      },
      "logicalLocations": [
        {
          "name": "API Gateway",
          "fullyQualifiedName": "DMZ/API Gateway",
          "kind": "process"
        }
      ]
    }
  ],
  "partialFingerprints": {
    "primaryLocationLineHash": "a1b2c3d4e5f67890",
    "findingId/v1": "S-1",
    "correlationGroup": "CG-1"
  }
}
```

## Dual-Location Instructions

Every SARIF result MUST include both a `physicalLocation` and a `logicalLocations[]` array in its `locations[]` entry. This dual-location strategy satisfies different SARIF consumers: GitHub Code Scanning requires `physicalLocation` for display, while VS Code SARIF Viewer and Azure DevOps benefit from `logicalLocations` for semantic component navigation.

**1. `physicalLocation`** — required by GitHub Code Scanning:

- `artifactLocation.uri`: Set to the input architecture file path (the file the user provided to tachi)
- `region.startLine`: Set to `1` — architecture-level threat analysis operates on the full document, not individual lines. Line `1` is a convention to satisfy SARIF viewers that require a region.

**2. `logicalLocations[]`** — one entry per finding with component-level semantics:

- `name`: The component name from the finding IR `component` field (e.g., `"API Gateway"`, `"User Database"`)
- `fullyQualifiedName`: `"{trust_zone}/{component_name}"` — the trust zone value MUST come from the Phase 1 Trust Zones/Trust Boundaries extraction (Section 2 Trust Zones table), not from the finding itself. Cross-reference the finding's `component` value against the Phase 1 trust zone assignments to resolve the correct zone. For example, if Phase 1 assigned `"API Gateway"` to the `"DMZ"` trust zone, then `fullyQualifiedName` is `"DMZ/API Gateway"`.
- `kind`: Map the finding's `dfd_element_type` to lowercase-hyphenated custom values:
  - `External Entity` → `external-entity`
  - `Process` → `process`
  - `Data Store` → `data-store`
  - `Data Flow` → `data-flow`

**Note**: `logicalLocations` is not displayed by GitHub Code Scanning but is rendered by VS Code SARIF Viewer (component tree navigation) and Azure DevOps (logical grouping in security reports). Include it on every result regardless of the target consumer.

**Example — result with both physicalLocation and logicalLocations**:

```json
{
  "locations": [
    {
      "physicalLocation": {
        "artifactLocation": {
          "uri": "architecture/input.md"
        },
        "region": {
          "startLine": 1
        }
      },
      "logicalLocations": [
        {
          "name": "User Database",
          "fullyQualifiedName": "Internal/User Database",
          "kind": "data-store"
        }
      ]
    }
  ]
}
```

## Fingerprint Computation

Every SARIF result MUST include a `partialFingerprints` object with deterministic values that enable GitHub Code Scanning to track findings across runs. **Same inputs MUST produce same outputs** — given identical `ruleId` and `component_name` values, the fingerprint output must be identical across separate invocations.

**1. `primaryLocationLineHash`** — the key GitHub uses for alert deduplication:

- Concatenate `ruleId` and `component_name` with a pipe separator: `"{ruleId}|{component_name}"`
  - Example: `"tachi/stride/spoofing|API Gateway"`
- Compute the SHA-256 hash of the concatenated string
- Truncate to the first **16 hex characters** of the hash digest
- This value MUST be deterministic and stable: produce a consistent hash value. Given the same `ruleId` and `component_name` inputs, the hash output must be identical across separate invocations. If two findings share the same category and component, they will share the same `primaryLocationLineHash` — this is intentional for GitHub dedup behavior.

**2. `findingId/v1`** — cross-reference to `threats.md`:

- Set to the finding IR `id` value (e.g., `"S-1"`, `"AG-2"`, `"T-4"`)
- This enables users to navigate from a SARIF alert back to the corresponding finding in the `threats.md` output

**3. `correlationGroup`** (conditional) — only for correlated findings:

- Only present if the finding is the **primary member** of a correlation group (see Correlated Finding Mapping above)
- Set to the correlation group identifier (e.g., `"CG-1"`)
- Do NOT include this key for uncorrelated findings or for correlated peers (peers are not top-level results)

**Example — partialFingerprints with all three keys (correlated primary finding)**:

```json
{
  "partialFingerprints": {
    "primaryLocationLineHash": "a1b2c3d4e5f67890",
    "findingId/v1": "S-1",
    "correlationGroup": "CG-1"
  }
}
```

**Example — partialFingerprints for an uncorrelated finding (no correlationGroup)**:

```json
{
  "partialFingerprints": {
    "primaryLocationLineHash": "f0e9d8c7b6a54321",
    "findingId/v1": "AG-1"
  }
}
```

**4. `baselineRunId`** (conditional — baseline-aware mode only):

- Only present when the pipeline ran with a baseline (`baseline.present == true`).
- Set to the `baseline.run_id` from the pipeline's Phase 0 metadata (e.g., `"2026-03-25T12-53-57"`).
- For `NEW` findings (not in baseline): set to an empty string `""`.
- For `UNCHANGED`, `UPDATED`, `RESOLVED` findings: set to the baseline run_id that originally discovered or last assessed this finding.
- When no baseline is present (first run): omit this key entirely from `partialFingerprints`.

**Baseline-aware result properties**:

When the pipeline operates in baseline-aware mode, each SARIF result MUST include a `baselineState` property in its `properties` object:

| `baselineState` Value | Maps From | SARIF Convention | Description |
|----------------------|-----------|------------------|-------------|
| `new` | `delta_status: NEW` | New finding | Discovered this run, not present in baseline |
| `unchanged` | `delta_status: UNCHANGED` | Unchanged | Identical to baseline — same component, threat, context |
| `updated` | `delta_status: UPDATED` | Updated | Same finding but context changed (re-scored) |
| `absent` | `delta_status: RESOLVED` | Absent from current run | No longer applicable — component removed or threat eliminated |

**Note on SARIF convention**: SARIF 2.1.0 uses `"absent"` where tachi uses `"RESOLVED"`. The mapping is: `RESOLVED` → `absent` in SARIF output. This aligns with the SARIF specification's `baselineState` enum values (`new`, `unchanged`, `updated`, `absent`).

When no baseline is present, set `baselineState` to `"new"` for all findings.

**Example — partialFingerprints with baseline fields (UNCHANGED finding)**:

```json
{
  "partialFingerprints": {
    "primaryLocationLineHash": "a1b2c3d4e5f67890",
    "findingId/v1": "S-1",
    "baselineRunId": "2026-03-25T12-53-57"
  },
  "properties": {
    "baselineState": "unchanged"
  }
}
```

**Determinism note**: The `primaryLocationLineHash` is the primary mechanism GitHub Code Scanning uses to match alerts across runs. If the hash changes for the same finding, GitHub will close the old alert and open a new one, losing comment history and triage state. Treat hash stability as a correctness requirement.

## SARIF Taxonomies

This section is **enabled by default** — every generated `threats.sarif` file MUST include taxonomy declarations and rule-to-taxonomy relationships as described below.

Taxonomies enrich findings with references to industry-standard frameworks (OWASP Top 10 and CWE), enabling SARIF viewers to cross-reference threats against established vulnerability catalogs. While GitHub Code Scanning does not display taxonomy data, viewers such as Azure DevOps, VS Code SARIF Viewer, and SARIF Explorer surface taxonomy relationships in their UI.

**Step 1 — Declare taxonomy frameworks in `run.taxonomies[]`**

Add a `taxonomies` array to the `runs[0]` object. Each entry is a `toolComponent` object representing an external taxonomy framework. Declare exactly two entries:

```json
{
  "taxonomies": [
    {
      "name": "OWASP",
      "version": "2021",
      "informationUri": "https://owasp.org/Top10/",
      "organization": "OWASP Foundation",
      "shortDescription": {
        "text": "OWASP Top 10 Web Application Security Risks"
      }
    },
    {
      "name": "CWE",
      "version": "4.13",
      "informationUri": "https://cwe.mitre.org/",
      "organization": "MITRE",
      "shortDescription": {
        "text": "Common Weakness Enumeration"
      }
    }
  ]
}
```

**Step 2 — Register supported taxonomies in `tool.driver.supportedTaxonomies[]`**

Add a `supportedTaxonomies` array to the `tool.driver` object. Each entry references a declared taxonomy by name and index position in the `run.taxonomies[]` array:

```json
{
  "tool": {
    "driver": {
      "name": "Tachi",
      "supportedTaxonomies": [
        { "name": "OWASP", "index": 0 },
        { "name": "CWE", "index": 1 }
      ]
    }
  }
}
```

**Step 3 — Add `relationships[]` to each rule (reportingDescriptor)**

For each `reportingDescriptor` in `tool.driver.rules[]`, add a `relationships` array that maps the rule to its corresponding OWASP and CWE taxonomy entries. Each relationship object contains:

- `target.id` — the taxonomy entry identifier (e.g., `"A07"` for OWASP, `"CWE-287"` for CWE)
- `target.toolComponent.name` — the taxonomy name (`"OWASP"` or `"CWE"`)
- `kinds` — set to `["relevant"]` to indicate the relationship type

Use the following mapping table to determine the correct taxonomy entries for each STRIDE and AI threat category:

| Category               | OWASP Target ID | CWE Target ID | Notes                                                        |
|------------------------|-----------------|---------------|--------------------------------------------------------------|
| Spoofing               | A07             | CWE-287       | Identification and Authentication Failures / Improper Authentication |
| Tampering              | A08             | CWE-345       | Software and Data Integrity Failures / Insufficient Verification of Data Authenticity |
| Repudiation            | A09             | CWE-778       | Security Logging and Monitoring Failures / Insufficient Logging |
| Information Disclosure | A01             | CWE-200       | Broken Access Control / Exposure of Sensitive Information     |
| Denial of Service      | A05             | CWE-400       | Security Misconfiguration / Uncontrolled Resource Consumption |
| Elevation of Privilege | A01             | CWE-269       | Broken Access Control / Improper Privilege Management         |
| Agentic Threats        | —               | CWE-693       | No direct OWASP Top 10 mapping; CWE-693 Protection Mechanism Failure |
| LLM Threats            | —               | CWE-74        | No direct OWASP Top 10 mapping; CWE-74 Improper Neutralization of Special Elements in Output. Reference OWASP LLM Top 10 in the rule `help.markdown` field when applicable |

For categories with an OWASP mapping, include two relationship entries (one OWASP, one CWE). For categories without an OWASP mapping (Agentic Threats, LLM Threats), include only the CWE relationship entry.

**Example — rule with both OWASP and CWE relationships (Spoofing)**:

```json
{
  "id": "tachi/stride/spoofing",
  "shortDescription": {
    "text": "Identity spoofing threats"
  },
  "relationships": [
    {
      "target": {
        "id": "A07",
        "toolComponent": { "name": "OWASP" }
      },
      "kinds": ["relevant"]
    },
    {
      "target": {
        "id": "CWE-287",
        "toolComponent": { "name": "CWE" }
      },
      "kinds": ["relevant"]
    }
  ]
}
```

**Example — rule with CWE-only relationship (Agentic Threats)**:

```json
{
  "id": "tachi/ai/agentic-threats",
  "shortDescription": {
    "text": "AI agent autonomy and misuse threats"
  },
  "relationships": [
    {
      "target": {
        "id": "CWE-693",
        "toolComponent": { "name": "CWE" }
      },
      "kinds": ["relevant"]
    }
  ]
}
```

## SARIF Schema Compliance Structure

The generated `threats.sarif` file MUST use this exact top-level JSON structure conforming to SARIF 2.1.0:

```json
{
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json",
  "version": "2.1.0",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "Tachi",
          "semanticVersion": "<schema_version from output.yaml>",
          "informationUri": "<repository URL>",
          "rules": [
            // One reportingDescriptor per active threat category
          ]
        }
      },
      "results": [
        // One result per finding (after deduplication)
      ]
    }
  ]
}
```

**Structural requirements**:
- The file MUST contain exactly one `runs` entry (single run per invocation)
- `$schema` MUST use the exact OASIS URI shown above
- `version` MUST be `"2.1.0"`
- `results` array contains one entry per finding after deduplication — correlated peers do NOT appear as separate top-level results
- Empty findings: If the threat model produces zero findings, `results` is an empty array `[]` and `rules` is an empty array `[]`

See `../../../templates/tachi/output-schemas/threats.sarif` for a complete structural reference with example values.

## JSON Structural Self-Check

Before writing the `threats.sarif` file, run the following validation checklist. If any check fails, correct the issue before producing the output.

- [ ] **Required properties**: The JSON contains `$schema`, `version`, `runs` at the top level, and `tool`, `results` within `runs[0]`.
- [ ] **Result completeness**: Every result has `ruleId`, `message.text`, `level`, `locations[]` (with both `physicalLocation` and `logicalLocations`), and `partialFingerprints`.
- [ ] **Rule-result consistency**: Every `ruleId` referenced by a result has a corresponding entry in `tool.driver.rules[]`. No orphan rule IDs.
- [ ] **Security-severity format**: Every `security-severity` value in `tool.driver.rules[].properties` is a numeric string (e.g., `"8.0"`) matching the Severity Mapping Table values.
- [ ] **MAESTRO layer properties**: Every result has `"maestro-layer"` in `properties` (full layer name or "Unclassified") and a `"maestro-layer:{layer-id}"` entry in `properties.tags[]`.
- [ ] **Result count**: The number of top-level results equals the expected deduplicated finding count. If the STRIDE and AI tables contain N findings after deduplication, the `results` array MUST contain exactly N entries.

If any check fails, correct the error before proceeding. Do not produce a `threats.sarif` file that fails any of these structural checks.

After the self-check passes, write the `threats.sarif` file to the output directory alongside `threats.md`.

---

## Fingerprint Preservation Rules

When the orchestrator generates SARIF output, fingerprint fields serve dual purposes: enabling SARIF consumers (GitHub Code Scanning) to track alerts across uploads, and enabling the orchestrator's own baseline correlation pipeline to match findings across runs. The fingerprint values written to SARIF MUST be consistent with the baseline fingerprint registry (Phase 0) so that a SARIF file from one run can serve as a correlation source for the next.

### Field Roles

| Fingerprint Field | SARIF Path | Role | Stability Requirement |
|-------------------|------------|------|----------------------|
| `findingId/v1` | `result.partialFingerprints["findingId/v1"]` | **Primary correlation key** for matching findings across runs | Must be preserved exactly as assigned in Phase 3 (e.g., "S-1", "AG-2"). Never regenerate or renumber during SARIF generation. |
| `primaryLocationLineHash` | `result.partialFingerprints["primaryLocationLineHash"]` | **Validation signal** confirming correlation correctness | Must be computed identically to the Fingerprint Computation rules above. Same ruleId + component_name inputs must produce the same hash across all invocations. |
| `correlationGroup` | `result.partialFingerprints["correlationGroup"]` | **Correlation group identifier** linking related findings | Must match the correlation group ID from the Correlation Detection phase (e.g., "CG-1"). Only present on the primary finding of each group. |

### Preservation Rules

1. **`findingId/v1` is authoritative**: The `findingId/v1` is the primary key the baseline pipeline uses to match findings between runs. If a finding's `findingId/v1` changes between runs (e.g., due to renumbering), the baseline pipeline will classify the old ID as RESOLVED and the new ID as NEW, losing correlation history. During SARIF generation, copy the finding ID exactly as it was assigned in Phase 3 -- do not reassign, renumber, or reformat.

2. **`primaryLocationLineHash` is a validation signal, not a discriminator**: Two findings with the same `findingId/v1` but different `primaryLocationLineHash` values should be flagged for manual review but still correlated (per architect review). The hash confirms a match is correct but does not override `findingId/v1` as the primary key. This means:
   - The hash MUST be computed deterministically using the same algorithm every time (SHA-256 of `"{ruleId}|{component_name}"`, truncated to 16 hex characters).
   - If a component is renamed between runs, the hash will change. The baseline pipeline detects this via the rename/refactor detection rules in Phase 1a, not via hash comparison.
   - If two findings share the same category and component (same hash), they are distinguished by `findingId/v1`.

3. **`correlationGroup` is conditional and primary-only**: The `correlationGroup` field is only present on the primary finding of each correlation group. Correlated peers do not appear as top-level SARIF results (they are in `relatedLocations[]`), so they have no `correlationGroup` field. When reading a SARIF file as baseline input, the presence of `correlationGroup` indicates the result represents a group of related findings, and `relatedLocations[]` enumerates the peers.

4. **`baselineRunId` bridges runs**: When the pipeline operates in baseline-aware mode, the `baselineRunId` field in `partialFingerprints` records which run originally discovered or last assessed each finding. This field enables downstream consumers to trace finding provenance across multiple runs. See the `baselineRunId` rules in the Fingerprint Computation section above for value assignment per delta status.

### Cross-Run Consistency Guarantee

Given the same architecture input and the same finding set, the orchestrator MUST produce identical fingerprint values in the SARIF output. This guarantee enables:

- **GitHub Code Scanning**: Stable alert tracking across uploads. Changing fingerprints causes GitHub to close old alerts and open new ones, losing triage state and comments.
- **Baseline correlation**: The next pipeline run reads the SARIF file (or the co-produced `threats.md`) and uses `findingId/v1` as the primary correlation key. Unstable IDs break the entire baseline-aware pipeline.
- **Downstream scoring**: The risk-scorer and compensating-controls agents consume `threats.md` findings by ID. If SARIF and `threats.md` disagree on finding IDs, cross-format traceability is broken.

---

## Taxonomy Passthrough Rules

When the orchestrator generates SARIF output, taxonomy references from the finding IR (OWASP, CWE, MITRE identifiers in the `references` field) must be passed through into the SARIF taxonomy structures. This ensures that findings carry their framework references into SARIF viewers that display taxonomy data (Azure DevOps, VS Code SARIF Viewer, SARIF Explorer).

### Passthrough Pipeline

```
Finding IR `references` field
    ↓
Rule `help.markdown` (inline text references)
    ↓
Rule `properties.tags` (searchable tags)
    ↓
Rule `relationships[]` (structured taxonomy links)
    ↓
`run.taxonomies[]` (framework declarations)
```

Each finding's framework references flow through four SARIF structures. The orchestrator MUST ensure consistency across all four levels.

### Rule 1: All referenced frameworks must be declared in `run.taxonomies[]`

Every taxonomy framework referenced by any rule's `relationships[]` MUST have a corresponding entry in `run.taxonomies[]`. The two standard taxonomies (OWASP and CWE) are always declared. If a finding references an additional framework (e.g., MITRE ATLAS for agentic threats), it is referenced in `help.markdown` and `tags` but does NOT require a `run.taxonomies[]` entry unless a formal `relationships[]` link is created.

### Rule 2: `relationships[]` entries must use the canonical mapping

The SARIF Taxonomies section above defines the canonical mapping from each threat category to its OWASP and CWE taxonomy entries. When generating `relationships[]` for a rule:

- Use the `target.id` values from the canonical mapping table (e.g., `"A07"` for Spoofing, `"CWE-287"` for Spoofing).
- Do NOT substitute finding-specific OWASP or CWE references that differ from the canonical mapping. The canonical mapping represents the category-level relationship; finding-specific references belong in `help.markdown`.
- For categories without an OWASP Top 10 mapping (Agentic Threats, LLM Threats), include only the CWE relationship entry. Reference the relevant OWASP initiative (e.g., OWASP Agentic Security Initiative, OWASP LLM Top 10) in `help.markdown` instead.

### Rule 3: `help.markdown` carries finding-specific references

The `help.markdown` field on each rule is the appropriate location for finding-specific framework references that go beyond the canonical category-level mapping. For example:

- A specific spoofing finding might reference CWE-290 (Authentication Bypass by Spoofing) in addition to the canonical CWE-287. This specific reference belongs in `help.markdown`, not in `relationships[]`.
- An LLM threat finding might reference OWASP LLM01:2025 (Prompt Injection). Since there is no formal OWASP Top 10 taxonomy entry for LLM threats, this reference belongs in `help.markdown`.

### Rule 4: `properties.tags` must include framework identifiers

Each rule's `tags` array must include searchable identifiers for all referenced frameworks. At minimum:

- `"security"` (always first)
- Category family: `"stride"` or `"ai"`
- Category name: e.g., `"spoofing"`, `"tampering"`, `"agentic"`
- Framework identifiers: `"owasp"`, `"cwe"`, and any additional identifiers relevant to the category (e.g., `"authentication"`, `"data-integrity"`)

Tags enable SARIF viewers and security dashboards to filter findings by framework. Maximum 20 tags per rule.

### Rule 5: Taxonomy index references must be stable

The `target.toolComponent.name` in `relationships[]` references the taxonomy by name (e.g., `"OWASP"`, `"CWE"`). The `supportedTaxonomies[]` array in `tool.driver` references taxonomies by name and index position. The index positions MUST remain stable:

| Index | Taxonomy Name |
|-------|---------------|
| 0 | OWASP |
| 1 | CWE |

If additional taxonomies are added in future versions, they MUST be appended (index 2, 3, etc.) -- never inserted before existing entries. Reordering would break `index` references in existing SARIF files used as baselines.
