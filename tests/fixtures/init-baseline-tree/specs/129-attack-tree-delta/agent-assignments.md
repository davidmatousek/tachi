# Agent Assignments: Feature 129 — Attack Tree Delta Sub-Agent

**Feature**: 129-attack-tree-delta
**Generated**: 2026-04-13
**Total Tasks**: 13 (T001-T013)
**Total Waves**: 7
**Estimated Duration**: 3.5-4.0 hours

---

## Agent Assignment Matrix

| Task | Description | Agent | Rationale |
|------|-------------|-------|-----------|
| T001 | Add Baseline Reconciliation section to attack-tree-construction.md | senior-backend-engineer | Markdown reference file authoring |
| T002 | Add Section 5 Delta Annotations to narrative-templates.md | senior-backend-engineer | Markdown reference file authoring |
| T003 | Create attack-tree-delta.md sub-agent definition | senior-backend-engineer | Agent definition authoring (SKILL.md pattern) |
| T004 | Externalize similarity algorithm to reference file | senior-backend-engineer | Reference content extraction to maintain line cap |
| T005 | Update attack_tree_count in schemas/report.yaml | senior-backend-engineer | Schema definition edit |
| T006 | Update attack_tree_count in output-schemas/threat-report.md | senior-backend-engineer | Output schema markdown edit |
| T007 | Add Agent to threat-report.md frontmatter tools list | senior-backend-engineer | Agent frontmatter config edit |
| T008 | Refactor threat-report.md Section 5 logic | senior-backend-engineer | Critical agent logic refactor (largest task) |
| T009 | Update agent roster _README.md | senior-backend-engineer | Registry markdown edit |
| T010 | Verify backward compatibility (test suite) | tester | Backward-compat validation via pytest |
| T011 | Verify sub-agent line count within Leaf tier | tester | Line count compliance check (SC-005) |
| T012 | Verify threat-report line count under Report tier | tester | Line count compliance check (SC-003) |
| T013 | Cross-check attack_tree_count definition consistency | tester | Cross-file definition consistency audit (SC-002) |

**Agent Load Summary**:
- senior-backend-engineer: 9 tasks (T001-T009) — all implementation
- tester: 4 tasks (T010-T013) — all validation

---

## Parallel Execution Waves

### Wave 1: Reference File Updates (Phase 1)
**Parallel**: T001 + T002
**Agent**: senior-backend-engineer
**Duration**: ~25 min
**Dependencies**: None — can start immediately

| Task | File | Action |
|------|------|--------|
| T001 | `.claude/skills/tachi-threat-reporting/references/attack-tree-construction.md` | Add Baseline Reconciliation section |
| T002 | `.claude/skills/tachi-threat-reporting/references/narrative-templates.md` | Add Section 5 Delta Annotations section |

**Quality Gate**: Both reference files updated. Sub-agent can now load reconciliation guidance at workflow start.

---

### Wave 2: Sub-Agent Creation (Phase 2 — MVP Core)
**Sequential**: T003
**Agent**: senior-backend-engineer
**Duration**: ~35 min
**Dependencies**: T001 (sub-agent loads attack-tree-construction.md at workflow start)

| Task | File | Action |
|------|------|--------|
| T003 | `.claude/agents/tachi/attack-tree-delta.md` | Create new Leaf-tier sub-agent definition |

**Quality Gate**: Sub-agent file exists with correct frontmatter (name, tools, model). Rule dispatch logic covers Rules 1-3 + no-baseline fallback. Line count target 100-150 (hard cap 200).

---

### Wave 3: Externalization + Schema Alignment (Phase 2 + Phase 3)
**Parallel**: T004 + T005 + T006
**Agent**: senior-backend-engineer
**Duration**: ~30 min
**Dependencies**: T004 depends on T003 (refines externalization from agent to reference). T005 and T006 are independent of all prior waves.

| Task | File | Action |
|------|------|--------|
| T004 | `.claude/skills/tachi-threat-reporting/references/attack-tree-construction.md` | Externalize similarity algorithm details from agent |
| T005 | `schemas/report.yaml` | Update attack_tree_count canonical definition |
| T006 | `templates/tachi/output-schemas/threat-report.md` | Update attack_tree_count to match canonical definition |

**Quality Gate**: Sub-agent references externalized algorithm (not inlined). Schema and output template definitions are identical. T004 does not push sub-agent over Leaf tier line cap.

---

### Wave 4: Threat-Report Frontmatter (Phase 4 — Prep)
**Sequential**: T007
**Agent**: senior-backend-engineer
**Duration**: ~10 min
**Dependencies**: None strictly, but sequenced before T008 per tasks.md (frontmatter before logic)

| Task | File | Action |
|------|------|--------|
| T007 | `.claude/agents/tachi/threat-report.md` | Add `Agent` to tools list in frontmatter |

**Quality Gate**: threat-report.md frontmatter tools list includes Agent. No other frontmatter fields changed.

---

### Wave 5: Section 5 Refactor (Phase 4 — Critical Path)
**Sequential**: T008
**Agent**: senior-backend-engineer
**Duration**: ~50 min (largest task — refactor with preservation requirements)
**Dependencies**: T003 (sub-agent must exist), T007 (Agent tool must be in frontmatter)

| Task | File | Action |
|------|------|--------|
| T008 | `.claude/agents/tachi/threat-report.md` | Remove Rules 1-3, add sub-agent spawn + manifest consumption |

**Quality Gate**: Section 5 delegates to attack-tree-delta sub-agent. Sections 1-4, 6-8 unchanged. Correlation group cross-referencing (Section 4a) remains in threat-report. Line count trending toward sub-300.

---

### Wave 6: Roster Update (Phase 4 — Finalization)
**Sequential**: T009
**Agent**: senior-backend-engineer
**Duration**: ~10 min
**Dependencies**: T003 (sub-agent must exist to register)

| Task | File | Action |
|------|------|--------|
| T009 | `.claude/agents/_README.md` | Add attack-tree-delta entry to Agent Roster |

**Quality Gate**: Roster entry includes tier (Leaf), description, spawned-by (threat-report), and note about first pipeline sub-spawning pattern.

---

### Wave 7: Validation (Phase 5)
**Parallel**: T010 + T011 + T012 + T013
**Agent**: tester
**Duration**: ~20 min
**Dependencies**: All implementation waves (1-6) complete

| Task | Validation Target | Pass Criteria |
|------|-------------------|---------------|
| T010 | Backward compatibility | 5/5 baselines byte-identical under SOURCE_DATE_EPOCH=1700000000 |
| T011 | Sub-agent line count | 100-150 target, hard cap 200 (SC-005) |
| T012 | Threat-report line count | Under 300-line Report tier hard cap (SC-003) |
| T013 | attack_tree_count consistency | Identical definition in schemas/report.yaml, output-schemas/threat-report.md, and manifest instructions (SC-002) |

**Quality Gate**: All 4 validation checks pass. Feature is ready for PR.

---

## Execution Summary

| Wave | Tasks | Agent | Parallel | Duration |
|------|-------|-------|----------|----------|
| 1 | T001, T002 | senior-backend-engineer | Yes | ~25 min |
| 2 | T003 | senior-backend-engineer | No | ~35 min |
| 3 | T004, T005, T006 | senior-backend-engineer | Yes | ~30 min |
| 4 | T007 | senior-backend-engineer | No | ~10 min |
| 5 | T008 | senior-backend-engineer | No | ~50 min |
| 6 | T009 | senior-backend-engineer | No | ~10 min |
| 7 | T010, T011, T012, T013 | tester | Yes | ~20 min |
| **Total** | **13 tasks** | **2 agents** | | **~3h (optimistic) / ~3.5h (realistic) / ~4h (pessimistic)** |

**Critical Path**: Wave 1 -> Wave 2 -> Wave 3 (T004) -> Wave 4 -> Wave 5 -> Wave 6 -> Wave 7

**Risk Note**: T008 (Wave 5) is the highest-risk task — refactoring Section 5 logic while preserving Sections 1-4 and 6-8 unchanged. Budget extra time for careful diff review after this wave.

---

**End of Agent Assignments**
