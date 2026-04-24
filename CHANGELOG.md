# Changelog

All notable changes to tachi will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [4.21.0](https://github.com/davidmatousek/tachi/compare/v4.20.0...v4.21.0) (2026-04-24)


### Features

* **206:** misinformation threat agent (OWASP LLM09:2025) ([#207](https://github.com/davidmatousek/tachi/issues/207)) ([b703e52](https://github.com/davidmatousek/tachi/commit/b703e52be2fac041dd9b5ffc23b1f5b610e8a262))

## [4.20.0](https://github.com/davidmatousek/tachi/compare/v4.19.0...v4.20.0) (2026-04-20)


### Features

* update template from AOD-kit (first F129 run) ([a36a73f](https://github.com/davidmatousek/tachi/commit/a36a73fc28a367047c1eabb2860ba83c60a83e5d))

## [4.19.0](https://github.com/davidmatousek/tachi/compare/v4.18.1...v4.19.0) (2026-04-19)


### Features

* **201:** output-integrity threat agent (OWASP LLM05:2025) ([#202](https://github.com/davidmatousek/tachi/issues/202)) ([558e75e](https://github.com/davidmatousek/tachi/commit/558e75eb333ad7787167833c97b645bc251492e1))

## [4.18.1](https://github.com/davidmatousek/tachi/compare/v4.18.0...v4.18.1) (2026-04-18)


### Bug Fixes

* **198:** merge source_attribution onto Tier 1/2 findings ([#199](https://github.com/davidmatousek/tachi/issues/199)) ([e637d31](https://github.com/davidmatousek/tachi/commit/e637d31927c1e2c66f4f0afe5b2ab2b9ea8abcd1))

## [4.18.0](https://github.com/davidmatousek/tachi/compare/v4.17.0...v4.18.0) (2026-04-18)


### Features

* **194:** Coverage Attestation Report Section (F-B / BLP-01) ([#195](https://github.com/davidmatousek/tachi/issues/195)) ([c4b8dc6](https://github.com/davidmatousek/tachi/commit/c4b8dc68f36b59ee7ab49cc587661526ffd1a818))

## [4.17.0](https://github.com/davidmatousek/tachi/compare/v4.16.0...v4.17.0) (2026-04-18)


### Features

* **189:** F-A2 source attribution schema extension ([#189](https://github.com/davidmatousek/tachi/issues/189)) ([#190](https://github.com/davidmatousek/tachi/issues/190)) ([6d5d890](https://github.com/davidmatousek/tachi/commit/6d5d890c388af5f546246f4e39f8a4d61fe840b1))

## [4.16.0](https://github.com/davidmatousek/tachi/compare/v4.15.0...v4.16.0) (2026-04-17)


### Features

* **180:** F-A1 Taxonomy Crosswalk Collection ([#181](https://github.com/davidmatousek/tachi/issues/181)) ([8b7c7bf](https://github.com/davidmatousek/tachi/commit/8b7c7bf59a6de93a0d3f5016a4395755de19c79e))

## [4.15.0](https://github.com/davidmatousek/tachi/compare/v4.14.1...v4.15.0) (2026-04-16)


### Features

* **142:** MAESTRO Phase 3 — Agentic Threat Pattern Expansion ([#172](https://github.com/davidmatousek/tachi/issues/172)) ([c0b7378](https://github.com/davidmatousek/tachi/commit/c0b73780c83aa3df16ac7965738bc76034e88454))

## [4.14.1](https://github.com/davidmatousek/tachi/compare/v4.14.0...v4.14.1) (2026-04-14)


### Bug Fixes

* fall back to architecture.md H1 when threats.md lacks project name ([#165](https://github.com/davidmatousek/tachi/issues/165)) ([b746cb7](https://github.com/davidmatousek/tachi/commit/b746cb74595f9a15041c50bcdef69e5e0ed21709))

## [4.14.0](https://github.com/davidmatousek/tachi/compare/v4.13.0...v4.14.0) (2026-04-14)


### Features

* **129:** attack tree delta sub-agent — extract Section 5 generation ([#162](https://github.com/davidmatousek/tachi/issues/162)) ([0729490](https://github.com/davidmatousek/tachi/commit/072949017f633d029ac4af22032da21efcb67b17))


### Bug Fixes

* auto-detect newest docs/security run directory in tachi commands ([#164](https://github.com/davidmatousek/tachi/issues/164)) ([39c962c](https://github.com/davidmatousek/tachi/commit/39c962c4eaed2e4cec899f5036169ba005b6d163))

## [4.13.0](https://github.com/davidmatousek/tachi/compare/v4.12.0...v4.13.0) (2026-04-12)


### Features

* **141:** MAESTRO Phase 2 — Cross-Layer Attack Chain Analysis ([#159](https://github.com/davidmatousek/tachi/issues/159)) ([5a108e9](https://github.com/davidmatousek/tachi/commit/5a108e984aa8623df3a856007c876006cdff6eb3))


### Bug Fixes

* **141:** constrain attack chain diagram height to fit one page ([2310af3](https://github.com/davidmatousek/tachi/commit/2310af313128aaec1cd147a3f028aba41a2f2150))

## [4.12.0](https://github.com/davidmatousek/tachi/compare/v4.11.1...v4.12.0) (2026-04-12)


### Features

* **154:** deterministic Gemini prompt scaffold for infographic quality stability ([f2ad9be](https://github.com/davidmatousek/tachi/commit/f2ad9be2f24d8d94168dc82cd49048623164f4de))


### Bug Fixes

* **154:** add .claude/skills/tachi-*/ to INSTALL_MANIFEST ([6547360](https://github.com/davidmatousek/tachi/commit/6547360d39c44301adb51c8b8ec23cc722a13e8a))
* **154:** infographic quality — extract risk metrics, update Gemini model config ([3cd5d27](https://github.com/davidmatousek/tachi/commit/3cd5d27edde4310dc0ad650ef7265bcc49f098d6))
* **154:** MAESTRO layer detection in /tachi.infographic checks wrong file and pattern ([30f9ad9](https://github.com/davidmatousek/tachi/commit/30f9ad96b49178b447c79a3d6e49b97977b6ab0d))

## [4.11.1](https://github.com/davidmatousek/tachi/compare/v4.11.0...v4.11.1) (2026-04-12)


### Bug Fixes

* **154:** PDF report — attack trees, MAESTRO headings, landscape whitespace ([#155](https://github.com/davidmatousek/tachi/issues/155)) ([7f047b7](https://github.com/davidmatousek/tachi/commit/7f047b7fe42736bd51e60d8dfca18af33cb86d98)), closes [#154](https://github.com/davidmatousek/tachi/issues/154)

## [4.11.0](https://github.com/davidmatousek/tachi/compare/v4.10.1...v4.11.0) (2026-04-12)


### Features

* **082:** threat agent skill references — detection tier lean refactor ([#151](https://github.com/davidmatousek/tachi/issues/151)) ([6f9a40d](https://github.com/davidmatousek/tachi/commit/6f9a40dbe17b14a04f10b56357f1a81bb025e24d))

## [4.10.1](https://github.com/davidmatousek/tachi/compare/v4.10.0...v4.10.1) (2026-04-11)


### Bug Fixes

* **130:** enforce mmdc as hard prerequisite with loud preflight/mid-render aborts ([#148](https://github.com/davidmatousek/tachi/issues/148)) ([d35a667](https://github.com/davidmatousek/tachi/commit/d35a6676dd8e409d32b06eb5e03760a0aab3f560))

## [4.10.0](https://github.com/davidmatousek/tachi/compare/v4.9.2...v4.10.0) (2026-04-10)


### Features

* **136:** align MAESTRO layer names with canonical CSA taxonomy ([#146](https://github.com/davidmatousek/tachi/issues/146)) ([31356fb](https://github.com/davidmatousek/tachi/commit/31356fb5bb48ac02b62ce8ead35f19d91db36c13))

## [Unreleased]

### Added — Agentic Pattern Schema Extension (#142, Feature 142)

**Schema Version Bump (`schemas/finding.yaml` 1.3 → 1.4)**: Schema version bumped from `1.3` to `1.4` to accommodate the new `agentic_pattern` enum field introduced by MAESTRO Phase 3 (Feature 142 — Agentic Threat Pattern Expansion). Per [ADR-026](docs/architecture/02_ADRs/ADR-026-pattern-classification-mechanism.md), this is a **minor bump** because the change is additive: a new enum-typed field with a default value (`none`) is introduced, the schema shape is unchanged, and no existing required fields are removed or renamed. The bump extends the Feature 136 enum-VALUE-rename minor-bump rule (ADR-020 Revision History) to cover NEW enum-typed field additions under the same three additive-compatibility conditions.

**threats.md Output Schema Bump (1.3 → 1.4)**: The `templates/tachi/output-schemas/threats.md` frontmatter `schema_version` is bumped from `1.3` to `1.4` alongside `finding.yaml` to reflect the additive structural changes to the output: (a) new Pattern column in Section 7 between Category and Component, and (b) new conditional Section 4b "Findings by Agentic Pattern" gated by `has-agentic-patterns: true`. Per the Feature 104 precedent (threat-report.md 1.0 → 1.1 for baseline delta propagation), additive structural changes to an output schema warrant a minor bump on that schema. The change is purely additive and backward-compatible: pre-Feature-142 parsers reading the new output see `schema_version: "1.4"` but the Pattern column renders `—` on legacy-style data (pattern=`none`) and Section 4b is suppressed entirely. The `.claude/skills/tachi-orchestration/references/output-schemas.md` frontmatter example and descriptive table are updated to match.

#### New `agentic_pattern` Enum Field

The finding IR gains a required `agentic_pattern` field with eight permitted values surfacing the six canonical CSA MAESTRO agentic threat patterns plus two sentinel values:

| Value | Meaning |
|-------|---------|
| `agent_collusion` | Multiple compromised agents coordinating to achieve malicious objectives |
| `emergent_behavior` | Exploiting unpredictable behaviors arising from agent interactions |
| `temporal_attack` | Sleeper agents, gradual corruption, seasonal exploitation, time-delayed activation |
| `trust_exploitation` | Identity spoofing between agents, reputation manipulation, trust chain attacks |
| `communication_vulnerability` | Inter-agent message interception, protocol manipulation, routing attacks |
| `resource_competition` | Resource monopolization, priority manipulation, coordination disruption between agents |
| `none` | Finding does not map to any canonical pattern (sentinel; default) |
| `multiple` | Finding exemplifies two or more patterns equally (rare; prefer the dominant pattern when one exists) |

The default value is `none`. The field is populated during orchestrator Phase 3.6 (Pattern Synthesis Engine) using a deterministic rule-based classification engine. The multi-agent gate predicate (FR-006) ensures that single-agent architectures receive `none` for every finding, preserving backward compatibility on the 5 baseline architectures (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`).

#### `id.pattern` Regex Extension — `AGP-` Prefix

The `finding.id.pattern` regex has been extended from `^(S|T|R|I|D|E|AG|LLM)-\d+$` to `^(S|T|R|I|D|E|AG|LLM|AGP)-\d+$` to accept the new `AGP-` prefix reserved for **net-new findings** generated by Phase 3.6 for previously-uncovered patterns (Agent Collusion, Emergent Behavior, Temporal Attack). `AGP-NN` findings map to `category: agentic` and are appended to the deduplicated finding IR only when the architecture satisfies the multi-agent gate predicate AND no existing detection-tier finding already carries the pattern label. See [data-model.md Entity 5](specs/142-maestro-agentic-pattern-expansion/data-model.md) for the full net-new finding generation contract.

#### Backward Compatibility

The addition is **backward-compatible** per FR-017. Pre-Feature-142 baseline findings (which lack the `agentic_pattern` field) parse correctly with default `agentic_pattern: none` when consumed by Feature 142 parsers. The 5 non-multi-agent baseline PDFs remain byte-identical under `SOURCE_DATE_EPOCH=1700000000` per [ADR-021](docs/architecture/02_ADRs/ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md) because the multi-agent gate predicate evaluates `false` on those architectures, causing every finding to receive `agentic_pattern: none` and the Pattern column to render as `—` for all rows (with Section 4b "Findings by Agentic Pattern" suppressed entirely).

#### References

- ADR-026: [docs/architecture/02_ADRs/ADR-026-pattern-classification-mechanism.md](docs/architecture/02_ADRs/ADR-026-pattern-classification-mechanism.md)
- Spec: [specs/142-maestro-agentic-pattern-expansion/spec.md](specs/142-maestro-agentic-pattern-expansion/spec.md)
- Plan: [specs/142-maestro-agentic-pattern-expansion/plan.md](specs/142-maestro-agentic-pattern-expansion/plan.md)
- Data model: [specs/142-maestro-agentic-pattern-expansion/data-model.md](specs/142-maestro-agentic-pattern-expansion/data-model.md)
- GitHub Issue: [#142](https://github.com/davidmatousek/tachi/issues/142)

---

### Changed — Detection Quality and Lean Agent Architecture Complete (#151, Feature 082)

**All 17 Tachi Agents Now Use Lean-Agent Architecture**: The 11 remaining threat detection agents (6 STRIDE + 5 AI-specific) have been migrated from self-contained inline shape to the lean-agent + skill references pattern, completing the lean-agent architecture for the entire tachi agent fleet. Pre-refactor, STRIDE agents were 113-141 lines and AI agents were 167-201 lines (3 AI agents were over the 180-line hard cap); post-refactor, STRIDE agents are 50-54 lines and AI agents are 78-114 lines — every agent within FR-10 tier caps (STRIDE ≤120, AI ≤150, hard cap ≤180). Detection quality has been enriched with +30 new pattern categories across the 11 agents, covering OWASP LLM Top 10 2025, MITRE ATLAS v5.1+ (including the October 2025 agent techniques AML.T0058-T0062), OWASP AI Exchange, CWE Top 25 2024, and NIST AI 600-1. Users running `/tachi.threat-model` on an agentic AI application will see additional findings surfaced that the pre-refactor inline patterns could not reach.

#### Detection Variant of Lean-Agent Pattern

Feature 082 introduces a second documented shape of the lean-agent pattern, sibling to the methodology variant already used by `control-analyzer`. The detection variant loads its companion reference at invocation start via a single `**MANDATORY**: Read` directive rather than phase-gated loads. All 11 threat agents now host their detection patterns at `.claude/skills/tachi-<name>/references/detection-patterns.md` (byte-preserved from the pre-refactor agent content plus enriched categories).

| Pattern Variant | Used By | Load Style |
|-----------------|---------|------------|
| Methodology variant | control-analyzer | Phase-gated loads per workflow step |
| **Detection variant** (new) | 11 threat agents | Single-point load at detection start |

See [ADR-023](docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md) for the full pattern definition, the MAESTRO ownership rule, and the additive-only shared reference invariant.

#### New Enrichment Categories (+30 / ≥22 Floor)

All 11 threat agents gained new detection pattern categories sourced from authoritative primaries:

| Source | Coverage Added |
|--------|---------------|
| OWASP LLM Top 10 2025 | Prompt injection variants, data poisoning vectors, model theft techniques, excessive agency patterns |
| MITRE ATLAS v5.1+ | AML.T0058 context poisoning, AML.T0059 memory corruption, AML.T0060 agent-in-the-middle, AML.T0061 excessive agency runtime, AML.T0062 cascading agent failures |
| OWASP AI Exchange | Cross-cutting AI supply chain, model lifecycle, and training data governance patterns |
| MITRE ATT&CK v15+ | STRIDE-side technique mappings (especially T1078 valid accounts, T1550 alt auth, T1562 impair defenses) |
| CWE Top 25 2024 | Modernized weakness enumeration with 2024 updates |
| NIST AI 600-1 | Generative AI risk management profile controls |

T048 security review (Wave 13) flagged 5 first-draft categories for primary-source realignment; T048a (Wave 13.5) rebuilt all 5 byte-verbatim preserving substance. The final aggregate was **30 new categories** against a **≥22 floor** (SC-006 / FR-7) — **+8 margin**. See [KB-030 in INSTITUTIONAL_KNOWLEDGE.md](docs/INSTITUTIONAL_KNOWLEDGE.md) for the "cite primary sources in first draft" lesson that emerged from the T048 rebuild cycle.

#### Additive-Only Shared Reference Consolidation

`finding-format-shared.md` gains a new "For Threat Agents" producer section describing the finding construction responsibility for detection-tier agents. The existing "For Risk Scorer / Control Analyzer / Threat Report" consumer sections remain byte-identical — the edit is **additive-only** (T046 invariant), preventing regressions in the 6 infrastructure agents that were already in production. All 11 threat agents' Skill References tables register the shared reference for load at detection start. The OWASP 3×3 risk matrix now lives in exactly one canonical file (`severity-bands-shared.md:72`), normalized to Unicode `×` to match the SC-004 canonical-form audit. Wave 16 remediation removed 22 inline "OWASP 3×3" brand-name mentions from agent prose.

#### Backward Compatibility

Feature 082 is **purely agent-behavior-facing**. The PDF pipeline reads committed `threats.md`, `risk-scores.md`, `compensating-controls.md`, and `attack-trees/` files — none of which are modified by this feature. Typst templates, `extract-report-data.py`, and `extract-infographic-data.py` are untouched. The 5 byte-deterministic example PDFs (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) remain **byte-identical** under `SOURCE_DATE_EPOCH=1700000000` per [ADR-021](docs/architecture/02_ADRs/ADR-021-deterministic-pdf-comparison.md). The 6th example (`agentic-app`) was regenerated as the T057 US2 AC-3 independent test, surfacing **+8 new AI findings** (22 baseline → 30) — consistent with the Option B+ gate prediction. Zero new runtime dependencies (SC-014 — empty diff on `pyproject.toml`, `requirements*.txt`, `package.json`).

#### Option B+ Gate Methodology

Phase 1a / 1b (2-agent prototype) and Phase 3 (11-agent scale) regression gates used **content-equivalence + DFD-vs-pattern matching** rather than live orchestrator invocation. The method was ratified by the T021 joint architect + team-lead gate approval under the "±2 tolerance interpretation (b)" ruling: pre-existing pattern categories must delta=0, new categories can have any non-negative delta from enrichment. T050 full regression gate (Wave 15) used Option B+ to prove SC-005 for all 11 agents × 6 examples; T057 live regeneration on `agentic-app` (Wave 17) then confirmed the prediction was exact.

#### References

- PRD: [docs/product/02_PRD/082-threat-agent-skill-references-2026-04-11.md](docs/product/02_PRD/082-threat-agent-skill-references-2026-04-11.md)
- Spec: [specs/082-threat-agent-skill/spec.md](specs/082-threat-agent-skill/spec.md)
- Plan: [specs/082-threat-agent-skill/plan.md](specs/082-threat-agent-skill/plan.md)
- Delivery retrospective: [specs/082-threat-agent-skill/delivery.md](specs/082-threat-agent-skill/delivery.md)
- ADR-023: [docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md](docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md)
- PR: [#151](https://github.com/davidmatousek/tachi/pull/151)
- GitHub Issue: [#82](https://github.com/davidmatousek/tachi/issues/82)

---

### Breaking Changes — Correctness Fix (#148, Feature 130)

**mmdc Is Now a Hard Prerequisite**: When `/tachi.security-report` is run against a project containing Critical/High attack trees, `@mermaid-js/mermaid-cli` (`mmdc`) must be installed on `PATH`. Previously, a missing `mmdc` triggered a silent text fallback that shipped 40+ lines of raw `flowchart TD` source per attack-path page inside the PDF; the pipeline reported exit 0 and the broken output was only discoverable by paging through the PDF manually. The text-fallback Typst branch has been deleted outright, and two defense-in-depth preflight gates now raise a loud error with the canonical install command.

#### Install

```sh
npm install -g @mermaid-js/mermaid-cli
```

The check is gated on input detection — projects without `attack-trees/` content continue to work unchanged without `mmdc`. See [ADR-022](docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md) for the full governance rationale, rejected alternatives (pymmdc, Kroki, auto-install), and the Future Work clause.

#### Error Output on Missing Prerequisite

```
Attack path rendering requires @mermaid-js/mermaid-cli (mmdc).
Install with: npm install -g @mermaid-js/mermaid-cli
Then re-run /tachi.security-report.
```

The same canonical message fires from both enforcement points: a shell-level `command -v mmdc` check in `.claude/commands/tachi.security-report.md` Step 1 (mirrors the existing Typst check) and a Python-level `shutil.which("mmdc") → raise RuntimeError(...)` inside `scripts/extract-report-data.py::render_mermaid_to_png()`.

#### Mid-Render Failures Now Abort With Per-Finding Detail

When `mmdc` is present but a specific attack tree fails to render (invalid Mermaid syntax, subprocess crash, timeout), the pipeline now aggregates per-finding errors and raises `RuntimeError("Attack path rendering failed for N findings: ...")` with each failing finding's ID, source path, failure class (`exit:<code>`, `timeout`, or `signal`), and a 200-byte stderr excerpt. Previously, each failing entry was silently marked `has_image=False` and the text fallback kicked in. No PDF is emitted when mid-render failures occur.

#### Backward Compatibility

The happy path (mmdc present, all trees render) is byte-identical to the pre-Feature 130 output under `SOURCE_DATE_EPOCH=1700000000`. The 5 byte-deterministic baselines (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) remain unchanged. Projects without `attack-trees/` content are completely unaffected.

#### Documentation

- **README.md** gains a new `## Prerequisites` section naming `typst` and `@mermaid-js/mermaid-cli` with per-OS install commands (macOS/Linux/WSL).
- **scripts/install.sh** gains a courtesy `command -v mmdc` warning at setup time.
- **docs/architecture/00_Tech_Stack/README.md** mmdc section rewritten as a hard prerequisite with ADR-022 cross-reference.
- **specs/112-attack-path-pages/spec.md** SC-004 inverted (text fallback is no longer a supported shipping mode) with audit-trail comment.
- **specs/112-attack-path-pages/research.md** pymmdc description corrected (GPL-3.0 Node.js wrapper, not a pure-Python renderer) with a Durable Decision Rationale block.
- **New CI workflow** `.github/workflows/tachi-mmdc-preflight.yml` asserts the loud-failure path fires on `ubuntu-latest` (no mmdc preinstalled) and fails the job if `mmdc` is unexpectedly present on `PATH`.

---

### Breaking Changes — Correctness Fix (#136)

**MAESTRO Canonical Layer Alignment**: tachi's MAESTRO seven-layer taxonomy has been aligned with the canonical CSA Ken Huang reference. Three L5/L6/L7 layer names, the acronym expansion, and a third-divergent name ("Integration Services") in the Typst PDF template have been corrected. This is a **correctness fix**, not a feature addition.

#### Enum Value Migration (`schemas/finding.yaml` `maestro_layer`)

The `maestro_layer` enum in `schemas/finding.yaml` has changed values. Downstream consumers (dashboards, scripts, tooling built on the enum) MUST update their code.

| Old Value | New Value |
|-----------|-----------|
| `L5 — Security` | `L5 — Evaluation and Observability` |
| `L6 — Agent Ecosystem` | `L6 — Security and Compliance` |
| `L7 — User Interface` | `L7 — Agent Ecosystem` |
| `L6 — Integration Services` (Typst template bug) | `L6 — Security and Compliance` |

L1–L4 enum values are unchanged.

#### Schema Version Bump

`schemas/finding.yaml` schema version bumped from `1.2` to `1.3`. This signals the enum-value-only breaking change. The schema shape and required fields are unchanged — only the allowed values for `maestro_layer` changed. Per ADR-020, enum-value-only breaking changes warrant a minor schema bump (not major), provided schema shape and required fields are unchanged.

#### Acronym Correction

The MAESTRO acronym expansion in `.claude/skills/tachi-shared/references/maestro-layers-shared.md` (line 17) and `docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md` (line 123) has been corrected from:

- **Old**: "Multi-Agent Environment Security Toolkit for Reasoning and Orchestration"
- **New**: "Multi-Agent Environment, Security, Threat, Risk, and Outcome"

The new form matches the canonical CSA source.

#### Typst PDF Template Fix

`templates/tachi/security-report/maestro-findings.typ` fallback dictionary (lines 132-134) previously contained `"L6": "Integration Services"` — a third divergent name matching neither the canonical CSA spec nor the prior shared reference. This pre-existing bug was corrected as part of this fix.

#### Regenerated Example Outputs

All six example architectures in `examples/*` have had their threat model outputs regenerated with canonical layer names:

- `examples/web-app/` — threats.md + security-report.pdf.baseline
- `examples/microservices/` — threats.md + security-report.pdf.baseline
- `examples/ascii-web-api/` — threats.md + security-report.pdf.baseline
- `examples/free-text-microservice/` — threats.md + security-report.pdf.baseline
- `examples/mermaid-agentic-app/` — threats.md + threat-report.md + threat-infographic-spec.md + attack-trees/ + security-report.pdf.baseline
- `examples/agentic-app/sample-report/` — full pipeline (threats.md, risk-scores.md, compensating-controls.md, threat-report.md, infographic specs, security-report.pdf)

The five non-agentic-app PDF baselines are byte-deterministic under `SOURCE_DATE_EPOCH=1700000000` per ADR-021. The agentic-app sample remains intentionally excluded from byte-determinism testing due to non-deterministic Gemini infographic generation.

#### New L5 Keyword Set

A new L5 Evaluation and Observability keyword section has been added covering: audit log, monitoring, observability, telemetry, anomaly detection, SIEM, forensics, behavioral monitoring, metrics, human oversight, log aggregation. Previously, findings targeting audit loggers and observability components had no dedicated layer and were misrouted or lost.

#### Downstream Migration Guidance

If you consume tachi output programmatically:

1. Update any hardcoded references to the old layer names (see enum migration table above)
2. Update any scripts parsing `maestro_layer` values from `threats.md`, `risk-scores.md`, or `compensating-controls.md`
3. Regenerate any custom report templates that reference layer names
4. Check `schema_version` field — expect `"1.3"` going forward

#### References

- PRD: [docs/product/02_PRD/136-maestro-canonical-layer-correctness-fix-2026-04-10.md](docs/product/02_PRD/136-maestro-canonical-layer-correctness-fix-2026-04-10.md)
- Spec: [specs/136-maestro-canonical-layer/spec.md](specs/136-maestro-canonical-layer/spec.md)
- Plan: [specs/136-maestro-canonical-layer/plan.md](specs/136-maestro-canonical-layer/plan.md)
- ADR-020 (canonical taxonomy rule): [docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md](docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md)
- GitHub Issue: [#136](https://github.com/davidmatousek/tachi/issues/136)

---

## [4.9.2](https://github.com/davidmatousek/tachi/compare/v4.9.1...v4.9.2) (2026-04-10)


### Bug Fixes

* **138:** lowercase attack tree PNG filenames to match convention ([#139](https://github.com/davidmatousek/tachi/issues/139)) ([1400e47](https://github.com/davidmatousek/tachi/commit/1400e478ff58a9f1357f69d42c62ea0437e0d4c8)), closes [#138](https://github.com/davidmatousek/tachi/issues/138)

## [4.9.1](https://github.com/davidmatousek/tachi/compare/v4.9.0...v4.9.1) (2026-04-10)


### Bug Fixes

* **134:** threat-report attack tree baseline, MAESTRO layer rendering, filename convention ([#135](https://github.com/davidmatousek/tachi/issues/135)) ([716df8e](https://github.com/davidmatousek/tachi/commit/716df8e9c98768eb5edf5d87be943833aab81ab1)), closes [#134](https://github.com/davidmatousek/tachi/issues/134)

## [4.9.0](https://github.com/davidmatousek/tachi/compare/v4.8.0...v4.9.0) (2026-04-10)


### Features

* **128:** add executive threat architecture infographic with early-page PDF positioning ([#131](https://github.com/davidmatousek/tachi/issues/131)) ([7b217fe](https://github.com/davidmatousek/tachi/commit/7b217fe2447ba758db770ec1be0ac428e23fa252))

## [4.8.0](https://github.com/davidmatousek/tachi/compare/v4.7.0...v4.8.0) (2026-04-09)


### Features

* **120:** add architecture lifecycle command ([#124](https://github.com/davidmatousek/tachi/issues/124)) ([f814c02](https://github.com/davidmatousek/tachi/commit/f814c027db03cf5424599b640bd99ac1aa8cd37e))

## [4.7.0](https://github.com/davidmatousek/tachi/compare/v4.6.0...v4.7.0) (2026-04-09)


### Features

* **121:** rename tachi commands to tachi.* dot-namespace ([#122](https://github.com/davidmatousek/tachi/issues/122)) ([7d0f968](https://github.com/davidmatousek/tachi/commit/7d0f9684166a8fd6af10517fcca3f1aa85abad73))

## [Unreleased]

### Added

- **Executive Threat Architecture Infographic** (Feature 128) — New `/tachi.infographic --template executive-architecture` (alias: `exec`) generates a layered architecture diagram with Critical/High finding callouts, designed for CISO-level readers. In the compiled PDF security report the new page lands immediately after the Executive Summary (pages 2–3 area) so executives see the visual threat narrative within their first-glance window. Included in the `all` shorthand expansion alongside the existing five templates. Backward compatible — example PDFs without a generated `threat-executive-architecture.jpg` render byte-identical to the pre-F-128 baseline. Ships with tachi's first project-level pytest harness (`pyproject.toml`, `requirements-dev.txt`, `tests/`) and five committed `.baseline` PDFs guarding backward compatibility against silent regressions.
- **Architecture Lifecycle Command** (Feature 120) — `/tachi.architecture` now tracks versions with YAML frontmatter (version, date, description, SHA-256 checksum), archives previous versions to `.archive/v{N}/`, and supports guided updates through change categories. `/tachi.threat-model` automatically snapshots the architecture file into each timestamped output folder for full traceability. Backward compatible with existing architecture files.

### Changed

- **Command Namespace Migration** (Feature 121) — All tachi pipeline commands renamed from unprefixed names to `tachi.*` namespace prefix. New `/tachi.architecture` command added. Install script now cleans up deprecated command files on upgrade. See migration table below.

#### Command Name Migration

| Old Command | New Command |
|-------------|-------------|
| `/threat-model` | `/tachi.threat-model` |
| `/risk-score` | `/tachi.risk-score` |
| `/compensating-controls` | `/tachi.compensating-controls` |
| `/infographic` | `/tachi.infographic` |
| `/security-report` | `/tachi.security-report` |
| *(new)* | `/tachi.architecture` |

Upgrading: Run `install.sh` — it automatically removes old unprefixed command files and installs the new `tachi.*` versions.

---

## [4.6.0](https://github.com/davidmatousek/tachi/compare/v4.5.0...v4.6.0) (2026-04-09)


### Features

* **119:** auto-polish release notes via Claude API after release ([a44127f](https://github.com/davidmatousek/tachi/commit/a44127fccd11aef959cc1939670158ac8dffabb6)), closes [#119](https://github.com/davidmatousek/tachi/issues/119)


### Bug Fixes

* **119:** move release notes polishing to local-only script ([0dd33fd](https://github.com/davidmatousek/tachi/commit/0dd33fd4c4fd686393207837485386afac16ad03))

## [4.5.0](https://github.com/davidmatousek/tachi/compare/v4.4.2...v4.5.0) (2026-04-09)

### Added

- **Attack Path Pages in PDF Reports** (Feature 112) — Each Critical and High finding with an attack tree now gets a dedicated page in the security report PDF, showing a rendered Mermaid diagram, plain-English narrative explaining the attack chain, and specific remediation steps. Pages are ordered by severity (Critical first) and introduced by an "Attack Path Analysis" section divider with TOC entry. Mermaid diagrams render to PNG at 2x resolution via `mmdc`; graceful text fallback when the tool is unavailable. Fully backward compatible — reports without attack trees generate identically to before.
- **Automated release notes polishing** (Feature 119) — Local script (`scripts/polish-release-notes.sh`) rewrites auto-generated release notes into user-facing language via Claude API. Run after merging a Release PR.
- **README refresh** — Updated with MAESTRO layer classification, `/security-report` command, baseline delta tracking, all 5 infographic templates, and 6 examples (was 3).

### Changed

- release-please now hides `docs`, `chore`, `refactor`, `test`, and `style` commits from auto-generated CHANGELOG entries. Only `feat`, `fix`, and `perf` appear.

---

## [4.4.2](https://github.com/davidmatousek/tachi/compare/v4.4.1...v4.4.2) (2026-04-09)

### Fixed

- MAESTRO heading detection now falls back gracefully when headings use inconsistent formatting in threat-report.md. Attack trees regenerated fresh for all 6 examples. MAESTRO Findings section now appears in all reports and PDF output.

---

## [4.4.1](https://github.com/davidmatousek/tachi/compare/v4.4.0...v4.4.1) (2026-04-09)

### Fixed

- Attack tree generation no longer includes RESOLVED findings. Previously, findings marked as resolved in a baseline comparison still produced attack trees, cluttering the report with irrelevant attack paths.

---

## [4.4.0](https://github.com/davidmatousek/tachi/compare/v4.3.4...v4.4.0) (2026-04-09)

### Added

- **Downstream Baseline Propagation** (Feature 104) — Baseline severity and status fields from `threats.md` now propagate through all pipeline stages: risk scoring, compensating controls, threat report, infographics, and PDF report. Delta annotations (NEW, UNCHANGED, UPDATED, RESOLVED) carry through the entire pipeline. New Section 8 (Delta Summary) in `threats.md` and `threat-report.md`. All 6 example outputs regenerated with baseline columns.

---

## [4.3.4](https://github.com/davidmatousek/tachi/compare/v4.3.3...v4.3.4) (2026-04-08)

### Fixed

- Baseline-aware pipeline now enforces mandatory Phase 2 discovery even when a baseline exists, preventing false confidence from carry-forward-only runs.

---

## [4.3.3](https://github.com/davidmatousek/tachi/compare/v4.3.2...v4.3.3) (2026-04-08)

### Fixed

- Baseline auto-detection now correctly resolves paths, and downstream commands (`/risk-score`, `/compensating-controls`) no longer exceed context limits when processing large baseline files.

---

## [4.3.2](https://github.com/davidmatousek/tachi/compare/v4.3.1...v4.3.2) (2026-04-08)

### Fixed

- Version reporting (`install.sh`) now fetches tags before checking the installed version, showing the correct tag instead of a commit hash.
- release-please respects `release-please-config.json` instead of using a hardcoded release type.

---

## [4.3.1](https://github.com/davidmatousek/tachi/compare/v4.3.0...v4.3.1) (2026-04-08)

### Fixed

- Version examples in README and `install.sh` now auto-bump via release-please extra-files configuration.

---

## [4.3.0](https://github.com/davidmatousek/tachi/compare/v4.2.1...v4.3.0) (2026-04-08)

### Added

- **MAESTRO Infographic Templates and PDF Report Section** (Feature 091) — Two new infographic templates for MAESTRO-aware threat visualization: `maestro-stack` (vertical seven-layer risk distribution diagram) and `maestro-heatmap` (component-by-layer severity grid). New MAESTRO Findings page in the PDF security report. `maestro` shorthand in `/infographic` generates both templates in one invocation. All gated by `has-maestro-data` for backward compatibility with non-agentic threat models.

---

## [4.2.1](https://github.com/davidmatousek/tachi/compare/v4.2.0...v4.2.1) (2026-04-08)

### Fixed

- release-please workflow now supports `workflow_dispatch` for manual re-runs.

---

## [4.2.0](https://github.com/davidmatousek/tachi/compare/v4.1.0...v4.2.0) (2026-04-08)

### Added

- **MAESTRO Layer Mapping** (Feature 084) — Every threat finding is now classified into the CSA MAESTRO seven-layer taxonomy (L1 Foundation Model through L7 User Interface). The orchestrator assigns layers via keyword classification in Phase 1, and the mapping propagates downstream through risk scoring, compensating controls, and the threat report. New `maestro_layer` field in the finding schema (v1.2), SARIF `maestro-layer` tags, and MAESTRO Layer columns in all output tables. All 6 example outputs regenerated.

---

## [4.1.0](https://github.com/davidmatousek/tachi/compare/v4.0.0...v4.1.0) (2026-04-07)

### Added

- **Automated Release Tagging** (Feature 086) — Releases are now automated via Google's release-please GitHub Action. Conventional commits on main trigger a Release PR with auto-generated CHANGELOG entries. Merging the Release PR creates the git tag and GitHub Release. New files: `.github/workflows/release-please.yml`, `release-please-config.json`, `.release-please-manifest.json`.

---

## 4.0.x — Pre-release-please Features

*These features shipped between v4.0.0 and v4.1.0, before release-please was adopted. They were not individually tagged.*

### Feature 112 context already captured in v4.5.0 above.

### Feature 078 — Agent Context Optimization

Restructured 6 tachi agents from monolithic prompts to lean definitions with on-demand skill references. Created 4 skill directories with 25+ granular reference files. Shared severity bands, STRIDE+AI categories, and finding format as single-source-of-truth. 40-60% prompt size reduction across methodology agents.

### Feature 075 — Tachi Agent Best Practices

Shared best practices document with tier caps (Leaf 300, Report 800, Methodology 1,000 lines), 8-criterion quality checklist. Extracted domain knowledge from orchestrator (-39%), report agent (-41%), and control-analyzer (-30%) into dedicated skills.

### Feature 074 — Baseline-Aware Pipeline

Baseline-aware threat detection with 4-phase correlation (detect, carry-forward, discover, merge+dedup), coverage checklists per component type, delta annotations (NEW, UNCHANGED, UPDATED, RESOLVED), and SARIF `baselineState` properties. Compare threat model runs to track risk posture changes over time.

### Feature 071 — Deterministic Infographic Data Extraction

Shared parser module (`scripts/tachi_parsers.py`) and deterministic extraction script (`scripts/extract-infographic-data.py`) replacing LLM-based markdown parsing for infographics. Largest Remainder Method for percentage rounding, deterministic tie-breaking, 4-tier risk funnel computation. Python 3.9+ stdlib only.

### Feature 067 — Deterministic Report Data Extraction

Deterministic Python parsing script (`scripts/extract-report-data.py`) replacing LLM-based markdown extraction for PDF report generation. 3-tier severity source selection, internal consistency validation, scope data extraction. Zero external dependencies.

### Feature 066 — Install Script and Version Tagging

Single-command install script (`scripts/install.sh`) replacing 6+ manual `cp` commands. Supports `--source` override, `--version` pinned installs with trap-based cleanup. First semantic version tag `v4.0.0`.

### Feature 060 — Professional PDF Security Report

Professional branded PDF with modular Typst template system: disclaimer, TOC, methodology, scope, theme, and report-config pages. `brand/` asset directory with logo variants. Extended `security-report.yaml` schema v1.1.

### Feature 054 — Security Assessment PDF Booklet

`/security-report` command and report-assembler agent for generating multi-page PDF security assessment booklets from tachi pipeline artifacts. 7 Typst templates, graceful degradation for partial pipelines, full-bleed landscape infographic pages.

### Feature 053 — Risk Reduction Funnel

4-tier risk reduction funnel infographic template with graceful degradation (4-tier/3-tier/1-tier modes), ghost tiers with CTAs, and metrics sidebar.

### Feature 048 — Infographic Tiered Pipeline Auto-Detection

Three-tier data source auto-detection for `/infographic` (compensating-controls.md > risk-scores.md > threats.md). Residual risk extraction, enhancement tips at each pipeline tier, risk label distinction across templates.

### Feature 045 — Developer Guide

Comprehensive developer guide covering tachi's command pipeline with step-by-step walkthrough, pipeline diagram, and command reference.

### Feature 039 — Standalone /infographic Command

`/infographic` as a standalone command with auto-detection, dual-path extraction, and template selection. Removed from `/threat-model` pipeline (now 5-phase only).

### Feature 036 — Compensating Controls Analysis

`/compensating-controls` command with 6-phase pipeline, 8 STRIDE + 2 AI control categories, effectiveness classification, residual risk calculation, and dual-format output (markdown + SARIF).

### Feature 035 — Quantitative Risk Scoring

`/risk-score` command with four-dimensional scoring (CVSS 3.1, exploitability, scalability, reachability), weighted composite scores, governance fields, and dual-format output (markdown + SARIF).

### Feature 029 — Agent Right-Sizing

Right-sized 3 threat agents via reference-extraction pattern: orchestrator (-39%), report (-41%), infographic (-30%). 6 reference docs extracted. Portable `.claude/agents/tachi/` agent set.

### Feature 024 — Example Threat Models

Three end-to-end examples: web-app (STRIDE), agentic-app (STRIDE + AI), microservices (cross-service STRIDE). Each with Mermaid architecture and schema v1.1 output.

### Feature 021 — Platform Adapters

Adapters for 5 targets: Claude Code, Generic, Cursor, Copilot, GitHub Actions (with SARIF upload).

### Feature 018 — Threat Infographic Agent

Visual risk spec generation with Gemini API image output. Integrated as orchestrator Phase 6.

### Feature 015 — Threat Report Agent & Attack Trees

Narrative threat report with STRIDE+AI attack trees (Mermaid). 7-section template with 12 attack tree examples.

### Feature 012 — SARIF Output Generation

SARIF 2.1.0 output with STRIDE+AI rule mapping, CVSS severity alignment, deterministic fingerprints, and optional OWASP/CWE taxonomies.

### Feature 010 — Deduplication & Risk Rating

Cross-agent finding correlation with 5 deterministic rules, three-state coverage matrix, and OWASP 3x3 risk calibration. Schema v1.1.

### Feature 007 — AI Threat Agents

5 AI threat agent prompts: prompt injection, data poisoning, tool abuse, model theft, agent autonomy.

### Feature 003 — Orchestrator Agent

Orchestrator with 4-phase OWASP workflow, 5-format input parsing, 11-agent dispatch, and structured output assembly.

### Feature 001 — Project Skeleton

Project skeleton with STRIDE + AI threat agent prompts, schemas, output template, interface contract, and 3 example inputs.

---

## [4.0.0](https://github.com/davidmatousek/tachi/compare/v3.0.0...v4.0.0) (2026-02-08)

### BREAKING CHANGES

- **AOD Rebranding** — `.specify/` directory renamed to `.aod/`, `docs/SPEC_KIT_TRIAD.md` renamed to `docs/AOD_TRIAD.md`, environment variables and log prefixes updated. Update any local scripts referencing `.specify/` paths.

### Added

- 3 new thinking lenses: Four Causes, Cargo Cult Detection, Golden Mean.

---

## [3.0.0](https://github.com/davidmatousek/tachi/compare/v2.1.0...v3.0.0) (2026-02-07)

### BREAKING CHANGES

- **SpecKit commands removed** — All `/speckit.*` commands consolidated into `/triad.*`. See [migration table in previous CHANGELOG](https://github.com/davidmatousek/tachi/blob/v3.0.0/CHANGELOG.md) for command mapping.

### Added

- 4 new triad commands: `/triad.clarify`, `/triad.analyze`, `/triad.checklist`, `/triad.constitution`.

### Removed

- All 8 `/speckit.*` command files and "Vanilla Commands" documentation.

---

## [2.1.0](https://github.com/davidmatousek/tachi/compare/v2.0.0...v2.1.0) (2026-01-31)

### Added

- Agent refactoring: all 12 agents restructured to consistent 8-section format (58% line reduction). Team-lead split into team-lead + orchestrator (13 agents). New thinking-lens skill.

---

## [2.0.0](https://github.com/davidmatousek/tachi/compare/v1.1.0...v2.0.0) (2026-01-24)

### Added

- **Parallel Triad Reviews** — PM + Architect reviews run simultaneously with context forking. Triple sign-off executes in parallel.
- Automatic Claude Code version detection with feature flags and graceful degradation.

---

## [1.1.0](https://github.com/davidmatousek/tachi/compare/v1.0.0...v1.1.0) (2025-12-15)

### Added

- Modular rules system: governance, git workflow, deployment, scope, commands, and context loading extracted from CLAUDE.md (192 → 70 lines).

---

## [1.0.0](https://github.com/davidmatousek/tachi/releases/tag/v1.0.0) (2025-12-04)

### Added

- Initial release: product-led governance template, SDLC Triad framework, 13 agents, 8 skills, triad + vanilla commands, documentation structure.
