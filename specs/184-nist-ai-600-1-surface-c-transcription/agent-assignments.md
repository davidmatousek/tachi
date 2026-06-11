---
feature: 184-nist-ai-600-1-surface-c-transcription
artifact: agent-assignments.md
author: team-lead
date: 2026-06-10
branch: 184-nist-ai-600-1-surface-c-transcription
source_tasks: specs/184-nist-ai-600-1-surface-c-transcription/tasks.md
tasks_count: 15
waves_count: 5 (W0 → W1 → W2 → W3 → W4) + final pre-PR gate
calendar:
  day_1: 2026-06-10 (same-day expectation — realistic 0.75–1.0 d; pessimistic tail 1.25 d spills to next morning only)
signoff:
  team_lead: APPROVED (2026-06-10 — tasks.md timeline/feasibility review, .aod/results/team-lead.md)
  pm: recorded in tasks.md frontmatter by /aod.tasks (parallel review)
  architect: recorded in tasks.md frontmatter by /aod.tasks (parallel review)
supersedes: F-224 agent-assignments.md (2026-04-26) — stale file replaced at F-184 tasks sign-off
---

# Agent Assignments — Feature 184 NIST AI 600-1 Surface C Transcription

Operationalizes `specs/184-nist-ai-600-1-surface-c-transcription/tasks.md` (15 tasks, W0–W4 + final gate) into agent-by-wave execution units. All `subagent_type` values are exact entries from `.claude/agents/_README.md`. Single-executor model with checkpoint gates (Team-Lead Q3; #186 lesson: parallelism is isolation, not speedup).

**Binding contract**: `specs/184-nist-ai-600-1-surface-c-transcription/contracts/surface-c-transcription.contract.md` (C1–C6). **Verification commands**: `quickstart.md` (interpreter-pinned `/usr/bin/python3`). **All wave gates use 541/578.**

---

## 1. Agent Assignment Matrix

| Task ID | Wave | Agent (`subagent_type`) | Parallel | Notes |
|---------|------|-------------------------|----------|-------|
| T001 | W0 | `senior-backend-engineer` | — | Baseline suite 5/5 via `/usr/bin/python3` (Team-Lead C5 pin). **STOP-gate** |
| T002 | W0 | `senior-backend-engineer` | — | Count pins: 542/37/0=579; drift class =16 (1:1 vs C3); control→rmf =31 (do NOT touch — 4 extras are Issue #325); →nist-ai-600-1 =0. **STOP-gate** |
| T003 | W1 | `senior-backend-engineer` | — | Catalog per contract C1 (12 records, quoted ids — Team-Lead C3) |
| T004 | W1 | `senior-backend-engineer` | — | C4 test surgery: 7 edit sites + site-8 invariant (`_sort_key_nist` byte-untouched; separate `_sort_key_section` — Team-Lead C4) |
| T005 | W1 | `senior-backend-engineer` | — | W1 gate + single commit; AST byte-untouched check (Architect F2) |
| T006 | W2 | `senior-backend-engineer` | — | Remove 16 drift edges by class filter (never line ranges); pair-list 1:1 vs C3 |
| T007 | W2 | `senior-backend-engineer` | — | Append 15 Surface C edges per C2 (quoted target ids) |
| T008 | W2 | `senior-backend-engineer` | — | Crosswalk header (8-value enum, 541/37/0) + retire mid-file deferral NOTE |
| T009 | W2 | `senior-backend-engineer` | — | W2 gate + ONE change-set commit; **tester validates gate output** (541/37/0=578; drift=0; control→rmf still 31). Shippable MVP |
| T010 | W3 | `code-reviewer` | — | Transcription-fidelity (15 adds, 16 removes 1:1 vs contract) + diff drift-guard + exempt-surface zero-diff. Risk-184.3 gate |
| T011 | W4 | `senior-backend-engineer` | [P] | ADR-027 entry + Decision 3 annotation + arch README blurb — ONE commit (OQ-3). **Architect reviews entry text at build checkpoint** |
| T012 | W4 | `senior-backend-engineer` | [P] | taxonomy README §3.8 + snippet/composition/count updates per C5 |
| T013 | W4 | `senior-backend-engineer` | [P] | CHANGELOG hand-curated Unreleased `feat(184)` (dual-CHANGELOG model — no release-please edits) |
| T014 | W4 | `senior-backend-engineer` | — | W4 sweep gate (one expected F-186 lineage survivor); **tester validates gate output**; commits (T011 alone; T012+T013 may share) |
| T015 | Final | `senior-backend-engineer` | — | Full pre-PR gate + `/aod.analyze` + PR #324 title check + push. Deliver-time items excluded |

**Deliver-time (NOT build tasks)**: Issue #184 `stage:done` closure + OQ-4 ADR-025 one-line note (incl. §2.6 or/and observation) + PR ready/squash-merge → `product-manager` / `architect` at `/aod.deliver`.

**Agent-count summary**: `senior-backend-engineer` 14 (executor), `code-reviewer` 1 (T010), `tester` gate-validation at T009/T014 outputs, `architect` ADR-text checkpoint at T011. All `subagent_type` values valid per `.claude/agents/_README.md`.

---

## 2. Wave Sequencing & Critical Path

```
T001 → T002 → [T003 → T004 → T005] → [T006 → T007 → T008 → T009 → T010] → [T011 ∥ T012 ∥ T013 → T014] → T015
      W0              W1 (1 commit)              W2 (1 commit)      W3              W4 (2 commits)          gate
```

- **Cycles**: none. **False parallelism**: none — only T011/T012/T013 are [P] (three disjoint files), and they still serialize on the single executor (isolation, not speedup).
- **FR-008 ordering invariant**: catalog + test surgery (W1) land before/with the edge change-set (W2); suite 5/5 at every commit boundary.
- **Gates**: T001/T002 STOP-gates (abort + escalate on red/drift) · T005 W1 gate · T009 W2 gate (MVP) · T010 W3 fidelity gate · T014 W4 sweep gate · T015 pre-PR gate. Gate evidence → `specs/184-*/test-results/`.

---

## 3. Capacity Check

| Agent | Load (single day) | Verdict |
|-------|-------------------|---------|
| `senior-backend-engineer` | ~60–80% (≈4.5–6.5h content across 14 tasks; governance docs W4 is the largest bucket) | PASS — at ceiling only in the pessimistic case, which spills to next morning rather than overloading |
| `code-reviewer` | ~10% (T010 fidelity + drift-guard) | PASS |
| `tester` | ~5% (T009/T014 gate-output validation) | PASS |
| `architect` | ~5% (T011 ADR entry text checkpoint) | PASS |

No agent >80% at the realistic point. Effort envelope **0.75–1.25 d; realistic 0.75–1.0 d; expect same-day** (Team-Lead calibration, FR-7 +0.1–0.15 d already folded).

---

## 4. Scheduling Directives (binding)

1. **Serialize #185** (Team-Lead C2): do NOT start #185's build mid-#184 — `crosswalk.yaml`, `schemas/taxonomy/README.md`, `CHANGELOG.md` are shared surfaces.
2. **Issue #325 fence**: the 4 `tachi-control-category → nist-ai-rmf` non-table extras are out of scope — control→rmf stays exactly 31 at every gate.
3. **Exempt surfaces** (contract C5): zero diffs on `docs/architecture/01_system_design/README.md`, `specs/180-*`, ratified ADR bodies, historical PRDs, release-please CHANGELOG sections.
4. **Interpreter pin** (Team-Lead C5): all test/verification invocations use `/usr/bin/python3`.
5. **Avoid** (tasks.md Notes): editing `_sort_key_nist`, splitting the W2 change-set, folding deliver-time actions into build.

---

## 5. Handoff to Orchestrator

- Follow Section 2 strictly; do not advance past a gate without green state; STOP-gates at T001/T002 abort the run.
- Dispatch exact `subagent_type` values from Section 1 — no improvisation.
- On any STOP-gate failure or unintended diff at T010: PAUSE, surface to team-lead + architect.
- Entry command: `/aod.build`.

**End of Agent Assignments — Feature 184**
