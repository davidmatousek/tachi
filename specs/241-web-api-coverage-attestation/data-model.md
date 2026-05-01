# Data Model: F-241 Web/API Coverage Attestation + Populator Wiring

**Feature**: 241 — F-8 + F-A3 Web/API Coverage Attestation + Populator Wiring [Tier 3]
**Created**: 2026-05-01
**Phase**: Plan / Phase 1 design artifact
**Source**: ADR-027 (taxonomy catalog), ADR-028 (source_attribution schema), ADR-029 (rendering surface), spec.md FR-001..FR-024

---

## 1. `source_attribution` Array Shape (per ADR-028)

The `source_attribution` field on each finding emitted by tachi's detection-tier agents is a list of citation records.

### Schema (verbatim from `schemas/finding.yaml` v1.8 lines 235–270)

```yaml
source_attribution:
  type: array
  description: External taxonomy citations supporting this finding
  items:
    type: object
    required: [taxonomy, id]
    properties:
      taxonomy:
        type: string
        enum:
          - owasp           # OWASP Top 10:2021, API Top 10:2023, ASI:2026, LLM:2025, Mobile:2024, ML:2023
          - mitre-attack    # MITRE ATT&CK Enterprise
          - mitre-atlas     # MITRE ATLAS
          - nist-ai-rmf     # NIST AI Risk Management Framework
          - cwe             # Common Weakness Enumeration
      id:
        type: string
        description: Canonical short ID (e.g., A01, LLM05, T1190, AML.T0024, CWE-79)
      relationship:
        type: string
        enum:
          - primary          # Direct framework match (default)
          - related          # Adjacent mapping (e.g., CWE alongside OWASP primary)
          - derived          # Transitive via crosswalk (post-MVP)
        default: primary
```

### F-A3 Populator Pattern (per F-1/F-2/F-4 net-new agent precedent)

Each of the 11 newly-wired host agents adopts the canonical pattern:

```yaml
source_attribution:
  - taxonomy: owasp
    id: <PRIMARY-OWASP-ID>     # e.g., A01, API1, ASI01, LLM01, M1, ML01
    relationship: primary
  - taxonomy: cwe
    id: <RELATED-CWE-ID>        # e.g., CWE-79, CWE-345, CWE-287
    relationship: related
```

**Multi-CWE related**: Some pattern categories warrant multiple `related` CWE citations (e.g., F-4's human-trust-exploitation lines 117–120 demonstrate dual-CWE related on a single finding).

**No new prefixes**: F-241 reuses the F-A2 5-value taxonomy enum and 3-value relationship enum without modification. `schemas/finding.yaml` remains at v1.8 (sixth zero-bump BLP-01 detection feature).

---

## 2. Taxonomy YAML Record Shape (per ADR-027 D1 + Architect MEDIUM-A extension)

### Existing fields (ADR-027 D1, no change)

```yaml
- id: A05                                                         # Short canonical ID
  full_id: OWASP-2021-A05                                         # Framework-prefixed ID
  name: Security Misconfiguration                                 # Verbatim canonical name
  url: https://owasp.org/Top10/2021/A05_2021-Security_Misconfiguration/  # Retrievable URL
  cwe_refs: [CWE-16, CWE-2, CWE-260]                              # List of CWE IDs (non-empty for OWASP; empty [] for ATT&CK/ATLAS)
```

### Extended fields (F-241 adds, ADR-037 D-7)

```yaml
- id: A05
  full_id: OWASP-2021-A05
  name: Security Misconfiguration
  url: https://owasp.org/Top10/2021/A05_2021-Security_Misconfiguration/
  cwe_refs: [CWE-16, CWE-2, CWE-260]
  out_of_scope: false                                             # NEW (default: false)
  out_of_scope_rationale: ""                                      # NEW (default: empty string)
```

### Backward Compatibility

Existing F-A1 records that omit `out_of_scope` and `out_of_scope_rationale` parse correctly under YAML default behavior:

- `out_of_scope` absent → treated as `false` (in-scope)
- `out_of_scope_rationale` absent → treated as empty string

A new test (`test_pyyaml_deferred_import.py` partner — actually `test_coverage_attestation_audit.py` validates this) asserts that all F-A1 records pre-F-241 continue to parse correctly post-F-241.

### Out-of-Scope Annotation Patterns

Two annotation modes are supported:

**Per-item annotation** (used on `mitre-atlas.yaml` and ATT&CK records inside in-scope tactics):

```yaml
- id: T1078.004
  full_id: ATT&CK-T1078.004
  name: Valid Accounts — Cloud Accounts
  url: https://attack.mitre.org/techniques/T1078/004/
  cwe_refs: []
  out_of_scope: true
  out_of_scope_rationale: "Cloud account abuse operates at runtime/IR layer; tachi's design-time threat modeling cannot detect credential validity at the architecture layer."
```

**Tactic-level group annotation** (used on `mitre-attack.yaml` for design-time-irrelevant tactics):

```yaml
- id: T1071
  full_id: ATT&CK-T1071
  name: Application Layer Protocol
  url: https://attack.mitre.org/techniques/T1071/
  cwe_refs: []
  out_of_scope: true
  out_of_scope_rationale: "Tactic TA0011 (Command and Control): runtime network communication; outside design-time threat-modeling scope."
```

The `out_of_scope_rationale` for tactic-grouped items references the tactic-level rationale. The 5–7 design-time-irrelevant tactics (TA0005, TA0007, TA0008, TA0009, TA0010, TA0011, TA0040) carry uniform tactic-level rationales applied to all member items.

---

## 3. Coverage Aggregate Typst Data Contract (ADR-029 + F-241 Stream 4 extension)

### Existing contract (preserved)

```typst
let report-data = (
  has-source-attribution: true,
  per-finding-rows: (...),
  per-framework-aggregates: (
    (
      framework: "owasp",
      yaml-record-count: 60,         // Pre-F-241; post-F-241: 60 in-scope (out-of-scope filter applied)
      covered-count: 14,             // Items with ≥1 primary citation
      partial-count: 6,              // Items with ≥1 related/derived only
      gap-count: 40,                 // Items with zero citations
      coverage-percentage: "23.33%", // (covered-count / in-scope-record-count) * 100
      items: (...),                  // Per-item details
    ),
    // ... 4 more framework aggregates: mitre-attack, mitre-atlas, nist-ai-rmf, cwe
  ),
)
```

### F-241 Stream 4 incremental changes

**Aggregator denominator filter**: `_build_per_framework_aggregate()` (line 1144 of `extract-report-data.py`) gains:

```python
# Filter Out-of-Scope records before computing denominator
in_scope_records = [r for r in records if not r.get("out_of_scope", False)]
denominator = len(in_scope_records)
coverage_pct = (covered_count / denominator) * 100 if denominator else None
```

**Edge cases**:
- Findings citing Out-of-Scope items: rendered on per-finding attribution table (preserves traceability) but excluded from coverage-percentage denominator (preserves accuracy of coverage attestation).
- `denominator == 0` (entirely Out-of-Scope framework): returns `"N/A"` (preserves existing behavior).

---

## 4. Six Partial Item Closure Mapping (Stream 2)

| OWASP ID | Item Name | Closure Path | Target Companion Catalog | New Indicator? |
|----------|-----------|--------------|-------------------------|----------------|
| A05 | Security Misconfiguration | Primary Source addition + non-mobile Indicator extension on Pattern Category 11 | `tachi-privilege-escalation/references/detection-patterns.md` | No |
| A06 | Vulnerable and Outdated Components | Primary Source block on Pattern Category 8 (Software Supply Chain Integrity Failures) | `tachi-tampering/references/detection-patterns.md` | No |
| API6 | Unrestricted Access to Sensitive Business Flows | **NEW Indicator category** per Q-Plan-1 RESOLVED → `tachi-tool-abuse` | `tachi-tool-abuse/references/detection-patterns.md` | **Yes** (one new) |
| API8 | Security Misconfiguration | API-specific Indicator extension on Pattern Category 11 | `tachi-privilege-escalation/references/detection-patterns.md` (consolidates with A05) | No |
| API9 | Improper Inventory Management | **NEW Indicator category** per Q-Plan-2 RESOLVED → `tachi-info-disclosure` | `tachi-info-disclosure/references/detection-patterns.md` | **Yes** (one new) |
| API10 | Unsafe Consumption of APIs | Primary Source + cross-reference on Pattern Category 9 (Injection) and Pattern Category 7 (SSRF) | `tachi-tampering/...` (Injection) + `tachi-info-disclosure/...` (SSRF; consolidates with API9 file) | No |

**Scope discipline**: Per FR-007 allowance of "at most one new Indicator category per Partial item" — Stream 2 introduces 2 new Indicator categories total (API6 + API9). No more.

**Deferral path** (FR-008): If any item cannot close under the existing-pattern + new-Indicator allowance, that item surfaces with explicit ADR-037 D-numbered deferral rationale + a follow-on GitHub Issue. BLP-01 closes at the actual Covered count (e.g., 58/60 if 2 items defer).

---

## 5. Tactical-Grouping Out-of-Scope Rationale Set (Stream 3 — ATT&CK)

Five to seven tactic-level Out-of-Scope rationales applied to ATT&CK Enterprise tactics whose threat surface lies outside tachi's design-time scope:

| Tactic | ID | Out-of-Scope Rationale (verbatim, applied to all member items) |
|--------|------|--------|
| Defense Evasion | TA0005 | Tactic TA0005 operates at runtime via active-malware behavior; outside tachi's design-time threat-modeling scope. |
| Discovery | TA0007 | Tactic TA0007 operates at runtime via active reconnaissance; outside tachi's design-time threat-modeling scope. |
| Lateral Movement | TA0008 | Tactic TA0008 operates at runtime via post-compromise pivoting; outside tachi's design-time threat-modeling scope. |
| Collection | TA0009 | Tactic TA0009 operates at runtime via active data harvesting; outside tachi's design-time threat-modeling scope. |
| Exfiltration | TA0010 | Tactic TA0010 operates at runtime via active data egress; outside tachi's design-time threat-modeling scope. |
| Command and Control | TA0011 | Tactic TA0011 operates at runtime via active C2 channels; outside tachi's design-time threat-modeling scope. |
| Impact | TA0040 | Tactic TA0040 operates at runtime via active impact actions (data destruction, encryption); outside tachi's design-time threat-modeling scope. |

**In-Scope tactics** (per-item Out-of-Scope rationale only on individual runtime-only sub-techniques):

| Tactic | ID | Scope rationale |
|--------|------|--------|
| Initial Access | TA0001 | Design-time relevant: architecture-layer attack surfaces (exposed endpoints, supply chain, valid-account spoofing). |
| Execution | TA0002 | Design-time relevant where related to deployment-time configurations or trusted-component invocations. |
| Persistence | TA0003 | Design-time relevant: persistent backdoors, account creation, scheduled tasks declared at architecture layer. |
| Privilege Escalation | TA0004 | Design-time relevant: token manipulation, exploitation of vulnerabilities accessible at architecture layer. |
| Credential Access | TA0006 | Design-time relevant: credential storage / handling / theft surfaces. |
| Resource Development | TA0042 | Design-time relevant: supply-chain compromise, infrastructure-development surfaces. |

---

## 6. Catalog-Resolvable vs Prose-Only Reference Rule (per ADR-036 D-7 precedent)

This rule, established by F-7 ADR-036 D-7 and preserved by F-241, governs how taxonomy citations are surfaced on findings:

- **Catalog-resolvable references** appear in `source_attribution` arrays (validated against the corresponding taxonomy YAML at audit time).
- **Prose-only references** appear in finding `references:` arrays as narrative context only (NOT in `source_attribution`).

After Stream 3 expansion, fewer references will fall into the prose-only category (because taxonomy YAMLs cover more catalog-resolvable IDs). However, some references will remain prose-only:

- ATT&CK Mobile entries marked Out-of-Scope at the tactic level (e.g., T1474 Supply Chain Compromise — Mobile, T1626 Abuse Elevation Control Mechanism, T1398 Boot or Logon Initialization Scripts) per F-7 ADR-036 D-7 precedent.
- ATLAS entries identified as catalog-absent during Stream 3 expansion (preserve F-5 / F-6 prose-only precedent).
- Custom NIST AI RMF references that don't yet have a stable canonical ID.

---

## 7. Validation Predicates (test fixtures)

Test fixtures under `tests/scripts/fixtures/web_api_coverage_attestation/` exercise:

1. **Source attribution wiring** (Stream 1 verification): Sample finding for each of 11 newly-wired host agents demonstrating canonical `primary` + `related` pattern.
2. **Six Partial item closures** (Stream 2 verification): Sample finding for each of A05, A06, API6, API8, API9, API10 demonstrating citation evidence per the closure mapping table above.
3. **Coverage-percentage cross-check** (Stream 4 verification): Synthetic findings + synthetic taxonomy YAMLs (with mixed in-scope / Out-of-Scope records) used to compute coverage % independently; assertion that aggregator output matches.
4. **Out-of-Scope citation handling**: Sample findings citing Out-of-Scope items; assertion that they appear in per-finding rows but excluded from denominator.
5. **Backward-compat parsing** (record-shape extension verification): Pre-F-241 taxonomy YAML records (without `out_of_scope` / `out_of_scope_rationale` fields) parse correctly post-F-241.

---

## 8. State Transitions (none required)

F-241 has no state machinery. All edits are content-tier (Markdown / YAML) plus one Python aggregator function extension. No new tables, no new locks, no new lifecycles. The §6 Coverage Matrix transitions from "source of truth" to "historical" via annotation only — the file is preserved.

---

## 9. References

- **ADR-027** (F-A1, taxonomy catalog) — D1 record-shape contract (5 fields → +2 fields per F-241 ADR-037 D-7)
- **ADR-028** (F-A2, source_attribution schema) — 5-value taxonomy enum + 3-value relationship enum
- **ADR-029** (F-B, rendering surface) — `has-source-attribution` conditional gate + 3-value classification (Covered / Partial / Gap)
- **ADR-036 D-7** (F-7) — catalog-resolvable vs prose-only reference rule (carried forward by F-241)
- **ADR-037** (F-241, this feature) — single combined attestation + populator-wiring scope per Q-PM-1 plan-day RESOLVED
