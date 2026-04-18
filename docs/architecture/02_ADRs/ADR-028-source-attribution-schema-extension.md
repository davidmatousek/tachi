# ADR-028: Source Attribution Schema Extension

**Status**: Accepted
**Date**: 2026-04-17 (Proposed); 2026-04-17 (Accepted — provisional; confirmed at post-merge SHA fill)
**Accepted-commit-SHA**: `<pending-post-merge-fill>`
**Deciders**: Architect, Product Manager, Team-Lead
**Feature**: 189 (F-A2 Source Attribution Schema Extension)
**Related ADRs**: [ADR-020](ADR-020-maestro-layer-classification.md) (MAESTRO classification — additive-optional-field precedent), [ADR-021](ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md) (SOURCE_DATE_EPOCH determinism), [ADR-023](ADR-023-threat-agent-skill-references-pattern.md) (22-file zero-edit invariant), [ADR-026](ADR-026-pattern-classification-mechanism.md) (minor-bump rule — extended here), [ADR-027](ADR-027-taxonomy-crosswalk-schema.md) (F-A1 taxonomy schema — direct predecessor)

---

## Context

Tachi's agentic-AI threat-modeling pipeline emits findings (the atomic unit of threat analysis output) conforming to `schemas/finding.yaml`, currently at schema_version 1.4 per Feature 142. Each finding carries category (STRIDE+AI), component, threat narrative, risk level, mitigation prose, and a handful of additive-optional enum fields added in prior features (`maestro_layer` per ADR-020, `agentic_pattern` per ADR-026, `delta_status` and `baseline_run_id` per Feature 104). Every finding also carries a free-text `references` list-of-string that threat agents populate today with citation URLs and external-framework identifiers (OWASP LLM05, CWE-1426, MITRE ATLAS AML.T0051, NIST MEASURE 2.7, and so on).

Feature 180 (F-A1) shipped 2026-04-17 (squash-merge commit `8b7c7bf`) as the first feature in the BLP-01 Foundation tier. F-A1 delivered 7 machine-readable taxonomy catalogs under `schemas/taxonomy/` plus a 526-edge cross-framework `crosswalk.yaml`, governed by ADR-027. F-A1 is a pure reference-data feature: no pipeline stage consumes the YAMLs at runtime yet, and the zero-runtime-touch invariant (ADR-027 Reason 5) was preserved by construction. F-A1 is the supply side of a two-feature bridge — it publishes the framework-ID vocabulary downstream coverage consumers will join against.

Feature 189 (F-A2 — this ADR) is the demand-side bridge. Today every adopter who wants to aggregate tachi output across OWASP, CWE, MITRE, or NIST IDs must text-parse the `references` list-of-string and the agent markdown prose, since the citations live embedded in narrative text. This works for a human reading a single report; it fails for any programmatic consumer (vulnerability manager, SIEM, compliance dashboard, F-B coverage attestation report). F-A2 extends `schemas/finding.yaml` with a new optional `source_attribution` field — an array of 3-field records `{taxonomy, id, relationship}` — that carries the same citation information as a machine-readable list keyed by the F-A1 catalog vocabulary. Together F-A1 and F-A2 let every downstream consumer resolve "what framework items does finding X cite?" via a single `yaml.safe_load` plus a closed-enum field lookup, with zero text-parsing.

F-A2 deliberately narrows its scope to the **data-contract layer**. It does not populate the new field, and it does not wire any downstream consumer. Two explicit follow-on features are carved out: F-A3 (the **populator** feature — threat agents emit `source_attribution` values during detection, touching the 11 detection agents and their 11 companion skill-reference files) and F-B (the **coverage attestation** feature — a new section in the security report that joins `source_attribution` arrays against `schemas/taxonomy/crosswalk.yaml` to compute per-framework coverage claims). F-A2's contract-only posture is what preserves the 22-file zero-edit invariant from ADR-023 and the byte-identity SC-2 gate from ADR-021 — the 5 non-agentic baselines ship with absent `source_attribution` on every finding, no serialization surface emits, and every regenerated PDF is byte-identical.

PRD 189 was approved 2026-04-17 with full Triad sign-off; the spec was PM-approved same day with 1:1 PRD-to-spec mapping preserved. The PRD and spec are deliberately surface-neutral on two questions that are architect-authority: **Q1** (the serialization surface for `source_attribution` in `threats.md` or a co-emitted artifact) and **Q2** (the pipeline phase at which referential-integrity validation runs). Both questions are resolved in this ADR.

### Constraints

- **Byte-identity backward compatibility** (spec SC-002, FR-012): the 5 non-agentic example PDFs (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) MUST regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000` per ADR-021. Any Q1 resolution that emits a non-empty `threats.md` section when no finding carries attribution regresses the gate. The 5 baselines have absent `source_attribution` on every finding today and in F-A2 — F-A3 is the populator feature.
- **22-file zero-edit invariant** (spec SC-007, FR-015): F-A2 MUST NOT edit any file under `.claude/agents/tachi/stride/` (6 files), `.claude/agents/tachi/ai/` (5 files), or `.claude/skills/tachi-{agent-name}/references/detection-patterns.md` (11 files). ADR-023 Decision 2 stabilized this 22-file scope as the detection-tier boundary. F-A2 is the contract feature; F-A3 is the populator feature that may edit these surfaces.
- **Zero new runtime dependencies** (spec SC-006, FR-016): empty diffs on `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, and `package.json`. `pyyaml` and `pytest` are developer-only per Feature 128; no runtime additions are permitted.
- **ADR-021 determinism**: any validation helper introduced by F-A2 MUST be a pure function of its inputs — no HTTP fetches, no timestamps, no environment reads beyond `SOURCE_DATE_EPOCH` (which only the existing Typst harness consumes). No module-level mutable state. Per-invocation caches scoped to a local dict only.
- **ADR-027 referential anchor**: F-A2's `source_attribution.id` lookups resolve against the F-A1 catalog YAMLs. F-A2 MUST NOT modify any file under `schemas/taxonomy/` — F-A1 is the authoritative source of framework IDs.
- **ADR-026 schema-versioning discipline**: the 1.4 → 1.5 bump is only a minor bump if the ADR-026 conditions hold (additive, has default, schema shape unchanged). Decision 1 below records the extension of the ADR-026 rule to list-of-RECORD fields.
- **Q1 and Q2 are architect-authority**: spec FR-007, FR-008, and FR-010 are deliberately surface-neutral and phase-neutral. The ADR Proposed commit at Day 1 Wave 1.1 is the schema-lock point that resolves both questions and unblocks parallel authoring in Wave 2.1 and beyond.

---

## Decision

We adopt the **F-A2 source attribution schema extension** as specified below. `schemas/finding.yaml` bumps from schema_version 1.4 to 1.5; a new optional list-of-RECORD field `source_attribution` is appended to the `finding:` mapping; the `parse_threats_findings` parser at `scripts/tachi_parsers.py:621` gains a conditional-key round-trip for the field; a new validation helper `validate_source_attribution` runs post-parse at orchestrator Phase 4; and a new conditional `## 9. Source Attribution` YAML block in `threats.md` carries the serialization payload. Seven numbered decisions below document the contract.

### Decision 1 — Additive-optional-field bump under the ADR-026 Complex-Shape Addition Clarifier

`schemas/finding.yaml` bumps from `schema_version: "1.4"` to `schema_version: "1.5"` — a **minor bump** under the ADR-026 minor-bump rule, extended here to cover **list-of-RECORD** fields.

ADR-026's minor-bump rule (authored for Feature 142's `agentic_pattern` enum addition) permits a minor bump when three conditions hold: (a) the new field is additive (no existing field is removed, renamed, or re-typed), (b) the new field has a default value that preserves backward compatibility for parsers reading absent data, and (c) the schema document's top-level shape and existing required fields are unchanged. ADR-026 documents the rule for NEW enum-typed **scalar** field additions (e.g., `agentic_pattern: string`).

F-A2 extends the ADR-026 rule to **list-of-RECORD** fields — this is the first such extension in tachi's schema evolution. The three conditions hold for `source_attribution`:

| ADR-026 Condition | How F-A2 Satisfies It |
|-------------------|------------------------|
| (a) Additive | All 14 pre-existing schema 1.4 fields retain type signatures verbatim. `source_attribution` is appended as the 15th top-level field under `finding:`. No removal, rename, or re-typing. |
| (b) Has default | The FIELD's default state is **absent** (the field is omitted entirely when a finding cites no framework items — not present as `[]`). The per-RECORD optional `relationship` field has default `primary`, injected by the parser when absent on input. Callers reading schema 1.5 output against schema 1.4 expectations see no new key. |
| (c) Schema shape unchanged | Top-level `finding:` mapping remains a single-key document. No new required field is added. No cross-field required-when rule is introduced. The document's top-level serialization shape is unchanged. |

We label this extension the **Complex-Shape Addition Clarifier**: the ADR-026 rule applies uniformly to list-of-RECORD fields when the three conditions hold at both the FIELD tier (optional, default-absent) and the RECORD tier (optional per-record fields have defaults, record shape is closed by its published contract). Future list-of-RECORD additions MAY cite this ADR to invoke the same clarifier; other complex-shape additions (e.g., dict-of-record, list-of-list-of-scalar) require explicit future-ADR extension before invoking the minor-bump rule.

**Scope boundary**: the Complex-Shape Addition Clarifier does NOT authorize schema-rename, enum-value-removal, or required-field-addition changes under the minor-bump rule. Those remain major-bump changes regardless of list-vs-scalar typing. The Clarifier is a typing-generalization of the existing additive-compatibility rule, not a scope expansion.

### Decision 2 — Serialization surface: conditional `## 9. Source Attribution` YAML block in `threats.md` (Q1)

We select **Q1-E** as the F-A2 serialization surface: a new conditional `## 9. Source Attribution` section in `threats.md`, rendered only when at least one finding carries `source_attribution`, containing a single YAML code fence keyed by finding ID. **Q1-B** (sidecar YAML file `threats-attribution.yaml` co-located with `threats.md`) is documented as the **fallback escape hatch** — F-A3 MAY invoke the fallback IF per-finding attribution populator logic emits payloads whose Section 9 rendering would be too large for readable inline presentation in `threats.md`. F-A2 does NOT implement the fallback; it documents the invocation protocol.

**Section 9 shape** (F-A2 contract):

```markdown
## 9. Source Attribution

```yaml
source_attribution:
  T-1:
    - taxonomy: owasp
      id: LLM05
      relationship: primary
    - taxonomy: cwe
      id: CWE-1426
      relationship: primary
  I-3:
    - taxonomy: mitre-atlas
      id: AML.T0051
      relationship: related
```
```

The outer YAML document key is always the literal string `source_attribution:`. Each second-level key is a finding ID (matching the `^(S|T|R|I|D|E|AG|LLM|AGP)-\d+$` pattern from schema 1.4). Each value is a list of SourceAttributionRecord entries as specified in Decision 3 and Decision 4.

**Gating rule** (Feature 141 `has-attack-chains` precedent): the orchestrator computes a `has-source-attribution` boolean at write time. If any finding in the current threat model carries `source_attribution`, the boolean is `true` and Section 9 is rendered. If no finding carries `source_attribution`, the boolean is `false` and Section 9 is **omitted entirely** — no section header, no empty code fence, no trailing separator. This is the direct Feature 141 Section 6 conditional-section convention.

**Backward-compatibility argument** (SC-2 preservation): the 5 non-agentic baseline threat models have absent `source_attribution` on every finding today and through F-A2 merge. The `has-source-attribution` boolean evaluates to `false` on all 5. Section 9 is omitted from every baseline `threats.md`. Downstream `threat-report.md`, SARIF export, PDF rendering, and all Typst templates are unchanged by F-A2 (F-A3 scope). Therefore every byte of every baseline artifact is unchanged, and SC-002 holds by construction.

**Why Q1-E over Q1-B as primary**:
- Q1-E keeps attribution data co-located with its findings. A reader opening `threats.md` sees the finding table in §7 and the attribution data in §9 without juggling files.
- Q1-E inherits the Feature 141 `has-attack-chains` gating pattern, which is already proven against the byte-identity harness across Feature 141's Section 6 delivery. No new gating convention is introduced.
- Q1-B (sidecar file) requires F-A3 populators to emit a second artifact alongside `threats.md`, multiplying the write-surface for every threat model run. Q1-E uses a single write target.

**Why Q1-B is documented as fallback, not rejected**: if F-A3's populator logic emits attribution payloads large enough to make Section 9 rendering unreadable (hundreds of findings × tens of records each), the readability cost may outweigh the co-location benefit. F-A3 is the feature that will measure this in practice. F-A2 documents the fallback invocation protocol: F-A3 MAY, on an architect decision recorded in a follow-on ADR amendment to this one, migrate the serialization surface from Section 9 to a sidecar file `threats-attribution.yaml` co-located with `threats.md`. The parser contract in Decision 5 is written to accommodate either surface without schema version change — the switch is an internal implementation detail of `_extract_source_attribution` and does NOT trigger another schema bump.

**Why Q1-A (cell-string column in §7 finding table) and Q1-D (new Section 8 rendered in PDF) are rejected**: per PRD 189 §Options, Q1-A collapses nested-record structure into a single cell string, losing the `relationship` enum and the ordered list semantics — this forces downstream consumers to re-parse delimited text and defeats the F-A2 point. Q1-D commits F-A2 to modifying `extract-report-data.py` and a new Typst template, which violates SC-2 (the PDF is a baseline artifact) and blurs the contract-vs-populator scope boundary.

### Decision 3 — `taxonomy` field: closed 5-value enum (external frameworks only)

The `SourceAttributionRecord.taxonomy` field is a closed enum with exactly **5 values**, corresponding to the external-framework subset of F-A1's 7-value taxonomy enum:

| Value | F-A1 Catalog YAML |
|-------|---------------------|
| `owasp` | `schemas/taxonomy/owasp.yaml` |
| `mitre-attack` | `schemas/taxonomy/mitre-attack.yaml` |
| `mitre-atlas` | `schemas/taxonomy/mitre-atlas.yaml` |
| `nist-ai-rmf` | `schemas/taxonomy/nist-ai-rmf.yaml` |
| `cwe` | `schemas/taxonomy/cwe.yaml` |

The 2 internal tachi taxonomies from ADR-027 Decision 3 — `tachi-control-category` and `tachi-stride-ai-category` — are **deliberately EXCLUDED** from the F-A2 enum. This is an architecturally material narrowing of F-A1's 7-value enum into F-A2's 5-value enum.

**Rationale — the cite-vs-categorize distinction**: ADR-027 Decision 3 includes the 2 internal tachi taxonomies as first-class participants in crosswalk edges. Crosswalk edges express "framework X's item maps to tachi's category Y" relationships — bidirectional, and the internal taxonomies participate on BOTH sides (source and target). The crosswalk is answering the question "what does this framework item correspond to in tachi's published vocabulary?"

F-A2 answers a different question: "what external-framework items does this finding *cite*?" The 2 internal tachi taxonomies are tachi's own output vocabulary — they are the categorization tachi applies to findings (via the existing `category` field in schema 1.0 and the existing compensating-control analysis), not a framework tachi claims coverage of. A finding citing `tachi-stride-ai-category: spoofing` would be a self-referential claim (the finding is already categorized as STRIDE Spoofing via the schema 1.0 `category` field); a finding citing `tachi-control-category: authentication` would be a control-analysis output claim that belongs in `compensating-controls.md`, not in a source-attribution field.

**Downstream-impact argument**: cross-scope mixing (external frameworks + internal taxonomies in the same array) would allow coverage dashboards consuming `source_attribution` to aggregate self-referential claims alongside external-framework claims, inflating coverage numbers. A dashboard counting "how many findings cite 3+ framework items" would count a finding citing `{owasp: LLM05, tachi-stride-ai-category: prompt-injection, tachi-control-category: input-validation}` as 3-framework when in fact it cites 1 external framework plus 2 internal self-references. The 5-value external-only enum forecloses this class of error at the schema layer.

**Forward compatibility**: if a future feature requires bidirectional internal-taxonomy references (e.g., a finding-level annotation that a finding IS categorized under both `tachi-stride-ai-category` and `tachi-control-category`), that feature may author a distinct schema field (e.g., `internal_categorization`) with its own enum. It MUST NOT reuse `source_attribution` for internal self-references. A future ADR extending `source_attribution` to include internal taxonomies would require explicit architect re-evaluation of the cite-vs-categorize boundary.

### Decision 4 — `relationship` field: closed 3-value enum with default-to-`primary`

The `SourceAttributionRecord.relationship` field is a closed enum with exactly **3 values**:

| Value | Semantics |
|-------|-----------|
| `primary` | The finding's canonical framework mapping — "this finding directly addresses this framework item." The overwhelmingly common case. |
| `related` | An adjacent mapping — the framework item is semantically related to the finding but is not the canonical mapping (e.g., a CWE parent when the finding's primary is a more-specific child CWE). |
| `derived` | An inferred mapping — the framework item is derived from another citation (e.g., a NIST Subcategory derived from the primary OWASP item via a crosswalk edge). Downstream consumers MAY weight `derived` records lower in coverage-percentage aggregations than `primary` records. |

**Default injection**: when the `relationship` key is absent on an input record, the parser MUST inject `relationship: "primary"` at emission time. The parser's output contract is "every emitted record has all three keys populated" — consumers never need to handle the absent-relationship case. This is distinct from the FIELD-tier conditional-key rule (Decision 5), which concerns whether the `source_attribution` key is present on the finding object at all.

**Rationale — distinguish canonical from adjacent citations**: without the `relationship` enum, every downstream consumer would reinvent relationship vocabulary to distinguish "this finding really addresses this item" from "this item is tangentially mentioned." Closed enums are the tachi convention for schema fields whose value space is small and known (per ADR-027 Rationale Reason 2). Reserving `related` and `derived` as authorized-and-populated values at schema-freeze point (in contrast to ADR-027 Decision 4's deferred-population `edge_type` values) reflects that F-A2 expects all three values to be used by F-A3 populators from the outset — the enum is closed to prevent drift, not to defer population.

**Rationale — default-to-`primary`**: the overwhelmingly common case is a finding directly addressing a framework item. Defaulting to `primary` when `relationship` is absent reduces the boilerplate every F-A3 populator would otherwise emit. The alternative defaults considered were:
- `related` (rejected — too conservative; would cause downstream coverage dashboards to under-count canonical mappings by default)
- `derived` (rejected — semantically narrow; `derived` implies a second-hop inference that most primary citations are not)
- no default, field always required (rejected — imposes boilerplate cost on F-A3 populators with no downstream benefit)

**Relationship to ADR-027 `edge_type`**: ADR-027's `edge_type` enum on crosswalk edges uses `{primary, related, superseded}`. F-A2's `relationship` enum on source-attribution records uses `{primary, related, derived}`. The two enums share the `primary` and `related` values but diverge on the third: `superseded` is a crosswalk-edge concept (mapping X has been superseded by mapping Y due to framework evolution) that has no finding-level analog; `derived` is a finding-citation concept (this citation was inferred from another) that has no crosswalk-edge analog. The enums are intentionally distinct and MUST NOT be conflated — downstream consumers joining `source_attribution.relationship` against `crosswalk.edge_type` MUST treat them as independent vocabularies.

### Decision 5 — Referential-integrity contract: two-tier validation with separate post-parse helper (Q2)

We select **Q2-B** as the F-A2 validation architecture: a two-tier model with parser-tier enum validation and a separate post-parse referential-integrity validator.

**Tier 1 — parser-tier enum validation** (inline in `parse_threats_findings`): on every record read, the parser validates:
- V1: `taxonomy ∈ {owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe}` (closed 5-value enum per Decision 3)
- V2: `relationship ∈ {primary, related, derived}` (closed 3-value enum per Decision 4, after default-injection)
- V3: `id` is a non-empty string
- V5: record has exactly the key set `{taxonomy, id}` or `{taxonomy, id, relationship}` (no extra keys)

Parser-tier violations raise `ValueError` with a structured message naming the finding ID, the bad value, and the closed-domain list. This fails fast at parse time — the same pattern used by other schema-enum validation in `tachi_parsers.py`.

**Tier 2 — referential-integrity validator** (new function, separate phase): a new helper `validate_source_attribution(findings: list[dict], taxonomy_dir: Path = Path("schemas/taxonomy")) -> list[ValidationError]` is added to `scripts/tachi_parsers.py` alongside `parse_threats_findings`. For every finding with `source_attribution`, for every record, the helper loads `taxonomy_dir/{record.taxonomy}.yaml` and asserts that `record.id` resolves as a top-level `id:` key in the catalog. Unresolved IDs yield structured `ValidationError(finding_id, record, target_yaml_path, reason)` entries. The helper returns an empty list on success or a non-empty list on failure — callers decide whether to raise or log (structured-error return is the tachi convention for validators whose failure mode is non-fatal-observability per ADR-006).

**Canonical caller — orchestrator Phase 4 ("Assess")**: the `validate_source_attribution` helper is invoked at the start of orchestrator Phase 4, after Phase 3 deduplication and Phase 3.5/3.6 synthesis complete and before Phase 4 risk assessment begins. Phase 4 is the first phase that reads the final finding IR and therefore the natural enforcement point for a contract that depends on the full deduplicated set. Alternative phase placements considered:
- Phase 1 (dispatch) — too early; findings don't exist yet
- Phase 2 (detection) — would require every threat agent to invoke the validator, violating the 22-file zero-edit invariant
- Phase 3 (deduplication) — duplicates validation work across the per-agent finding flows; couples dedup to taxonomy-lookup I/O
- Phase 5 (report assembly) — too late; a validation error surfaces only after report rendering has started

**ADR-021 determinism preservation**: the validator is a pure function of its inputs. It reads `schemas/taxonomy/*.yaml` from the local filesystem (no HTTP), performs no timestamp reads, and accesses no environment variables. The per-invocation cache is scoped to a **local dict** in the validator's call frame — loading the same taxonomy YAML twice within a single `validate_source_attribution` call hits the cache; a second call from a separate Phase 4 invocation re-loads from disk. No module-level state, no cross-invocation memoization — this preserves ADR-021 determinism AND prevents test-state leakage between fixture-driven pytest runs.

**Caching scope and correctness**: the local-dict cache is keyed by taxonomy name (one of the 5 enum values) and maps to the parsed YAML. Within a single call processing N findings with total M records across K unique taxonomies, the validator performs at most K disk reads (not M). This mitigates PRD Risk R3 (parse-time bloat from repeated F-A1 YAML reads) without introducing module-level state that could cause cross-test contamination.

**CLI exposure**: a standalone `scripts/validate_source_attribution.py` CLI entry point is **optional** and out of F-A2 scope if the orchestrator Phase 4 direct invocation suffices for the contract feature. F-A3 populators may re-introduce the CLI if development-time validation ergonomics warrant it — that is an F-A3 decision, not an F-A2 commitment.

**Why Q2-B over Q2-A (all-in-parser validation)**: Q2-A would couple `parse_threats_findings` to filesystem layout (the parser would need `schemas/taxonomy/` as an implicit dependency). Parser hot-path I/O would bloat parse time for every threat model run, including runs that do not need attribution validation (e.g., standalone parser invocations from debugging or ad-hoc tooling). Q2-B keeps the parser pure (string input → structured output) and isolates I/O to the dedicated validator, matching the tachi convention of thin parsers + separate validators.

### Decision 6 — Zero-edit invariant on the 22-file detection tier (ADR-023 lineage)

F-A2 MUST NOT edit any file in the 22-file zero-edit scope enumerated in ADR-023 Decision 2. The scope is grep-auditable:

**STRIDE agent files (6)** — flat layout under `.claude/agents/tachi/`:
- `.claude/agents/tachi/spoofing.md`
- `.claude/agents/tachi/tampering.md`
- `.claude/agents/tachi/repudiation.md`
- `.claude/agents/tachi/info-disclosure.md`
- `.claude/agents/tachi/denial-of-service.md`
- `.claude/agents/tachi/privilege-escalation.md`

**AI agent files (5)** — flat layout under `.claude/agents/tachi/`:
- `.claude/agents/tachi/prompt-injection.md`
- `.claude/agents/tachi/data-poisoning.md`
- `.claude/agents/tachi/model-theft.md`
- `.claude/agents/tachi/tool-abuse.md`
- `.claude/agents/tachi/agent-autonomy.md`

**Skill-reference files (11)** — one per agent above:
- `.claude/skills/tachi-spoofing/references/detection-patterns.md`
- `.claude/skills/tachi-tampering/references/detection-patterns.md`
- `.claude/skills/tachi-repudiation/references/detection-patterns.md`
- `.claude/skills/tachi-info-disclosure/references/detection-patterns.md`
- `.claude/skills/tachi-denial-of-service/references/detection-patterns.md`
- `.claude/skills/tachi-privilege-escalation/references/detection-patterns.md`
- `.claude/skills/tachi-prompt-injection/references/detection-patterns.md`
- `.claude/skills/tachi-data-poisoning/references/detection-patterns.md`
- `.claude/skills/tachi-model-theft/references/detection-patterns.md`
- `.claude/skills/tachi-tool-abuse/references/detection-patterns.md`
- `.claude/skills/tachi-agent-autonomy/references/detection-patterns.md`

**Rationale — ADR-023 sibling-pattern governance**: ADR-023 stabilized the 11-agent skill-references pattern in Feature 082 with explicit "do not reopen existing agents" governance. The 22-file scope is the combined detection-tier surface — 11 agent files plus 11 companion skill-reference files. F-A2 is structurally a schema + parser + validator feature; none of its acceptance criteria require detection-agent behavioral changes. Preserving the 22-file boundary keeps the contract feature (F-A2) and the populator feature (F-A3) on separate review cycles, with F-A3 bearing the regression risk of reopening the detection tier.

**Scope boundary — F-A2 contract vs F-A3 populator**:
- F-A2 (this feature) ships the schema field, the parser round-trip, the validator, the ADR, and the tests. It does NOT emit any attribution data. Zero of the 22 files are touched.
- F-A3 (follow-on feature) wires the populators — threat-detection agents emit `source_attribution` values during detection. F-A3 MAY edit the 22 files AND MAY extend the downstream consumer surface (risk-scorer, control-analyzer, threat-report, SARIF exporter, Typst templates). F-A3 is governed by its own PRD and ADR.

**Enforcement — grep-auditable**: the F-A2 PR is blocked from merge if `git diff main..HEAD --name-only` returns any file in the 22-file scope. This is enforced at PR review time by the team-lead per spec SC-007.

**Downstream silence — F-A2 consumers are read-only no-ops**: the risk-scorer, control-analyzer, threat-report, threat-infographic, report-assembler, `extract-report-data.py`, `extract-infographic-data.py`, and all Typst templates under `templates/tachi/` are also NOT edited in F-A2. These surfaces read `threats.md` and derived artifacts today; in F-A2 they continue to read the same fields they already read. The new `source_attribution` field is ignored by every downstream consumer in F-A2 — F-A3 is the feature that wires consumer awareness.

### Decision 7 — Governance Protocol (Proposed → Accepted dual-commit)

This ADR is authored in **Status: Proposed** at Day 1 Wave 1.1 of the F-A2 implementation (2026-04-20, the Monday after spec approval). The Proposed commit serves as the schema-lock point that unblocks parallel authoring in Wave 2.1 and beyond — specifically, the `schemas/finding.yaml` 1.4 → 1.5 diff, the test fixtures under `tests/scripts/fixtures/source_attribution/`, and the parser extension work can all begin once Q1 and Q2 are resolved in this ADR's Proposed commit.

**Protocol**:
- **Day 1 Wave 1.1 (2026-04-20 AM)** — ADR authored with `Status: Proposed`, `Accepted-commit-SHA: <pending-post-merge-fill>`, and the Accepted-date line carrying `TBD (Accepted — pending PR merge)`. This commit lands on the feature branch and is the schema-lock signal. All six Decision sections are fully populated at Proposed time; no Decision field is deferred to Accepted.
- **Day 3 Wave 6.1 (2026-04-22 PM, pre-merge)** — ADR transitions to `Status: Accepted` with `Accepted-date: 2026-04-22` (provisional; may be corrected at post-merge if merge slips) and `Accepted-commit-SHA: <pending-post-merge-fill>` (unchanged placeholder). This transition is recorded as a Revision History entry dated 2026-04-22.
- **Post-merge (T036)** — the `<pending-post-merge-fill>` placeholder is replaced with the actual squash-merge commit SHA. If the merge date differs from the provisional 2026-04-22, the Accepted-date is NOT retroactively corrected per ADR-027 T039 precedent (the provisional date reflects the Day 3 Wave 6.1 authoring-time projection; correcting it would retcon the transition record without adding provenance value beyond the new SHA field).

**Prior art**: this protocol mirrors ADR-027 Decision 8 (F-A1 taxonomy schema — direct predecessor) and the earlier ADR-024 / ADR-025 dual-commit precedent. The dual-commit pattern has three concrete benefits: (1) the Day 1 Proposed commit is an authoritative schema-lock point that unblocks parallel work without waiting for PR merge, (2) the Accepted commit at merge captures the final decision record with the specific decisions ratified, and (3) the post-merge SHA fill completes the provenance chain so the ADR carries a verifiable pointer to the commit that implemented it.

**Rationale — why not single-commit-at-merge**: authoring the ADR only at PR merge would lose the Day 1 schema-lock signal that unblocks Wave 2.1+ parallel work. Wave 2.1 authors need the Q1 and Q2 resolutions (and the Decision 3-4 enum definitions) to write their tests and fixtures correctly; waiting until merge to publish those resolutions would serialize Wave 1 and Wave 2 artificially. The dual-commit pattern is optimal for features whose schema-lock ADR content drives parallel downstream authoring.

---

## Alternatives Considered

### Alternative 1 — Always-inject `source_attribution: []` default

Every finding object emitted by `parse_threats_findings` always carries the `source_attribution` key; when no attribution data is present on the finding, the value is `[]`.

**Pros**:
- Simpler parser contract — consumers never need to handle the absent-key case
- Matches the `agentic_pattern` always-inject convention (schema 1.4) where every emitted finding carries the field defaulted to `"none"`

**Cons**:
- Violates AC-1 of US-189-2: "parser omits the key on absent-path findings" — an explicit product-tier requirement
- Breaks the semantic distinction between absent (no claim made) and present-but-empty (explicitly no attribution claimed) — these are two distinct states that downstream consumers may need to distinguish for coverage-policy reasons
- Would regress byte-identity on downstream artifacts that serialize the finding object (SARIF emission, JSON export if ever introduced) — every baseline finding would gain an empty-list key
- Does not match the Feature 104 `delta_status` conditional-key precedent, which the PRD explicitly cites as the shape to follow

**Why Not Chosen**: the PRD AC is explicit (conditional-key, not always-inject), the Feature 104 precedent exists and is the correct mental model for an optional attribution-bearing field, and the absent-vs-empty semantic distinction is non-trivial for coverage consumers. The slight consumer-side simplicity benefit is outweighed by the semantic loss and the AC violation.

### Alternative 2 — 7-value `taxonomy` enum matching F-A1's crosswalk enum

The F-A2 `source_attribution.taxonomy` field accepts all 7 values from ADR-027 Decision 3, including the 2 internal taxonomies (`tachi-control-category`, `tachi-stride-ai-category`).

**Pros**:
- Consistency with F-A1 — one enum definition reused everywhere
- Forward-compatible — any future use case requiring internal-taxonomy references is already schema-supported

**Cons**:
- Blurs the cite-vs-categorize boundary (Decision 3 rationale) — internal taxonomies are tachi's output vocabulary, not frameworks tachi claims coverage of
- Enables cross-scope mixing in downstream coverage aggregation — a dashboard counting "framework items cited" would over-count findings that mix external citations with internal self-references
- The 2 internal taxonomies are the RECIPIENT side of F-A1 crosswalk edges; making them the CITED side in F-A2 changes their semantic role across two schema surfaces, which is confusing

**Why Not Chosen**: F-A2 and F-A1 answer different questions (cite vs map), and the 5-value narrowing forecloses a class of coverage-aggregation errors at the schema layer. If a future feature genuinely requires internal-taxonomy references on findings, it SHOULD introduce a distinct schema field with its own enum rather than overload `source_attribution`. The consistency cost is paid by one ADR cross-reference (this ADR Decision 3 explicitly references ADR-027 Decision 3) rather than by a widened enum surface.

### Alternative 3 — All-in-parser validation (Q2-A)

Referential-integrity validation (V4) runs inline inside `parse_threats_findings`, alongside the parser-tier enum validation (V1/V2/V3/V5). The parser reads `schemas/taxonomy/*.yaml` on every invocation.

**Pros**:
- Single validation pass — all failure modes surface at parse time
- Simplest orchestrator integration — Phase 4 doesn't need a separate validation step

**Cons**:
- Couples the parser to filesystem layout — `parse_threats_findings` would have a hidden dependency on `schemas/taxonomy/` being present and well-formed. Standalone parser invocations (e.g., debugging tools, ad-hoc analysis) would fail or need workaround flags when the taxonomy directory is absent
- Parser hot-path I/O — every parse reads up to 5 YAML files, even when the parse is for a legacy (pre-F-A2) threat model with no attribution data
- Violates the tachi convention of thin parsers + separate validators (consistent with V1-V5 two-tier split in `data-model.md`)
- Harder to test — parser tests for non-attribution paths would need to mock filesystem access to the taxonomy directory

**Why Not Chosen**: Q2-B (two-tier split with separate post-parse validator) keeps the parser pure and isolates I/O to the dedicated validator. The orchestrator Phase 4 invocation cost is one function call; the alternative's parse-time bloat and hidden-filesystem-dependency costs are every-parse-call charges. The two-tier split is also the shape that lets F-A3 populators invoke the validator independently (e.g., as a pre-emission check) without re-running the full parser.

### Alternative 4 — Q1-A cell-string column addition in `threats.md` Section 7

The existing §7 finding table in `threats.md` gains a new "Source Attribution" column, and `source_attribution` records are serialized as delimited strings (e.g., `owasp:LLM05:primary; cwe:CWE-1426:primary; mitre-atlas:AML.T0051:related`) in that column.

**Pros**:
- Co-locates attribution with the finding row — a reader scanning §7 sees attribution immediately
- No new section — minimal structural change to `threats.md`
- Matches the convention of §7 carrying all per-finding fields

**Cons**:
- Collapses nested-record structure into a single cell string — loses the `relationship` enum as a first-class field, loses the ordered-list semantics, loses per-record key-value structure
- Forces downstream consumers to re-parse delimited text — defeats the F-A2 point of making attribution machine-readable
- No natural way to represent empty arrays vs absent — the cell is either empty (ambiguous) or carries a sentinel value (adds a new convention)
- Column additions to §7 historically trigger byte-identity sensitivity on the 5 baselines (§7 is rendered on every threat model); SC-2 preservation would require careful conditional-column logic

**Why Not Chosen**: this alternative was rejected at PRD time (PRD 189 §Options rejected Q1-A outright). The Q1-E conditional-section shape solves the byte-identity problem (Section 9 omitted when no attribution exists) and preserves first-class nested-record structure (YAML code fence, not delimited string). The §7 column approach is a regression in both machine-readability and byte-identity risk.

---

## Consequences

### Positive

- **Machine-readable source-attribution contract for F-A3 and F-B**. Downstream populators (F-A3) and coverage consumers (F-B, ecosystem integrators) can read `source_attribution` arrays with a single `yaml.safe_load` and resolve framework IDs against F-A1 catalogs with a single dict lookup. The pattern generalizes to any future ecosystem integrator that needs to aggregate tachi output across multiple frameworks.
- **ADR-026 rule extension to list-of-RECORD fields**. The Complex-Shape Addition Clarifier is a durable precedent for future schema evolutions. Any future list-of-RECORD addition meeting the three ADR-026 conditions (additive, has default, schema shape unchanged) can invoke this ADR to justify a minor-bump rather than a major-bump.
- **Closed-enum filterability at both tiers**. The 5-value `taxonomy` enum and the 3-value `relationship` enum make every `source_attribution` record programmatically filterable without free-text parsing. Coverage dashboards can compute per-framework counts, per-relationship weights, and per-finding citation-density metrics directly from the field.
- **Zero regression on the 22-file detection tier**. ADR-023 stabilization holds. The 11 detection agents and their 11 skill-reference files are byte-identical at F-A2 merge. F-A3 bears the regression risk of reopening the detection tier.
- **SC-2 byte-identity preserved by construction**. The Q1-E conditional Section 9 is omitted entirely on the 5 non-agentic baselines (`has-source-attribution: false` on all 5). No byte of any baseline artifact changes. The SC-2 gate is green at merge without any special-case harness work.
- **Zero new runtime dependencies**. Empty diffs on `pyproject.toml`, `requirements*.txt`, and `package.json`. `pyyaml` and `pytest` remain developer-only per Feature 128.
- **Determinism preserved**. The validator is a pure function with per-invocation local-dict caching; no HTTP, no timestamps, no module-level state, no environment reads. ADR-021 byte-identity harness consumes no new knobs.
- **F-A3 scope is well-defined by F-A2's explicit deferrals**. Every F-A3 surface is documented: populators on the 22-file detection tier, consumers on risk-scorer, control-analyzer, threat-report, SARIF exporter, Typst templates. F-A3 PRD authoring starts from a fully-specified surface list.
- **Forward-compatible fallback documented**. The Q1-B sidecar file is the documented escape hatch if F-A3's populator payloads overwhelm Section 9 readability. Switching serialization surfaces does NOT require a schema version bump — the internal parser helper `_extract_source_attribution` absorbs the change.

### Negative

- **F-A3 downstream surface is combinatorially larger than F-A2 surface**. F-A3 must design 3 distinct downstream consumer integrations (risk-scorer, control-analyzer, threat-report) plus SARIF emission plus Typst template updates — each a separate design decision. PRD 189 Risk R2 captures this combinatorial burden; F-A2 inherits it only as a documentation obligation, but F-A3 bears the full design cost.
- **Section 9 byte-sensitivity under F-A3 populators**. When F-A3 starts emitting attribution data, the `agentic-app` baseline (which F-A3 will regenerate) and any new baselines carrying attribution will be byte-sensitive to Section 9 rendering details (YAML indentation, key ordering within records, list-element ordering). F-A2 sets the shape; F-A3 must be disciplined about rendering determinism (e.g., sorted record emission within each finding's list). Mitigated by the Feature 141 `has-attack-chains` precedent, which has already proven rendering determinism for conditional YAML sections.
- **Validator filesystem coupling**. The `validate_source_attribution` helper reads `schemas/taxonomy/*.yaml` at invocation time. If a future refactor moves or renames the taxonomy directory, the validator needs an update. Mitigated by the `taxonomy_dir` parameter (default `Path("schemas/taxonomy")`) which is overridable for test fixtures and future path changes.
- **Fixture authoring burden**. F-A2 requires 7 fixture files under `tests/scripts/fixtures/source_attribution/` (4 valid + 3 invalid) plus round-trip and validation test coverage. This adds to the already-substantial fixture surface from Feature 128 + 142. Mitigated by fixture reuse across multiple test functions (one fixture serves multiple acceptance criteria per the data-model.md traceability table).
- **Two-tier validation model is subtle**. The distinction between parser-tier enum validation (V1/V2/V3/V5, raises immediately) and validator-tier referential integrity (V4, returns structured errors) is a non-trivial mental model for F-A3 and future maintainers. Mitigated by explicit Decision 5 documentation and by the `data-model.md` V1-V6 traceability section.
- **Future ADR amendment burden for fallback invocation**. If F-A3 invokes the Q1-B sidecar fallback per Decision 2, an ADR amendment to this ADR is required recording the migration rationale. This is a deliberate governance cost — the fallback is not automatic; it is an architect decision.

### Neutral

- **Divergence from `agentic_pattern` always-inject convention**. Schema 1.4's `agentic_pattern` field is always-injected with default `"none"`, not conditional-key per Feature 104. F-A2 chooses conditional-key (Feature 104 precedent) deliberately because the absent-vs-empty semantic distinction is meaningful for attribution claims in a way it is not for pattern classification. Future schema evolutions will need to choose one convention per field based on the field's semantic profile; neither convention is universally correct.
- **Relationship enum divergence from ADR-027 `edge_type`**. F-A2 `relationship` uses `{primary, related, derived}`; ADR-027 `edge_type` uses `{primary, related, superseded}`. The shared `primary`/`related` values and the diverged third value (`derived` vs `superseded`) reflect that the two enums describe different semantic spaces (finding citation vs crosswalk-edge mapping). This is an intentional, documented divergence — downstream consumers MUST treat them as independent vocabularies.
- **Validator is optional at the CLI surface**. Decision 5 allows F-A3 to introduce a standalone `scripts/validate_source_attribution.py` CLI if development ergonomics warrant it. F-A2 ships without the CLI; this is not a commitment either way.
- **Schema 1.5 minor-bump precedent**. The Complex-Shape Addition Clarifier authorizes minor-bumps for list-of-RECORD additions meeting the three ADR-026 conditions. This is a bounded generalization, not a wholesale relaxation of the major-bump rule. Future additions of new required fields, removed fields, renamed fields, or re-typed fields remain major-bump changes.

---

## Related Decisions

- [ADR-020](ADR-020-maestro-layer-classification.md): MAESTRO layer classification — additive-optional-field precedent for the schema 1.1 → 1.2 bump adding `maestro_layer`. F-A2 inherits the *additive-optional* half of the precedent but NOT the *orchestrator-populated* half: `maestro_layer` is populated by orchestrator Phase 1 keyword classification; `source_attribution` is NOT populated in F-A2 (F-A3 is the populator feature). This divergence is deliberate and scope-disciplined — F-A2 is a contract feature.
- [ADR-021](ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md): SOURCE_DATE_EPOCH determinism. F-A2's validator preserves ADR-021 by construction: pure-function evaluation, per-invocation local-dict cache only, no HTTP/timestamps/env reads. The SC-2 byte-identity gate at `tests/scripts/test_backward_compatibility.py` is reused unmodified; no new determinism knobs introduced.
- [ADR-023](ADR-023-threat-agent-skill-references-pattern.md): 22-file zero-edit invariant on the 11 threat-detection agents plus their 11 companion skill-reference files. F-A2 preserves this invariant by construction — the feature is schema + parser + validator + ADR + tests, with no acceptance criterion requiring detection-agent edits. F-A3 is the feature that may reopen the 22-file scope.
- [ADR-026](ADR-026-pattern-classification-mechanism.md): minor-bump rule for NEW enum-typed field additions under three conditions (additive, has default, schema shape unchanged). This ADR's Decision 1 **extends** the ADR-026 rule to list-of-RECORD fields under the Complex-Shape Addition Clarifier. The rule is a durable precedent for future list-of-RECORD additions meeting the three conditions; other complex-shape additions (dict-of-record, list-of-list-of-scalar) require explicit future-ADR extension.
- [ADR-027](ADR-027-taxonomy-crosswalk-schema.md): F-A1 taxonomy schema — direct predecessor. F-A2's 5-value `taxonomy` enum is the external-framework subset of ADR-027 Decision 3's 7-value enum. F-A2's `source_attribution.id` resolves against the F-A1 catalog YAMLs (read-only; F-A2 does NOT modify any file under `schemas/taxonomy/`). This ADR's Decision 7 mirrors ADR-027 Decision 8's dual-commit governance protocol exactly. The two features together form the BLP-01 Foundation tier supply + demand sides; F-A1 ships the catalog vocabulary, F-A2 ships the finding-side bridge.

---

## References

- Spec: [`specs/189-source-attribution-schema-extension/spec.md`](../../../specs/189-source-attribution-schema-extension/spec.md) — FR-001 through FR-016, SC-001 through SC-007, US-1/US-2/US-3
- Plan: [`specs/189-source-attribution-schema-extension/plan.md`](../../../specs/189-source-attribution-schema-extension/plan.md) — C1..C6 components, Data Flow diagram, R1..R5 risks, Delivery Milestones
- Data model: [`specs/189-source-attribution-schema-extension/data-model.md`](../../../specs/189-source-attribution-schema-extension/data-model.md) — Finding (extended) + SourceAttributionRecord entities, V1..V6 validation rules, test-coverage traceability
- Research: [`specs/189-source-attribution-schema-extension/research.md`](../../../specs/189-source-attribution-schema-extension/research.md) — parser round-trip shape at `scripts/tachi_parsers.py:621`, F-A1 YAMLs verified, Feature 141 `has-attack-chains` precedent
- PRD: [`docs/product/02_PRD/189-source-attribution-schema-extension-2026-04-17.md`](../../product/02_PRD/189-source-attribution-schema-extension-2026-04-17.md)
- F-A1 PRD (direct predecessor): [`docs/product/02_PRD/180-taxonomy-crosswalk-collection-2026-04-17.md`](../../product/02_PRD/180-taxonomy-crosswalk-collection-2026-04-17.md)
- Schema head: [`schemas/finding.yaml`](../../../schemas/finding.yaml) — currently schema_version 1.4; F-A2 bumps to 1.5
- Parser target: [`scripts/tachi_parsers.py`](../../../scripts/tachi_parsers.py) — `parse_threats_findings` at line 621; `delta_status` conditional-key precedent at lines 672-676
- F-A1 catalog YAMLs: [`schemas/taxonomy/owasp.yaml`](../../../schemas/taxonomy/owasp.yaml), [`mitre-attack.yaml`](../../../schemas/taxonomy/mitre-attack.yaml), [`mitre-atlas.yaml`](../../../schemas/taxonomy/mitre-atlas.yaml), [`nist-ai-rmf.yaml`](../../../schemas/taxonomy/nist-ai-rmf.yaml), [`cwe.yaml`](../../../schemas/taxonomy/cwe.yaml) — 5 external-framework catalogs referenced by the F-A2 `taxonomy` enum; `tachi-control-category.yaml` and `tachi-stride-ai-category.yaml` are deliberately excluded per Decision 3
- Backward-compat harness: [`tests/scripts/test_backward_compatibility.py`](../../../tests/scripts/test_backward_compatibility.py) — SC-2 gate under `SOURCE_DATE_EPOCH=1700000000`
- Feature 141 precedent (conditional-section gating): [`docs/product/02_PRD/141-maestro-cross-layer-attack-chains-2026-04-12.md`](../../product/02_PRD/141-maestro-cross-layer-attack-chains-2026-04-12.md) — Section 6 `has-attack-chains` boolean is the direct architectural precedent for Decision 2's Section 9 `has-source-attribution` boolean
- Feature 104 precedent (conditional-key parser emission): [`scripts/tachi_parsers.py`](../../../scripts/tachi_parsers.py) lines 672-676 — `delta_status` is injected only when present in input, omitted otherwise; F-A2's `source_attribution` adopts the same shape

---

## Revision History

**2026-04-17 (Proposed — Feature 189, Day 1 Wave 1.1 schema-lock commit)**: Records the F-A2 Source Attribution Schema Extension decisions. Documents 7 numbered decisions covering the additive-optional-field minor-bump under the ADR-026 Complex-Shape Addition Clarifier extension for list-of-RECORD fields (Decision 1), the Q1-E conditional Section 9 serialization surface with Q1-B sidecar fallback (Decision 2), the 5-value `taxonomy` enum restricted to external frameworks (Decision 3), the 3-value `relationship` enum with default-to-`primary` (Decision 4), the Q2-B two-tier validation model with separate post-parse `validate_source_attribution` helper at orchestrator Phase 4 (Decision 5), the 22-file zero-edit invariant on the detection tier per ADR-023 lineage (Decision 6), and the Proposed → Accepted dual-commit governance protocol (Decision 7). Q1, Q2, and Q3 resolutions are all recorded at Proposed time; no Decision field is deferred to Accepted. Authored at end of Day 1 Wave 1.1 after Q1/Q2 architect memo; serves as the schema-lock signal that unblocks parallel authoring in Wave 2.1 onwards. Status transitions to Accepted at Day 3 Wave 6.1 (T031) per Decision 7; `<pending-post-merge-fill>` placeholder on the `Accepted-commit-SHA` field replaced at post-merge T036 with the squash-merge commit SHA.

**2026-04-17 (Accepted — Feature 189, Wave 6.1 pre-merge transition T031)**: Transitioned ADR-028 from `Status: Proposed` to `Status: Accepted`. All 7 numbered decisions land as specified at Proposed time; no decision text is amended at Accepted. Implementation waves 1-5 verified green: schema 1.4 → 1.5 bump landed in `schemas/finding.yaml`, parser round-trip + two-tier validation landed in `scripts/tachi_parsers.py` (lines 621-977), 7 fixtures + 9 tests under `tests/scripts/` pass, SC-2 byte-identity harness 6/6 baselines byte-identical under `SOURCE_DATE_EPOCH=1700000000`, and 22-file zero-edit invariant preserved (ADR-023 sibling governance). Checkpoint 5.5 interim pytest gate (team-lead concern #4) green: full `pytest tests/scripts/ -v` reports 279 passed / 1 skipped (pre-existing SC-003 narrowing). Accepted-date is provisional pending PR merge; `<pending-post-merge-fill>` placeholder on `Accepted-commit-SHA` will be replaced by the squash-merge commit SHA at post-merge task T036 per Decision 7.
