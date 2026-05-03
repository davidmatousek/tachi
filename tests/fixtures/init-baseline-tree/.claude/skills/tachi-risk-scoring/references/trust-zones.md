---
source_agent: risk-scorer
extracted_from: .claude/agents/tachi/risk-scorer.md
version: 1.0.0
---

# Trust Zone Extraction Reference

Extract trust zone data from `threats.md` Section 2 to build a component-to-zone mapping dictionary. This mapping is consumed by the Reachability Analysis phase (Section 6) to derive architecture-aware reachability scores per finding.

## Input Source

Trust zone data lives in `threats.md` under the `## 2. Trust Boundaries` heading, within the `### Trust Zones` subsection. The canonical table structure is defined in `templates/tachi/output-schemas/threats.md`.

## 2a. Locating the Trust Zone Table

**Step 1 -- Find Section 2**: Scan for a markdown heading matching `## 2. Trust Boundaries` (case-insensitive). If no Section 2 heading is found, skip to the Fallback Behavior rules below.

**Step 2 -- Find the Trust Zones subsection**: Within Section 2, locate the `### Trust Zones` subheading. The trust zone table immediately follows this subheading (after any optional descriptive paragraph).

**Step 3 -- Identify the table**: The trust zone table has exactly three columns:

| Column | Description |
|--------|-------------|
| Zone | Zone name (e.g., "External Zone", "User Zone", "DMZ", "Public Internet") |
| Trust Level | Classification: `Untrusted`, `Semi-Trusted`, or `Trusted` |
| Components | Comma-separated list of component names assigned to this zone |

The table header row MUST contain "Zone", "Trust Level", and "Components" (case-insensitive match). If a table is found under Section 2 but does not match this three-column structure, treat it as a malformed table (see Error Handling below).

## 2b. Parsing Table Rows

For each data row (after the header and separator rows), extract:

| Field | Extraction Rule |
|-------|-----------------|
| `zone_name` | Trim whitespace from the Zone column value |
| `trust_level` | Normalize the Trust Level column value (see Trust Level Normalization below) |
| `components` | Split the Components column on commas, trim whitespace from each component name |

**Example input row**:

```
| Application Zone | Semi-Trusted | Guardrails Service, LLM Agent Orchestrator, MCP Tool Server |
```

**Extracted fields**:
- `zone_name`: `Application Zone`
- `trust_level`: `Semi-Trusted`
- `components`: `["Guardrails Service", "LLM Agent Orchestrator", "MCP Tool Server"]`

## 2c. Trust Level Normalization

The Trust Level column value MUST be normalized to one of exactly three canonical values: `Untrusted`, `Semi-Trusted`, or `Trusted`. Real-world `threats.md` files exhibit capitalization and phrasing variations. Apply the following normalization rules in order:

**Step 1 -- Case-insensitive match against canonical values**:
- `untrusted` (any case) → `Untrusted`
- `semi-trusted` or `semi trusted` (any case, with or without hyphen) → `Semi-Trusted`
- `trusted` (any case, but NOT matching "untrusted" or "semi-trusted") → `Trusted`

**Step 2 -- Keyword-based classification for non-standard phrasing**:

If Step 1 does not produce a match, classify by scanning for keywords (case-insensitive):

| Keywords Present | Normalized Trust Level |
|------------------|----------------------|
| "untrust", "external", "public", "internet", "unauth" | `Untrusted` |
| "semi", "dmz", "perimeter", "gateway", "partial" | `Semi-Trusted` |
| "trust", "internal", "private", "backend", "core" | `Trusted` |

**Keyword precedence**: If multiple keywords match across categories, apply the most restrictive (lowest trust) level. "Semi" keywords take precedence over "Trusted" keywords; "Untrusted" keywords take precedence over all others.

**Step 3 -- Unresolvable trust level**: If neither Step 1 nor Step 2 produces a classification, default to `Semi-Trusted` and emit a warning: `"Trust level '{original_value}' for zone '{zone_name}' could not be classified; defaulting to Semi-Trusted"`.

## 2d. Zone Name Normalization

Zone names are stored as-is from the table (preserving the original author's naming) but are matched case-insensitively when performing component lookups. No renaming or canonicalization is applied to zone names.

**Observed zone name variations** (from the tachi example corpus):
- `External Zone`, `User Zone`, `Public Internet`, `External Clients`, `External Services`
- `DMZ`, `Application Zone`, `Internal Services Zone`
- `Internal Zone`, `Internal Network`, `Internal Services`

## 2e. Component-to-Zone Mapping Dictionary

Build a dictionary mapping each component name to its zone and trust level. This is the primary output of the Trust Zone Extraction phase.

**Dictionary structure**:

```
component_zone_map = {
    "<component_name>": {
        "zone": "<zone_name>",
        "trust_level": "<Untrusted|Semi-Trusted|Trusted>"
    },
    ...
}
```

**Construction rules**:

1. For each parsed table row, iterate over the extracted `components` list
2. For each component, add an entry to the dictionary with the component name as key (trimmed, preserving original case)
3. Component lookup at scoring time is **case-insensitive** -- when the Reachability Analysis phase (Section 6) queries this dictionary, it compares component names using case-insensitive matching
4. If a component appears in multiple zones (duplicate assignment), use the **first occurrence** and emit a warning: `"Component '{component_name}' appears in multiple zones; using first assignment: '{zone_name}' ({trust_level})"`

**Example output** (from `examples/agentic-app/sample-report/threats.md`):

```
component_zone_map = {
    "User": {
        "zone": "User Zone",
        "trust_level": "Untrusted"
    },
    "Guardrails Service": {
        "zone": "Application Zone",
        "trust_level": "Semi-Trusted"
    },
    "LLM Agent Orchestrator": {
        "zone": "Application Zone",
        "trust_level": "Semi-Trusted"
    },
    "MCP Tool Server": {
        "zone": "Application Zone",
        "trust_level": "Semi-Trusted"
    },
    "Knowledge Base": {
        "zone": "Application Zone",
        "trust_level": "Semi-Trusted"
    },
    "Audit Logger": {
        "zone": "Application Zone",
        "trust_level": "Semi-Trusted"
    },
    "External API": {
        "zone": "External Services",
        "trust_level": "Untrusted"
    }
}
```

## 2f. Cross-Reference with Section 1 Components

After building the `component_zone_map`, cross-reference it against the Components table parsed from Section 1 (System Overview) during Threat Parsing (Section 1a):

1. For each component in the Section 1 Components table, check whether it exists in `component_zone_map`
2. If a Section 1 component is **not found** in any trust zone, assign it a default zone entry: `{ "zone": "Unassigned", "trust_level": "Semi-Trusted" }` and emit a warning: `"Component '{component_name}' from Section 1 has no trust zone assignment; defaulting to Semi-Trusted"`
3. If a trust zone table component is **not found** in the Section 1 Components table, retain it in the mapping (trust zone assignments are authoritative for reachability scoring regardless of Section 1 coverage)

This cross-reference ensures that every component referenced by a finding has a trust level available for reachability scoring, even when the trust zone table does not cover all components.

## 2g. Fallback Behavior

When no trust zone data is available, the Reachability Analysis phase (Section 6) cannot derive zone-based scores. The following fallback cascade applies:

1. **No Section 2 heading**: If `threats.md` does not contain a `## 2. Trust Boundaries` heading, set `component_zone_map` to empty and emit a warning: `"No trust boundaries section found in threats.md; reachability will use default scores"`
2. **Section 2 exists but no Trust Zones table**: If the heading exists but no valid three-column trust zone table is found beneath `### Trust Zones`, set `component_zone_map` to empty and emit a warning: `"Trust Boundaries section found but no valid trust zone table; reachability will use default scores"`
3. **Empty trust zone table**: If the table exists but contains zero data rows (only header and separator), set `component_zone_map` to empty and emit a warning: `"Trust zone table is empty; reachability will use default scores"`
4. **SARIF-only input**: When parsing from `threats.sarif` (no `threats.md` available), trust zone data is not available in the SARIF format. Set `component_zone_map` to empty. The warning is: `"Trust zone data not available in SARIF input; reachability will use default scores"`

In all fallback cases, the Reachability Analysis phase (Section 6) applies a default reachability score of 5.0 (medium exposure) to all findings, with the corresponding warning propagated to the output.

## 2h. Error Handling

**Malformed table rows**: If a table row has fewer than three cells after splitting on pipe delimiters, skip the row and emit a warning: `"Skipping malformed trust zone row: '{raw_row_text}'"`. Continue processing remaining rows.

**Empty component list**: If the Components column is empty or contains only whitespace for a row, skip the row and emit a warning: `"Trust zone '{zone_name}' has no components assigned; skipping"`.

**Empty zone name**: If the Zone column is empty or contains only whitespace, skip the row and emit a warning: `"Trust zone row with empty zone name; skipping"`.

**Duplicate zone names**: If two rows share the same zone name (case-insensitive), merge their component lists under the first occurrence's trust level. Emit a warning if the trust levels differ: `"Zone '{zone_name}' appears with conflicting trust levels ('{first_level}' and '{second_level}'); using '{first_level}'"`.

**Non-table content in Section 2**: The `### Boundary Crossings` subsection also appears in Section 2 and contains a different table (5 columns: Crossing, From Zone, To Zone, Components, Controls). Do NOT parse the Boundary Crossings table as trust zone data. Only parse the table directly under the `### Trust Zones` subheading.
