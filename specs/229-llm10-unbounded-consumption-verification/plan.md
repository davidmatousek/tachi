---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-27
    status: APPROVED
    notes: "High-fidelity translation of approved PRD/spec. All 22 spec FRs and all 22 spec SCs explicitly wave-mapped. 3 P0 user stories AC-level operationalized: US-229-1 (full LLM10 surface) via Wave 1.1 + Wave 2 four-file additive edits + Wave 2 example regen; US-229-2 (LLM-specific mitigation naming) via Wave 1.1 + Wave 2 mitigation-text authoring on Cat 12/13/10/11; US-229-3 (audit-confirmed additive transition with mapping table) via Wave 1.1 ADR-034 Proposed with 5-row mapping table populated complete + Wave 4 Coverage Matrix update. Q1 SPLIT cross-agent vector decomposition (Cat 13 latency-DoS Vector A in DoS / Cat 11 cost-DoW Vector B in model-theft) operationalized via ADR-034 Decision 3 audit table + Cat 13/11 worked-example scope notes. Q3 severity (HIGH default + 2-condition CRITICAL floor on Cat 11 multi-tenant freemium) encoded in finding-contract + Cat 11 worked-example narrative. Q4 4-categories total preserved at plan time (no merge — indicator surface + Q1 SPLIT justify distinct categories per host). Q5 example target `examples/agentic-app/` preserved. Q2 plan-day default-NO (zero functional dispatch-tier touches preserved). Heuristic A second-execution at two-agent scope narrative preserved end-to-end. Zero scope creep — F-5 stays purely additive. Conventional Commits PR title contract (FR-022/SC-022) and delivery retrospective (SC-022 / DoD bullet 15) wave-mapped to Wave 4. Day 1 / Day 2 split rebalanced per team-lead MEDIUM-1 (ADR-034 mapping table populated COMPLETE at Wave 1.1 — NOT skeleton); tester role for SC-014 explicit (team-lead MEDIUM-2); buffer-day priority order enumerated (team-lead MEDIUM-3). 0 BLOCKING / 0 HIGH / 0 MEDIUM / 2 LOW (stylistic only). PM APPROVES for /aod.tasks. Full review: .aod/results/product-manager.md."
  architect_signoff:
    agent: architect
    date: 2026-04-27
    status: APPROVED
    notes: "10/10 review dimensions PASS. All ground-truth claims independently verified at plan time: denial-of-service.md=53 lines, model-theft.md=95 lines + owasp_references already includes LLM10, DoS companion=179 lines hybrid heading no Trigger Keywords, model-theft companion=154 lines uniform headings + Trigger Keywords line 19, schema_version=1.8 with id.pattern unchanged (D + LLM enumerated), ADR-034 free, all 4 catalog citations resolve (LLM10 line 373 / LLM03 / CWE-400 line 130 / CWE-770 line 182), T1496 absent (prose-only), finding-format-shared.md lines 12 + 16 already contain both agents, dispatch-rules.md line 73 has model-theft LLM10 annotation but DoS lacks one (Q2 default-NO confirmed), 0 MAESTRO refs in all 4 target files. Plan correctly: (1) honors ADR-023 lean-agent + Decision 3 additive-only edits; (2) preserves byte-identity on Cat 1-11 (DoS) + Cat 1-9 (model-theft) (SC-008 + SC-010 BLOCKERs); (3) reuses D + LLM prefixes without schema bump (second BLP-01 detection feature with no schema bump after F-3, first at two-agent scope); (4) preserves 24-file zero-edit invariant on remaining 24 of 28 detection-tier files; (5) F-A3 deferral correct — F-5 cites LLM10 in references array only, source_attribution populator wiring deferred; (6) Heuristic A rationale at two-agent scope via ADR-030 D1 + ADR-031 D8 (asymmetry — F-5 does NOT invoke) + ADR-032 lines 84+182 forecast + ADR-033 D2 (structural sibling) cross-refs valid; (7) topology gate (FR-015) does correctness + byte-identity double-duty under SOURCE_DATE_EPOCH; (8) Pattern Category Disambiguation DoS Cat 9 vs Cat 12/13 + model-theft Cat 6 vs Cat 10/11 in ADR-034 Decision 7; (9) 6 non-LLM-serving baselines byte-identical via topology gate; (10) zero new dependencies. Q1 SPLIT cross-agent vector decomposition cleanly executed; Q3 severity 2-condition CRITICAL floor encoded in Cat 11 worked example + ADR-034 Decision 3 audit-table annotation column. Q2 plan-day decision: default-NO confirmed (zero functional dispatch-tier touches preserved). 0 BLOCKING / 0 HIGH / 0 MEDIUM / 2 LOW (advisory only). Architect APPROVES for /aod.tasks. Full review: .aod/results/architect.md."
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: LLM10 Unbounded Consumption Verification (OWASP LLM10:2025)

**Branch**: `229-llm10-unbounded-consumption-verification` | **Date**: 2026-04-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/229-llm10-unbounded-consumption-verification/spec.md`
**PRD**: [docs/product/02_PRD/229-llm10-unbounded-consumption-verification-2026-04-27.md](../../docs/product/02_PRD/229-llm10-unbounded-consumption-verification-2026-04-27.md)
**BLP-01 Phase**: Tier 1 F-5 — fifth Tier 1 closure feature; **second execution** of the Heuristic A **enrichment** branch (after F-3 single-agent scope) and the **first at two-agent scope**; closes LLM10:2025 Partial → Covered, completing OWASP LLM Top 10 = 10/10 Covered milestone

## Summary

Enrich the existing `denial-of-service` STRIDE-tier and `model-theft` AI-tier threat agents to close OWASP LLM10:2025 detection gap via Heuristic A consolidation at **two-agent scope**. **No new agent file, no new skill directory, no schema bump, no consumers-list edit, no functional orchestrator/dispatch edit, no `source_attribution` populator wiring extension.** Net change is **purely additive** to four existing files plus one new ADR-034: (1) `denial-of-service.md` metadata `owasp_references += [OWASP LLM10:2025]`, `## Purpose` 1–3 line extension, Detection Workflow Step 5 references += `OWASP LLM10:2025` exemplar mention; (2) `tachi-denial-of-service/references/detection-patterns.md` appends Pattern Category 12 (LLM Inference-Request Flooding and Token Exhaustion) + Pattern Category 13 (Context-Window Exhaustion — Latency-Driven Variant — Q1 SPLIT Vector A) after Cat 11, plus Primary Sources extension; (3) `model-theft.md` `owasp_references` audit-confirmed (LLM10 already present — zero net change), `## Purpose` 1–3 line extension; (4) `tachi-model-theft/references/detection-patterns.md` appends Pattern Category 10 (Cost Amplification via Recursive or Cost-Asymmetric Prompting) + Pattern Category 11 (Denial-of-Wallet via Context-Window Cost Amplification — Q1 SPLIT Vector B + broader DoW) after Cat 9, plus Primary Sources extension; (5) public ADR-034 documenting the Heuristic A enrichment pattern at two-agent scope as operational precedent (Proposed → Accepted dual-commit per ADR-027/028/029/030/031/032/033 lineage). Findings emit with existing `D-{N}` prefix (DoS) and `LLM-{N}` prefix (model-theft) and existing `category: denial-of-service` / `category: llm` enum values; each Cat 12/13 + Cat 10/11 finding cites OWASP LLM10:2025 in its prose-level `references:` array (existing finding-YAML field since v1.0; F-5 does NOT extend `source_attribution` populator wiring — that scope belongs to F-A3).

**Architectural approach**: Apply ADR-023 Decision 3 additive-only edit discipline. Existing prose in `denial-of-service.md` and `model-theft.md` `## Purpose` sections + Cat 1–11 (DoS) + Cat 1–9 (model-theft) + `## Overview` + `## Targeted DFD Element Types` + `## Trigger Keywords` (model-theft companion only) + `## Primary Sources` (existing entries) remain **byte-identical** pre/post edit (grep-checkable). PRD-resolved Q1 SPLIT (cross-agent vector decomposition of context-window exhaustion: Vector A latency-DoS in DoS Cat 13 / Vector B cost-DoW in model-theft Cat 11) and Q3 severity (HIGH default for Cat 10/11 + 2-condition CRITICAL floor on Cat 11 multi-tenant freemium) operationalized via ADR-034 Decision 3 5-row mapping table with severity-hint annotation column. The enriched agents activate as they do today on Process / Data Store / Data Flow components matching existing trigger keywords; new Pattern Categories fire only on architectures additionally exhibiting LLM-serving topology indicators (the LLM-serving topology gate ensures byte-identity on the 6 non-LLM-serving baselines).

**Touch points**: 0 new agent files, 0 new skill directories, 0 schema edits, 0 functional dispatch edits, 0 consumers-list edits, 0 `source_attribution` populator wiring extensions, 0 new runtime dependencies. **4 additive file edits** (`denial-of-service.md`, DoS companion, `model-theft.md`, model-theft companion) + **1 new ADR** (ADR-034 with 5-row mapping table) + **1 example regeneration** (`examples/agentic-app/` per Q5 RESOLVED) + **1 optional cosmetic annotation** (`dispatch-rules.md` `denial-of-service` entry → `denial-of-service (..., LLM10)` for parity with model-theft's existing LLM10 annotation per PRD Q2 default-NO architect-tractable). **F-5 surface is ~2× F-3's pattern-authoring surface but smaller than F-2's full new-agent shape.**

## Technical Context

**Language/Version**: Markdown + YAML + Python 3.11 (existing — stdlib + `pyyaml`); agent and skill content files, not executable code
**Primary Dependencies**: `pyyaml` (runtime, already declared), `pytest` (dev-only, already declared per Feature 128 precedent); **no new runtime or dev dependencies**
**Storage**: File-based; reads `schemas/finding.yaml` (v1.8, **no edit**), `schemas/taxonomy/{owasp,cwe}.yaml` (F-A1 catalogs, read-only for `references` validation); writes only to `.claude/agents/tachi/denial-of-service.md`, `.claude/agents/tachi/model-theft.md`, `.claude/skills/tachi-denial-of-service/references/detection-patterns.md`, `.claude/skills/tachi-model-theft/references/detection-patterns.md`, `docs/architecture/02_ADRs/ADR-034-llm10-unbounded-consumption-audit.md`, `examples/agentic-app/` (Q5 RESOLVED)
**Testing**: pytest (existing harness at `tests/scripts/`) + backward-compatibility test `tests/scripts/test_backward_compatibility.py` under `SOURCE_DATE_EPOCH=1700000000` per ADR-021 — **6 non-LLM-serving baselines** byte-identity gate (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`); structural-diff tests on Cat 1–11 (DoS) + Cat 1–9 (model-theft) byte-identity in both companions; line-count tests on `denial-of-service.md` (≤120) + `model-theft.md` (≤150); MAESTRO grep tests on all four enriched files; references-array assertion tests on Cat 12/13 + Cat 10/11 fixture findings (LLM10 + CWE-400 + CWE-770 + LLM03 catalog-resolvable; T1496 prose-only)
**Target Platform**: Command-line Python tooling (macOS/Linux/WSL); orchestrator + threat agents invoked via `/tachi.threat-model` Claude command; PDF rendering via Typst + Mermaid CLI (unchanged)
**Project Type**: Single project (methodology toolkit — agents + skills + schemas + templates in a unified repo); no frontend/backend split
**Performance Goals**: Agent invocation latency unchanged. Two new Pattern Categories per host add O(2 additional pattern matches per host dispatch); empirical impact <1ms per architecture file. No new performance regressions.
**Constraints**: (a) SC-008 byte-identity on Cat 1–11 (DoS) + `## Overview` + `## Targeted DFD Element Types` + `## Primary Sources` (existing entries) in DoS companion is a BLOCKER (note: DoS companion lacks `## Trigger Keywords` section, asymmetric to model-theft companion); (b) SC-010 byte-identity on Cat 1–9 (model-theft) + `## Overview` + `## Targeted DFD Element Types` + `## Trigger Keywords` (line 19) + `## Primary Sources` (existing entries) in model-theft companion is a BLOCKER; (c) SC-014 byte-identity on **6 non-LLM-serving example PDFs** under `SOURCE_DATE_EPOCH=1700000000` is a BLOCKER; (d) SC-002 line-count cap ≤120 on `denial-of-service.md` is a BLOCKER (PRD-time + plan-time baseline 53; expected post-edit 56–60); (e) SC-005 line-count cap ≤150 on `model-theft.md` is a BLOCKER (PRD-time + plan-time baseline 95; expected post-edit 98–102); (f) SC-017 24-file zero-edit invariant on every detection-tier file other than the four F-5 enrichment targets is a BLOCKER (post-F-4 inventory: 28 detection-tier files; F-5 edits 4; the remaining 24 stay byte-identical); (g) SC-018 schema invariant — `schemas/finding.yaml` `schema_version` MUST remain `"1.8"` (BLOCKER); (h) SC-019 `references:` array must include LLM10 + CWE-400 (Cat 12/13) and LLM10 (Cat 10/11) at minimum on every emitted new finding (BLOCKER); (i) SC-020 zero MAESTRO references in all four enriched files (grep-auditable, BLOCKER); (j) FR-015 LLM-serving topology gate (correctness BLOCKER) — Cat 12/13 + Cat 10/11 emit zero findings on architectures lacking LLM-serving indicators
**Scale/Scope**: 0 new agent files; 0 new skill directories; 4 file edits (~5–10 lines additive on `denial-of-service.md`; ~5 lines additive on `model-theft.md`; ~140–180 lines additive on DoS companion; ~140–180 lines additive on model-theft companion); 4 new Pattern Categories total (Cat 12 + Cat 13 in DoS companion; Cat 10 + Cat 11 in model-theft companion) with ≥4 indicators each, ≥1 worked example each, named LLM-specific mitigations; 1 new ADR (~280–400 lines including 5-row mapping table); 1 example regeneration (`examples/agentic-app/` per Q5 RESOLVED). **Edit surface is structurally between F-3 (single-agent enrichment, 1d) and F-2 (full new-agent shape, 2d). Realistic envelope: 1.5 working days.**

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Evaluated against `.aod/memory/constitution.md`:

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | PASS | Pattern Categories 12/13 (DoS) and 10/11 (model-theft) detect generic LLM-serving infrastructure resource-exhaustion + cost-amplification + denial-of-wallet signal classes; no hardcoded project-type assumptions; works on any architecture exhibiting LLM-serving topology indicators |
| II. API-First Design | N/A | No REST/GraphQL surface; threat agents are content files consumed by the orchestrator at invocation time |
| III. Backward Compatibility (NON-NEGOTIABLE) | PASS | LLM-serving topology gate (FR-015) ensures byte-identity on 6 non-LLM-serving baselines. Schema unchanged; existing D-{N} and LLM-{N} findings remain valid. Local `.aod/` workflows unaffected. **No schema bump means even the schema-version-pinning surface is byte-identical** — F-5 is the second BLP-01 detection feature with zero schema-tier impact (after F-3) and the first at two-agent enrichment scope. |
| IV. Concurrency & Data Integrity | N/A | F-5 is single-invocation content authoring; no concurrent state |
| V. Privacy & Data Isolation | PASS | Worked examples use clearly-fictional scenarios (multi-tenant LLM-serving SaaS with `/v1/completions` endpoint, consumer chatbot with adversarial conversation history, RAG advisory assistant with recursive prompt); no PII, no adopter data, no network calls by the agent |
| VI. Testing Excellence (MANDATORY) | PASS | Structural-diff tests on Cat 1–11 (DoS) + Cat 1–9 (model-theft) byte-identity; line-count tests on both agent files; MAESTRO grep test on all four enriched files; references-array assertion tests for Cat 12/13 + Cat 10/11 fixture findings; backward-compat byte-identity gate on 6 non-LLM-serving baselines (per team-lead MEDIUM-2: explicit `tester` agent ownership separate from `senior-backend-engineer`) |
| VII. Definition of Done (NON-NEGOTIABLE) | PASS | Spec-defined SCs (SC-001 through SC-022) map to grep-checkable / wc-checkable / byte-identity predicates. SC-008 + SC-010 + SC-014 + SC-017 + SC-018 + SC-019 + SC-020 are BLOCKER-level gates. DoD bullet 15 (delivery retrospective at SC-022) carried via Day 2 buffer-day slot per team-lead MEDIUM-3 priority order. DoD bullet 16 (ADR-034 SHA-fill) carried via post-merge protocol per team-lead LOW-2 |
| VIII. Product-Spec Alignment | PASS | Approved PRD 229 exists (PM APPROVED, Architect APPROVED_WITH_CONCERNS — 12/12 v2 findings RESOLVED, Team-Lead APPROVED_WITH_CONCERNS — 5 findings absorbed); spec.md has PM APPROVED sign-off (0 BLOCKING / 0 HIGH / 0 MEDIUM / 1 LOW) |
| IX. Git Workflow | PASS | Feature branch `229-llm10-unbounded-consumption-verification` created; draft PR will be opened with `feat(229):` Conventional Commits title at `/aod.project-plan` close; no main commits; ADR-034 Proposed → Accepted dual-commit pattern |
| X. Zero-Edit Invariant (ADR-023 lineage) | PASS | FR-018 / SC-017 explicit; 24-file invariant covers 12 other threat agents + 12 other companion `detection-patterns.md` files (post-F-4 inventory: 28 detection-tier files; F-5 edits 4 host files; 24 stay byte-identical). FR-017 / SC-017 also enforce zero edit to `finding-format-shared.md` consumers list. FR-019 / SC-021 enforces zero functional edit to orchestrator dispatch tier (cosmetic Q2 annotation carve-out is documentation-only). FR-020 enforces zero `source_attribution` populator wiring extension on host agents (deferred to F-A3). |

**Gate verdict**: No violations. No Complexity Tracking entries required.

## Project Structure

### Documentation (this feature)

```
specs/229-llm10-unbounded-consumption-verification/
├── plan.md                  # This file (/aod.project-plan output)
├── research.md              # Phase 0 output (populated by /aod.spec)
├── data-model.md            # Phase 1 output — Pattern Category 10/11/12/13 shape + LLM-serving topology gate + finding shape
├── contracts/
│   └── finding-contract.md  # Finding IR contract for Cat 12/13 D-{N} and Cat 10/11 LLM-{N} findings (references-array + mitigation rules; Q3 severity-hint conditional)
├── quickstart.md            # Phase 1 output — verification walkthrough
├── spec.md                  # PM-approved spec
└── tasks.md                 # Task breakdown (/aod.tasks output)
```

### Source Code (repository root)

```
tachi/
├── .claude/
│   ├── agents/
│   │   └── tachi/
│   │       ├── denial-of-service.md                    # MODIFY (additive; 3 small edits) — 53 → 56-60 lines
│   │       ├── model-theft.md                          # MODIFY (additive; 1 small Purpose edit + zero-net-change owasp_references audit) — 95 → 98-102 lines
│   │       ├── orchestrator.md                         # UNCHANGED (zero functional edit; both agents already registered at lines 37/42/298/372)
│   │       ├── output-integrity.md / misinformation.md / human-trust-exploitation.md  # UNCHANGED (24-file invariant; F-1/F-2/F-4 agents)
│   │       ├── tool-abuse.md                           # UNCHANGED (24-file invariant; F-3 host)
│   │       ├── prompt-injection.md / data-poisoning.md / agent-autonomy.md            # UNCHANGED (24-file invariant)
│   │       ├── spoofing / tampering / repudiation / info-disclosure / privilege-escalation.md  # UNCHANGED (5 STRIDE — DoS is enriched)
│   │       ├── risk-scorer.md                          # UNCHANGED (FR-021 infrastructure-tier invariant)
│   │       ├── control-analyzer.md                     # UNCHANGED
│   │       ├── threat-report.md                        # UNCHANGED
│   │       ├── threat-infographic.md                   # UNCHANGED
│   │       └── report-assembler.md                     # UNCHANGED
│   │
│   └── skills/
│       ├── tachi-denial-of-service/
│       │   └── references/
│       │       └── detection-patterns.md               # MODIFY (additive; appends Cat 12 + Cat 13 + Primary Sources extension) — 179 → ~310-360 lines
│       │
│       ├── tachi-model-theft/
│       │   └── references/
│       │       └── detection-patterns.md               # MODIFY (additive; appends Cat 10 + Cat 11 + Primary Sources extension) — 154 → ~290-340 lines
│       │
│       ├── tachi-orchestration/
│       │   └── references/
│       │       └── dispatch-rules.md                   # UNCHANGED (Q2 cosmetic annotation contingent — architect plan-day decision; default-NO; documentation-only if applied)
│       │
│       ├── tachi-shared/
│       │   └── references/
│       │       └── finding-format-shared.md            # UNCHANGED (denial-of-service at line 12; model-theft at line 16; both already in consumers list)
│       │
│       ├── tachi-output-integrity/                      # UNCHANGED (24-file invariant; F-1's companion)
│       ├── tachi-misinformation/                        # UNCHANGED (24-file invariant; F-2's companion)
│       ├── tachi-tool-abuse/                            # UNCHANGED (24-file invariant; F-3 host companion)
│       ├── tachi-human-trust-exploitation/              # UNCHANGED (24-file invariant; F-4's companion)
│       └── tachi-{8 other detection skills}/            # UNCHANGED (24-file invariant)
│
├── schemas/
│   ├── finding.yaml                                     # UNCHANGED — schema_version stays "1.8"; id.pattern unchanged
│   └── taxonomy/                                        # UNCHANGED — read-only source for references validation
│       ├── owasp.yaml                                   # LLM10 entry present (verified at PRD time + plan time at line 373); LLM03 present
│       ├── cwe.yaml                                     # CWE-400 (line 130), CWE-770 (line 182) entries present
│       └── mitre-attack.yaml                            # T1496 entry ABSENT — named in mitigation prose only on Cat 10/11 findings; NOT in references
│
├── docs/
│   └── architecture/
│       └── 02_ADRs/
│           └── ADR-034-llm10-unbounded-consumption-audit.md # NEW — Proposed → Accepted dual-commit (PRD-time + plan-time verified next-available number; ADR-033 highest)
│
├── tests/
│   └── scripts/
│       ├── test_llm10_unbounded_consumption_enrichment.py  # NEW — structural-diff tests on Cat 1–11 (DoS) + Cat 1–9 (model-theft) byte-identity + line-count tests on both agents + MAESTRO grep tests on all 4 files + references-array assertion fixtures for Cat 12/13 + Cat 10/11
│       ├── test_backward_compatibility.py                  # UNCHANGED — 6 non-LLM-serving baselines byte-identity gate (extended scope automatic; LLM-serving topology gate ensures zero impact)
│       └── fixtures/
│           └── llm10_unbounded_consumption/                # NEW — fixture findings for Cat 12/13 + Cat 10/11
│               ├── valid_category_12_inference_flooding_finding.yaml
│               ├── valid_category_13_context_window_latency_finding.yaml
│               ├── valid_category_10_cost_amplification_finding.yaml
│               ├── valid_category_11_denial_of_wallet_finding.yaml
│               └── valid_category_11_critical_floor_freemium_finding.yaml
│
├── examples/
│   ├── web-app / microservices / ascii-web-api / mermaid-agentic-app / free-text-microservice / maestro-reference/  # UNCHANGED (SC-014 baselines; non-LLM-serving — zero new findings)
│   ├── agentic-app/                                     # REGENERATE (Q5 RESOLVED at PRD time — multi-component LLM topology already exercised by F-3; no `.baseline` file by design)
│   └── consumer-agent-app/                              # UNCHANGED (F-4's mutation target without `.baseline` file; untouched by F-5)
│
└── scripts/
    └── tachi_parsers.py                                 # UNCHANGED (validate references field — no F-5 changes; F-A3 will own source_attribution populator wiring later)
```

**Structure Decision**: Single-project layout (existing tachi repo structure). **Zero new top-level directories**. All changes confined to `.claude/agents/tachi/{denial-of-service,model-theft}.md`, `.claude/skills/tachi-{denial-of-service,model-theft}/references/detection-patterns.md`, `docs/architecture/02_ADRs/`, `tests/scripts/`, `examples/agentic-app/`. F-5 follows Feature 082 (lean-agent refactor) + ADR-023 (additive-only shared-reference edits) + Feature 142 (multi-agent component types) + Feature 201 F-1 + Feature 206 F-2 + Feature 219 F-3 + Feature 224 F-4 precedents. **F-5 is the first BLP-01 feature to exercise ADR-023 Decision 3 at two-agent scope simultaneously** — the four-file additive surface across two host-agent + companion pairs.

## System Design

### Components

**Modified components (additive edits only — F-5-owned)**:

1. **`denial-of-service` Threat Agent** (`.claude/agents/tachi/denial-of-service.md`)
   - **Edit 1** (one-line additive): metadata YAML `owasp_references` list extended with `"OWASP LLM10:2025 — Unbounded Consumption"` as the 10th entry. Pre-existing 9 entries (`OWASP A04:2021`, `OWASP DoS Cheat Sheet`, `OWASP API4:2023`, `CWE-400`, `CWE-770`, `CWE-1333`, `CWE-502`, `MITRE ATT&CK T1498`, `MITRE ATT&CK T1499`) byte-identical
   - **Edit 2** (1–3 line additive append within `## Purpose` section): name the LLM-inference-exhaustion surface (inference-request flooding on LLM endpoints, token-budget exhaustion via unbounded prompt-size, context-window-exhaustion latency-driven variant per Q1 SPLIT) alongside existing infrastructure-availability surface — preserves existing `## Purpose` prose byte-identical (additive append only)
   - **Edit 3** (additive references-list extension on Detection Workflow Step 5): existing `(OWASP, CWE, MITRE ATT&CK from the pattern catalog's Primary Sources list)` references-mention extended with `OWASP LLM10:2025` exemplar mention (architect-finalized prose at Wave 1.1)
   - Line count: ≤120 (STRIDE tier cap per ADR-023); PRD-time + plan-time baseline 53; expected post-edit 56–60
   - Five-section canonical layout, single `**MANDATORY**: Read` directive, zero MAESTRO references — all preserved

2. **`model-theft` Threat Agent** (`.claude/agents/tachi/model-theft.md`)
   - **Edit 1** (audit confirmation, **zero net change**): `owasp_references: [OWASP LLM10:2025, OWASP LLM03:2025]` already includes `OWASP LLM10:2025` at line 17 (PRD-time + plan-time grep verified). F-5's audit confirms metadata completeness; zero net change to the `owasp_references` block. Asymmetric to `denial-of-service.md` Edit 1 which is a one-line append.
   - **Edit 2** (1–3 line additive append within `## Purpose` section): name the cost-amplification and denial-of-wallet surface (recursive or cost-asymmetric prompting that drives output-token amplification, multi-tenant denial-of-wallet attacks) alongside existing model-extraction surface — preserves existing `## Purpose` prose byte-identical (additive append only)
   - Line count: ≤150 (AI tier cap per ADR-023); PRD-time + plan-time baseline 95; expected post-edit 98–102
   - Zero MAESTRO references preserved

3. **DoS Pattern Catalog** (`.claude/skills/tachi-denial-of-service/references/detection-patterns.md`)
   - **Edit 1** (additive append after Cat 11 line ~155 region): **Pattern Category 12 — LLM Inference-Request Flooding and Token Exhaustion** with primary OWASP LLM10:2025, related CWE-400 + CWE-770; ≥4 indicators (target 5) covering inference endpoint without per-tenant queries-per-second rate limit, unbounded prompt-size accepted, missing token-budget enforcement, missing token-counting middleware, request-timeout not distinguishing LLM-call latency tail-risk; ≥1 worked example (multi-tenant LLM-serving SaaS `/v1/completions` endpoint exposed without per-tenant QPS rate limit; attacker registers free-tier accounts and floods endpoint); named LLM-specific mitigations (per-tenant QPS rate limit at API gateway, prompt-size cap, per-tenant token budget per request with hard-cap, request-timeout tuned to LLM-call p99 latency, token-counting middleware with anomaly alerting on per-tenant token-velocity spikes)
   - **Edit 2** (additive append after Cat 12): **Pattern Category 13 — Context-Window Exhaustion (Latency-Driven Variant — Q1 SPLIT Vector A)** with primary OWASP LLM10:2025, related CWE-400; explicit Q1 SPLIT scope note clarifying Cat 13 covers Vector A (availability disruption via per-request latency tail) only — Vector B (economic damage) lives in `model-theft` Cat 11; ≥4 indicators (target 5) covering adversarial prompt expansion (no max-context-window enforcement at API gateway), multi-message conversation history without per-conversation truncation policy, recursive prompt patterns not detected at API gateway, context-window monitoring absent, per-tenant context-window cap not differentiated; ≥1 worked example (consumer-facing chatbot with adversarial 32k-token mega-history payload driving context-window to 99% of model max — same architecture also surfaces `model-theft` Cat 11 cost-DoW finding for Vector B); named LLM-specific mitigations (max-context-window enforcement with 413-response, per-conversation truncation with sliding-window limit, recursive-prompt-pattern detection, context-window monitoring with anomaly alerting, per-tenant context-window cap distinct from per-request cap)
   - **Edit 3** (additive append within Pattern Category Disambiguation section per FR-2 / ADR-034 Decision 7): explicit non-overlap carve between **DoS Cat 9** (CWE Top 25 generic infrastructure resource exhaustion) and **Cat 12/13** (LLM-tier inference-resource exhaustion) — same CWE-400 root cause but distinct mitigation surfaces (Cat 9 = HTTP-service-generic; Cat 12/13 = LLM-API-gateway-specific). Same architecture may legitimately surface Cat 9 + Cat 12 + Cat 13 findings.
   - **Edit 4** (additive list extension on `## Primary Sources`): append `OWASP LLM10:2025 — Unbounded Consumption`
   - Pre-existing Cat 1–11 (with hybrid heading: 8 thematic groupings for Cat 1–8 + 3 named `## Pattern Category 9/10/11` headings) + `## Overview` + `## Targeted DFD Element Types` + `## Primary Sources` (existing entries) remain byte-identical pre/post edit. **Note**: this companion does NOT have a `## Trigger Keywords` section (asymmetric to model-theft companion — verified at line 19).

4. **model-theft Pattern Catalog** (`.claude/skills/tachi-model-theft/references/detection-patterns.md`)
   - **Edit 1** (additive append after Cat 9 line ~154): **Pattern Category 10 — Cost Amplification via Recursive or Cost-Asymmetric Prompting** with primary OWASP LLM10:2025, related OWASP LLM03:2025 (inherited supply-chain vocabulary from existing agent metadata); ≥4 indicators (target 5) covering recursive or chain-of-thought prompts without depth limit, output-token cap missing or set higher than realistic per-query response length, output-amplification ratio not monitored per query, cost-per-query p99 alerting absent, per-tenant cost-amplification anomaly detection missing; ≥1 worked example (RAG advisory assistant accepts 10-token prompt triggering recursive chain-of-thought generating 32k tokens of self-amplifying output); named LLM-specific mitigations (per-query output-token cap, recursive-prompt depth limit, output-amplification-ratio monitoring, cost-per-query p99 alerting tied to per-tenant billing attribution, per-tenant cost-amplification anomaly detection); **MITRE ATT&CK T1496 Resource Hijacking** named in mitigation narrative as text-only cross-reference (NOT in references; T1496 not catalog-resolvable per plan-time grep on `schemas/taxonomy/mitre-attack.yaml`)
   - **Edit 2** (additive append after Cat 10): **Pattern Category 11 — Denial-of-Wallet via Context-Window Cost Amplification (Q1 SPLIT Vector B + broader DoW)** with primary OWASP LLM10:2025, related OWASP LLM03:2025 (inherited; cost-flow-through-third-party-models adjacency); explicit Q1 SPLIT scope note clarifying Cat 11 covers Vector B (cost-amplification via context-window expansion driving economic damage — the wallet is the bill) plus the broader denial-of-wallet attack class — Vector A (latency-driven DoS) lives in `denial-of-service` Cat 13; ≥4 indicators (target 5) covering multi-tenant LLM-serving without per-tenant token budget hard-cap, context-window expansion not capped per-tenant, cost-per-query p99 alerting absent, denial-of-wallet anomaly detection absent, automated tenant suspension on budget breach missing, per-tenant billing attribution missing or computed asynchronously; ≥1 worked example (B2C consumer chatbot SaaS allowing freemium users to consume inference compute without per-tenant token budget; attacker registers thousands of freemium accounts and runs cost-amplification queries plus drives context-window to model max per call); named LLM-specific mitigations (per-tenant token budget with hard-cap at API gateway, per-tenant context-window cost reconciliation, cost-per-query p99 alerting tied to per-tenant billing attribution, denial-of-wallet anomaly detection via cost-velocity monitoring, automated tenant suspension on budget breach, per-tenant billing attribution computed at-query-time); **explicit severity-floor note** encoding Q3 RESOLVED 2-condition CRITICAL floor: HIGH default; CRITICAL floor ONLY when (a) multi-tenant freemium structure structurally evident AND (b) both per-tenant token budget AND cost alerting absent; **MITRE ATT&CK T1496 Resource Hijacking** named in mitigation narrative as text-only cross-reference
   - **Edit 3** (additive append within Pattern Category Disambiguation section per FR-3 / ADR-034 Decision 7): explicit non-overlap carve between **model-theft Cat 6** (Unbounded Inference Consumption — pre-existing, abstraction-level per-tenant quotas / cost-controls / billing-attribution gaps) and **Cat 10** (cost-amplification specific attack vectors) and **Cat 11** (denial-of-wallet named economic attack class). Same architecture may legitimately surface Cat 6 + Cat 10 + Cat 11 findings.
   - **Edit 4** (additive list extension on `## Primary Sources`): append `OWASP LLM10:2025 — Unbounded Consumption`
   - Pre-existing Cat 1–9 (uniform `## Pattern Category N:` headings) + `## Overview` + `## Targeted DFD Element Types` + `## Trigger Keywords` (line 19) + `## Primary Sources` (existing entries) remain byte-identical pre/post edit

5. **Public Per-Feature ADR** (`docs/architecture/02_ADRs/ADR-034-llm10-unbounded-consumption-audit.md`)
   - Proposed → Accepted dual-commit (ADR-027/028/029/030/031/032/033 precedent)
   - 7+ numbered Decisions in body:
     - **Decision 1**: Heuristic A enrichment vs. new agent at **two-agent scope** — signal-class identity rationale (same-class with both `denial-of-service` infrastructure-resource-exhaustion sub-class AND `model-theft` extraction-driven-resource-abuse sub-class)
     - **Decision 2**: Additive-only edit discipline per ADR-023 Decision 3 with byte-identity proof on Cat 1–11 (DoS) + Cat 1–9 (model-theft)
     - **Decision 3**: **Canonical 5-row LLM10 sub-pattern → owning-agent mapping table** with severity-hint annotation column per Q3 (the audit deliverable). Rows: (a) inference-request flooding → DoS Cat 12 (severity MEDIUM-HIGH default); (b) token-budget exhaustion → DoS Cat 12 (MEDIUM-HIGH default); (c) context-window exhaustion latency-Vector A → DoS Cat 13 (MEDIUM-HIGH default); (d) context-window exhaustion cost-Vector B → model-theft Cat 11 (HIGH default; CRITICAL floor under 2-condition rule); (e) cost amplification → model-theft Cat 10 (HIGH default); (f) denial-of-wallet broader → model-theft Cat 11 (HIGH default; CRITICAL floor under 2-condition rule)
     - **Decision 4**: No schema bump — reuses D-{N} and LLM-{N} prefixes; structurally symmetric with F-3 (ADR-032 lines 84+182 forecast); asymmetric to F-1/F-2/F-4
     - **Decision 5**: No consumers-list edit — both `denial-of-service` (line 12) and `model-theft` (line 16) already in `finding-format-shared.md` consumers list
     - **Decision 6**: No functional orchestrator/dispatch-rules edit — both agents already fully registered at multiple callsites; cosmetic Q2 annotation default-NO architect-tractable
     - **Decision 7**: Pattern Category Disambiguation — DoS Cat 9 vs. Cat 12/13 non-overlap carve; model-theft Cat 6 vs. Cat 10/11 non-overlap carve
     - **Decision 8**: No `source_attribution` populator wiring extension on host agents — deferred to F-A3; F-5 cites LLM10 in prose-level `references:` array only; F-A3 inheritance one-way
     - **Decision 9**: Public ADR omits commercial framing per SDR-001 Option C
   - Cross-references: ADR-021 (byte-identity baseline harness), ADR-023 (lean+skill-references pattern, additive-only edits Decision 3), ADR-027 (taxonomy crosswalk), ADR-028 (source attribution schema extension + Decision 6 F-A3 deferral), ADR-030 Decision 1 (signal-class taxonomy in LLM tier), ADR-031 Decision 8 (regex-alternation minor-bump rule as the **asymmetry** F-5 does NOT invoke), ADR-032 (first enrichment-branch execution at single-agent scope; **explicit cross-reference to lines 84 + 182 forecast** that F-5 will not need a schema bump), ADR-033 Decision 2 (sub-scope carve-up structural sibling — ASI09 documentation-layer carve-up; F-5 is pattern-catalog-layer carve-up)
   - Detection Calibration Note: clarifies structural-absence detection style consistent with F-1 / F-2 / F-4 absence-style; acceptable FP risk on architectures with implicit-but-undeclared controls per existing tachi convention
   - Zero-MAESTRO-reference invariant: ADR-034 itself contains zero MAESTRO references in Decision sections (mirrors agent file invariant per ADR-023 Decision 2)
   - Revision History table tracking Proposed → Accepted dates; post-merge SHA fill recording squash commit per team-lead LOW-2 / DoD bullet 16

**Optional cosmetic component (Q2 architect plan-day decision)**:

6. **Dispatch Rules Annotation** (`.claude/skills/tachi-orchestration/references/dispatch-rules.md` — annotation only, contingent)
   - If architect approves Q2 at plan time (PRD default-NO; architect-tractable): one-token annotation update extending the `denial-of-service` entry to cite LLM10 for parity with the existing `model-theft (OWASP LLM10:2025)` annotation at line 73
   - **Documentation-only**, zero functional dispatch change — does not invalidate the SC-021 zero-functional-touch claim. Default-NO per PRD.

### Data Flow

Given a DFD architecture description, the orchestrator dispatches the `denial-of-service` agent **as it does today** when any DFD `Process`, `Data Store`, or `Data Flow` element matches existing trigger keywords (availability-relevant keywords) AND the `model-theft` agent when any `Process` matches LLM-relevant keywords. Each agent reads its companion `detection-patterns.md` via the existing single `**MANDATORY**: Read` directive, evaluates pattern categories on each dispatched component, and emits zero or more findings. The new Pattern Categories (Cat 12/13 in DoS; Cat 10/11 in model-theft) enforce the **LLM-serving topology gate** (FR-015): findings emit only when the architecture additionally exhibits LLM-serving indicators (declared inference endpoint, LLM API gateway, per-tenant API key, token-counting middleware, cost-attribution layer, multi-tenant LLM-serving topology). Cat 13 (DoS Vector A latency) and Cat 11 (model-theft Vector B cost) are emitted independently — same architecture exhibiting context-window-exhaustion exposure surfaces BOTH findings (neither is duplicate; Q1 SPLIT cross-agent vector decomposition). Findings flow through orchestrator Phase 3, Phase 4 (referential validation reads `references` array — no F-5 changes; F-A3 will own `source_attribution` populator wiring later), and Phase 5 (deduplication) **identically** to existing Cat 1–11 (DoS) `D-{N}` and Cat 1–9 (model-theft) `LLM-{N}` findings. No consumer-tier changes required. Report-tier rendering (`threat-report.md`, `threats.md`) groups all `D-{N}` findings (Cat 1–13) cohesively in `category: denial-of-service` section and all `LLM-{N}` findings (Cat 1–11) cohesively in `category: llm` section — single-namespace ID space per agent, sequential numbering across all categories.

### Tech Stack

- **Agent / skill files**: Markdown + YAML (ADR-023 lean-agent + additive-only shared-reference pattern)
- **Schema**: `schemas/finding.yaml` v1.8 — **unchanged** (D and LLM prefixes already enumerated; F-5 reuses both)
- **Taxonomy catalogs**: `schemas/taxonomy/{owasp,cwe}.yaml` (F-A1, unchanged) — consumed read-only for `references` validation. `schemas/taxonomy/mitre-attack.yaml` consulted to confirm T1496 absence (named in mitigation prose only).
- **Orchestrator dispatch**: `.claude/agents/tachi/orchestrator.md` + `.claude/skills/tachi-orchestration/references/dispatch-rules.md` — **unchanged** (both agents already fully registered; optional Q2 cosmetic annotation is documentation-only)
- **Parser**: `scripts/tachi_parsers.py` (unchanged — `references` field validation already in place; F-A3 will own `source_attribution` populator wiring later)
- **Test harness**: pytest + `tests/scripts/test_backward_compatibility.py` (existing — automatic scope extension via LLM-serving topology gate ensuring zero impact on 6 non-LLM-serving baselines) + new `tests/scripts/test_llm10_unbounded_consumption_enrichment.py` (structural-diff + line-count + MAESTRO grep + references-array assertion fixtures for Cat 12/13 + Cat 10/11)
- **Example regeneration pipeline**: `/tachi.threat-model` → `/tachi.risk-score` → `/tachi.compensating-controls` → `/tachi.infographic all` → `/tachi.security-report` (existing pipeline, unchanged)
- **Typst templates**: no edits — PDF renderer reads `threats.md` / `risk-scores.md` / `compensating-controls.md` and existing pipeline artifacts auto-render post-regeneration
- **ADR dual-commit**: standard Proposed → Accepted lifecycle via `gh pr` + squash merge (ADR-027/028/029/030/031/032/033 precedent)

## Phase 0: Research

**Status**: Populated by `/aod.spec` at [research.md](./research.md). Key grounding facts re-confirmed at plan time (2026-04-27):

- `.claude/agents/tachi/denial-of-service.md` is **53 lines** (PRD-time + plan-time verified; expected post-edit 56–60 lines)
- `.claude/agents/tachi/model-theft.md` is **95 lines** (PRD-time + plan-time verified; expected post-edit 98–102 lines); `owasp_references: [OWASP LLM10:2025, OWASP LLM03:2025]` already includes LLM10 (zero net change on metadata)
- `.claude/skills/tachi-denial-of-service/references/detection-patterns.md` is **179 lines** with **8 thematic Cat 1–8 groupings + 3 named `## Pattern Category 9/10/11` headings + Primary Sources** (PRD-time + plan-time verified); hybrid heading structure documented in spec edge cases. Companion lacks `## Trigger Keywords` section.
- `.claude/skills/tachi-model-theft/references/detection-patterns.md` is **154 lines** with **9 named `## Pattern Category N:` headings (Cat 1–9) + Overview + Targeted DFD + Trigger Keywords (line 19) + Primary Sources** (PRD-time + plan-time verified)
- `schemas/finding.yaml:13` `schema_version: "1.8"` (post-F-4; F-5 does NOT bump)
- `schemas/finding.yaml` `id.pattern: "^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\\d+$"` — `D` and `LLM` already enumerated; F-5 reuses both
- `schemas/taxonomy/owasp.yaml` contains **LLM10** record (line 373 plan-time-verified) and LLM03 record
- `schemas/taxonomy/cwe.yaml` contains **CWE-400** (line 130) and **CWE-770** (line 182)
- `schemas/taxonomy/mitre-attack.yaml` does NOT contain **T1496** (Resource Hijacking) — F-5 cites T1496 in mitigation prose only on Cat 10/11 findings; NOT in `references`
- `.claude/skills/tachi-shared/references/finding-format-shared.md` consumers list contains `denial-of-service` at line 12 and `model-theft` at line 16 (PRD-time + plan-time verified — no edits needed)
- `dispatch-rules.md` line 73: `model-theft (OWASP LLM10:2025)` already annotated; `denial-of-service` not LLM10-annotated. PRD Q2 cosmetic parity option default-NO architect-tractable.
- ADR-034 does NOT yet exist (PRD-time + plan-time verified next-available ADR number; ADR-033 is highest existing per `ls docs/architecture/02_ADRs/`)
- 0 MAESTRO references in all four target files (PRD-time + plan-time grep-verified)
- F-1, F-2, F-3, F-4 ADRs (ADR-030, ADR-031, ADR-032, ADR-033) are Accepted; F-5 ADR-034 cross-references ADR-030 D1, ADR-031 D8 (asymmetry — F-5 does NOT invoke), ADR-032 (direct precedent), ADR-033 D2 (structural sibling)

**Open research items resolved at PRD time** (not re-litigated during /aod.project-plan):
- **Q1**: Where does context-window-exhaustion live? — RESOLVED at PRD time (architect 2026-04-27): **SPLIT** — Vector A latency-DoS in `denial-of-service` Cat 13; Vector B cost-DoW in `model-theft` Cat 11. Audit table in ADR-034 Decision 3 maps both vectors to disjoint owning categories.
- **Q3**: Severity baseline — Critical severity floor for denial-of-wallet? — RESOLVED at PRD time (architect 2026-04-27): YES Critical floor on Cat 11 conditional. CRITICAL floor ONLY when (a) multi-tenant freemium structure structurally evident AND (b) both per-tenant token budget AND cost alerting absent. Otherwise HIGH default. Cat 12 + Cat 13 MEDIUM-HIGH default. Encoded as severity-hint annotation column in ADR-034 Decision 3 audit table.
- **Q4**: How many new Pattern Categories total? — RESOLVED at PRD time: 4 categories (2 per agent). Architect retains plan-day floor authority to merge into 1 per agent (2-category total floor per Issue #229 DoD bullet) if indicator surface justifies; default 4.
- **Q5**: Example regeneration target? — RESOLVED at PRD time (architect 2026-04-27): `examples/agentic-app/` confirmed. No new architecture authoring needed.

**Open research items resolved during /aod.project-plan** (architect plan-day decision):
- **Q2** (Cosmetic dispatch-rules annotation `denial-of-service` → `denial-of-service (..., LLM10)` for parity with model-theft's existing LLM10 annotation): architect plan-day decision per PRD; default-NO. **Plan-time decision: NO** (zero functional dispatch-tier touches preserved; cosmetic parity is achievable but not required). If architect overrides to YES at Wave 1.0, the edit is single-token and lands at Wave 1.1 alongside `denial-of-service.md` edits. PRD-time architect-leaning was default-NO per architect call.

## Phase 1: Design & Contracts

**Prerequisites**: research.md populated (Phase 0 complete)

### Finding IR Contract (`contracts/finding-contract.md`)

**Purpose**: Document the shape of Cat 12/13 `D-{N}` findings (DoS) and Cat 10/11 `LLM-{N}` findings (model-theft) emitted by the enriched agents, including `references` array invariants, mitigation-text rules, and Q3 severity-floor conditional. See [contracts/finding-contract.md](./contracts/finding-contract.md) for full contract.

**Contract summary (DoS Cat 12/13)**:

```yaml
id: "D-{N}"                           # existing prefix (no schema bump in F-5); single-namespace across Cat 1–13
category: "denial-of-service"         # existing enum value — unchanged
title: "{pattern_category}: {short_summary}"  # e.g., "LLM Inference-Request Flooding: /v1/completions endpoint without per-tenant QPS rate limit"
severity: "medium" | "high" | "critical"  # OWASP 3×3 matrix via severity-bands-shared.md; Cat 12/13 default MEDIUM-HIGH per Q3
component: "{DFD Process | Data Store | Data Flow component name}"
description: "{2-4 sentence threat description distinguishing LLM-tier inference exhaustion from generic infrastructure DoS}"
mitigation: "{LLM-API-gateway / token-budget / context-window mechanism}"  # e.g., "Per-tenant queries-per-second rate limit at the API gateway with prompt-size cap and per-tenant token budget"
references:
  - "OWASP LLM10:2025 — Unbounded Consumption"        # REQUIRED on every Cat 12/13 finding
  - "CWE-400 Uncontrolled Resource Consumption"        # REQUIRED on every Cat 12/13 finding
  - "CWE-770 Allocation of Resources Without Limits or Throttling"  # APPLICABLE per architecture indicator
source_attribution: []                # NOT POPULATED by F-5 — deferred to F-A3 per ADR-028 Decision 6
```

**Contract summary (model-theft Cat 10/11)**:

```yaml
id: "LLM-{N}"                         # existing prefix (no schema bump in F-5); single-namespace across Cat 1–11
category: "llm"                       # existing enum value — unchanged
title: "{pattern_category}: {short_summary}"  # e.g., "Denial-of-Wallet via Context-Window Cost Amplification: multi-tenant LLM SaaS without per-tenant token budget"
severity: "high" | "critical"         # Cat 10 HIGH default; Cat 11 HIGH default with CRITICAL floor on 2-condition rule
component: "{DFD Process | Data Store component name}"
description: "{2-4 sentence threat description distinguishing cost-amplification (Cat 10) from denial-of-wallet (Cat 11)}"
mitigation: "{output-token cap / recursive-prompt depth limit / per-tenant token budget / cost-velocity monitoring mechanism, with text-only T1496 cross-reference}"  # e.g., "Per-tenant token budget with hard-cap at API gateway plus denial-of-wallet anomaly detection via cost-velocity monitoring (cf. MITRE ATT&CK T1496 Resource Hijacking)"
references:
  - "OWASP LLM10:2025 — Unbounded Consumption"        # REQUIRED on every Cat 10/11 finding
  - "OWASP LLM03:2025 — Supply Chain"                 # APPLICABLE for cost-flow-through-third-party-models adjacency
  # NOTE: T1496 NOT in references (not catalog-resolvable); named in mitigation prose only
source_attribution: []                # NOT POPULATED by F-5 — deferred to F-A3 per ADR-028 Decision 6
```

**Invariants**:
- Every Cat 12/13 `D-{N}` finding's `references` array MUST contain at minimum `OWASP LLM10:2025` and `CWE-400`; CWE-770 included per applicability
- Every Cat 10/11 `LLM-{N}` finding's `references` array MUST contain at minimum `OWASP LLM10:2025`; LLM03 included per applicability
- The `mitigation` field MUST name at least one specific LLM-API-gateway / token-budget / context-window / cost-control mechanism — NOT generic "rate-limit your endpoints"
- Cat 10/11 mitigation narratives MUST text-only-mention `MITRE ATT&CK T1496 Resource Hijacking` as a cross-reference (NOT in `references`)
- The `id` MUST match schema 1.8 `id.pattern` regex (existing D and LLM prefixes; no bump)
- Both agents MUST enforce the LLM-serving topology gate (FR-015): Cat 12/13 + Cat 10/11 emit zero findings on architectures lacking LLM-serving indicators
- Cat 11 severity computation MUST encode the Q3 RESOLVED 2-condition CRITICAL floor: HIGH default; CRITICAL floor ONLY when (a) multi-tenant freemium structure structurally evident AND (b) both per-tenant token budget AND cost alerting absent
- F-5 does NOT extend `source_attribution` populator wiring on either host agent — that scope belongs to F-A3 per ADR-028 Decision 6

### Data Model (`data-model.md`)

**Purpose**: Document Pattern Category 12/13 (DoS) + Cat 10/11 (model-theft) entity shapes, the LLM-serving topology gate predicates, references-array patterns per category, Q3 severity-floor conditional predicate, and Pattern Category Disambiguation entities (DoS Cat 9 vs. Cat 12/13; model-theft Cat 6 vs. Cat 10/11; Q1 SPLIT cross-agent vector decomposition for context-window exhaustion).

See [data-model.md](./data-model.md) for full entity definitions.

### Quickstart (`quickstart.md`)

**Purpose**: Step-by-step verification walkthrough — given a regenerated `examples/agentic-app/`, confirm ≥1 new `D-{N}` finding (Cat 12 OR 13) AND ≥1 new `LLM-{N}` finding (Cat 10 OR 11) with valid `references` array (LLM10 + CWE-400 + CWE-770 / LLM03 per category), valid LLM-specific mitigation text (named mechanism), passing structural validation (line caps, byte-identity, MAESTRO grep), and 6 non-LLM-serving baselines byte-identical under `SOURCE_DATE_EPOCH=1700000000`.

See [quickstart.md](./quickstart.md) for the verification procedure.

### Agent Context Update

Run `.aod/scripts/bash/update-agent-context.sh claude` after plan approval to refresh `CLAUDE.md` / agent-specific context with the Feature 229 entry.

## Implementation Approach (Phased Waves)

Calendar-verified against `cal 4 2026`: 2026-04-28 Tuesday (plan day per Tuesday-after-Monday-PRD cadence), 2026-04-29 Wednesday (Day 1 build), 2026-04-30 Thursday (Day 2 / buffer day).

**1.5-day envelope** per PRD §Timeline: F-5 surface is structurally between F-3 (1 day single-agent enrichment) and F-2 (2 days new-agent shape). Realistic envelope: **1.5 working days**, 1 day aspirational, 2 days conservative. F-5's wave structure follows the team-lead MEDIUM-1 rebalance — Day 1 PM is no longer back-loaded with ADR-034 mapping table population (Q1/Q3 resolved at PRD time so Day 1 AM lands the final mapping table including 5-row sub-pattern → owning-category map plus severity-hint annotation column).

### Wave 1 — Day 1 AM (Wednesday 2026-04-29, ~0.4d)

**ADR-034 Proposed (with mapping table populated complete) + DoS agent + companion edits + structural validation.**

- **Wave 1.0 (15–30 min)**: Architect re-verifies (a) all 4 catalog citations still resolve in `schemas/taxonomy/{owasp,cwe}.yaml` (re-runs PRD-time + plan-time grep checks: LLM10 line 373, LLM03 present, CWE-400 line 130, CWE-770 line 182); (b) T1496 still absent in `schemas/taxonomy/mitre-attack.yaml`; (c) Heuristic A enrichment-vs-new-agent decision intact at two-agent scope (SDR-001 Decision 4 locked; ADR-030 D1 + ADR-031 D8 + ADR-032 + ADR-033 D2 cross-refs valid); (d) `denial-of-service.md` line count is still 53 + `model-theft.md` line count is still 95 (no concurrent edit landed since plan time); (e) `model-theft.md` `owasp_references` still includes LLM10 (zero-net-change audit baseline); (f) **Q2 plan-day decision** on cosmetic dispatch-rules annotation (default-NO per plan; YES override single-token edit at Wave 1.1).
- **Wave 1.1 (parallel)**:
  - **ADR-034 Proposed commit** with body containing 9 numbered Decisions (per System Design §Components item 5); cross-references to ADR-021/023/027/028 + ADR-030 D1 + ADR-031 D8 (asymmetry) + ADR-032 (lines 84+182 forecast) + ADR-033 D2 (structural sibling); 24-file zero-edit invariant proof with grep-auditable enumeration; 28-file detection-tier inventory documented; **canonical 5-row LLM10 sub-pattern → owning-agent mapping table populated complete** (NOT skeleton — Q1/Q3 resolved at PRD time per team-lead MEDIUM-1 rebalance); Detection Calibration Note; Revision History table.
  - **`denial-of-service.md` edits (Edit 1 + Edit 2 + Edit 3)**: metadata `owasp_references += "OWASP LLM10:2025 — Unbounded Consumption"` (10th entry); `## Purpose` 1–3 line extension naming LLM-inference-exhaustion surface; Detection Workflow Step 5 references-mention extended with `OWASP LLM10:2025` exemplar mention. Architect adjudicates final `## Purpose` prose at Wave 1.1.
  - **DoS companion `detection-patterns.md` edits (Edit 1 + Edit 2 + Edit 3 + Edit 4)**: append Cat 12 + Cat 13 (with Q1 SPLIT Vector A scope note on Cat 13) + Pattern Category Disambiguation subsection (DoS Cat 9 vs. Cat 12/13 carve) + Primary Sources extension. Architect-finalized prose at Wave 1.1.
  - **Test fixture authoring (DoS half)**: `tests/scripts/fixtures/llm10_unbounded_consumption/valid_category_12_inference_flooding_finding.yaml`, `valid_category_13_context_window_latency_finding.yaml`.
  - **Optional Q2 cosmetic annotation**: if architect approved YES at Wave 1.0, single-token edit to `dispatch-rules.md` for `denial-of-service` LLM10 parity. Default-NO per plan.
- **Structural validation at Wave 1.1 EOD**: `wc -l .claude/agents/tachi/denial-of-service.md` returns ≤120 (expected 56–60); `grep -c '\*\*MANDATORY\*\*: Read' .claude/agents/tachi/denial-of-service.md` returns 1 (unchanged); `grep -i maestro .claude/agents/tachi/denial-of-service.md` returns empty; structural diff of pre/post DoS companion returns empty for Cat 1–11 + `## Overview` + `## Targeted DFD Element Types`.

### Wave 2 — Day 1 PM (Wednesday 2026-04-29, ~0.5d)

**model-theft agent + companion edits + structural validation + example regen + Day 1 PM byte-identity spot-check.**

- **`model-theft.md` edits (Edit 1 + Edit 2)**: audit-confirm `owasp_references` already includes LLM10 (zero net change documented in commit message); `## Purpose` 1–3 line extension naming cost-amplification and denial-of-wallet surface. Architect adjudicates final `## Purpose` prose.
- **model-theft companion `detection-patterns.md` edits (Edit 1 + Edit 2 + Edit 3 + Edit 4)**: append Cat 10 + Cat 11 (with Q1 SPLIT Vector B + broader DoW scope note on Cat 11; Q3 severity-floor 2-condition note explicitly written; T1496 in mitigation prose only) + Pattern Category Disambiguation subsection (model-theft Cat 6 vs. Cat 10/11 carve) + Primary Sources extension. Architect-finalized prose.
- **Test fixture authoring (model-theft half)**: `tests/scripts/fixtures/llm10_unbounded_consumption/valid_category_10_cost_amplification_finding.yaml`, `valid_category_11_denial_of_wallet_finding.yaml`, `valid_category_11_critical_floor_freemium_finding.yaml`.
- **Example regeneration on `examples/agentic-app/`** (FR-013): run `/tachi.threat-model examples/agentic-app/architecture.md` to confirm dispatch emits ≥1 new Cat 12/13 `D-{N}` finding AND ≥1 new Cat 10/11 `LLM-{N}` finding.
- **Run full downstream pipeline** (`/tachi.risk-score`, `/tachi.compensating-controls`, `/tachi.infographic all`, `/tachi.security-report`).
- **Commit regenerated artifacts**: `threats.md`, `threats.sarif`, `risk-scores.md`, `risk-scores.sarif`, `compensating-controls.md`, `compensating-controls.sarif`, `threat-report.md`, `attack-trees/`, `attack-chains.md`, infographic JPEGs, `security-report.pdf`.
- **Verify**: ≥1 new Cat 12/13 `D-{N}` finding present with `references` array containing LLM10 + CWE-400 (and where applicable CWE-770); ≥1 new Cat 10/11 `LLM-{N}` finding present with `references` array containing LLM10 (and where applicable LLM03); cohesive category rendering (all `D-{N}` adjacent in `category: denial-of-service`; all `LLM-{N}` adjacent in `category: llm`).
- **Day 1 PM end early-signal byte-identity spot-check** per team-lead MEDIUM-1 rebalance: regenerate 1–2 baselines (e.g., `web-app` + `maestro-reference`) under `SOURCE_DATE_EPOCH=1700000000` to catch regen surprises before Day 2. Pulls SC-014 verification gate forward by ~12 hours.
- **Structural validation at Wave 2 EOD**: `wc -l .claude/agents/tachi/model-theft.md` returns ≤150 (expected 98–102); `grep -i maestro` on `model-theft.md` + model-theft companion returns empty; structural diff of pre/post model-theft companion returns empty for Cat 1–9 + `## Overview` + `## Targeted DFD Element Types` + `## Trigger Keywords` + Primary Sources existing entries.

### Wave 3 — Day 2 AM (Thursday 2026-04-30, ~0.3d)

**Full byte-identity verification + tests + ADR-034 Accepted transition.**

- **`tester` agent owns Wave 3 byte-identity gate** per team-lead MEDIUM-2 (separate from `senior-backend-engineer` who authored Waves 1+2).
- Run `tests/scripts/test_backward_compatibility.py` — **6 non-LLM-serving baselines** (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`) MUST be byte-identical under `SOURCE_DATE_EPOCH=1700000000`. Includes 4 baselines NOT covered by Day 1 PM spot-check.
- Run `tests/scripts/test_llm10_unbounded_consumption_enrichment.py` — structural-diff tests on Cat 1–11 (DoS) + Cat 1–9 (model-theft) byte-identity (BLOCKER per SC-008 + SC-010); line-count tests on both agents (BLOCKER per SC-002 + SC-005); MAESTRO grep tests on all 4 enriched files (BLOCKER per SC-020); references-array assertion tests on Cat 12/13 + Cat 10/11 fixture findings (BLOCKER per SC-019).
- Code-review pass: senior-backend-engineer + code-reviewer review pattern catalog worked examples for clearly-fictional framing (no real institutional/clinician/lawyer/advisor identities); structural-diff invariants; line-count caps; MAESTRO grep; T1496 prose-only mention not in references.
- **Transition ADR-034 Proposed → Accepted** with provisional merge-date.
- **PR title pre-merge verification** per Release Discipline subsection: re-verify PR title is `feat(229): llm10 unbounded consumption verification` (or similar Conventional Commits form ≤70 chars); retitle if any deviation slipped through.

### Wave 4 — Day 2 PM (Thursday 2026-04-30, ~0.2d)

**PR ready + squash-merge + post-merge release-please verification + Coverage Matrix update + delivery retrospective.**

- Mark PR (draft) ready for review via `gh pr ready`.
- Triple-review + merge (squash commit with `feat(229): llm10 unbounded consumption verification` Conventional Commits title).
- **Post-merge release-please verification** (SC-022 / R6) within ~30s: confirm release-please PR opened. If empty, push empty `feat(229): llm10 unbounded consumption verification — release marker` commit per F-212 incident recovery pattern.
- **Post-merge SHA fill** on ADR-034 Revision History table per team-lead LOW-2 / DoD bullet 16.
- **BLP-01 Coverage Matrix update** (SC-021): LLM10:2025 transitions Partial → Covered with F-5 (Feature 229) named as closure feature. Coverage milestones panel updates to **OWASP LLM Top 10:2025 = 10 of 10 Covered**. Combined with post-F-4 OWASP Agentic Top 10:2026 = 10/10: post-F-5 tachi covers **20 of 20 OWASP AI top-10 entries**. Post-merge documentation commit to `_internal/strategy/BLP-01-threat-coverage.md`.
- **Delivery retrospective filing** per SC-022 / DoD bullet 15 / team-lead MEDIUM-3 priority order: file `specs/229-llm10-unbounded-consumption-verification/delivery.md` per F-1 + F-2 + F-3 + F-4 precedent. Captures: actual vs. estimated effort, **second execution of Heuristic A enrichment-pattern at two-agent scope** lessons (precedent for F-6/F-7 Tier 2 ML+Mobile bundles which may also use multi-agent enrichment), Q1 SPLIT cross-agent vector decomposition lessons (first BLP-01 sub-pattern with cross-agent vector decomposition), byte-identity preservation evidence (SC-008 + SC-010 + SC-014 grep proofs across 6 baselines), canonical sub-pattern mapping table audit-deliverable lessons, ADR-034 Accepted-commit SHA-fill execution, any deviations from PRD timeline or scope.

## Touch Points Summary

| File | Change | Lines | Scope |
|------|--------|-------|-------|
| `.claude/agents/tachi/denial-of-service.md` | MODIFY (additive; 3 small edits) | ~3–7 added | Metadata + Purpose + Step 5 references |
| `.claude/agents/tachi/model-theft.md` | MODIFY (additive; 1 Purpose edit + zero-net-change `owasp_references` audit) | ~3–7 added | Audit + Purpose extension |
| `.claude/skills/tachi-denial-of-service/references/detection-patterns.md` | MODIFY (additive; 4 sections appended) | ~140–180 added | Cat 12 + Cat 13 + Pattern Category Disambiguation + Primary Sources extension |
| `.claude/skills/tachi-model-theft/references/detection-patterns.md` | MODIFY (additive; 4 sections appended) | ~140–180 added | Cat 10 + Cat 11 + Pattern Category Disambiguation + Primary Sources extension |
| `.claude/skills/tachi-orchestration/references/dispatch-rules.md` | OPTIONAL annotation (Q2 plan-day decision; default-NO; documentation-only if applied) | ~1 token | Cosmetic LLM10 parity for `denial-of-service` entry — zero functional change |
| `docs/architecture/02_ADRs/ADR-034-llm10-unbounded-consumption-audit.md` | NEW | ~280–400 | Public ADR with 9 Decisions + canonical 5-row mapping table + Detection Calibration Note + Revision History |
| `tests/scripts/test_llm10_unbounded_consumption_enrichment.py` | NEW | ~150–200 | Structural-diff + line-count + MAESTRO grep + references-array assertion fixtures |
| `tests/scripts/fixtures/llm10_unbounded_consumption/*.yaml` | NEW | ~20–30 each | Test fixtures (5 files: 1 per Cat 12/13/10/11 + 1 Cat 11 critical-floor freemium) |
| `examples/agentic-app/*` | REGENERATE | — | Pipeline artifacts (no `.baseline` PDF by design — F-3 / F-5 mutation target) |
| `.claude/agents/tachi/{12 other detection-tier}.md` + `.claude/skills/tachi-{12 other detection-tier}/references/detection-patterns.md` | ZERO CHANGES | — | 24-file invariant (post-F-4 inventory: 28 detection-tier files; F-5 edits 4 host files; 24 stay byte-identical) |
| `.claude/agents/tachi/orchestrator.md` | ZERO CHANGES | — | Both agents already registered at lines 37/42/298/372 |
| `.claude/skills/tachi-shared/references/finding-format-shared.md` | ZERO CHANGES | — | Both agents already in consumers list at lines 12 + 16 |
| `.claude/agents/tachi/{risk-scorer,control-analyzer,threat-report,threat-infographic,report-assembler}.md` | ZERO CHANGES | — | Infrastructure-tier invariant |
| `schemas/finding.yaml` | ZERO CHANGES | — | No schema bump (second BLP-01 detection feature with no schema bump after F-3; first at two-agent scope) |
| `schemas/taxonomy/*.yaml` | ZERO CHANGES | — | LLM10/LLM03/CWE-400/CWE-770 already present; T1496 absent intentionally |
| `scripts/*.py` | ZERO CHANGES | — | Parser + orchestrator scripts; F-A3 will own `source_attribution` populator wiring |
| `templates/tachi/*` | ZERO CHANGES | — | Typst templates |
| `requirements*.txt`, `pyproject.toml`, `package.json` | ZERO CHANGES | — | No new dependencies |

## Risks & Mitigations

See spec.md Edge Cases + PRD §Risks & Dependencies for the full list. Plan-phase active risks:

- **R1 (Example regeneration friction on `examples/agentic-app/`)** — Mitigation: Q5 RESOLVED at PRD time per architect adjudication; no new architecture authoring needed. Wave 2 structured pre-vs-post diff; Wave 3 / Day 2 AM and the buffer-day priority order (per team-lead MEDIUM-3) reserves up to 8 hours for regen friction absorption. Status: LOW-MEDIUM likelihood (cumulative mutation pressure post-F-3 + F-4).
- **R2 (Heuristic A two-agent scope pushback at architect review)** — Mitigation: Wave 1.0 architect re-verifies SDR-001 Decision 4 + ADR-030 D1 + ADR-031 D8 + ADR-032 + ADR-033 D2 cross-refs intact; PRD §"Three things the solution is deliberately NOT" pre-empts most likely concerns. Status: LOW likelihood per architect APPROVED_WITH_CONCERNS at PRD review (12/12 v2 findings RESOLVED, 0 net-new).
- **R3 (Canonical sub-pattern → owning-agent mapping table boundary disputes)** — Mitigation: Q1 SPLIT RESOLVED at PRD time with 5-row mapping table populated complete at Wave 1.1 (NOT skeleton, per team-lead MEDIUM-1). ADR-034 Decision 3 5-row table with severity-hint annotation column. Status: LOW likelihood; if architect disputes the SPLIT post-Wave-1.0, single-row mapping change is a one-paragraph edit.
- **R4 (Catalog drift between PRD time and build time)** — Mitigation: Wave 1.0 re-verification of all 4 catalog citations (LLM10, LLM03, CWE-400, CWE-770) and T1496 absence. F-A2 referential-integrity validator (when F-A3 ships) catches drift programmatically. Status: VERY LOW likelihood (taxonomy catalogs are stable post-F-A1).
- **R5 (Severity-discrimination calibration on denial-of-wallet findings)** — Mitigation: Q3 RESOLVED at PRD time per OWASP 3×3 reasoning. Cat 11 severity floor encoded in worked example narrative + ADR-034 Decision 3 audit-table annotation column. Status: VERY LOW likelihood.
- **R6 (Release-please skip if PR title misformatted)** — Mitigation: Plan-stage opens draft PR with `feat(229):` title from start. Wave 3 pre-merge re-verifies title and retitles if needed; Wave 4 post-merge verifies release-please PR opens within ~30s; recovery via empty `feat(229): ... release marker` commit per F-212 precedent.
- **R7 (BLP-01 Tier 1 momentum perception — closing milestone)** — Mitigation: F-5 closing the last LLM Top 10 gap within 1.5 working days demonstrates that the BLP-01 sequencing strategy converges to a clean 20-of-20 OWASP AI top-10 milestone. Status: VERY LOW likelihood.
- **R8 (Closing-milestone over-attribution risk)** — Mitigation: README / docs claim "detection coverage for 20/20 OWASP AI top-10 entries" (precise) rather than "comprehensive coverage" (overclaim); Coverage Matrix transitions explicitly cite closure features (LLM10 → F-5 / Feature 229; ASI09 → F-4 / Feature 224). Status: LOW likelihood.

## Open Questions (PRD Q-set — Architect Decisions)

Architect-owned per PRD §Architecture & Design Decisions. PRD-resolved Q1/Q3/Q4/Q5 not re-litigated; Q2 resolved during /aod.project-plan per architect plan-day decision authority.

| # | Question | Architect Decision | Justification | Codified In |
|---|---|---|---|---|
| Q1 | Where does context-window-exhaustion live — `denial-of-service` (infrastructure resource exhaustion class) or `model-theft` (extraction-driven cost class)? | **RESOLVED at PRD time (architect 2026-04-27)**: SPLIT — Vector A latency-DoS in DoS Cat 13 / Vector B cost-DoW in model-theft Cat 11 | Same architecture surfaces both; neither is duplicate. Audit table maps each vector to disjoint owning category. Avoids cross-agent finding fragmentation while honoring dual-attack-vector signal-class structure. | ADR-034 Decision 3 5-row mapping table; DoS Cat 13 + model-theft Cat 11 worked examples |
| Q2 | Does the orchestrator's dispatch list need a cosmetic annotation update (`denial-of-service` → `denial-of-service (..., LLM10)` for parity with model-theft's existing LLM10 annotation)? | **NO** (plan-time architect decision; default-NO per PRD architect leaning) | OWASP refs metadata extension on `denial-of-service.md` per FR-001 is sufficient for Coverage Matrix traceability. Zero functional dispatch-tier touches preserved. Cosmetic parity is achievable but not required. | `dispatch-rules.md` UNCHANGED at Wave 1.1; F-5 zero-functional-orchestrator-touch claim preserved |
| Q3 | Severity baseline — Critical severity floor for denial-of-wallet findings? | **RESOLVED at PRD time (architect 2026-04-27)**: YES Critical floor on Cat 11 conditional. CRITICAL floor ONLY when (a) multi-tenant freemium structurally evident AND (b) both per-tenant token budget AND cost alerting absent. Otherwise HIGH default. Cat 12+13 MEDIUM-HIGH. | OWASP 3×3 (likelihood × impact composite). Worst-case quadrant warrants Critical floor for narrowly-defined trigger; broader cases retain HIGH default to preserve severity discrimination. | ADR-034 Decision 3 severity-hint annotation column; model-theft Cat 11 worked example explicitly states 2-condition Critical floor |
| Q4 | How many new Pattern Categories total across both agents? | **CONFIRMED at PRD time: 2 per agent (4 total)** — DoS gains Cat 12 + Cat 13; model-theft gains Cat 10 + Cat 11. Architect retains plan-day floor authority to merge into 1 per agent (2-category total floor per Issue #229 DoD bullet) if indicator surface justifies. **Plan-time decision: 4 categories total** (no merge — indicator surface + Q1 SPLIT cross-agent vector decomposition justify distinct categories per host). | Cat 12 + Cat 13 in DoS represent distinct attack-vector signal classes (per-request resource exhaustion via flooding vs. via context-window expansion); merging would conflate vectors. Cat 10 + Cat 11 in model-theft represent distinct economic attack vectors (cost-amplification on individual queries vs. denial-of-wallet at multi-tenant scale); merging would conflate granularity. | DoS companion Cat 12 + Cat 13 + model-theft companion Cat 10 + Cat 11 — all distinct sections at Wave 1.1 / Wave 2 |
| Q5 | Example regeneration target — `examples/agentic-app/` (proven mutation candidate from F-3) or new `examples/llm-serving-app/`? | **RESOLVED at PRD time (architect 2026-04-27)**: `examples/agentic-app/` confirmed | No new architecture authoring needed; mutation candidate is multi-component LLM topology already exercised by F-3. ADR-034 Detection Calibration Note clarifies new categories fire on structural absence of named control mechanisms (consistent with F-1/F-2/F-4 absence-style detection). | Wave 2 example regeneration on `examples/agentic-app/` |

## Success Criteria Mapping

| Spec SC | Implementation Phase | Deliverable |
|---|---|---|
| SC-001 | Wave 1.1 | `denial-of-service.md` `owasp_references += "OWASP LLM10:2025 — Unbounded Consumption"`; existing 9 entries byte-identical (grep) |
| SC-002 | Wave 1.1 EOD | `wc -l .claude/agents/tachi/denial-of-service.md` returns ≤120 (expected 56–60) |
| SC-003 | Wave 1.1 + Wave 3 | DoS `## Purpose` 1–3 line extension appended; pre-existing prose byte-identical (structural diff) |
| SC-004 | Wave 1.1 | DoS Detection Workflow Step 5 references-mention extended with `OWASP LLM10:2025` exemplar; existing entries byte-identical |
| SC-005 | Wave 2 EOD | `wc -l .claude/agents/tachi/model-theft.md` returns ≤150 (expected 98–102) |
| SC-006 | Wave 2 + Wave 3 | model-theft `## Purpose` 1–3 line extension appended; pre-existing prose byte-identical (structural diff). `owasp_references` audit-confirmed (zero net change; verified via empty diff on metadata block) |
| SC-007 | Wave 1.1 | DoS companion Cat 12 + Cat 13 appended with ≥4 indicators each, ≥1 worked example each, named LLM-specific mitigations |
| SC-008 | Wave 1.1 EOD | Structural diff of pre/post DoS companion returns empty for Cat 1–11 + `## Overview` + `## Targeted DFD Element Types` + `## Primary Sources` (existing entries) |
| SC-009 | Wave 2 | model-theft companion Cat 10 + Cat 11 appended with ≥4 indicators each, ≥1 worked example each, named LLM-specific mitigations; T1496 in mitigation prose only on Cat 10/11 |
| SC-010 | Wave 2 EOD | Structural diff of pre/post model-theft companion returns empty for Cat 1–9 + `## Overview` + `## Targeted DFD Element Types` + `## Trigger Keywords` + `## Primary Sources` (existing entries) |
| SC-011 | Wave 1.1 + Wave 2 | Both companions' `## Primary Sources` extended with `OWASP LLM10:2025`; existing entries byte-identical |
| SC-012 | Wave 1.1 + Wave 3 | ADR-034 Proposed at Wave 1.1 with 5-row mapping table populated complete; Accepted at Wave 3 with all 9 required Decisions + cross-references |
| SC-013 | Wave 2 + Wave 3 | Regenerated `examples/agentic-app/` emits ≥1 new Cat 12/13 `D-{N}` finding AND ≥1 new Cat 10/11 `LLM-{N}` finding; non-qualifying baselines emit 0 (LLM-serving topology gate enforces FR-015) |
| SC-014 | Wave 2 (spot-check) + Wave 3 (full) | `test_backward_compatibility.py` passes on **6 non-LLM-serving baselines** under `SOURCE_DATE_EPOCH=1700000000`. Owner: `tester` agent per team-lead MEDIUM-2 |
| SC-015 | Wave 2 | `examples/agentic-app/` regeneration produces ≥1 new `D-{N}` finding (Cat 12 OR 13) + ≥1 new `LLM-{N}` finding (Cat 10 OR 11) with concrete LLM-specific mitigations + `OWASP LLM10:2025` in their prose-level `references:` arrays |
| SC-016 | All waves | Empty diff on dependency manifest files (verified at PR pre-merge) |
| SC-017 | All waves | Grep audit at PR pre-merge confirms zero edits to 24 detection-tier files (12 other agents + 12 other companions); 28-file post-F-4 inventory minus 4 F-5 targets = 24 |
| SC-018 | All waves | `schemas/finding.yaml` `schema_version` remains `"1.8"`; `id.pattern` regex unchanged (verified at PR pre-merge) |
| SC-019 | Wave 2 + Wave 3 | Cat 12/13 `D-{N}` findings carry LLM10 + CWE-400 (and where applicable CWE-770) in `references` array; Cat 10/11 `LLM-{N}` findings carry LLM10 (and where applicable LLM03) in `references` array; T1496 in mitigation prose only (NOT in references); fixture tests confirm |
| SC-020 | All waves | `grep -i maestro` on `denial-of-service.md` + `model-theft.md` + both companions returns empty |
| SC-021 | All waves + Wave 4 | `orchestrator.md` + `dispatch-rules.md` show zero functional diff (Q2 cosmetic annotation default-NO; if applied YES, single-token documentation-only); BLP-01 Coverage Matrix updated post-merge: LLM10:2025 Partial → Covered, OWASP LLM Top 10 = 10/10 Covered, OWASP AI top-10 = 20/20 |
| SC-022 | Wave 4 | PR title `feat(229): ...`; pre-merge re-verification at Wave 3 + `/aod.deliver`; post-merge release-please PR opens within ~30s (or recovery via empty release-marker commit per F-212 precedent); `delivery.md` filed per team-lead MEDIUM-3 priority |

## PR Pre-Merge Checklist

- [ ] All Wave 1–3 structural validations green (line counts ≤120 on `denial-of-service.md` + ≤150 on `model-theft.md`, MANDATORY count = 1 on both, MAESTRO grep empty on all 4 files)
- [ ] DoS Cat 1–11 byte-identity grep audit returns empty diff for unchanged regions in DoS companion
- [ ] model-theft Cat 1–9 byte-identity grep audit returns empty diff for unchanged regions in model-theft companion
- [ ] 24-file zero-edit grep audit returns empty for 12 other threat-agent files + 12 other companion `detection-patterns.md` files (28 detection-tier files − 4 F-5 targets)
- [ ] Infrastructure-tier consumer files (risk-scorer, control-analyzer, threat-report, threat-infographic, report-assembler) show zero diff
- [ ] `orchestrator.md` shows zero diff; `finding-format-shared.md` shows zero diff
- [ ] `schemas/finding.yaml` shows zero diff (no schema bump)
- [ ] `dispatch-rules.md` shows zero functional diff (cosmetic annotation default-NO; if applied is single-token, contingent on Q2)
- [ ] `test_backward_compatibility.py` passes on 6 non-LLM-serving baselines (Owner: `tester` agent)
- [ ] `test_llm10_unbounded_consumption_enrichment.py` passes (structural-diff + line-count + MAESTRO grep + Cat 12/13 + Cat 10/11 references-array fixtures)
- [ ] `examples/agentic-app/` regeneration commits present (no `.baseline` PDF by design)
- [ ] At least 1 new Cat 12/13 `D-{N}` finding emitted on regenerated example with valid `references` array (LLM10 + CWE-400, CWE-770 where applicable) + grounded LLM-specific mitigation
- [ ] At least 1 new Cat 10/11 `LLM-{N}` finding emitted on regenerated example with valid `references` array (LLM10, LLM03 where applicable) + grounded LLM-specific mitigation + T1496 in mitigation prose only
- [ ] ADR-034 transitioned Proposed → Accepted with Revision History entry; cross-references to ADR-021/023/027/028/030 D1/031 D8/032/033 D2 present; canonical 5-row mapping table populated complete with severity-hint annotation column; zero MAESTRO references in ADR Decision sections
- [ ] Pattern Category Disambiguation subsections present in both companions per FR-2/3 / ADR-034 Decision 7
- [ ] Q1 SPLIT cross-agent vector decomposition documented in DoS Cat 13 + model-theft Cat 11 scope notes
- [ ] Q3 severity-floor 2-condition encoded in model-theft Cat 11 worked example narrative
- [ ] PR title is `feat(229): ...` Conventional Commits format
- [ ] Dependency manifest diff is empty (pyproject.toml, requirements*.txt, package.json)
- [ ] Cohesive category rendering verified on regenerated example (D-{N} adjacent in `category: denial-of-service`; LLM-{N} adjacent in `category: llm`)
- [ ] Triple sign-off in tasks.md frontmatter (PM + Architect + Team-Lead) — enforced in `/aod.tasks`

## References

- PRD: [229-llm10-unbounded-consumption-verification-2026-04-27.md](../../docs/product/02_PRD/229-llm10-unbounded-consumption-verification-2026-04-27.md)
- Spec: [spec.md](./spec.md)
- Research: [research.md](./research.md)
- Feature 082 precedent: [082-threat-agent-skill-references](../082-threat-agent-skill/)
- Feature 142 precedent (multi-agent component types): [142-maestro-phase-2](../142-maestro-phase-2/)
- Feature 201 F-1 precedent (first net-new AI-tier agent under ADR-023; new-agent branch of Heuristic A): [201-output-integrity-threat-agent](../201-output-integrity-threat-agent/)
- Feature 206 F-2 precedent (second net-new AI-tier agent; new-agent branch second-execution validation): [206-misinformation-threat-agent](../206-misinformation-threat-agent/)
- Feature 219 F-3 precedent (**direct enrichment-branch precedent — first execution at single-agent scope; ADR-032 lines 84+182 forecast F-5 will not need a schema bump**): [219-asi07-tool-abuse-enrichment](../219-asi07-tool-abuse-enrichment/)
- Feature 224 F-4 precedent (third net-new agent; sub-scope carve-up structural sibling per ADR-033 D2): [224-trust-exploitation-threat-agent](../224-trust-exploitation-threat-agent/)
- ADR-021 (SOURCE_DATE_EPOCH determinism): `docs/architecture/02_ADRs/ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md`
- ADR-023 (Lean-agent + additive-only shared-reference Decision 3): `docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md`
- ADR-027 (Taxonomy crosswalk schema): `docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md`
- ADR-028 (Source attribution schema extension; Decision 6 F-A3 deferral): `docs/architecture/02_ADRs/ADR-028-source-attribution-schema-extension.md`
- ADR-030 (F-1 output-integrity agent, Decision 1 signal-class taxonomy in LLM tier): `docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md`
- ADR-031 (F-2 misinformation agent, Decision 8 regex-alternation minor-bump rule — F-5 cross-references as **asymmetry**: F-5 does NOT invoke): `docs/architecture/02_ADRs/ADR-031-misinformation-agent.md`
- ADR-032 (F-3 ASI07 tool-abuse enrichment — **direct precedent**: first enrichment-branch execution at single-agent scope; lines 84+182 forecast F-5 will not need a schema bump): `docs/architecture/02_ADRs/ADR-032-asi07-tool-abuse-enrichment.md`
- ADR-033 (F-4 human-trust-exploitation agent, Decision 2 sub-scope carve-up — **structural sibling**: ADR-033 carved one OWASP entry across two host agents at the documentation layer; ADR-034 enriches one OWASP entry across two host agents at the pattern-catalog layer): `docs/architecture/02_ADRs/ADR-033-human-trust-exploitation-agent.md`
