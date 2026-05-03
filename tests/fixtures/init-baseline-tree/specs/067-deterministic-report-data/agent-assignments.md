# Agent Assignments: Deterministic Report Data Extraction (067)

**Date**: 2026-03-30
**Feature Branch**: `067-deterministic-report-data`
**Feasibility**: APPROVED
**Total Tasks**: 32
**Estimated Duration**: Optimistic 3h | Realistic 4h | Pessimistic 6h

---

## Agent Assignment Matrix

| Task | Description | Agent (`subagent_type`) | Effort | Notes |
|------|-------------|------------------------|--------|-------|
| T001 | CLI skeleton with argparse | senior-backend-engineer | 10 min | Script creation |
| T002 | Artifact detection function | senior-backend-engineer | 5 min | File existence checks |
| T003 | Tier selection logic | senior-backend-engineer | 5 min | Conditional logic |
| T004 | `parse_frontmatter()` | senior-backend-engineer | 10 min | Regex extraction |
| T005 | `parse_markdown_table()` | senior-backend-engineer | 10 min | Core utility, gates all parsers |
| T006 | `strip_bold()` + `escape_typst_string()` | senior-backend-engineer | 5 min | String utilities |
| T007 | `parse_project_name()` | senior-backend-engineer | 5 min | Heading extraction |
| T008 | `parse_threats_severity()` | senior-backend-engineer | 10 min | Section 6 table parsing |
| T009 | `parse_threats_findings()` | senior-backend-engineer | 10 min | Section 7 table parsing |
| T010 | `parse_risk_scores_severity()` | senior-backend-engineer | 10 min | risk-scores.md Section 1 |
| T011 | `parse_risk_scores_findings()` | senior-backend-engineer | 10 min | risk-scores.md Section 2 |
| T012 | `parse_component_distribution()` | senior-backend-engineer | 5 min | Count + sort |
| T013 | `generate_report_data_typ()` | senior-backend-engineer | 15 min | Largest task -- ~25 variable categories |
| T014 | Wire `main()` + verify determinism | senior-backend-engineer | 10 min | Integration + diff test |
| T015 | `validate()` function | senior-backend-engineer | 10 min | Severity sum + ID uniqueness |
| T016 | Note severity handling | senior-backend-engineer | 5 min | Parse Note row, exclude from sum |
| T017 | `parse_scope_data()` | senior-backend-engineer | 20 min | 4 table types from 2 sections |
| T018 | Scope validation extension | senior-backend-engineer | 5 min | Count assertions |
| T019 | Update report-assembler agent | senior-backend-engineer | 10 min | Steps 2-3 replacement |
| T020 | Preserve report-config.typ copy | senior-backend-engineer | 5 min | Agent orchestration concern |
| T021 | `parse_threat_report_md()` | senior-backend-engineer | 10 min | Executive narrative extraction |
| T022 | `parse_compensating_controls_md()` | senior-backend-engineer | 15 min | Coverage + controls parsing |
| T023 | Remediation source priority | senior-backend-engineer | 10 min | 3-source priority chain |
| T024 | `detect_images()` + `detect_brand_assets()` | senior-backend-engineer | 10 min | File existence + path computation |
| T025 | Schema v1.0 compatibility | senior-backend-engineer | 5 min | Version check + skip logic |
| T026 | Verify Tier 2 (agentic-app) | tester | 5 min | Run twice, diff, verify counts |
| T027 | Create Tier 1 test fixture | senior-backend-engineer | 15 min | compensating-controls.md per schema |
| T028 | Verify Tier 1 fixture | tester | 5 min | Run with fixture, verify output |
| T029 | Verify Tier 3 scenario | tester | 5 min | Run without risk-scores.md |
| T030 | E2E `/security-report` verification | tester | 10 min | Full pipeline, verify PDF |
| T031 | Byte-identical PDF verification | tester | 5 min | Run twice, diff PDFs |
| T032 | Error handling verification | tester | 5 min | Missing file + bad data tests |

### Agent Workload Summary

| Agent (`subagent_type`) | Tasks Assigned | Total Effort | Utilization |
|------------------------|----------------|--------------|-------------|
| senior-backend-engineer | 25 tasks | ~3h 15min | 81% |
| tester | 5 tasks | ~30min | 13% |
| code-reviewer | 2 reviews (post-MVP, post-complete) | ~15min | 6% |

---

## Parallel Execution Waves

### Wave 1: Setup + Foundation (Phases 1-2)

**Goal**: Script skeleton with CLI, artifact detection, and core utilities.
**Duration**: ~50 min

| Step | Tasks | Agent | Parallel? |
|------|-------|-------|-----------|
| 1a | T001 (CLI skeleton) | senior-backend-engineer | Sequential |
| 1b | T002 (artifact detection) | senior-backend-engineer | Sequential (depends on T001) |
| 1c | T003 (tier selection) | senior-backend-engineer | Sequential (depends on T002) |
| 1d | T004, T005, T006 (frontmatter, table parser, string utils) | senior-backend-engineer | Parallel (3 independent functions) |
| 1e | T007 (project name) | senior-backend-engineer | Sequential (after T004 for frontmatter context) |

**Quality Gate**: Script runs, detects artifacts from `examples/agentic-app/sample-report/`, selects Tier 2, exits cleanly. Core utilities callable.

---

### Wave 2: MVP -- Tier 2 Determinism (Phase 3)

**Goal**: Complete Tier 2 end-to-end parsing with determinism verification.
**Duration**: ~60 min

| Step | Tasks | Agent | Parallel? |
|------|-------|-------|-----------|
| 2a | T008, T009 (threats severity + findings) | senior-backend-engineer | Parallel (independent parsers) |
| 2b | T010, T011 (risk-scores severity + findings) | senior-backend-engineer | Parallel (independent parsers) |
| 2c | T012 (component distribution) | senior-backend-engineer | After T009 or T011 (needs findings) |
| 2d | T013 (Typst generation) | senior-backend-engineer | After T008-T012 (needs all parsed data) |
| 2e | T014 (wire main + verify) | senior-backend-engineer | After T013 |

**Quality Gate**: Run script twice on `examples/agentic-app/sample-report/`, diff outputs. Zero differences. **MVP COMPLETE.**

**Post-MVP Review**: code-reviewer validates script structure, naming conventions, and data-model.md contract compliance.

---

### Wave 3: Validation + Scope + Agent (Phases 4-6)

**Goal**: Add validation, scope extraction, and agent integration.
**Duration**: ~55 min

| Step | Tasks | Agent | Parallel? |
|------|-------|-------|-----------|
| 3a | T015, T016 (validation + Note handling) | senior-backend-engineer | Parallel (independent additions) |
| 3b | T017, T018 (scope parsing + scope validation) | senior-backend-engineer | Sequential (T018 depends on T017) |
| 3c | T019, T020 (agent update + report-config) | senior-backend-engineer | After T014 complete (needs working script) |

Steps 3a and 3b can run concurrently with 3c (different files: Python script vs agent markdown).

**Quality Gate**: Validation catches injected errors (exit 2). Scope counts match source. `/security-report` invokes script and produces PDF.

---

### Wave 4: Tier 1 + Recommendations (Phase 7)

**Goal**: Complete all three tiers with recommendation extraction.
**Duration**: ~35 min

| Step | Tasks | Agent | Parallel? |
|------|-------|-------|-----------|
| 4a | T021 (threat-report parsing) | senior-backend-engineer | Parallel with 4b |
| 4b | T022 (compensating-controls parsing) | senior-backend-engineer | Parallel with 4a |
| 4c | T023 (remediation priority) | senior-backend-engineer | After T021 + T022 |

**Quality Gate**: All three tiers produce valid output. Recommendations extracted verbatim. Tier 1 parsing complete.

---

### Wave 5: Testing + Polish (Phases 8-9)

**Goal**: Full verification across all tiers, E2E PDF, error handling.
**Duration**: ~65 min

| Step | Tasks | Agent | Parallel? |
|------|-------|-------|-----------|
| 5a | T024 (image + brand detection) | senior-backend-engineer | Parallel with 5b |
| 5b | T025 (schema v1.0 compat) | senior-backend-engineer | Parallel with 5a |
| 5c | T027 (create Tier 1 fixture) | senior-backend-engineer | After T022 (needs controls parser) |
| 5d | T026 (verify Tier 2) | tester | After Wave 2 complete |
| 5e | T028 (verify Tier 1) | tester | After T027 (needs fixture) |
| 5f | T029 (verify Tier 3) | tester | Parallel with T026/T028 |
| 5g | T030 (E2E security-report) | tester | After Wave 3 (needs agent update) |
| 5h | T031 (byte-identical PDF) | tester | After T030 |
| 5i | T032 (error handling) | tester | Parallel with T030 |

**Quality Gate**: All 3 tiers verified with determinism. E2E PDF generated. Error handling confirmed (exit 1 for missing file, exit 2 for bad data).

**Final Review**: code-reviewer validates complete script for code quality, naming, edge case coverage, and data-model.md compliance.

---

## Wave Summary

| Wave | Phases | Duration | Key Deliverable |
|------|--------|----------|-----------------|
| Wave 1 | 1-2 | ~50 min | Script skeleton + core utilities |
| Wave 2 | 3 | ~60 min | **MVP: Tier 2 determinism verified** |
| Wave 3 | 4-6 | ~55 min | Validation + scope + agent integration |
| Wave 4 | 7 | ~35 min | All 3 tiers + recommendations |
| Wave 5 | 8-9 | ~65 min | Full testing + E2E + polish |
| **Total** | **1-9** | **~265 min (~4.4h)** | Feature complete |

---

## Quality Gates Between Waves

| Gate | Between | Validation | Pass Criteria |
|------|---------|-----------|---------------|
| G1 | Wave 1 -> Wave 2 | Run script on example data | Exits cleanly, tier detected, no errors |
| G2 | Wave 2 -> Wave 3 | **MVP gate**: diff two runs | Zero differences in output files |
| G3 | Wave 3 -> Wave 4 | Validation + E2E | Exit code 2 on bad data; `/security-report` produces PDF |
| G4 | Wave 4 -> Wave 5 | Tier coverage | All 3 tiers produce valid output |
| G5 | Wave 5 exit | Final verification | All tester tasks pass; code-reviewer approves |

**STOP-and-VALIDATE at G2**: This is the MVP checkpoint. If the diff test fails at G2, do not proceed to Wave 3. Debug determinism issues first.

---

## Time Estimates Per Wave

| Wave | Optimistic | Realistic | Pessimistic |
|------|-----------|-----------|-------------|
| Wave 1 | 35 min | 50 min | 75 min |
| Wave 2 | 45 min | 60 min | 90 min |
| Wave 3 | 40 min | 55 min | 80 min |
| Wave 4 | 25 min | 35 min | 50 min |
| Wave 5 | 45 min | 65 min | 90 min |
| **Total** | **190 min (3.2h)** | **265 min (4.4h)** | **385 min (6.4h)** |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation | Owner |
|------|-----------|--------|------------|-------|
| Table parsing edge cases not covered by research | Low | Medium | Edge cases documented in research.md; malformed rows skip with warning | senior-backend-engineer |
| Typst string escaping produces invalid syntax | Low | Low | Only 3 escape rules; test with real data | senior-backend-engineer |
| Tier 1 fixture does not match real pipeline output | Medium | Low | Schema at `schemas/compensating-controls.yaml` is authoritative | senior-backend-engineer |
| PDF not byte-identical due to Typst metadata | Medium | Medium | Verify Typst does not inject timestamps; test at G2 | tester |
| T013 (Typst generation) takes longer than estimated | Medium | Low | data-model.md specifies all variables; no ambiguity | senior-backend-engineer |

---

Signed: team-lead | 2026-03-30
