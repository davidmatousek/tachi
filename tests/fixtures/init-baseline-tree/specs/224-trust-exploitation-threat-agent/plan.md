---
spec_reference: .aod/spec.md
prd_reference: docs/product/02_PRD/224-trust-exploitation-threat-agent-2026-04-26.md
triad:
  pm_signoff: {agent: product-manager, date: 2026-04-26, status: APPROVED, notes: "15/15 SCs assigned to Waves with concrete deliverables; 19/19 FRs traced to Wave anchors with double-anchoring on FR-013 (Wave 2 + Wave 4), FR-019 (Wave 1.1 + Wave 6), R6 (Wave 1.3 + Wave 4), R12 (Wave 1.1 + Wave 6 pre-merge + Wave 6 post-merge); 6/6 architect Q1-Q6 binding decisions captured in Open Questions table; 12/12 risks (R1-R12) carried forward with active wave-anchored mitigations; 26-file zero-edit invariant + agent-autonomy.md NOT-edit discipline anchored at 9 plan locations; 11/11 Constitution Check principles PASS (incl. new XI Naming Discipline); NFR-006 four safe-language patterns enforced at Wave 2 + Wave 6; NFR-007 self-disclosure discipline enforced at Wave 2 + Wave 6; three-prefix-family discipline (SC-014) verified at Wave 5; two-part emission gate (FR-013) verified at Wave 4 BEFORE Wave 5 regen (critical sequencing explicit); R10 enforceable trigger at Wave 3 Step 0 via gh queries; Q5 conditional fallback gate at Wave 3 Step 1; Wave 1.3 EOD pre-positioning eliminates Wave 2→3 friction; Pre-Mortem lens (6 failure modes anticipated) + Systems Thinking lens (no suspect coupling) both confirm sound design. One LOW non-blocking concern: cosmetic wave-numbering nomenclature drift between PRD timing (Wave 1.0/1.1/1.2/1.3, 2.0/2.1/2.2/2.3) and plan numbering (Wave 1-7); plan reconciles via in-line PRD-timing translations; optional translation table at /aod.tasks. Plan READY for Architect plan-stage review (architect sign-off still required separately before /aod.tasks). Full review at .aod/results/product-manager.md §Plan-Stage Review."}
  architect_signoff: {agent: architect, date: 2026-04-26, status: APPROVED_WITH_CONCERNS, notes: "14/14 architect review dimensions PASS. Plan.md technically sound and architecturally faithful to PRD-224 v2 + spec.md. All architect BLOCKING-1 (Process-only DFD reversal) + HIGH-1 (rename to human-trust-exploitation) + HIGH-2 (ASI09 sub-scope carve-up with agent-autonomy.md NOT-edit) + HIGH-3 (Agentic DUO→TRIO) + MEDIUM-2 (CWE-287 added) + MEDIUM-3 (ATLAS sparseness) + MEDIUM-4 (Q5 conditional fallback) + MEDIUM-5 (Wave 2.0 grep-checklist) + LOW-1/2 fixes preserved with multi-anchor verification. ADR-023 lean-agent conformance verified (≤150 lines + single MANDATORY Read + zero MAESTRO grep on agent + companion); F-1/F-2 baseline disk state confirmed (output-integrity 120 lines, misinformation 120 lines). Schema bump 1.7→1.8 third recorded application of ADR-030 D8 regex-alternation rule (additive-compatible). 6 coordinated edits across orchestrator.md (3 — including Edit 3 sequential-mode text confirmed will fire given disk state at orchestrator.md:297 explicit enumeration) + dispatch-rules.md (3); FR-009 Wave 2.0 grep-checklist explicit. 26-file zero-edit invariant including agent-autonomy.md NOT-edit verified (carve-up at ADR-033 body item 2 layer only; agent-autonomy.md:17 retains ASI-09 in owasp_references unchanged). source_attribution contract: catalog-resolved CWE-223/287/290/345 verified on disk (cwe.yaml lines 82/106/110/118); CWE-451 confirmed absent → prose-only; MITRE ATLAS prose-only (AML.T0060 offensive use-case at mitre-atlas.yaml:83-87); external regulatory refs prose-only. Heuristic A four-way scope resolution + ASI09 sub-scope carve-up at ADR-033 body item 2; ADR-030 D2 Outcome B reservation explicit consumption confirmed. ADR-033 10 body items (8 PRD-original + 2 architect-required: Naming Disambiguation HIGH-1 + DFD Target Decision BLOCKING-1) preserved verbatim. Two-part emission gate FR-013 + 5-category pattern catalog with persona anti-indicator + byte-identity preservation on 5 non-consumer-facing baselines + 6 dependencies on-disk verified (F-A1+F-A2+F-B+F-1+F-2+F-3) + zero new deps SC-008 + Wave sequencing (Wave 1.0 Heuristic A gate; Wave 1.3 EOD review; Wave 3 Step 0 R10 enforceable trigger → Step 1 Q5 fallback gate → Step 2 architect lands edits → Step 3 grep-checklist; Wave 4 false-positive check before Wave 5 regen; Wave 6 pre-merge title check + post-merge release-please) + R11 mitigation (ADR-033 §Naming Disambiguation + FR-018 grep test) + R12 mitigation (PR title two-step at Wave 1.1 + Wave 6) all PASS. Pre-Mortem on Wave 3 ordering + Systems Thinking on F-1+F-2+F-3 reconciliation / ADR-030 D2 Outcome B / ADR-030 D8 third application / F-5 concurrency / 3-prefix-family agentic + 6-prefix-family AI threat surface — all sound. Three plan-stage residuals (MEDIUM-A R10 schema-touch grep-disambiguation, MEDIUM-B Q5 fallback expected-diff manifest, LOW-C F-5 schema-baseline forward-pointer) absorbed at /aod.tasks task-level enforcement; none gate-blocking. No re-adjudication of Q1-Q6 required. Ready for /aod.tasks. Full review at .aod/results/architect.md."}
  techlead_signoff: null   # Added by /aod.tasks
---

# Implementation Plan: `human-trust-exploitation` Threat Agent (OWASP ASI09:2026)

**Branch**: `224-trust-exploitation-threat-agent` | **Date**: 2026-04-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `.aod/spec.md`
**PRD**: [docs/product/02_PRD/224-trust-exploitation-threat-agent-2026-04-26.md](../docs/product/02_PRD/224-trust-exploitation-threat-agent-2026-04-26.md)
**BLP-01 Phase**: Tier 1 F-4 — fourth net-new threat detection agent under the BLP-01 governance umbrella; follows F-1 Feature 201 (`output-integrity`) merged 2026-04-19, F-2 Feature 206 (`misinformation`) merged 2026-04-24, F-3 Feature 219 (`tool-abuse` enrichment) merged 2026-04-26; closes OWASP ASI09:2026 communication axis on the BLP-01 Coverage Matrix

## Summary

Author one new AI-tier threat agent `human-trust-exploitation` and its companion skill directory to detect OWASP ASI09:2026 — the human-victim communication-axis signal class covering undisclosed AI authorship, authority-claim emission without confidence/source attestation, persuasive-tone manipulation / missing uncertainty disclosure, persona-boundary violations on long-running dialogues, and synthetic-relationship exploitation. The agent emits findings with `TE-{N}` ID prefix and `category: agentic`, every finding carrying a populated `source_attribution` array citing OWASP ASI09:2026 (primary) plus applicable CWEs (CWE-223, CWE-345, CWE-287, CWE-290). Structure conforms to the ADR-023 lean-agent detection variant established in Feature 082 for the original 11 threat agents and extended by F-1 (`output-integrity`) and F-2 (`misinformation`).

**Architectural approach**: Mirror F-2 (`misinformation.md`) verbatim in shape — it is the closest sibling and the immediate precedent for "third-execution standalone-branch new AI-tier threat agent under ADR-023 lean pattern": 5-section canonical layout, ≤150 lines, single `**MANDATORY**: Read` directive under `## Detection Workflow`, zero MAESTRO references. Two orchestrator-tier additive edits register the new agent in dispatch (`orchestrator.md` dispatch list + Agentic Threats row DUO → TRIO; `dispatch-rules.md` Agentic dispatch DUO → TRIO + table row + trigger-keyword rules). One additive edit to `finding-format-shared.md` `consumers:` frontmatter (tier-grouping placement: Agentic-category cluster, between `tool-abuse` and `output-integrity`). One additive schema regex bump (`schemas/finding.yaml` 1.7 → 1.8 extending `id.pattern` to include `TE` prefix — third recorded application of ADR-030 Decision 8 regex-alternation minor-bump rule). One public per-feature ADR (ADR-033) under Proposed → Accepted dual-commit pattern with **10 body items** (8 PRD-original + 2 architect-required additions: §Naming Disambiguation + §DFD Target Decision). One example regeneration target — Q5 lean: new `examples/consumer-agent-app/`; conditional fallback to `examples/agentic-app/` extension at Wave 2.0 AM gate (architect MEDIUM-4).

**Touch points**: 1 new agent file, 1 new companion skill directory (README + detection-patterns.md), 6 coordinated additive edits across 2 orchestrator-tier files (3 in orchestrator.md, 3 in dispatch-rules.md — Wave 2.0 grep-checklist verifies), 1 additive edit to `finding-format-shared.md`, 1 schema regex edit + version bump, 1 new ADR with 10 body items, 1 example regeneration. Zero edits to the 26 existing detection-tier files (13 threat agents + 13 companion `detection-patterns.md`; 22 original + F-1's 2 + F-2's 2; F-3 enrichment-edits to `tool-abuse.md` + companion are reconciled into the post-F-3 baseline). **Critically: `agent-autonomy.md` is NOT edited** despite the ASI09 sub-scope carve-up — the carve-up is documented in ADR-033 body item 2, not at the metadata layer. Zero edits to infrastructure-tier consumers (risk-scorer, control-analyzer, threat-report, threat-infographic, report-assembler), zero new runtime dependencies.

## Technical Context

**Language/Version**: Markdown + YAML + Python 3.11 (existing — stdlib + `pyyaml`); agents and skills are markdown/YAML content files, not executable code
**Primary Dependencies**: `pyyaml` (runtime, already declared), `pytest` (dev-only, already declared per Feature 128 precedent); no new runtime or dev dependencies
**Storage**: File-based; reads `schemas/finding.yaml` (v1.7 pre-edit, v1.8 post-edit), `schemas/taxonomy/{owasp,cwe,mitre-atlas,nist-ai-rmf}.yaml` (F-A1 catalogs for `source_attribution` validation); writes to `.claude/agents/tachi/`, `.claude/skills/tachi-human-trust-exploitation/`, `docs/architecture/02_ADRs/`, `examples/consumer-agent-app/` (or `examples/agentic-app/` per Q5 fallback)
**Testing**: pytest (existing harness at `tests/scripts/`) + backward-compatibility test `tests/scripts/test_backward_compatibility.py` under `SOURCE_DATE_EPOCH=1700000000` (ADR-021) — 5 non-consumer-facing baselines byte-identity; regex unit test for schema 1.8 `id.pattern`; referential-integrity fixtures for `TE-{N}` source_attribution; FR-018 grep-checkable test for AGP-vs-TE prose-synthesis-prevention on regenerated example
**Target Platform**: Command-line Python tooling (macOS/Linux/WSL); orchestrator + threat agents invoked via `/tachi.threat-model` Claude command; PDF rendering via Typst + Mermaid CLI (unchanged)
**Project Type**: Single project (methodology toolkit — agents + skills + schemas + templates in a unified repo); no frontend/backend split
**Performance Goals**: Agent dispatch + pattern evaluation <5s on the regenerated example (informational floor, within existing `/tachi.threat-model` budget); no new performance regressions
**Constraints**: (a) SC-006 byte-identity on 5 non-consumer-facing baselines under `SOURCE_DATE_EPOCH=1700000000` is a BLOCKER; (b) SC-009 26-file zero-edit invariant on 13 threat agents + 13 companion skill references (22 original + F-1's 2 + F-2's 2; F-3 reconciled) **including `agent-autonomy.md` NOT-edit despite the ASI09 sub-scope carve-up** is a BLOCKER; (c) FR-001 zero MAESTRO references in agent + companion is a grep-auditable invariant; (d) SC-010 F-A2 referential-integrity validation must pass on every emitted `TE-{N}` finding; (e) SC-008 zero new runtime or developer dependencies is a BLOCKER; (f) FR-013 two-part emission gate (AI keyword AND human-user-facing emission indicator) is a correctness BLOCKER — keyword match alone MUST NOT emit; (g) SC-014 three-prefix-family discipline within agentic category (AG / AGP / TE adjacent without prose synthesis) is a quality predicate; (h) NFR-006 four safe-language patterns enforced verbatim on all 5 worked examples; (i) NFR-007 self-disclosure discipline applied to all agent-authored prose
**Scale/Scope**: 1 new agent file (~100-150 lines), 1 new companion README (~30-50 lines), 1 new detection-patterns.md (~250-350 lines), 5 pattern categories, ~22 trigger keywords (architect-curated per Q2 binding; final count tightened or expanded at architect Wave 1.0 review per architect MEDIUM-A residual concern), 4 indicator categories in Human-User-Facing Emission Indicators subsection, 2-3 example findings in agent file, 5 worked examples in detection-patterns.md (one per pattern category) with NFR-006 safe-language patterns. 6 coordinated edits total (3 orchestrator-tier + 1 shared reference + 1 schema + 1 ADR + 1 example regen). 10 ADR body items (vs. F-1's 8, F-2's 8, F-3's 7 — F-4 carries 2 architect-required additions: Naming Disambiguation + DFD Target Decision).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Evaluated against `.aod/memory/constitution.md`:

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | PASS | Agent detects a generic human-trust communication-axis signal class (AI agent emitting to human user without architectural mechanisms preventing impersonation / over-persuasion / undisclosed authorship); no hardcoded project-type assumptions |
| II. API-First Design | N/A | No REST/GraphQL surface; threat agents are content files consumed by the orchestrator at invocation time |
| III. Backward Compatibility (NON-NEGOTIABLE) | PASS | Two-part emission gate (FR-013) + zero-finding default on non-qualifying architectures → 5 non-consumer-facing baselines byte-identical. Local `.aod/` workflows unaffected. Schema 1.7 → 1.8 is additive regex extension; existing IDs remain valid |
| IV. Concurrency & Data Integrity | N/A | F-4 is single-invocation content authoring; no concurrent state |
| V. Privacy & Data Isolation | PASS | Worked examples use clearly-fictional scenarios per NFR-006 (mental health / eldercare / financial / legal / clinical domains explicitly anonymized with Hypothetical: prefix and "for context, not legal interpretation" framing); no PII, no adopter data, no network calls by the agent |
| VI. Testing Excellence (MANDATORY) | PASS | Regex unit test for schema 1.8 `id.pattern`; fixture-driven tests for `source_attribution` referential integrity on `TE-{N}` findings; backward-compat byte-identity gate on 5 baselines; structural-diff check on agent line-count + MANDATORY-Read count + zero MAESTRO grep; FR-018 grep-checkable test for AGP-vs-TE prose-synthesis-prevention; FR-009 Wave 2.0 grep-checklist verifying all 6 coordinated edits |
| VII. Definition of Done (NON-NEGOTIABLE) | PASS | Spec-defined SCs (SC-001 through SC-015) map to testable predicates. SC-006 + SC-009 + SC-010 are BLOCKER-level gates; DoD bullet 12 (delivery retrospective) carried via team-lead MEDIUM-3 buffer-day default-slotting |
| VIII. Product-Spec Alignment | PASS | Approved PRD 224 exists (PM APPROVED, Architect APPROVED, Team-Lead APPROVED_WITH_CONCERNS with all 0 BLOCKING / 2 HIGH / 3 MEDIUM / 2 LOW absorbed inline); spec.md has PM APPROVED_WITH_CONCERNS sign-off (2 non-blocking concerns absorbed inline at NFR subsection addition + LOW-A governance observation) |
| IX. Git Workflow | PASS | Feature branch `224-trust-exploitation-threat-agent` created at /aod.plan stage; draft PR #225 opened with `feat(224):` Conventional-Commit prefix per F-212 incident-prevention discipline (R12 mitigation); no main commits; Proposed → Accepted dual-commit ADR pattern |
| X. Zero-Edit Invariant (ADR-023 lineage) | PASS | FR-014 / SC-009 explicit; orchestrator-tier carve-out documented per F-1 + F-2 + Feature 142 precedent; grep audit at PR pre-merge; invariant now 26 files (22 original + F-1's 2 + F-2's 2; F-3 enrichment-edits reconciled). **agent-autonomy.md NOT-edit invariant explicit despite ASI09 sub-scope carve-up — carve-up documented at ADR-033 body item 2 layer** |
| XI. Naming Discipline (Naming Disambiguation) | PASS | Repository slug `224-trust-exploitation-threat-agent` preserved per `.claude/rules/git-workflow.md` `NNN-descriptive-name` convention; agent / file / directory / schema-prefix names use disambiguated `human-trust-exploitation` (hyphen-cased) per architect HIGH-1 fix; explicit contrast vs. existing `trust_exploitation` agentic_pattern enum value (underscore-cased, Feature 142, multi-agent topology) documented in ADR-033 §"Naming Disambiguation" (FR-012 body item 9); FR-018 grep-checkable test verifies no prose synthesis at threat-report rendering |

**Gate verdict**: No violations. No Complexity Tracking entries required. F-4 is a third-execution standalone-branch repeat of the F-1 / F-2 pattern with deltas constrained to: (a) different OWASP framework anchor (ASI09 vs. LLM05/09), (b) different DFD-target invariant rationale (Process-only with indicator-level human-user filtering vs. simpler Process-only), (c) different schema-prefix (TE vs. OI/MI), (d) two architect-required additional ADR body items (Naming Disambiguation + DFD Target Decision), (e) ASI09 sub-scope carve-up with `agent-autonomy.md` documented at ADR layer (no metadata-layer edit), (f) NFR-006 four safe-language patterns enforced verbatim on vulnerable-population worked examples, (g) NFR-007 self-disclosure discipline applied to all agent-authored prose, (h) Agentic dispatch DUO → TRIO (vs. F-2's LLM quartet → quintet).

## Project Structure

### Documentation (this feature)

```
.aod/                                # Active workspace (moves to specs/224-trust-exploitation-threat-agent/ at /aod.deliver)
├── plan.md                          # This file (/aod.project-plan output)
├── research.md                      # Phase 0 output (this iteration)
├── data-model.md                    # Phase 1 output — agent metadata shape + finding shape + pattern category shape
├── contracts/
│   └── finding-contract.md          # Finding IR contract for TE-{N} findings (source_attribution + mitigation rules)
├── quickstart.md                    # Phase 1 output — verification walkthrough
├── checklists/
│   └── requirements.md              # Spec quality checklist
├── spec.md                          # PM-approved spec
└── tasks.md                         # Task breakdown (/aod.tasks output)
```

### Source Code (repository root)

```
tachi/
├── .claude/
│   ├── agents/
│   │   └── tachi/
│   │       ├── human-trust-exploitation.md         # NEW — lean AI-tier (agentic-category) agent, ≤150 lines (≤180 hard cap)
│   │       ├── orchestrator.md                     # MODIFY (additive) — add human-trust-exploitation + DUO→TRIO Agentic Threats row + sequential-mode text (if applicable)
│   │       ├── output-integrity.md                 # UNCHANGED (26-file invariant; F-1's agent)
│   │       ├── misinformation.md                   # UNCHANGED (26-file invariant; F-2's agent)
│   │       ├── tool-abuse.md                       # UNCHANGED (26-file invariant; F-3 enrichment baseline)
│   │       ├── agent-autonomy.md                   # UNCHANGED — CRITICAL: not edited despite ASI09 sub-scope carve-up; carve-up documented in ADR-033 body item 2
│   │       ├── prompt-injection.md                 # UNCHANGED
│   │       ├── data-poisoning.md                   # UNCHANGED
│   │       ├── model-theft.md                      # UNCHANGED
│   │       ├── spoofing / tampering / repudiation / info-disclosure / denial-of-service / privilege-escalation.md  # UNCHANGED (6 STRIDE)
│   │       ├── risk-scorer.md                      # UNCHANGED (FR-014 infrastructure-tier invariant)
│   │       ├── control-analyzer.md                 # UNCHANGED
│   │       ├── threat-report.md                    # UNCHANGED
│   │       ├── threat-infographic.md               # UNCHANGED
│   │       ├── report-assembler.md                 # UNCHANGED
│   │       └── attack-tree-delta.md                # UNCHANGED
│   │
│   └── skills/
│       ├── tachi-human-trust-exploitation/         # NEW — companion skill directory
│       │   ├── README.md                           # NEW — consumers + purpose header
│       │   └── references/
│       │       └── detection-patterns.md           # NEW — 5 pattern categories with NFR-006 safe-language patterns
│       │
│       ├── tachi-orchestration/
│       │   └── references/
│       │       └── dispatch-rules.md               # MODIFY (additive) — Agentic DUO → TRIO + table row + trigger-keyword rules
│       │
│       ├── tachi-shared/
│       │   └── references/
│       │       └── finding-format-shared.md        # MODIFY (additive) — consumers: list adds human-trust-exploitation between tool-abuse and output-integrity
│       │
│       ├── tachi-output-integrity/                 # UNCHANGED — F-1's companion skill
│       ├── tachi-misinformation/                   # UNCHANGED — F-2's companion skill
│       ├── tachi-tool-abuse/                       # UNCHANGED — F-3 baseline (post-enrichment Categories 9+10 reconciled)
│       └── tachi-{11 original AI + STRIDE skills}/ # UNCHANGED (26-file invariant)
│
├── schemas/
│   ├── finding.yaml                                # MODIFY — schema_version 1.7 → 1.8; id.pattern regex adds TE prefix; examples list gains TE-1 entry after MI-1
│   └── taxonomy/                                   # UNCHANGED — read-only source for source_attribution validation
│       ├── owasp.yaml                              # ASI09 entry present (verified: lines 318-322; cwe_refs: [])
│       ├── cwe.yaml                                # CWE-223, CWE-287, CWE-290, CWE-345 entries present (verified: lines 82, 106, 110, 118)
│       └── mitre-atlas.yaml                        # AML.T0060 present but offensive-use-case (prose-only); no direct trust-exploitation match
│
├── docs/
│   └── architecture/
│       └── 02_ADRs/
│           └── ADR-033-human-trust-exploitation-agent.md  # NEW — Proposed → Accepted dual-commit, 10 body items
│
├── tests/
│   └── scripts/
│       ├── test_human_trust_exploitation.py        # NEW — regex + source_attribution validation tests
│       ├── test_backward_compatibility.py          # UNCHANGED — 5 non-consumer-facing baselines byte-identity gate
│       └── fixtures/
│           └── human_trust_exploitation/           # NEW — fixture findings
│               ├── valid_te_finding.yaml
│               └── invalid_attribution_finding.yaml
│
├── examples/
│   ├── web-app / microservices / ascii-web-api / mermaid-agentic-app / free-text-microservice / maestro-reference/  # UNCHANGED (SC-006 baselines)
│   ├── agentic-app/                                # CONDITIONAL FALLBACK regeneration target (Q5 fallback at Wave 2.0 AM gate)
│   └── consumer-agent-app/                         # NEW (Q5 lean) — chatbot / mental-health-companion / eldercare-coach archetype
│
└── scripts/
    └── tachi_parsers.py                            # UNCHANGED (F-A2 validate_source_attribution already accepts TE via regex post-bump)
```

**Structure Decision**: Single-project layout (existing tachi repo structure). No new top-level directories. All changes confined to `.claude/agents/`, `.claude/skills/`, `schemas/`, `docs/architecture/02_ADRs/`, `tests/scripts/`, `examples/consumer-agent-app/` (or `examples/agentic-app/` per Q5 fallback). Follows Feature 082 (lean-agent refactor) + Feature 142 (orchestrator-tier additive edits) + Feature 201 F-1 / Feature 206 F-2 (second + third standalone-new-agent authoring) precedent. Repository slug `224-trust-exploitation-threat-agent` preserved per `.claude/rules/git-workflow.md`; agent / file / directory / schema-prefix names use disambiguated `human-trust-exploitation` per architect HIGH-1 fix.

## System Design

### Components

**New components (F-4-owned)**:

1. **`human-trust-exploitation` Threat Agent** (`.claude/agents/tachi/human-trust-exploitation.md`)
   - 5-section canonical shape per ADR-023 (frontmatter → metadata YAML → `## Purpose` → `## Skill References` table → `## Detection Workflow`) with optional `## Example Findings`
   - Metadata: `category: agentic`, `threat_class: ASI`, `dfd_targets: [Process]`, `owasp_references: [OWASP ASI09:2026]`, `output_schema: ../../../schemas/finding.yaml`
   - **No `agentic_pattern` in metadata** — assigned downstream by orchestrator Phase 3.6 per ADR-026 (FR-001)
   - Detection Workflow has exactly one `**MANDATORY**: Read` directive loading the companion `detection-patterns.md`
   - Two-part emission gate (FR-013) explicit in workflow step: AI-agent keyword match AND human-user-facing emission indicator both required
   - Emits `TE-{N}` findings with `category: agentic`, populated `source_attribution`, human-trust-specific mitigation text (AI-disclosure / authority-attestation / persuasion-safeguard / persona-boundary / synthetic-relationship)
   - Line count: ≤150 (AI tier cap per ADR-023), hard ceiling 180
   - **Naming Disambiguation** (FR-012 body item 9): `human-trust-exploitation` agent name (hyphen-cased) is distinct from existing `trust_exploitation` value in `agentic_pattern` enum (`schemas/finding.yaml:162`, underscore-cased, Feature 142 multi-agent topology pattern); `TE` schema prefix is the agent-name-agnostic threat-class abbreviation
   - **NFR-007 self-disclosure discipline**: agent prose models neutral mitigation language ("Implement X" / "Configure Y") without persuasive language

2. **Pattern Catalog** (`.claude/skills/tachi-human-trust-exploitation/references/detection-patterns.md`)
   - Frontmatter: `name`, `description`, `consumers: [tachi-human-trust-exploitation]`, `last_updated: 2026-04-27` (or actual merge date)
   - `## Overview` paragraph explaining scope (human-trust communication-axis signal class; distinct from output-integrity output-sanitization per ADR-030 D1; distinct from misinformation factual-integrity per ADR-031; distinct from agent-autonomy autonomy axis per ADR-033 sub-scope carve-up; OWASP ASI09:2026 communication-axis canonical surface)
   - `## Detection Scope` with three subsections: (a) `### Trigger Keywords` (~22 keywords per FR-005, with `persona` anti-indicator subsection per Q2 LOW-2 discipline), (b) `### Applicable DFD Element Types` (`Process` only per Q4 BLOCKING-1 fix), (c) `### Human-User-Facing Emission Indicators` (4 indicator categories per FR-006 — outgoing Data Flow to human-named External Entity, Process description with human-user-facing keywords, sustained-engagement framing, authority-claim emission framing)
   - `## Detection Patterns` with 5 numbered categories per FR-004: (1) **Undisclosed AI Authorship** (primary OWASP ASI09:2026, related CWE-223), (2) **Authority-Claim Emission Without Confidence/Source Attestation** (primary OWASP ASI09:2026, related CWE-345), (3) **Persuasive-Tone Manipulation / Missing Uncertainty Disclosure** (primary OWASP ASI09:2026, related CWE-345 + optional CWE-223), (4) **Persona-Boundary Violations on Long-Running Dialogues** (primary OWASP ASI09:2026, related CWE-287 + CWE-290), (5) **Synthetic-Relationship Exploitation** (primary OWASP ASI09:2026, related CWE-223 + CWE-290 + vulnerable-population safeguards layer). Each category carries indicators (3-6 bullets), ≥1 worked example with **NFR-006 safe-language patterns** (Hypothetical: prefix; "for context, not legal interpretation" framing; non-clinical distress framing; no real institutional names), primary-source citation, trigger keywords, applicable DFD element types
   - **Anti-indicator discipline** per architect Q2 LOW-2: explicit `persona` anti-indicator subsection — when `persona` keyword appears WITHOUT human-user-facing emission indicator (e.g., prompt-engineering context only), agent emits zero findings on that component
   - **Primary Sources section** cites OWASP ASI09:2026 (catalog-resolvable), CWE-223/287/290/345 (catalog-resolvable), CWE-451 (prose-only — catalog absent at PRD/plan time), MITRE ATLAS AML.T0060 (prose-only — offensive use-case, no defensive match), External regulatory references FTC/FDA/ABA/SEC/SB-1001/AARP (prose-only — not framework-anchored)
   - **NFR-007 self-disclosure discipline**: pattern-catalog prose models neutral mitigation language; the catalog itself is the negative-space example demonstrating disclosure discipline

3. **Companion Skill README** (`.claude/skills/tachi-human-trust-exploitation/README.md`)
   - Mirror `tachi-misinformation/README.md` shape: short description + consumers list header + layout overview

4. **Public Per-Feature ADR** (`docs/architecture/02_ADRs/ADR-033-human-trust-exploitation-agent.md`)
   - Proposed → Accepted dual-commit (ADR-027 / ADR-028 / ADR-029 / ADR-030 / ADR-031 / ADR-032 precedent)
   - Body: **10 items** (8 PRD-original + 2 architect-required additions per FR-012):
     1. **Decision** statement — adopt new `human-trust-exploitation` agent for ASI09 communication-axis closure
     2. **Heuristic A signal-class rationale + ASI09 sub-scope carve-up** (HIGH-2 fix) — four-way scope boundary: distinct from `output-integrity` (ADR-030 D1), distinct from `misinformation` (ADR-031), distinct from `agent-autonomy` autonomy axis (ADR-033 sub-scope carve-up — both retain ASI-09 in `owasp_references`, neither agent edits the other), scoped to human-victim communication axis. Explicit consumption of ADR-030 Decision 2 Outcome B reservation that creates F-4's scope. **No edit to `agent-autonomy.md`** — carve-up at ADR layer only
     3. **Standalone-vs-enrichment branch contrast** — explicit contrast against F-3 / ADR-032 enrichment-branch path: `agent-autonomy`'s autonomy-axis vocabulary (excessive-autonomy / missing-HITL / goal-drift / cascading-failures) does not cover communication-axis vocabulary (AI-disclosure / authority-claim / persuasion / persona / synthetic-relationship); enrichment is structurally not available — Outcome B (standalone) is the only Heuristic A path forward
     4. **Lean-agent shape conformance** per ADR-023 — single-point load, ≤150 lines, zero MAESTRO references
     5. **Cross-references** to ADR-021, ADR-023, ADR-026, ADR-027, ADR-028, ADR-029, ADR-030 (Decision 2 Outcome B reservation + Decision 8 regex-alternation rule third application), ADR-031 (F-2 precedent for second-execution standalone branch), ADR-032 (F-3 precedent for enrichment-branch alternative)
     6. **26-file zero-edit invariant** preservation with **grep-auditable enumeration** (architect MEDIUM-5 fix) — explicit listing of untouched files; new agent + companion are additions; **`agent-autonomy.md` is NOT edited** despite ASI09 sub-scope carve-up
     7. **Commercial framing omitted** per blueprint governance — public ADR stands on technical merits alone
     8. **Revision history** table tracking Proposed → Accepted transition with dates
     9. **(NEW per architect HIGH-1)** **Naming Disambiguation** — explicit documentation of new `human-trust-exploitation` agent name (hyphen-cased file/directory convention) vs. existing `trust_exploitation` agentic_pattern enum value (`schemas/finding.yaml:162`, underscore-cased schema-enum convention; multi-agent topology pattern per Feature 142 / `maestro-agentic-patterns-shared.md:220-231` R-04); the two cover non-overlapping scopes (agent-to-human ASI09 vs. agent-to-agent CSA MAESTRO multi-agent topology); the `TE` finding-prefix is the threat-class abbreviation (agent-name-agnostic, "Trust Exploitation"); FR-018 grep-checkable test verifies no prose synthesis at threat-report rendering
     10. **(NEW per architect BLOCKING-1)** **DFD Target Decision** — explicit rationale for `dfd_targets: [Process]` (Process-only) declaration: F-4 mirrors F-1 / F-2 single-DFD-target precedent; human-user trust boundary captured at indicator level within `detection-patterns.md` rather than dispatch metadata level; no existing AI-tier or agentic-category agent has declared External Entity as a DFD target (only STRIDE-only precedent exists: `repudiation`, `spoofing`); architectural commitment that future AI-tier agents wishing to declare External Entity must update this ADR and document orchestrator-tier dispatch-rules External Entity inclusion pattern explicitly; deferred External Entity pattern available for future enrichment if/when a second AI-tier agent justifies the cost

**Modified components (additive edits only)**:

5. **Orchestrator Dispatch List** (`.claude/agents/tachi/orchestrator.md`)
   - **Edit 1**: Insert `- human-trust-exploitation` in the AI-tier dispatch block after `tool-abuse` (Agentic-tier ordering preserves established `agent-autonomy → tool-abuse → human-trust-exploitation`)
   - **Edit 2**: Update Agentic Threats row from `agent-autonomy, tool-abuse` → `agent-autonomy, tool-abuse, human-trust-exploitation` (DUO → TRIO per architect HIGH-3 fix)
   - **Edit 3**: Update sequential-mode text if it enumerates Agentic agents (architect verifies at Wave 1.0 whether current state uses generic "Agentic agents" phrasing or explicit list; if generic, edit 3 is a no-op confirming nothing to update)

6. **Dispatch Rules Agentic Trio** (`.claude/skills/tachi-orchestration/references/dispatch-rules.md`)
   - **Edit 4**: Extend the Agentic dispatch DUO (post-F-3 state: `agent-autonomy`, `tool-abuse`) to a TRIO by adding `human-trust-exploitation` as the 3rd agentic agent with FR-013-style activation rule (two-part gate — AI keyword AND human-user-facing emission indicator)
   - **Edit 5**: Update the table row for Agentic dispatch from `agent-autonomy, tool-abuse` → `agent-autonomy, tool-abuse, human-trust-exploitation` — identical TRIO update
   - **Edit 6**: Extend trigger-keyword rules section with `human-trust-exploitation` activation logic per FR-005 keyword list (with `persona` anti-indicator discipline per Q2 LOW-2)
   - **No External Entity declaration** in DFD element types per Q4 BLOCKING-1 fix — F-4 declares Process only

   **Wave 2.0 grep-checklist (architect MEDIUM-5)**: explicit verification that all 6 coordinated edits land cleanly. Verification artifact lands in PR description (or `.aod/results/wave-2.0-grep-checklist.md`) with a six-row checklist marking each edit ✓ landed.

7. **Shared Finding-Format Consumer List** (`.claude/skills/tachi-shared/references/finding-format-shared.md` — frontmatter `consumers:` list)
   - Insert `- human-trust-exploitation` between `tool-abuse` (current line 18) and `output-integrity` (current line 19) — tier-grouping placement (Agentic-category cluster) per FR-010
   - Architect adjudicates final position at Wave 1.0 per F-1 HIGH-2 / F-2 MEDIUM-1 architect-fix pattern
   - Body content byte-identical pre/post edit per ADR-023 Decision 3 (F-1 / F-2 precedents already validated this invariant)

8. **Finding Schema Regex** (`schemas/finding.yaml`)
   - Line 13: `schema_version: "1.7"` → `schema_version: "1.8"` (minor bump per ADR-026 Complex-Shape Clarifier extended by ADR-030 Decision 8 to regex-alternation prefix addition — F-4 is the **third recorded application** of Decision 8 after F-1 OI 1.5→1.6 and F-2 MI 1.6→1.7; F-3 was the first BLP-01 feature to ship without invoking this rule per ADR-032 D3 enrichment-branch path)
   - Line 18: `id.pattern: "^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI)-\\d+$"` → `"^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\\d+$"`
   - `examples:` list gains a `TE-1` entry **appended after the existing `MI-1` entry** (current MI-1 at line 28) to preserve chronological prefix-introduction ordering

### Data Flow

Given a DFD architecture description, the orchestrator dispatches the `human-trust-exploitation` agent when any Process component matches an AI-agent trigger keyword. The agent reads the companion `detection-patterns.md` via the single `**MANDATORY**: Read` directive, evaluates the **two-part emission gate** on each dispatched Process (AI-agent keyword match AND at least one human-user-facing emission indicator from the four FR-006 categories — outgoing Data Flow to human-named External Entity, Process description with human-user-facing keywords, sustained-engagement framing, authority-claim emission framing), and emits zero or more `TE-{N}` findings with populated `source_attribution` per applicable pattern category. Findings flow through orchestrator Phase 3 (MAESTRO assignment, agentic_pattern assignment), Phase 4 (referential validation against `schemas/taxonomy/*.yaml`), and Phase 5 (deduplication) identically to existing `AG-{N}` and `AGP-{N}` findings — no consumer-tier changes required. Report-tier rendering (`threat-report.md`, `threats.md`) groups `TE-{N}` findings in the `category: agentic` section alongside `AG-{N}` and `AGP-{N}` findings, preserving the **three-prefix-family discipline within agentic** (SC-014) without prose synthesis. FR-018 grep-checkable test verifies AGP-vs-TE prose-synthesis-prevention on the regenerated example (R11 mitigation).

### Tech Stack

- **Agent / skill files**: Markdown + YAML (ADR-023 lean-agent pattern)
- **Schema**: `schemas/finding.yaml` v1.8 post-edit (regex alternation extension, backward-compatible)
- **Taxonomy catalogs**: `schemas/taxonomy/{owasp,cwe}.yaml` (F-A1, unchanged) — consumed read-only for `source_attribution` validation
- **Orchestrator dispatch**: `.claude/agents/tachi/orchestrator.md` + `.claude/skills/tachi-orchestration/references/dispatch-rules.md` (additive edits — 6 coordinated edits with Wave 2.0 grep-checklist verification)
- **Parser**: `scripts/tachi_parsers.py` (unchanged — `validate_source_attribution` already accepts any ID prefix matching the regex post-bump)
- **Test harness**: pytest + `tests/scripts/test_backward_compatibility.py` (existing) + new `tests/scripts/test_human_trust_exploitation.py` + FR-018 grep test
- **Example regeneration pipeline**: `/tachi.threat-model` → `/tachi.risk-score` → `/tachi.compensating-controls` → `/tachi.infographic all` → `/tachi.security-report` (existing pipeline, unchanged)
- **Typst templates**: no edits — PDF renderer reads `threats.md` / `risk-scores.md` / `compensating-controls.md` and the coverage-attestation section auto-renders from `source_attribution` post-regeneration
- **ADR dual-commit**: standard Proposed → Accepted lifecycle via `gh pr` + squash merge (ADR-027/028/029/030/031/032 precedent)

## Phase 0: Research

**Status**: Populated by `/aod.spec` at [research.md](./research.md). Key grounding facts confirmed at PRD/spec/plan time (verified by research agent at /aod.plan):

- F-2 (`misinformation.md`) and F-1 (`output-integrity.md`) are the structural templates F-4 mirrors verbatim (5-section AI-tier pattern, ≤150 lines)
- `schemas/finding.yaml:13` schema_version = `"1.7"` post-F-2; line 18 `id.pattern` = `"^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI)-\\d+$"`; `TE` prefix absent (confirming FR-011 bump requirement)
- `schemas/finding.yaml:28` `MI-1` example present; `TE-1` will append after MI-1
- `schemas/finding.yaml:162` `agentic_pattern` enum carries `trust_exploitation` value (Feature 142, multi-agent topology pattern per `maestro-agentic-patterns-shared.md:220-231` R-04) — Naming Disambiguation discipline anchored here
- `schemas/taxonomy/owasp.yaml:318-322` carries ASI09 record with `name: Human-Agent Trust Exploitation`, `cwe_refs: []` (confirmed)
- `schemas/taxonomy/cwe.yaml:82,106,110,118` carries CWE-223 (Omission of Security-relevant Information), CWE-287 (Improper Authentication), CWE-290 (Authentication Bypass by Spoofing), CWE-345 (Insufficient Verification of Data Authenticity) (confirmed)
- `schemas/taxonomy/cwe.yaml`: CWE-451 CONFIRMED ABSENT → prose-only citation in pattern catalog, MUST NOT appear in `source_attribution` (R3 CLOSED at PRD time + plan time)
- `schemas/taxonomy/mitre-atlas.yaml:83-87` carries AML.T0060 (Publish Hallucinated Entities) — offensive use-case, prose-only in pattern catalog; ADR-033 documents the genuinely-sparse ATLAS coverage of agent-to-human-victim surface as intentional (architect MEDIUM-3 fix)
- `.claude/skills/tachi-orchestration/references/dispatch-rules.md:91-92` Agentic dispatch DUO post-F-3: `agent-autonomy`, `tool-abuse` — extends to TRIO with `human-trust-exploitation` per FR-008
- `.claude/skills/tachi-shared/references/finding-format-shared.md:6-21` consumers list current state; insertion point for `human-trust-exploitation` is between `tool-abuse` (line 18) and `output-integrity` (line 19) per FR-010 PM-leaning placement
- `.claude/agents/tachi/agent-autonomy.md:17` `owasp_references: [ASI-01, ASI-06, ASI-08, ASI-09, ASI-10, LLM06:2025, LLM10:2025]` — ASI-09 explicitly carried; F-4 sub-scope carve-up retains this attribution at autonomy axis without metadata edit
- ADR-033 does NOT yet exist (no forward-dependency conflict)
- F-1 regenerated `agentic-app` 2026-04-19; F-3 regenerated `agentic-app` 2026-04-26 with new AG-8 inter-agent-communication finding; current `agentic-app` carries `LLM-{N}` + `OI-{N}` + `AG-{N}` (1-8) findings; `agentic-app` selected as F-4 conditional fallback per Q5 (architect MEDIUM-4)
- `examples/consumer-agent-app/` does NOT exist — Q5 lean target requires fixture authoring at Wave 1.1 (tester) with conditional fallback at Wave 2.0 AM gate
- F-1 / F-2 NFR-6 safe-language framing precedent exists in `.claude/skills/tachi-misinformation/references/detection-patterns.md` (lines 70, 98, 127, 155 use "A hypothetical..." / "(fictional scenario; no real institution)") — F-4 inherits and extends with the 4 explicit safe-language patterns per architect Pre-Mortem fix R7

**Open research items resolved during /aod.project-plan** (see Open Questions section):
- Q1 (Pattern category count) — resolved at PRD time: **5 categories** (architect APPROVE per Q1 binding)
- Q2 (Trigger keyword count) — resolved at PRD time: **~22 keywords with `persona` anti-indicator discipline** (architect APPROVE 12 keywords baseline; spec FR-005 captures verbatim Q2 enumeration with architect license to refine at Wave 1.0 per architect MEDIUM-A residual concern)
- Q3 (Category enum) — resolved at PRD time: **`category: agentic`** (architect APPROVE — OWASP framework attribution decisive)
- Q4 (DFD targets) — resolved at PRD time: **Process only with indicator-level human-user filtering** (architect REVERSED to BLOCKING-1 fix from PM original lean Process+ExternalEntity)
- Q5 (Example regeneration target) — resolved at PRD time: **new `examples/consumer-agent-app/` with conditional fallback to `examples/agentic-app/` extension at Wave 2.0 AM gate** (architect APPROVE with MEDIUM-4 conditional fallback)
- Q6 (ADR-033 sequencing) — resolved at PRD time: **Day 1 Wave 1.1 Proposed** (architect APPROVE — F-1 / F-2 precedent)

## Phase 1: Design & Contracts

**Prerequisites**: research.md populated (Phase 0 complete)

### Finding IR Contract (`contracts/finding-contract.md`)

**Purpose**: Document the shape of `TE-{N}` findings emitted by the new agent, including `source_attribution` invariants and mitigation-text rules.

**Contract**:

```yaml
id: "TE-{N}"                          # monotonically increasing per run, TE prefix new in schema 1.8
category: "agentic"                   # existing enum value — unchanged
title: "{pattern_category}: {short_summary}" # e.g., "Undisclosed AI Authorship: customer-support chatbot lacks AI-generation disclosure banner"
severity: "low" | "medium" | "high" | "critical"  # OWASP 3×3 matrix via severity-bands-shared.md
component: "{DFD Process component name}"
description: "{2-4 sentence threat description distinguishing authorship-disclosure / authority-attestation / persuasion-manipulation / persona-boundary / synthetic-relationship}"
mitigation: "{AI-disclosure / confidence-calibration / refusal-pattern / persona-boundary / synthetic-relationship-safeguard mechanism}"
references:
  - "OWASP ASI09:2026"
  - "https://cwe.mitre.org/data/definitions/{CWE_NUMBER}.html"
source_attribution:
  - {taxonomy: "owasp", id: "ASI09", relationship: "primary"}   # REQUIRED on every TE-{N} finding
  - {taxonomy: "cwe", id: "CWE-{NUMBER}", relationship: "related"}  # per applicable pattern category (CWE-223, CWE-345, CWE-287, CWE-290)
maestro_layer: "L7"                   # assigned downstream by orchestrator Phase 1 (existing Feature 084) — agentic-tier default
agentic_pattern: "none" | "<existing enum value>"  # assigned downstream by orchestrator Phase 3.6 (Feature 142); MUST NOT be "trust_exploitation" (multi-agent topology) — that's a different scope
delta_status: null                    # assigned downstream if baseline present (existing Feature 104)
```

**Invariants**:
- Every `TE-{N}` finding MUST pass `validate_source_attribution()` at orchestrator Phase 4
- The `source_attribution` array MUST contain at minimum `{taxonomy: owasp, id: ASI09, relationship: primary}`
- CWE entries MUST use IDs present in `schemas/taxonomy/cwe.yaml`: CWE-223 (undisclosed AI authorship + synthetic-relationship), CWE-345 (authority-claim + persuasive-tone), CWE-287 (persona-boundary), CWE-290 (persona-boundary + synthetic-relationship)
- CWE-451 MUST NOT appear in `source_attribution` (confirmed absent from catalog)
- MITRE ATLAS entries MUST NOT appear in `source_attribution` (no direct trust-exploitation match)
- External regulatory references (FTC/FDA/ABA/SEC/SB-1001/AARP) MUST NOT appear in `source_attribution` (not framework-anchored)
- The `mitigation` field MUST name at least one specific AI-disclosure / confidence-calibration / refusal-pattern / persona-boundary / synthetic-relationship-safeguard mechanism (not generic "disclose AI authorship")
- The `id` MUST match schema 1.8 `id.pattern` regex
- The agent MUST enforce the two-part emission gate (FR-013): finding emission requires BOTH AI-agent keyword match AND human-user-facing emission indicator
- The `agentic_pattern` field, when assigned by orchestrator Phase 3.6, MUST NOT take the value `trust_exploitation` (that's the agent-to-agent multi-agent topology pattern from Feature 142, not the agent-to-human communication-axis pattern from F-4) — Naming Disambiguation discipline (R11 mitigation)
- Vulnerable-population findings (category 5) MUST cite consumer-protection rationale in description prose AND MUST recommend escalation-to-human path as a baseline mitigation (NFR-006)

### Data Model (`data-model.md`)

**Purpose**: Document the agent metadata YAML shape + pattern category structure + companion skill README shape + Human-User-Facing Emission Indicators shape.

See [data-model.md](./data-model.md) for full entity definitions. Key entities:
- **Agent metadata YAML** (`category: agentic`, `threat_class: ASI`, `dfd_targets: [Process]`, etc.)
- **Pattern category** (name, primary/related taxonomy, indicators 3-6 bullets, worked example with NFR-006 patterns, mitigations)
- **Human-User-Facing Emission Indicator** (4 categories: outgoing Data Flow target, Process description keywords, sustained-engagement framing, authority-claim emission framing)
- **Trigger keyword + anti-indicator pair** (the dispatch keyword + the negation condition that suppresses emission)

### Quickstart (`quickstart.md`)

**Purpose**: Step-by-step verification walkthrough — given the regenerated `examples/consumer-agent-app/` (or `examples/agentic-app/` extension per Q5 fallback), confirm ≥1 `TE-{N}` finding with valid source_attribution, valid mitigation text, passing referential validation, and FR-018 grep-test passing on AGP-vs-TE prose-synthesis-prevention.

See [quickstart.md](./quickstart.md) for the verification procedure.

### Agent Context Update

Run `.aod/scripts/bash/update-agent-context.sh claude` after plan approval to refresh `CLAUDE.md` / agent-specific context with the Feature 224 entry.

## Implementation Approach (Phased Waves)

Calendar-verified against `cal 4 2026`: 2026-04-26 Sun (today; PRD/plan authored), 2026-04-27 Mon (Day 1), 2026-04-28 Tue (Day 2), 2026-04-29 Wed (Buffer), 2026-04-30 Thu (post-buffer slack).

### Wave 1 — Day 1 AM (Monday 2026-04-27, ~0.4d)

**Gate-critical, front-loaded to unblock parallel Day 1 PM authoring.**

- **Wave 1.0 (30-60 min)**: Architect verifies Heuristic A signal-class intact (ADR-030 Decision 2 Outcome B + ADR-033 sub-scope carve-up still govern). Architect adjudicates final FR-005 trigger keyword count (architect MEDIUM-A residual concern) and FR-010 finding-format-shared.md placement. If a subsume-into-`agent-autonomy` signal surfaces, escalate per spec R1 Day 1 gate before Wave 1.1.
- **Wave 1.1 (parallel)**:
  - **Schema-lock commit**: `schemas/finding.yaml` regex bump 1.7 → 1.8; `id.pattern` includes `TE` prefix; `examples:` list gains `TE-1` entry after `MI-1`. Unit test `test_human_trust_exploitation.py::test_regex_matches_te_prefix`.
  - **ADR-033 Proposed commit**: ADR body with all 10 items including Heuristic A four-way scope resolution + ASI09 sub-scope carve-up (HIGH-2), Naming Disambiguation § (HIGH-1 addition), DFD Target Decision § (BLOCKING-1 addition), lean-agent shape conformance, cross-references to ADR-021/023/026/027/028/029/030 (Decision 2 Outcome B + Decision 8 third application callouts), 26-file zero-edit invariant with `agent-autonomy.md` NOT-edit explicit, Revision History table.
  - **Agent file skeleton**: `.claude/agents/tachi/human-trust-exploitation.md` 5-section scaffold with metadata YAML, Purpose section stub, Skill References table.
  - **Tester fixture authoring**: `tests/scripts/fixtures/human_trust_exploitation/valid_te_finding.yaml` + `invalid_attribution_finding.yaml`. Tester begins authoring `examples/consumer-agent-app/architecture.md` (Q5 lean target) — chatbot / mental-health-companion / eldercare-coach archetype.
  - **PR-creation discipline (R12 mitigation)**: Draft PR already opened with title `feat(224): human-trust-exploitation threat agent (ASI09)` per `.claude/rules/git-workflow.md`; verify title pre-commit at any rebase.
- **Escalation gate**: If Wave 1.0 Heuristic A verification surfaces a subsume-into-agent-autonomy signal, halt Wave 1.1 ADR work until architect + team-lead ruling recorded.

### Wave 2 — Day 1 PM (Monday 2026-04-27, ~0.5d, **stretched 3-4h per team-lead MEDIUM-1**)

**Pattern catalog authoring + Skill References + agent body.**

- `.claude/skills/tachi-human-trust-exploitation/references/detection-patterns.md`: 5 pattern categories with indicators, worked examples enforced verbatim with **NFR-006 four safe-language patterns** (Hypothetical: prefix; "for context, not legal interpretation" framing; non-clinical distress framing; no real institutional/clinician/lawyer/advisor/product names), primary-source citations, trigger keywords, applicable DFD element types. Anti-indicator discipline per architect Q2 LOW-2 (`persona` anti-indicator subsection). 4-category Human-User-Facing Emission Indicators subsection per FR-006.
- `.claude/skills/tachi-human-trust-exploitation/README.md`: companion README (mirror `tachi-misinformation/README.md`).
- `.claude/agents/tachi/human-trust-exploitation.md`: fill out `## Purpose` (four-way scope boundary + ASI09 sub-scope carve-up prose per FR-002 — distinct-from-output-integrity + distinct-from-misinformation + distinct-from-agent-autonomy-autonomy-axis + scoped-to-human-victim-communication-axis; cite ADR-030 D2 Outcome B + ADR-033 §"ASI09 Sub-Scope Carve-Up"), `## Detection Workflow` with single `**MANDATORY**: Read` and explicit two-part emission gate step (FR-013), optional `## Example Findings` (2-3 worked examples across pattern categories with NFR-006 framing).
- **NFR-007 self-disclosure discipline applied**: pattern-catalog prose + agent prose use neutral mitigation language ("Implement X" / "Configure Y") without persuasive language; the catalog itself is the negative-space example.
- **Structural validation**: `wc -l ≤ 150`, `grep -c '\*\*MANDATORY\*\*: Read' = 1`, `grep -i maestro` returns empty on both agent file AND companion `detection-patterns.md`.
- **Wave 1.3 PM EOD checkpoint** (R6 mitigation): Architect reviews the Human-User-Facing Emission Indicators subsection in `detection-patterns.md` (Process-only-with-indicator-filter is a first-execution pattern for AI-tier agents); architect Day-1-EOD pre-positioning checklist for Wave 2.0 (per team-lead LOW-1) — the four explicit edits to `schemas/finding.yaml`, `finding-format-shared.md`, `orchestrator.md`, `dispatch-rules.md` are pre-staged.

### Wave 3 — Day 2 AM (Tuesday 2026-04-28, ~0.3d) — **Wave 2.0 in PRD timing**

**R10 enforceable trigger + Q5 fallback gate + orchestrator registration + shared reference additive edits.**

- **Step 0 (R10 enforceable trigger per team-lead HIGH-1 fix)**: team-lead runs `gh issue list --label stage:plan --state open --search "F-5"` AND `gh pr list --state open --search "schemas/finding.yaml"` (etc.) on the 4 surface files. If any non-empty, HALT and escalate. Otherwise proceed.
- **Step 1 (Q5 fallback gate per architect MEDIUM-4)**: assess fixture authoring progress on `examples/consumer-agent-app/`. If on track → continue with Q5 lean. If foreseeable slip (architecture authoring exceeds 1 day OR test-harness friction surfaces) → switch FR-015 to fallback (a) `examples/agentic-app/` extension; document decision in PR description with the trigger that fired the gate.
- **Step 2 (architect lands Day-1-EOD checklist)**:
  - `.claude/agents/tachi/orchestrator.md`: insert `- human-trust-exploitation` in Agentic-tier dispatch list (Edit 1); update Agentic Threats row DUO → TRIO (Edit 2); update sequential-mode text if applicable (Edit 3, may be no-op). Edit owner: architect (mirrors F-1 HIGH-1 / F-2 MEDIUM-4 resolution).
  - `.claude/skills/tachi-orchestration/references/dispatch-rules.md`: extend Agentic DUO → TRIO at lines 91-92 (Edit 4); add human-trust-exploitation activation rule (two-part gate per FR-013) (Edit 4 cont'd); update table row DUO → TRIO (Edit 5); extend trigger-keyword rules section with FR-005 keyword set including `persona` anti-indicator (Edit 6).
  - `.claude/skills/tachi-shared/references/finding-format-shared.md`: add `- human-trust-exploitation` between `tool-abuse` (line 18) and `output-integrity` (line 19) in `consumers:` list per FR-010.
  - Senior-backend-engineer runs schema parser round-trip test post-bump (`pyyaml.safe_load(open('schemas/finding.yaml'))` succeeds + regex matches `TE-1`).
- **Step 3 (Wave 2.0 grep-checklist per architect MEDIUM-5 / FR-009)**: explicit verification of all 6 coordinated edits across `orchestrator.md` (3 edits) and `dispatch-rules.md` (3 edits). Verification artifact lands in PR description with a six-row checklist marking each edit ✓ landed.
- **Structural-diff validation**: `## ` headings in `finding-format-shared.md` byte-identical pre/post edit; grep-check confirms TRIO is consistent across `orchestrator.md` Agentic Threats row + `dispatch-rules.md` Agentic dispatch list + `dispatch-rules.md` table row.

### Wave 4 — Day 2 AM (Tuesday 2026-04-28, ~0.2d) — **Wave 2.1 in PRD timing**

**False-positive check on non-consumer-facing baselines (R6 mitigation per FR-017).**

- Run dispatch dry-run grep against `examples/web-app/architecture.md` and `examples/microservices/architecture.md` for the FR-005 trigger keyword set; verify zero AI-agent-keyword matches with adjacent human-user-facing emission indicators (because these baselines have no consumer-facing AI Processes); confirm zero `TE-{N}` findings would emit per the two-part emission gate FR-013.
- **Critical sequencing**: Wave 4 MUST complete and pass BEFORE Wave 5 regen runs. If false positives surface, halt and tighten the emission gate (FR-013) before proceeding to FR-015 regeneration.

### Wave 5 — Day 2 PM (Tuesday 2026-04-28, ~0.4d) — **Wave 2.2 in PRD timing**

**Example regeneration + backward-compat verification.**

- Run `/tachi.threat-model examples/{consumer-agent-app|agentic-app}/architecture.md` (per Q5 decision at Wave 3 Step 1) to confirm dispatch emits `TE-{N}` findings.
- Run full downstream pipeline (`/tachi.risk-score`, `/tachi.compensating-controls`, `/tachi.infographic all`, `/tachi.security-report`).
- Commit regenerated artifacts: `threats.md`, `threats.sarif`, `risk-scores.md`, `risk-scores.sarif`, `compensating-controls.md`, `compensating-controls.sarif`, `threat-report.md`, `attack-trees/`, `attack-chains.md`, 6 infographic JPEGs, `security-report.pdf`, `security-report.pdf.baseline`.
- Verify ≥1 `TE-{N}` finding present (SC-004); verify F-A2 referential validation passes (`validate_source_attribution` returns no errors) (SC-010); verify three-prefix-family discipline within agentic (`AG-{N}`, `AGP-{N}` if applicable, `TE-{N}` adjacent in `category: agentic` section without prose synthesis) (SC-014); run FR-018 grep-checkable test for AGP-vs-TE prose-synthesis-prevention (SC-012 — R11 mitigation).
- Run `tests/scripts/test_backward_compatibility.py` — 5 non-consumer-facing baselines MUST be byte-identical under `SOURCE_DATE_EPOCH=1700000000` (SC-006).
- If Q5 fallback to `examples/agentic-app/` triggered: `agentic-app` regenerates additively (new `TE-{N}` findings on top of existing `LLM-{N}` + `OI-{N}` + `AG-{N}` (1-8) + `AGP-{N}` findings); diff is expected non-empty; verify the new findings render in the right sections without prose synthesis.

### Wave 6 — Day 2 PM (Tuesday 2026-04-28, ~0.3d) — **Wave 2.3 in PRD timing**

**Code review + ADR-033 Accepted transition + PR ready.**

- Senior-backend-engineer + code-reviewer double-check pattern catalog worked examples for **NFR-006 compliance** (4 explicit safe-language patterns: Hypothetical: prefix; "for context, not legal interpretation" framing; non-clinical distress framing; no real institutional/clinician/lawyer/advisor/product names) — **R7 mitigation**. Code-reviewer also verifies **NFR-007 self-disclosure discipline** (no persuasive language in agent-authored prose).
- Transition ADR-033 Proposed → Accepted with provisional merge-date.
- Run full pytest suite; grep audit on 26-file zero-edit invariant (13 threat agents + 13 companion `detection-patterns.md` files; **including `agent-autonomy.md` NOT-edit verification**); validate SC-001 through SC-015.
- **Pre-merge PR-title verification (R12 mitigation per team-lead HIGH-2 / FR-019)**: re-verify PR title is Conventional-Commit-formatted (`feat(224): ...`) before merge; if non-conventional title slipped, retitle via `gh pr edit <PR> --title "feat(224): ..."`.
- Triple-review + merge (squash commit).
- **Post-merge release-please verification (R12 mitigation)**: after squash-merge, verify a release-please PR opened within ~30s via `gh pr list --state open --search "release-please" --limit 3`. If empty, push empty `feat(224):` marker commit on main.
- **Post-merge SHA fill** on ADR-033 Revision History (deferred to buffer day per team-lead LOW-2 prioritization).

### Wave 7 — Day 3 BUFFER (Wednesday 2026-04-29) — **Buffer day in PRD timing**

**Delivery retrospective + post-merge follow-through + contingent buffer-day work — prioritization per team-lead LOW-2.**

- **First call**: any in-flight contingency from R2/R6/R7 takes priority.
- **Second call**: delivery retrospective (DEFAULT-SLOTTED HERE per team-lead MEDIUM-3 — same-day in Wave 6 only with explicit team-lead opt-in; default is buffer-day). Authors `.aod/delivery.md` (or `specs/224-trust-exploitation-threat-agent/delivery.md` post-deliver-stage move) following F-2 / F-3 retrospective template.
- **Third call**: post-merge SHA fill on ADR-033 + `/aod.deliver` execution + release-please PR verification (push empty `feat(224):` marker if release-please skips per F-212 / R12).
- **Fourth call**: F-5 PRD drafting NOT until F-4 deliver-stage closes (Constraint Analysis on R10).
- **BLP-01 Coverage Matrix update** (SC-011): ASI09:2026 communication axis transitions Planned → Covered with F-4 (Feature 224) named as closure feature; autonomy axis remains attributed to `agent-autonomy`. Post-merge documentation commit to `_internal/strategy/BLP-01-threat-coverage.md`.

## Touch Points Summary

| File | Change | Lines | Scope |
|------|--------|-------|-------|
| `.claude/agents/tachi/human-trust-exploitation.md` | NEW | ~100-150 | Agent file (≤150 line cap, ≤180 hard ceiling) |
| `.claude/skills/tachi-human-trust-exploitation/README.md` | NEW | ~30-50 | Skill README |
| `.claude/skills/tachi-human-trust-exploitation/references/detection-patterns.md` | NEW | ~250-350 | Pattern catalog (5 categories with NFR-006 patterns) |
| `.claude/agents/tachi/orchestrator.md` | MODIFY (3 edits — Edit 1 dispatch list + Edit 2 Agentic Threats row + Edit 3 sequential-mode text if applicable) | 3 edits | Dispatch list + DUO → TRIO |
| `.claude/skills/tachi-orchestration/references/dispatch-rules.md` | MODIFY (3 edits — Edit 4 Agentic dispatch list + Edit 5 table row + Edit 6 trigger-keyword rules) | 3 edits | Agentic DUO → TRIO + activation rule + trigger keywords |
| `.claude/skills/tachi-shared/references/finding-format-shared.md` | MODIFY (add 1 line) | ~1 | Consumer list |
| `schemas/finding.yaml` | MODIFY (3 lines: version + regex + examples TE-1 entry) | ~13, ~18, ~28 | Schema bump 1.7 → 1.8 |
| `docs/architecture/02_ADRs/ADR-033-human-trust-exploitation-agent.md` | NEW | ~300-400 | Public ADR (10 body items) |
| `tests/scripts/test_human_trust_exploitation.py` | NEW | ~100-150 | Regex + source_attribution + FR-018 grep tests |
| `tests/scripts/fixtures/human_trust_exploitation/*.yaml` | NEW | ~20-30 each | Test fixtures |
| `examples/consumer-agent-app/*` (Q5 lean) OR `examples/agentic-app/*` (Q5 fallback) | NEW or REGENERATE | — | Pipeline artifacts + PDF baseline |
| `.claude/agents/tachi/{13 existing}.md` + `.claude/skills/tachi-{13 existing}/references/detection-patterns.md` | ZERO CHANGES | — | 26-file invariant **including `agent-autonomy.md`** |
| `.claude/agents/tachi/{risk-scorer,control-analyzer,threat-report,threat-infographic,report-assembler,attack-tree-delta}.md` | ZERO CHANGES | — | Infrastructure-tier invariant (FR-014) |
| `scripts/*.py` | ZERO CHANGES | — | Parser + orchestrator scripts |
| `templates/tachi/*` | ZERO CHANGES | — | Typst templates |
| `requirements*.txt`, `pyproject.toml`, `package.json` | ZERO CHANGES | — | No new dependencies (SC-008) |

## Risks & Mitigations

See spec.md Edge Cases + PRD §Risks & Mitigations for the full list. Plan-phase active risks:

- **R1 (Heuristic A signal-class re-adjudication)** — Mitigation: Wave 1.0 architect verification; escalation gate before Wave 1.1 ADR commit if subsume signal surfaces. Status: LOW likelihood per ADR-030 Decision 2 Outcome B + ADR-033 sub-scope carve-up.
- **R2 (Regeneration friction on chosen example baseline)** — Mitigation: Q5 fallback gate at Wave 3 Step 1 (architect MEDIUM-4); buffer-day reserved per team-lead LOW-2; explicit decision artifact in PR description.
- **R3 (CWE-451 absent from `cwe.yaml`)** — CLOSED at PRD time + plan time; pattern-catalog prose retains CWE-451 citation; `source_attribution` anchors on ASI09 + CWE-223 + CWE-287 + CWE-290 + CWE-345.
- **R4 (MITRE ATLAS sparseness)** — Mitigation: ADR-033 documents intentional sparseness; ATLAS attribution prose-only.
- **R5 (Schema bump 1.7 → 1.8 collision with concurrent F-5 build)** — Mitigation: F-4 ships solo verified at PRD + plan time; R10 enforceable trigger at Wave 3 Step 0.
- **R6 (Process-only with indicator-level filter first-execution risk)** — Mitigation: Wave 1.3 PM EOD architect review of Human-User-Facing Emission Indicators subsection; Wave 4 false-positive check on `web-app` and `microservices` baselines (FR-017) — must yield zero TE findings before proceeding to Wave 5 regen.
- **R7 (Vulnerable-population worked-example prose-quality risk)** — Mitigation: NFR-006 four safe-language patterns enforced verbatim; Wave 6 senior-backend-engineer + code-reviewer double-check.
- **R8 (Orchestrator dispatch-rules + orchestrator coordinated-edit surface — 6 edits across 2 files)** — Mitigation: FR-009 Wave 2.0 grep-checklist explicitly verifies all 6 coordinated edits land cleanly; recoverable (additive-only).
- **R9 (Finding-format-shared consumer list placement drift)** — Mitigation: FR-010 specifies placement (after `tool-abuse`, before `output-integrity`); architect adjudicates final placement at Wave 1.0.
- **R10 (F-5 concurrent build 4-surface conflict)** — Mitigation: R10 enforceable trigger at Wave 3 Step 0 — `gh issue list` + `gh pr list` queries on 4 surface files; non-empty result HALTs Wave 3 and escalates to team-lead.
- **R11 (Naming-collision residual risk)** — Mitigation: ADR-033 §"Naming Disambiguation" (FR-012 body item 9) + FR-018 grep-checkable test verifies no prose synthesis between `AGP-{N}` (multi-agent topology) and `TE-{N}` (human-trust communication axis) findings at threat-report rendering; SC-012 verifies test passes on regenerated example.
- **R12 (PR-title release-please incident per F-212 prevention)** — Mitigation: two-step belt-and-suspenders enforcement per `.claude/rules/git-workflow.md` — (1) Wave 1.1 PR-creation already applied at branch-creation step with `feat(224):` prefix; (2) Wave 6 pre-merge re-verification AND post-merge release-please PR verification (push empty `feat(224):` marker if needed).

## Open Questions (PRD Q-set — Architect Decisions, all Resolved at PRD time)

Architect-owned per PRD §Architecture & Design Decisions. All Q1-Q6 resolved at PRD review time per architect-binding sign-off. Re-listed here for plan-time traceability.

| # | Question | Architect Decision | Justification | Codified In |
|---|---|---|---|---|
| Q1 | Pattern category count — 5 or 6+? | **5 categories** (APPROVE) | F-1 / F-2 5-category floor validated; vulnerable-population fits in category 5 sub-axis (`Synthetic-Relationship Exploitation` with vulnerable-population safeguards layer); cross-channel deferred to F-7 Mobile bundle. | `detection-patterns.md` 5 numbered categories per FR-004; ADR-033 decision record |
| Q2 | Trigger keyword count + `persona` anti-indicator? | **~22 keywords with `persona` / `personality` / `character agent` anti-indicator subsection** (architect APPROVE 12 baseline; spec FR-005 captures verbatim Q2 enumeration; final count tightened or expanded at architect Wave 1.0 review per architect MEDIUM-A residual concern) | Covers consumer-facing AI vocabulary (`chatbot`, `assistant`, `advisor`, `customer-facing`, `companion`, `coach`, `tutor`) plus high-stakes domain signals (`mental health`, `eldercare`, `clinical decision support`, `legal advisor`, `financial advisor`) plus dual-use keywords (`persona`, `personality`, `character agent`) with explicit anti-indicator. | `detection-patterns.md` `## Detection Scope` Trigger Keywords subsection with persona anti-indicator; `dispatch-rules.md` trigger-keyword rules |
| Q3 | Category enum — `agentic` or `llm`? | **`category: agentic`** (APPROVE) | OWASP framework attribution decisive — ASI09 is in OWASP Agentic Top 10. Aligns with `agent-autonomy` and `tool-abuse` precedent. | Agent metadata `category: agentic`; FR-001 |
| Q4 | DFD target set — Process only, or Process + External Entity? | **Process only with indicator-level human-user filtering** (REVERSED to BLOCKING-1 fix; original PM lean was Process+ExternalEntity) | No AI-tier or agentic-category agent declares External Entity; only STRIDE-only precedents exist. F-4 mirrors F-1 / F-2 single-DFD-target pattern. Capture human-user trust boundary at indicator level within `detection-patterns.md`. ADR-033 body item 10 documents the DFD Target Decision and reserves future External Entity declaration for a subsequent enrichment if/when a second AI-tier agent justifies the pattern. | Agent metadata `dfd_targets: [Process]`; `detection-patterns.md` `### Human-User-Facing Emission Indicators` subsection per FR-006; ADR-033 body item 10 |
| Q5 | Example regeneration target — new `consumer-agent-app` or extend `agentic-app`? | **New `examples/consumer-agent-app/`** with conditional fallback to `examples/agentic-app/` extension at Wave 3 Step 1 AM gate (architect MEDIUM-4) | Cumulative-complexity argument is sound; 0.5-1 day delta absorbed by buffer; explicit fallback gate documented. Team-lead capacity-budget visibility (MEDIUM-2): candidate (b) consumes ~50% of buffer day BEFORE any contingency triggers — Wave 3 Step 1 AM gate is the explicit decision point. | `examples/consumer-agent-app/` (Q5 lean) OR `examples/agentic-app/` extension (fallback); decision artifact in PR description per FR-015 |
| Q6 | ADR-033 sequencing — Day 1 Wave 1.1 Proposed or Day 2 AM? | **Day 1 Wave 1.1 Proposed** (APPROVE) | F-1 / F-2 precedent; no re-adjudication signal. Proposed → Accepted dual-commit unblocks parallel pattern-catalog authoring downstream of Heuristic A signal-class verification. Day 2 Wave 6 Accepted transition mirrors ADR-030 / ADR-031 / ADR-032 provisional-merge-date pattern; post-merge SHA fill records squash commit (deferred to buffer day per team-lead LOW-2). | ADR-033 Proposed commit at Wave 1.1; Accepted transition at Wave 6 |

## Success Criteria Mapping

| Spec SC | Implementation Phase | Deliverable |
|---|---|---|
| SC-001 | Wave 2 | `human-trust-exploitation.md` ≤150 lines, 1 MANDATORY Read, 0 MAESTRO; verified `wc -l` + `grep -c` |
| SC-002 | Wave 2 | `detection-patterns.md` ≥5 categories with worked examples (NFR-006 patterns), citations, triggers, DFD types, anti-indicators |
| SC-003 | Wave 3 | `finding-format-shared.md` edit + structural-diff validation (`## ` headings byte-identical pre/post edit) |
| SC-004 | Wave 5 | Regenerated example emits ≥1 `TE-{N}` finding with valid `source_attribution`; non-qualifying baselines emit 0 (two-part emission gate FR-013 enforces) |
| SC-005 | Wave 1.1 + Wave 6 | ADR-033 Proposed at Wave 1.1; Accepted at Wave 6 with all 10 required body items (incl. Naming Disambiguation + DFD Target Decision) |
| SC-006 | Wave 5 | `test_backward_compatibility.py` passes on 5 non-consumer-facing baselines under SOURCE_DATE_EPOCH=1700000000; SHA-256 comparison against post-F-3 baselines |
| SC-007 | Wave 5 | Regenerated example produces TE-{N} finding(s) with disclosure / persuasion-safeguard / persona-boundary mitigations + ASI09 citation |
| SC-008 | All waves | Empty diff on dependency manifest files (verified at PR pre-merge) |
| SC-009 | All waves | Grep audit at PR pre-merge confirms zero edits to 26 detection-tier files (22 original + F-1's 2 + F-2's 2; F-3 reconciled) **INCLUDING `agent-autonomy.md` NOT-edit** |
| SC-010 | Wave 5 + Wave 6 | `validate_source_attribution` returns no errors on regenerated findings; fixture tests confirm CWE-451/ATLAS/regulatory-references prose-only |
| SC-011 | Wave 7 | BLP-01 Coverage Matrix updated: ASI09:2026 communication axis Planned → Covered with F-4 named as closure feature; autonomy axis remains `agent-autonomy` |
| SC-012 | Wave 5 | FR-018 grep-checkable test passes — `AGP-` and `TE-` prefixes in distinct prose blocks on regenerated `threat-report.md` (R11 mitigation) |
| SC-013 | Wave 1.1 + Wave 6 | PR title `feat(224): ...` Conventional-Commit-formatted at draft creation (already applied) + pre-merge re-verification + post-merge release-please verification (R12 mitigation) |
| SC-014 | Wave 5 | Three-prefix-family discipline verified within agentic: AG-{N}, AGP-{N} (if applicable), TE-{N} adjacent in `category: agentic` section without prose synthesis |
| SC-015 | Wave 3 | FR-009 Wave 2.0 grep-checklist verifies all 6 coordinated edits across `orchestrator.md` (3) + `dispatch-rules.md` (3); verification artifact in PR description |

## PR Pre-Merge Checklist

- [ ] All Wave 2-6 structural validations green (line count, MANDATORY count, MAESTRO grep)
- [ ] **26-file zero-edit grep audit** returns empty for 13 threat agents + 13 companion `detection-patterns.md` files **INCLUDING `agent-autonomy.md` NOT-edit verification** (SC-009)
- [ ] Infrastructure-tier consumer files (risk-scorer, control-analyzer, threat-report, threat-infographic, report-assembler, attack-tree-delta) show zero diff (FR-014)
- [ ] `test_backward_compatibility.py` passes on 5 non-consumer-facing baselines (SC-006)
- [ ] `test_human_trust_exploitation.py` passes (regex + source_attribution fixtures + FR-018 grep test)
- [ ] Regenerated example commits present including `security-report.pdf.baseline` (SC-007)
- [ ] ADR-033 transitioned Proposed → Accepted with Revision History entry; **all 10 body items present** including Naming Disambiguation (HIGH-1) + DFD Target Decision (BLOCKING-1) (SC-005)
- [ ] Dependency manifest diff is empty (pyproject.toml, requirements*.txt, package.json) (SC-008)
- [ ] `schemas/finding.yaml` schema_version = "1.8" + `id.pattern` extended to include `TE`; examples entry for `TE-1` appended after `MI-1`
- [ ] `consumers:` list on finding-format-shared.md: `human-trust-exploitation` inserted between `tool-abuse` and `output-integrity` (SC-003)
- [ ] **Wave 2.0 grep-checklist artifact** in PR description with all 6 coordinated edits ✓ landed (SC-015)
- [ ] Three-prefix-family discipline verified on regenerated example (AG-{N}, AGP-{N}, TE-{N} adjacent in `category: agentic` section without prose synthesis) (SC-014)
- [ ] **FR-018 grep test passes** on regenerated `threat-report.md` confirming AGP-vs-TE prose-synthesis-prevention (SC-012 — R11 mitigation)
- [ ] **NFR-006 compliance verified**: all 5 worked examples carry "Hypothetical:" prefix + "for context, not legal interpretation" framing + non-clinical distress framing + no real institutional/clinician/lawyer/advisor/product names (R7 mitigation)
- [ ] **NFR-007 compliance verified**: agent-authored prose models neutral mitigation language without persuasive framing
- [ ] **PR title verified Conventional-Commit-formatted**: `feat(224): ...` pre-merge re-verification + post-merge release-please PR existence (R12 mitigation per FR-019 / SC-013)
- [ ] Triple sign-off in tasks.md frontmatter (PM + Architect + Team-Lead) — enforced in `/aod.tasks`

## References

- PRD: [224-trust-exploitation-threat-agent-2026-04-26.md](../docs/product/02_PRD/224-trust-exploitation-threat-agent-2026-04-26.md)
- Spec: [spec.md](./spec.md)
- Research: [research.md](./research.md)
- Feature 082 precedent (lean-agent refactor + 22-file zero-edit baseline): `specs/082-threat-agent-skill/`
- Feature 142 precedent (orchestrator-tier additive edits + `trust_exploitation` agentic_pattern enum): `specs/142-maestro-phase-2/`
- Feature 201 F-1 precedent (first standalone-branch new AI-tier agent under ADR-023): `specs/201-output-integrity-threat-agent/`
- Feature 206 F-2 precedent (second standalone-branch new AI-tier agent under ADR-023): `specs/206-misinformation-threat-agent/`
- Feature 219 F-3 precedent (enrichment-branch alternative — explicit contrast in ADR-033 body item 3): `specs/219-asi07-tool-abuse-enrichment/`
- ADR-021 (SOURCE_DATE_EPOCH determinism): `docs/architecture/02_ADRs/ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md`
- ADR-023 (Lean-agent detection variant): `docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md`
- ADR-026 (Pattern Classification Mechanism + minor-bump rule): `docs/architecture/02_ADRs/ADR-026-pattern-classification-mechanism.md`
- ADR-027 (Taxonomy crosswalk schema): `docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md`
- ADR-028 (Source attribution schema extension): `docs/architecture/02_ADRs/ADR-028-source-attribution-schema-extension.md`
- ADR-029 (Coverage attestation report section): `docs/architecture/02_ADRs/ADR-029-coverage-attestation-report-section.md`
- ADR-030 (F-1 output-integrity agent — **Decision 2 Outcome B reservation creates F-4's scope**; **Decision 8 regex-alternation minor-bump rule invoked third time on `TE` prefix**): `docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md`
- ADR-031 (F-2 misinformation agent — second-execution standalone-branch precedent; structural template): `docs/architecture/02_ADRs/ADR-031-misinformation-agent.md`
- ADR-032 (F-3 ASI07 tool-abuse enrichment — enrichment-branch alternative; F-4 explicitly contrasts in ADR-033 body item 3): `docs/architecture/02_ADRs/ADR-032-asi07-tool-abuse-enrichment.md`
- ADR-033 (this feature — to be authored at FR-012)
