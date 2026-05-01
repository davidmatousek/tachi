# ADR-037: Web/API Coverage Attestation + Populator Wiring — F-8 Tier 3 Closure + F-A3 Heuristic A Closure across 11 Host Agents

**Status**: Proposed
**Date**: Proposed: 2026-05-01 (Wave 1.1 T004 plan-day stub commit pending; Accepted: post Wave 6.1 T064 dual-commit per Decision 10 lineage)
**Deciders**: Architect (tachi project)
**Feature**: [241-web-api-coverage-attestation](../../../specs/241-web-api-coverage-attestation/spec.md)
**Supersedes**: None
**Superseded by**: None
**Related ADRs**: [ADR-021](ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md) (SOURCE_DATE_EPOCH determinism — F-241 preserves byte-identity on 6 pre-existing baselines under SOURCE_DATE_EPOCH=1700000000), [ADR-023](ADR-023-threat-agent-skill-references-pattern.md) (lean-agent + additive-only shared-reference Decision 3 — F-241 follows additive-only edit discipline across 11 host agents and 4 companion catalogs), [ADR-027](ADR-027-taxonomy-crosswalk-schema.md) (F-A1 taxonomy crosswalk — F-241 D-7 extends owasp.yaml + mitre-atlas.yaml + mitre-attack.yaml record-shape with `out_of_scope` + `out_of_scope_rationale` fields; ADR-027 receives forward-pointer addendum cross-linking D-7 per M-1 carry-forward), [ADR-028](ADR-028-source-attribution-schema-extension.md) (F-A2 source_attribution schema — F-241 D-2/D-3 closes the F-A3 deferral debt across 11 host agents), [ADR-030](ADR-030-output-integrity-agent.md) (F-1 — net-new agent populator template referenced in D-3), [ADR-031](ADR-031-misinformation-agent.md) (F-2 — net-new agent populator template referenced in D-3), [ADR-032](ADR-032-asi07-tool-abuse-enrichment.md) (F-3 — F-A3 deferral predicate; closes via D-10), [ADR-033](ADR-033-human-trust-exploitation-agent.md) (F-4 — net-new agent populator template referenced in D-3), [ADR-034](ADR-034-llm10-unbounded-consumption-audit.md) (F-5 — F-A3 deferral predicate; closes via D-10), [ADR-035](ADR-035-ml-top-10-coverage-bundle.md) (F-6 — F-A3 deferral predicate; closes via D-10), [ADR-036](ADR-036-mobile-top-10-coverage-bundle.md) (F-7 — F-A3 deferral predicate; closes via D-10)

---

## Context

> **STATUS: Proposed stub — full Context narrative to be authored at Wave 5.3 T059 per the agent-assignments timeline (Day 26 Fri 6/5). The 10 D-numbered decisions below are skeleton placeholders with one-line decision summaries. T059 expands each D-N into a full Decision/Context/Consequence narrative; T064 promotes status to Accepted via dual-commit governance pattern per ADR-035 D-10 / ADR-036 D-10 precedent.**

F-241 is BLP-01 Tier 3 — the eleventh and final feature in the BLP-01 11-feature initiative. It closes three structural debts that have accumulated across the BLP-01 lineage:

1. **F-8 Web/API Coverage Attestation** — replaces the manually-curated `_internal/strategy/BLP-01-threat-coverage.md` §6 Coverage Matrix with pipeline-generated, per-baseline Coverage Attestation pages emitted into `security-report.pdf` from real-time `findings.yaml` source_attribution data. Source-of-truth shifts from human-maintained matrix to executable pipeline.

2. **F-A3 Populator Wiring** — wires `source_attribution` populators across **11 host agents** (5 STRIDE-heavy: `spoofing`, `tampering`, `info-disclosure`, `privilege-escalation`, `repudiation`; 2 STRIDE-extended: `denial-of-service`, `tool-abuse`; 2 ML-tier: `data-poisoning`, `model-theft`; 2 LLM-tier: `prompt-injection`, `agent-autonomy`). Combined with the 3 pre-existing F-1/F-2/F-4 net-new agents, this brings detection-tier coverage to **14/14** files.

3. **Coverage Attestation extensions** — Stream 2 closes 6 Partial items (A05/A06/API6/API8/API9/API10), Stream 3 expands ATLAS 12→30 + ATT&CK 38→600 records with tactical-grouping Out-of-Scope strategy, Stream 4 implements Out-of-Scope-aware denominator filter in the aggregator.

### Constraints

- **finding.yaml v1.8 unchanged** — F-241 reuses 5+3 enum (no schema bump). Asymmetry to F-1/F-2/F-4 minor bumps; symmetry with F-3/F-5/F-6/F-7 zero-bump enrichment branch.
- **F-7 28-file detection-tier zero-edit invariant** — only 11 F-A3 host agents + 4 Stream 2 companion catalogs modified per FR-021.
- **Zero new runtime dependencies** — empty diffs on `pyproject.toml`, `requirements*.txt`, `package.json`.
- **Stdlib-only module-load invariant preserved** — `import yaml` remains inside function bodies in `scripts/extract-report-data.py` per Architect MEDIUM-B; verified by AST walk in `tests/scripts/test_pyyaml_deferred_import.py`.
- **Byte-identity backward compatibility (ADR-021 lineage)** — 6 pre-existing baselines regenerate byte-identically on non-CA pages under `SOURCE_DATE_EPOCH=1700000000`; intentional updates limited to Coverage Attestation pages only.
- **F-A2 referential-integrity contract preserved (ADR-028 D5)** — every emitted F-241 finding's `references` array cites catalog-resolvable taxonomy primaries.
- **Two new mutation-target baselines** at canonical paths: `examples/predictive-ml-app/sample-report/security-report.pdf.baseline` + `examples/mobile-banking-app/sample-report/security-report.pdf.baseline` per Architect L-1 carry-forward (NOT `examples/{arch}/security-report.pdf.baseline`).

### Single Combined ADR (Q-PM-1 RESOLVED)

Per plan-day Q-PM-1 RESOLVED (PM + Architect joint sign-off), F-241 ships a **single combined ADR-037** rather than splitting into separate ADRs for F-8 attestation and F-A3 wiring. Rationale: the four work streams interlock (Stream 1 produces `source_attribution`, Stream 3 produces denominator inventory, Stream 4 reads both), and a split would fragment the F-A3 closure narrative across two artifacts and complicate the cumulative ADR-032/034/035/036 deferral lineage citation. The taxonomy YAML record-shape extension (Architect MEDIUM-A) is acknowledged in dedicated D-7 narrative within ADR-037 rather than a separate ADR.

---

## Decisions

> **STATUS: Skeleton placeholders — full narratives authored at Wave 5.3 T059.**

### D-1: Combined-vs-Split ADR Scope (RESOLVED single combined per Q-PM-1)

**Decision**: Single combined ADR-037 documenting all four work streams (F-8 attestation + F-A3 wiring + record-shape extension + aggregator filter).

**Stream**: Cross-cutting

*Full narrative authored at Wave 5.3 T059.*

### D-2: F-A3 11-Host Expansion (Architect HIGH-A — includes `prompt-injection` + `agent-autonomy`)

**Decision**: Wire `source_attribution` populators across all 11 candidate host agents — including `prompt-injection` and `agent-autonomy` per Architect HIGH-A — because the aggregator reads only `source_attribution[].id` directly without distinguishing agent provenance.

**Stream**: Stream 1

*Full narrative authored at Wave 5.3 T059.*

### D-3: F-A3 Wiring Template (one `primary` + ≥1 `related` CWE per pattern category)

**Decision**: Adopt the F-1/F-2/F-4 net-new agent populator template — each finding has exactly one `relationship: primary` taxonomy entry plus ≥1 `relationship: related` CWE entry, mirroring `output-integrity.md`, `misinformation.md`, and `human-trust-exploitation.md` precedent.

**Stream**: Stream 1

*Full narrative authored at Wave 5.3 T059.*

### D-4: Six Partial Item Closure Mapping (4 closeable + 2 new-Indicator)

**Decision**: Close A05 + A06 on existing companions (Primary Source extension), close API6 + API9 with new Indicator categories per Q-Plan-1 (API6 → `tachi-tool-abuse`) and Q-Plan-2 (API9 → `tachi-info-disclosure`), close API8 with API-specific Indicator extension on `tachi-privilege-escalation`, close API10 with Primary Source on `tachi-tampering` Cat 9 + cross-ref to `tachi-info-disclosure` Cat 7.

**Stream**: Stream 2

*Full narrative authored at Wave 5.3 T059.*

### D-5: Tactical-Grouping Out-of-Scope Strategy on ATT&CK Enterprise (TA0005/7/8/9/10/11/40)

**Decision**: Apply tactical-grouping `out_of_scope: true` rationale to 7 ATT&CK Enterprise tactics that are runtime/IR-only (not design-time-relevant): TA0005 Defense Evasion, TA0007 Discovery, TA0008 Lateral Movement, TA0009 Collection, TA0010 Exfiltration, TA0011 Command and Control, TA0040 Impact. In-scope tactics (TA0001 Initial Access, TA0002 Execution, TA0003 Persistence, TA0004 Privilege Escalation, TA0006 Credential Access, TA0042 Resource Development) receive per-item `out_of_scope` rationale on individual runtime-only sub-techniques.

**Stream**: Stream 3

*Full narrative authored at Wave 5.3 T059.*

### D-6: ATLAS + OWASP Audit-Only Scope

**Decision**: Expand ATLAS 12 → ~30 records with per-item Out-of-Scope on runtime/IR-only techniques. OWASP audit only (60 records) — no new rows added; verify citation completeness (≥1 agent + ≥1 pattern category per Covered citation per BLP-01 §8).

**Stream**: Stream 3

*Full narrative authored at Wave 5.3 T059.*

### D-7: Taxonomy YAML Record-Shape +2 Field Extension (Architect MEDIUM-A acknowledged)

**Decision**: Extend `schemas/taxonomy/{owasp,mitre-atlas,mitre-attack}.yaml` record shape with two new optional fields: `out_of_scope: <bool, default false>` and `out_of_scope_rationale: <string, default "">`. Backward compatibility preserved via YAML defaults — pre-F-241 records render identically when the new fields are absent. ADR-027 receives forward-pointer addendum cross-linking D-7 per M-1 carry-forward.

**Stream**: Stream 3 / cross-cutting

*Full narrative authored at Wave 5.3 T059.*

### D-8: Aggregator Out-of-Scope-Aware Denominator Filter

**Decision**: Apply Out-of-Scope-aware filter at `_load_framework_yaml_records()` (line 1073) OR `load_framework_yaml_record_counts()` (line 1101) in `scripts/extract-report-data.py` — NOT at `_build_per_framework_aggregate()` (line 1144) where the count is already pre-computed per Architect M-2 carry-forward. Coverage percentage formula: `(covered_count / in_scope_record_count) * 100` with `N/A` on zero denominator. Stdlib-only module-load invariant preserved (`import yaml` inside function bodies, asserted by AST walk).

**Stream**: Stream 4

*Full narrative authored at Wave 5.3 T059.*

### D-9: Eight-Baseline Scope Expansion

**Decision**: Regenerate Coverage Attestation pages on all 8 baselines: 6 pre-existing (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`) + 2 net-new (`predictive-ml-app`, `mobile-banking-app`) at canonical paths per Architect L-1 carry-forward (`examples/{arch}/sample-report/security-report.pdf.baseline`). Intentional updates limited to CA pages only; non-CA pages remain byte-identical under `SOURCE_DATE_EPOCH=1700000000`.

**Stream**: Stream 4

*Full narrative authored at Wave 5.3 T059.*

### D-10: F-A3 Deferral Lineage Closure + §6 Coverage Matrix Demotion

**Decision**: F-241 closes the F-A3 deferral lineage opened at ADR-032 (F-3) and re-deferred at ADR-034 D-8 (F-5) / ADR-035 D-10 (F-6) / ADR-036 D-10 (F-7). Post-F-241, no further F-A3 deferrals are open — populator wiring is complete across all 14 detection-tier agents (3 net-new + 11 enriched). The historical `_internal/strategy/BLP-01-threat-coverage.md` §6 Coverage Matrix is demoted with annotation: "historical — superseded by pipeline-generated attestation" + pointer to F-B section. BLP-01 11-feature initiative closes at F-241 squash-merge.

**Stream**: Cross-cutting

*Full narrative authored at Wave 5.3 T059.*

---

## Consequences

> **STATUS: Skeleton placeholder — full Consequences narrative authored at Wave 5.3 T059.**

### Positive

- Source-of-truth for OWASP/ATT&CK/ATLAS coverage shifts from human-maintained markdown to pipeline-generated PDF Coverage Attestation pages.
- F-A3 deferral debt fully cleared (ADR-032/034/035/036 → ADR-037 D-10 closure).
- 14/14 detection-tier agents emit `source_attribution` (verifiable by `grep -l "source_attribution" .claude/agents/tachi/*.md | wc -l`).
- Backward compatibility preserved (finding.yaml v1.8 unchanged; non-CA pages byte-identical).
- BLP-01 11-feature initiative closes.

### Negative / Trade-offs

*Full Consequences narrative authored at Wave 5.3 T059.*

### Neutral

*Full Consequences narrative authored at Wave 5.3 T059.*

---

## Implementation Notes

> **STATUS: Skeleton placeholder — full Implementation Notes authored at Wave 5.3 T059.**

- 84 tasks across 29 working days; Wave 1.1 → 6.3 timeline.
- 4 work streams: Stream 1 (F-A3 wiring) ‖ Stream 2 (Partial closures) ‖ Stream 3 (taxonomy expansion) ‖ Stream 4 (aggregator + baseline regen).
- ADR-037 dual-commit lifecycle: Proposed at Wave 5.3 T059 (Day 26) → Accepted at Wave 6.1 T064 (Day 27) with post-merge SHA fill-in at Wave 6.3 T068 (Day 29).

---

**End of ADR-037 stub** — full narrative pending Wave 5.3 T059 authoring per agent-assignments.md timeline.
