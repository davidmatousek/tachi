# Agent Assignments: Feature 112 — Attack Path Pages in Security Report PDF

**Date**: 2026-04-09
**Feasibility**: APPROVED
**Estimated Duration**: 1.5-2 hours (with parallel waves), 2-3 hours (sequential)
**Confidence**: HIGH

---

## Agent Assignment Matrix

| Task | Description | Agent | File(s) | Effort |
|------|-------------|-------|---------|--------|
| T001 | `detect_artifacts()` attack-trees detection | senior-backend-engineer | `scripts/tachi_parsers.py` | S |
| T002 | `parse_attack_trees()` function | senior-backend-engineer | `scripts/extract-report-data.py` | M |
| T003 | `render_mermaid_to_png()` function | senior-backend-engineer | `scripts/extract-report-data.py` | M |
| T004 | Narrative construction + remediation splitting | senior-backend-engineer | `scripts/extract-report-data.py` | S |
| T005 | Attack tree data binding in `format_report_data()` | senior-backend-engineer | `scripts/extract-report-data.py` | S |
| T006 | `attack-path.typ` page template | frontend-developer | `templates/tachi/security-report/attack-path.typ` | M |
| T007 | `main.typ` orchestrator update | frontend-developer | `templates/tachi/security-report/main.typ` | S |
| T008 | Section divider + TOC validation | tester | `templates/tachi/security-report/main.typ` | S |
| T009 | `security-report.md` artifact detection table | code-reviewer | `.claude/commands/security-report.md` | S |
| T010 | `report-assembler.md` artifact detection | code-reviewer | `.claude/agents/tachi/report-assembler.md` | S |
| T011 | Regenerate `agentic-app` example | senior-backend-engineer | `examples/agentic-app/sample-report/` | S |
| T012 | Regenerate `cloud-native` example | senior-backend-engineer | `examples/cloud-native/sample-report/` | S |
| T013 | Regenerate `data-pipeline` example | senior-backend-engineer | `examples/data-pipeline/sample-report/` | S |
| T014 | Regenerate `healthcare-ai` example | senior-backend-engineer | `examples/healthcare-ai/sample-report/` | S |
| T015 | Regenerate `iot-fleet` example | senior-backend-engineer | `examples/iot-fleet/sample-report/` | S |
| T016 | Regenerate `rag-chatbot` example | senior-backend-engineer | `examples/rag-chatbot/sample-report/` | S |
| T017 | CLAUDE.md Recent Changes update | code-reviewer | `CLAUDE.md` | S |
| T018 | Backward compatibility validation | tester | (all examples) | S |

**Effort Key**: S = Small (<15 min), M = Medium (15-30 min), L = Large (30+ min)

---

## Agent Workload Summary

| Agent | Task Count | Waves Active | Max Concurrent | Load |
|-------|-----------|-------------|----------------|------|
| senior-backend-engineer | 11 | 1, 2, 3, 6 | 6 (Wave 6) | 55% |
| frontend-developer | 2 | 1, 4 | 1 | 15% |
| tester | 2 | 5, 7 | 1 | 15% |
| code-reviewer | 3 | 1, 6 | 2 (Wave 1) | 15% |

No agent exceeds 60% load. Workload is balanced with natural idle periods between waves.

---

## Parallel Execution Waves

### Wave 1 — Foundation (no dependencies)
**Duration**: 30-45 min | **Agents**: 3 in parallel

| Task | Agent | File | Depends On |
|------|-------|------|-----------|
| T001 | senior-backend-engineer | `scripts/tachi_parsers.py` | — |
| T002 | senior-backend-engineer | `scripts/extract-report-data.py` | — |
| T006 | frontend-developer | `templates/.../attack-path.typ` | — |
| T009 | code-reviewer | `.claude/commands/security-report.md` | — |
| T010 | code-reviewer | `.claude/agents/tachi/report-assembler.md` | — |

**Note**: T001 and T002 target different files, safe for same agent in sequence. T006 is a new file, fully independent.

---

### Wave 2 — Extraction Extensions (depends on Wave 1: T002)
**Duration**: 20-30 min | **Agents**: 1

| Task | Agent | File | Depends On |
|------|-------|------|-----------|
| T003 | senior-backend-engineer | `scripts/extract-report-data.py` | T002 |
| T004 | senior-backend-engineer | `scripts/extract-report-data.py` | T002 |

**Note**: Both modify same file. Execute sequentially within agent.

---

### Wave 3 — Data Binding (depends on Wave 2: T003, T004)
**Duration**: 10-15 min | **Agents**: 1

| Task | Agent | File | Depends On |
|------|-------|------|-----------|
| T005 | senior-backend-engineer | `scripts/extract-report-data.py` | T003, T004 |

---

### Wave 4 — Orchestrator Integration (depends on Wave 1: T006, Wave 3: T005)
**Duration**: 15-20 min | **Agents**: 1

| Task | Agent | File | Depends On |
|------|-------|------|-----------|
| T007 | frontend-developer | `templates/.../main.typ` | T005, T006 |

---

### Wave 5 — Validation Gate (depends on Wave 4: T007)
**Duration**: 15-20 min | **Agents**: 1

| Task | Agent | File | Depends On |
|------|-------|------|-----------|
| T008 | tester | Full pipeline | T007 |

**Quality Gate**: Compile `agentic-app` example. Verify:
- Attack path pages render in PDF
- Section divider page present
- TOC includes "Attack Path Analysis"
- Page numbering continuous

---

### Wave 6 — Example Regeneration (depends on Wave 5: T008)
**Duration**: 20-30 min | **Agents**: 2 in parallel

| Task | Agent | File | Depends On |
|------|-------|------|-----------|
| T011 | senior-backend-engineer | `examples/agentic-app/` | T008 |
| T012 | senior-backend-engineer | `examples/cloud-native/` | T008 |
| T013 | senior-backend-engineer | `examples/data-pipeline/` | T008 |
| T014 | senior-backend-engineer | `examples/healthcare-ai/` | T008 |
| T015 | senior-backend-engineer | `examples/iot-fleet/` | T008 |
| T016 | senior-backend-engineer | `examples/rag-chatbot/` | T008 |
| T017 | code-reviewer | `CLAUDE.md` | T008 |

**Note**: T011-T016 are all independent (different directories). T017 has no file dependencies on T011-T016.

**Note**: Only `agentic-app` has attack-trees. T012-T016 validate backward compatibility (no attack path pages generated, no errors).

---

### Wave 7 — Final Validation (depends on Wave 6: T011-T016)
**Duration**: 15-20 min | **Agents**: 1

| Task | Agent | File | Depends On |
|------|-------|------|-----------|
| T018 | tester | (all examples) | T011-T016 |

**Quality Gate**: Backward compatibility confirmed. Verify:
- No attack path pages in examples without `attack-trees/`
- No errors or warnings
- All existing pages render correctly
- Output matches pre-feature baseline for non-attack-tree examples

---

## Quality Gates Between Waves

| Gate | After Wave | Before Wave | Validation |
|------|-----------|-------------|-----------|
| **Extraction Pipeline** | 3 | 4 | Run `python3 scripts/extract-report-data.py --target-dir examples/agentic-app/sample-report/ --output /tmp/test-data.typ` and verify attack tree variables in output |
| **Full Pipeline** | 4 | 5 | Compile `agentic-app` example through extraction + Typst and verify pages in PDF |
| **Section + TOC** | 5 | 6 | Verify section divider, TOC entry, continuous page numbers |
| **Backward Compat** | 7 | Done | Verify examples without attack trees produce unchanged output |

---

## Critical Path

```
T002 ──> T003 ──> T005 ──> T007 ──> T008 ──> T011-T016 ──> T018
              └──> T004 ──┘
```

**Estimated critical path duration**: ~2 hours

**Off-critical-path tasks** (can execute in parallel without blocking):
- T001 (Wave 1, parallel with T002)
- T006 (Wave 1, parallel with T002, different agent)
- T009, T010 (Wave 1, documentation)
- T017 (Wave 6, documentation)
