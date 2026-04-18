# Session Continuation: Feature 189 — F-A2 Source Attribution Schema Extension

**Generated**: 2026-04-17
**Branch**: `189-source-attribution-schema-extension`
**Last Commit**: `b2419b6 docs(180): post-delivery quality review (#188)` (pre-session baseline)
**Status**: Partial `/aod.build` run — stopped at 3-wave hard ceiling (standalone mode)

---

## Completed This Session

Waves 1.1, 2.1, 3.1 delivered (11/36 tasks). US1 MVP is functional; US-189-1 AC-3 round-trip proven end-to-end.

### Wave 1.1 — Day 1 AM (Schema Lock + Architect Memo)
- **T001** ✅ ADR-028 Proposed authored (355 lines) at `docs/architecture/02_ADRs/ADR-028-source-attribution-schema-extension.md`. Resolves Q1 (Q1-E primary conditional `## 9. Source Attribution` YAML block; Q1-B sidecar fallback), Q2 (Q2-B two-tier validation), Q3 (ADR-028 mechanical). Documents all 6 FR-014 body items + dual-commit governance protocol.
- **T002** ✅ Created `tests/scripts/fixtures/source_attribution/` with `.gitkeep`.
- **T003** ✅ Baseline git diff verified — no polluting drift.

### Wave 2.1 — Day 1 PM (Schema Bump)
- **T004** ✅ `schemas/finding.yaml` `schema_version` bumped `"1.4"` → `"1.5"`; new `source_attribution` optional list-of-RECORD field appended after `baseline_run_id`.
- **T005** ✅ Section header comment block authored (`# Source Attribution (v1.5 — Feature 189)`).

### Wave 3.1 — Day 2 AM (US1 MVP — Multi-Framework Citation)
- **T006** ✅ Fixture `valid_multi_record.md` — LLM-5 finding with 3 attribution records (owasp/LLM05, cwe/CWE-1426, mitre-atlas/AML.T0051).
- **T007** ✅ Fixture `valid_single_record.md` — S-1 finding with 1 record (owasp/A01, relationship omitted for default-injection path).
- **T008** ✅ `test_round_trip_multi_record` — PASS.
- **T009** ✅ `test_round_trip_single_record` — PASS.
- **T010** ✅ `_extract_source_attribution_block` + `_extract_source_attribution` + `_parse_source_attribution_flow_dict` helpers added to `scripts/tachi_parsers.py`. Conditional injection wired into `parse_threats_findings` after the delta_status block. Stdlib-only (PAT-014 preserved).
- **T011** ✅ V5 shape validation inside `_extract_source_attribution` — exactly 2 or 3 keys per record; extras raise `ValueError` with finding ID + offending keys.

### Checkpoint 3 (post-Wave 3.1) — GREEN
US1 tests pass (T008 + T009). Multi-framework citation round-trip is functional and testable independently.

### P0 Architect Checkpoint — APPROVED
Retroactive checkpoint fired at end of Wave 3.1. Verdict: **APPROVED**. Verified:
- 22-file zero-edit invariant preserved (empty diff on `.claude/agents/tachi/{stride,ai}/` + `detection-patterns.md`)
- Zero new runtime dependencies (empty diff on `requirements-dev.txt`, `pyproject.toml`, `package.json`)
- Q1-E Section 9 shape fully implementable by F-A3 without revisiting Wave 1-3 decisions
- No blockers for Wave 4.1+

Architect non-blocking observations for next session:
1. `validate_source_attribution` post-parse helper not yet implemented (Wave 5.1 / T027 scope).
2. Wave 4.1 should add absent-section omits-key + explicit `[]` preserved-empty assertions.
3. V1/V2/V3/V5 parser-tier failure paths need negative-path fixtures (Wave 4.1/5.1).

---

## Current State

- **Phase**: implement (mid-flight; Wave 4.1 is next)
- **Uncommitted**: 10 files (5 tracked modifications + 5 untracked)
  - Modified: `schemas/finding.yaml`, `scripts/tachi_parsers.py`, `docs/architecture/01_system_design/README.md`, `docs/product/02_PRD/INDEX.md`, `docs/product/_backlog/BACKLOG.md`
  - New: `docs/architecture/02_ADRs/ADR-028-source-attribution-schema-extension.md`, `docs/product/02_PRD/189-source-attribution-schema-extension-2026-04-17.md`, `specs/189-source-attribution-schema-extension/` (full spec dir), `tests/scripts/fixtures/source_attribution/` (2 fixtures + .gitkeep), `tests/scripts/test_source_attribution.py`
- **Tasks**: 11/36 complete (30.5%) — T001-T011 done; T012-T036 pending
- **Test suite**: 272 pre-existing + 2 new = **274 pass** / 1 pre-existing skip (mermaid-agentic-app, unrelated to F-A2)
- **GitHub Issue**: moved to `stage:build` at session start

---

## Next Actions

### Immediate: Resume with Wave 4.1 — US2 Parser Round-Trip + SC-2 Byte-Identity Gate

**Tasks in order**:
1. **T012** `[P]` Author `tests/scripts/fixtures/source_attribution/valid_absent.md` (no findings carry attribution; no Section 9 block).
2. **T013** `[P]` Author `tests/scripts/fixtures/source_attribution/valid_empty_array.md` (one finding with `source_attribution: []` explicitly).
3. **T014** Test `test_absent_omits_key` — assert no `source_attribution` key on any returned finding.
4. **T015** Test `test_empty_array_preserved` — assert `finding["source_attribution"] == []` preserved.
5. **T016** Refine `_extract_source_attribution` for V6 absent-vs-empty distinction (may already be correctly implemented — verify via T014 + T015 dual-path assertion).
6. **T017** 🔑 **SC-2 gate**: `pytest tests/scripts/test_backward_compatibility.py -v` under `SOURCE_DATE_EPOCH=1700000000`. 5/5 baselines MUST match byte-identically. Spec constraint C1 treats regression as BLOCKER.

**Checkpoint 4** — SC-002 byte-identity gate green; MVP slice (US1 + US2) ready.

### Then: Wave 5.1 — US3 Closed-Enum + Referential Integrity (T018-T028)

Hand-author 3 invalid fixtures (bad taxonomy, bad relationship, bad id). Add 5 test functions (T021-T025). Implement `validate_source_attribution` helper (T027) with per-invocation cache. Add V1/V2/V3 parser-tier enum validation (T026). T028: determinism audit (no HTTP, no env, no timestamps, no module-level state).

**Checkpoint 5** — Two-tier validation functional.

### Then: Interim Checkpoint 5.5 (team-lead concern #4)

`pytest tests/scripts/ -v` full suite gate BEFORE T031 ADR Proposed→Accepted flip. Catches any regression introduced by Wave 4/5 work.

### Then: Wave 6.1 — Polish + PR (T029-T035)

- T029 `[P]` README.md Recent Changes line + link to ADR-028.
- T030 `[P]` `docs/architecture/00_Tech_Stack/README.md` schema-evolution timeline entry.
- T031 ADR-028 Status: Proposed → Accepted (provisional merge date + SHA placeholder).
- T032 SC audit grep: SC-001 (schema 1.5) + SC-006 (empty dep diffs) + SC-007 (22-file zero-edit). Save to `.aod/results/sc-audit.md`.
- T033 `[P]` Quickstart walk-through validation → `.aod/results/quickstart-validation.md`.
- T034 Full pytest final gate.
- T035 PR submission.

**Checkpoint 6** — PR merged.

### Post-Merge

- **T036** ADR-028 post-merge SHA fill (single-line commit `docs(adr): ADR-028 post-merge SHA fill`).

---

## Key Decisions Already Locked

From ADR-028 Proposed body (architect-authority, signed off):

| Decision | Resolution |
|----------|-----------|
| Q1 Serialization surface | **Q1-E**: conditional `## 9. Source Attribution` YAML block in `threats.md`, gated by `has-source-attribution` boolean. Q1-B (sidecar) is documented fallback for F-A3 if needed. |
| Q2 Referential integrity phase | **Q2-B**: two-tier — parser-tier enum (V1/V2/V3/V5) inline; referential integrity (V4) in separate `validate_source_attribution` helper invoked by orchestrator Phase 4. |
| Q3 ADR number | **ADR-028** (mechanical) |
| Schema version | `"1.4"` → `"1.5"` (minor bump per ADR-026 Complex-Shape Addition Clarifier extension) |
| taxonomy enum | Closed 5-value: `{owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe}` (external-framework subset of F-A1's 7-value enum; internal `tachi-control-category` / `tachi-stride-ai-category` DELIBERATELY EXCLUDED) |
| relationship enum | Closed 3-value: `{primary, related, derived}`, default `primary` |
| Conditional-key semantic | Per Feature 104 `delta_status`: absent-input → absent-key; `[]`-input → `[]`-output (V6 invariant) |
| 22-file zero-edit scope | Preserved per ADR-023 / FR-015 |

---

## Context Files to Reload Next Session

**Must-read on resume**:
- `specs/189-source-attribution-schema-extension/tasks.md` — current task state with `[X]` markers
- `specs/189-source-attribution-schema-extension/agent-assignments.md` — wave breakdown + team-lead concerns encoded
- `specs/189-source-attribution-schema-extension/spec.md` — FR/SC/AC mapping
- `docs/architecture/02_ADRs/ADR-028-source-attribution-schema-extension.md` — Q1/Q2/Q3 decisions (Proposed; flip to Accepted at T031)

**Working-tree changes in this session** (not yet committed):
- `schemas/finding.yaml` (schema 1.5 + new field)
- `scripts/tachi_parsers.py` (new helpers + inject point)
- `tests/scripts/fixtures/source_attribution/valid_multi_record.md`
- `tests/scripts/fixtures/source_attribution/valid_single_record.md`
- `tests/scripts/test_source_attribution.py`
- `docs/architecture/02_ADRs/ADR-028-source-attribution-schema-extension.md`

---

## Resume Command

```bash
claude "Resume Feature 189 F-A2 source-attribution implementation (branch: 189-source-attribution-schema-extension). Waves 1.1, 2.1, 3.1 complete (11/36 tasks). P0 architect checkpoint APPROVED. Run /aod.build to continue with Wave 4.1 (US2 absent-vs-empty + SC-2 baseline gate at T017) → Wave 5.1 (US3 enum + validator) → Checkpoint 5.5 pytest gate → Wave 6.1 (ADR Accepted + docs + PR) → post-merge T036."
```

---

## Notes

- **No commits made this session**. All Wave 1-3 deliverables live in the working tree unstaged. Before running Wave 4.1, the user should decide whether to commit Waves 1-3 as one logical group (recommended per Constitution Principle IX) or continue accumulating.
- **Test command**: `python3 -m pytest tests/scripts/ -q` (python, not python3, isn't available on this system).
- **SC-2 command**: `SOURCE_DATE_EPOCH=1700000000 python3 -m pytest tests/scripts/test_backward_compatibility.py -v` (for T017).
