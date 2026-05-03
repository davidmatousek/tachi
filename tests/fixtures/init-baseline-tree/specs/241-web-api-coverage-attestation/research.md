# Research Summary: Feature 241 — F-8 + F-A3 Web/API Coverage Attestation + Populator Wiring

**Created**: 2026-04-30
**PRD**: [docs/product/02_PRD/241-web-api-coverage-attestation-2026-04-29.md](../../docs/product/02_PRD/241-web-api-coverage-attestation-2026-04-29.md)
**Phase**: BLP-01 Tier 3 closure (final feature in 11-feature initiative)

---

## Knowledge Base Findings

- **KB-037**: Documents "two-execution-deep pattern validation across detection-tier features" (Feature 206 retrospective) — captures 10 stable architectural patterns for new detection-tier features. **Not** the pyyaml deferred-import invariant (PRD reference confused). The actual pyyaml deferred-import invariant is documented **inline at `scripts/extract-report-data.py:1077–1080`** (verified during research): "imported lazily so the module loads without pyyaml installed — required by the stdlib-only module-load invariant in sibling tachi_parsers." F-241 should codify this invariant via a new test (`test_pyyaml_deferred_import.py`) to lock the discipline; the test, not a new KB entry, becomes the regression guard.
- **F-A3 one-way dependency precedent** (F-5 / F-6 / F-7 specs): Each used the exact phrase "F-X → F-A3 inheritance; F-X does not require F-A3 to ship" — establishing that enrichment-branch features defer F-A3 wiring uniformly, while net-new agent features (F-1 / F-2 / F-4) ship populator wiring inline at genesis. F-241 closes this dependency direction by retroactively wiring all 11 enrichment-deferred hosts.

## Codebase Analysis

### Three net-new agents that already populate `source_attribution` (F-A3 wiring template)

All three follow an identical pattern — `## Example Findings` section emits inline YAML with `source_attribution` array; Detection Workflow Step 5 (References) explicitly names the populator contract:

| Agent | File | Section | Pattern |
|-------|------|---------|---------|
| `output-integrity` (F-1) | `.claude/agents/tachi/output-integrity.md` | `## Example Findings` (line 48) | `{taxonomy: owasp, id: LLM05, relationship: primary}` + `{taxonomy: cwe, id: CWE-79, relationship: related}` |
| `misinformation` (F-2) | `.claude/agents/tachi/misinformation.md` | `## Example Findings` (line 48) | `{taxonomy: owasp, id: LLM09, relationship: primary}` + `{taxonomy: cwe, id: CWE-345, relationship: related}` |
| `human-trust-exploitation` (F-4) | `.claude/agents/tachi/human-trust-exploitation.md` | `## Example Findings` (line 60) | `{taxonomy: owasp, id: ASI09, relationship: primary}` + multi-CWE `related` (CWE-223/287/290/345) |

**Canonical wiring pattern**: One `primary` OWASP citation + one or more `related` CWE citations, populated inline at the Detection Workflow step that emits findings. No companion catalog edits required (Pattern Category → Primary Source maps already exist post-F-7 in `references/detection-patterns.md` files).

### Eleven F-A3 target agents (current line counts vs. ADR-036 200-line cap)

All 11 files confirmed present at `.claude/agents/tachi/<name>.md` with substantial expansion headroom:

| Agent | Lines | Headroom (200 - lines) |
|-------|-------|------------------------|
| repudiation | 53 | 147 |
| spoofing | 55 | 145 |
| privilege-escalation | 55 | 145 |
| denial-of-service | 56 | 144 |
| info-disclosure | 60 | 140 |
| tampering | 60 | 140 |
| data-poisoning | 90 | 110 |
| prompt-injection | 96 | 104 |
| tool-abuse | 100 | 100 |
| model-theft | 105 | 95 |
| agent-autonomy | 114 | 86 |

All 11 companion `references/detection-patterns.md` files confirmed present.

### Aggregator semantics (`scripts/extract-report-data.py`)

- **Function**: `classify_framework_items()` (lines 1112–1140) reads `finding.get("source_attribution")` directly at line 1130. **No implicit prefix-attribution path exists** (PRD claim verified). Direct match: `if ref.get("taxonomy") == framework_name and ref.get("id") == record_id`.
- **Coverage classification (already implemented, lines 1133–1138)**:
  - `Covered` ← ≥1 finding cites with `relationship: primary`
  - `Partial` ← zero `primary` AND ≥1 `related`/`derived`
  - `Gap` ← zero citations
- **Coverage percentage (already implemented at `_build_per_framework_aggregate()` line 1144)**: `(covered_count / yaml_record_count) * 100` → "X.XX%"; "N/A" when denominator is zero. **F-241's incremental work**: filter denominator by `out_of_scope: false` records when those fields land in YAML schema.
- **YAML import**: Deferred to function scope at line 1085 within `_load_framework_yaml_records()` (per stdlib-only module-load invariant). F-241 must preserve this discipline.
- **File line count**: 2164 lines.

### F-B Typst template (`templates/tachi/security-report/coverage-attestation.typ`)

- **Line count**: 403 lines.
- **Data contract** (lines 321–324): Already binds `per-finding-rows` (array of attribution dicts) and `per-framework-aggregates` (5 dicts with `framework`, `yaml-record-count`, `covered-count`, `partial-count`, `gap-count`, **`coverage-percentage`**, `items`). **Coverage percentage rendering already in place** (line 168: `let coverage-pct = str(aggregate.at("coverage-percentage", default: "N/A"))`).
- **Conditional gate**: `main.typ` line 417 wraps section in `has-source-attribution AND per-finding-rows.len() > 0`.

### F-A2 schema field definition (`schemas/finding.yaml`)

- **Schema version**: v1.8 (line 13). F-241 preserves at v1.8 (sixth zero-`finding.yaml`-bump BLP-01 detection feature).
- **5-value taxonomy enum** (lines 242–247): `owasp | mitre-attack | mitre-atlas | nist-ai-rmf | cwe`.
- **3-value relationship enum** (lines 263–266): `primary | related | derived`.

### Current taxonomy YAML state (`schemas/taxonomy/`)

| File | Records | Notes |
|------|---------|-------|
| `owasp.yaml` | 60 | **Already populated**: A01–A10 (10) + API1–API10 (10) + ASI01–ASI10 (10) + LLM01–LLM10 (10) + M1–M10 (10) + ML01–ML10 (10). F-241's audit work focuses on attesting each row with ≥1 agent-plus-pattern-category citation, not on adding new rows. |
| `mitre-attack.yaml` | 38 | 21 parent + 17 sub-techniques. Target: ~600 Enterprise items per PRD. **Largest expansion delta** — tactical-grouping Out-of-Scope strategy (5–7 design-time-irrelevant tactics) bounds the practical authoring scope to in-scope tactics: TA0001 / TA0002 / TA0003 / TA0004 / TA0006 / TA0042. |
| `mitre-atlas.yaml` | 12 | 7 seed + 5 Oct 2025 curated. Target: ~30 records. |

**Record shape** (ADR-027 D1, lines 47–53 of ADR-027): 5 fields per record — `id`, `full_id`, `name`, `url`, `cwe_refs` (non-empty for OWASP, empty for ATT&CK/ATLAS).

**F-241 record-shape extension** (PRD §3 Architect MEDIUM-A acknowledged): adds `out_of_scope: bool` (default `false`) + `out_of_scope_rationale: string` (default empty). Backward-compat preserved via YAML defaults; existing F-A1 records that omit these fields parse correctly.

### Example architectures (`examples/`)

10 directories present; **6 have `security-report.pdf.baseline`**, 4 do not:

| Directory | Baseline? | F-241 scope? |
|-----------|-----------|--------------|
| web-app | ✅ | ✅ regen |
| microservices | ✅ | ✅ regen |
| ascii-web-api | ✅ | ✅ regen |
| mermaid-agentic-app | ✅ | ✅ regen |
| free-text-microservice | ✅ | ✅ regen |
| maestro-reference | ✅ | ✅ regen |
| predictive-ml-app (F-6) | ❌ | ✅ **net-new baseline + regen** |
| mobile-banking-app (F-7) | ❌ | ✅ **net-new baseline + regen** |
| agentic-app | ❌ | ❌ (out of F-241 scope) |
| consumer-agent-app | ❌ | ❌ (out of F-241 scope) |

**Eight-baseline scope** (per Architect Q-Architect-4 MEDIUM resolution) = the six pre-existing baselines + two new baselines for `predictive-ml-app` + `mobile-banking-app`. The other two (agentic-app, consumer-agent-app) remain unbaselined per their respective feature scopes (F-3 / F-4 PRD boundaries).

## Architecture Constraints

### ADR Lineage (Foundation + four deferral ADRs F-241 closes)

- **ADR-027** (F-A1): Establishes 7-value taxonomy catalog + D1 5-field record-shape contract (`id`, `full_id`, `name`, `url`, `cwe_refs`). F-241 extends record shape +2 fields per Architect MEDIUM-A acknowledgment.
- **ADR-028** (F-A2): Establishes `source_attribution` 5-value taxonomy enum + 3-value relationship discrimination. F-241 Stream 1 + Stream 4 both consume this contract.
- **ADR-029** (F-B): Establishes conditional-inclusion (`has-source-attribution`) + 3-value classification (Covered / Partial / Gap) MVP boundary. F-241 *populates* the renderer rather than expanding the rendering contract.
- **ADR-032** (F-3 single-agent): First defer (zero deferral language because F-3 was the genesis of the enrichment-branch defer pattern; precedent set, not stated explicitly).
- **ADR-034 D-8** (F-5 two-agent): "F-A3 deferral per ADR-028 Decision 6" — first explicit deferral statement.
- **ADR-035 D-10** (F-6 three-agent): "F-6 is the second BLP-01 detection feature to defer populator wiring (after F-5)."
- **ADR-036 D-10** (F-7 four-or-five-agent, **MOST RECENT, MUST CITE VERBATIM**): "F-7 is the third BLP-01 detection feature to defer populator wiring. **The three-feature precedent (F-5 + F-6 + F-7) establishes a clear pattern: enrichment-branch features uniformly defer F-A3 populator wiring, while net-new agent features (F-1 + F-2 + F-4) ship populator wiring inline. The split simplifies F-A3's eventual scope: F-A3 owns the populator wiring for ALL existing host agents that emit BLP-01 findings via enrichment, while net-new agents continue to ship inline populator wiring at their own genesis.**" Cumulative scope established as 9 unique enrichment-deferred hosts; F-241 expands this to 11 per Architect HIGH-A v1.1.

### Next available ADR number

ADR-037 (highest existing = ADR-036; ADR-004 historically absent; no other gaps).

### BLP-01 §8 Coverage Matrix Quality Bar (closure rule)

1. No **Planned** items remain at completion (all closed or escalated to **Out of Scope** with ADR rationale).
2. No **Partial** items remain without an associated open PRD or explicit deferral note.
3. Every **Covered** item cites ≥1 tachi agent AND ≥1 detection-pattern category.

### BLP-01 §10 One-Line Success Statement (true at runtime after F-241)

> "Tachi automatically tells you, per engagement, which OWASP / MITRE / NIST / CWE items it detects and which it misses."

### Constitution alignment (`.aod/memory/constitution.md`)

1. **Additive-only edits** (Principle: Git Workflow): F-241 wiring + audit must preserve additive discipline inherited from ADR-023 D3 (extended through F-1..F-7).
2. **Byte-identity baselines** (ADR-021 lineage): Six pre-existing baselines must regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000`; the two intentional baseline updates (Coverage Attestation section populated on all eight) are the only non-byte-identical deltas.
3. **No `finding.yaml` shape change without ADR**: F-241 holds finding.yaml at v1.8 (zero shape change); taxonomy YAML +2-field extension covered by ADR-037.

## Industry Research

Web research not strictly required for this attestation pass — the relevant external authorities are already enumerated in the PRD §References:
- [OWASP Top 10:2021](https://owasp.org/Top10/) — A01–A10 entries
- [OWASP API Security Top 10:2023](https://owasp.org/API-Security/editions/2023/en/0x11-t10/) — API1–API10 entries
- [MITRE ATT&CK Enterprise](https://attack.mitre.org/) — full Enterprise matrix (~600 items, target inventory for Stream 3)
- [MITRE ATLAS](https://atlas.mitre.org/) — full ATLAS matrix (~30 items, target inventory for Stream 3)

These authorities are the canonical sources for the taxonomy YAML expansion in Stream 3. No new external best-practices research surfaces relevant to attestation + populator-wiring scope.

## Recommendations for Spec

### Structure recommendations

1. **Follow F-237 precedent structure** (most recent BLP-01 closure spec at 207 lines):
   - YAML frontmatter → Overview → User Scenarios → Requirements → Success Criteria → Assumptions → Plan-Day Decision Deferrals → Out of Scope.
   - Use **Plan-Day Decision Deferrals table** for the one PRD-carry-forward question (Q-PM-1: single combined ADR vs. split ADR for taxonomy YAML record-shape extension).

2. **Four user stories** preserving PRD US-241-1 through US-241-4 verbatim as primary; all P1 priority. Each story must be independently testable.

3. **FR organization by work stream + artifact** (mirrors F-237 / F-232 agent-grouping convention, adapted for F-241's 4-stream scope):
   - Stream 1 (F-A3 wiring): one FR per agent or grouped by Wave (5 + 6 fan-out)
   - Stream 2 (Partial item audit): one FR per item or grouped by closure path (4 closeable + 2 new-Indicator)
   - Stream 3 (taxonomy expansion): one FR per YAML
   - Stream 4 (rendering): one FR for aggregator extension + one for baseline regen
   - Cross-cutting: ADR-037, §6 demotion, schema invariants, byte-identity, tests

4. **Success Criteria preserving PRD SC-1..SC-15 verbatim** as SC-001..SC-015; add measurable outcomes if any PRD criterion needs operationalization.

5. **Edge Cases section** — capture:
   - Tactical-grouping rationale challenge (Risk 5 from PRD)
   - Partial item Deferral path (Risk 3 from PRD; some items may not close)
   - ATT&CK inventory authoring overrun (Risk 1 from PRD)
   - F-A3 wiring per-agent variance (Risk 2 from PRD)
   - Non-Coverage-Attestation page byte-identity preservation (Risk 4 from PRD)
   - `agentic-app` / `consumer-agent-app` deliberate exclusion from baseline scope

6. **Assumptions section** — codify A-1..A-4 from PRD with their resolved-status labels (REVISED / PARTIALLY VALID / RESOLVED).

7. **Plan-Day Decision Deferrals table** — single open question carry-forward:
   - Q-PM-1: Single combined ADR-037 vs. split ADR (one for F-8 attestation + one for F-A3 populator-wiring + record-shape extension).

8. **Out-of-Scope section** — explicit Won't Have list:
   - AIVSS scoring formula
   - `schemas/finding.yaml` shape change
   - New finding-ID prefixes
   - Cross-framework crosswalk JOIN (F-B ADR-029 MVP boundary)
   - New threat agents
   - `agentic-app` / `consumer-agent-app` baselines

### Avoidances

- **No implementation details** in spec.md (no Python code, no Typst snippets, no YAML record shapes — those go in plan.md).
- **No tech stack mentions** beyond what's already established in PRD references (taxonomy YAML format, Typst template, Python aggregator).
- **No `[NEEDS CLARIFICATION]` markers** — PRD already resolved all open questions during third-pass Triad review (only Q-PM-1 carries forward as an explicit Plan-Day deferral, which goes in the Decisions Deferrals table, not as a clarification marker).
