---
description: "Tasks for Feature 145 — Canonical MAESTRO Worked Example"
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-16
    status: APPROVED
    notes: "All 8 evaluation criteria pass. User story coverage complete (US1-11 tasks, US2-15, US3-16, US4-10, US5-22, US6-2). Scope strictly content-authoring. FR-013/FR-014/Feature 082 zero-edit invariants explicitly verified via T045/T046/T047. PM Concerns 1-3 fully resolved (T036 4 security-analyst criteria checkboxes, T035 4 PM tone criteria checkboxes, T051 PRD-FR to spec-FR to wave traceability). Risk 145.4/145.5 converted from directional prose to operational checkable criteria. Healthcare content-risk defense-in-depth via T006 + T029 + T036. P1 Should-Have items correctly absent. Full review: .aod/results/product-manager.md"
  architect_signoff:
    agent: architect
    date: 2026-04-16
    status: APPROVED_WITH_CONCERNS
    notes: "Tasks faithfully implement plan Wave structures, C1/C2/C3 keyword-hygiene (T007/T008/T009 verified against maestro-layers-shared.md L1/L3/L4/L5 keyword tables), FR-005 checklist conditions (T011-T014), Path B frontmatter workflow (T048-T050), byte-determinism protocol (T037-T038), zero-edit invariant verification (T046/T047), fallback ranking (T024-T026), structural DoD (T052). 4.75d critical path within 4-8d PRD budget. Minor citation discrepancies (non-blocking): T012 includes 'delegation' which is not in canonical R-01 description_contains list (additive, harmless — R-01 uses OR); T013 over-constrains R-02 evidence with description keywords (R-02 canonically requires only topology — defensible conservative posture); T014 includes 'feedback loop' not in canonical R-03 list (additive, harmless). T027 iteration cap enforced by task discipline rather than hard gate — recommendation: add dedicated escalation gate if future cycles tighten. No BLOCKING technical issues."
  techlead_signoff:
    agent: team-lead
    date: 2026-04-16
    status: APPROVED_WITH_CONCERNS
    notes: "53 tasks across 8 phases correctly map 4-8d budget and 4.5d pessimistic critical path. Granularity defensible: T004 author-atomicity for Mermaid body is correct (splitting by layer introduces merge risk in single artifact). Wave 4 parallelism M2/L2 correctly split between T028-T032 (parallel with Wave 3) and T033-T034 (gated on Wave 2 output freeze). Fallback ranking M3 correctly ordered (T024 keyword-tune -> T025 extend -> T026 relax LAST RESORT). L4 structural DoD enforced via T052. 5 non-blocking concerns: (1) critical path note about T033/T034 extending beyond Wave 2 Gate — addressed inline; (2) Wave 3 pessimistic 2-round estimate tightened from 1d to 0-1.5d — addressed inline; (3) T028-T032 [P] single-PM-author requires 1.5-2d serialized — noted in Parallel Team Strategy; (4) architect capacity on critical path ~3.5-4.5d contiguous — track Wave 0 availability; (5) T036 dependency on committed T029 + T006 disclaimers implicit but could be explicit. Architect is single-agent capacity risk; mitigated by Wave 4 PM parallelism + fallback cap."
---

# Tasks: Canonical MAESTRO Worked Example

**Input**: Design documents from `specs/145-maestro-canonical-worked-example/`
**Prerequisites**: spec.md (required — PM APPROVED_WITH_CONCERNS), plan.md (required — PM + Architect APPROVED_WITH_CONCERNS), research.md, quickstart.md

**Tests**: Not applicable in the conventional sense — this is a content-authoring feature with no source code to test. Verification is via (a) static architecture review, (b) pipeline output quality gates, (c) byte-identity regression via `pytest tests/scripts/test_backward_compatibility.py`, (d) `/aod.analyze` cross-artifact consistency.

**Organization**: Tasks grouped by execution Wave (matching plan.md Wave structure) with user-story labels ([US1]..[US6]) on tasks serving specific stories. Content-authoring features do not decompose cleanly by story (a single artifact set serves multiple stories), so Wave ordering is primary with story traceability preserved via labels.

## Format: `[ID] [P?] [Story] Description with file path`

---

## Phase 1: Setup (Wave 0 Confirmation + Directory Scaffold)

**Purpose**: Confirm plan-level Wave 0 gate resolutions are held and create the empty example directory.

- [X] T001 Verify plan.md Wave 0 gate resolutions remain held: WG-1 Domain=Option A Healthcare, WG-2 Directory=Option Y flat, WG-3 mmdc CI=N/A (vacuously satisfied). Any reversal of these gates requires returning to `/aod.project-plan`. Confirmation is reading-only — no file edits.
- [X] T002 Create empty directory `examples/maestro-reference/` at the repo root (flat per Option Y — do NOT create a `sample-report/` subdirectory)
- [X] T003 [P] Create empty subdirectory `examples/maestro-reference/attack-trees/` as the per-finding attack tree target

**Checkpoint**: Empty example directory exists at the correct flat path. Ready for architecture authoring.

---

## Phase 2: Foundational

**Purpose**: None — plan-level Wave 0 resolutions (WG-1/WG-2/WG-3) already serve as the foundational gate for this feature. No additional blocking prerequisites.

**Rationale**: Content-authoring features consume existing delivered infrastructure (Phases 1-5 MAESTRO features). No new data models, no migrations, no shared middleware. The only foundational requirement is the plan-sign-off gate, which is satisfied.

**Checkpoint**: All user-story work can now proceed via the Wave 1+ phases below.

---

## Phase 3: Wave 1 — Architecture Authoring

**Goal**: Hand-author `architecture.md` body (Mermaid + Component Summary table + header comment) with all 18 components pre-tuned to satisfy the FR-005 Pre-Execution Architecture Review Checklist by design. NO frontmatter yet (Path B per FR-012).

**Independent Test**: Static review of the committed `architecture.md` confirms all 4 FR-005 conditions green AND architect-review keyword-hygiene items C1/C2/C3 handled.

### Architecture Authoring (serves US-2 cross-layer chains, US-3 canonical comparison, US-5 validation target)

- [X] T004 [US2] [US3] [US5] Author Mermaid `flowchart TD` diagram with 18 components organized into seven MAESTRO-layered subgraphs (User Zone containing L7 user-facing; Ecosystem L7; Agent Frameworks L3; Foundation Models L1; Data Operations L2; Deployment Infrastructure L4; Evaluation & Observability L5; Security & Compliance L6) in `examples/maestro-reference/architecture.md`
- [X] T005 [US2] [US3] [US5] Author Component Summary table below the Mermaid diagram listing every component with DFD element type + MAESTRO layer intent + AI dispatch trigger in `examples/maestro-reference/architecture.md`
- [X] T006 [US2] [US3] [US5] [P] Author architecture.md header comment with domain disclaimer (FR-016 defense-in-depth: "This is a security reference scenario for threat-modeling teaching purposes only; not a real clinical system, no real patient data") in `examples/maestro-reference/architecture.md`
- [X] T007 [US5] **Keyword-hygiene C1** (architect review) — rename "Outcomes Tracking & Physician Override Registry" to an L5-aligned noun that avoids the L4 "registry" keyword collision (recommended: "Outcomes Telemetry & Physician Override Audit Store"); verify description leads with L5 keywords (`monitoring`, `tracing`, `telemetry`, `audit log`, `outcome tracking`) in `examples/maestro-reference/architecture.md`
- [X] T008 [US5] **Keyword-hygiene C2** (architect review) — verify "Diagnostic Agent" description contains at least one L3 phrase keyword (`executor`, `planner`, `tool dispatch`, `orchestrator`) so the component lands at L3 despite bare "agent" not being an L3 keyword in `examples/maestro-reference/architecture.md`
- [X] T009 [US5] **Keyword-hygiene C3** (architect review) — verify "Risk Stratification Model" description contains at least one L1 phrase keyword (`fine-tuned model`, `foundation model`, `base model`, `model weights`, `language model`, `inference engine`) so the component lands at L1 despite bare "model" not being an L1 keyword in `examples/maestro-reference/architecture.md`
- [X] T010 [US5] Verify every other component name + description against its intended MAESTRO layer using the keyword tables in `.claude/skills/tachi-shared/references/maestro-layers-shared.md` — each of the 18 components must hit its intended layer via first-match-wins. Note: L5-before-L6 ordering is load-bearing. Record verification in `examples/maestro-reference/architecture.md` Component Summary table "MAESTRO layer intent" column.

### Pre-Execution Architecture Review Checklist (FR-005 / SC-011)

- [X] T011 [US2] [US5] Verify **Condition 1: Multi-agent gate predicate TRUE** — confirm ≥2 components classified as `agentic`/`llm` (Supervisor Orchestrator, Diagnostic Agent, Treatment Planner Agent all carry LLM+AG keywords) AND (inter-agent data flow Supervisor↔Diagnostic AND Supervisor↔Treatment-Planner exists in Mermaid diagram OR architecture description contains `multi-agent`/`supervisor`/`delegation`/`swarm`/`agent mesh` keywords). Record check in `specs/145-maestro-canonical-worked-example/research.md` appendix.
- [X] T012 [US2] [US5] Verify **Condition 2: R-01 Agent Collusion precondition** — inter-agent data flow between two agentic components explicitly present in the Mermaid diagram (Supervisor↔Diagnostic Agent via Inter-Agent Communication Channel; Supervisor↔Treatment Planner Agent). Verify flow descriptions contain R-01 trigger keywords (`coordinate`, `joint`, `cross-agent`, `inter-agent`, `shared channel`, `shared memory`, `delegation`). Record check in `specs/145-maestro-canonical-worked-example/research.md` appendix.
- [X] T013 [US2] [US5] Verify **Condition 3: R-02 Temporal Attack precondition** — persistent-state component present (Outcomes Telemetry & Physician Override Audit Store per T007 rename) with description containing R-02 keywords (`learning loop`, `feedback loop`, `continual learning`, `re-training`, `drift`, `persistent state`). Record check in `specs/145-maestro-canonical-worked-example/research.md` appendix.
- [X] T014 [US3] [US5] Verify **Condition 4: R-03 Emergent Behavior precondition** — multi-agent topology verified (via Condition 1) AND at least one agentic component description contains R-03 emergent-behavior keywords (`cascade`, `unpredictable`, `interaction`, `emergent`, `feedback loop`). Recommended: Supervisor Orchestrator description mentions "cascading delegation across specialist agents with emergent coordination patterns". Record check in `specs/145-maestro-canonical-worked-example/research.md` appendix.

**Checkpoint (Wave 1 Gate)**: All 4 FR-005 conditions verified green by static review. All 3 architect keyword-hygiene items (C1/C2/C3) handled. `architecture.md` body is ready for pipeline invocation. **No frontmatter committed** (Path B per FR-012).

---

## Phase 4: Wave 2 — Pipeline Run + Output Verification

**Goal**: Run the full existing tachi pipeline end-to-end against the authored `architecture.md` and commit all generated outputs. Verify FR-007 + FR-008 quality gates.

**Independent Test**: After pipeline run, every committed artifact (`threats.md`, `threats.sarif`, `threat-report.md`, `risk-scores.md`, `risk-scores.sarif`, `compensating-controls.md`, `compensating-controls.sarif`, `attack-trees/*`, `attack-chains.md` if chains surface, 6 infographic JPEGs with specs, `security-report.pdf`) is present; output quality gates pass.

### Pipeline Invocation (serves US-2, US-3, US-4)

- [X] T015 [US2] [US3] Run `/tachi.threat-model examples/maestro-reference/` — emits `threats.md`, `threats.sarif`, `threat-report.md`, `attack-trees/<finding-id>-attack-tree.md` per Critical/High finding, `attack-chains.md` (conditional on chain surfacing). Commit outputs under `examples/maestro-reference/`.
- [X] T016 [US2] [US3] Run `/tachi.risk-score examples/maestro-reference/` — emits `risk-scores.md` + `risk-scores.sarif`. Commit outputs.
- [X] T017 [US2] [US3] Run `/tachi.compensating-controls examples/maestro-reference/` — emits `compensating-controls.md` + `compensating-controls.sarif`. Commit outputs.
- [X] T018 [US3] Run `/tachi.infographic all examples/maestro-reference/` — emits 6 JPEGs (baseball-card, system-architecture, executive-architecture, risk-funnel, maestro-stack, maestro-heatmap) + 6 spec `.md` files. Commit outputs.
- [X] T019 [US4] Run `/tachi.security-report examples/maestro-reference/` — emits `security-report.pdf`. Commit output (baseline will be separately regenerated in Wave 5). **Note**: T019 agent applied source-data format fixes (threats.md heading `### 3.1 Spoofing` style, compensating-controls.md duplicate-row removal) to bridge tachi-orchestrator→parser format drift. PDF is 6.4MB / 74 pages, all 6 infographics + 3 chains + MAESTRO findings page. Cover shows "Unknown Project" — minor cosmetic issue, see Wave G carry-forward note in NEXT-SESSION.md.

### Output Quality Gate Verification (FR-007 / FR-008)

- [X] T020 [US3] Verify **FR-007 MAESTRO layer coverage** — `examples/maestro-reference/threats.md` surfaces findings tagged with ≥6 of 7 MAESTRO layers (all 7 preferred). Inspect the MAESTRO Findings section of `examples/maestro-reference/threat-report.md` and count populated per-layer subsections. — **PASS 7/7** per research.md Appendix B T020.
- [X] T021 [US2] Verify **FR-008(b) cross-layer chain surfacing** — `examples/maestro-reference/threat-report.md` Cross-Layer Attack Chains section contains ≥1 chain spanning ≥3 MAESTRO layers. Inspect `examples/maestro-reference/attack-chains.md` to confirm chain member findings trace architectural component lineage. — **PASS 3 chains, max span 5 layers (CHAIN-001)** per research.md Appendix B T021.
- [X] T022 [US3] Verify **FR-008(c) agentic pattern surfacing** — `examples/maestro-reference/threat-report.md` Agentic Pattern Analysis section contains ≥3 of 6 canonical patterns populated with substantive narratives (Agent Collusion, Emergent Behavior, Temporal Attack minimum per FR-005 conditions 2/4/3 respectively). — **PASS 6/6 in threats.md; 5/6 narrated in threat-report.md** per research.md Appendix B T022.
- [X] T023 [US3] Verify **FR-008(a) MAESTRO Findings section populated** — `examples/maestro-reference/threat-report.md` MAESTRO Findings section (Feature 084/091) renders per-layer subsections with populated content. — **PASS per-layer content populated across threat-report.md + threats.md** per research.md Appendix B T023.

**Checkpoint (Wave 2 Gate)**: All 4 output quality gates pass. If any gate fails → proceed to Wave 3 iteration (Phase 5). If all pass → skip Wave 3 and proceed to Wave 4 in parallel.

---

## Phase 5: Wave 3 — Architecture Iteration (Conditional, Capped at 2 Rounds)

**Goal**: If Wave 2 output quality gates fail, iterate on `architecture.md` using the fallback ranking (team-lead M3): (a) keyword-tune → (b) extend architecture → (c) relax FR-004 coverage to 6/7 layers as last resort.

**Independent Test**: Re-running Wave 2 pipeline after Wave 3 iteration produces output that meets T020-T023 gates.

### Iteration Loop (serves US-2, US-3, US-5)

- [X] T024 [US2] [US3] [US5] Skip entirely if all Wave 2 gates pass on first run. Otherwise, apply fallback (a) keyword-tune: edit component names and descriptions in `examples/maestro-reference/architecture.md` to match classification keyword tables. Consult `.claude/skills/tachi-shared/references/maestro-layers-shared.md`, `.claude/skills/tachi-shared/references/maestro-agentic-patterns-shared.md`, `.claude/skills/tachi-shared/references/attack-chain-patterns-shared.md`. Re-run T011-T014 static checklist after tuning. — **SKIPPED (N/A)**: Wave 2 gates T020-T023 all passed on first run.
- [X] T025 [US2] [US3] [US5] (Conditional) If fallback (a) does not close the gap after one iteration, apply fallback (b) extend architecture: add 2-3 additional multi-agent components (e.g., additional specialist agent, additional persistent-state component, additional inter-agent channel) in `examples/maestro-reference/architecture.md`. Re-run T011-T014. — **SKIPPED (N/A)**: Wave 2 gates T020-T023 all passed on first run.
- [X] T026 [US2] [US3] [US5] (Conditional, LAST RESORT) If fallback (b) still does not close the gap, convene architect + team-lead for approval to apply fallback (c) relax FR-004 coverage expectation from 7/7 to 6/7 MAESTRO layers (still satisfies FR-007 which already accepts 6/7). Document the approved relaxation in `specs/145-maestro-canonical-worked-example/research.md` with the specific layer gap and rationale. — **SKIPPED (N/A)**: 7/7 coverage achieved on first run; no relaxation needed.
- [X] T027 [US2] [US3] [US5] (Conditional) Re-run Wave 2 pipeline (T015-T019) after any iteration. Re-verify Wave 2 gates (T020-T023). Iteration cap is 2 rounds — if 2 rounds fail, escalate to architect + team-lead + PM for domain-change or scope adjustment decision. — **SKIPPED (N/A)**: No iteration needed; Wave 2 gates passed on first run.

**Checkpoint (Wave 3 Gate)**: Wave 2 gates pass (either on first run or after ≤2 iteration rounds). If 2 rounds fail, feature scope decision required from Triad before continuing.

---

## Phase 6: Wave 4 — README Authoring (Parallel with Waves 3 and 5)

**Goal**: Hand-author the adopter-facing `README.md` with all 7 required sections (FR-003). Sections 1/2/5/6/7 can be drafted in parallel with Wave 3 iteration (team-lead M2/L2 parallelism opportunity). Sections 3/4 are gated on Wave 2 pipeline output freeze.

**Independent Test**: Reading `examples/maestro-reference/README.md` end-to-end delivers the adopter-facing tour per FR-003; PM tone review passes; security-analyst disclaimer review passes.

### Parallel Sections (can draft during Wave 3 iteration — serve US-1 and US-6)

- [X] T028 [P] [US1] Author **README Section 1 Introduction** (~100-150 words: what the example is, why it exists as canonical MAESTRO walkthrough, expected takeaways) in `examples/maestro-reference/README.md`
- [X] T029 [P] [US1] Author **README Section 2 Domain Overview** (~150-200 words: describe Healthcare CDSS reference scenario, components at a glance, prominent disclaimer per FR-016 "not a real clinical system, no real patient data, no regulatory advice") in `examples/maestro-reference/README.md`
- [X] T030 [P] [US1] Author **README Section 5 Reading-Order Recommendation** ("If you have 5 minutes / 15 minutes / an hour, read X / X+Y / the full PDF") in `examples/maestro-reference/README.md`
- [X] T031 [P] [US6] Author **README Section 6 Compliance Posture Cross-References** (~100-150 words each for AIVSS and NIST AI RMF, linking to `docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md` and `docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md` with accurate decision-noun phrasing) in `examples/maestro-reference/README.md`
- [X] T032 [P] [US1] Author **README Section 7 Limitations and Scope** (what the example does not demonstrate: custom risk weights, organization-specific controls, real-world constraint data, clinical accuracy claims) in `examples/maestro-reference/README.md`

### Output-Dependent Sections (gated on Wave 2 output freeze — serve US-1, US-2, US-3)

- [X] T033 [US3] Author **README Section 3 MAESTRO Layer Coverage Table** (two-column table mapping every component in committed `architecture.md` to its MAESTRO layer(s), enumerating all 18 components) in `examples/maestro-reference/README.md`
- [X] T034 [US1] [US2] Author **README Section 4 What to Look For in Output** (pointers to specific sections and findings in the committed pipeline outputs: layer-tagged findings in `threats.md` Section 7 with Pattern column, specific chain title in `threat-report.md` Section 6, specific patterns in Agentic Pattern Analysis section, MAESTRO stack/heatmap infographic filenames) in `examples/maestro-reference/README.md`

### Wave 4 Review Gates (PM + security-analyst — serve US-1 and Risk 145.4 / 145.5 mitigation)

- [X] T035 [US1] PM tone review of committed `examples/maestro-reference/README.md` against four explicit acceptance criteria (from plan PM review Concern 2 — Risk 145.4 mitigation rigor): **APPROVED** (all 4 criteria PASS)
    - [X] README does not use marketing language ("industry-leading", "best-in-class", "world-class", etc.) — **PASS no violations**
    - [X] README states limitations explicitly in Section 7 (FR-003(g)) — **PASS 5/5 + 1 additional covered**
    - [X] README tone matches existing `examples/README.md` register (factual, matter-of-fact) — **PASS factual register preserved**
    - [X] README does not overclaim MAESTRO completeness — positions tachi as one of several agentic threat-modeling frameworks — **PASS explicit hedging at lines 9 and 114**
    - If any criterion fails, PM returns CHANGES_REQUESTED; author iterates (low-cost iteration, ≤0.5 day per Risk 145.4 contingency).
- [X] T036 [US1] security-analyst review of committed `examples/maestro-reference/README.md` disclaimer prose + `examples/maestro-reference/architecture.md` header disclaimer against four explicit acceptance criteria (FR-017 / SC-014, from plan PM review Concern 1 — Risk 145.5 mitigation rigor): **APPROVED** (all 4 criteria PASS across 7 artifacts scanned)
    - [X] No real patient names appear in any artifact under `examples/maestro-reference/` — **PASS scan across README, architecture, threats, threat-report, risk-scores, compensating-controls, attack-chains**
    - [X] No clinical specialty (e.g., "pediatric oncology") claims diagnostic accuracy — **PASS README:112 explicit negation**
    - [X] No text can be interpreted as regulatory advice (no HIPAA compliance guidance framed as advice, no FDA claims) — **PASS HIPAA/FDA/GDPR/SOC2 only as framework context**
    - [X] Explicit "not a real system" framing is present in both `README.md` Section 2 AND `architecture.md` header comment — **PASS README.md:13 + architecture.md:3 blockquote confirmed**
    - If any criterion fails, security-analyst returns CHANGES_REQUESTED; author iterates before commit.

**Checkpoint (Wave 4 Gate)**: README is committed with all 7 required sections; PM tone review passes; security-analyst disclaimer review passes. All 4 criteria in each review are explicitly checked.

---

## Phase 7: Wave 5 — Baseline Commit + Regression Integration

**Goal**: Regenerate the PDF under `SOURCE_DATE_EPOCH=1700000000`, verify byte-identity across two consecutive regenerations, commit the deterministic baseline, add the example to `BASELINE_EXAMPLES`, and update `examples/README.md`.

**Independent Test**: `pytest tests/scripts/test_backward_compatibility.py` passes on all 6 baselines (5 existing byte-identical, 1 new `maestro-reference` byte-identical).

### Baseline Regeneration (serves US-4)

- [X] T037 [US4] Regenerate `examples/maestro-reference/security-report.pdf.baseline` with `SOURCE_DATE_EPOCH=1700000000` using the two-command sequence documented in `specs/145-maestro-canonical-worked-example/quickstart.md` (extract-report-data.py followed by typst compile). Commit output. — **DONE** commit 342e873 (6.4MB / 74 pages).
- [X] T038 [US4] Run the same two-command sequence a second time producing a temporary PDF at `/tmp/security-report-check.pdf`; run `cmp examples/maestro-reference/security-report.pdf.baseline /tmp/security-report-check.pdf` — MUST be silent (byte-identical). If not silent → do NOT commit the baseline; diagnose determinism regression before proceeding. Clean up `/tmp/security-report-check.pdf` afterward. — **PASS byte-identical**; transient `report-data.typ` + `/tmp/security-report-check.pdf` cleaned up.
- [X] T039 [US4] If byte-identity cannot be achieved after diagnosis, defer FR-011 / SC-013 per Risk 145.3 contingency: do NOT add to `BASELINE_EXAMPLES`; ship example as adopter-facing artifact only; create follow-up GitHub Issue for baseline integration. Document deferral in `specs/145-maestro-canonical-worked-example/research.md`. Skip T040 and T041 in this branch. — **SKIPPED (N/A)**: T038 passed; no deferral needed.

### Regression Suite Integration (serves US-4 — conditional on T038 success)

- [X] T040 [US4] Add `"maestro-reference"` string to the `BASELINE_EXAMPLES` list in `tests/scripts/test_backward_compatibility.py` (currently at lines 38-44) as the sixth entry after `"free-text-microservice"`. Surgical edit — no other changes to this file. — **DONE** commit 342e873 (6th entry added).
- [X] T041 [US4] Run `pytest tests/scripts/test_backward_compatibility.py -v` — verify all 6 parameterized `test_unmodified_examples_byte_identical_pdfs` cases pass. Verify 5 existing baselines (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice) remain byte-identical (FR-013 invariant). Verify `test_feature_142_zero_edit_invariant_on_detection_agents` continues to pass (11 detection agents unmodified — Feature 082 / ADR-026 Decision 1). — **PASS** 13 passed, 1 documented skip (mermaid-agentic-app SC-003 per T033). All 6 byte-identity PDFs pass incl. new maestro-reference; zero-edit invariant on detection agents pass. Follow-up noted: `parse_threats_findings` column-order drift does not read Agentic Pattern column when threats.md emits `| ID | Component | MAESTRO Layer | Agentic Pattern |` order — 21 non-`none` tokens confirmed in threats.md; parser bug out of Feature 145 scope (FR-014 / T047 invariant).

### Examples Directory Cross-Reference (serves US-1)

- [X] T042 [US1] Update `examples/README.md` — add a new row to the "Standardized Examples" table describing the canonical MAESTRO example. Key Demonstration column: "Canonical MAESTRO walkthrough — all 7 layers, cross-layer attack chains, agentic patterns, compliance posture cross-references". Preserve the existing 3 rows (web-app, agentic-app, microservices) unmodified. — **DONE** commit 7ff494b (row 16, 18 components enumerated).
- [X] T043 [US1] Update `examples/README.md` — add a prominent first-read callout near the top of the README directing new MAESTRO-interested adopters to `examples/maestro-reference/README.md` as the recommended first read. Surgical edit — no deletion of existing content. — **DONE** commit 7ff494b (blockquote callout at line 5, factual register).
- [X] T044 [US1] Verify `examples/README.md` "Format-Specific Test Fixtures" 3-row table (ascii-web-api, free-text-microservice, mermaid-agentic-app) is unchanged; verify "Framework Relationship Hierarchy" section is unchanged; verify "Usage Instructions" is unchanged. Only the Standardized Examples table row-addition + first-read callout are in scope. — **VERIFIED** all four preserved sections byte-identical to pre-edit state (PM agent confirmed +3 uniform line shift only). Minor consistency edit applied: "Three polished examples" → "Four polished examples" + "schema v1.1" → "schema v1.1+" (direct consequence of T042 row addition).

### Backward Compatibility Verification (serves US-4, US-5)

- [X] T045 [US4] [US5] Verify no file under `examples/web-app/`, `examples/microservices/`, `examples/ascii-web-api/`, `examples/mermaid-agentic-app/`, `examples/free-text-microservice/`, `examples/agentic-app/` is modified as part of this feature (FR-013, FR-014). Run `git diff --name-only main..HEAD | grep '^examples/' | grep -v '^examples/maestro-reference/' | grep -v '^examples/README.md$'` — MUST be empty. — **PASS empty** (T051 cross-verified).
- [X] T046 [US4] [US5] Verify no file under `.claude/agents/tachi/*.md` is modified as part of this feature (Feature 082 / ADR-026 Decision 1 zero-edit invariant). Run `git diff --name-only main..HEAD | grep '^.claude/agents/tachi/'` — MUST be empty. — **PASS empty** (T051 cross-verified).
- [X] T047 [US4] [US5] Verify no schema, script, template, or dependency file is modified. Run `git diff --name-only main..HEAD | grep -E '^(schemas/|scripts/|templates/|requirements.*\.txt$|pyproject\.toml$|package\.json$)'` — MUST be empty (except `scripts/install.sh` if it was incidentally modified elsewhere — but this feature has no reason to touch it). — **PASS empty** (T051 cross-verified; only additive change outside these paths is `tests/scripts/test_backward_compatibility.py` one-line BASELINE_EXAMPLES addition allowed by T041 / FR-011).

**Checkpoint (Wave 5 Gate)**: PDF baseline is byte-identical on repeat regeneration; 6 baselines pass regression; 5 existing example directories + agentic-app + 11 detection agents + schemas + scripts + templates + dependencies are all unmodified. `examples/README.md` carries the first-read callout. If baseline byte-identity failed, FR-011 is deferred per T039.

---

## Phase 8: Wave 6 — Feature 120 Frontmatter Injection + Final Validation

**Goal**: Freeze the architecture body; invoke `/tachi.architecture` in "create" mode to compute SHA-256 + inject v1.0 frontmatter (FR-012 Path B); run final DoD validation.

**Independent Test**: `/aod.analyze` passes with no cross-artifact inconsistencies; DoD checklist from spec.md and plan.md is fully checked.

### Architecture Frontmatter Injection (serves US-5)

- [X] T048 [US5] Freeze `examples/maestro-reference/architecture.md` body — no further edits to the Mermaid diagram, Component Summary table, or header comment past this point. This is the post-Wave-3 checkpoint mandated by Path B per FR-012. — **FROZEN** at 189 lines committed in 6dfd694 (Waves A-F baseline).
- [X] T049 [US5] Invoke `/tachi.architecture examples/maestro-reference/` in "create" mode — this computes SHA-256 over the frozen body via `shasum -a 256` and injects Feature 120 v1.0 YAML frontmatter (`version: "1.0"`, `date: 2026-04-YY`, `description: ...`, `checksum: sha256:...`, `previous_version: null`) at the top of `examples/maestro-reference/architecture.md`. Commit the frontmatter as a separate commit after the body is frozen (two-pass checksum auditability per plan.md Wave 6 commit sequence). — **DONE** commit 93b5167. Manual frontmatter application using Feature 120 convention since `/tachi.architecture` is codebase-regeneration oriented and would have destroyed the hand-crafted 18-component body; convention verified against command spec Step 3a.
- [X] T050 [US5] Verify Feature 120 v1.0 frontmatter is present with `version: "1.0"`, valid ISO 8601 `date`, non-empty `description`, valid `sha256:` prefixed checksum, and `previous_version: null` (SC-012). Confirm the `.archive/` subdirectory is NOT created (no prior version exists on initial commit). — **PASS all 5 fields**: `version: "1.0"` (string), `date: 2026-04-17`, non-empty description, `checksum: sha256:55f3ba95ca9caea8671696d725de4b6cc30e0d2b56a713c00d9a537bbefa6e8c`, `previous_version: null`. `.archive/` directory confirmed absent.

### Cross-Artifact Consistency Check (serves US-5, US-1 — addresses PM Concern 3)

- [X] T051 Run `/aod.analyze` — verify no cross-artifact inconsistencies between `spec.md`, `plan.md`, `tasks.md`, and the committed artifacts under `examples/maestro-reference/` (FR-018 / SC-010). If any inconsistency surfaces, resolve before proceeding. The analyze report should include a PRD-FR → spec-FR → wave traceability table (per plan PM review Concern 3 recommendation) for future audit. — **PASS with 1 LOW concern**: 18/18 FR→task coverage (100%), 14/14 SC→task coverage (100%), zero-edit invariants verified across other examples + `.claude/agents/tachi/` + schemas/scripts/templates, deliverable inventory complete, constitution aligned, triple sign-off well-formed. LOW concern I1: "L4 Deployment **and** Infrastructure" drift in spec FR-004 / plan Component Inventory / research Appendix vs canonical "L4 Deployment Infrastructure" (Feature 136 naming); not visible in any adopter-facing or pipeline-generated artifact — defer to docs-only housekeeping.

### Structural DoD Discipline Verification (team-lead L4)

- [X] T052 [US4] [US5] Verify **no accidental mixed structure** — confirm `examples/maestro-reference/sample-report/` subdirectory does NOT exist. Run `ls examples/maestro-reference/` and confirm all ~20 artifacts are flat under the root. If a stray `sample-report/` surfaces, relocate contents to flat layout before committing. — **PASS** no `sample-report/` subdirectory; 26 files at flat root (plus `attack-trees/` and `attack-chains/` subdirectories which are expected per plan.md Wave 2 deliverables). Option Y flat structure preserved.

### DoD Checklist Walkthrough

- [X] T053 Walk through the full Definition of Done checklist from `specs/145-maestro-canonical-worked-example/spec.md` (Success Criteria SC-001 through SC-014) and `docs/product/02_PRD/145-maestro-canonical-worked-example-2026-04-16.md` Definition of Done section. Every checkbox MUST be verified green. Any unchecked item blocks `/aod.deliver`. — **ALL 14 SC PASS**:
  - **SC-001** 18 components / 7 layers / ≥2 per layer → T010 verified (architecture.md Component Summary table)
  - **SC-002** ≥1 chain spanning ≥3 layers → T021 verified (3 chains, max span 5 layers per research.md Appendix B)
  - **SC-003** ≥3 of 6 patterns substantive → T022 verified (6/6 in threats.md, 5/6 narrated)
  - **SC-004** ≥6 of 7 layers populated → T020 verified (7/7)
  - **SC-005** 7 sections + neutral tone + PM review → T035 APPROVED (4/4 criteria PASS)
  - **SC-006** examples/README.md row + first-read callout, no removals → T042-T044 commit 7ff494b
  - **SC-007** byte-identical baseline repeat → T037/T038 PASS (`cmp` silent)
  - **SC-008** 5 existing baselines byte-identical → T041 PASS 5/5
  - **SC-009** agentic-app unchanged → T045 empty diff
  - **SC-010** /aod.analyze PASS → T051 PASS with 1 LOW docs-only concern
  - **SC-011** FR-005 4-condition checklist green → T011-T014 research.md Appendix A
  - **SC-012** v1.0 frontmatter + valid SHA-256 → T049/T050 PASS (sha256:55f3ba95...)
  - **SC-013** BASELINE_EXAMPLES + byte-identity passes → T040/T041 PASS (unconditional per plan.md:102; mmdc provisioned locally)
  - **SC-014** security-analyst disclaimer review → T036 APPROVED (4/4 criteria PASS across 7 artifacts)

**Checkpoint (Wave 6 Gate / Final)**: Architecture has v1.0 frontmatter with valid checksum; `/aod.analyze` passes; no mixed structure; all DoD items checked. Feature 145 is ready for `/aod.deliver`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001-T003 — no dependencies, can start immediately after `/aod.tasks` triple sign-off.
- **Foundational (Phase 2)**: No tasks — plan-level Wave 0 resolutions serve as the foundational gate.
- **Wave 1 Architecture Authoring (Phase 3)**: Depends on Phase 1 directory existing. T004 blocks T005-T014; T004-T010 block T011-T014 (checklist needs finalized component names/descriptions).
- **Wave 2 Pipeline Run (Phase 4)**: Depends on Phase 3 Wave 1 Gate (T011-T014 all green). T015 (threat-model) MUST run first; T016-T019 can then run sequentially (some pipeline stages read prior outputs). T020-T023 verify T015-T019 outputs.
- **Wave 3 Iteration (Phase 5)**: Conditional on Wave 2 Gate failure. T024 → T025 → T026 → T027 (cycle).
- **Wave 4 README Authoring (Phase 6)**: T028-T032 can START during Wave 3 iteration (parallel); T033-T034 are gated on Wave 2 Gate pass (need committed pipeline output). T035-T036 gated on all README sections committed.
- **Wave 5 Baseline + Regression (Phase 7)**: Depends on Wave 2 Gate pass AND Wave 4 complete (architecture.md + README.md + pipeline outputs all stable). T037 → T038 → (T039 branch OR T040-T041); T042-T044 in parallel with T037-T041.
- **Wave 6 Frontmatter + Final (Phase 8)**: Depends on all prior waves. T048 → T049 → T050 → T051 → T052 → T053 sequential.

### User Story Dependencies

- **US-1 New Adopter First-Read (P0)**: Primarily served by Wave 4 (README) + Wave 5 `examples/README.md` positioning. Tests: reading committed README + examples/README.md.
- **US-2 Cross-Layer Attack Chain Demo (P0)**: Primarily served by Wave 1 architecture + Wave 2 pipeline → committed `threat-report.md`. Tests: reading Cross-Layer Attack Chains section.
- **US-3 Canonical Comparison Surface (P0)**: Primarily served by Wave 1 architecture + Wave 2 pipeline + Wave 4 README Section 3. Tests: reading Agentic Pattern Analysis + README Section 3.
- **US-4 Regression Fixture (P1)**: Primarily served by Wave 5. Tests: `pytest tests/scripts/test_backward_compatibility.py`.
- **US-5 Validation Target (P1)**: Primarily served by Wave 1 Pre-Execution Checklist (T011-T014) + Wave 6 frontmatter. Tests: static review of architecture.md + `/aod.analyze`.
- **US-6 Compliance Cross-References (P1)**: Primarily served by Wave 4 README Section 6. Tests: reading Section 6 + verifying ADR-024 / ADR-025 links resolve.

All 6 user stories share the same Wave 1-3 architecture work. None are independently shippable as MVP increments — the feature ships as one coherent artifact set.

### Parallel Opportunities

- **Wave 1 setup**: T002 + T003 can run in parallel (different directories).
- **Wave 1 authoring**: T006 (header comment) marked [P] — can be drafted in parallel with the Mermaid body (T004-T005).
- **Wave 4 parallel sections**: T028-T032 all marked [P] — author-parallelism available; these 5 README sections do NOT depend on pipeline output.
- **Wave 5 cross-reference**: T042-T043 (examples/README.md updates) can run in parallel with T037-T041 (baseline regeneration) — different files.

### Critical Path

Phase 1 → Phase 3 (Wave 1) → Phase 4 (Wave 2) → (Phase 5 Wave 3 conditional) → Phase 7 (Wave 5) → Phase 8 (Wave 6). Phase 6 (Wave 4) runs in parallel with the second half of the critical path — T028-T032 parallel-drafting during Wave 3 iteration; T033/T034 extend Wave 4 beyond the Wave 2 Gate (they require committed pipeline output).

**Pessimistic critical path**: 0.25d (Phase 1) + 1.5d (Wave 1) + 1d (Wave 2) + 0-1.5d (Wave 3 conditional, 2 iteration rounds pessimistic) + 0.5d (Wave 5) + 0.5d (Wave 6) = **4.75-5.25 days**, within the 4-8 day PRD budget with ~3-3.25 days of residual contingency. Wave 4 parallel fits in the 4.75-5.25-day envelope; single-PM author scenario requires ~1.5-2d serialized drafting of sections 1/2/5/6/7 + sections 3/4 post-freeze.

---

## Parallel Example: Wave 4 README Authoring

```bash
# During Wave 3 iteration, draft these 5 README sections in parallel:
Task: "Author README Section 1 Introduction (~100-150 words) in examples/maestro-reference/README.md"
Task: "Author README Section 2 Domain Overview with disclaimer (~150-200 words) in examples/maestro-reference/README.md"
Task: "Author README Section 5 Reading-Order Recommendation in examples/maestro-reference/README.md"
Task: "Author README Section 6 Compliance Posture Cross-References (~100-150 words) in examples/maestro-reference/README.md"
Task: "Author README Section 7 Limitations and Scope in examples/maestro-reference/README.md"

# After Wave 2 pipeline output freeze, add the output-dependent sections:
Task: "Author README Section 3 MAESTRO Layer Coverage Table in examples/maestro-reference/README.md"
Task: "Author README Section 4 What to Look For in Output in examples/maestro-reference/README.md"
```

---

## Implementation Strategy

### Wave-by-Wave Delivery

1. **Phase 1 Setup (≤0.25 day)** — scaffold directory
2. **Phase 3 Wave 1 (1-1.5 days)** — hand-author architecture.md body + run FR-005 static checklist
3. **Phase 4 Wave 2 (~1 day)** — run pipeline, verify output gates
4. **Phase 5 Wave 3 (0-1 day conditional, capped at 2 iterations)** — iterate if gates fail
5. **Phase 6 Wave 4 (parallel with Waves 3-5, ~1.5-2 days)** — author README with PM + security-analyst review gates
6. **Phase 7 Wave 5 (~0.5 day)** — regenerate baseline, integrate regression fixture, update examples/README.md
7. **Phase 8 Wave 6 (~0.5 day)** — inject frontmatter, run /aod.analyze, DoD walkthrough

### MVP Increment Note

Unlike conventional features where user stories can ship as incremental MVPs, this content-authoring feature ships as one coherent artifact set. Partial delivery (e.g., README without pipeline output, or pipeline output without README) would create a confusing adopter experience. The wave structure exists to sequence authoring + verification, not to enable partial delivery.

### Parallel Team Strategy

With multiple team members:
- Architect owns Wave 1 (T004-T014)
- Architect owns Wave 2 + Wave 3 pipeline invocation and iteration (T015-T027)
- PM owns Wave 4 T028-T032 parallel sections during architect's Wave 3 iteration (team-lead M2/L2 parallelism opportunity)
- PM owns Wave 4 review gate T035
- security-analyst owns Wave 4 review gate T036
- Architect owns Wave 5 (T037-T047) baseline regeneration + regression fixture
- Architect owns Wave 6 (T048-T053) final validation

---

## Notes

- [P] tasks operate on different files or different sections of the same file with no in-flight edits — can truly run in parallel.
- [Story] labels preserve traceability from tasks back to user stories US-1..US-6; labels are multi-valued for tasks serving more than one story (e.g., T004 serves US-2, US-3, and US-5).
- No unit/integration test tasks were generated — this is a content-authoring feature. Verification is via static review + pipeline output gates + byte-identity regression via pytest + `/aod.analyze`.
- Keyword-hygiene items C1/C2/C3 (architect review, plan Components section) are captured as T007/T008/T009 in Wave 1 to convert three potential Wave 3 iterations into Wave 1 pre-flight checks.
- PM review Concerns 1 + 2 (itemize 4 security-analyst + 4 PM review criteria) are captured as explicit checkboxes in T035 and T036. Risk 145.4 + 145.5 mitigation rigor is now operational, not directional.
- PM review Concern 3 (PRD-FR-to-spec-FR-to-wave traceability) is captured in T051 as a requirement on the `/aod.analyze` report. No plan.md edit was needed.
- Commit after each task or logical group. Maintain a clean commit history for the two-pass checksum auditability (T049 frontmatter injection is its own commit separate from the body commits).
- Stop at any checkpoint gate (Wave 1, Wave 2, Wave 4, Wave 5, Wave 6) to validate before proceeding. Iteration caps and fallback rankings are documented above.
- Avoid: any edit to existing example directories (FR-013/FR-014), any edit to detection-tier agents (Feature 082 / ADR-026), any schema/script/template/dependency change (scope discipline).
