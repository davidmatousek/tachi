# Finding & Coverage Contracts: F-241 Web/API Coverage Attestation + Populator Wiring

**Feature**: 241 — F-8 + F-A3 Web/API Coverage Attestation + Populator Wiring [Tier 3]
**Created**: 2026-05-01
**Phase**: Plan / Phase 1 design artifact

This document codifies the contracts that downstream consumers (the F-B aggregator, audit scripts, test fixtures, future contributors) rely on for F-241's outputs. Three contracts are scoped here:

1. **Finding `source_attribution` Populator Contract** (Stream 1 — F-A3 wiring)
2. **Coverage-Percentage Computation Contract** (Stream 4 — aggregator extension)
3. **Catalog-Resolvable vs Prose-Only Reference Rule** (Stream 3 — taxonomy expansion)

---

## 1. Finding `source_attribution` Populator Contract

### Pre-condition

A finding emitted by one of the 11 F-A3 target host agents (`spoofing`, `tampering`, `info-disclosure`, `privilege-escalation`, `repudiation`, `denial-of-service`, `tool-abuse`, `data-poisoning`, `model-theft`, `prompt-injection`, `agent-autonomy`) for any pattern category in its companion `references/detection-patterns.md`.

### Post-condition

The finding's `source_attribution` array is populated with at least one citation record matching the canonical pattern.

### Canonical pattern

```yaml
source_attribution:
  - taxonomy: <one of: owasp | mitre-attack | mitre-atlas | nist-ai-rmf | cwe>
    id: <canonical short ID for the cited item>
    relationship: primary
  - taxonomy: cwe
    id: <related CWE ID>
    relationship: related
  # Optional additional `related` or `derived` citations
```

**Constraints**:
- **At minimum one `primary` taxonomy citation per pattern category** (per spec SC-002).
- **At minimum one `related` CWE citation per pattern category** where applicable (mirrors F-1/F-2/F-4 net-new agent precedent; not strictly required for cases where no canonical CWE exists, e.g., agentic-only patterns).
- **Multiple `related` CWE citations permitted** when the pattern category warrants (e.g., F-4's human-trust-exploitation lines 117–120 demonstrate dual-CWE related on a single finding for ASI09 patterns covering CWE-223 + CWE-290).
- **`derived` relationship reserved for crosswalk JOIN** (post-MVP; not used in F-241 since F-B's MVP boundary excludes cross-framework reasoning per ADR-029).

### Per-pattern-category citation map

For each of the 11 F-A3 target hosts, the populator wiring uses the Pattern Category → Primary Source map already present in the host's companion `references/detection-patterns.md` file (post-F-7 inventory). The wiring agent does NOT modify the companion catalog Pattern Category → Primary Source maps; it consumes them.

Example for `tachi-spoofing`:

| Pattern Category | Primary Source (taxonomy: id) | Related CWE(s) |
|------------------|------------------------------|-----------------|
| Spoofed identities (existing) | (taxonomy: owasp, id: A07) | CWE-287, CWE-290 |
| OAuth token theft (existing) | (taxonomy: owasp, id: A07) | CWE-287 |
| Mobile credential storage (M1, F-7-added) | (taxonomy: owasp, id: M1) | CWE-522, CWE-256 |
| Insecure mobile auth/authz (M3, F-7-added) | (taxonomy: owasp, id: M3) | CWE-287 |

The populator block in `spoofing.md` would contain example YAML like:

```yaml
# Detection Workflow Step 5 — References (additive populator block)
source_attribution:
  - taxonomy: owasp
    id: A07              # OWASP Top 10:2021 — Identification and Authentication Failures
    relationship: primary
  - taxonomy: cwe
    id: CWE-287          # Improper Authentication
    relationship: related
```

### Verification (test predicates)

- `grep -l "source_attribution" .claude/agents/tachi/*.md` returns **14 paths** (3 pre-existing + 11 newly wired).
- Per-host structural assertion: each newly-wired host's `.md` file contains at least one `source_attribution:` YAML block under a Detection Workflow / Example Findings section.
- Line-count assertion: each newly-wired host's `.md` file remains ≤200 lines (ADR-036 cap).

---

## 2. Coverage-Percentage Computation Contract

### Pre-condition

- `schemas/taxonomy/<framework>.yaml` is loaded with full record inventory.
- Findings array parsed from `threats.md` Section 9 YAML output is available with `source_attribution` arrays populated.

### Post-condition

For each of the 5 frameworks (OWASP, MITRE ATT&CK, MITRE ATLAS, NIST AI RMF, CWE), the aggregator emits to the Typst data contract:

```typst
(
  framework: "<framework_name>",
  yaml-record-count: <total records in YAML, including out-of-scope>,
  in-scope-record-count: <records with out_of_scope == false>,
  covered-count: <items with ≥1 primary citation>,
  partial-count: <items with ≥1 related/derived but zero primary>,
  gap-count: <in-scope items with zero citations>,
  coverage-percentage: <(covered-count / in-scope-record-count) * 100, formatted as "X.XX%">,
  items: <per-item details>,
)
```

### Computation formulas

```python
in_scope_records = [r for r in records if not r.get("out_of_scope", False)]
in_scope_count = len(in_scope_records)

covered_ids = {r.id for r in in_scope_records if has_primary_citation(r.id, findings)}
partial_ids = {r.id for r in in_scope_records 
               if has_related_or_derived_citation(r.id, findings) 
               and r.id not in covered_ids}
gap_ids = {r.id for r in in_scope_records 
           if r.id not in covered_ids and r.id not in partial_ids}

covered_count = len(covered_ids)
partial_count = len(partial_ids)
gap_count = len(gap_ids)

assert covered_count + partial_count + gap_count == in_scope_count

coverage_pct = (covered_count / in_scope_count) * 100 if in_scope_count else None
```

### Edge case: Out-of-Scope citations

A finding citing an Out-of-Scope item (e.g., a finding with `source_attribution: [{taxonomy: mitre-attack, id: T1071, relationship: primary}]` where T1071 is in TA0011 Out-of-Scope) is rendered on the **per-finding attribution table** for traceability but **excluded from the per-framework aggregate**:

- Out-of-Scope items don't appear in `covered_ids`, `partial_ids`, or `gap_ids` (excluded from `in_scope_records` upstream).
- Their citations on findings still render (via the `per-finding-rows` data binding) so adopters can see the full citation trail.

### Edge case: Empty framework (entirely Out-of-Scope)

If `in_scope_count == 0`, the aggregator returns `coverage-percentage: "N/A"` (preserves existing behavior at line 1144 of `extract-report-data.py`). The Typst template already handles "N/A" rendering at line 168 (`let coverage-pct = str(aggregate.at("coverage-percentage", default: "N/A"))`).

### Verification (test predicates)

`tests/scripts/test_coverage_percentage_computation.py` exercises:

1. **Synthetic-fixture cross-check**: Hand-authored taxonomy fixture (10 records, 3 Out-of-Scope) + hand-authored finding fixture (4 findings citing 3 in-scope items as `primary`). Expected coverage_pct = (3 / 7) * 100 = "42.86%". Aggregator output must match.
2. **Real-baseline cross-check**: For each of 8 example architectures, audit script computes coverage_pct independently (re-reading taxonomy + findings) and asserts equality with the value rendered in `report-data.typ`.
3. **0 percentage point delta**: SC-009 BLOCKER-level assertion across all 5 frameworks × 8 baselines = 40 cross-check pairs.

### Non-modification guarantees

- The 3-value classification (Covered / Partial / Gap) per ADR-029 is preserved.
- The numerator (covered count) is computed from `primary` citations only (NOT `related` or `derived`).
- The Typst template binding at line 168 of `coverage-attestation.typ` is unchanged.
- The conditional-inclusion gate (`has-source-attribution AND per-finding-rows.len() > 0`) at `main.typ:417` is unchanged.

---

## 3. Catalog-Resolvable vs Prose-Only Reference Rule (per ADR-036 D-7 precedent)

### Rule statement (verbatim from F-7 ADR-036 D-7, carried forward by F-241)

> A reference to an external authority (OWASP / MITRE / CWE / NIST) is **catalog-resolvable** if and only if the canonical ID appears as a record in the corresponding `schemas/taxonomy/<framework>.yaml` file. Catalog-resolvable references appear in finding `source_attribution` arrays. Non-catalog-resolvable references appear in finding `references:` arrays as narrative context only.

### F-241 changes to the catalog-resolvable boundary

After Stream 3 expansion:

- **OWASP**: All 60 records (A01–A10 + API1–API10 + ASI01–ASI10 + LLM01–LLM10 + M1–M10 + ML01–ML10) catalog-resolvable. **No change** — already at full inventory pre-F-241.
- **MITRE ATT&CK Enterprise**: ~600 records catalog-resolvable post-Stream 3 (vs. 38 pre-F-241). Major expansion of the catalog-resolvable boundary on this framework.
- **MITRE ATLAS**: ~30 records catalog-resolvable post-Stream 3 (vs. 12 pre-F-241).
- **MITRE ATT&CK Mobile**: F-7's T1474, T1626, T1398 (per ADR-036 D-7) remain prose-only because they are NOT in the `mitre-attack.yaml` Enterprise catalog (per F-7 verification). F-241 does NOT expand the catalog to ATT&CK Mobile in Stream 3 (Mobile is a distinct ATT&CK matrix; remains future scope).
- **NIST AI RMF**: Catalog state unchanged from F-A1 baseline. Records that lack canonical IDs remain prose-only.
- **CWE**: Catalog state unchanged. Records present in F-A1 baseline remain catalog-resolvable; CWE-Top-25 entries that aren't in F-A1 remain prose-only.

### Implications for finding emissions

- **A finding citing T1190 (Exploit Public-Facing Application)**: Catalog-resolvable post-F-241 (T1190 is in TA0001 Initial Access in-scope tactic). Emit in `source_attribution` array.
- **A finding citing T1474 (Supply Chain Compromise — Mobile)**: Prose-only (per F-7 ADR-036 D-7 precedent). Emit in `references:` narrative array only.
- **A finding citing AML.T0024 (Exfiltration via ML Inference API)**: Catalog-resolvable (in `mitre-atlas.yaml` per F-A1). Emit in `source_attribution` array.
- **A finding citing AML.T0015**: Prose-only (NOT in `mitre-atlas.yaml` per F-6 ADR-035 D-7 precedent).

### Verification (test predicate)

`tests/scripts/test_coverage_attestation_audit.py` walks all `source_attribution` arrays in fixture findings and asserts:
- Every cited `(taxonomy, id)` resolves to a record in the corresponding `schemas/taxonomy/<framework>.yaml`.
- Every prose-only reference in the corresponding finding's `references:` array does NOT resolve to a YAML record (i.e., the prose-only / catalog-resolvable boundary is correctly drawn).

---

## 4. Stream 2 Closure-Path Contract (Six Partial Web/API Items)

For each of the six Partial items, the closure path produces:

- **A Primary Source block** (or extension) on the affected pattern category in the target companion `references/detection-patterns.md` file.
- **At most one new Indicator category** (FR-007 allowance) — used only for API6 (per Q-Plan-1 → `tachi-tool-abuse`) and API9 (per Q-Plan-2 → `tachi-info-disclosure`).
- **A finding fixture** under `tests/scripts/fixtures/web_api_coverage_attestation/` demonstrating `source_attribution` resolves to the OWASP item.

OR (alternative path FR-008): explicit Deferral with:

- **An ADR-037 D-numbered decision** documenting the reason the item could not close under existing-pattern + new-Indicator allowance.
- **A follow-on GitHub Issue** scoped to close the item in a future feature.
- **A Coverage Matrix annotation** (in §6 of `_internal/strategy/BLP-01-threat-coverage.md`) showing the item as Deferred with pointer to the ADR + Issue.

### Per-item closure expectations (plan-day default)

| Item | Default Closure Path | Plan-Day Resolution |
|------|---------------------|---------------------|
| A05 | Primary Source on Cat 11 of `tachi-privilege-escalation` | Closeable per Architect Q2 |
| A06 | Primary Source on Cat 8 of `tachi-tampering` | Closeable per Architect Q2 |
| API6 | NEW Indicator category in `tachi-tool-abuse` | Q-Plan-1 RESOLVED → tool-abuse (rejected privilege-escalation) |
| API8 | API-Indicator extension on Cat 11 of `tachi-privilege-escalation` (consolidates with A05) | Closeable per Architect Q2 |
| API9 | NEW Indicator category in `tachi-info-disclosure` | Q-Plan-2 RESOLVED → info-disclosure (rejected repudiation) |
| API10 | Primary Source + cross-reference on Cat 9 (`tachi-tampering` Injection) and Cat 7 (`tachi-info-disclosure` SSRF) | Closeable per Architect Q2 |

### Aggregate closure outcome (target SC-005)

If all 6 items close: BLP-01 four-framework total = 60/60 (40 four-framework already closed at F-7 + 20 Web/API closed at F-241). If 1–2 items defer: BLP-01 closes at the actual Covered count (e.g., 58/60).

---

## 5. Test Fixture Catalog (under `tests/scripts/fixtures/web_api_coverage_attestation/`)

Fixtures grouped by Stream verification:

```
tests/scripts/fixtures/web_api_coverage_attestation/
├── stream_1_f_a3_wiring/
│   ├── valid_spoofing_a07_finding.yaml                    # Spoofing host source_attribution sample
│   ├── valid_tampering_a03_finding.yaml                   # Tampering host
│   ├── valid_info_disclosure_a01_finding.yaml             # Info-disclosure host
│   ├── valid_privilege_escalation_a01_finding.yaml        # Privilege-escalation host
│   ├── valid_repudiation_a09_finding.yaml                 # Repudiation host
│   ├── valid_denial_of_service_llm10_finding.yaml         # Denial-of-service host (LLM10 attribution per F-5)
│   ├── valid_tool_abuse_asi07_finding.yaml                # Tool-abuse host (ASI07 attribution per F-3)
│   ├── valid_data_poisoning_ml06_finding.yaml             # Data-poisoning host (ML06 corpus-side per F-6)
│   ├── valid_model_theft_ml03_finding.yaml                # Model-theft host (ML03 per F-6)
│   ├── valid_prompt_injection_llm01_finding.yaml          # Prompt-injection host (per HIGH-A)
│   └── valid_agent_autonomy_asi01_finding.yaml            # Agent-autonomy host (per HIGH-A)
│
├── stream_2_partial_closures/
│   ├── valid_a05_security_misconfiguration_finding.yaml   # A05 closure evidence
│   ├── valid_a06_vulnerable_components_finding.yaml       # A06 closure evidence
│   ├── valid_api6_business_flow_abuse_finding.yaml        # API6 closure evidence (Q-Plan-1)
│   ├── valid_api8_security_misconfiguration_finding.yaml  # API8 closure evidence
│   ├── valid_api9_inventory_management_finding.yaml       # API9 closure evidence (Q-Plan-2)
│   └── valid_api10_unsafe_consumption_finding.yaml        # API10 closure evidence
│
├── stream_3_taxonomy/
│   ├── synthetic_owasp_subset.yaml                        # 5-record synthetic OWASP subset for unit tests
│   ├── synthetic_attack_with_out_of_scope.yaml            # 10-record synthetic ATT&CK subset (3 out-of-scope) for coverage-% test
│   └── synthetic_atlas_subset.yaml                        # 5-record synthetic ATLAS subset
│
└── stream_4_coverage_percentage/
    ├── synthetic_findings_for_coverage_test.yaml          # Hand-authored findings exercising primary/related/derived citations
    ├── synthetic_findings_with_out_of_scope_citations.yaml # Findings citing Out-of-Scope items (excluded from denominator)
    └── empty_findings.yaml                                # Edge case: zero findings → coverage_pct = 0% on all in-scope frameworks
```

### Fixture authoring note

Fixtures intentionally use synthetic data not reflecting any real adopter architecture or finding. They exercise contract behavior, not domain accuracy.

---

## 6. References

- **ADR-027** (F-A1, taxonomy catalog) — D1 record-shape contract
- **ADR-028** (F-A2, source_attribution schema) — 5-value taxonomy enum + 3-value relationship enum
- **ADR-029** (F-B, rendering surface) — has-source-attribution conditional gate + 3-value classification
- **ADR-035 D-7** (F-6, ATLAS catalog gap) — prose-only ATLAS technique precedent
- **ADR-036 D-7** (F-7, ATT&CK Mobile catalog gap) — prose-only ATT&CK Mobile technique precedent
- **ADR-037** (F-241, this feature) — single combined ADR per Q-PM-1 plan-day RESOLVED
