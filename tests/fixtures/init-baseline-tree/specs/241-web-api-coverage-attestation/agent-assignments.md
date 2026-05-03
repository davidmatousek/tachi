---
feature: 241-web-api-coverage-attestation
authored_by: team-lead
date: 2026-05-01
calendar:
  day_1: 2026-04-30  # Thu
  day_29: 2026-06-10  # Wed
  non_working: [2026-05-25]  # Memorial Day
working_days: 29
agent_registry_source: .claude/agents/_README.md
agents_used:
  - architect
  - orchestrator
  - product-manager
  - security-analyst
  - senior-backend-engineer
  - tester
load_cap_per_day: 0.80  # 80% per-agent per-day per Team-Lead MEDIUM-R1
---

# Agent Assignments: F-8 + F-A3 Web/API Coverage Attestation + Populator Wiring [Tier 3]

**Branch**: `241-web-api-coverage-attestation` | **Plan**: [plan.md](./plan.md) | **Tasks**: [tasks.md](./tasks.md)

This document maps every task T001–T084 to its primary agent (and pair-author when applicable), groups tasks into dependency-ordered execution waves matching `plan.md` §"Wave Breakdown" (Wave 0.0 → 6.3 + Buffer), defines Quality Gates between waves, estimates wall-clock time per wave (sums to 29 working days), and verifies the per-agent 80%/day load cap is respected across all 29 days. Pair-authoring on Days 1–4 (Stream 1 Wave 1) splits load between `senior-backend-engineer` and `security-analyst` per Team-Lead MEDIUM-R1 to keep the senior-backend-engineer load within cap during the STRIDE-heavy host wiring concentration.

**Agent registry compliance**: Only agents from `.claude/agents/_README.md` are referenced (architect, orchestrator, product-manager, security-analyst, senior-backend-engineer, tester). No generic labels (e.g. `file-agent`, `doc-agent`, `qa-agent`) appear anywhere in this document. Markdown/doc authoring (T076, T077, T078) is mapped to `senior-backend-engineer` per project convention; validation/acceptance to `tester`; no research tasks in F-241 require `web-researcher`.

---

## 1. Agent Assignment Matrix

Columns: Task ID, short Description, Phase, Wave, Primary Agent, Pair Author (if applicable), Estimated Effort (in agent-hours; 1 working day = 6 effort hours).

### Phase 1 — Setup (Day 0 → Day 1)

| Task ID | Description | Phase | Wave | Primary Agent | Pair Author | Effort (h) |
|---------|-------------|-------|------|---------------|-------------|------------|
| T001 | Confirm feature branch `241-web-api-coverage-attestation` is current | 1 | 0.0 | senior-backend-engineer | — | 0.25 |
| T002 | Confirm draft PR #242 exists with `feat(241):` Conventional Commit title | 1 | 0.0 | senior-backend-engineer | — | 0.25 |
| T003 [P] | Create test fixture directory tree under `tests/scripts/fixtures/web_api_coverage_attestation/` | 1 | 0.0 | tester | — | 0.5 |
| T004 [P] | Author ADR-037 stub at `docs/architecture/02_ADRs/ADR-037-web-api-coverage-attestation-and-populator-wiring.md` (status: Proposed, 10-decision skeleton) | 1 | 0.0 | architect | — | 1.5 |

### Phase 2 — Foundational (Day 1)

| Task ID | Description | Phase | Wave | Primary Agent | Pair Author | Effort (h) |
|---------|-------------|-------|------|---------------|-------------|------------|
| T005 | Verify aggregator filter insertion point per Architect M-2 (line 1073/1101 vs 1144) | 2 | 1.1 | architect | senior-backend-engineer | 1.0 |
| T006 | Verify canonical baseline path per Architect L-1 (`examples/{arch}/sample-report/security-report.pdf.baseline`) | 2 | 1.1 | architect | senior-backend-engineer | 0.5 |
| T007 [P] | Read F-1/F-2/F-4 net-new agent populator templates; document canonical `## Example Findings` structure | 2 | 1.1 | senior-backend-engineer | security-analyst | 1.0 |
| T008 [P] | Read `schemas/finding.yaml` v1.8 to confirm `source_attribution` field shape (5+3 enum) | 2 | 1.1 | senior-backend-engineer | — | 0.5 |

### Phase 3 — User Story 4 (Stream 1 / F-A3 Populator Wiring) — Days 1–11

#### Wave 1.1 — Days 1–2 (3 of 5 STRIDE-heavy hosts; pair-authoring per Team-Lead MEDIUM-R1)

| Task ID | Description | Phase | Wave | Primary Agent | Pair Author | Effort (h) |
|---------|-------------|-------|------|---------------|-------------|------------|
| T009 [P] [US4] | Wire `source_attribution` populator in `.claude/agents/tachi/spoofing.md` (≤200 lines) | 3 | 1.1 | senior-backend-engineer | security-analyst | 3.0 |
| T010 [P] [US4] | Wire populator in `.claude/agents/tachi/tampering.md` (≤200 lines) | 3 | 1.1 | senior-backend-engineer | security-analyst | 3.0 |
| T011 [P] [US4] | Wire populator in `.claude/agents/tachi/info-disclosure.md` (≤200 lines) | 3 | 1.1 | senior-backend-engineer | security-analyst | 3.0 |

#### Wave 1.2 — Days 3–4 (final 2 of 5 STRIDE-heavy hosts; pair-authoring continues)

| Task ID | Description | Phase | Wave | Primary Agent | Pair Author | Effort (h) |
|---------|-------------|-------|------|---------------|-------------|------------|
| T012 [P] [US4] | Wire populator in `.claude/agents/tachi/privilege-escalation.md` (≤200 lines) | 3 | 1.2 | senior-backend-engineer | security-analyst | 3.0 |
| T013 [P] [US4] | Wire populator in `.claude/agents/tachi/repudiation.md` (≤200 lines) | 3 | 1.2 | senior-backend-engineer | security-analyst | 3.0 |
| T014 [US4] | Author Stream 1 Wave 1 fixture findings (5 fixture YAMLs under `stream_1_f_a3_wiring/`) | 3 | 1.2 | tester | senior-backend-engineer | 2.5 |

#### Wave 1.3 — Day 5 (Wave 1 smoke test on 3 baselines per Team-Lead MEDIUM-R2)

| Task ID | Description | Phase | Wave | Primary Agent | Pair Author | Effort (h) |
|---------|-------------|-------|------|---------------|-------------|------------|
| T015 [US4] | Run F-A3 wiring smoke test on 3 baselines (`web-app`, `agentic-app`, `predictive-ml-app`); manually verify `source_attribution` arrays render in `threats.md` Section 9 YAML | 3 | 1.3 | tester | senior-backend-engineer | 4.0 |

#### Wave 2.1 — Days 6–7 (Stream 1 Wave 2 + Stream 2 Wave 1 start)

| Task ID | Description | Phase | Wave | Primary Agent | Pair Author | Effort (h) |
|---------|-------------|-------|------|---------------|-------------|------------|
| T016 [P] [US4] | Wire populator in `.claude/agents/tachi/denial-of-service.md` (cite LLM10 per F-5 ADR-034) | 3 | 2.1 | senior-backend-engineer | — | 2.5 |
| T017 [P] [US4] | Wire populator in `.claude/agents/tachi/tool-abuse.md` (cite ASI07 per F-3 ADR-032) | 3 | 2.1 | senior-backend-engineer | — | 2.5 |
| T025 [P] [US2] | Close A05 Security Misconfiguration on `tachi-privilege-escalation` Pattern Category 11 (Primary Source + non-mobile Indicator extension) | 4 | 2.1 | security-analyst | — | 3.0 |
| T026 [P] [US2] | Close A06 Vulnerable and Outdated Components on `tachi-tampering` Pattern Category 8 (Primary Source block) | 4 | 2.1 | security-analyst | — | 3.0 |

#### Wave 2.2 — Days 8–9 (Stream 1 Wave 2 ML hosts + Stream 2 Wave 2 API8 start)

| Task ID | Description | Phase | Wave | Primary Agent | Pair Author | Effort (h) |
|---------|-------------|-------|------|---------------|-------------|------------|
| T018 [P] [US4] | Wire populator in `.claude/agents/tachi/data-poisoning.md` (cite ML06 corpus per F-6 ADR-035) | 3 | 2.2 | senior-backend-engineer | — | 2.5 |
| T019 [P] [US4] | Wire populator in `.claude/agents/tachi/model-theft.md` (cite ML03/ML06 artifact per F-6) | 3 | 2.2 | senior-backend-engineer | — | 2.5 |
| T027 [US2] | Author A05/A06 fixture findings under `stream_2_partial_closures/` | 4 | 2.2 | tester | — | 1.5 |
| T029 [P] [US2] | Close API8 Security Misconfiguration on `tachi-privilege-escalation` (API-specific Indicator extension; consolidates with T025) | 4 | 2.2 | security-analyst | — | 2.0 |

#### Wave 2.3 — Days 10–11 (Stream 1 Wave 2 +1-day HIGH-A absorption + closure verification)

| Task ID | Description | Phase | Wave | Primary Agent | Pair Author | Effort (h) |
|---------|-------------|-------|------|---------------|-------------|------------|
| T020 [P] [US4] | Wire populator in `.claude/agents/tachi/prompt-injection.md` (cite LLM01 per HIGH-A) | 3 | 2.3 | senior-backend-engineer | — | 2.5 |
| T021 [P] [US4] | Wire populator in `.claude/agents/tachi/agent-autonomy.md` (cite ASI01/06/08/10 + LLM06 per HIGH-A) | 3 | 2.3 | senior-backend-engineer | — | 3.0 |
| T022 [US4] | Author Stream 1 Wave 2 fixture findings (6 fixture YAMLs under `stream_1_f_a3_wiring/`) | 3 | 2.3 | tester | senior-backend-engineer | 3.0 |
| T023 [US4] | Author `tests/scripts/test_f_a3_populator_wiring.py` (14/14 grep + line-cap + YAML-block assertions) | 3 | 2.3 | tester | — | 3.0 |
| T024 [US4] | Run F-A3 closure verification across all 8 baselines; document `source_attribution` count per baseline | 3 | 2.3 | tester | senior-backend-engineer | 3.0 |

### Phase 4 — User Story 2 (Stream 2 / Six Partial Item Closures) — Days 6–13 (overlaps with Phase 3)

#### Wave 3.1 — Days 12–13 (Stream 2 completion: API6 + API9 + API10)

| Task ID | Description | Phase | Wave | Primary Agent | Pair Author | Effort (h) |
|---------|-------------|-------|------|---------------|-------------|------------|
| T028 [P] [US2] | Close API6 Unrestricted Access to Sensitive Business Flows → `tachi-tool-abuse` (NEW Indicator category per Q-Plan-1) | 4 | 3.1 | security-analyst | — | 3.5 |
| T030 [P] [US2] | Close API9 Improper Inventory Management → `tachi-info-disclosure` (NEW Indicator category per Q-Plan-2) | 4 | 3.1 | security-analyst | — | 3.5 |
| T031 [P] [US2] | Close API10 Unsafe Consumption of APIs (Primary Source on `tachi-tampering` Cat 9 + cross-ref `tachi-info-disclosure` Cat 7) | 4 | 3.1 | security-analyst | — | 3.0 |
| T032 [US2] | Author Wave 2 fixtures (4 YAMLs under `stream_2_partial_closures/`) | 4 | 3.1 | tester | — | 2.0 |
| T033 [US2] | Verify Stream 2 byte-identity invariant on `tachi-repudiation` + `tachi-spoofing` companions | 4 | 3.1 | tester | — | 1.0 |
| T034 [US2] | (Contingent FR-008) If any closure fails: document Deferral D-decision in ADR-037 + open follow-on Issue + annotate §6 | 4 | 3.1 | product-manager | architect | 1.0 (contingent) |
| T035 [US2] | Author `tests/scripts/test_coverage_attestation_audit.py` (walks owasp.yaml; resolves Covered citations to ≥1 agent + ≥1 pattern category per BLP-01 §8) | 4 | 3.1 | tester | — | 3.5 |

### Phase 5 — User Story 1 (Streams 3+4) — Days 14–25

#### Wave 3.2 — Days 14–16 (Stream 3 OWASP audit + ATLAS expansion)

| Task ID | Description | Phase | Wave | Primary Agent | Pair Author | Effort (h) |
|---------|-------------|-------|------|---------------|-------------|------------|
| T036 [P] [US1] | Audit `schemas/taxonomy/owasp.yaml` for citation completeness (60 records × ≥1 agent + ≥1 pattern category) | 5 | 3.2 | security-analyst | — | 4.0 |
| T037 [P] [US1] | Extend `owasp.yaml` record shape: add `out_of_scope: false` + `out_of_scope_rationale: ""` to all 60 records | 5 | 3.2 | security-analyst | — | 2.5 |
| T038 [P] [US1] | Expand `mitre-atlas.yaml` from 12 → ~30 records (ATLAS phases coverage) | 5 | 3.2 | security-analyst | — | 5.5 |
| T039 [P] [US1] | Extend `mitre-atlas.yaml` record shape: +2 fields (with per-item Out-of-Scope where ATLAS technique is runtime/IR-only) | 5 | 3.2 | security-analyst | — | 3.0 |

#### Wave 4.1 — Day 17 (Stream 3 ATT&CK tactical-grouping audit start; last working day before Memorial Day)

| Task ID | Description | Phase | Wave | Primary Agent | Pair Author | Effort (h) |
|---------|-------------|-------|------|---------------|-------------|------------|
| T040 [US1] | Begin ATT&CK Enterprise tactical-grouping audit (TA0005/7/8/9/10/11/40 Out-of-Scope rationales per data-model.md §5) | 5 | 4.1 | security-analyst | architect | 5.0 |

#### Wave 4.2 — Days 18–19 (Stream 3 ATT&CK expansion; post-Memorial Day)

| Task ID | Description | Phase | Wave | Primary Agent | Pair Author | Effort (h) |
|---------|-------------|-------|------|---------------|-------------|------------|
| T041 [US1] | Expand `mitre-attack.yaml` from 38 → ~600 records; apply tactical-grouping Out-of-Scope on TA0005/7/8/9/10/11/40 | 5 | 4.2 | security-analyst | — | 6.0 |
| T042 [US1] | Author per-item Out-of-Scope rationales on individual runtime-only sub-techniques inside in-scope tactics (TA0001/2/3/4/6/42) | 5 | 4.2 | security-analyst | — | 3.5 |
| T043 [US1] | Verify `mitre-attack.yaml` record-shape +2 fields present on all ~600 records (defaults preserved on in-scope) | 5 | 4.2 | security-analyst | — | 2.5 |

#### Wave 4.3 — Days 20–21 (Stream 4 aggregator extension)

| Task ID | Description | Phase | Wave | Primary Agent | Pair Author | Effort (h) |
|---------|-------------|-------|------|---------------|-------------|------------|
| T044 [US1] | Read `scripts/extract-report-data.py` lines 1070–1175; finalize filter insertion at `_load_framework_yaml_records()` (1073) OR `load_framework_yaml_record_counts()` (1101) per Architect M-2 | 5 | 4.3 | senior-backend-engineer | architect | 1.5 |
| T045 [US1] | Implement Out-of-Scope-aware filter at chosen insertion point; emit `in-scope-record-count` to Typst data contract | 5 | 4.3 | senior-backend-engineer | — | 3.5 |
| T046 [US1] | Preserve stdlib-only module-load invariant (`import yaml` inside function bodies); add documenting comment | 5 | 4.3 | senior-backend-engineer | — | 1.0 |
| T047 [US1] | Update `_build_per_framework_aggregate()` caller to pass `in_scope_count` denominator; preserve `(covered/in_scope)*100` formula + `N/A` on denominator==0 | 5 | 4.3 | senior-backend-engineer | — | 2.0 |
| T048 [US1] | Author Stream 3+4 fixtures under `stream_3_taxonomy/` + `stream_4_coverage_percentage/` (synthetic OWASP/ATT&CK/ATLAS subsets, mixed in-scope/out-of-scope, expected coverage_pct values) | 5 | 4.3 | tester | senior-backend-engineer | 4.0 |

#### Wave 5.1 — Days 22–23 (4 new test scripts + backward-compat updates)

| Task ID | Description | Phase | Wave | Primary Agent | Pair Author | Effort (h) |
|---------|-------------|-------|------|---------------|-------------|------------|
| T049 [P] [US1] | Author `tests/scripts/test_coverage_percentage_computation.py` (0 ppt delta on 8 baselines × 5 frameworks = 40 cross-check pairs) | 5 | 5.1 | tester | — | 4.0 |
| T050 [P] [US1] | Author `tests/scripts/test_pyyaml_deferred_import.py` (AST walk of `import yaml` nodes per Architect MEDIUM-B) | 5 | 5.1 | tester | — | 2.0 |
| T051 [P] [US1] | Update `test_backward_compatibility.py` — remove 11 hosts from `DETECTION_AGENT_PATHS`; add to `DETECTION_PATTERN_REF_ENRICHMENT_HOSTS` frozenset | 5 | 5.1 | tester | — | 1.5 |
| T052 [P] [US1] | Update `test_backward_compatibility.py` — add `predictive-ml-app` + `mobile-banking-app` to mutation-target exclusion list | 5 | 5.1 | tester | — | 1.0 |

#### Wave 5.2 — Days 24–25 (8-baseline regen + SC-007/009/015 verification)

| Task ID | Description | Phase | Wave | Primary Agent | Pair Author | Effort (h) |
|---------|-------------|-------|------|---------------|-------------|------------|
| T053 [US1] | Regenerate 6 pre-existing baselines under `SOURCE_DATE_EPOCH=1700000000`; verify CA-pages populated, non-CA byte-identical | 5 | 5.2 | senior-backend-engineer | — | 4.0 |
| T054 [US1] | Author net-new baseline at `examples/predictive-ml-app/sample-report/security-report.pdf.baseline` (canonical path per Architect L-1) | 5 | 5.2 | senior-backend-engineer | — | 2.0 |
| T055 [US1] | Author net-new baseline at `examples/mobile-banking-app/sample-report/security-report.pdf.baseline` (canonical path per Architect L-1) | 5 | 5.2 | senior-backend-engineer | — | 2.0 |
| T056 [US1] | Verify SC-007 across all 8 baselines (≥1 row in per-finding attribution + non-zero coverage-percentage on at least one served framework family) | 5 | 5.2 | tester | — | 1.5 |
| T057 [US1] | Verify SC-009 across all 8 baselines (0 ppt delta on 40 cross-check pairs) | 5 | 5.2 | tester | — | 1.5 |
| T058 [US1] | Verify SC-015 across all 8 baselines (non-CA pages byte-identical pre/post Stream 4 regen under fixed `SOURCE_DATE_EPOCH=1700000000`) | 5 | 5.2 | tester | — | 1.5 |

### Phase 6 — User Story 3 (§6 Demotion + ADR-037 Accepted + PR merge) — Days 26–29

#### Wave 5.3 — Day 26 (ADR-037 Proposed narrative + ADR-027 cross-link + §6 demotion)

| Task ID | Description | Phase | Wave | Primary Agent | Pair Author | Effort (h) |
|---------|-------------|-------|------|---------------|-------------|------------|
| T059 [US3] | Author full ADR-037 narrative (D-1..D-10 per plan §"ADR-037 D-numbered Decision Outline"; status: Proposed; 10-row mapping table) | 6 | 5.3 | architect | — | 4.5 |
| T060 [US3] | Address Architect M-1: extend ADR-027 with `## Extension History` forward-pointer addendum cross-linking ADR-037 D-7 (bidirectional) | 6 | 5.3 | architect | — | 0.5 |
| T061 [US3] | Annotate BLP-01 §6 Coverage Matrix in `_internal/strategy/BLP-01-threat-coverage.md` ("historical — superseded by pipeline-generated attestation" + pointer to F-B section) | 6 | 5.3 | senior-backend-engineer | — | 1.0 |
| T062 [US3] | (Contingent FR-008) If any item deferred per T034: document each Deferral as ADR-037 D-numbered Decision (D-11+) with rationale + Issue link + §6 annotation | 6 | 5.3 | product-manager | architect | 1.0 (contingent) |

#### Wave 6.1 — Day 27 (PR title verification + ADR-037 Accepted dual-commit)

| Task ID | Description | Phase | Wave | Primary Agent | Pair Author | Effort (h) |
|---------|-------------|-------|------|---------------|-------------|------------|
| T063 [US3] | Squash-merge prep: verify PR #242 title is `feat(241):` Conventional Commit per `.claude/rules/git-workflow.md` two-step Pre-merge | 6 | 6.1 | senior-backend-engineer | — | 0.25 |
| T064 [US3] | ADR-037 Accepted via dual-commit governance pattern (mirror ADR-035 D-10 / ADR-036 D-10): Proposed commit → SHA capture → Accepted commit (post-merge SHA fill-in deferred to T067/T068) | 6 | 6.1 | architect | — | 1.5 |

#### Wave 6.2 — Day 28 (Triple Triad sign-off + 18 SC verification)

| Task ID | Description | Phase | Wave | Primary Agent | Pair Author | Effort (h) |
|---------|-------------|-------|------|---------------|-------------|------------|
| T065 [US3] | Triple Triad sign-off recorded on `tasks.md` (PM + Architect + Team-Lead all APPROVED or APPROVED_WITH_CONCERNS) | 6 | 6.2 | product-manager | architect, team-lead | 1.5 |
| T066 [US3] | Verify all 18 SCs (SC-001..SC-018) achieved per spec; document any non-achieved SC with deferral rationale + follow-on Issue | 6 | 6.2 | product-manager | — | 2.5 |

#### Wave 6.3 — Day 29 (PR squash-merge + post-merge SHA + release-please verification)

| Task ID | Description | Phase | Wave | Primary Agent | Pair Author | Effort (h) |
|---------|-------------|-------|------|---------------|-------------|------------|
| T067 [US3] | Mark PR #242 ready (`gh pr ready 242`); squash-merge (`gh pr merge --squash --delete-branch 242`) | 6 | 6.3 | senior-backend-engineer | — | 0.5 |
| T068 [US3] | Post-merge: fill in ADR-037 Accepted SHA placeholder (T064 dual-commit pattern); push commit to main | 6 | 6.3 | architect | senior-backend-engineer | 0.5 |
| T069 [US3] | Verify release-please PR opens within ~30s per R12 enforcement; if empty, push empty `feat(241):` marker commit | 6 | 6.3 | senior-backend-engineer | — | 0.5 |
| T070 [US3] | (Cross-ref T036) Verify owasp.yaml audit completeness post-Stream 2 closures (60 records × citation evidence post-A05/A06/API6/API8/API9/API10) | 6 | 6.2 | security-analyst | — | 1.5 |

### Phase 7 — Polish & Cross-Cutting (Days 26–29; overlaps with Phase 6)

| Task ID | Description | Phase | Wave | Primary Agent | Pair Author | Effort (h) |
|---------|-------------|-------|------|---------------|-------------|------------|
| T071 [P] | Run full pytest suite under `tests/scripts/` (4 new + modified `test_backward_compatibility.py` + all pre-existing) | 7 | 5.3 | tester | — | 1.5 |
| T072 [P] | Run `make regenerate` end-to-end on all 8 baselines under `SOURCE_DATE_EPOCH=1700000000` for final byte-identity | 7 | 5.3 | senior-backend-engineer | — | 2.0 |
| T073 [P] | Confirm zero new runtime deps: `git diff main..HEAD -- pyproject.toml requirements*.txt package.json` empty (SC-013) | 7 | 5.3 | senior-backend-engineer | — | 0.25 |
| T074 [P] | Confirm `schemas/finding.yaml` unchanged at v1.8 (SC-014) | 7 | 5.3 | senior-backend-engineer | — | 0.25 |
| T075 [P] | Confirm F-7 28-file detection-tier zero-edit invariant (only 11 F-A3 hosts + 4 Stream 2 catalogs modified per FR-021) | 7 | 5.3 | senior-backend-engineer | — | 0.5 |
| T076 [P] | Update CHANGELOG.md if release-please does not auto-generate (feature entry referencing PR #242, F-241 BLP-01 closure) | 7 | 6.3 | senior-backend-engineer | — | 0.5 |
| T077 [P] | Update `docs/product/_backlog/BACKLOG.md` via `bash .aod/scripts/bash/backlog-regenerate.sh` (F-241 stage:done transition) | 7 | 6.3 | senior-backend-engineer | — | 0.5 |
| T078 [P] | Document delivery retrospective in `specs/241-web-api-coverage-attestation/delivery.md` per F-7/F-6 precedent (actual-vs-estimated, surprises, BLP-01 closure narrative) | 7 | 6.3 | senior-backend-engineer | — | 1.5 |
| T079 | Move GitHub Issue #241 to `stage:done` via `aod_gh_update_stage 241 done` | 7 | 6.3 | senior-backend-engineer | — | 0.25 |
| T080 | Verify ADR-037 D-numbered decisions all populated with final rationales (D-1..D-10) | 7 | 6.1 | architect | — | 1.5 |
| T081 | Per Architect L-1 carry-forward: confirm canonical baseline path consistency across plan.md, tasks.md, test_backward_compatibility.py, ADR-037 D-9 | 7 | 6.1 | architect | senior-backend-engineer | 0.5 |
| T082 | Per Architect M-2 carry-forward: confirm aggregator filter insertion point clearly documented in ADR-037 D-8 narrative | 7 | 6.1 | architect | — | 0.5 |
| T083 | Per Architect M-1 carry-forward: confirm bidirectional cross-link between ADR-027 addendum and ADR-037 D-7 back-reference | 7 | 6.1 | architect | — | 0.5 |
| T084 | Sanity-check Architect M-2 implementation: open `extract-report-data.py` post-edit; confirm filter at chosen insertion point (NOT line 1144) | 7 | 6.1 | architect | senior-backend-engineer | 0.5 |

**Task count summary**: 84 tasks across 6 distinct primary agents.

| Agent | Primary Tasks | Pair-Author Tasks | Total Touchpoints |
|-------|---------------|-------------------|-------------------|
| architect | 14 (T004, T040 pair, T044 pair, T059, T060, T064, T068, T080, T081, T082, T083, T084 + T034 contingent + T062 contingent) | 5 (T005, T006, T034 contingent, T062 contingent, T065) | 19 |
| orchestrator | 0 (cross-cutting wave coordination only — see §2 Wave Quality Gates) | 0 | wave-level |
| product-manager | 4 (T034 contingent, T062 contingent, T065, T066) | 0 | 4 |
| security-analyst | 16 (T025, T026, T028, T029, T030, T031, T036, T037, T038, T039, T040, T041, T042, T043, T070 + Days 1–4 pair-author) | 5 (T009, T010, T011, T012, T013) Days 1–4 pair-author per Team-Lead MEDIUM-R1 | 21 |
| senior-backend-engineer | 30 (T001, T002, T007, T008, T016, T017, T018, T019, T020, T021, T044, T045, T046, T047, T053, T054, T055, T061, T063, T067, T069, T072, T073, T074, T075, T076, T077, T078, T079) + 1 contingent fallback | 11 (T005, T006, T014, T015, T022, T024, T044 pair, T048, T068, T081, T084) | 42 |
| tester | 19 (T003, T014, T015, T022, T023, T024, T027, T032, T033, T035, T048, T049, T050, T051, T052, T056, T057, T058, T071) | 0 | 19 |

(`orchestrator` is engaged at wave-boundary checkpoints — coordinating multi-agent task runs at Wave 1.3, 2.3, 3.1, 4.3, 5.2, 6.3 — rather than owning specific tasks; this matches `.claude/agents/_README.md` "Workflow Executor" role definition.)

---

## 2. Parallel Execution Waves

Tasks group into 19 waves matching `plan.md` §"Wave Breakdown" plus the Buffer reserve. Each wave has dependency-ordered task firings; within a wave, `[P]` tasks fire in true parallel where the agent registry allows.

### Wave 0.0 — Day 0 (Wed 2026-04-29) — Plan-day approvals + pair-authoring reservation

- **Tasks**: (none from T001–T084; this wave is pre-Day-1 plan-stage governance)
- **Output**: PM + Architect + Team-Lead sign-offs on plan.md and tasks.md confirmed; pair-authoring reservation (senior-backend-engineer + security-analyst Days 1–4) confirmed.
- **Quality Gate**: All three Triad sign-offs present in tasks.md frontmatter.

### Wave 1.1 — Days 1–2 (Thu 4/30 + Fri 5/1) — Setup + Foundational + Stream 1 Wave 1 (3 hosts)

- **Parallel tasks**: T003 (fixture dirs) ‖ T004 (ADR stub) ‖ T005 (aggregator path) ‖ T006 (baseline path) ‖ T007 (template read) ‖ T008 (schema read)
- **Then sequential parallel** (within wave): T009 (spoofing) ‖ T010 (tampering) ‖ T011 (info-disclosure) — pair-authored
- **Setup tasks** (sequential, low-effort): T001 + T002
- **Quality Gate (end Day 2)**: 3 of 5 STRIDE-heavy hosts wired; ADR-037 stub + fixture directory exist; foundational reads complete.

### Wave 1.2 — Days 3–4 (Mon 5/4 + Tue 5/5) — Stream 1 Wave 1 completion (final 2 hosts) + Wave 1 fixtures

- **Parallel tasks**: T012 (privilege-escalation) ‖ T013 (repudiation) — pair-authored
- **Sequential after wiring**: T014 (Wave 1 fixture authoring; depends on T009–T013)
- **Quality Gate (end Day 4)**: 5/5 STRIDE-heavy hosts wired; 5 fixture YAMLs authored.

### Wave 1.3 — Day 5 (Wed 5/6) — F-A3 Wave 1 smoke test (CHECKPOINT 1: Day 5 deliverable)

- **Sequential**: T015 (smoke test on `web-app` + `agentic-app` + `predictive-ml-app`)
- **Quality Gate (end Day 5)**: Smoke test green on all 3 baselines; `source_attribution` arrays render in `threats.md` Section 9 YAML for all 5 newly-wired STRIDE-heavy hosts. **PRD Day 5 deliverable per Team-Lead MEDIUM-R2 confirmed.**

### Wave 2.1 — Days 6–7 (Thu 5/7 + Fri 5/8) — Stream 1 Wave 2 + Stream 2 Wave 1 start

- **Parallel tasks (Stream 1)**: T016 (DoS) ‖ T017 (tool-abuse)
- **Parallel tasks (Stream 2)**: T025 (A05) ‖ T026 (A06)
- **Quality Gate (end Day 7)**: 7/11 hosts wired; 2/6 Partial items (A05, A06) closed; companion catalog edits limited to `tachi-privilege-escalation` + `tachi-tampering`.

### Wave 2.2 — Days 8–9 (Mon 5/11 + Tue 5/12) — Stream 1 Wave 2 ML hosts + Stream 2 Wave 2 (API8) + Wave 1 fixtures

- **Parallel tasks (Stream 1)**: T018 (data-poisoning) ‖ T019 (model-theft)
- **Parallel tasks (Stream 2)**: T029 (API8) ‖ T027 (A05/A06 fixtures depending on T025/T026)
- **Quality Gate (end Day 9)**: 9/11 hosts wired; 3/6 Partial items closed (API8 added); fixtures authored for first 2 closures.

### Wave 2.3 — Days 10–11 (Wed 5/13 + Thu 5/14) — Stream 1 Wave 2 +1-day HIGH-A absorption + Stream 1 verification (CHECKPOINT 2: Day 11)

- **Parallel tasks (Stream 1)**: T020 (prompt-injection) ‖ T021 (agent-autonomy)
- **Sequential after wiring**: T022 (Wave 2 fixtures) → T023 (test_f_a3_populator_wiring.py) → T024 (8-baseline closure verification)
- **Quality Gate (end Day 11)**: 11/11 hosts wired; 14/14 detection-tier total (3 pre-existing + 11 newly-wired); F-A3 deferral debt fully cleared. **PRD Phase 3 deliverable per spec FR-005 confirmed.**

### Wave 3.1 — Days 12–13 (Fri 5/15 + Mon 5/18) — Stream 2 completion (CHECKPOINT 3: Day 13)

- **Parallel tasks (Stream 2 closures)**: T028 (API6 → tool-abuse per Q-Plan-1) ‖ T030 (API9 → info-disclosure per Q-Plan-2) ‖ T031 (API10 → tampering Cat 9 + info-disclosure Cat 7 cross-ref)
- **Sequential after closures**: T032 (Wave 2 fixtures) → T033 (byte-identity check) → T034 (contingent FR-008 deferral docs) → T035 (audit test)
- **Quality Gate (end Day 13)**: 6/6 Partial items closed (or any non-closing item surfaces with Deferral ADR rationale + follow-on Issue per FR-008); audit test green.

### Wave 3.2 — Days 14–16 (Tue 5/19 + Wed 5/20 + Thu 5/21) — Stream 3 OWASP audit + ATLAS expansion

- **Parallel tasks**: T036 (owasp.yaml audit) ‖ T037 (owasp record-shape +2 fields) ‖ T038 (atlas 12→30 expansion) ‖ T039 (atlas record-shape +2 fields)
- **Quality Gate (end Day 16)**: 2 of 3 taxonomy YAMLs at full inventory; both have +2 fields applied to all records; OWASP citation completeness audit passes (60 records × ≥1 agent + ≥1 pattern).

### Wave 4.1 — Day 17 (Fri 5/22) — Stream 3 ATT&CK tactical-grouping audit start (last working day before Memorial Day)

- **Sequential**: T040 (ATT&CK Out-of-Scope rationale strings for TA0005/7/8/9/10/11/40 per data-model.md §5)
- **Quality Gate (end Day 17)**: 7 tactic-level Out-of-Scope rationales documented and ready for Wave 4.2 to consume.

### Memorial Day — Mon 5/25 — Non-working

### Wave 4.2 — Days 18–19 (Tue 5/26 + Wed 5/27) — Stream 3 ATT&CK expansion (post-Memorial Day)

- **Sequential**: T041 (ATT&CK 38→600 expansion) → T042 (per-item rationale on in-scope tactics) → T043 (record-shape verification)
- **Quality Gate (end Day 19)**: 3 of 3 taxonomy YAMLs at full inventory; ~600 ATT&CK records have +2 fields with `out_of_scope: true` propagated to TA0005/7/8/9/10/11/40 members and per-item rationale on in-scope tactics where applicable.

### Wave 4.3 — Days 20–21 (Thu 5/28 + Fri 5/29) — Stream 4 aggregator extension + fixtures

- **Sequential**: T044 (insertion-point lookup) → T045 (filter implementation) → T046 (yaml import discipline) → T047 (caller update) → T048 (Stream 3+4 fixtures)
- **Quality Gate (end Day 21)**: Aggregator filter at line 1073 OR 1101 (NOT 1144 per Architect M-2); `import yaml` invariant preserved (asserted by post-edit grep); fixtures authored with synthetic mixed in-scope/out-of-scope records and expected coverage_pct.

### Wave 5.1 — Days 22–23 (Mon 6/1 + Tue 6/2) — 4 new test scripts + backward-compat updates

- **Parallel tasks**: T049 (coverage % computation test) ‖ T050 (pyyaml deferred-import test) ‖ T051 (DETECTION_AGENT_PATHS removal) ‖ T052 (mutation-target additions)
- **Quality Gate (end Day 23)**: 4 new test scripts green; modified `test_backward_compatibility.py` green on existing 6-baseline byte-identity loop.

### Wave 5.2 — Days 24–25 (Wed 6/3 + Thu 6/4) — 8-baseline regen + SC-007/009/015 verification (CHECKPOINT 5: Day 25)

- **Sequential (regen)**: T053 (6 pre-existing baselines) → T054 (predictive-ml-app new baseline) → T055 (mobile-banking-app new baseline)
- **Sequential (verification)**: T056 (SC-007) → T057 (SC-009) → T058 (SC-015)
- **Quality Gate (end Day 25)**: 8/8 baselines render Coverage Attestation; aggregator emits accurate coverage percentages with 0 ppt delta (40 cross-check pairs); non-CA pages byte-identical pre/post regen on the 6 pre-existing baselines under `SOURCE_DATE_EPOCH=1700000000`.

### Wave 5.3 — Day 26 (Fri 6/5) — ADR-037 Proposed + ADR-027 cross-link + §6 demotion + Polish parallel start

- **Sequential cross-cutting**: T059 (ADR-037 narrative D-1..D-10) → T060 (ADR-027 forward-pointer) → T061 (§6 demotion annotation) → T062 (contingent deferral docs)
- **Parallel polish (overlap start)**: T071 ‖ T072 ‖ T073 ‖ T074 ‖ T075
- **Quality Gate (end Day 26)**: ADR-037 status=Proposed with full 10-decision narrative; ADR-027 has bidirectional Extension History addendum; §6 Coverage Matrix carries demotion annotation + pointer; full pytest suite + final regen + 4 invariant audits green.

### Wave 6.1 — Day 27 (Mon 6/8) — ADR-037 Accepted dual-commit + final ADR sanity-checks

- **Sequential**: T063 (PR title verify) → T064 (ADR-037 Accepted dual-commit Proposed→Accepted)
- **Parallel polish**: T080 ‖ T081 ‖ T082 ‖ T083 ‖ T084 (Architect carry-forward sanity-checks)
- **Quality Gate (end Day 27)**: ADR-037 status=Accepted (post-merge SHA placeholder pending T068); all M-1/M-2/L-1 carry-forwards documented in ADR-037 narrative consistent with tasks.md, plan.md, and test_backward_compatibility.py.

### Wave 6.2 — Day 28 (Tue 6/9) — Triple Triad sign-off + 18 SC verification + cross-ref T070

- **Sequential**: T065 (Triple Triad sign-off injection) → T066 (18 SC verification) → T070 (owasp.yaml audit completeness post-Stream 2)
- **Quality Gate (end Day 28)**: All three Triad agents have status APPROVED or APPROVED_WITH_CONCERNS on tasks.md; all 18 SCs achieved (or each non-achieved SC has explicit deferral rationale + follow-on Issue); owasp.yaml citation evidence intact post-Stream 2.

### Wave 6.3 — Day 29 (Wed 6/10) — PR squash-merge + post-merge SHA + release-please verification + delivery polish (CHECKPOINT 6: Day 29 BLP-01 closure)

- **Sequential merge**: T067 (PR ready + squash-merge) → T068 (post-merge SHA fill-in for ADR-037 dual-commit) → T069 (release-please PR verify)
- **Parallel close-out polish**: T076 ‖ T077 ‖ T078 ‖ T079
- **Quality Gate (end Day 29)**: PR #242 squash-merged with `feat(241):` Conventional Commit title; release-please PR opens within ~30s of merge per R12 enforcement; ADR-037 has both Proposed and Accepted SHAs filled; CHANGELOG + BACKLOG updated; delivery retrospective authored; Issue #241 → stage:done. **BLP-01 11-feature initiative closes.**

### Buffer — Days 30+ (reserve)

- Reserved for Risk 1 (ATT&CK overrun absorption — defer T041 expansion to follow-on Issue per FR-008) or Risk 3 (1–2 Partial item Deferrals require ADR-037 D-11+ rationale + follow-on Issue per T034/T062 contingent path). PRD already accepted pessimistic-case 0–0.5wk margin per Team-Lead MEDIUM-2.

---

## 3. Quality Gates Between Waves

Each Wave checkpoint requires the listed condition green before the next wave fires. Checkpoints are non-overlapping and gate downstream parallelism. Severity column captures BLOCKER vs ADVISORY per spec SC-level designation.

| End-of-Wave Checkpoint | Day | Condition Required Green | Severity | Verification |
|------------------------|-----|--------------------------|----------|--------------|
| Wave 0.0 | Day 0 | Triple Triad sign-off on plan.md + tasks.md present | BLOCKER | grep frontmatter `triad:` block in tasks.md |
| Wave 1.1 | Day 2 | 3 STRIDE hosts wired (`spoofing`, `tampering`, `info-disclosure`); ADR-037 stub exists; foundational reads done | ADVISORY | `grep -l "source_attribution" .claude/agents/tachi/{spoofing,tampering,info-disclosure}.md` returns 3 paths |
| Wave 1.2 | Day 4 | 5/5 STRIDE hosts wired; Wave 1 fixtures authored | ADVISORY | `grep -l "source_attribution" .claude/agents/tachi/{spoofing,tampering,info-disclosure,privilege-escalation,repudiation}.md` returns 5; `ls tests/scripts/fixtures/web_api_coverage_attestation/stream_1_f_a3_wiring/*.yaml` returns 5 |
| Wave 1.3 (CHECKPOINT 1) | Day 5 | Smoke test green on 3 baselines; `source_attribution` arrays render in Section 9 YAML | BLOCKER | Manual inspection of `examples/{web-app,agentic-app,predictive-ml-app}/sample-report/threats.md` Section 9 |
| Wave 2.1 | Day 7 | 7/11 hosts wired; A05 + A06 closed | ADVISORY | grep returns 7 hosts; companion catalog diffs show Primary Source blocks added |
| Wave 2.2 | Day 9 | 9/11 hosts wired; API8 closed; Wave 1 fixtures green | ADVISORY | grep returns 9 hosts; pytest on Wave 1 fixtures green |
| Wave 2.3 (CHECKPOINT 2) | Day 11 | 11/11 hosts wired; 14/14 detection-tier; `pytest test_f_a3_populator_wiring.py` green | BLOCKER (SC-001) | `grep -l "source_attribution" .claude/agents/tachi/*.md \| wc -l` returns 14; pytest green |
| Wave 3.1 (CHECKPOINT 3) | Day 13 | 6/6 Partial items closed (or Deferral ADR docs exist for any non-closing item); `pytest test_coverage_attestation_audit.py` green | BLOCKER (SC-005) | pytest green; if T034 fired, ADR-037 has D-11+ deferral decisions documented |
| Wave 3.2 | Day 16 | 2/3 taxonomy YAMLs at full inventory; +2 fields applied | ADVISORY | YAML record count + grep `out_of_scope:` on owasp.yaml + mitre-atlas.yaml |
| Wave 4.1 | Day 17 | ATT&CK tactical-grouping rationale strings ready | ADVISORY | T040 task-notes file populated with 7 tactic-level rationales |
| Wave 4.2 | Day 19 | 3/3 taxonomy YAMLs at full inventory | BLOCKER (Stream 3 closure) | YAML record counts: owasp 60, mitre-atlas ~30, mitre-attack ~600; record-shape verification |
| Wave 4.3 | Day 21 | Aggregator filter at line 1073 OR 1101 (NOT 1144); `import yaml` inside function bodies | BLOCKER (FR-014, M-2) | grep + AST walk; T084 sanity-check |
| Wave 5.1 | Day 23 | 4 new test scripts green; modified test_backward_compatibility.py green | BLOCKER (Constitution VI) | `pytest tests/scripts/test_{f_a3_populator_wiring,coverage_attestation_audit,coverage_percentage_computation,pyyaml_deferred_import}.py tests/scripts/test_backward_compatibility.py` |
| Wave 5.2 (CHECKPOINT 5) | Day 25 | 8/8 baselines render Coverage Attestation; 0 ppt delta; non-CA byte-identical | BLOCKER (SC-007, SC-009, SC-015) | Manual inspection + `pytest test_coverage_percentage_computation.py` + byte-identity diff under `SOURCE_DATE_EPOCH=1700000000` |
| Wave 5.3 | Day 26 | ADR-037 Proposed; ADR-027 forward-pointer; §6 demoted; full pytest + regen green | BLOCKER (PRD Stage 6 entry) | grep + ADR file inspection |
| Wave 6.1 | Day 27 | ADR-037 Accepted dual-commit; carry-forward sanity-checks pass | BLOCKER | `grep -E "^status:" docs/architecture/02_ADRs/ADR-037-*.md` returns `Accepted` |
| Wave 6.2 | Day 28 | Triple Triad sign-off on tasks.md; 18 SCs verified | BLOCKER (SC-016 + Constitution VIII) | tasks.md frontmatter + spec.md SC-by-SC checklist |
| Wave 6.3 (CHECKPOINT 6) | Day 29 | PR #242 squash-merged `feat(241):`; release-please PR open; BLP-01 closes | BLOCKER (R12 + SC-016) | `gh pr list --state open --search "release-please"` returns ≥1 entry; CHANGELOG entry exists |

**End-of-feature gate (Day 29 close-out)**: All 18 SCs verifiable; 84/84 tasks marked `[X]`; PR squash-merged; release-please PR open; ADR-037 Accepted with both SHAs filled; §6 demoted; BLP-01 11-feature initiative status:done.

---

## 4. Time Estimates Per Wave

Wall-clock day-budgets per wave (working-day count). Sum equals 29 working days end-to-end (Day 1 = Thu 2026-04-30 → Day 29 = Wed 2026-06-10; Memorial Day Mon 5/25 non-working). The Buffer is reserved (out of envelope) for Risk 1 / Risk 3 absorption per FR-008 deferral path.

| Wave | Days | Working-Day Count | Cumulative | Wave Effort (h, sum across all primary agents) | Avg Daily Effort (h/day) |
|------|------|-------------------|------------|------------------------------------------------|--------------------------|
| 0.0 | Day 0 (Wed 4/29) | 1 (pre-feature) | 0 (excluded) | sign-off only | n/a |
| 1.1 | Days 1–2 (Thu 4/30, Fri 5/1) | 2 | 2 | 12.5 (T001+T002+T003+T004+T005+T006+T007+T008+T009+T010+T011) | 6.25 |
| 1.2 | Days 3–4 (Mon 5/4, Tue 5/5) | 2 | 4 | 8.5 (T012+T013+T014) | 4.25 |
| 1.3 | Day 5 (Wed 5/6) | 1 | 5 | 4.0 (T015) | 4.00 |
| 2.1 | Days 6–7 (Thu 5/7, Fri 5/8) | 2 | 7 | 11.0 (T016+T017+T025+T026) | 5.50 |
| 2.2 | Days 8–9 (Mon 5/11, Tue 5/12) | 2 | 9 | 8.5 (T018+T019+T027+T029) | 4.25 |
| 2.3 | Days 10–11 (Wed 5/13, Thu 5/14) | 2 | 11 | 14.5 (T020+T021+T022+T023+T024) | 7.25 |
| 3.1 | Days 12–13 (Fri 5/15, Mon 5/18) | 2 | 13 | 17.5 (T028+T030+T031+T032+T033+T034+T035) | 8.75 (split across 2 agents) |
| 3.2 | Days 14–16 (Tue 5/19, Wed 5/20, Thu 5/21) | 3 | 16 | 15.0 (T036+T037+T038+T039) | 5.00 |
| 4.1 | Day 17 (Fri 5/22) | 1 | 17 | 5.0 (T040) | 5.00 |
| Memorial Day (Mon 5/25) | — | 0 | 17 | 0 | 0 |
| 4.2 | Days 18–19 (Tue 5/26, Wed 5/27) | 2 | 19 | 12.0 (T041+T042+T043) | 6.00 |
| 4.3 | Days 20–21 (Thu 5/28, Fri 5/29) | 2 | 21 | 12.0 (T044+T045+T046+T047+T048) | 6.00 |
| 5.1 | Days 22–23 (Mon 6/1, Tue 6/2) | 2 | 23 | 8.5 (T049+T050+T051+T052) | 4.25 |
| 5.2 | Days 24–25 (Wed 6/3, Thu 6/4) | 2 | 25 | 12.5 (T053+T054+T055+T056+T057+T058) | 6.25 |
| 5.3 | Day 26 (Fri 6/5) | 1 | 26 | 11.5 (T059+T060+T061+T062 contingent + T071+T072+T073+T074+T075) | 11.50 (split across 4 agents — OK) |
| 6.1 | Day 27 (Mon 6/8) | 1 | 27 | 5.25 (T063+T064+T080+T081+T082+T083+T084) | 5.25 |
| 6.2 | Day 28 (Tue 6/9) | 1 | 28 | 5.5 (T065+T066+T070) | 5.50 |
| 6.3 | Day 29 (Wed 6/10) | 1 | 29 | 4.25 (T067+T068+T069+T076+T077+T078+T079) | 4.25 |
| Buffer | Days 30+ | reserve | 29+ | risk absorption | n/a |
| **Total** | **Day 1 → Day 29** | **29 working days** | **29** | **~167 effort hours** | ~5.8 h/day per primary owner |

**Sanity check**: 29 working days × 6 effort hours per day per primary owner = 174 effort-hours capacity for a single owner. The pessimistic-case load aggregate (~167 h) is within capacity when distributed across 6 primary agents, since most waves run 2 agents in parallel (e.g., Wave 2.1 has senior-backend-engineer on Stream 1 + security-analyst on Stream 2). The PRD Option A 5–6 working-week budget is held.

**Memorial Day handling**: Mon 2026-05-25 is non-working per `plan.md` §"Wave Breakdown". T040 fires last working day before (Fri 5/22 = Day 17). T041 fires first working day after (Tue 5/26 = Day 18). The 1-day calendar gap is excluded from working-day count and from the 80%/day cap math.

---

## 5. 80%/day Cap Math (Per-Agent Load Verification)

Per Team-Lead MEDIUM-R1, no agent's daily load may exceed 80% (4.8 effort hours of 6 nominal hours/day). Pair-authoring on Days 1–4 splits the senior-backend-engineer load with security-analyst on the STRIDE-heavy host wiring concentration (Wave 1.1 + 1.2). The matrix below shows per-agent daily load across all 29 working days. Daily load is computed as: hours assigned to that agent that day / 6 nominal hours.

### Per-agent load — Heatmap (rounded to 0.05; values >0.80 flagged)

| Day | Date | Wave | senior-backend-engineer | security-analyst | tester | architect | product-manager | orchestrator |
|-----|------|------|-------------------------|------------------|--------|-----------|-----------------|--------------|
| 1 | Thu 4/30 | 1.1 | 0.55 (T001+T007+T008 + half of T009) | 0.55 (pair half of T009) | 0.05 (T003) | 0.45 (T004+T005+T006) | 0 | wave-coord |
| 2 | Fri 5/1 | 1.1 | 0.55 (T002 + half of T010+T011) | 0.55 (pair half of T010+T011) | 0 | 0 | 0 | wave-coord |
| 3 | Mon 5/4 | 1.2 | 0.50 (half of T012) | 0.50 (pair half of T012) | 0 | 0 | 0 | — |
| 4 | Tue 5/5 | 1.2 | 0.50 (half of T013) | 0.50 (pair half of T013) | 0.40 (T014) | 0 | 0 | — |
| 5 | Wed 5/6 | 1.3 | 0.10 (T015 pair-support) | 0 | 0.65 (T015 lead) | 0 | 0 | wave-coord |
| 6 | Thu 5/7 | 2.1 | 0.40 (T016) | 0.50 (T025) | 0 | 0 | 0 | — |
| 7 | Fri 5/8 | 2.1 | 0.40 (T017) | 0.50 (T026) | 0 | 0 | 0 | — |
| 8 | Mon 5/11 | 2.2 | 0.40 (T018) | 0.35 (T029) | 0.25 (T027) | 0 | 0 | — |
| 9 | Tue 5/12 | 2.2 | 0.40 (T019) | 0 (T029 finished) | 0 | 0 | 0 | — |
| 10 | Wed 5/13 | 2.3 | 0.40 (T020) | 0 | 0.40 (T022 pair start) | 0 | 0 | — |
| 11 | Thu 5/14 | 2.3 | 0.50 (T021 + T022 pair-support + T024 pair-support) | 0 | 0.65 (T023+T024 lead) | 0 | 0 | wave-coord |
| 12 | Fri 5/15 | 3.1 | 0 | 0.55 (T028+T030 split) | 0.20 (T032) | 0 | 0 | — |
| 13 | Mon 5/18 | 3.1 | 0 | 0.55 (T031 + T028/T030 finish) | 0.55 (T032+T033+T035) | 0.10 (T034 contingent) | 0.10 (T034 contingent) | wave-coord |
| 14 | Tue 5/19 | 3.2 | 0 | 0.75 (T036+T037 lead) | 0 | 0 | 0 | — |
| 15 | Wed 5/20 | 3.2 | 0 | 0.75 (T038 lead) | 0 | 0 | 0 | — |
| 16 | Thu 5/21 | 3.2 | 0 | 0.65 (T039+finish T036/T037/T038) | 0 | 0 | 0 | — |
| 17 | Fri 5/22 | 4.1 | 0 | 0.70 (T040 lead) | 0 | 0.15 (T040 pair) | 0 | — |
| Mon 5/25 | Memorial Day | — | non-working | non-working | non-working | non-working | non-working | — |
| 18 | Tue 5/26 | 4.2 | 0 | 0.75 (T041 lead) | 0 | 0 | 0 | — |
| 19 | Wed 5/27 | 4.2 | 0 | 0.75 (T042+T043 lead) | 0 | 0 | 0 | — |
| 20 | Thu 5/28 | 4.3 | 0.55 (T044+T045 start) | 0 | 0 | 0.10 (T044 pair) | 0 | — |
| 21 | Fri 5/29 | 4.3 | 0.65 (T045 finish + T046 + T047 + T048 pair) | 0 | 0.40 (T048 lead) | 0 | 0 | wave-coord |
| 22 | Mon 6/1 | 5.1 | 0 | 0 | 0.75 (T049+T050 + T051 start) | 0 | 0 | — |
| 23 | Tue 6/2 | 5.1 | 0 | 0 | 0.40 (T051 finish + T052) | 0 | 0 | — |
| 24 | Wed 6/3 | 5.2 | 0.65 (T053+T054 start) | 0 | 0 | 0 | 0 | — |
| 25 | Thu 6/4 | 5.2 | 0.45 (T054 finish + T055) | 0 | 0.75 (T056+T057+T058) | 0 | 0 | wave-coord |
| 26 | Fri 6/5 | 5.3 | 0.50 (T061 + T071+T072 + T073+T074+T075) | 0 | 0.25 (T071 verify) | 0.80 (T059 lead + T060 + T062 contingent) | 0.15 (T062 contingent) | wave-coord |
| 27 | Mon 6/8 | 6.1 | 0.20 (T063 + T084 pair + T081 pair) | 0 | 0 | 0.75 (T064 + T080 + T081 + T082 + T083 + T084 lead) | 0 | — |
| 28 | Tue 6/9 | 6.2 | 0 | 0.25 (T070) | 0 | 0.25 (T065 pair) | 0.65 (T065 lead + T066) | wave-coord |
| 29 | Wed 6/10 | 6.3 | 0.65 (T067+T069 + T076+T077+T078+T079) | 0 | 0 | 0.10 (T068 lead) | 0 | wave-coord |

### Cap-violation audit

**Result: ZERO days exceed the 80% cap on any single agent.** Highest single-day load: 0.80 (architect Day 26 — full 4.5h ADR-037 narrative + 0.5h ADR-027 cross-link + 1.0h contingent T062 = exactly at cap, accepted by Team-Lead). Second-highest: 0.75 on multiple days (security-analyst Days 14/15/18/19/22 ATT&CK + ATLAS expansion peaks; tester Days 22/25 test-script + verification peaks; architect Day 27 carry-forward + Accept dual-commit).

**Pair-authoring effectiveness (Days 1–4)**: Without pair-authoring, T009/T010/T011/T012/T013 would each consume ~3h on senior-backend-engineer alone, peaking ~1.0 load on Day 1 (T009+T011 partial overlap). With pair-authoring per Team-Lead MEDIUM-R1, load splits 50/50 between senior-backend-engineer and security-analyst, holding both within 0.55 cap on Days 1–2 and 0.50 on Days 3–4. **Pair-authoring discipline confirmed essential to 80%/day cap math.**

**Contingent-task float**: T034 + T062 are CONTINGENT on Stream 2 closure failures per FR-008. If all 6 Partial closures succeed (the high-confidence path per Architect Q-Architect-2 analysis), T034 + T062 collapse to 0 effort and Day 13 + Day 26 loads decrease by ~0.20 each. Worst case (1–2 deferrals fire), T034 absorbs ~1.0h on Day 13 and T062 absorbs ~1.0h on Day 26, both within cap.

**Wave 5.3 architect Day 26 = 0.80 exactly**: Highest individual-agent day in the schedule. Composition: T059 ADR-037 narrative (4.5h) + T060 ADR-027 forward-pointer (0.5h) + T062 contingent deferral docs absorption (~0h–1.0h depending on T034 fire pattern). The 4.5h ADR-037 narrative is the largest single-task effort in the schedule. If contingent T062 fires fully, architect Day 26 hits 0.92 — REMEDY: shift T060 (0.5h) to Day 27 (architect already at 0.75; absorbs to 0.83 on Day 27, still within cap). Pre-emptive shift documented; orchestrator should monitor at end-Wave-5.2 checkpoint to decide.

**Stream 2 days (Days 12–13) split between security-analyst and tester**: security-analyst on T028+T030+T031 closures (~0.55 + 0.55 average); tester on T032+T033+T035 fixtures + audit test (~0.20 + 0.55). Confirms the 80%/day cap with comfortable margin; no shift required.

**Stream 3 ATT&CK Days 14–19 security-analyst-loaded**: Peaks at 0.75 daily. The ATT&CK 38→600 expansion is the largest single-task effort in the schedule (6.0h on T041 + 3.5h on T042). Remedy if cap exceeded: defer per FR-008 (Risk 1 absorption) — but cap math confirms this is not currently required.

**Verdict**: 80%/day cap math holds across all 29 working days for all 6 primary agents under nominal-path execution. Contingent-path execution (T034 + T062 fire fully) requires at most a 0.5h shift between Day 26 and Day 27 on architect; documented inline.

---

## 6. Coordination Notes

- **Pair-authoring window (Days 1–4)**: senior-backend-engineer leads, security-analyst pair-reviews. Per Team-Lead MEDIUM-R1, this is the only formal pair-authoring stretch in F-241; subsequent Stream 2 / Stream 3 / Stream 4 work is single-author (senior-backend-engineer or security-analyst per the matrix).
- **Cross-stream parallel days (Days 6–11)**: Stream 1 Wave 2 (senior-backend-engineer on T016/T017/T018/T019/T020/T021) runs in parallel with Stream 2 Waves 1+2 (security-analyst on T025/T026/T027/T029). Tester picks up fixtures (T027) and Wave-end verification (T022+T024) without overlap with primary wiring.
- **Memorial Day seam**: T040 last working day before (Fri 5/22 = Day 17); T041 first working day after (Tue 5/26 = Day 18). Calendar gap is excluded from working-day count and 80%/day cap math.
- **Wave coordination**: orchestrator engaged at Wave 1.3 (smoke test multi-agent), Wave 2.3 (closure verification multi-agent), Wave 3.1 (Stream 2 multi-closure), Wave 4.3 (aggregator + fixture multi-task), Wave 5.2 (8-baseline regen + verification), Wave 6.3 (PR merge + post-merge SHA + close-out polish). Wave-coord effort is not separately scheduled (folded into wave Quality Gates) per `.claude/agents/_README.md` Workflow Executor role definition.
- **Buffer reservation (Days 30+)**: Reserved for Risk 1 (T041 ATT&CK overrun → defer to follow-on Issue per FR-008) or Risk 3 (T034 + T062 contingent path fully fires). PRD already accepted pessimistic-case 0–0.5wk margin per Team-Lead MEDIUM-2.

---

## 7. Compliance Audit

- [x] All 84 tasks (T001–T084) assigned to a primary agent.
- [x] All primary agents are exact names from `.claude/agents/_README.md` registry: architect, orchestrator, product-manager, security-analyst, senior-backend-engineer, tester. No generic labels.
- [x] Pair-authoring on Days 1–4 (T009–T013) splits load between senior-backend-engineer and security-analyst per Team-Lead MEDIUM-R1.
- [x] Per-agent daily load ≤ 0.80 across all 29 working days under nominal-path execution. Contingent-path (T034 + T062 fire) requires at most a 0.5h shift between Day 26 and Day 27 on architect; documented in §5.
- [x] Wave-day mapping matches `plan.md` §"Wave Breakdown" (Wave 0.0 → 6.3 + Buffer); Memorial Day Mon 5/25 properly excluded.
- [x] Quality Gates between Waves capture BLOCKER vs ADVISORY severity per spec SC-level.
- [x] Time estimates per Wave sum to 29 working days (Day 1 = Thu 2026-04-30 → Day 29 = Wed 2026-06-10).
- [x] Architect carry-forwards M-1 (T060+T083), M-2 (T044+T045+T084), L-1 (T054+T055+T081) all owned by architect with senior-backend-engineer pair-support.
- [x] Contingent FR-008 path (T034 + T062) owned by product-manager with architect pair-author.
- [x] Triple Triad sign-off (T065) primary product-manager with architect + team-lead pair-authors.

---

**End of agent-assignments.md** — Authored 2026-05-01 by team-lead. PR #242 draft. Ready for orchestrator hand-off at Wave 1.1 start (Day 1 = Thu 2026-04-30).
