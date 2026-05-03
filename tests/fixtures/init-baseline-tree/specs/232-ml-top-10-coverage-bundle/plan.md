---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-27
    status: APPROVED
    notes: "Plan faithfully translates spec's 26 FRs and 26 SCs into 18 sequential waves with explicit ownership + buffer day reserved. All 3 P0 user stories operationalized: US-1 via Wave 1.1+2.x+3.x edits + Wave 4.0 predictive-ml-app regen; US-2 via Wave 1.0 ADR-035 Proposed + 22-file zero-edit invariant verification at Wave 5.0 + Pattern Category Disambiguation per FR-011 (architect MEDIUM-3 absorbed in ADR-035 D-9); US-3 via Wave 4.1+5.0 byte-identity verification + Wave 0.0 predictive-ml-app authoring (Q1 RESOLVED). All architect-deferred MEDIUM-3/4/5 absorbed into ADR-035 D-numbered decisions (D-9/D-4/D-5). All team-lead-deferred MEDIUMs absorbed: MEDIUM-1 (R5 deferral pair) at spec OoS-15 + Wave 5.6 buffer; MEDIUM-2 (Day 1 PM checkpoints) at Waves 2.1/2.2/2.3; MEDIUM-3 (Day 2 PM tester) at FR-025 + Wave 4.1; LOW-1 (Day 3 AM split) at Waves 5.0/5.1. Q-numbering plan-day RESOLVED: Q1 (predictive-ml-app default), Q2 (2 rows ML06), Q3 (3/6 ATLAS catalog-resolvable), Q4 (single Cat 10 D), Q6 (severity-hint column). Wed-Fri 3-day envelope + Mon buffer feasible. 0 BLOCKING / 0 HIGH / 2 MEDIUM (advisory) / 4 LOW (style). PM APPROVES for /aod.tasks. Full review: .aod/results/product-manager-plan-232.md."
  architect_signoff:
    agent: architect
    date: 2026-04-27
    status: APPROVED
    notes: "Plan technically sound and dependency-satisfied. Heuristic A protocol compliance FULL at three-agent scope (third execution after F-3 single + F-5 two; symmetric ADR-023 D3 conformance). All 6 baselines verified: tampering.md=51, data-poisoning.md=78, model-theft.md=97 (post-F-5), companions=190/137/211 — all match plan claims; tier-cap margins ≥42 lines on tightest case (model-theft.md). Schema invariant verified: finding.yaml v1.8, id.pattern regex unchanged (T+D+LLM already enumerated; F-6 third no-schema-bump enrichment after F-3+F-5; first at three-agent scope per ADR-034 lines 192-204 forecast). Catalog-resolvability verified: ML01-ML10 (10 entries) catalog-resolvable; AML.T0018+T0020+T0024 catalog-resolvable; AML.T0015+T0019+T0031 absent (3/6 prose-only at 3x F-5 T1496 precedent scale). ADR-035 D-numbered structure complete: D-1 Heuristic A 3-agent, D-2 additive-only, D-3 canonical 8-row mapping table with severity-hint column (Q6 YES), D-4 ML06 two-facet disjoint tells (architect MEDIUM-4 absorbed), D-5 ML03/ML04 disjoint tells (architect MEDIUM-5 absorbed), D-6 no schema bump, D-7 no consumers-list edit, D-8 no orchestrator edit, D-9 Pattern Category Disambiguation 3 instances (architect MEDIUM-3 absorbed), D-10 no source_attribution wiring. 22-file zero-edit invariant correctly scoped (28 detection-tier files - 6 F-6 targets = 22 unchanged). Predictive-ML topology gate (FR-016) enforces zero-impact-when-absent on 6 non-ML baselines. Constitution Check 10/10 PASS; gate verdict: no violations. Q1 RESOLVED (predictive-ml-app/ default per architect HIGH-1 empirical grep); Q2/Q3/Q4/Q6 plan-day RESOLVED. Wave allocation correctly partitions sequential authoring (Wave 1.1→2.x→3.x) from parallel verification (Wave 4.1+4.0; 5.0+5.1). 0 BLOCKING / 0 HIGH / 0 MEDIUM / 0 LOW (5 advisory recommendations). Architect APPROVES for /aod.tasks. Full review: .aod/results/architect-plan-232.md."
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: ML Top 10 Coverage Bundle (OWASP Machine Learning Security Top 10:2023)

**Branch**: `232-ml-top-10-coverage-bundle` | **Date**: 2026-04-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/232-ml-top-10-coverage-bundle/spec.md`
**PRD**: [docs/product/02_PRD/232-ml-top-10-coverage-bundle-2026-04-27.md](../../docs/product/02_PRD/232-ml-top-10-coverage-bundle-2026-04-27.md)
**BLP-01 Phase**: Tier 2 F-6 — first Tier 2 closure feature; **third execution** of the Heuristic A **enrichment** branch (after F-3 single-agent and F-5 two-agent), **first at three-agent scope**; closes ML01/ML03/ML04/ML07/ML08 Planned → Covered and ML06 Partial → Covered, completing OWASP ML Top 10:2023 = 10/10 milestone (combined post-F-5 OWASP AI top-10 = 20/20: post-F-6 30 of 30 across all three top-10 frameworks)

## Summary

Enrich three existing host threat agents — `tampering` (STRIDE-tier), `data-poisoning` (AI-tier), `model-theft` (AI-tier) — to close 6 OWASP ML Top 10:2023 detection gaps via Heuristic A consolidation at **three-agent scope**. **No new agent files, no new skill directories, no schema bump, no consumers-list edit, no functional orchestrator/dispatch edit, no `source_attribution` populator wiring extension.** Net change is **purely additive** to six existing files plus one new ADR-035: (1) `tampering.md` metadata `owasp_references += [OWASP ML01:2023, MITRE ATLAS AML.T0015]`, `## Purpose` 1–3 line extension, Detection Workflow Step 5 references += new ML/ATLAS exemplar mention; (2) `tachi-tampering/references/detection-patterns.md` appends Pattern Category 10 (Adversarial Input Manipulation, Predictive ML) after Cat 9 + Pattern Category Disambiguation subsection + Primary Sources extension; (3) `data-poisoning.md` metadata `owasp_references += [OWASP ML06:2023, ML07:2023, ML08:2023, MITRE ATLAS T0018, T0019, T0020, T0031]`, `## Purpose` extension, Step 5 references extension; (4) `tachi-data-poisoning/references/detection-patterns.md` appends Pattern Category 8 (Transfer Learning Supply Chain) + Cat 9 (Feedback-Loop Model Skewing) + Cat 10 (Predictive-ML Supply Chain Completeness) after Cat 7 + Pattern Category Disambiguation subsection + Primary Sources extension; (5) `model-theft.md` metadata `owasp_references += [OWASP ML03:2023, ML04:2023, ML06:2023, MITRE ATLAS T0024]`, `## Purpose` extension, Step 5 references extension; (6) `tachi-model-theft/references/detection-patterns.md` appends Pattern Category 12 (Model Inversion) + Cat 13 (Membership Inference) + Cat 14 (Predictive-ML Artifact Supply Chain) after Cat 11 + Pattern Category Disambiguation subsection + Primary Sources extension; (7) public ADR-035 documenting the Heuristic A enrichment pattern at three-agent scope as operational precedent (Proposed → Accepted dual-commit per ADR-027/028/029/030/031/032/033/034 lineage). Findings emit with existing `T-{N}` prefix (tampering), `D-{N}` prefix (data-poisoning), and `LLM-{N}` prefix (model-theft); each new finding cites the appropriate `OWASP ML0X:2023` primary in its prose-level `references:` array (existing finding-YAML field since v1.0; F-6 does NOT extend `source_attribution` populator wiring — that scope belongs to F-A3).

**Architectural approach**: Apply ADR-023 Decision 3 additive-only edit discipline. Existing prose in all three agent `.md` files' `## Purpose` sections + Cat 1–9 (tampering) + Cat 1–7 (data-poisoning) + Cat 1–11 (model-theft post-F-5) + `## Overview` + `## Targeted DFD Element Types` + `## Trigger Keywords` + `## Primary Sources` (existing entries) sections remain **byte-identical** pre/post edit (grep-checkable). Architect MEDIUM-3/4/5 (Pattern Category Disambiguation requirement on three companions; ML06 two-facet disjoint-tells decision; ML03/ML04 disjoint-tells decision) absorbed into ADR-035 D-numbered decisions and FR-011/SC-014 enforceable invariants. Q1 RESOLVED at PRD time (architect HIGH-1 finding: agentic-app has zero predictive-ML signal — new `examples/predictive-ml-app/` example authoring is the default plan-day path). The enriched agents activate as they do today on Process / Data Store / Data Flow components matching existing trigger keywords; new Pattern Categories fire only on architectures additionally exhibiting predictive-ML topology indicators (the predictive-ML topology gate ensures byte-identity on the 6 non-predictive-ML baselines).

**Touch points**: 0 new agent files, 0 new skill directories, 0 schema edits, 0 functional dispatch edits, 0 consumers-list edits, 0 `source_attribution` populator wiring extensions, 0 new runtime dependencies. **6 additive file edits** (3 host agents + 3 companions) + **1 new ADR** (ADR-035 with 8-row mapping table + ML06 two-facet decision + ML03/ML04 disjoint-tells decision) + **1 new example architecture** (`examples/predictive-ml-app/architecture.md` Q1 RESOLVED) + **1 example regeneration** (`predictive-ml-app/`) + **0 cosmetic annotation edits** (default-NO; all three host agents already fully registered and lack any LLM-tier annotation that would warrant ML-tier parity since ML coverage is detection-side only). **F-6 surface is 75% larger than F-5's pattern-authoring surface but no new file shape (asymmetric to F-2's full new-agent shape). Realistic envelope: 2.5 working days.**

## Technical Context

**Language/Version**: Markdown + YAML + Python 3.11 (existing — stdlib + `pyyaml`); agent and skill content files, not executable code
**Primary Dependencies**: `pyyaml` (runtime, already declared), `pytest` (dev-only, already declared per Feature 128 precedent); **no new runtime or dev dependencies**
**Storage**: File-based; reads `schemas/finding.yaml` (v1.8, **no edit**), `schemas/taxonomy/{owasp,mitre-atlas,mitre-attack}.yaml` (F-A1 catalogs, read-only for `references` validation); writes only to `.claude/agents/tachi/{tampering,data-poisoning,model-theft}.md`, `.claude/skills/tachi-{tampering,data-poisoning,model-theft}/references/detection-patterns.md`, `docs/architecture/02_ADRs/ADR-035-ml-top-10-coverage-bundle.md`, `examples/predictive-ml-app/` (Q1 RESOLVED — new architecture authoring at plan day Tuesday 2026-04-28)
**Testing**: pytest (existing harness at `tests/scripts/`) + backward-compatibility test `tests/scripts/test_backward_compatibility.py` under `SOURCE_DATE_EPOCH=1700000000` per ADR-021 — **6 non-predictive-ML baselines** byte-identity gate (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`); structural-diff tests on Cat 1–9 (tampering) + Cat 1–7 (data-poisoning) + Cat 1–11 (model-theft post-F-5) byte-identity in all three companions; line-count tests on `tampering.md` (≤120) + `data-poisoning.md` (≤150) + `model-theft.md` (≤150); MAESTRO grep tests on all six enriched files; references-array assertion tests on Cat 10 (T) + Cat 8/9/10 (D) + Cat 12/13/14 (LLM) fixture findings (catalog-resolvable: ML01-ML10, AML.T0018, AML.T0020, AML.T0024, T1195; prose-only: AML.T0015, AML.T0019, AML.T0031)
**Target Platform**: Command-line Python tooling (macOS/Linux/WSL); orchestrator + threat agents invoked via `/tachi.threat-model` Claude command; PDF rendering via Typst + Mermaid CLI (unchanged)
**Project Type**: Single project (methodology toolkit — agents + skills + schemas + templates in a unified repo); no frontend/backend split
**Performance Goals**: Agent invocation latency unchanged. Seven new Pattern Categories (1 + 3 + 3) add O(7 additional pattern matches across three host dispatches); empirical impact <2ms per architecture file. No new performance regressions.
**Constraints**: (a) SC-005 byte-identity on Cat 1–9 (tampering) + structural sections is a BLOCKER; (b) SC-009 byte-identity on Cat 1–7 (data-poisoning) + structural sections is a BLOCKER; (c) SC-013 byte-identity on Cat 1–11 (model-theft post-F-5) + structural sections is a BLOCKER; (d) SC-018 byte-identity on **6 non-predictive-ML example PDFs** under `SOURCE_DATE_EPOCH=1700000000` is a BLOCKER; (e) SC-002 line-count cap ≤120 on `tampering.md` is a BLOCKER (PRD/plan-time baseline 51; expected post-edit 54-58); (f) SC-007 line-count cap ≤150 on `data-poisoning.md` is a BLOCKER (baseline 78; expected 84-90); (g) SC-011 line-count cap ≤150 on `model-theft.md` is a BLOCKER (baseline 97; expected 103-108); (h) SC-021 22-file zero-edit invariant on every detection-tier file other than the six F-6 enrichment targets is a BLOCKER (post-F-5 inventory: 28 detection-tier files; F-6 edits 6; the remaining 22 stay byte-identical); (i) SC-022 schema invariant — `schemas/finding.yaml` `schema_version` MUST remain `"1.8"` (BLOCKER); (j) SC-023 `references:` array must include the appropriate ML primary on every emitted new finding plus catalog-resolvable ATLAS where applicable (BLOCKER); (k) SC-024 zero MAESTRO references in all six enriched files (grep-auditable, BLOCKER); (l) FR-016 predictive-ML topology gate (correctness BLOCKER) — Cat 10 (T) + Cat 8/9/10 (D) + Cat 12/13/14 (LLM) emit zero findings on architectures lacking predictive-ML indicators; (m) FR-011 / SC-014 Pattern Category Disambiguation subsection on each companion (3 instances total) is a BLOCKER per architect MEDIUM-3
**Scale/Scope**: 0 new agent files; 0 new skill directories; 6 file edits (~5 lines additive on `tampering.md`; ~10 lines additive on `data-poisoning.md`; ~7 lines additive on `model-theft.md`; ~50-60 lines additive on tampering companion (Cat 10 + Disambiguation + Primary Sources); ~150-180 lines additive on data-poisoning companion (Cat 8 + 9 + 10 + Disambiguation + 3 Primary Sources); ~150-180 lines additive on model-theft companion (Cat 12 + 13 + 14 + Disambiguation + 3 Primary Sources)); 7 new Pattern Categories total (Cat 10 in tampering; Cat 8/9/10 in data-poisoning; Cat 12/13/14 in model-theft) with ≥4 indicators each, ≥1 worked example each, named ML-specific mitigations; 1 new ADR (~330-400 lines including 8-row mapping table + ML06 two-facet decision + ML03/ML04 disjoint-tells decision + 9-10 numbered Decisions); 1 new example architecture (`predictive-ml-app/architecture.md` ~150-200 lines authored at plan day) + 1 example regeneration. **Edit surface is between F-5 (two-agent enrichment, 1.5d) and F-2 (full new-agent shape, 2d). Realistic envelope: 2.5 working days.**

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Evaluated against `.aod/memory/constitution.md`:

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | PASS | Pattern Category 10 (tampering), 8/9/10 (data-poisoning), 12/13/14 (model-theft) detect generic predictive-ML adversarial signal classes; no hardcoded project-type assumptions; works on any architecture exhibiting predictive-ML topology indicators |
| II. API-First Design | N/A | No REST/GraphQL surface; threat agents are content files consumed by the orchestrator at invocation time |
| III. Backward Compatibility (NON-NEGOTIABLE) | PASS | Predictive-ML topology gate (FR-016) ensures byte-identity on 6 non-predictive-ML baselines. Schema unchanged; existing T-{N} / D-{N} / LLM-{N} findings remain valid. Local `.aod/` workflows unaffected. **No schema bump means even the schema-version-pinning surface is byte-identical** — F-6 is the third BLP-01 detection feature with zero schema-tier impact (after F-3 + F-5) and the first at three-agent enrichment scope. |
| IV. Concurrency & Data Integrity | N/A | F-6 is single-invocation content authoring; no concurrent state |
| V. Privacy & Data Isolation | PASS | Worked examples use clearly-fictional scenarios (predictive-ML fraud-detection classifier, computer-vision NLP classifier with active-learning, MLOps registry promoting versioned artifacts, fine-tuning pipeline pulling pretrained weights from HuggingFace Hub); no PII, no adopter data, no network calls by the agent |
| VI. Testing Excellence (MANDATORY) | PASS | Structural-diff tests on Cat 1–9 (T) + Cat 1–7 (D) + Cat 1–11 (LLM model-theft) byte-identity; line-count tests on all three agent files; MAESTRO grep test on all six enriched files; references-array assertion tests for Cat 10 (T) + Cat 8/9/10 (D) + Cat 12/13/14 (LLM) fixture findings; backward-compat byte-identity gate on 6 non-predictive-ML baselines (per team-lead MEDIUM-3 / FR-025: explicit `tester` agent ownership separate from `senior-backend-engineer`); Pattern Category Disambiguation header presence test (3 matches expected per FR-011) |
| VII. Definition of Done (NON-NEGOTIABLE) | PASS | Spec-defined SCs (SC-001 through SC-026) map to grep-checkable / wc-checkable / byte-identity predicates. SC-005 + SC-009 + SC-013 + SC-014 + SC-018 + SC-021 + SC-022 + SC-023 + SC-024 are BLOCKER-level gates. DoD bullet 16 (delivery retrospective at SC-026) carried via Day 3 PM close-out slot or buffer day per FR-026. DoD bullet 17 (release-please post-merge gate) carried via `/aod.deliver` two-step Pre-merge + Post-merge enforcement per `.claude/rules/git-workflow.md` |
| VIII. Product-Spec Alignment | PASS | Approved PRD 232 v2 exists (PM APPROVED; Architect APPROVED_WITH_CONCERNS — 0 BLOCKING / 1 HIGH absorbed in v2 / 5 MEDIUM-deferred / 3 LOW; Team-Lead APPROVED_WITH_CONCERNS — 0 BLOCKING / 0 HIGH / 3 MEDIUM-deferred / 4 LOW); spec.md has PM APPROVED sign-off (0 BLOCKING / 0 HIGH / 2 MEDIUM (clarification only) / 4 LOW) |
| IX. Git Workflow | PASS | Feature branch `232-ml-top-10-coverage-bundle` created; draft PR #233 opened with `feat(232):` Conventional Commits title at plan stage; no main commits; ADR-035 Proposed → Accepted dual-commit pattern. R12 release-please mitigation enforced via two-step Pre-merge + Post-merge per `.claude/rules/git-workflow.md` (F-212 incident precedent). |
| X. Zero-Edit Invariant (ADR-023 lineage) | PASS | FR-019 / SC-021 explicit; 22-file invariant covers 11 other threat agents + 11 other companion `detection-patterns.md` files (post-F-5 inventory: 28 detection-tier files; F-6 edits 6 host files; 22 stay byte-identical). FR-018 / SC-025 also enforce zero edit to `finding-format-shared.md` consumers list. FR-020 / SC-025 enforces zero functional edit to orchestrator dispatch tier (no cosmetic annotation defaults — all three host agents already registered). FR-021 enforces zero `source_attribution` populator wiring extension on host agents (deferred to F-A3). |

**Gate verdict**: No violations. No Complexity Tracking entries required.

## Project Structure

### Documentation (this feature)

```
specs/232-ml-top-10-coverage-bundle/
├── plan.md                  # This file (/aod.project-plan output)
├── research.md              # Phase 0 output (populated by /aod.spec)
├── data-model.md            # Phase 1 output — Pattern Category 10/8/9/10/12/13/14 shape + predictive-ML topology gate + finding shape
├── contracts/
│   └── finding-contract.md  # Finding IR contract for Cat 10 T-{N}, Cat 8/9/10 D-{N}, Cat 12/13/14 LLM-{N} findings (references-array + mitigation rules)
├── quickstart.md            # Phase 1 output — verification walkthrough
├── checklists/
│   └── requirements.md      # Spec quality checklist (PM-validated)
├── spec.md                  # PM-approved spec
└── tasks.md                 # Task breakdown (/aod.tasks output)
```

### Source Code (repository root)

```
tachi/
├── .claude/
│   ├── agents/
│   │   └── tachi/
│   │       ├── tampering.md                              # MODIFY (additive; 3 small edits) — 51 → 54-58 lines
│   │       ├── data-poisoning.md                         # MODIFY (additive; 3 small edits) — 78 → 84-90 lines
│   │       ├── model-theft.md                            # MODIFY (additive; 3 small edits) — 97 → 103-108 lines
│   │       ├── orchestrator.md                           # UNCHANGED (zero functional edit; all three agents already registered)
│   │       ├── output-integrity.md / misinformation.md / human-trust-exploitation.md  # UNCHANGED (22-file invariant; F-1/F-2/F-4 agents)
│   │       ├── tool-abuse.md                             # UNCHANGED (22-file invariant; F-3 host)
│   │       ├── denial-of-service.md                      # UNCHANGED (22-file invariant; F-5 host — F-6 does not re-enrich DoS)
│   │       ├── prompt-injection.md / agent-autonomy.md   # UNCHANGED (22-file invariant)
│   │       ├── spoofing / repudiation / info-disclosure / privilege-escalation.md  # UNCHANGED (4 STRIDE — tampering is enriched)
│   │       ├── risk-scorer.md                            # UNCHANGED (FR-022 infrastructure-tier invariant)
│   │       ├── control-analyzer.md                       # UNCHANGED
│   │       ├── threat-report.md                          # UNCHANGED
│   │       ├── threat-infographic.md                     # UNCHANGED
│   │       └── report-assembler.md                       # UNCHANGED
│   │
│   └── skills/
│       ├── tachi-tampering/
│       │   └── references/
│       │       └── detection-patterns.md                 # MODIFY (additive; appends Cat 10 + Pattern Category Disambiguation + Primary Sources extension) — 190 → ~240-260 lines
│       │
│       ├── tachi-data-poisoning/
│       │   └── references/
│       │       └── detection-patterns.md                 # MODIFY (additive; appends Cat 8 + Cat 9 + Cat 10 + Pattern Category Disambiguation + 3 Primary Sources entries) — 137 → ~290-330 lines
│       │
│       ├── tachi-model-theft/
│       │   └── references/
│       │       └── detection-patterns.md                 # MODIFY (additive; appends Cat 12 + Cat 13 + Cat 14 + Pattern Category Disambiguation + 3 Primary Sources entries) — 211 → ~360-400 lines
│       │
│       ├── tachi-orchestration/
│       │   └── references/
│       │       └── dispatch-rules.md                     # UNCHANGED (all three host agents already registered; no cosmetic annotation defaults)
│       │
│       ├── tachi-shared/
│       │   └── references/
│       │       └── finding-format-shared.md              # UNCHANGED (tampering, data-poisoning, model-theft all in consumers list — verified at PRD time + plan time)
│       │
│       ├── tachi-output-integrity/                        # UNCHANGED (22-file invariant; F-1's companion)
│       ├── tachi-misinformation/                          # UNCHANGED (22-file invariant; F-2's companion)
│       ├── tachi-tool-abuse/                              # UNCHANGED (22-file invariant; F-3 host companion)
│       ├── tachi-human-trust-exploitation/                # UNCHANGED (22-file invariant; F-4's companion)
│       ├── tachi-denial-of-service/                       # UNCHANGED (22-file invariant; F-5 host companion — not re-enriched by F-6)
│       └── tachi-{6 other detection skills}/              # UNCHANGED (22-file invariant)
│
├── schemas/
│   ├── finding.yaml                                       # UNCHANGED — schema_version stays "1.8"; id.pattern unchanged
│   └── taxonomy/                                          # UNCHANGED — read-only source for references validation
│       ├── owasp.yaml                                     # ML01-ML10 entries present (verified at PRD/plan time; 10 entries via grep)
│       ├── mitre-atlas.yaml                               # AML.T0018 + T0020 + T0024 catalog-resolvable; **AML.T0015 + T0019 + T0031 ABSENT** — named in mitigation prose only on Cat 10 (T) + Cat 8/9/10 (D) findings
│       └── mitre-attack.yaml                              # T1195 + T1195.001 + T1195.002 entries present (catalog-resolvable for ML06 supply-chain citations)
│
├── docs/
│   └── architecture/
│       └── 02_ADRs/
│           └── ADR-035-ml-top-10-coverage-bundle.md       # NEW — Proposed → Accepted dual-commit (PRD/plan-time verified next-available; ADR-034 highest existing)
│
├── tests/
│   └── scripts/
│       ├── test_ml_top_10_coverage_bundle_enrichment.py   # NEW — structural-diff tests on Cat 1–9 (T) + Cat 1–7 (D) + Cat 1–11 (LLM model-theft) byte-identity + line-count tests on all three agents + MAESTRO grep tests on all 6 files + Pattern Category Disambiguation header presence test (3 matches) + references-array assertion fixtures for Cat 10 (T) + Cat 8/9/10 (D) + Cat 12/13/14 (LLM)
│       ├── test_backward_compatibility.py                 # MODIFY (additive infrastructure update) — `DETECTION_AGENT_PATHS` removes `tampering.md` + `data-poisoning.md` (10 → 8 entries); `DETECTION_PATTERN_REF_ENRICHMENT_HOSTS` frozenset adds tampering + data-poisoning companions (5 → 7 entries; model-theft companion already in F-5 set); 6-baseline byte-identity loop unchanged
│       └── fixtures/
│           └── ml_top_10_coverage_bundle/                 # NEW — fixture findings for Cat 10 (T) + Cat 8/9/10 (D) + Cat 12/13/14 (LLM)
│               ├── valid_category_10_tampering_adversarial_input_finding.yaml
│               ├── valid_category_8_data_poisoning_transfer_learning_finding.yaml
│               ├── valid_category_9_data_poisoning_feedback_loop_finding.yaml
│               ├── valid_category_10_data_poisoning_corpus_supply_chain_finding.yaml
│               ├── valid_category_12_model_theft_inversion_finding.yaml
│               ├── valid_category_13_model_theft_membership_inference_finding.yaml
│               └── valid_category_14_model_theft_artifact_supply_chain_finding.yaml
│
├── examples/
│   ├── web-app / microservices / ascii-web-api / mermaid-agentic-app / free-text-microservice / maestro-reference/  # UNCHANGED (SC-018 baselines; non-predictive-ML — zero new findings)
│   ├── agentic-app/                                       # UNCHANGED (F-3 + F-5 mutation target — F-6 zero-touch per architect MEDIUM-2 correction)
│   ├── consumer-agent-app/                                # UNCHANGED (F-4 mutation target without `.baseline` byte-identity loop entry; untouched by F-6)
│   └── predictive-ml-app/                                 # NEW — F-6 mutation target; authored at plan day Tuesday 2026-04-28 by architect + senior-backend-engineer co-authoring; ~150-200 lines architecture.md exhibiting all 5 predictive-ML topology indicators (training pipeline, fine-tuning step on pretrained weights, MLOps registry, prediction-API serving classifier with no input-validation barrier, active-learning feedback loop); baseline excluded from `test_backward_compatibility.py` byte-identity loop (mirrors agentic-app + consumer-agent-app precedent)
│
└── scripts/
    └── tachi_parsers.py                                   # UNCHANGED (validate references field — no F-6 changes; F-A3 will own source_attribution populator wiring later)
```

**Structure Decision**: Single-project layout (existing tachi repo structure). **Zero new top-level directories**. All changes confined to `.claude/agents/tachi/{tampering,data-poisoning,model-theft}.md`, `.claude/skills/tachi-{tampering,data-poisoning,model-theft}/references/detection-patterns.md`, `docs/architecture/02_ADRs/`, `tests/scripts/`, `examples/predictive-ml-app/` (new). F-6 follows Feature 082 (lean-agent refactor) + ADR-023 (additive-only shared-reference edits) + Feature 142 (multi-agent component types) + F-1 + F-2 + F-3 + F-4 + F-5 precedents. **F-6 is the first BLP-01 feature to exercise ADR-023 Decision 3 at three-agent scope simultaneously** — the six-file additive surface across three host-agent + companion pairs.

## System Design

### Components

**Modified components (additive edits only — F-6-owned)**:

1. **`tampering` Threat Agent** (`.claude/agents/tachi/tampering.md`)
   - **Edit 1** (two-line additive): metadata YAML `owasp_references` list extended with `"OWASP ML01:2023 — Input Manipulation Attack"` and `"MITRE ATLAS AML.T0015 — Evade ML Model"` appended. Pre-existing entries byte-identical.
   - **Edit 2** (1–3 line additive append within `## Purpose` section): name the adversarial input manipulation surface for predictive ML (small-perturbation adversarial examples, FGSM/PGD-style attacks, decision-boundary attacks against deployed classifiers) alongside existing data-tampering surface — preserves existing `## Purpose` prose byte-identical
   - **Edit 3** (additive references-list extension on Detection Workflow Step 5): existing references-mention extended with `OWASP ML01:2023, MITRE ATLAS AML.T0015` exemplar mention
   - Line count: ≤120 (STRIDE tier cap per ADR-023); PRD/plan-time baseline 51; expected post-edit 54-58
   - Five-section canonical layout, single `**MANDATORY**: Read` directive, zero MAESTRO references — all preserved

2. **`data-poisoning` Threat Agent** (`.claude/agents/tachi/data-poisoning.md`)
   - **Edit 1** (seven-line additive): metadata YAML `owasp_references` list extended with `"OWASP ML06:2023 — AI Supply Chain Attacks"`, `"OWASP ML07:2023 — Transfer Learning Attack"`, `"OWASP ML08:2023 — Model Skewing"`, `"MITRE ATLAS AML.T0018 — Backdoor ML Model"`, `"MITRE ATLAS AML.T0019 — Publish Poisoned Datasets"`, `"MITRE ATLAS AML.T0020 — Poison Training Data"`, `"MITRE ATLAS AML.T0031 — Erode ML Model Integrity"`. Pre-existing entries byte-identical.
   - **Edit 2** (1–3 line additive append within `## Purpose` section): name the predictive-ML training poisoning, transfer-learning supply-chain, and feedback-loop skewing surfaces alongside the existing LLM/RAG poisoning surface — preserves existing `## Purpose` prose byte-identical
   - **Edit 3** (additive references-list extension on Detection Workflow Step 5): existing references-mention extended with `OWASP ML06:2023, ML07:2023, ML08:2023` exemplar mention plus catalog-resolvable ATLAS techniques (T0018, T0020); T0019 + T0031 named in prose only
   - Line count: ≤150 (AI tier cap per ADR-023); baseline 78; expected post-edit 84-90
   - Zero MAESTRO references preserved

3. **`model-theft` Threat Agent** (`.claude/agents/tachi/model-theft.md`)
   - **Edit 1** (four-line additive): metadata YAML `owasp_references` list extended with `"OWASP ML03:2023 — Model Inversion Attack"`, `"OWASP ML04:2023 — Membership Inference Attack"`, `"OWASP ML06:2023 — AI Supply Chain Attacks"` (predictive-ML artifact facet), `"MITRE ATLAS AML.T0024 — Exfiltration via ML Inference API"` appended. Pre-existing entries (LLM03:2025 pre-F-5 + LLM10:2025 from F-5) byte-identical.
   - **Edit 2** (1–3 line additive append within `## Purpose` section): name the predictive-ML extraction (model inversion, membership inference) and predictive-ML artifact supply-chain integrity surfaces alongside existing LLM-extraction and cost-amplification (F-5) surfaces — preserves existing `## Purpose` prose byte-identical
   - **Edit 3** (additive references-list extension on Detection Workflow Step 5): existing references-mention extended with `OWASP ML03:2023, ML04:2023, ML06:2023, MITRE ATLAS AML.T0024` exemplar mention
   - Line count: ≤150 (AI tier cap per ADR-023); baseline 97 (post-F-5); expected post-edit 103-108
   - Zero MAESTRO references preserved

4. **tampering Pattern Catalog** (`.claude/skills/tachi-tampering/references/detection-patterns.md`)
   - **Edit 1** (additive append after Cat 9): **Pattern Category 10 — Adversarial Input Manipulation (Predictive ML)** with primary OWASP ML01:2023, related MITRE ATLAS AML.T0015 (named in mitigation prose only — not catalog-resolvable); ≥4 indicators (target 5) covering deployed predictive ML classifier + inference endpoint with no input-validation barrier + missing adversarial-defense controls + missing distribution-shift monitoring + missing confidence-thresholding HITL escalation; ≥1 worked example (fraud-detection ML classifier serving a `/predict` endpoint with no input-validation barrier; attacker crafts feature-space perturbations to evade fraud detection); named adversarial-defense mitigations distinct from generic tampering controls (adversarial training on the model side, statistical anomaly detection on inputs, distribution-shift monitoring, inference-time confidence-thresholding with HITL escalation, ensemble disagreement detection)
   - **Edit 2** (additive Pattern Category Disambiguation subsection per FR-011 / ADR-035 D-numbered): explicit non-overlap carve between **tampering Cat 9** (Injection Attacks: XSS/SQLi/Command Injection — pre-existing, generic web-application injection) and **Cat 10** (Adversarial Input Manipulation against predictive ML inference endpoints) — same architecture may surface both Cat 9 + Cat 10 findings if it has both a generic API surface and a predictive-ML inference endpoint. Cat 1-8 surfaces (deserialization, supply-chain integrity gaps, etc.) also disambiguated.
   - **Edit 3** (additive list extension on `## Primary Sources`): append `OWASP ML01:2023 — Input Manipulation Attack`
   - Pre-existing Cat 1–9 + `## Overview` + `## Targeted DFD Element Types` + `## Trigger Keywords` + `## Primary Sources` (existing entries) remain byte-identical pre/post edit per ADR-023 Decision 3 (BLOCKER per SC-005)

5. **data-poisoning Pattern Catalog** (`.claude/skills/tachi-data-poisoning/references/detection-patterns.md`)
   - **Edit 1** (additive append after Cat 7): **Pattern Category 8 — Transfer Learning Supply Chain (Predictive ML)** with primary OWASP ML07:2023, related MITRE ATLAS AML.T0018 (catalog-resolvable, in `references` array) + AML.T0019 (named in mitigation prose only — not catalog-resolvable); ≥4 indicators (target 5) covering fine-tuning predictive-ML models on untrusted pretrained weights from public registries (HuggingFace Hub, TensorFlow Hub, PyTorch Hub) without checksum verification, adapter poisoning where malicious LoRA/adapter weights are merged, missing provenance metadata on pretrained weight artifacts, fine-tuning hash-pinning absent, model-card provenance review missing; ≥1 worked example (fine-tuning pipeline pulling pretrained weights from HuggingFace Hub without `revision=` checksum pinning; attacker publishes weight artifact with backdoor); named LLM-specific mitigations (signed-weight-artifact policy with cryptographic verification at load time — Sigstore-style or KMS-backed, allowlist of trusted pretrained-weight sources, fine-tuning hash-pinning for reproducibility, model-card provenance review)
   - **Edit 2** (additive append after Cat 8): **Pattern Category 9 — Feedback-Loop Model Skewing (Active Learning / Online Learning)** with primary OWASP ML08:2023, related MITRE ATLAS AML.T0020 (catalog-resolvable) + AML.T0031 (prose-only); ≥4 indicators (target 5) covering active-learning pipelines where production data feeds back into training without integrity controls, label-flipping in HITL labeling tools where attacker-controlled labelers introduce poisoned labels, online-learning drift injection where adversarial inference inputs poison subsequent retraining, recommendation-system feedback loops where clickstream is reused for retraining without tamper-detection, drift-detection alarms missing; ≥1 worked example (active-learning loop reading production predictions back into training without tamper-detection on label distribution drift); named mitigations (feedback-data integrity gates with anomaly detection on label distribution drift, labeler-trust scoring with reputation-based weighting, periodic retraining-data audit with held-out canaries, drift-detection alarms on production inference distributions)
   - **Edit 3** (additive append after Cat 9): **Pattern Category 10 — Predictive-ML Supply Chain Completeness (Datasets, Feature Stores, MLOps Registry)** with primary OWASP ML06:2023 (corpus-side facet per ADR-035 D-numbered ML06 two-facet split), related MITRE ATT&CK T1195 + T1195.001 + T1195.002 (all catalog-resolvable); ≥4 indicators (target 5) covering dataset repositories (Kaggle datasets, public corpora) with no integrity verification, feature stores (Feast, Tecton, custom S3-backed stores) with no access control or write-audit, MLOps model registries (MLflow, SageMaker Model Registry, Vertex AI Model Registry) with no signed-artifact policy on model promotions, missing model-card or datasheet metadata, dataset-checksum manifest absent; ≥1 worked example (training pipeline ingesting from a public Kaggle dataset without checksum verification + Feast feature store with no IAM write-audit + MLflow registry promoting models without signed-artifact policy); named mitigations (signed-artifact policy at registry boundary, IAM-enforced write-audit on feature stores, dataset-checksum manifest with reproducibility verification, model-card review gate before promotion to production)
   - **Edit 4** (additive Pattern Category Disambiguation subsection per FR-011 / ADR-035 D-numbered): explicit non-overlap carve between **data-poisoning Cat 6** (RAG corpus poisoning — pre-existing, LLM retrieval-augmented-generation knowledge stores) and **Cat 8** (Transfer Learning Supply Chain — predictive-ML pretrained weights). Cat 7 (Backdoor Triggers via Prompt Injection — pre-existing, LLM-tier) vs **Cat 9** (Feedback-Loop Model Skewing — predictive-ML active-learning). Cat 6 (LLM RAG) vs **Cat 10** (Predictive-ML corpus-side supply chain — datasets/feature-stores/registries). Same architecture may legitimately surface both LLM-tier (Cat 6/7) and predictive-ML-tier (Cat 8/9/10) findings if both topology types are present (e.g., LLM-fronted assistant with predictive-ML classifier subprocess).
   - **Edit 5** (additive list extension on `## Primary Sources`): append `OWASP ML06:2023 — AI Supply Chain Attacks`, `OWASP ML07:2023 — Transfer Learning Attack`, `OWASP ML08:2023 — Model Skewing`
   - Pre-existing Cat 1–7 + `## Overview` + `## Targeted DFD Element Types` + `## Trigger Keywords` + `## Primary Sources` (existing entries) remain byte-identical pre/post edit per ADR-023 Decision 3 (BLOCKER per SC-009)

6. **model-theft Pattern Catalog** (`.claude/skills/tachi-model-theft/references/detection-patterns.md`)
   - **Edit 1** (additive append after Cat 11 line ~211): **Pattern Category 12 — Model Inversion (Predictive ML)** with primary OWASP ML03:2023, related MITRE ATLAS AML.T0024 (catalog-resolvable; **shared with Cat 13 but disjoint architectural-tells per ADR-035 D-numbered**); ≥4 indicators (target 5) covering reconstruction of training-data inputs from model outputs via white-box gradient inversion or black-box optimization against the prediction API, attribute-inference attacks where attacker queries model to infer sensitive attributes of training records, inversion attacks on face-recognition / medical-imaging / tabular-PII classifiers, no DP-SGD on training, output-perturbation noise injection absent at inference time, query-rate throttling per tenant absent, model-extraction-pattern detection (anomalous query distributions) absent; ≥1 worked example (medical-imaging classifier serving `/predict` endpoint without DP-SGD on training and without per-tenant query rate throttling; attacker performs gradient-inversion against the prediction API to reconstruct training images); named mitigations (differential privacy on training with DP-SGD bounded ε, output-perturbation noise injection at inference time, query-rate throttling per tenant, model-extraction-pattern detection)
   - **Edit 2** (additive append after Cat 12): **Pattern Category 13 — Membership Inference (Predictive ML)** with primary OWASP ML04:2023, related MITRE ATLAS AML.T0024 (catalog-resolvable; shared with Cat 12 but disjoint architectural-tells); ≥4 indicators (target 5) covering attacks that determine whether a specific record was present in training set via confidence-thresholding (high-confidence prediction = likely member), shadow-model attacks (training a surrogate to mimic the target), label-only attacks against APIs returning only the predicted class, no DP-SGD on training, confidence-output truncation absent, label-only response mode missing for sensitive endpoints; ≥1 worked example (fraud-detection classifier API returning prediction confidence values; attacker uses confidence-thresholding to infer that a target individual is in the training set); named mitigations (DP-SGD on training, confidence-output truncation or label-only response mode for sensitive endpoints, query-rate throttling, training-data minimization)
   - **Edit 3** (additive append after Cat 13): **Pattern Category 14 — Predictive-ML Artifact Supply Chain (Model Registry, Weight Tampering)** with primary OWASP ML06:2023 (artifact-side facet per ADR-035 D-numbered ML06 two-facet split), related MITRE ATT&CK T1195 + T1195.001 + T1195.002 (catalog-resolvable); ≥4 indicators (target 5) covering model-registry checkpoint poisoning where malicious models are promoted via compromised registry credentials, weight-tampering between training and serving where serialized model files (`.pkl`, `.pt`, `.h5`) are modified in transit or at rest, missing model-signing or attestation policy, registry IAM with promotion-gate review absent, integrity verification at model-load time absent, immutable artifact storage with audit logging absent; ≥1 worked example (MLflow model registry promoting models without signed-artifact policy or IAM-enforced promotion review; attacker compromises registry credentials and pushes a backdoored model checkpoint); named mitigations (model-signing with cryptographic attestation — Sigstore-style or KMS-backed, registry IAM with promotion-gate review, integrity verification at model-load time, immutable artifact storage with audit logging)
   - **Edit 4** (additive Pattern Category Disambiguation subsection per FR-011 / ADR-035 D-numbered): explicit non-overlap carve between **model-theft Cat 1-9** (LLM-tier extraction — pre-existing, weight-leak via debugging interfaces, query-based extraction, prediction-API abuse, system-prompt leakage) and **Cat 12** (Model Inversion — predictive-ML training-data input reconstruction). **Cat 12 vs Cat 13** disambiguation per ADR-035 D-numbered: Cat 12 = white-box gradient inversion + black-box optimization for **input reconstruction**; Cat 13 = confidence-thresholding + shadow-model attacks for **training-set membership determination**. Shared `MITRE ATLAS AML.T0024` citation acceptable but architectural-tells must be distinguishable to prevent duplicate findings on the same prediction-API endpoint. **Cat 10/11 (LLM-tier cost-DoW from F-5)** vs **Cat 14 (predictive-ML artifact supply-chain)**: Cat 10/11 fire on LLM-tier cost-amplification + denial-of-wallet; Cat 14 fires on predictive-ML model-registry/weight-artifact integrity at promotion gate. Same architecture (LLM + predictive-ML hybrid) may surface Cat 10/11 + Cat 14 findings.
   - **Edit 5** (additive list extension on `## Primary Sources`): append `OWASP ML03:2023 — Model Inversion Attack`, `OWASP ML04:2023 — Membership Inference Attack`, `OWASP ML06:2023 — AI Supply Chain Attacks`
   - Pre-existing Cat 1–11 (post-F-5; uniform `## Pattern Category N:` headings) + `## Overview` + `## Targeted DFD Element Types` + `## Trigger Keywords` (line 19) + `## Primary Sources` (existing entries including LLM10 from F-5) remain byte-identical pre/post edit per ADR-023 Decision 3 (BLOCKER per SC-013)

7. **Public Per-Feature ADR** (`docs/architecture/02_ADRs/ADR-035-ml-top-10-coverage-bundle.md`)
   - Proposed → Accepted dual-commit (ADR-027/028/029/030/031/032/033/034 precedent)
   - **9-10 numbered Decisions** in body:
     - **Decision 1**: Heuristic A enrichment vs. new agents at **three-agent scope** — signal-class identity rationale (same-class with three host agents: ML01 → tampering data-integrity sub-class; ML06-corpus + ML07 + ML08 → data-poisoning adversarial-corpus sub-class; ML03 + ML04 + ML06-artifact → model-theft extraction + artifact-integrity sub-class). Three hypothetical new agents (`adversarial-input-manipulation`, `predictive-ml-poisoning`, `predictive-ml-extraction`) explicitly NOT created.
     - **Decision 2**: Additive-only edit discipline per ADR-023 Decision 3 with byte-identity proof on Cat 1–9 (T) + Cat 1–7 (D) + Cat 1–11 (LLM model-theft post-F-5)
     - **Decision 3**: **Canonical 8-row ML Top 10 sub-pattern → owning-agent mapping table** (the audit deliverable). Closure rows: (a) ML01 input manipulation → tampering Cat 10 (severity MEDIUM-HIGH default); (b) ML07 transfer learning → data-poisoning Cat 8 (HIGH default); (c) ML08 model skewing → data-poisoning Cat 9 (HIGH default); (d) ML06 corpus-side → data-poisoning Cat 10 (HIGH default); (e) ML03 model inversion → model-theft Cat 12 (MEDIUM-HIGH default); (f) ML04 membership inference → model-theft Cat 13 (MEDIUM-HIGH default); (g) ML06 artifact-side → model-theft Cat 14 (HIGH default); (h) ML02/05/09/10 reference rows showing pre-F-6 ownership (ML02 → data-poisoning Cat 1-7 pre-F-6; ML05 → model-theft Cat 1-9 pre-F-6; ML09 → output-integrity F-1 closure; ML10 → existing pre-BLP-01 work)
     - **Decision 4**: **ML06 two-facet disjoint architectural-tells decision** (architect MEDIUM-4): corpus-side Cat 10 (data-poisoning) owns dataset-repos / feature-stores / training-data path; artifact-side Cat 14 (model-theft) owns model-registry / weight-artifact-storage / serving-time integrity. Same architecture may surface both findings without duplication.
     - **Decision 5**: **ML03 vs ML04 disjoint architectural-tells decision** (architect MEDIUM-5): Cat 12 (model-inversion) = white-box gradient inversion + black-box optimization for **input reconstruction**; Cat 13 (membership-inference) = confidence-thresholding + shadow-model attacks for **training-set membership determination**. Both share AML.T0024 citation but architectural-tells distinguishable.
     - **Decision 6**: No schema bump — reuses T-{N} / D-{N} / LLM-{N} prefixes; structurally symmetric with F-3 (ADR-032 lines 84+182 forecast) and F-5 (ADR-034 lines 192–204 forecast). **Third BLP-01 detection feature with no schema bump after F-3 + F-5; first at three-agent enrichment scope.** Asymmetric to F-1/F-2/F-4 (which all bumped schema).
     - **Decision 7**: No consumers-list edit — `tampering`, `data-poisoning`, `model-theft` all already in `finding-format-shared.md` consumers list (PRD/plan-time verified)
     - **Decision 8**: No functional orchestrator/dispatch-rules edit — all three host agents already fully registered. No cosmetic annotation defaults (asymmetric to F-5's Q2 architect-tractable cosmetic carve-out).
     - **Decision 9**: **Pattern Category Disambiguation requirement on three companions** (architect MEDIUM-3): tampering disambiguates Cat 10 from Cat 1-9; data-poisoning disambiguates Cat 8/9/10 from Cat 1-7; model-theft disambiguates Cat 12/13/14 from Cat 1-11 (including F-5's Cat 10/11 cost-DoW carve-out). Mirrors F-3 ADR-032 D7 + F-5 ADR-034 D7 precedent at three-agent scale.
     - **Decision 10**: No `source_attribution` populator wiring extension on host agents — deferred to F-A3; F-6 cites ML Top 10 references in prose-level `references:` array only; F-A3 inheritance one-way
     - (Optional Decision 11): Public ADR omits commercial framing per SDR-001 Option C
   - Cross-references: ADR-021 (byte-identity baseline harness), ADR-023 (lean+skill-references pattern, additive-only edits Decision 3), ADR-027 (taxonomy crosswalk), ADR-028 (source attribution schema extension + Decision 6 F-A3 deferral), ADR-030 Decision 1 (signal-class taxonomy in LLM tier), ADR-031 Decision 8 (regex-alternation minor-bump rule as the **asymmetry** F-6 does NOT invoke — third no-bump enrichment), ADR-032 (first enrichment-branch execution at single-agent scope; lines 84+182 forecast), ADR-034 (second enrichment-branch execution at two-agent scope; **explicit cross-reference to lines 192–204 forecast** that F-6 will land at three-agent scope with no schema bump)
   - Detection Calibration Note: clarifies structural-absence detection style consistent with F-1 / F-2 / F-4 / F-5 absence-style; acceptable FP risk on architectures with implicit-but-undeclared controls per existing tachi convention
   - Zero-MAESTRO-reference invariant: ADR-035 itself contains zero MAESTRO references in Decision sections (mirrors agent file invariant per ADR-023 Decision 2)
   - Revision History table tracking Proposed → Accepted dates; post-merge SHA fill recording squash commit per team-lead LOW-1 / FR-026

### Data Flow

Given a DFD architecture description, the orchestrator dispatches `tampering` **as it does today** when any DFD `Process`, `Data Store`, or `Data Flow` element matches existing tampering trigger keywords AND `data-poisoning` when any `Process` or `Data Store` matches existing data-poisoning trigger keywords AND `model-theft` when any `Process` matches existing model-theft trigger keywords. Each agent reads its companion `detection-patterns.md` via the existing single `**MANDATORY**: Read` directive, evaluates pattern categories on each dispatched component, and emits zero or more findings. The new Pattern Categories (Cat 10 in tampering; Cat 8/9/10 in data-poisoning; Cat 12/13/14 in model-theft) enforce the **predictive-ML topology gate** (FR-016): findings emit only when the architecture additionally exhibits predictive-ML indicators (declared training pipeline, MLOps registry, feature store, fine-tuning step on pretrained weights, active-learning loop, prediction-API endpoint serving classifier/regressor, model-deployment artifact, weight checkpoint storage). Cat 12 (model-inversion) and Cat 13 (membership-inference) are emitted independently — same prediction-API endpoint exhibiting input-reconstruction exposure surfaces Cat 12; same endpoint exhibiting membership-determination exposure surfaces Cat 13; both can fire on the same architecture without duplication per ADR-035 D-5 disjoint architectural-tells. Cat 10 (data-poisoning ML06 corpus-side) and Cat 14 (model-theft ML06 artifact-side) are emitted independently when the architecture exhibits both corpus-side and artifact-side supply-chain signals per ADR-035 D-4 disjoint architectural-tells. Findings flow through orchestrator Phase 3, Phase 4 (referential validation reads `references` array — no F-6 changes; F-A3 will own `source_attribution` populator wiring later), and Phase 5 (deduplication) **identically** to existing T-{N}, D-{N}, LLM-{N} findings. No consumer-tier changes required. Report-tier rendering (`threat-report.md`, `threats.md`) groups all `T-{N}` findings (Cat 1–10) cohesively in `category: tampering` section, all `D-{N}` findings (Cat 1–10) cohesively in `category: data-poisoning` section, and all `LLM-{N}` findings from model-theft (Cat 1–14) cohesively in `category: llm` section — single-namespace ID space per agent, sequential numbering across all categories.

### Tech Stack

- **Agent / skill files**: Markdown + YAML (ADR-023 lean-agent + additive-only shared-reference pattern)
- **Schema**: `schemas/finding.yaml` v1.8 — **unchanged** (T, D, LLM prefixes already enumerated; F-6 reuses all three)
- **Taxonomy catalogs**: `schemas/taxonomy/{owasp,mitre-atlas,mitre-attack}.yaml` (F-A1, unchanged) — consumed read-only for `references` validation. ML01-ML10 catalog-resolvable; AML.T0018, T0020, T0024 catalog-resolvable; **AML.T0015, T0019, T0031 ABSENT** (named in mitigation prose only); T1195 + T1195.001 + T1195.002 catalog-resolvable.
- **Orchestrator dispatch**: `.claude/agents/tachi/orchestrator.md` + `.claude/skills/tachi-orchestration/references/dispatch-rules.md` — **unchanged** (all three host agents already fully registered)
- **Parser**: `scripts/tachi_parsers.py` (unchanged — `references` field validation already in place; F-A3 will own `source_attribution` populator wiring later)
- **Test harness**: pytest + `tests/scripts/test_backward_compatibility.py` (modified additively — `DETECTION_AGENT_PATHS` removes 2 entries; `DETECTION_PATTERN_REF_ENRICHMENT_HOSTS` adds 2 entries; 6-baseline byte-identity loop unchanged thanks to predictive-ML topology gate ensuring zero impact on non-ML baselines) + new `tests/scripts/test_ml_top_10_coverage_bundle_enrichment.py` (structural-diff + line-count + MAESTRO grep + Pattern Category Disambiguation header presence test + references-array assertion fixtures for Cat 10 (T) + Cat 8/9/10 (D) + Cat 12/13/14 (LLM))
- **Example regeneration pipeline**: `/tachi.threat-model` → `/tachi.risk-score` → `/tachi.compensating-controls` → `/tachi.infographic all` → `/tachi.security-report` (existing pipeline, unchanged)
- **Typst templates**: no edits — PDF renderer reads `threats.md` / `risk-scores.md` / `compensating-controls.md` and existing pipeline artifacts auto-render post-regeneration
- **ADR dual-commit**: standard Proposed → Accepted lifecycle via `gh pr` + squash merge (ADR-027/028/029/030/031/032/033/034 precedent)
- **New example architecture**: `examples/predictive-ml-app/architecture.md` authored at plan day (Q1 RESOLVED) exhibiting all 5 predictive-ML topology indicators

## Phase 0: Research

**Status**: Populated by `/aod.spec` at [research.md](./research.md). Key grounding facts re-confirmed at plan time (2026-04-27):

- `.claude/agents/tachi/tampering.md` is **51 lines** (PRD-time + plan-time verified; expected post-edit 54-58 lines)
- `.claude/agents/tachi/data-poisoning.md` is **78 lines** (PRD-time + plan-time verified; expected post-edit 84-90 lines)
- `.claude/agents/tachi/model-theft.md` is **97 lines** post-F-5 (PRD-time + plan-time verified; expected post-edit 103-108 lines); existing `owasp_references` includes LLM03:2025 + LLM10:2025 — F-6 appends ML03/ML04/ML06/AML.T0024 (4-line append)
- `.claude/skills/tachi-tampering/references/detection-patterns.md` is **190 lines** (PRD/plan-time verified) with Cat 1–9 + Overview + Targeted DFD Element Types + Trigger Keywords + Primary Sources
- `.claude/skills/tachi-data-poisoning/references/detection-patterns.md` is **137 lines** (PRD/plan-time verified) with Cat 1–7 + structural sections
- `.claude/skills/tachi-model-theft/references/detection-patterns.md` is **211 lines** post-F-5 (PRD/plan-time verified) with Cat 1–11 (post-F-5 baseline) + Overview + Targeted DFD + Trigger Keywords (line 19) + Primary Sources
- `schemas/finding.yaml:13` `schema_version: "1.8"` (post-F-5; F-6 does NOT bump)
- `schemas/finding.yaml` `id.pattern: "^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\\d+$"` — `T`, `D`, `LLM` already enumerated; F-6 reuses all three
- `schemas/taxonomy/owasp.yaml` contains **ML01-ML10** records (10 entries plan-time-verified via grep)
- `schemas/taxonomy/mitre-atlas.yaml` catalog-resolvability:
  - **AML.T0018** (Backdoor ML Model): present (Cat 8 references)
  - **AML.T0020** (Poison Training Data): present (Cat 9 references)
  - **AML.T0024** (Exfiltration via ML Inference API): present (Cat 12/13 references)
  - **AML.T0015** (Evade ML Model): **ABSENT** — named in Cat 10 (T) mitigation prose only
  - **AML.T0019** (Publish Poisoned Datasets): **ABSENT** — named in Cat 8 mitigation prose only
  - **AML.T0031** (Erode ML Model Integrity): **ABSENT** — named in Cat 9 mitigation prose only
- `schemas/taxonomy/mitre-attack.yaml` contains **T1195** + **T1195.001** + **T1195.002** entries (catalog-resolvable for ML06 supply-chain citations on Cat 10 (D) + Cat 14 (LLM))
- `.claude/skills/tachi-shared/references/finding-format-shared.md` consumers list contains all three host agents (PRD-time + plan-time verified — no edits needed)
- `.claude/skills/tachi-orchestration/references/dispatch-rules.md` references all three host agents at multiple callsites (no functional dispatch edit needed; no cosmetic annotation defaults — asymmetric to F-5's Q2 architect-tractable carve-out)
- ADR-035 does NOT yet exist (PRD-time + plan-time verified next-available ADR number; ADR-034 is highest existing per `ls docs/architecture/02_ADRs/`)
- 0 MAESTRO references in all six target files (PRD-time + plan-time grep-verified)
- F-1, F-2, F-3, F-4, F-5 ADRs (ADR-030, ADR-031, ADR-032, ADR-033, ADR-034) are Accepted; F-6 ADR-035 cross-references ADR-030 D1, ADR-031 D8 (asymmetry — F-6 does NOT invoke), ADR-032 (single-agent precedent), ADR-034 (two-agent precedent + lines 192–204 forecast)

**Open research items resolved at PRD time** (not re-litigated during /aod.project-plan):
- **Q1**: Mutation-target example for FR-7 (now FR-014) — RESOLVED at PRD time (architect HIGH-1 finding 2026-04-27): **agentic-app has zero predictive-ML signal** (negative grep on 13 indicators); new `examples/predictive-ml-app/` example authoring is the **default plan-day path**, not contingency. Plan-day Tuesday 2026-04-28 architect/senior-backend-engineer co-authoring.

**Open research items resolved during /aod.project-plan** (architect plan-day decision):
- **Q2**: Single category vs split for ML06 in mapping table — architect plan-day decision per PRD; default: two rows for explicit disambiguation. **Plan-time decision: TWO ROWS** in ADR-035 mapping table (corpus-side Cat 10 + artifact-side Cat 14 as separate rows) per ADR-035 D-4. Encoded as ML06 two-facet disjoint architectural-tells.
- **Q3**: MITRE ATLAS catalog-resolvability for AML.T0015/T0018/T0019/T0020/T0024/T0031 — RESOLVED at plan time via grep on `schemas/taxonomy/mitre-atlas.yaml`: **3 of 6 are catalog-resolvable** (T0018, T0020, T0024); **3 of 6 are absent** (T0015, T0019, T0031). The 3 absent entries appear in mitigation prose only at 3x F-5 T1496 precedent scale. Catalog augmentation deferred to F-A1.1 follow-on per spec OoS-6.
- **Q4**: Pattern Category granularity on `data-poisoning` Cat 10 (Predictive-ML Supply Chain Completeness) — single category covering datasets + feature stores + MLOps registries vs 2-3 finer-grained categories — architect plan-day decision per PRD; default: single category. **Plan-time decision: SINGLE CATEGORY** per Q4 default. Indicator surface (5+ indicators) supports single-category cohesion. Architect retains plan-day floor authority but default holds.
- **Q5**: `examples/agentic-app/` baseline regen strategy — N/A for F-6 (architect MEDIUM-2 correction: F-6 does NOT touch agentic-app; new `predictive-ml-app/` is F-6 mutation target). Q5 effectively dissolved into Q1 RESOLVED.
- **Q6**: ADR-035 mapping-table column structure — should the table have a "severity-hint" column (mirroring ADR-034's 5-row table)? Default: yes, matching ADR-034 structure for consistency. **Plan-time decision: YES** — ADR-035 mapping table includes severity-hint annotation column for parity with ADR-034 + cross-feature comparability.

## Phase 1: Design & Contracts

**Prerequisites**: research.md populated (Phase 0 complete)

### Finding IR Contract (`contracts/finding-contract.md`)

**Purpose**: Document the shape of Cat 10 `T-{N}` findings (tampering), Cat 8/9/10 `D-{N}` findings (data-poisoning), and Cat 12/13/14 `LLM-{N}` findings (model-theft) emitted by the enriched agents, including `references` array invariants, mitigation-text rules, and predictive-ML topology gate. See [contracts/finding-contract.md](./contracts/finding-contract.md) for full contract.

**Contract summary (tampering Cat 10)**:

```yaml
id: "T-{N}"                           # existing prefix (no schema bump in F-6); single-namespace across Cat 1–10
category: "tampering"                 # existing enum value — unchanged
title: "Adversarial Input Manipulation: {classifier} prediction-API without input-validation barrier"
severity: "medium" | "high"           # OWASP 3×3 matrix; Cat 10 default MEDIUM-HIGH
component: "{DFD Process serving deployed predictive-ML classifier}"
description: "{2-4 sentence threat description distinguishing predictive-ML adversarial input manipulation from generic injection attacks}"
mitigation: "{adversarial-defense mechanisms — adversarial training, statistical anomaly detection, distribution-shift monitoring, confidence-thresholding HITL escalation, ensemble disagreement detection}"
references:
  - "OWASP ML01:2023 — Input Manipulation Attack"  # REQUIRED on every Cat 10 finding
  # MITRE ATLAS AML.T0015 named in mitigation prose only — NOT in references (catalog-absent)
```

**Contract summary (data-poisoning Cat 8/9/10)**:

```yaml
id: "D-{N}"                           # existing prefix; single-namespace across Cat 1–10
category: "data-poisoning"            # existing enum value — unchanged
title: "{Cat 8: Transfer Learning Supply Chain | Cat 9: Feedback-Loop Model Skewing | Cat 10: Predictive-ML Supply Chain Completeness}: {short_summary}"
severity: "medium" | "high"           # Cat 8/9/10 default HIGH (training-pipeline integrity)
component: "{DFD Process | Data Store — fine-tuning step | active-learning loop | dataset repository | feature store | MLOps registry}"
description: "{2-4 sentence threat description}"
mitigation: "{ML-specific control mechanisms — signed-weight-artifact policy / labeler-trust scoring / signed-artifact registry IAM / etc.}"
references:
  - "OWASP ML07:2023 — Transfer Learning Attack"  # Cat 8 REQUIRED
  - "OWASP ML08:2023 — Model Skewing"             # Cat 9 REQUIRED
  - "OWASP ML06:2023 — AI Supply Chain Attacks"   # Cat 10 REQUIRED (corpus-side facet)
  - "MITRE ATLAS AML.T0018 — Backdoor ML Model"   # Cat 8 catalog-resolvable
  - "MITRE ATLAS AML.T0020 — Poison Training Data"  # Cat 9 catalog-resolvable
  - "MITRE ATT&CK T1195 — Supply Chain Compromise"  # Cat 10 catalog-resolvable (T1195.001 + T1195.002 sub-techniques)
  # MITRE ATLAS AML.T0019 named in Cat 8 mitigation prose only — NOT in references (catalog-absent)
  # MITRE ATLAS AML.T0031 named in Cat 9 mitigation prose only — NOT in references (catalog-absent)
```

**Contract summary (model-theft Cat 12/13/14)**:

```yaml
id: "LLM-{N}"                         # existing prefix shared with prompt-injection / output-integrity / misinformation; single-namespace within model-theft across Cat 1–14
category: "llm"                       # existing enum value — unchanged
title: "{Cat 12: Model Inversion | Cat 13: Membership Inference | Cat 14: Predictive-ML Artifact Supply Chain}: {short_summary}"
severity: "medium" | "high"           # Cat 12/13 default MEDIUM-HIGH; Cat 14 default HIGH (artifact integrity at promotion gate)
component: "{DFD Process — prediction API | model registry | weight artifact storage}"
description: "{2-4 sentence threat description distinguishing predictive-ML extraction from LLM-tier extraction (Cat 1-9)}"
mitigation: "{predictive-ML-specific control mechanisms — DP-SGD / output-perturbation / confidence-truncation / model-signing / etc.}"
references:
  - "OWASP ML03:2023 — Model Inversion Attack"           # Cat 12 REQUIRED
  - "OWASP ML04:2023 — Membership Inference Attack"      # Cat 13 REQUIRED
  - "OWASP ML06:2023 — AI Supply Chain Attacks"          # Cat 14 REQUIRED (artifact-side facet)
  - "MITRE ATLAS AML.T0024 — Exfiltration via ML Inference API"  # Cat 12 + Cat 13 catalog-resolvable (shared but disjoint architectural-tells)
  - "MITRE ATT&CK T1195 — Supply Chain Compromise"       # Cat 14 catalog-resolvable
```

**Predictive-ML topology gate** (FR-016 enforcement contract): every Cat 10 (T) + Cat 8/9/10 (D) + Cat 12/13/14 (LLM) finding emits ONLY when the architecture additionally exhibits ≥1 predictive-ML topology indicator from the named set: declared training pipeline, MLOps registry (MLflow / SageMaker Model Registry / Vertex AI Model Registry / custom), feature store (Feast / Tecton / S3-backed), fine-tuning step on pretrained weights from public registry (HuggingFace Hub / TensorFlow Hub / PyTorch Hub), active-learning feedback loop, prediction-API endpoint serving classifier/regressor with no input-validation barrier, model-deployment artifact (`.pkl` / `.pt` / `.h5` / `.onnx` / `SavedModel` / `.bin`), weight checkpoint storage with no signed-artifact policy. Architectures lacking predictive-ML topology emit zero new findings (BLOCKER per FR-016 + SC-018 byte-identity preservation).

### Data Model (`data-model.md`)

**Purpose**: Document the architectural-tell indicators that drive Cat 10 (T) + Cat 8/9/10 (D) + Cat 12/13/14 (LLM) emission. See [data-model.md](./data-model.md).

**Pattern Category 10 (tampering) — Adversarial Input Manipulation indicators**:
- Deployed predictive ML classifier (Process)
- Inference endpoint with no input-validation barrier (Data Flow)
- Missing adversarial-defense controls (no adversarial training, no statistical anomaly detection, no distribution-shift monitoring)
- Confidence-thresholding HITL escalation absent
- Ensemble disagreement detection absent

**Pattern Category 8 (data-poisoning) — Transfer Learning Supply Chain indicators**:
- Fine-tuning step on pretrained weights from public registry (HuggingFace Hub, TensorFlow Hub, PyTorch Hub)
- Weights pulled without checksum verification or signed-artifact policy
- Missing provenance metadata on pretrained weight artifacts
- Adapter (LoRA, etc.) merged without integrity verification
- Fine-tuning hash-pinning absent
- Model-card provenance review missing

**Pattern Category 9 (data-poisoning) — Feedback-Loop Model Skewing indicators**:
- Active-learning pipeline reading production data back into training
- HITL labeling tool with attacker-controlled labelers (no labeler-trust scoring)
- Online-learning drift injection from inference inputs
- Recommendation-system feedback loop with no tamper-detection on clickstream
- Drift-detection alarms missing on production inference distributions
- Periodic retraining-data audit with held-out canaries absent

**Pattern Category 10 (data-poisoning) — Predictive-ML Supply Chain Completeness indicators**:
- Dataset repository (Kaggle, public corpus) with no integrity verification
- Feature store (Feast, Tecton, S3-backed) with no IAM-enforced write-audit
- MLOps model registry (MLflow, SageMaker, Vertex AI) with no signed-artifact policy
- Missing model-card or datasheet metadata
- Dataset-checksum manifest absent
- Promotion-gate review missing

**Pattern Category 12 (model-theft) — Model Inversion indicators**:
- Prediction API serving classifier with sensitive training data (face-recognition, medical-imaging, tabular-PII)
- No DP-SGD on training (differential privacy with bounded ε absent)
- Output-perturbation noise injection absent at inference time
- Query-rate throttling per tenant absent
- Model-extraction-pattern detection (anomalous query distributions) absent
- White-box gradient access available to untrusted users

**Pattern Category 13 (model-theft) — Membership Inference indicators**:
- Prediction API returning confidence values (high-confidence = likely member)
- Shadow-model attack feasibility (training data publicly known or inferrable)
- Label-only response mode missing for sensitive endpoints
- DP-SGD absent
- Confidence-output truncation absent
- Training-data minimization not enforced

**Pattern Category 14 (model-theft) — Predictive-ML Artifact Supply Chain indicators**:
- MLOps model registry (MLflow, SageMaker, Vertex AI) with no signed-artifact policy
- Weight tampering surface between training and serving (mutable artifact storage)
- Missing model-signing or attestation policy (no Sigstore-style or KMS-backed)
- Registry IAM with promotion-gate review absent
- Integrity verification at model-load time absent
- Audit logging on artifact mutations absent

### Quickstart (`quickstart.md`)

**Purpose**: Walk through verifying F-6 enrichment on the new `examples/predictive-ml-app/` architecture and confirming byte-identity on the 6 non-predictive-ML baselines. See [quickstart.md](./quickstart.md).

**Verification flow**:

1. **Plan day** (Tuesday 2026-04-28): Architect + senior-backend-engineer co-author `examples/predictive-ml-app/architecture.md` exhibiting all 5 predictive-ML topology indicators. ADR-035 Proposed at Day 1 AM.
2. **Wave 1**: Land FR-1 + FR-2 (`tampering.md` + companion: 1 new pattern category Cat 10) + ADR-035 Proposed with 8-row mapping table populated COMPLETE (NOT skeleton).
3. **Wave 2**: Land FR-5 + FR-6 (`data-poisoning.md` + companion: 3 new pattern categories Cat 8 + 9 + 10) — densest authoring slot; per team-lead MEDIUM-2 broken into 3 sequential category-by-category checkpoints (T-NN-1 / T-NN-2 / T-NN-3) at ~90 minutes each with rollback capability.
4. **Wave 3**: Land FR-8 + FR-10 (`model-theft.md` + companion: 3 new pattern categories Cat 12 + 13 + 14) — second-densest authoring slot; integration checkpoint with F-5's Cat 11 (visual continuity Cat 10 → 11 → 12 → 13 → 14).
5. **Wave 4 AM**: Tester engages for early-signal byte-identity spot-check on 1–2 baselines (e.g., `web-app` + `maestro-reference`) per FR-025 / team-lead MEDIUM-3.
6. **Wave 4 PM**: Architect + senior-backend-engineer regenerate `examples/predictive-ml-app/` end-to-end via `/tachi.threat-model` → `/tachi.risk-score` → `/tachi.compensating-controls` → `/tachi.infographic all` → `/tachi.security-report`. Verify ≥6 new ML findings (≥1 per host agent).
7. **Wave 5 AM-1**: Tester runs full byte-identity verification across 6 baselines per FR-025 + SC-018.
8. **Wave 5 AM-2**: Architect transitions ADR-035 Proposed → Accepted with post-merge SHA fill.
9. **Wave 5 PM**: Triad sign-offs on tasks.md (PM + Architect + Team-Lead) + close-out per `/aod.deliver` + Coverage Matrix update (FR-023 single commit) + delivery retrospective filing per FR-026.

**Verification gates**:

- `wc -l .claude/agents/tachi/{tampering,data-poisoning,model-theft}.md` — all three within tier caps (120 / 150 / 150)
- `git diff main HEAD -- '.claude/agents/tachi/' '.claude/skills/tachi-*/references/'` — exactly 6 files in diff
- `grep -i 'maestro' .claude/agents/tachi/{tampering,data-poisoning,model-theft}.md .claude/skills/tachi-{tampering,data-poisoning,model-theft}/references/detection-patterns.md` — 0 matches (FR-015 / SC-024)
- `grep -c "## Pattern Category Disambiguation" .claude/skills/tachi-{tampering,data-poisoning,model-theft}/references/detection-patterns.md` — 3 matches (FR-011 / SC-014)
- `grep -E '^schema_version:' schemas/finding.yaml` — `"1.8"` (FR-017 / SC-022)
- `grep -E '^\s+pattern:' schemas/finding.yaml` — `^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\\d+$` unchanged (FR-017 / SC-022)
- `pytest tests/scripts/test_backward_compatibility.py -k "byte_identity" -v` — 6/6 passing (FR-016 / SC-018)
- `pytest tests/scripts/test_ml_top_10_coverage_bundle_enrichment.py -v` — all enrichment tests passing
- `git diff main HEAD -- examples/predictive-ml-app/sample-report/security-report.pdf.baseline` — present (new mutation target baseline)
- `git diff main HEAD -- examples/agentic-app/` — empty (architect MEDIUM-2: agentic-app zero-touch)
- `git diff main HEAD -- examples/consumer-agent-app/` — empty (F-4 mutation target untouched)

### Wave Allocation

| Wave | Day/Slot | Owner | Task | Cumulative State |
|------|----------|-------|------|------------------|
| 0.0 | Tue 2026-04-28 PM | architect + senior-backend-engineer | New `examples/predictive-ml-app/architecture.md` co-authoring (Q1 RESOLVED; ~4-6 hours; ~150-200 lines) | New mutation target ready |
| 1.0 | Wed 2026-04-29 AM | architect | ADR-035 Proposed commit with 8-row mapping table populated COMPLETE (NOT skeleton); 9-10 numbered Decisions including ML06 two-facet (D-4) + ML03/ML04 disjoint tells (D-5) + Pattern Category Disambiguation requirement (D-9); cross-references ADR-023/030/032/034 | ADR-035 Proposed |
| 1.1 | Wed 2026-04-29 AM | senior-backend-engineer | FR-001 + FR-002 + FR-003: `tampering.md` 3 small additive edits (owasp_references, Purpose, Step 5) — 51 → 54-58 lines; FR-004: `tachi-tampering` companion Cat 10 + Pattern Category Disambiguation + Primary Sources extension — 190 → ~240-260 lines; FR-012 partial: tampering Primary Sources entry | tampering enrichment complete |
| 2.0 | Wed 2026-04-29 PM | senior-backend-engineer | FR-005 + FR-006: `data-poisoning.md` 3 small additive edits (owasp_references 7-line, Purpose, Step 5) — 78 → 84-90 lines | data-poisoning agent metadata complete |
| 2.1 | Wed 2026-04-29 PM | senior-backend-engineer | FR-007 PART 1 + team-lead MEDIUM-2 checkpoint T-NN-1: Cat 8 (Transfer Learning Supply Chain) land + self-review (~30 lines) | data-poisoning Cat 8 complete |
| 2.2 | Wed 2026-04-29 PM | senior-backend-engineer | FR-007 PART 2 + team-lead MEDIUM-2 checkpoint T-NN-2: Cat 9 (Feedback-Loop Model Skewing) land + self-review (~30 lines) | data-poisoning Cat 9 complete |
| 2.3 | Wed 2026-04-29 PM | senior-backend-engineer | FR-007 PART 3 + team-lead MEDIUM-2 checkpoint T-NN-3: Cat 10 (Predictive-ML Supply Chain Completeness) land + self-review (~30 lines) + Pattern Category Disambiguation subsection + 3 Primary Sources entries | data-poisoning enrichment complete (137 → ~290-330 lines) |
| 3.0 | Thu 2026-04-30 AM | senior-backend-engineer | FR-008 + FR-009: `model-theft.md` 3 small additive edits (owasp_references 4-line, Purpose, Step 5) — 97 → 103-108 lines | model-theft agent metadata complete |
| 3.1 | Thu 2026-04-30 AM | senior-backend-engineer | FR-010: `tachi-model-theft` companion Cat 12 (Model Inversion) + Cat 13 (Membership Inference) + Cat 14 (Predictive-ML Artifact Supply Chain) + Pattern Category Disambiguation subsection (Cat 12/13/14 vs Cat 1-11 including F-5's Cat 10/11) + 3 Primary Sources entries — 211 → ~360-400 lines | model-theft enrichment complete |
| 3.2 | Thu 2026-04-30 AM | architect | Integration walkthrough: Cat 10 → 11 → 12 → 13 → 14 visual continuity check (model-theft companion, post-F-5 + post-F-6) | Integration verified |
| 4.0 | Thu 2026-04-30 PM | senior-backend-engineer | `examples/predictive-ml-app/` end-to-end regen: `/tachi.threat-model` → `/tachi.risk-score` → `/tachi.compensating-controls` → `/tachi.infographic all` → `/tachi.security-report` | predictive-ml-app baseline + all artifacts |
| 4.1 | Thu 2026-04-30 PM | tester (per FR-025 / team-lead MEDIUM-3) | Early-signal byte-identity spot-check on 1–2 baselines (`web-app` + `maestro-reference` recommended) | Early-signal spot-check passed |
| 5.0 | Fri 2026-05-01 AM-1 | tester (per FR-025) | Full byte-identity verification across 6 baselines under `SOURCE_DATE_EPOCH=1700000000` per ADR-021 | SC-018 verified 6/6 |
| 5.1 | Fri 2026-05-01 AM-2 | architect | ADR-035 Accepted transition + post-merge SHA fill (provisional date pre-merge; final SHA post-merge per FR-026) | ADR-035 Accepted |
| 5.2 | Fri 2026-05-01 AM | senior-backend-engineer | New test file `tests/scripts/test_ml_top_10_coverage_bundle_enrichment.py` with structural-diff + line-count + MAESTRO grep + Pattern Category Disambiguation header presence + references-array fixtures (7 fixtures: Cat 10 T + Cat 8/9/10 D + Cat 12/13/14 LLM); modify `test_backward_compatibility.py` infrastructure (`DETECTION_AGENT_PATHS` 10 → 8; `DETECTION_PATTERN_REF_ENRICHMENT_HOSTS` 5 → 7) | Test infrastructure complete |
| 5.3 | Fri 2026-05-01 PM | senior-backend-engineer | FR-023: BLP-01 Coverage Matrix six-row update (ML01/03/04/07/08 Planned → Covered, ML06 Partial → Covered, F-6 closure-feature column populated; coverage milestones panel update) — single commit per F-3/F-4/F-5 precedent | Coverage Matrix transitioned |
| 5.4 | Fri 2026-05-01 PM | product-manager + architect + team-lead | Triple Triad sign-offs on tasks.md per `/aod.tasks` | Triple sign-off recorded |
| 5.5 | Fri 2026-05-01 PM | senior-backend-engineer + architect | `/aod.deliver` close-out: pre-merge title verification + squash-merge with `feat(232):` Conventional Commits title + post-merge release-please verification + delivery retrospective filing per FR-026 (or buffer day Mon 2026-05-04 if residual capacity insufficient) | F-6 delivered |
| 5.6 (buffer) | Mon 2026-05-04 | — | Slip absorption / regen friction / delivery retrospective filing fallback / R5 contingency invocation if triggered (deferral pair = data-poisoning Cat 10 + model-theft Cat 14 per spec OoS-15) | Buffer reserved |

**Wave parallelism notes**: Wave 1.1 + Wave 2.x + Wave 3.x are sequential (single-engineer fan-out — three agents in one half-day each would risk authoring quality). Wave 4.0 (regen) and Wave 4.1 (tester spot-check) are weakly parallel (tester can begin spot-check on 1–2 baselines before regen of `predictive-ml-app/` completes). Wave 5.0 (full verification) and Wave 5.1 (ADR-035 SHA fill) are strongly parallel per team-lead LOW-1 Day 3 AM split annotation.

**Buffer-day priority order** (per team-lead recommendations): (1) Day 2 / Day 3 slip absorption; (2) delivery retrospective filing if Day 3 PM slot insufficient; (3) post-merge ADR-035 SHA fill + `/aod.deliver` execution + release-please PR verification; (4) F-7 PRD drafting NOT until F-6 deliver-stage closes.

## Complexity Tracking

*No Constitution Check violations. No Complexity Tracking entries required.*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | (none) | (none) |

---

## Plan-Day Architect Decisions Summary

For traceability and reviewer cross-reference, the architect plan-day decisions resolved during /aod.project-plan:

| Decision | Default | Plan-Time Decision | Rationale |
|----------|---------|---------------------|-----------|
| Q2 (ML06 mapping table column structure: 1 row vs 2 rows) | 2 rows | **2 ROWS** | Disjoint architectural-tells per architect MEDIUM-4 demand explicit ML06-corpus + ML06-artifact rows |
| Q3 (ATLAS catalog-resolvability for 6 entries) | RESOLVE at plan time | **3 of 6 catalog-resolvable** (T0018, T0020, T0024); 3 of 6 absent (T0015, T0019, T0031) | Empirical grep on `schemas/taxonomy/mitre-atlas.yaml` — 3x F-5 T1496 prose-only precedent scale |
| Q4 (data-poisoning Cat 10 granularity: single vs 2-3 finer-grained) | Single category | **SINGLE CATEGORY** | Indicator surface (5+ indicators) supports cohesion; ADR-035 D-4 ML06 two-facet split already disambiguates corpus vs artifact |
| Q6 (ADR-035 mapping-table column structure: severity-hint column) | YES (parity with ADR-034) | **YES** | ADR-035 mapping table includes severity-hint annotation column for parity + cross-feature comparability |
| Architect MEDIUM-3 (Pattern Category Disambiguation requirement) | DEFERRED to plan day | **ENCODED** as FR-011 / SC-014 (3 instances per FR-011) + ADR-035 D-9 | Mirrors F-3 ADR-032 D7 + F-5 ADR-034 D7 precedent at three-agent scale |
| Architect MEDIUM-4 (ML06 two-facet disjoint architectural-tells) | DEFERRED to plan day | **ENCODED** as ADR-035 D-4 with explicit corpus-side / artifact-side ownership | Promotes from R4 mitigation to D-numbered decision |
| Architect MEDIUM-5 (ML03 vs ML04 disjoint architectural-tells) | DEFERRED to plan day | **ENCODED** as ADR-035 D-5 with white-box-gradient-inversion vs confidence-thresholding-shadow-model carve | Both share AML.T0024 but architectural-tells distinguishable |
| Team-Lead MEDIUM-1 (R5 deferral pair pre-naming) | DEFERRED to plan day | **PRE-NAMED** as data-poisoning Cat 10 + model-theft Cat 14 (both ML06 facets) | Spec OoS-15 + plan Wave 5.6 buffer reserved |
| Team-Lead MEDIUM-2 (Day 1 PM category-by-category checkpoints) | DEFERRED to tasks.md | **WAVES 2.1 / 2.2 / 2.3** (T-NN-1 / T-NN-2 / T-NN-3) | Three sequential ~90-minute checkpoints with rollback capability |
| Team-Lead MEDIUM-3 (Day 2 PM tester engagement explicit) | DEFERRED to plan day | **ENCODED** as FR-025 + Wave 4.1 (tester engages) | SC-018 owner separation preserved across F-3/F-4/F-5/F-6 |
| Team-Lead LOW-1 (Day 3 AM split annotation) | DEFERRED to tasks.md | **ENCODED** as Wave 5.0 (tester) + Wave 5.1 (architect) split | Two activities don't share single slot owner |
