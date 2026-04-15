# Agent Assignments: Feature 143 — MAESTRO Phase 4: OWASP AIVSS Evaluation ADR

**Feature Branch**: `143-maestro-aivss-evaluation-adr`
**Tasks Source**: [tasks.md](tasks.md) (33 tasks, triple-sign-off APPROVED)
**Scope**: Documentation-only ADR spike — zero production code changes
**Target Wall-Clock**: 4.5 to 7 hours (single working day with margin)
**Structure**: Two waves per PRD Milestone table (Wave 1 research, Wave 2 authorship) + polish + verification + PR waves

---

## 1. Agent Assignment Matrix

All agent names below are drawn **verbatim** from `.claude/agents/_README.md` (Agent Registry v2.0.0, confirmed 2026-04-15). No generic labels, no invented agents.

| Task | Phase | Story | Agent | Rationale |
|------|-------|-------|-------|-----------|
| T001 | 1 Setup | — | senior-backend-engineer | Light context re-read (research.md + plan.md); markdown-adjacent prep, no code. Scoped to setup only. |
| T002 | 1 Setup | — | senior-backend-engineer | Branch verification via `git branch --show-current`; trivial shell. Continues the setup bundle with T001. |
| T003 | 2 Wave 1 | — | web-researcher | External source discovery at `aivss.owasp.org`; reachability + version lookup. Timebox 2h enforced. |
| T004 | 2 Wave 1 | — | web-researcher | End-to-end read of AIVSS specification; captures the four comparison axes. External-source expertise. |
| T005 | 2 Wave 1 | — | web-researcher | Cross-reads tachi's internal schema + references (risk-scoring.yaml, severity-bands-shared.md, scoring-dimensions.md) — same researcher preserves mental model continuity with T004. |
| T006 | 3 US1 MVP | US1 | architect | ADR-024 skeleton + frontmatter; ADR authorship is architect-canonical work per Registry. |
| T007 | 3 US1 MVP | US1 | architect | ADR-024 Decision section prose. Single writer preserves voice. |
| T008 | 3 US1 MVP | US1 | architect | SKILL.md `## AIVSS Relationship` section (80-200 words). Architect owns the decision-bearing surface to guarantee token equality with ADR. |
| T009 | 3 US1 MVP | US1 | architect | Decision-noun **equality** grep assertion (MED-1 tightened). Architect authored both files — fastest self-check. |
| T010 | 4 US2 | US2 | architect | ADR-024 Context Surface A (Dimension Set) table. |
| T011 | 4 US2 | US2 | architect | ADR-024 Context Surface B (Composite Formula Weights). |
| T012 | 4 US2 | US2 | architect | ADR-024 Context Surface C (Severity Band Thresholds). |
| T013 | 4 US2 | US2 | architect | Conditional Rationale worked examples (if Decision == diverge). Same writer. |
| T014 | 5 US3 | US3 | architect | Alternatives Considered — Option A (Adopt as Primary). |
| T015 | 5 US3 | US3 | architect | Alternatives Considered — Option B (Adopt as Supplementary). |
| T016 | 5 US3 | US3 | architect | Alternatives Considered — Option C (Document Divergence). |
| T017 | 5 US3 | US3 | architect | Consequences + When to Re-Evaluate sections. |
| T018 | 5 US3 | US3 | architect | Status: Accepted frontmatter enforcement (PM concern C2 — first of two checkpoints). |
| T019 | 6 US4 | US4 | architect | Surface A row audit (no TBD/unclear). |
| T020 | 6 US4 | US4 | architect | CVSS 3.1 vs 4.0 Conflict row enforcement (MED-1 Conflict labeling). |
| T021 | 6 US4 | US4 | architect | Renderer-independent HTML anchor `<a id="surface-a"></a>` (MED-2 explicit anchor). Preview in 2+ renderers. |
| T022 | 7 Issue | — | product-manager | Decision-branch read → routes to T023 XOR T024. Issue filing is product-scoping work. |
| T023 | 7 Issue | — | product-manager | **Conditional (Option A or B only)**: file follow-on Issue via `create-issue.sh` with `stage:discover` label + 3-5 surfaces + option-specific effort estimate. Mutually exclusive with T024. |
| T024 | 7 Issue | — | product-manager | **Conditional (Option C only)**: record "no follow-on Issue filed" in PR description + cite re-evaluation trigger. Mutually exclusive with T023. |
| T025 | 8 Verify | — | code-reviewer | `git diff` zero-drift assertion across 4 directories (schemas/, scripts/, .claude/agents/, examples/). Must be empty. |
| T026 | 8 Verify | — | code-reviewer | Status: Accepted grep (returns exactly 1). Second PM concern C2 checkpoint. |
| T027 | 8 Verify | — | code-reviewer | ADR-024 reference grep in SKILL.md (returns >= 1). |
| T028 | 8 Verify | — | code-reviewer | SKILL.md AIVSS Relationship word count 80-200 (pinned awk command per LOW-1). |
| T029 | 8 Verify | — | code-reviewer | Related ADRs list verification (ADR-020, ADR-019, ADR-018 all present). |
| T030 | 8 Verify | — | code-reviewer | Backward-compat test suite (`SOURCE_DATE_EPOCH=1700000000 pytest test_backward_compatibility.py`). All 5 baselines byte-identical. |
| T031 | 8 Verify | — | code-reviewer | Runtime-dependency diff (pyproject.toml, requirements*.txt, package.json). Must be empty. |
| T032 | 8 Verify | — | architect | Open PR with `docs(143):` conventional commit title. Same author as the content — preserves voice and ownership. |
| T033 | 8 Verify | — | architect | PR final review — APPROVED verdict = "Accepted at merge" attestation. LOW-3 contingency: revert to Status: Proposed if rejected. |

**Total tasks**: 33 (T023 **XOR** T024 — effective execution count is 32).

**Agent load distribution**:
- **architect**: 21 tasks (T006-T021, T032, T033) — heaviest load; ADR is architect-canonical work
- **code-reviewer**: 7 tasks (T025-T031) — all verification gates
- **web-researcher**: 3 tasks (T003-T005) — AIVSS research wave
- **product-manager**: 3 tasks (T022, T023 or T024) — conditional Issue logic (2 effective)
- **senior-backend-engineer**: 2 tasks (T001-T002) — setup only; no backend code changes in this feature

No agent exceeds 80% utilization (architect is ~64% of tasks but all within a single working day).

---

## 2. Parallel Execution Waves

### Wave 0: Setup — senior-backend-engineer

- **Tasks**: T001, T002 (sequential)
- **Agent**: senior-backend-engineer
- **Parallelism**: Sequential — T001 before T002
- **Output**: Confirmed feature branch + loaded context from research.md and plan.md

### Wave 1: AIVSS Research — web-researcher (BLOCKS Wave 2)

- **Tasks**: T003 → T004 → T005 (strictly sequential, single agent)
- **Agent**: web-researcher
- **Parallelism**: Sequential — researcher builds mental model incrementally (home → spec → tachi cross-read)
- **Timebox**: T003 hard 2-hour cap with PM escalation on miss (per PRD Risk R1)
- **Output channel**: Append to `specs/143-maestro-aivss-evaluation-adr/research.md` under `## Wave 1 AIVSS Spec Notes` (per LOW-2)
- **Blocking**: Wave 2 cannot start until Phase 2 checkpoint clears

### Wave 2A: US1 MVP — architect (MVP stop-and-validate point)

- **Tasks**: T006 → T007 → T008 → T009 (sequential within writer)
- **Agent**: architect
- **Parallelism**: Sequential — frontmatter (T006) before Decision (T007) before SKILL.md cross-ref (T008) before equality check (T009)
- **MVP boundary**: End of Wave 2A is the **MVP stop-and-validate point**. If nothing else ships, US1 alone delivers primary product value (CISO alignment answer).

### Wave 2B: US2 Context — architect (write-serialized)

- **Tasks**: T010, T011, T012 (can be drafted in parallel editors, writes serialized), T013 (conditional on Decision = diverge)
- **Agent**: architect
- **Parallelism**: Same writer, same file — serialize writes via patch-style edits. Content drafting in parallel editors is acceptable if single writer.
- **Conditional**: T013 runs only if Decision is Option C (diverge). If Option A or B, T013 is skipped and Rationale focuses on five-criteria justification per tasks.md note.

### Wave 2C: US3 Alternatives + Consequences — architect (write-serialized)

- **Tasks**: T014, T015, T016 (Options A/B/C — parallelizable drafts, serialized writes), T017 (Consequences), T018 (Status: Accepted enforcement)
- **Agent**: architect
- **Parallelism**: Same writer, same file — serialize writes. Options A/B/C drafted in parallel editors acceptable.
- **Gate**: T018 closes PM concern C2 (first of two enforcement checkpoints).

### Wave 2D: US4 Polish — architect (sequential refinements)

- **Tasks**: T019 → T020 → T021 (sequential refinements to Surface A)
- **Agent**: architect
- **Parallelism**: Sequential — audit (T019) before CVSS-Conflict labeling (T020) before anchor insertion (T021)
- **Anchor verification**: T021 requires preview in **2+ renderers** (GitHub + VS Code / pandoc / Docusaurus)

### Wave 3: Conditional Follow-on Issue — product-manager

- **Tasks**: T022 (decision read) → **T023 XOR T024** (mutually exclusive)
- **Agent**: product-manager
- **Parallelism**: None — strict exclusive-or branch
- **Logic**:
  - Decision = Option A or B → execute T023, skip T024
  - Decision = Option C → execute T024, skip T023
- **Gate**: Issue exists **iff** decision is A or B; conditionality respected per FR-007

### Wave 4: Parallel Verification Gates — code-reviewer

- **Tasks**: T025, T026, T027, T028, T029, T030, T031 (all [P] — fully parallel)
- **Agent**: code-reviewer
- **Parallelism**: **All 7 gates dispatch in parallel** — each reads different files, emits independent pass/fail signals
- **Gate commands**:
  1. T025: `git diff main..HEAD -- schemas/ scripts/ .claude/agents/ examples/` (must be empty)
  2. T026: `grep -c '^\*\*Status\*\*: Accepted' ADR-024-*.md` (must = 1)
  3. T027: `grep -c 'ADR-024' SKILL.md` (must >= 1)
  4. T028: Pinned awk word-count (must be 80-200)
  5. T029: Related ADRs grep includes ADR-020, ADR-019, ADR-018
  6. T030: `SOURCE_DATE_EPOCH=1700000000 pytest test_backward_compatibility.py` (all 5 baselines byte-identical)
  7. T031: `git diff main..HEAD -- pyproject.toml requirements*.txt package.json` (must be empty)

### Wave 5: PR + Architect Attestation — architect

- **Tasks**: T032 → T033 (sequential)
- **Agent**: architect
- **Parallelism**: Sequential — PR must be open before final review can issue APPROVED verdict
- **Attestation**: T033 APPROVED = "Accepted at merge" (closes PRD Open Question)
- **Contingency (LOW-3)**: If PR rejected, revert ADR-024 Status to `Proposed` before revision; restore to `Accepted` only on next APPROVED verdict

---

## 3. Quality Gates Between Waves

Each wave has a concrete completion criterion that must pass before the next wave starts. Gates are not advisory — failure halts progression.

### Wave 0 Gate

- [ ] `git branch --show-current` returns `143-maestro-aivss-evaluation-adr`
- [ ] research.md and plan.md have been re-read; Wave 1 / Wave 2 split and three-surface requirement are internalized

### Wave 1 Gate — AIVSS Research Complete (blocks Wave 2)

- [ ] `## Wave 1 AIVSS Spec Notes` section exists in research.md
- [ ] All four comparison axes are documented: (a) dimension list (10 AARFs expected), (b) composite formula (`((CVSS_Base_Score + AARS) / 2) × ThM` expected), (c) severity band thresholds (or explicit "none defined" if absent at observed version), (d) CVSS base version (v4.0 expected)
- [ ] Exact AIVSS version string captured (v0.8 expected per research.md but implementer confirms from `aivss.owasp.org`)
- [ ] Canonical URL captured
- [ ] 2-hour timebox **not exceeded** on T003 (PM escalation if exceeded)

### Wave 2A Gate — CISO Reader Test (MVP delivered)

- [ ] ADR-024 exists at `docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md` with frontmatter
- [ ] `**Status**: Accepted` (literal) — not `Proposed`
- [ ] Related ADRs frontmatter lists ADR-020, ADR-019, ADR-018
- [ ] Decision section is a single paragraph that names the chosen option (Adopt primary / Adopt supplementary / Diverge) and answers the alignment question in plain language
- [ ] SKILL.md `## AIVSS Relationship` section placed between `## Domain Overview` and `## Baseline-Aware Scoring Rules`
- [ ] Reader opens ADR-024 + SKILL.md **only** and can answer "does tachi align with AIVSS?" in under five minutes without reading any other file
- [ ] **MVP validation point**: if only Wave 2A ships, US1 still delivers primary product value

### Wave 2B Gate — Compliance Reader Test (three surfaces labeled)

- [ ] ADR-024 Context section contains three distinct, labeled subsections: Surface A (Dimension Set), Surface B (Composite Formula Weights), Surface C (Severity Band Thresholds)
- [ ] Every Surface A row is annotated with **exactly one** of: `Overlap`, `Gap`, `Conflict`, `No equivalent`
- [ ] No "TBD", "unclear", or empty cells remain
- [ ] Surface B includes tachi formula (`0.35 × CVSS + 0.30 × Exploitability + 0.20 × Reachability + 0.15 × Scalability`) vs AIVSS formula (`((CVSS_Base_Score + AARS) / 2) × ThM`) with a one-line structural-difference annotation
- [ ] Surface C includes tachi bands (Critical ≥ 9.0 / High 7.0-8.9 / Medium 4.0-6.9 / Low < 4.0) vs AIVSS bands (or explicit "no AIVSS severity bands defined in v{observed}")
- [ ] If Decision == diverge: T013 produces ≥ 2 concrete worked examples with numerically-quantified tachi-vs-AIVSS score differences

### Wave 2C Gate — Maintainer Reader Test (≥3 options + Status: Accepted)

- [ ] Alternatives Considered section enumerates **at least three** options: Option A (Adopt as Primary), Option B (Adopt as Supplementary), Option C (Document Divergence)
- [ ] Each option has: Pros, Cons, Effort (S/M/L with rough day range), Compliance Value for Regulated Adopters, "Why Not Chosen" / "Why Chosen" rationale
- [ ] Consequences section distinguishes follow-on implementation (Option A/B) vs no-further-action (Option C)
- [ ] When to Re-Evaluate trigger is concrete: "AIVSS publishes stable v1.0 with at least one external adopter case study"
- [ ] T018: `grep -c '^\*\*Status\*\*: Accepted' ADR-024-*.md` returns exactly `1` (first PM C2 checkpoint)

### Wave 2D Gate — Security Engineer Anchor Test

- [ ] Every Surface A Relationship cell contains exactly one of `Overlap`, `Gap`, `Conflict`, `No equivalent` — zero TBD/unclear
- [ ] CVSS row in Surface A is labeled `Conflict` with Note cell citing CVSS version gap (tachi 3.1 vs AIVSS v{observed} on v4.0)
- [ ] `<a id="surface-a"></a>` HTML anchor present immediately above the Surface A heading
- [ ] Anchor resolves in **2+ Markdown renderers** (GitHub preview + VS Code / pandoc / Docusaurus)

### Wave 3 Gate — Exclusive-Or Conditionality

- [ ] Decision from ADR-024 is read and logged
- [ ] **Exactly one** of T023 or T024 was executed — never both, never neither
  - If Decision == Option A or B: T023 executed, GitHub Issue exists with `stage:discover` label, 3-5 surfaces, option-specific effort estimate copied verbatim from ADR Alternatives Considered, Issue number written back into ADR-024 Consequences section
  - If Decision == Option C: T024 executed, PR description records "Decision: Option C (diverge). No follow-on implementation Issue filed per FR-007 conditionality.", ADR Consequences cites re-evaluation trigger instead
- [ ] Conditionality invariant verified: Issue exists **iff** Decision is A or B

### Wave 4 Gate — Zero-Drift Verification (all 7 commands pass)

All 7 verification commands must pass. Any failure halts PR.

- [ ] T025 passes: `git diff main..HEAD -- schemas/ scripts/ .claude/agents/ examples/` is empty (FR-008, SC-006)
- [ ] T026 passes: `grep -c '^\*\*Status\*\*: Accepted' ADR-024-*.md` returns exactly `1` (SC-002, second PM C2 checkpoint)
- [ ] T027 passes: `grep -c 'ADR-024' SKILL.md` returns >= 1 (SC-005)
- [ ] T028 passes: AIVSS Relationship section word count between 80 and 200 (SC-005, pinned awk per LOW-1)
- [ ] T029 passes: ADR-020, ADR-019, ADR-018 all present in Related ADRs (SC-009)
- [ ] T030 passes: Backward-compat suite byte-identical under `SOURCE_DATE_EPOCH=1700000000` (5/5 baseline PDFs) — trivially satisfied (no pipeline inputs change)
- [ ] T031 passes: No new runtime dependencies in pyproject.toml / requirements*.txt / package.json

### Wave 5 Gate — "Accepted at Merge" Attestation

- [ ] PR opened with title `docs(143): MAESTRO Phase 4 — OWASP AIVSS evaluation ADR` (conventional commit `docs:` per Constitution IX)
- [ ] PR body includes: (a) link to ADR-024, (b) 2-3 bullet summary of three-surface comparison, (c) recommended option, (d) T025 zero-drift output as evidence, (e) Issue number from T023 (or "no follow-on Issue filed — Option C" if T024 path)
- [ ] Architect PR review returns **APPROVED** — serves as "Accepted at merge" attestation
- [ ] ADR-024 Date field updated to actual merge date before squash-merge
- [ ] **Contingency honored**: if PR rejected, Status reverted to `Proposed` before rework; restored to `Accepted` only after next APPROVED verdict

---

## 4. Time Estimates Per Wave

Aggregate target: **≤ 7 hours wall-clock**, aligning with PRD Milestone table and Team-Lead sign-off ("4.5-7h wall-clock fits 1-day cycle with margin").

| Wave | Tasks | Agent | Wall-Clock Estimate | Running Total | Notes |
|------|-------|-------|---------------------|---------------|-------|
| **Wave 0: Setup** | T001-T002 | senior-backend-engineer | 10 min | 0:10 | Trivial context re-read + branch check |
| **Wave 1: AIVSS Research** | T003-T005 | web-researcher | **≤ 2h (hard cap)** | 2:10 | T003 timebox is absolute; if AIVSS not located → PM escalation → halt. T004+T005 fit inside the 2h window on success path. |
| **Wave 2A: US1 MVP** | T006-T009 | architect | 45 min | 2:55 | Frontmatter + Decision paragraph + SKILL.md section + equality grep. **MVP stop-and-validate point.** |
| **Wave 2B: US2 Context** | T010-T013 | architect | 60 min | 3:55 | Three surfaces + conditional worked examples (T013 skippable if Decision != diverge → ~45 min on adopt path) |
| **Wave 2C: US3 Alternatives** | T014-T018 | architect | 75 min | 5:10 | Three options (Pros/Cons/Effort/Compliance/Rationale each) + Consequences + Status enforcement |
| **Wave 2D: US4 Polish** | T019-T021 | architect | 30 min | 5:40 | Surface A audit + CVSS-Conflict labeling + HTML anchor + 2-renderer preview |
| **Wave 3: Conditional Issue** | T022, T023 XOR T024 | product-manager | 20 min | 6:00 | Issue filing (Option A/B) or PR-description note (Option C). T023 path is the upper bound. |
| **Wave 4: Verification Gates** | T025-T031 (parallel) | code-reviewer | 15 min (parallel dispatch) | 6:15 | All 7 gates dispatch in parallel; wall-clock is longest single gate (T030 backward-compat suite, ~5-10 min) |
| **Wave 5: PR + Attestation** | T032-T033 | architect | 30 min | **6:45** | PR open + body + architect final review |

**Total**: ~6h 45min on the upper (diverge-path-with-worked-examples) bound, well inside the 7h ceiling. Lower bound ~4.5h on an Option B path where T013 is skipped and Wave 1 clears in 90 minutes.

**Margin accommodations**:
- Wave 1 timebox of 2h is **hard**, not a sliding estimate. If breached, halt for PM escalation per PRD Risk R1.
- If Decision = Option A or B, T013 is skipped (~-15 min) and T023 adds ~15 min (~net zero)
- If Decision = Option C, T013 adds ~15 min and T024 is trivial (~+10 min)
- Wave 4 parallel dispatch is critical — sequential execution of all 7 gates would add 30-45 minutes
- Architect authoring continuity (Waves 2A-2D + 5) preserves voice; splitting across multiple writers would introduce revision overhead not accounted for here

---

## Sign-off

**Team-Lead Sign-off**: APPROVED

- All 33 tasks mapped to exact Agent Registry names (zero generic labels, zero invented agents)
- Agent load balanced: no agent exceeds 80% utilization in single-day cycle
- Two-wave structure per PRD Milestone table preserved
- Conditional exclusive-or logic (T023 XOR T024) explicitly encoded
- Phase 8 parallel-dispatch model validated (7 independent gates)
- 4.5-7h wall-clock total aligns with PRD feasibility envelope
- MVP stop-and-validate point at end of Wave 2A preserves CISO primary product value
- Contingency clauses from architect sign-off (MED-1, MED-2, LOW-1, LOW-2, LOW-3) all surfaced in gate checklists

**Date**: 2026-04-15
**Agent**: team-lead
