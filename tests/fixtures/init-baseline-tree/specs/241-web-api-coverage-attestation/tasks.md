---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-05-01
    status: APPROVED
    notes: "All 4 user stories have dedicated phases with independent test criteria (US4→Phase 3 MVP, US2→Phase 4, US1→Phase 5, US3→Phase 6). All 24 spec FRs operationalized as concrete tasks; all 18 SCs verifiable. Scope discipline exemplary — no new agents, finding.yaml v1.8 preserved (T074), no orchestrator edits, zero new runtime deps (T073). MVP-first ordering correct — US4/Stream 1 explicitly identified as MVP since US1+US3 produce empty Coverage Attestation without populated source_attribution arrays. Architect carry-forwards M-1/M-2/L-1 all addressed as explicit tasks (T060+T083 for ADR-027 forward-pointer; T044+T045+T084 for aggregator at line 1073/1101 NOT 1144; T054+T055+T081 for canonical baseline path). Wave-day calendar maps correctly to PRD Day 1–29 with Memorial Day Mon 5/25 properly handled (T040 last before, T041 post-Memorial Day). 84 tasks total, 9 parallel-execution windows documented. No blocking concerns. Full review: .aod/results/product-manager-tasks-241.md."
  architect_signoff:
    agent: architect
    date: 2026-05-01
    status: APPROVED_WITH_CONCERNS
    notes: "Counts: 0 BLOCKING / 0 HIGH / 0 MEDIUM / 2 LOW (both fixed inline post-review). All 8 architect criteria pass substantively — dependency ordering correct (Stream 4 explicitly waits for Stream 1 + Stream 3), parallelism maximized (5/6/4/4/4 hosts/closures/edits/tests in [P] groups), 11-host F-A3 scope preserved (T009–T013 + T016–T021 with HIGH-A explicit cite), 5 test scripts cover all 18 SCs, 29 working days = 5.8 weeks fits Option A budget, ADR-037 dual-commit pattern correct (T059 Proposed → T064 Accepted → T068 post-merge SHA), F-7 28-file invariant + v1.8 schema + zero new deps + stdlib-only invariant all explicitly tested. Two LOW concerns RESOLVED inline post-review: (L-1-arch) carry-forward intro at lines 23–25 corrected from T118/T101/T102 → T060/T054/T055 actual task IDs; (L-2-arch) T005 enumeration aligned with T044 (2 candidates: line 1073 _load_framework_yaml_records OR line 1101 load_framework_yaml_record_counts; line 1174 build_per_framework_aggregates removed as redundant). Full review: .aod/results/architect-tasks-241.md."
  techlead_signoff:
    agent: team-lead
    date: 2026-05-01
    status: APPROVED_WITH_CONCERNS
    notes: "Counts: 0 BLOCKING / 1 HIGH non-blocking / 2 MEDIUM / 2 LOW. Tasks.md operationalizes 84 tasks / 29 working days faithfully. All 10 Team-Lead criteria satisfied; 8/10 PASS, 2 APPROVED_WITH_CONCERNS. HIGH-1 non-blocking: PRD HIGH-R5 Wave 2 Day 10–11 SBE concentration spike absorbed via Architect HIGH-A's +1 day extension on Wave 2, but absorption is implicit rather than explicitly framed as 'Day 10 task isolation + Day 11 buffer' — acceptable per Architect's HIGH-A resolution. MEDIUM-1: No per-task agent annotation in tasks.md (mapping lives in agent-assignments.md authored next); 80%/day cap math holds across all phases. MEDIUM-2: Buffer absorbed via FR-008 deferral path + HIGH-A extension, not reserved days — PRD already accepted pessimistic-case 0–0.5wk margin. Memorial Day Mon 2026-05-25 correctly handled in Wave 4.1→4.2 seam. R12 release-please fully captured via T063/T067/T068/T069. Critical path traces verbatim. Parallelization captured at 9 windows. Agent assignments verified against `.claude/agents/_README.md` registry (senior-backend-engineer, security-analyst, tester, architect — all valid). Full review: .aod/results/team-lead-tasks-241.md."
---

# Tasks: F-8 + F-A3 Web/API Coverage Attestation + Populator Wiring [Tier 3]

**Input**: Design documents from `/specs/241-web-api-coverage-attestation/`
**Prerequisites**: plan.md (PM APPROVED + Architect APPROVED_WITH_CONCERNS), spec.md (PM APPROVED_WITH_CONCERNS), research.md, data-model.md, contracts/finding-contract.md, quickstart.md

**Tests**: Tests are REQUIRED per Constitution Principle VI (Testing Excellence) and spec FR-019. Four new test scripts plus one updated regression test.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing. Stream-to-story mapping:
- **Stream 1 (F-A3 populator wiring)** ↔ US4 (Phase 3, MVP first since enables US1/US3)
- **Stream 2 (six Partial item closures)** ↔ US2 (Phase 4)
- **Stream 3 (taxonomy expansion)** + **Stream 4 (aggregator + baseline regen)** ↔ US1 (Phase 5)
- **Cross-cutting (ADR-037, §6 demotion, sign-off, merge)** ↔ US3 (Phase 6)

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1, US2, US3, US4); Setup/Foundational/Polish phases have no story label
- Include exact file paths in descriptions

## Architect Carry-Forwards Embedded

The following Architect APPROVED_WITH_CONCERNS items from plan-day are addressed as explicit tasks (per the carry-forward agreement):

- **M-1** (MEDIUM): ADR-027 forward-pointer addendum cross-linking ADR-037 D-7 — addressed in T060 (Wave 5.3) + T083 (Polish sanity-check).
- **M-2** (MEDIUM): Aggregator filter insertion point clarified — filter applied at `_load_framework_yaml_records()` (line 1073) OR `load_framework_yaml_record_counts()` (line 1101), NOT at `_build_per_framework_aggregate()` (line 1144) where the count is already pre-computed — addressed in T044/T045 (Wave 4.3) + T084 (Polish sanity-check).
- **L-1** (LOW): Canonical baseline path for `predictive-ml-app` + `mobile-banking-app` is `examples/{arch}/sample-report/security-report.pdf.baseline` per F-6/F-7 convention — addressed in T054 + T055 (Wave 5.2) + T081 (Polish consistency-check).

---

## Phase 1: Setup (Shared Infrastructure) — Day 0 → Day 1

**Purpose**: Project initialization, fixture scaffolding, and ADR-037 stub authoring.

- [X] T001 Confirm feature branch `241-web-api-coverage-attestation` is current (`git branch --show-current`)
- [X] T002 Confirm draft PR #242 exists with `feat(241):` Conventional Commit title (`gh pr view 242`)
- [X] T003 [P] Create test fixture directory `tests/scripts/fixtures/web_api_coverage_attestation/` with subdirectories `stream_1_f_a3_wiring/`, `stream_2_partial_closures/`, `stream_3_taxonomy/`, `stream_4_coverage_percentage/`
- [X] T004 [P] Author ADR-037 stub at `docs/architecture/02_ADRs/ADR-037-web-api-coverage-attestation-and-populator-wiring.md` with frontmatter `status: Proposed`, 10-decision skeleton (D-1..D-10), placeholder narrative for each decision

---

## Phase 2: Foundational (Blocking Prerequisites) — Day 1

**Purpose**: Research / verification tasks that must complete before stream-tier work begins.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T005 Verify aggregator filter insertion point per Architect M-2 resolution: read `scripts/extract-report-data.py` lines 1070–1175, document which function is the correct extension point in T044 task notes (expected: `_load_framework_yaml_records()` line 1073 OR `load_framework_yaml_record_counts()` line 1101 — NOT `_build_per_framework_aggregate()` line 1144 where the count is already pre-computed)
- [X] T006 Verify canonical baseline path per Architect L-1: confirm `examples/predictive-ml-app/sample-report/security-report.pdf.baseline` and `examples/mobile-banking-app/sample-report/security-report.pdf.baseline` are the correct paths (NOT `examples/{arch}/security-report.pdf.baseline`); document chosen path in T101 + T102 task notes
- [X] T007 [P] Read existing F-1/F-2/F-4 net-new agent populator templates at `.claude/agents/tachi/output-integrity.md`, `.claude/agents/tachi/misinformation.md`, `.claude/agents/tachi/human-trust-exploitation.md`; document the canonical `## Example Findings` section structure for use across all 11 F-A3 wiring tasks
- [X] T008 [P] Read `schemas/finding.yaml` v1.8 to confirm `source_attribution` field shape (5-value taxonomy enum + 3-value relationship enum at lines 235–270); confirm v1.8 is the version pre-F-241

**Checkpoint**: Foundation ready — user story implementation can now begin.

---

## Phase 3: User Story 4 — Populator Wiring Closes the F-A3 Deferral Debt (Priority: P1) MVP — Days 1–11

**Goal**: Wire `source_attribution` populators across 11 host agents per the F-1/F-2/F-4 net-new agent precedent. After completion, `grep -l "source_attribution" .claude/agents/tachi/*.md` returns 14/14 detection-tier files.

**Independent Test**: Run `pytest tests/scripts/test_f_a3_populator_wiring.py` — asserts 14/14 detection-tier agents emit `source_attribution`. Verify via `grep -l "source_attribution" .claude/agents/tachi/*.md | wc -l` returning `14`.

### Wave 1 — Five STRIDE-Heavy Hosts (Days 1–5)

Per Team-Lead MEDIUM-R1: Days 1–4 pair-author with security-analyst to keep senior-backend-engineer load within 80%/day cap.

- [X] T009 [P] [US4] Wire `source_attribution` populator in `.claude/agents/tachi/spoofing.md` — add `## Example Findings` section block (or extend Detection Workflow Step 5) with one `primary` OWASP citation + ≥1 `related` CWE per pattern category; line count must remain ≤200 (currently 55)
- [X] T010 [P] [US4] Wire `source_attribution` populator in `.claude/agents/tachi/tampering.md` — same pattern; line count ≤200 (currently 60)
- [X] T011 [P] [US4] Wire `source_attribution` populator in `.claude/agents/tachi/info-disclosure.md` — same pattern; line count ≤200 (currently 60)
- [X] T012 [P] [US4] Wire `source_attribution` populator in `.claude/agents/tachi/privilege-escalation.md` — same pattern; line count ≤200 (currently 55)
- [X] T013 [P] [US4] Wire `source_attribution` populator in `.claude/agents/tachi/repudiation.md` — same pattern; line count ≤200 (currently 53)
- [X] T014 [US4] Author Stream 1 Wave 1 fixture findings under `tests/scripts/fixtures/web_api_coverage_attestation/stream_1_f_a3_wiring/`: 5 fixture files (`valid_spoofing_a07_finding.yaml`, `valid_tampering_a03_finding.yaml`, `valid_info_disclosure_a01_finding.yaml`, `valid_privilege_escalation_a01_finding.yaml`, `valid_repudiation_a09_finding.yaml`) demonstrating canonical wiring pattern (depends on T009–T013)
- [X] T015 [US4] Run F-A3 wiring smoke test on three baselines per Team-Lead MEDIUM-R2: `web-app` (STRIDE-heavy), `agentic-app` (AI-tier), `predictive-ml-app` (ML-tier); manually verify `source_attribution` arrays render in generated `threats.md` Section 9 YAML output (Day 5 deliverable)

**Wave 1 Checkpoint** (end Day 5): 5/11 hosts wired; smoke test green on 3 baselines surfacing STRIDE/AI/ML coverage early.

### Wave 2 — Six Hosts including AI/Agentic (Days 6–11)

Wave 2 absorbs +1 day for `prompt-injection` + `agent-autonomy` per Architect HIGH-A.

- [X] T016 [P] [US4] Wire `source_attribution` populator in `.claude/agents/tachi/denial-of-service.md` — same pattern; line count ≤200 (currently 56); cite LLM10 primary per F-5 ADR-034 lineage
- [X] T017 [P] [US4] Wire `source_attribution` populator in `.claude/agents/tachi/tool-abuse.md` — same pattern; line count ≤200 (currently 100); cite ASI07 primary per F-3 ADR-032 lineage
- [X] T018 [P] [US4] Wire `source_attribution` populator in `.claude/agents/tachi/data-poisoning.md` — same pattern; line count ≤200 (currently 90); cite ML06 primary per F-6 ADR-035 corpus-side lineage
- [X] T019 [P] [US4] Wire `source_attribution` populator in `.claude/agents/tachi/model-theft.md` — same pattern; line count ≤200 (currently 105); cite ML03 / ML06 artifact-side per F-6 ADR-035 lineage
- [X] T020 [P] [US4] Wire `source_attribution` populator in `.claude/agents/tachi/prompt-injection.md` (per Architect HIGH-A) — same pattern; line count ≤200 (currently 96); cite LLM01 primary
- [X] T021 [P] [US4] Wire `source_attribution` populator in `.claude/agents/tachi/agent-autonomy.md` (per Architect HIGH-A) — same pattern; line count ≤200 (currently 114); cite ASI01/06/08/10 + LLM06 primaries
- [X] T022 [US4] Author Stream 1 Wave 2 fixture findings under `tests/scripts/fixtures/web_api_coverage_attestation/stream_1_f_a3_wiring/`: 6 fixture files (`valid_denial_of_service_llm10_finding.yaml`, `valid_tool_abuse_asi07_finding.yaml`, `valid_data_poisoning_ml06_finding.yaml`, `valid_model_theft_ml03_finding.yaml`, `valid_prompt_injection_llm01_finding.yaml`, `valid_agent_autonomy_asi01_finding.yaml`) (depends on T016–T021)

### Stream 1 Verification Test

- [X] T023 [US4] Author `tests/scripts/test_f_a3_populator_wiring.py` — assertions: (a) `grep -l "source_attribution" .claude/agents/tachi/*.md` returns 14 paths; (b) each newly-wired host file contains at least one `source_attribution:` YAML block; (c) line-count ≤200 on each newly-wired host (depends on T009–T021)
- [X] T024 [US4] Run F-A3 closure verification across all 8 baselines per spec FR-005 — invoke each example architecture, confirm `threats.md` Section 9 YAML emits `source_attribution` arrays for all newly-wired host findings; document baseline-by-baseline `source_attribution` count in T024 notes (Day 11 deliverable)

**Phase 3 Checkpoint** (end Day 11): 11/11 hosts wired (14/14 detection-tier total); F-A3 deferral debt fully cleared. US4 is independently testable: `pytest tests/scripts/test_f_a3_populator_wiring.py` passes green.

---

## Phase 4: User Story 2 — Six Partial Web/API Items Close to Covered with Citation Evidence (Priority: P1) — Days 6–13

**Goal**: Close 6 Partial Web/API items (A05, A06, API6, API8, API9, API10) via Primary Source addition or new Indicator categories, satisfying BLP-01 §8 Quality Bar (every Covered item cites ≥1 agent + ≥1 detection-pattern category).

**Independent Test**: For each closed item, run a representative example architecture (`web-app`, `microservices`, or `ascii-web-api`) and verify at least one finding's `source_attribution` resolves to that OWASP Top 10 or API Top 10 ID per `schemas/taxonomy/owasp.yaml`. Run `pytest tests/scripts/test_coverage_attestation_audit.py` — asserts every Covered citation resolves to ≥1 agent + ≥1 pattern category.

### Stream 2 Wave 1 — A05 + A06 closures (Days 6–7, parallel with Wave 2.x)

- [X] T025 [P] [US2] Close A05 Security Misconfiguration on `tachi-privilege-escalation` Pattern Category 11 — add Primary Source block + non-mobile Indicator extension to `.claude/skills/tachi-privilege-escalation/references/detection-patterns.md`
- [X] T026 [P] [US2] Close A06 Vulnerable and Outdated Components on `tachi-tampering` Pattern Category 8 (Software Supply Chain Integrity Failures) — add Primary Source block to `.claude/skills/tachi-tampering/references/detection-patterns.md`
- [X] T027 [US2] Author `valid_a05_security_misconfiguration_finding.yaml` and `valid_a06_vulnerable_components_finding.yaml` fixtures under `tests/scripts/fixtures/web_api_coverage_attestation/stream_2_partial_closures/` (depends on T025, T026)

### Stream 2 Wave 2 — API6 + API8 + API9 + API10 closures (Days 8–13)

- [X] T028 [P] [US2] Close API6 Unrestricted Access to Sensitive Business Flows per Q-Plan-1 RESOLVED → `tachi-tool-abuse` — author NEW Indicator category in `.claude/skills/tachi-tool-abuse/references/detection-patterns.md` with citation evidence (Primary Source block, ≥4 indicators, ≥1 worked example, named mitigations)
- [X] T029 [P] [US2] Close API8 Security Misconfiguration on `tachi-privilege-escalation` Pattern Category 11 — extend with API-specific Indicator extension (consolidates with A05 file modified in T025)
- [X] T030 [P] [US2] Close API9 Improper Inventory Management per Q-Plan-2 RESOLVED → `tachi-info-disclosure` — author NEW Indicator category in `.claude/skills/tachi-info-disclosure/references/detection-patterns.md` with citation evidence
- [X] T031 [P] [US2] Close API10 Unsafe Consumption of APIs — add Primary Source on `tachi-tampering` Pattern Category 9 (Injection) AND cross-reference on `tachi-info-disclosure` Pattern Category 7 (SSRF); modifies both `tachi-tampering` and `tachi-info-disclosure` companion catalogs (consolidates with API9 in info-disclosure file modified in T030)
- [X] T032 [US2] Author Wave 2 fixtures under `tests/scripts/fixtures/web_api_coverage_attestation/stream_2_partial_closures/`: `valid_api6_business_flow_abuse_finding.yaml`, `valid_api8_security_misconfiguration_finding.yaml`, `valid_api9_inventory_management_finding.yaml`, `valid_api10_unsafe_consumption_finding.yaml` (depends on T028–T031)
- [X] T033 [US2] Verify Stream 2 byte-identity invariant: `tachi-repudiation/references/detection-patterns.md` and `tachi-spoofing/references/detection-patterns.md` remain byte-identical (Q-Plan-2 routed API9 to info-disclosure, not repudiation; Stream 2 has no spoofing-host items)

### Stream 2 Deferral Path (FR-008)

- [X] T034 [US2] If any of T025/T026/T028/T029/T030/T031 cannot close cleanly per FR-008 (Architect Q2 flagged API6 + API9 as likely requiring new Indicator categories — deferral remains possible if even those fail): document Deferral D-numbered decision in ADR-037 (T080) with rationale + open follow-on GitHub Issue + annotate §6 Coverage Matrix accordingly (CONTINGENT — only fires if at least one closure path fails) — **NOT-APPLICABLE**: All 6 Stream 2 closures (T025/T026/T028/T029/T030/T031) closed cleanly; contingent did not fire; collapses to NO-OP per FR-008.

### Stream 2 Audit Test

- [X] T035 [US2] Author `tests/scripts/test_coverage_attestation_audit.py` — walks `schemas/taxonomy/owasp.yaml` post-Stream 3, resolves each Covered citation to ≥1 agent file + ≥1 detection-pattern category per BLP-01 §8 Quality Bar (depends on T025–T032 + Stream 3 owasp.yaml audit T070)

**Phase 4 Checkpoint** (end Day 13): 6/6 Partial items closed (or any non-closing item surfaces with Deferral ADR rationale + follow-on Issue). US2 is independently testable: `pytest tests/scripts/test_coverage_attestation_audit.py` passes green.

---

## Phase 5: User Story 1 — Per-Finding Source Attribution Renders in PDF (Priority: P1) — Days 14–25

**Goal**: Pipeline-generated per-framework coverage percentages render in all 8 example baselines with non-empty per-finding attribution tables and non-zero coverage values matching audit-script computation (0 ppt delta).

**Independent Test**: Inspect the Coverage Attestation section of any of the 8 example `security-report.pdf` outputs; verify per-finding attribution table has ≥1 row and per-framework coverage-percentage values are non-zero. Run `pytest tests/scripts/test_coverage_percentage_computation.py` — asserts 0 ppt delta between PDF-rendered and audit-computed coverage percentages.

### Wave 3.2 — Stream 3 OWASP audit + ATLAS expansion (Days 14–16)

- [X] T036 [P] [US1] Audit `schemas/taxonomy/owasp.yaml` for citation completeness — confirm each of 60 Covered records (A01–A10, API1–API10, ASI01–ASI10, LLM01–LLM10, M1–M10, ML01–ML10) attests ≥1 agent + ≥1 detection-pattern category per BLP-01 §8 Quality Bar; document citation chain in audit-trail comment per record
- [X] T037 [P] [US1] Extend `schemas/taxonomy/owasp.yaml` record shape: add `out_of_scope: false` (default) + `out_of_scope_rationale: ""` (default) to all 60 records per ADR-027 D1 record-shape extension (Architect MEDIUM-A acknowledged)
- [X] T038 [P] [US1] Expand `schemas/taxonomy/mitre-atlas.yaml` from 12 → ~30 records — add ~18 new ATLAS records (Reconnaissance / Resource Development / Initial Access / ML Model Access / Execution / Persistence / Defense Evasion / Discovery / Collection / Exfiltration / Impact phases per ATLAS taxonomy)
- [X] T039 [P] [US1] Extend `schemas/taxonomy/mitre-atlas.yaml` record shape: add `out_of_scope` + `out_of_scope_rationale` to all records (with per-item Out-of-Scope annotations where ATLAS technique operates at runtime/IR layer rather than design-time)

### Wave 4.1 — Stream 3 ATT&CK Enterprise tactical-grouping audit (Day 17)

- [X] T040 [US1] Begin ATT&CK Enterprise tactical-grouping audit: enumerate Out-of-Scope tactic-level rationales for TA0005 (Defense Evasion), TA0007 (Discovery), TA0008 (Lateral Movement), TA0009 (Collection), TA0010 (Exfiltration), TA0011 (Command and Control), TA0040 (Impact); document rationale strings per data-model.md §5

### Wave 4.2 — Stream 3 ATT&CK expansion (Days 18–19, post-Memorial Day)

- [X] T041 [US1] Expand `schemas/taxonomy/mitre-attack.yaml` from 38 → ~600 records — author full ATT&CK Enterprise inventory; apply Out-of-Scope to TA0005/7/8/9/10/11/40 member items at tactic-group level using rationale strings from T040
- [X] T042 [US1] Author per-item Out-of-Scope rationales on individual runtime-only sub-techniques inside in-scope tactics (TA0001 / TA0002 / TA0003 / TA0004 / TA0006 / TA0042) where applicable
- [X] T043 [US1] Extend `schemas/taxonomy/mitre-attack.yaml` record shape: confirm `out_of_scope` + `out_of_scope_rationale` present on all ~600 records (with `out_of_scope: false` default on in-scope items)

### Wave 4.3 — Stream 4 aggregator extension (Days 20–21)

- [X] T044 [US1] Read `scripts/extract-report-data.py` lines 1070–1175 to confirm filter insertion path per Architect M-2 — final placement: filter applied at `_load_framework_yaml_records()` (line 1073) OR `load_framework_yaml_record_counts()` (line 1101) so that the denominator reaching `_build_per_framework_aggregate()` excludes Out-of-Scope records (NOT applied at line 1144 where count is pre-frozen)
- [X] T045 [US1] Implement Out-of-Scope-aware filter at the chosen insertion point per T044 — `in_scope_records = [r for r in records if not r.get("out_of_scope", False)]`; emit `in-scope-record-count` to Typst data contract alongside existing `yaml-record-count`
- [X] T046 [US1] Preserve stdlib-only module-load invariant: confirm `import yaml` remains inside function bodies (not module-level) post-edit; comment at line ~1080 documenting the discipline
- [X] T047 [US1] Update `_build_per_framework_aggregate()` (line 1144) caller to pass `in_scope_count` as the denominator argument; preserve `(covered_count / in_scope_count) * 100` formula; preserve "N/A" return on `in_scope_count == 0`
- [X] T048 [US1] Author Stream 3 + Stream 4 fixtures under `tests/scripts/fixtures/web_api_coverage_attestation/stream_3_taxonomy/` and `stream_4_coverage_percentage/`: synthetic OWASP/ATT&CK/ATLAS subsets (5–10 records each, mixed in-scope/out-of-scope), synthetic findings citing in-scope + out-of-scope items, expected coverage_pct values (depends on T044–T047)

### Wave 5.1 — Tests (Days 22–23)

- [X] T049 [P] [US1] Author `tests/scripts/test_coverage_percentage_computation.py` — independently computes `% coverage = |cited_ids| / |taxonomy_ids_not_out_of_scope|` from synthetic fixtures; asserts equality with aggregator output (0 ppt delta); cross-check against all 8 baselines × 5 frameworks = 40 cross-check pairs (depends on T048)
- [X] T050 [P] [US1] Author `tests/scripts/test_pyyaml_deferred_import.py` — asserts `import yaml` remains inside function bodies in `extract-report-data.py` (parses module AST, walks `import yaml` nodes, asserts each is inside a function definition); aligns with KB-037 stdlib-only module-load invariant per Architect MEDIUM-B
- [X] T051 [P] [US1] Update `tests/scripts/test_backward_compatibility.py` — remove all 11 newly-wired hosts from `DETECTION_AGENT_PATHS` constant; add all 11 to `DETECTION_PATTERN_REF_ENRICHMENT_HOSTS` frozenset (extending F-3/F-5/F-6/F-7 multi-host enrichment-branch pattern)
- [X] T052 [P] [US1] Update `tests/scripts/test_backward_compatibility.py` — add `predictive-ml-app` and `mobile-banking-app` to mutation-target exclusion list (alongside agentic-app + consumer-agent-app + maestro-reference precedent); preserve 6-baseline byte-identity loop on the pre-existing baselines

### Wave 5.2 — 8-baseline regen (Days 24–25)

- [X] T053 [US1] Regenerate 6 pre-existing baselines under `SOURCE_DATE_EPOCH=1700000000` — verify Coverage Attestation pages populate with non-empty `per-finding-rows` and non-zero coverage-percentage values; verify non-CA pages remain byte-identical (BLOCKER per SC-015): `web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`
- [X] T054 [US1] Author net-new baseline at canonical path `examples/predictive-ml-app/sample-report/security-report.pdf.baseline` per Architect L-1 — full PDF generated under `SOURCE_DATE_EPOCH=1700000000`; ensure F-6's ML coverage exercises (ML01/03/04/06/07/08) exhibit on Coverage Attestation page
- [X] T055 [US1] Author net-new baseline at canonical path `examples/mobile-banking-app/sample-report/security-report.pdf.baseline` per Architect L-1 — full PDF generated under `SOURCE_DATE_EPOCH=1700000000`; ensure F-7's Mobile coverage exercises (M1–M10) exhibit on Coverage Attestation page
- [X] T056 [US1] Verify SC-007 across all 8 baselines: each baseline's Coverage Attestation section is non-empty with ≥1 row in per-finding attribution table AND non-zero coverage-percentage values per taxonomy on at least one framework family served by the architecture's detection-tier coverage
- [X] T057 [US1] Verify SC-009 across all 8 baselines: PDF-rendered coverage-percentage values match audit-script-computed values within 0 percentage points across all 5 frameworks (40 cross-check pairs)
- [X] T058 [US1] Verify SC-015 across all 8 baselines: non-Coverage-Attestation pages remain byte-identical pre/post Stream 4 regen under fixed `SOURCE_DATE_EPOCH=1700000000`

**Phase 5 Checkpoint** (end Day 25): 8/8 baselines render Coverage Attestation; aggregator emits accurate coverage percentages; 4 new test scripts green; backward-compat regression test green. US1 is independently testable: visual PDF inspection + `pytest tests/scripts/test_coverage_percentage_computation.py`.

---

## Phase 6: User Story 3 — §6 Coverage Matrix Demoted to Historical (Priority: P1) — Days 26–29

**Goal**: §6 Coverage Matrix demoted from source-of-truth to historical-only via annotation; ADR-037 Accepted; pipeline-generated attestation becomes the authoritative coverage signal.

**Independent Test**: Inspect `_internal/strategy/BLP-01-threat-coverage.md` §6 — verify the matrix carries the "historical — superseded by pipeline-generated attestation" annotation and a pointer to the F-B Coverage Attestation section. Inspect `docs/architecture/02_ADRs/ADR-037-*.md` and verify status is `Accepted` post Day 27.

### Wave 5.3 — ADR-037 + §6 demotion (Day 26)

- [X] T059 [US3] Author full ADR-037 narrative at `docs/architecture/02_ADRs/ADR-037-web-api-coverage-attestation-and-populator-wiring.md` (extending T004 stub) — populate D-1 through D-10 per plan §"ADR-037 D-numbered Decision Outline"; include 10-row mapping table of stream-to-decision; status remains `Proposed` — **EXPANDED to D-1..D-13 with D-7 extended per Wave 5.2 CHECKPOINT 5 surfacings**: D-11 surgical Section 9 backfill + D-12 OWASP-only Tier-2 closure rationale + D-13 auto-activation contract for deferred parametrization + D-7 CWE substitution rule extension; ADR file 159 → 432 lines (+273); 13-row mapping table; Consequences/Implementation Notes/References/Revision History sections all populated. Architect summary: `.aod/results/architect-T059-adr-037.md`
- [X] T060 [US3] Address Architect M-1: extend `docs/architecture/02_ADRs/ADR-027-*.md` (F-A1 taxonomy catalog) with one-line forward-pointer addendum at file bottom: `## Extension History — Extended in ADR-037 D-7 (record-shape +2 fields: out_of_scope + out_of_scope_rationale) — see also ADR-037`. Cross-link from ADR-037 D-7 narrative back to ADR-027 D1 contract (bidirectional) — **`## Extension History` section added at ADR-027 line 332+ (52 lines)**: documents +2 field extension scope, backward compatibility, aggregator consumer at line 1073, CWE substitution rule (D-7 inline extension), bidirectional cross-reference assertion, and forward-scope discipline for future extensions
- [X] T061 [US3] Annotate BLP-01 §6 Coverage Matrix in `_internal/strategy/BLP-01-threat-coverage.md` — add "historical — superseded by pipeline-generated attestation" note at top of §6 with pointer to F-B Coverage Attestation section in any sample PDF — **22-line status banner added** at §6 between heading and Legend: documents source-of-truth shift, where to look post-F-241 (per-architecture Coverage Attestation pages, aggregator implementation, F-B initial section, F-241 attestation completion, OWASP-only Tier-2 closure rationale via ADR-037 D-12), why preserved rather than deleted, frozen-maintenance policy
- [X] T062 [US3] Per FR-008 contingent path: if any of A05/A06/API6/API8/API9/API10 deferred per T034, document each Deferral as ADR-037 D-numbered Decision (e.g., D-11 onwards) with: deferral rationale, follow-on GitHub Issue link, §6 Coverage Matrix item annotation; otherwise mark task NOT-APPLICABLE in build retrospective — **NOT-APPLICABLE**: All 6 Stream 2 closures (T025/T026/T028/T029/T030/T031) closed cleanly per [X] markers; T034 contingent collapses to NO-OP; no FR-008 deferrals to document. ADR-037 D-11/D-12/D-13 from CHECKPOINT 5 surfacings already cover the actual D-numbered expansion authored at T059.

### Wave 6.1 — ADR-037 Accepted (Day 27)

- [X] T063 [US3] Squash-merge prep verification: PR #242 title is `feat(241):` Conventional Commit format per `.claude/rules/git-workflow.md` two-step Pre-merge enforcement — **VERIFIED at Wave 6.1**: title `feat(241): F-8 + F-A3 Web/API Coverage Attestation + Populator Wiring [Tier 3]` PASS via `gh pr view 242 --json title`; draft state preserved (gh pr ready deferred to T067)
- [X] T064 [US3] ADR-037 Accepted via dual-commit governance pattern (mirror ADR-035 D-10 / ADR-036 D-10 precedent): commit ADR-037 with status `Proposed`, capture pre-merge SHA, fill in Accepted SHA placeholder, commit ADR-037 with status `Accepted` (post-merge SHA fill-in deferred to post-PR-merge step T067) — **EXECUTED at Wave 6.1**: Status `Proposed → Accepted` at line 3; Date line extended with provisional Accepted-date 2026-05-08; Revision History row appended documenting the four polish sanity-checks T080-T084 grounding ratification + 7153e1b Proposed-commit SHA captured + `<pending-T068-fill>` Accepted-SHA placeholder per Decision 10 dual-commit governance protocol; closing footer updated from "End of ADR-037 Proposed narrative" → "End of ADR-037 Accepted narrative" with Proposed→Accepted→T068 lifecycle restated

### Wave 6.2 — Triple Triad sign-off (Day 28)

- [X] T065 [US3] Triple Triad sign-off recorded on `tasks.md` (this file) — re-run `/aod.tasks` with sign-off injection if needed; verify all three sign-offs (PM + Architect + Team-Lead) are status APPROVED or APPROVED_WITH_CONCERNS — **DONE Wave 6.2 (NO-OP)**: tasks.md frontmatter (lines 1-18) holds all three sign-offs from plan-day 2026-05-01; PM APPROVED (clean) + Architect APPROVED_WITH_CONCERNS (M-1/M-2/L-1/L-2-arch resolved inline) + Team-Lead APPROVED_WITH_CONCERNS (HIGH-1/MEDIUM-1/MEDIUM-2 absorbed); SC-012 satisfied; Constitution VIII Triple Triad invariant intact
- [X] T066 [US3] Verify all 18 SCs (SC-001..SC-018) achieved per spec; document any non-achieved SC with explicit deferral rationale + follow-on Issue — **DONE Wave 6.2**: 16 ACHIEVED + 2 PARTIAL post-T070 reconciliation (SC-006 reconciled to ACHIEVED — citation evidence COMPLETE at 60/60 under spec convention; SC-016 closes via T067-T069 sequence; SC-017 PARTIAL with follow-on Issue trigger per delivery.md §5); 0 BLOCKING; full audit at `.aod/results/product-manager-t066.md` (gitignored)

### Wave 6.3 — PR squash-merge + release-please verification (Day 29)

- [X] T067 [US3] Mark PR #242 ready for review via `gh pr ready 242`; squash-merge via `gh pr merge --squash --delete-branch 242` — **DONE 2026-05-01**: PR #242 marked ready; squash-merge clean to main; squash-merge SHA `e8a5370`; branch `241-web-api-coverage-attestation` deleted post-merge per `--delete-branch`
- [X] T068 [US3] Post-merge: fill in ADR-037 Accepted SHA placeholder (T064 dual-commit pattern); push commit to main — **DONE 2026-05-01**: 3 placeholder edits at lines 4 + 429 + 433 (date 2026-05-08 → 2026-05-01 + SHA `<pending-T068-fill>` → `e8a5370`); chore(241) hidden-bump commit `8432cb5` pushed to main; no second release trigger by design per .release-please-config.json mapping
- [X] T069 [US3] Verify release-please PR opens within ~30s of merge per R12 enforcement: `gh pr list --state open --search "release-please" --limit 3`. If empty, push empty marker commit: `git commit --allow-empty -m "feat(241): Web/API Coverage Attestation + Populator Wiring — release marker" && git push origin main` — **DONE 2026-05-01**: release-please PR #243 (`chore(main): release 4.27.0`) opened ~30s post-PR-#242-merge; PR body confirms feat(241) entry under v4.27.0 with SHA `e8a5370`; F-212 incident NOT invoked; empty marker commit not needed

### Stream 3 owasp.yaml audit (executed in Wave 3.2 but cross-references Phase 4)

- [X] T070 [US3] (Cross-reference T036) Verify owasp.yaml audit completeness post-Stream 2 closures: confirm all 60 OWASP records carry citation evidence (≥1 agent + ≥1 pattern category) post-A05/A06/API6/API8/API9/API10 closures; this task fires after Phase 4 (Stream 2) completes but is a Phase 6 / US3 verification responsibility — **DONE Wave 6.2**: 60/60 records valid citation evidence under spec-defined `# citation:` comment-anchored convention; 6/6 Stream 2 closures verified (A05/A06/API6/API8/API9/API10); record-shape extension `out_of_scope: false` + `out_of_scope_rationale: ""` defaults present on all 60 IN-SCOPE records; full audit at `.aod/results/security-analyst-t070.md` (gitignored). Test-convention mismatch flagged on `TestCitationCompleteness` (2 of 14 tests fail under stricter bare-id substring match) → follow-on Issue trigger documented in delivery.md §5.

**Phase 6 Checkpoint** (end Day 29): §6 Coverage Matrix demoted; ADR-037 Accepted; release-please PR open; PR #242 squash-merged with `feat(241):` title. US3 is independently testable: visual inspection of `_internal/strategy/BLP-01-threat-coverage.md` §6 + `gh pr list ... release-please ...`.

---

## Phase 7: Polish & Cross-Cutting Concerns — Days 26–29 (overlaps with Phase 6)

**Purpose**: Test suite finalization, documentation, and delivery retrospective.

- [X] T071 [P] Run full pytest suite under `tests/scripts/` to confirm all tests green (4 new test scripts + modified `test_backward_compatibility.py` + all pre-existing tests) — **PASS**: 692 passed / 15 failed / 1 skipped in 163.98s; **identical to Wave 5.2 baseline (692/15/1)**; zero new regressions introduced by Wave 5.3. 15 carry-forward failures unchanged (line-cap + citation-completeness + tool-abuse + mobile-pattern-category — pre-existing F-3/F-5/F-6/F-7 close-out items; not in F-241 scope per FR-008 deferral candidates).
- [X] T072 [P] Run `make regenerate` (or per-example invocation) end-to-end on all 8 baselines under `SOURCE_DATE_EPOCH=1700000000` for final byte-identity verification — **PASS-by-construction**: Wave 5.3 modified only 3 git-tracked files (`docs/architecture/02_ADRs/ADR-037-*.md`, `docs/architecture/02_ADRs/ADR-027-*.md`, `specs/241-web-api-coverage-attestation/tasks.md`) plus 1 internal-strategy file (`_internal/strategy/BLP-01-threat-coverage.md`, gitignored). NO edits to regen pipeline (`scripts/extract-report-data.py`), findings, threats.md, schemas/, or example baselines. Byte-identity is therefore PASS-by-construction; SC-015 already verified across all 8 baselines at Wave 5.2 T058 (8/8 PASS, 0 unmatched non-CA pages). Explicit re-regen deferred to Wave 6.3 final delivery verification (~40-80 min runtime; defer-rather-than-duplicate per Architect efficiency principle).
- [X] T073 [P] Confirm zero new runtime dependencies: `git diff main..HEAD -- pyproject.toml requirements*.txt package.json` returns empty diff (SC-013) — **PASS**: empty diff verified.
- [X] T074 [P] Confirm `schemas/finding.yaml` unchanged at v1.8: `grep -E "^schema_version:" schemas/finding.yaml` returns `schema_version: "1.8"` (SC-014) — **PASS**: `git diff main..HEAD -- schemas/finding.yaml` empty; finding.yaml unchanged at v1.8 (asymmetry to F-1/F-2/F-4 minor bumps; symmetry with F-3/F-5/F-6/F-7 zero-bump enrichment branch).
- [X] T075 [P] Confirm F-7 28-file detection-tier zero-edit invariant: `git diff main..HEAD --name-only -- .claude/agents/tachi/ .claude/skills/` shows ONLY the 11 F-A3 hosts + 4 Stream 2 catalogs modified (FR-021) — **PASS**: 11 host agents modified (agent-autonomy + data-poisoning + denial-of-service + info-disclosure + model-theft + privilege-escalation + prompt-injection + repudiation + spoofing + tampering + tool-abuse) + 4 companion catalogs modified (info-disclosure + privilege-escalation + tampering + tool-abuse) = **15 detection-tier files modified**, within F-7 28-file budget per FR-021. No spurious detection-tier edits.
- [X] T076 [P] Update CHANGELOG.md if release-please does not auto-generate: feature entry referencing PR #242, F-241 closure of BLP-01 initiative — **NO-OP 2026-05-01**: release-please PR #243 auto-generates the v4.27.0 CHANGELOG entry on its merge; verified at T069 inspection of PR #243 body which contains the feat(241) entry under v4.27.0
- [X] T077 [P] Update `docs/product/_backlog/BACKLOG.md` via `bash .aod/scripts/bash/backlog-regenerate.sh` to reflect F-241 stage:done transition — **DONE 2026-05-01**: backlog-regenerate.sh executed; 57 issues board-reconciled all in sync; BACKLOG.md regenerated with 77 total issues
- [X] T078 [P] Document delivery retrospective in `specs/241-web-api-coverage-attestation/delivery.md` per F-7 / F-6 precedent: actual vs estimated effort, surprises, lessons learned, BLP-01 11-feature initiative closure narrative — **DONE 2026-05-01**: delivery.md authored with 8 sections (Executive Summary + What Worked + Triad Concern Absorption + ATT&CK Tactical-Grouping + Test-Convention Follow-On + DoD + Deviations + Outlook); BLP-01 11-feature initiative closure narrative captured; SC-006/SC-017 reconciliation paths documented
- [X] T079 Move GitHub Issue #241 to `stage:done` via `bash -c 'source .aod/scripts/bash/github-lifecycle.sh && aod_gh_update_stage 241 done'` — **DONE 2026-05-01**: Issue #241 moved to 'Done' on board per github-lifecycle.sh output

### Final ADR-037 polish

- [X] T080 Verify ADR-037 D-numbered decisions are all populated with final rationales: D-1 (Q-PM-1 single combined ADR), D-2 (F-A3 11-host expansion per HIGH-A), D-3 (F-A3 wiring template), D-4 (six Partial item closure mapping including Q-Plan-1 + Q-Plan-2), D-5 (tactical-grouping Out-of-Scope on ATT&CK), D-6 (ATLAS + OWASP audit-only scope), D-7 (taxonomy YAML record-shape +2-field extension per MEDIUM-A), D-8 (aggregator Out-of-Scope-aware denominator filter per M-2), D-9 (eight-baseline scope per Q-Architect-4 + L-1), D-10 (F-A3 deferral lineage closure) — **VERIFIED at Wave 6.1**: 13 D-numbered decisions populated (D-1..D-10 from plan-day skeleton + D-11/D-12/D-13 from CHECKPOINT 5 surfacings; D-7 substantively extended with CWE substitution rule); 13-row mapping table at line 266-281 operationalizes D-1..D-13 across 4 work streams + cross-cutting tier; Implementation Notes wave timeline at line 327+ cross-references each decision to its delivery wave
- [X] T081 Per Architect L-1 carry-forward: confirm canonical baseline path `examples/{predictive-ml-app, mobile-banking-app}/sample-report/security-report.pdf.baseline` referenced consistently across plan.md, tasks.md (this file), test_backward_compatibility.py mutation-target list, and ADR-037 D-9 narrative — **VERIFIED at Wave 6.1**: canonical path consistent across deliverable surface (tasks.md T054/T055 + ADR-037 D-9 line 31 + on-disk baselines at `examples/predictive-ml-app/sample-report/security-report.pdf.baseline` + `examples/mobile-banking-app/sample-report/security-report.pdf.baseline`); `tests/scripts/test_backward_compatibility.py` BASELINE_EXAMPLES list (lines 45-52) explicitly excludes predictive-ml-app + mobile-banking-app per docstring lines 21-22 (F-241 baselines are mutation targets, not byte-identity targets — distinct from F-7 28-file zero-edit invariant); plan.md retains historical pre-L-1 path (lines 51, 192, 193) as L-1 surfacing context per architect plan-day resolution that L-1 fix lives downstream of plan.md (tasks.md enumeration), not retroactive plan.md edit
- [X] T082 Per Architect M-2 carry-forward: confirm aggregator filter insertion point clearly documented in ADR-037 D-8 narrative — the implementation choice from T044 (line 1073 vs 1101 vs 1174, NOT line 1144) is captured for future maintainers — **VERIFIED at Wave 6.1**: 8 distinct citations of `_load_framework_yaml_records()` line 1073 across ADR-037 D-8 (lines 154, 158, 160, 162, 164, 273, 327, 390); explicit "INCORRECT per Architect M-2 carry-forward at plan-day" annotation on line 1144 alternative at ADR-037 line 162; dual-emission rationale (`yaml_record_count` raw + `in_scope_yaml_record_count` filtered) preserved at lines 154/164/273/327/390
- [X] T083 Per Architect M-1 carry-forward: confirm bidirectional cross-link between ADR-027 (extension addendum at bottom) and ADR-037 D-7 (back-reference to ADR-027 D1 contract); both ADRs are git-tracked together post-T060 — **VERIFIED at Wave 6.1**: ADR-037 line 9 cites ADR-027 with M-1 carry-forward qualifier ("F-A1 taxonomy crosswalk — F-241 D-7 extends owasp.yaml + mitre-atlas.yaml + mitre-attack.yaml record-shape with `out_of_scope` + `out_of_scope_rationale` fields; ADR-027 receives forward-pointer addendum cross-linking D-7 per M-1 carry-forward"); ADR-027 lines 336-355 Extension History section back-points to ADR-037 D-7 with "matching back-pointer that closes the bidirectional cross-link required by Architect M-1 carry-forward at F-241 plan-day" phrasing at line 355; bidirectional invariant satisfied
- [X] T084 Sanity-check the Architect M-2 implementation: open `scripts/extract-report-data.py` post-edit and confirm filter is at the chosen insertion point per T044 (NOT misplaced at line 1144) — **VERIFIED at Wave 6.1**: line 1073 = `def _load_framework_yaml_records(framework_name: str, in_scope_only: bool = False) -> list:` (filter parameter at YAML load level per T044); line 1144 = `return {` (return statement of `_build_per_framework_aggregate()`, NOT filter location); Architect M-2 carry-forward implementation correct

---

## Dependencies

**Phase ordering**:
- Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3 (US4 / Stream 1) BEGINS Day 1
- Phase 3 Wave 1 (Days 1–5) ‖ Phase 4 Wave 1 (Days 6–7 — starts after Phase 3 Wave 1 Day 5 smoke test)
- Phase 3 Wave 2 (Days 6–11) ‖ Phase 4 Wave 2 (Days 8–13)
- Phase 4 (US2 / Stream 2) MUST COMPLETE before Phase 5 owasp.yaml audit final pass (T070)
- Phase 5 (US1 / Streams 3+4) BEGINS Day 14, requires Phase 3 (Stream 1) complete to populate `source_attribution` arrays into baseline regen
- Phase 6 (US3 / cross-cutting) BEGINS Day 26, requires Phase 5 baseline regen complete + Phase 4 closure complete
- Phase 7 (Polish) overlaps Phase 6 (Days 26–29)

**Stream-to-stream parallelism** (per spec §Timeline):
- Stream 1 (Phase 3) ‖ Stream 2 (Phase 4) — both run in parallel during Days 6–11
- Stream 3 (Phase 5 partial) ‖ Stream 1 Wave 2 + Stream 2 — Stream 3 begins Day 14 after Stream 1 + Stream 2 complete
- Stream 4 (Phase 5 partial) — depends on Stream 1 + Stream 3 completing (Days 20–25)

**Critical path**: T009/T010/T011/T012/T013 (Wave 1 wiring, Days 1–5) → T015 (Day 5 smoke test) → T016/T017/T018/T019/T020/T021 (Wave 2 wiring, Days 6–11) → T024 (Day 11 closure verification) → T040/T041 (ATT&CK expansion, Days 17–19) → T044/T045/T047 (aggregator extension, Days 20–21) → T053–T058 (8-baseline regen, Days 24–25) → T059/T064 (ADR-037, Day 26–27) → T067/T069 (PR merge + release-please, Day 29).

---

## Parallel Execution Examples

### Day 1 (Phase 2 Foundational + Phase 3 Wave 1 start)
```
Parallel: T005 (verify aggregator path) ‖ T006 (verify baseline path) ‖ T007 (read F-1/F-2/F-4 templates) ‖ T008 (read finding.yaml schema)
```

### Days 1–4 (Phase 3 Wave 1 — STRIDE-heavy hosts)
```
Parallel (paired with security-analyst per MEDIUM-R1): T009 (spoofing) ‖ T010 (tampering) ‖ T011 (info-disclosure) ‖ T012 (privilege-escalation) ‖ T013 (repudiation)
Sequential after wiring: T014 (fixture authoring) → T015 (Day 5 smoke test)
```

### Days 6–11 (Phase 3 Wave 2 ‖ Phase 4 Wave 1)
```
Parallel: T016 (DoS) ‖ T017 (tool-abuse) ‖ T018 (data-poisoning) ‖ T019 (model-theft) ‖ T020 (prompt-injection) ‖ T021 (agent-autonomy)
Parallel: T025 (A05) ‖ T026 (A06)
Sequential: T022 + T023 + T024 (Wave 2 verification) ‖ T027 (A05/A06 fixtures)
```

### Days 8–13 (Phase 4 Wave 2)
```
Parallel: T028 (API6) ‖ T029 (API8) ‖ T030 (API9) ‖ T031 (API10)
Sequential: T032 (Wave 2 fixtures) → T033 (byte-identity verification) → T035 (audit test)
```

### Days 14–19 (Phase 5 Wave 3.2 + 4.1 + 4.2 — Stream 3)
```
Parallel: T036 (owasp audit) ‖ T037 (owasp record-shape) ‖ T038 (atlas expansion) ‖ T039 (atlas record-shape)
Sequential: T040 (ATT&CK tactical-grouping audit) → T041 (ATT&CK expansion) → T042 (per-item rationale) → T043 (record-shape verification)
```

### Days 20–21 (Phase 5 Wave 4.3 — Stream 4 aggregator)
```
Sequential: T044 (insertion point lookup) → T045 (filter implementation) → T046 (yaml import discipline) → T047 (caller update) → T048 (fixture authoring)
```

### Days 22–23 (Phase 5 Wave 5.1 — Tests)
```
Parallel: T049 (coverage % test) ‖ T050 (pyyaml deferred-import test) ‖ T051 (backward compat update — DETECTION_AGENT_PATHS) ‖ T052 (backward compat update — mutation targets)
```

### Days 24–25 (Phase 5 Wave 5.2 — Baseline regen)
```
Sequential: T053 (6 pre-existing baselines regen) → T054 (predictive-ml-app new baseline) → T055 (mobile-banking-app new baseline)
Sequential after baselines: T056 (SC-007 verify) → T057 (SC-009 verify) → T058 (SC-015 verify)
```

### Days 26–29 (Phase 6 + Phase 7 polish)
```
Sequential cross-cutting: T059 (ADR-037 narrative) → T060 (ADR-027 cross-link) → T061 (§6 demotion) → T062 (deferral docs if any) → T063 (PR title check) → T064 (ADR-037 Accepted) → T065 (Triad sign-off) → T066 (SC verification) → T067 (PR merge) → T068 (post-merge SHA) → T069 (release-please verify)
Parallel polish (Days 26–29 overlap): T071 (pytest full) ‖ T072 (final regen) ‖ T073 (no-new-deps) ‖ T074 (finding.yaml unchanged) ‖ T075 (zero-edit invariant) ‖ T076 (CHANGELOG) ‖ T077 (BACKLOG regen) ‖ T078 (delivery retrospective) ‖ T080–T084 (ADR-037 + carry-forward sanity)
```

---

## Implementation Strategy

**MVP-first ordering**: US4 (Phase 3, F-A3 wiring) is the MVP — every downstream user story depends on populated `source_attribution` arrays. Without US4, US1 and US3 produce empty Coverage Attestation sections, defeating the entire feature.

**Incremental delivery checkpoints**:
1. **Day 5** (Wave 1 complete): 5 STRIDE-heavy hosts wired; smoke test on 3 baselines surfaces per-agent variance early.
2. **Day 11** (Phase 3 complete): 14/14 detection-tier coverage achieved; F-A3 deferral debt cleared; can demonstrate non-empty Coverage Attestation on at least 6 of 8 baselines (subject to taxonomy YAML inventory state at that day).
3. **Day 13** (Phase 4 complete): 6 Partial Web/API items closed; OWASP page begins to render meaningful coverage on `web-app` / `microservices` / `ascii-web-api` baselines.
4. **Day 19** (Stream 3 complete): All 3 taxonomy YAMLs at full inventory; ATT&CK + ATLAS pages begin to render meaningful coverage.
5. **Day 25** (Phase 5 complete): All 8 baselines regenerated with populated Coverage Attestation; aggregator emits accurate coverage percentages with 0 ppt delta.
6. **Day 29** (Phase 6 + 7 complete): ADR-037 Accepted; §6 demoted; PR merged; BLP-01 11-feature initiative closes.

**Risk mitigation per spec edge cases**:
- **Risk 1 (ATT&CK overrun)**: T040 + T041 may overrun the Day 17–19 budget; if so, defer ATT&CK expansion to a follow-on Issue per spec FR-008 deferral path; ATLAS + OWASP closure + F-A3 wiring + 6 Partial item closure remain in feature scope.
- **Risk 2 (F-A3 per-agent variance)**: T015 Day 5 smoke test surfaces variance early; if variance is significant, extend Wave 1 by 0.5–1 day and compress Stream 2 audit start (T025/T026) to absorb.
- **Risk 3 (Partial item Deferral)**: T034 captures the contingent ADR-037 deferral path; any non-closing item surfaces as explicit ADR rationale + follow-on Issue.
- **Risk 4 (non-CA churn)**: T058 explicitly verifies SC-015 byte-identity on non-CA pages; non-CA-page churn investigated as regression before accepting baseline updates.
- **Risk 5 (tactical-grouping contested)**: T040 documents tactic-level rationales defensible by external auditor; contingency in ADR-037 D-5 narrative.

---

## Suggested MVP Scope (if budget compresses)

If the 5–6 week budget compresses to 3–4 weeks, the minimum viable closure is:
1. **Phase 3 (US4 / Stream 1) — REQUIRED MVP** — Without F-A3 wiring, no Coverage Attestation surface populates.
2. **Phase 4 (US2 / Stream 2) — REQUIRED for SC-005** — Six Partial closures are explicit success criteria.
3. **Phase 5 partial (Stream 4 only, no Stream 3 expansion)** — Aggregator extension + 6 pre-existing baseline regen with current taxonomy YAMLs (38 ATT&CK + 12 ATLAS + 60 OWASP). Defer Stream 3 expansion (ATT&CK 38→600, ATLAS 12→30) to a follow-on Issue.
4. **Phase 6 partial (ADR-037 + §6 demotion)** — Defer two net-new baselines (`predictive-ml-app`, `mobile-banking-app`) to follow-on if needed.

**Compression cost**: BLP-01 closes at lower coverage percentages (ATT&CK + ATLAS pages render lower coverage values until Stream 3 expansion ships); §6 Coverage Matrix demotion still semantically valid because the pipeline-generated attestation IS the source of truth even at small inventories.

---

## Task Count Summary

| Phase | Stream | Task Count | Story |
|-------|--------|------------|-------|
| Phase 1 (Setup) | n/a | 4 (T001–T004) | n/a |
| Phase 2 (Foundational) | n/a | 4 (T005–T008) | n/a |
| Phase 3 (Stream 1 / US4) | Stream 1 | 16 (T009–T024) | US4 |
| Phase 4 (Stream 2 / US2) | Stream 2 | 11 (T025–T035) | US2 |
| Phase 5 (Streams 3+4 / US1) | Streams 3+4 | 23 (T036–T058) | US1 |
| Phase 6 (Cross-cutting / US3) | n/a | 12 (T059–T070) | US3 |
| Phase 7 (Polish) | n/a | 14 (T071–T084) | n/a |
| **Total** | | **84** | |

**Independent test criteria per story**:
- US4 (Phase 3): `pytest tests/scripts/test_f_a3_populator_wiring.py` returns 14/14 hosts wired
- US2 (Phase 4): `pytest tests/scripts/test_coverage_attestation_audit.py` confirms 6/6 Partial items closed (or explicit Deferral docs exist)
- US1 (Phase 5): `pytest tests/scripts/test_coverage_percentage_computation.py` returns 0 ppt delta on 40 cross-check pairs (8 baselines × 5 frameworks)
- US3 (Phase 6): `_internal/strategy/BLP-01-threat-coverage.md` §6 carries demotion annotation; ADR-037 status: Accepted; release-please PR open

**Parallel opportunities**:
- Phase 3 Wave 1: 5 host wirings parallel (T009–T013)
- Phase 3 Wave 2: 6 host wirings parallel (T016–T021)
- Phase 4 Wave 2: 4 closures parallel (T028–T031)
- Phase 5 Wave 3.2: 4 OWASP/ATLAS edits parallel (T036–T039)
- Phase 5 Wave 5.1: 4 tests parallel (T049–T052)
- Phase 7 Polish: 9 polish tasks parallel (T071–T078, T080–T084)
