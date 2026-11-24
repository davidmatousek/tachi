---
source_agent: orchestrator.md
loaded_at: Phase 4 completion (SARIF output generation)
extracted_from: SARIF Output Generation section lines 1224-1718
version: "1.0"
---

> **Status (F-374).** This guide no longer tells any agent to author `risk-scores.sarif` or `compensating-controls.sarif`. Shipped renderers write both (`scripts/render-risk-scores.py` and `scripts/render-compensating-controls.py`), through the shared emitter, `scripts/sarif_common.py`.
>
> - **If you are the risk scorer or the control analyzer, you write no SARIF.** Nothing in this guide changes that, and the sections about `threats.sarif` are not yours. "Renderer-Owned SARIF Files", at the end, documents what the renderers write.
> - **`.claude/skills/tachi-shared/references/sarif-identity-shared.md` is the one contract** for identity (tools, categories, rule IDs, `primaryLocationLineHash`, `artifactLocation.uri`) and for membership (one result for each open finding) in all three SARIF files. Where this guide and that reference differ, the reference governs.
> - **The sections down to "Renderer-Owned SARIF Files" describe `threats.sarif`**, the one SARIF file that an agent still writes: the orchestrator writes it until the shipped generator takes it over. Their identity and membership text ("Correlated Finding Mapping", "Fingerprint Computation" and the result counts) is that file's legacy rule, which `sarif-specification.md` keeps in force until then. The shared reference replaces it when the generator ships.

### SARIF Output Generation

After the `threats.md` output is structurally validated, produce a `threats.sarif` file in the same output directory. The SARIF file contains the same findings in SARIF 2.1.0 format for integration with GitHub Code Scanning, VS Code SARIF Viewer, Azure DevOps, and other SARIF-compatible security tools.

Phase 4 already has all finding data from Phase 3. The SARIF generation step transforms that data into a JSON file — no additional analysis or agent invocation is needed. Follow the instructions below to produce the `threats.sarif` file.

#### Category to Rule ID Mapping Table

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

#### Severity Mapping Table

Map each finding's `risk_level` to SARIF severity using this CVSS alignment table. The `security-severity` value MUST be a numeric string (e.g., `"8.0"`, not `8.0`) for GitHub Code Scanning compatibility.

| Tachi Risk Level | SARIF `level` | `security-severity` (numeric string) | GitHub Display |
|-----------------|---------------|--------------------------------------|----------------|
| Critical | `error` | `"9.0"` | Critical |
| High | `error` | `"8.0"` | High |
| Medium | `warning` | `"5.0"` | Medium |
| Low | `note` | `"2.0"` | Low |
| Note | `note` | `"0.1"` | Low (informational) |

**Note-level mapping**: The Note level maps to `note`/`"0.1"` (not `none`/`"0.0"`) to keep informational findings visible in GitHub Code Scanning within the Low severity band. A value of `"0.0"` would cause GitHub to hide the finding entirely.

#### SARIF Tool Metadata

Populate the `tool.driver` object at the top of the SARIF file with the following fields:

- `name`: `"Tachi"`
- `semanticVersion`: Use the `schema_version` value from `../../../schemas/output.yaml` (currently `"1.1"`)
- `informationUri`: Use the repository URL (e.g., `"https://github.com/{owner}/{repo}"`)
- `rules`: An array of `reportingDescriptor` objects — one per threat category that produced findings in the current run. See Rule Definition Templates below.

#### Rule Definition Templates

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

#### Finding IR to SARIF Result Mapping

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
| Input file | `result.locations[].physicalLocation.artifactLocation.uri` | Architecture input file path |
| (fixed) | `result.locations[].physicalLocation.region.startLine` | Always `1` |

#### Correlated Finding Mapping

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

#### Dual-Location Instructions

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

#### Fingerprint Computation

> **`threats.sarif` only, and only until the generator ships.** `risk-scores.sarif` and `compensating-controls.sarif` don't use this recipe. Their renderers write tachi's own hash, `sha256("tachi-plh/1|" + tool + "|" + id)` (first 16 hex digits, then `:1`), so no two results in those files share a hash, and `findingId/v1` is only a cross-reference to `threats.md`. The shared reference replaces this section, and its claim below that a shared hash is intentional, when the generator takes `threats.sarif` over.

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

**Determinism note**: The `primaryLocationLineHash` is the primary mechanism GitHub Code Scanning uses to match alerts across runs. If the hash changes for the same finding, GitHub will close the old alert and open a new one, losing comment history and triage state. Treat hash stability as a correctness requirement.

#### SARIF Taxonomies (P1 Enhancement)

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

#### SARIF Schema Compliance Structure

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

#### JSON Structural Self-Check

Before writing the `threats.sarif` file, run the following validation checklist. If any check fails, correct the issue before producing the output.

- [ ] **Required properties**: The JSON contains `$schema`, `version`, `runs` at the top level, and `tool`, `results` within `runs[0]`.
- [ ] **Result completeness**: Every result has `ruleId`, `message.text`, `level`, `locations[]` (with both `physicalLocation` and `logicalLocations`), and `partialFingerprints`.
- [ ] **Rule-result consistency**: Every `ruleId` referenced by a result has a corresponding entry in `tool.driver.rules[]`. No orphan rule IDs.
- [ ] **Security-severity format**: Every `security-severity` value in `tool.driver.rules[].properties` is a numeric string (e.g., `"8.0"`) matching the Severity Mapping Table values.
- [ ] **Result count**: The number of top-level results equals the expected deduplicated finding count. If the STRIDE and AI tables contain N findings after deduplication, the `results` array MUST contain exactly N entries.

If any check fails, correct the error before proceeding. Do not produce a `threats.sarif` file that fails any of these structural checks.

After the self-check passes, write the `threats.sarif` file to the output directory alongside `threats.md`.

---

### Renderer-Owned SARIF Files

`risk-scores.sarif` and `compensating-controls.sarif` are written by the shipped renderers (`scripts/render-risk-scores.py` and `scripts/render-compensating-controls.py`) through the shared emitter (`scripts/sarif_common.py`). No agent authors either file. The risk scorer and the control analyzer supply judgment in part files, the renderer computes every value in the files it writes, and each markdown file and its SARIF agree by construction. This section records how the two files differ from `threats.sarif`. `sarif-identity-shared.md` has the identity and membership rules for all three.

#### Semantic Shift: `security-severity`

The meaning of `security-severity` differs between the three SARIF files:

| Property | `threats.sarif` | `risk-scores.sarif` | `compensating-controls.sarif` |
|----------|----------------|---------------------|-------------------------------|
| **Rule-level** `security-severity` | Static category-level value from the Severity Mapping Table (e.g., `"8.0"` for all High findings in a category) | **MAX composite score** among that rule's findings (e.g., `"8.4"` if the highest-scored spoofing finding has composite 8.4) | **MAX residual score** among that rule's findings |
| **Result-level** `security-severity` | Not present (severity lives only on the rule) | **Per-finding composite score** as a numeric string (e.g., `"7.8"`) — each finding gets its own calculated value | **Per-finding residual score** as a numeric string: the composite score after the control's reduction |

This shift enables GitHub Code Scanning to display granular, per-finding severity rather than flat category-level severity, allowing differentiation between findings that previously shared the same rating.

#### Extended Property Bag Schema

Each result in `risk-scores.sarif` includes these properties in its `properties` object, in this order. The renderer writes them, from the values it computed for the finding. A result with a correction or a tag-driven change also carries `score-corrections` after `score-flags`, objects `{field, from, to, cause}`:

```json
{
  "properties": {
    "security-severity": "<composite-score-as-numeric-string>",
    "cvss-base-score": "<0.0-10.0 as string>",
    "cvss-vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N",
    "exploitability": "<0.0-10.0 as string>",
    "scalability": "<0.0-10.0 as string>",
    "reachability": "<0.0-10.0 as string>",
    "composite-weights": "0.35/0.30/0.15/0.20",
    "score-source": "<inherited|fresh>",
    "score-flags": [],
    "severity-band": "<Critical|High|Medium|Low>",
    "risk-owner": "Unassigned",
    "remediation-sla": "<24h|7d|30d|90d>",
    "risk-disposition": "<Mitigate|Review>",
    "review-date": "<YYYY-MM-DD>",
    "maestro-layer": "<layer name or Unclassified>",
    "affected_assets": []
  }
}
```

| Property | Type | Description |
|----------|------|-------------|
| `security-severity` | numeric string | Composite risk score (weighted sum of four dimensions). Replaces the static category value from `threats.sarif`. |
| `cvss-base-score` | numeric string | CVSS 3.1 base score (0.0-10.0) |
| `cvss-vector` | string, or `null` | Full CVSS 3.1 vector string for auditability. `null` when a carried finding has no vector to verify |
| `exploitability` | numeric string | Exploitability assessment (0.0-10.0) |
| `scalability` | numeric string | Scalability assessment (0.0-10.0) |
| `reachability` | numeric string | Reachability assessment (0.0-10.0), derived from trust zone placement |
| `composite-weights` | string | Weight allocation used: `"cvss/exploitability/scalability/reachability"` |
| `score-source` | string | `inherited` when the finding's inputs were carried from a baseline, `fresh` when they were scored in this run |
| `score-flags` | array | Sorted `kind:field:cause` strings for the finding's integrity flags. Always present, and empty when nothing is flagged |
| `severity-band` | string | Severity classification mapped from composite: Critical (9.0-10.0), High (7.0-8.9), Medium (4.0-6.9), Low (0.0-3.9) |
| `risk-owner` | string | Remediation owner. Default: `"Unassigned"`, and a baseline's owner is carried forward |
| `remediation-sla` | string | Severity-driven deadline: Critical=24h, High=7d, Medium=30d, Low=90d |
| `risk-disposition` | string | Risk treatment decision: Critical/High=Mitigate, Medium/Low=Review |
| `review-date` | string | ISO 8601 date: scoring date + SLA duration |
| `maestro-layer` | string | The finding's MAESTRO layer, or `Unclassified` |
| `affected_assets` | array | The asset-sensitivity tags the asset-modifier step used for the finding. Emitting it changes no score |

`compensating-controls.sarif` carries the same `maestro-layer` property on every result, with these control properties beside it: `control-status`, `control-evidence`, `control-effectiveness`, `inherent-risk`, `residual-risk`, `recommendation` and `effort-estimate`, and `integrity-flags`, a sorted array of `kind:field:cause` strings that is always present. The renderer takes `recommendation` and `effort-estimate` from the finding's Section 4 block, so the two files agree. `templates/tachi/output-schemas/compensating-controls.sarif` lists the whole property bag.

#### The Result Message

Every result's `message` carries `text`, and the renderer always writes `markdown` beside it, the empty string included. A finding with no mitigation text keeps the key with an empty value, and no result drops it. In `risk-scores.sarif`, `markdown` is the finding's mitigation text.

#### Identity and Membership

Neither renderer-owned file copies a fingerprint from an upstream file. The renderer computes every key, and `sarif-identity-shared.md` has the recipes and the test vectors.

- **`primaryLocationLineHash`** is tachi's own hash on every result: `sha256("tachi-plh/1|" + tool + "|" + id)`, the first 16 hex digits, then `:1`. `tool` is the file's own driver name and `id` is the canonical finding ID, so the three files never share a hash, and no two results in one file do.
- **`partialFingerprints`** holds exactly two keys, `primaryLocationLineHash` and `findingId/v1`. `findingId/v1` is a cross-reference to `threats.md`, not a key. A correlation group is recorded in the result's `properties` (`correlation-group`, `correlation-role` and `correlation-primary`), and never in `partialFingerprints`.
- **`artifactLocation.uri`** is the user's architecture file, set by one shared resolver, so it is the same on every result of a run chain. A score, a rationale, a regroup or a re-run changes no key.
- **Membership.** Each file has one result for each open finding, correlated peers included, and a RESOLVED finding appears nowhere. The number of results is the number of open findings.

#### Taxonomies

Each renderer-owned file declares its taxonomies itself, from the shared emitter's own list (`sarif_common.TAXONOMIES`, which a test keeps equal to the catalogs): `run.taxonomies[]`, `tool.driver.supportedTaxonomies[]` and the rules' `relationships[]`. It never copies them from an upstream file.

#### Tool Metadata Differences

| Field | `threats.sarif` | `risk-scores.sarif` | `compensating-controls.sarif` |
|-------|----------------|---------------------|-------------------------------|
| `tool.driver.name` | `"Tachi"` | `"tachi-risk-scorer"` | `"tachi-control-analyzer"` |
| Recommended upload `category` | `threat-model` | `risk-score` | `compensating-controls` |

The tool name is verbatim: the threats tool has a capital T. Each name is an input to every alert's hash, and the three differ on purpose.

#### SARIF Supersession

No SARIF file supersedes another. `risk-scores.sarif` does not supersede `threats.sarif`, and `compensating-controls.sarif` does not supersede `risk-scores.sarif`: the three files carry different tool names and upload under different categories, and the tool and the category are part of an alert's key. Each file therefore keeps its own alerts, and uploading one never updates or closes another's. Upload each file under its own category, and use the per-finding `security-severity` shift above for granular severity display in the GitHub Security tab. An earlier version of this guide said that a later file supersedes an earlier one because fingerprints are preserved. That stopped being true when each file took its own tool name and tachi's own hash (ADR-050 D7).
