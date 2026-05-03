# Agent Assignments: Feature 144 — NIST AI RMF Integration Evaluation ADR

**Feature Branch**: `144-nist-ai-rmf-evaluation-adr`
**Tasks Source**: [tasks.md](tasks.md) (44 tasks across 9 phases, triple-sign-off completed 2026-04-15)
**Scope**: Documentation-only ADR spike — zero production code changes (MAESTRO Companion, regulated-adopter half)
**Target Wall-Clock**: 9-11 hours (~3h Wave 1 + 5-7h Wave 2 + 1h verification + PR cycle) — fits 1-day spike budget with margin
**Structure**: Two-wave authorship per PRD Milestone table (Wave 1 research, Wave 2 architect authorship) decomposed into 10 execution waves for governance + parallelization

---

## 1. Agent Assignment Matrix

All agent names below are drawn **verbatim** from `.claude/agents/_README.md` (Agent Registry v2.0.0, confirmed 2026-04-15). No generic labels, no invented agents. Assignments align with PRD line 476 Agent Assignment Rationale and plan.md Wave 1 / Wave 2 split.

| Task | Phase | Story | Agent | Rationale |
|------|-------|-------|-------|-----------|
| T001 | 1 Setup | — | senior-backend-engineer | Light context re-read (research.md + plan.md + quickstart.md) — markdown-adjacent prep, no code. Scoped to setup only; fallback writer per Registry. |
| T002 | 1 Setup | — | senior-backend-engineer | Branch verification via `git branch --show-current`; trivial shell. Continues the setup bundle with T001. |
| T003 | 2 Wave 1 | — | web-researcher | External source discovery at NIST canonical home; reachability + version lookup. **3-hour timebox enforced combined T003+T004+T005+T006.** |
| T004 | 2 Wave 1 | — | web-researcher | End-to-end read of AI RMF 1.0 (NIST.AI.100-1.pdf); captures Functions + Categories + Subcategories. External-source expertise. |
| T005 | 2 Wave 1 | — | web-researcher | End-to-end read of NIST AI 600-1 GAI Profile (NIST.AI.600-1.pdf); captures 12 GAI risks. Same researcher preserves mental model continuity with T004. |
| T006 | 2 Wave 1 | — | web-researcher | Cross-reads tachi's internal references (control-categories.md, stride-categories-shared.md, pipeline phase doc). Confirms SC-006 baseline. Closes Wave 1. |
| T007 | 3 US1 MVP | US1 | architect | ADR-025 skeleton + frontmatter with 6-ADR cross-reference line; ADR authorship is architect-canonical work per Registry. |
| T008 | 3 US1 MVP | US1 | architect | ADR-025 Context prose (NIST AI RMF + AI 600-1 summary + tachi recap). Single writer preserves voice. |
| T009 | 3 US1 MVP | US1 | architect | Surface A table (Functions × pipeline phases) with `<a id="surface-a"></a>` anchor. Same writer. |
| T010 | 3 US1 MVP | US1 | architect | Surface B table (Subcategories × control categories) with `<a id="surface-b"></a>` anchor. Same writer. |
| T011 | 3 US1 MVP | US1 | architect | Surface C table (GAI risks × STRIDE+AI categories) with `<a id="surface-c"></a>` anchor. Includes architect scope-reduction authority per Edge Case 3. Same writer. |
| T012 | 3 US1 MVP | US1 | architect | Row-label audit across Surfaces A/B/C (SC-004 gate: Overlap/Gap/Conflict/"No equivalent" only, no TBD/unclear). Audit authority is architect per ADR voice. |
| T013 | 3 US1 MVP | US1 | architect | **Decision section — canonical decision-noun chosen**. Per spec Assumption "pre-1.0 maturity does not auto-default to diverge"; reasoned afresh from FR-002 + five criteria. This task is the single source of truth for all downstream noun references (SC-007). |
| T014 | 4 US2 | US2 | architect | SKILL.md `## NIST AI RMF Relationship` section (80-200 words, decision-noun byte-identical to T013). Architect owns the decision-bearing surface to guarantee byte equality with ADR. |
| T015 | 4 US2 | US2 | architect | Decision-noun **byte-equality + non-empty guard** assertion (SC-007 with `[ -n "$ADR_NOUN" ]` guard per architect plan review C2 MEDIUM). Architect authored both files — fastest self-check. |
| T016 | 5 US3 | US3 | architect | Create `nist-ai-rmf-mapping.md` (content shape conditional on T013 decision-noun: full mapping for A, relationship stub for B/C). Architect consumes T013 decision directly. |
| T017 | 5 US3 | US3 | architect | Verify mapping reference exists + contains relative-path link to ADR-025 (SC-008). Continues architect's mapping-reference ownership. |
| T018 | 6 US4 | US4 | architect | ADR-025 Rationale section (five-criteria justification + ADR-024 comparison + sector-specific compliance refs). Same writer. |
| T019 | 6 US4 | US4 | architect | Alternatives Considered — Option A (Documentation-only mapping). Full Pros/Cons/Effort (S)/Compliance Value/Determinism Impact/Why-Chosen\|Why-Not-Chosen. |
| T020 | 6 US4 | US4 | architect | Alternatives Considered — Option B (Shallow wired integration). Effort estimate (M) must be crisp — downstream T027 copies verbatim. |
| T021 | 6 US4 | US4 | architect | Alternatives Considered — Option C (Deep wired integration). Effort estimate (L) must be crisp — downstream T027 copies verbatim. Hybrid B+C permitted per FR-003. |
| T022 | 6 US4 | US4 | architect | Consequences + When to Re-Evaluate + References sections. Triggers: "≥3 regulated adopter inquiries" OR "AI RMF 2.0" OR "SP 800-53 AI overlay GA". |
| T023 | 6 US4 | US4 | architect | ADR-024 back-reference single-line edit (append ADR-025 to Related ADRs line). Single-line edit; architect retains authorship continuity. Closes bidirectional cross-reference per spec Closed-at-Approval Q4. |
| T024 | 7 US5 | US5 | code-reviewer | `git diff main..HEAD -- schemas/ scripts/ .claude/agents/ examples/` zero-drift assertion (SC-006). Must be empty. Verification domain owned by code-reviewer. |
| T025 | 7 US5 | US5 | code-reviewer | Backward-compat pytest (`SOURCE_DATE_EPOCH=1700000000 pytest test_backward_compatibility.py`). All 5 baselines byte-identical (SC-010). Verification domain. |
| T026 | 8 Issue | — | product-manager | Decision-branch read from ADR-025 Decision section → routes to T027 XOR T028. Issue filing is product-scoping work per Registry. |
| T027 | 8 Issue | — | product-manager | **Conditional (Option B/C/hybrid only)**: file follow-on Issue via `create-issue.sh` with `stage:discover` label + 3-5 surfaces + option-specific effort estimate copied **verbatim** from ADR-025 Alternatives (architect plan review C1 MEDIUM dependency). Mutually exclusive with T028. |
| T028 | 8 Issue | — | product-manager | **Conditional (Option A only)**: record "no follow-on Issue filed — Option A (docs-only)" in PR description + cite `nist-ai-rmf-mapping.md` maintenance commitment + When-to-Re-Evaluate trigger. Mutually exclusive with T027. |
| T029 | 9 Verify | — | code-reviewer | SC-001 file-exists check (ADR-025 at canonical path). `[ -f ... ] && echo "SC-001 PASS"`. |
| T030 | 9 Verify | — | code-reviewer | SC-002 `**Status**: Accepted` grep (must return exactly 1). Update `**Date**` placeholder to actual merge date before squash. |
| T031 | 9 Verify | — | code-reviewer | SC-003 three Surface anchor grep (must return exactly 3). |
| T032 | 9 Verify | — | code-reviewer | SC-004 manual row-label inspection across Surfaces A/B/C (re-run T012 audit on any ambiguous cell). |
| T033 | 9 Verify | — | code-reviewer | SC-005 SKILL.md section word count (pinned awk + `wc -w`, range [80, 200]). |
| T034 | 9 Verify | — | code-reviewer | SC-006 re-run zero-drift git diff (same as T024). |
| T035 | 9 Verify | — | code-reviewer | SC-007 re-run decision-noun byte-equality with `[ -n ... ]` non-empty guard (same as T015). |
| T036 | 9 Verify | — | code-reviewer | SC-008 re-run mapping-reference existence + relative-link check (same as T017). |
| T037 | 9 Verify | — | code-reviewer | SC-009 conditional follow-on Issue check: `gh issue list --label stage:discover --search "ADR-025"` returns ≥1 for B/C/hybrid OR N/A for A. |
| T038 | 9 Verify | — | code-reviewer | SC-010 re-run backward-compat pytest (same as T025). |
| T039 | 9 Verify | — | code-reviewer | SC-011 ADR-024 back-reference grep (`grep -cE 'ADR-025' ADR-024-*.md` returns ≥1). |
| T040 | 9 Verify | — | code-reviewer | SC-012 `docs:` conventional commit prefix check (`git log main..144-... --pretty=%s \| grep -vE '^docs(\(.+\))?:'` must be empty). |
| T041 | 9 Verify | — | code-reviewer | SC-013 record Wave 1 timebox outcome in PR description (within-budget or contingency-chosen note). |
| T042 | 9 Verify | — | code-reviewer | No-new-dependencies diff (`pyproject.toml`, `requirements-dev.txt`, `package.json`). Must be empty. |
| T043 | 9 Verify | — | architect | Open PR with title `docs(144): MAESTRO Companion — NIST AI RMF evaluation ADR`. Same author as content preserves voice and ownership continuity through final review. |
| T044 | 9 Verify | — | architect | PR final review — APPROVED verdict serves as "Accepted at merge" attestation (closed-at-approval Q2). Update `**Date**: <merge-date-placeholder>` to actual YYYY-MM-DD before squash-merge. **Contingency**: if rejected, revert ADR-025 Status to `Proposed` before rework; restore to `Accepted` only on next APPROVED. |

**Total tasks**: 44 (T027 **XOR** T028 — effective execution count is 43).

**Agent load distribution**:
- **architect**: 21 tasks (T007-T023, T043-T044) — heaviest load; ADR is architect-canonical work, voice consistency preserved through single writer
- **code-reviewer**: 16 tasks (T024-T025, T029-T042) — all US5 zero-drift + Phase 9 verification gates, 14 of which are [P]-parallelizable
- **web-researcher**: 4 tasks (T003-T006) — NIST AI RMF research wave under combined 3-hour timebox
- **product-manager**: 3 tasks (T026, T027 or T028) — conditional Issue logic (2 effective per XOR)
- **senior-backend-engineer**: 2 tasks (T001-T002) — setup only; no backend code changes in this feature

No agent exceeds 80% utilization (architect is ~48% of tasks; code-reviewer ~36%; all within a single working day).

---

## 2. Parallel Execution Waves

### Wave 1: Setup — senior-backend-engineer

- **Tasks**: T001, T002 (sequential)
- **Agent**: senior-backend-engineer
- **Parallelism**: Sequential — T001 (re-read research.md + plan.md + quickstart.md) before T002 (branch verification)
- **Output**: Confirmed feature branch `144-nist-ai-rmf-evaluation-adr` + loaded Wave 1 / Wave 2 split + three-surface requirement internalized

### Wave 2: NIST AI RMF Research — web-researcher (BLOCKS all Wave 3+ authorship)

- **Tasks**: T003 → T004 → T005 → T006 (strictly sequential, single agent)
- **Agent**: web-researcher
- **Parallelism**: Sequential — researcher builds mental model incrementally (NIST home → AI RMF 1.0 → AI 600-1 → tachi cross-read)
- **Timebox**: **3-hour HARD cap combined T003+T004+T005+T006** (per PRD Risk R1 + spec SC-013). If budget exceeded, pause and choose ONE contingency per spec Edge Case 1:
  - (a) Descope FR-002 Surface B sample from "5-10 representative Subcategories" to "3 Subcategories"
  - (b) Defer FR-007 tachi-shared artifact creation to a follow-on Issue (ship only ADR-025 + SKILL.md update in this PR)
  - (c) Escalate to PM
- **Output channel**: Append findings to `specs/144-nist-ai-rmf-evaluation-adr/research.md` under `## Wave 1 — NIST AI RMF Spec Notes` (durable audit trail for PM escalation + delivery retrospective)
- **Blocking**: Wave 3 cannot start until Phase 2 checkpoint clears

### Wave 3: US1 MVP — ADR-025 Context + Surfaces + Decision — architect (MVP stop-and-validate point)

- **Tasks**: T007 → T008 → T009 → T010 → T011 → T012 → T013 (sequential within single writer)
- **Agent**: architect
- **Parallelism**: Sequential — skeleton (T007) before Context (T008) before Surface A/B/C drafts (T009, T010, T011 — can draft in parallel editor panes but writes serialized into shared ADR-025 file) before audit (T012) before Decision (T013)
- **MVP boundary**: End of Wave 3 is the **MVP stop-and-validate point**. If nothing else ships, US1 alone delivers primary product value (compliance-officer can answer "does tachi output map to NIST AI RMF vocabulary?" from ADR-025 alone).
- **T013 is the canonical decision-noun anchor**: all downstream noun references (T014, T016, T026, T027) trace back to T013's chosen noun

### Wave 4: US2 — SKILL.md NIST AI RMF Relationship + Byte-Equality Verifier — architect

- **Tasks**: T014 → T015 (sequential)
- **Agent**: architect
- **Parallelism**: Sequential — SKILL.md authoring (T014) before byte-equality + non-empty guard check (T015)
- **Dependency**: Requires T013 Decision finalized (canonical decision-noun established)
- **Gate**: SC-007 verifier passes with `[ -n "$ADR_NOUN" ]` guard satisfied (architect plan review C2 MEDIUM)

### Wave 5: US3 — nist-ai-rmf-mapping.md Creation — architect

- **Tasks**: T016 → T017 (sequential)
- **Agent**: architect
- **Parallelism**: Sequential — file creation with conditional content shape (T016) before existence + link verification (T017)
- **Dependency**: Requires T013 Decision finalized (content shape depends on chosen option)
- **Content-shape branch**:
  - Option A → full mapping (8 control categories → NIST Subcategories + Surface C crosswalk + ADR-025 back-link)
  - Option B/C → one-paragraph relationship stub (wired-integration site + follow-on Issue forward-link + ADR-025 back-link)
- **Gate**: SC-008 passes — file exists + relative-path link to ADR-025 present

### Wave 6: US4 — Alternatives + Rationale + Consequences + ADR-024 Back-Ref — architect (write-serialized)

- **Tasks**: T018 → T019, T020, T021 (drafts parallelizable, writes serialized) → T022 → T023 (sequential)
- **Agent**: architect
- **Parallelism**: Same writer, same file — Options A/B/C drafts (T019/T020/T021) can be drafted in parallel editor panes but serialized into ADR-025 via patch-style edits. T023 is single-line edit to ADR-024.
- **Dependency**: Requires T013 Decision finalized (Rationale explicitly compares to ADR-024 logic; Alternatives Considered Options A/B/C effort estimates are finalized and verbatim-quotable by T027)
- **Architect plan review C1 MEDIUM**: T027 follow-on Issue filing explicitly depends on T018-T021 being complete before Wave 8 begins

### Wave 7: US5 — Zero-Drift + Backward-Compat Gates — code-reviewer (parallelizable)

- **Tasks**: T024, T025 (both [P] — parallelizable)
- **Agent**: code-reviewer
- **Parallelism**: **Both gates dispatch in parallel** — independent commands, independent pass/fail signals
  - T024: `git diff main..HEAD -- schemas/ scripts/ .claude/agents/ examples/` (must be empty — SC-006)
  - T025: `SOURCE_DATE_EPOCH=1700000000 pytest test_backward_compatibility.py` (5/5 byte-identical — SC-010)
- **Dependency**: Requires all Wave 2-6 content changes committed to the branch (to catch accidental drift)
- **Gate**: Zero-drift invariant preserved; unregulated-adopter Constitution III invariant protected

### Wave 8: Conditional Follow-on Issue — product-manager

- **Tasks**: T026 (decision-branch read) → **T027 XOR T028** (mutually exclusive)
- **Agent**: product-manager
- **Parallelism**: None — strict exclusive-or branch
- **Logic**:
  - Decision = Option A (`documentation-only mapping`) → execute T028, skip T027
  - Decision = Option B (`shallow wired integration`), Option C (`deep wired integration`), or `hybrid BC` → execute T027, skip T028
- **Dependency**: Requires T018-T021 finalized so effort estimate string for chosen option is verbatim-copyable (architect plan review C1 MEDIUM)
- **Gate**: SC-009 conditional pass — Issue exists **iff** Decision is B/C/hybrid; Issue absent iff Decision is A

### Wave 9: Parallel Verification Gates — code-reviewer (FULLY PARALLEL — 14 gates)

- **Tasks**: T029, T030, T031, T032, T033, T034, T035, T036, T037, T038, T039, T040, T041, T042 (all [P] — fully parallel)
- **Agent**: code-reviewer
- **Parallelism**: **All 14 gates dispatch in parallel** — each reads different files or runs independent commands, emits independent pass/fail signals. Wall-clock is longest single gate (T038 backward-compat pytest, ~5-10 min).
- **Gate commands**:
  1. T029 (SC-001): `[ -f ADR-025-*.md ] && echo "PASS"`
  2. T030 (SC-002): `grep -cE '^\*\*Status\*\*: Accepted$' ADR-025-*.md` must = 1
  3. T031 (SC-003): `grep -c '<a id="surface-[abc]"></a>' ADR-025-*.md` must = 3
  4. T032 (SC-004): manual row-label inspection (re-run T012 audit on ambiguous cells)
  5. T033 (SC-005): pinned awk + `wc -w` SKILL.md section word count in [80, 200]
  6. T034 (SC-006): re-run zero-drift git diff (same as T024)
  7. T035 (SC-007): re-run decision-noun byte-equality with `[ -n ... ]` guard (same as T015)
  8. T036 (SC-008): re-run mapping-reference existence check (same as T017)
  9. T037 (SC-009): conditional follow-on Issue check via `gh issue list`
  10. T038 (SC-010): re-run backward-compat pytest (same as T025)
  11. T039 (SC-011): `grep -cE 'ADR-025' ADR-024-*.md` must ≥ 1
  12. T040 (SC-012): `git log main..HEAD --pretty=%s \| grep -vE '^docs(\(.+\))?:'` must be empty
  13. T041 (SC-013): Wave 1 timebox outcome recorded in PR description
  14. T042: no-new-deps diff (`pyproject.toml`, `requirements-dev.txt`, `package.json`) must be empty
- **Gate**: All 14 gates PASS — feature ready for PR

### Wave 10: PR + Architect Final Review — architect

- **Tasks**: T043 → T044 (sequential)
- **Agent**: architect
- **Parallelism**: Sequential — PR must be open (T043) before final review (T044) can issue APPROVED verdict
- **Attestation**: T044 APPROVED = "Accepted at merge" (closes PRD Open Question, closed-at-approval Q2)
- **Pre-squash step**: Update `**Date**: <merge-date-placeholder>` in ADR-025 to actual YYYY-MM-DD merge date
- **Contingency**: If PR rejected, revert ADR-025 Status to `Proposed` before revision cycle; restore to `Accepted` only after next APPROVED verdict — preserves literal consistency between Status marker and actual lifecycle state

---

## 3. Quality Gates Between Waves

Each wave has a concrete completion criterion that must pass before the next wave starts. Gates are not advisory — failure halts progression.

### Wave 1 Gate — Setup Complete

- [ ] `git branch --show-current` returns `144-nist-ai-rmf-evaluation-adr`
- [ ] research.md, plan.md, and quickstart.md have been re-read; Wave 1 / Wave 2 split + three-surface comparison requirement + five-surface allow-list (SC-006) all internalized

### Wave 2 Gate — NIST AI RMF Research Complete (BLOCKS Wave 3+)

- [ ] `## Wave 1 — NIST AI RMF Spec Notes` section exists in research.md
- [ ] All three comparison axes documented: (a) NIST AI RMF Functions × tachi pipeline phases, (b) NIST Subcategories × tachi control categories (5-10 Subcategories sampled), (c) NIST AI 600-1 GAI risks × tachi STRIDE+AI categories (exactly 12 GAI risks confirmed against PRD estimate)
- [ ] Exact AI RMF version string captured (1.0 expected but implementer confirms from NIST canonical home)
- [ ] Exact NIST AI 600-1 version string + DOI captured
- [ ] Canonical URLs captured (nist.gov/itl/ai-risk-management-framework, NIST.AI.100-1.pdf, NIST.AI.600-1.pdf)
- [ ] Notes on AI RMF 2.0 or revision status captured (per spec Edge Case 2)
- [ ] tachi internal references confirmed: 8 control categories + 11 STRIDE+AI categories + 6 pipeline phases (SC-006 baseline)
- [ ] **3-hour combined timebox not exceeded** on T003+T004+T005+T006 (PM escalation + contingency choice if exceeded)

### Wave 3 Gate — US1 MVP Delivered (Compliance Officer Reader Test)

- [ ] ADR-025 exists at `docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md` with full frontmatter
- [ ] `**Status**: Accepted` (literal) — not `Proposed`
- [ ] Related ADRs frontmatter lists ADR-024, ADR-020, ADR-019, ADR-018, ADR-021, ADR-023 (minimum 6 per architect plan review)
- [ ] Context section contains three labeled Surface subsections with explicit `<a id="surface-a"></a>`, `<a id="surface-b"></a>`, `<a id="surface-c"></a>` anchor tags
- [ ] Every row in Surfaces A/B/C uses exactly one of: `Overlap`, `Gap`, `Conflict`, `No equivalent` (zero TBD/unclear/empty — SC-004)
- [ ] Decision section first paragraph contains single canonical decision-noun from allow-list `(documentation-only mapping|shallow wired integration|deep wired integration|hybrid [BC])`
- [ ] **MVP validation point**: if only Wave 3 ships, US1 still delivers primary product value (compliance officer can answer NIST AI RMF mapping question from ADR-025 alone)

### Wave 4 Gate — US2 Delivered (Security Engineer Procurement-Justification Reader Test)

- [ ] SKILL.md `## NIST AI RMF Relationship` section placed between `## Domain Overview` and `## Baseline-Aware Control Analysis Rules`
- [ ] Section is 80-200 words (awk-extracted + `wc -w` verified)
- [ ] Section contains relative-path link to ADR-025: `../../../docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md`
- [ ] Section uses exact same canonical decision-noun as ADR-025 Decision (byte-identical modulo case)
- [ ] T015 SC-007 verifier passes with `[ -n "$ADR_NOUN" ]` non-empty guard satisfied (architect plan review C2 MEDIUM)

### Wave 5 Gate — US3 Delivered (CISO Audit-Preparation Reader Test)

- [ ] `nist-ai-rmf-mapping.md` exists at `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`
- [ ] Content shape matches T013 chosen option (full mapping for A; relationship stub for B/C)
- [ ] File contains relative-path link to ADR-025 (SC-008)
- [ ] File is additive only (does NOT modify any existing tachi-shared reference per ADR-023 additive-only invariant)
- [ ] File renders in standard Markdown without GFM extensions

### Wave 6 Gate — US4 Delivered (Maintainer Decision-Traceability Reader Test)

- [ ] Alternatives Considered section enumerates **at least three** options: A (docs-only), B (shallow wired), C (deep wired) — optional hybrid B+C
- [ ] Each option has: Pros, Cons, Effort (S/M/L with day range), Compliance Value for Regulated Adopters, Pipeline Determinism Impact, Why-Chosen|Why-Not-Chosen rationale
- [ ] Rationale addresses all five evaluation criteria (maturity, adoption, compatibility, effort, compliance value) AND explicitly compares to ADR-024 reasoning
- [ ] Rationale includes sector-specific compliance-value references (SOC 2, FedRAMP, HIPAA, FFIEC, EU AI Act) per US2 AC-3
- [ ] Consequences section distinguishes follow-on implementation (B/C) vs maintenance-commitment-only (A)
- [ ] When to Re-Evaluate trigger is concrete: "≥3 regulated adopter inquiries" OR "AI RMF 2.0 publication" OR "SP 800-53 AI overlay GA"
- [ ] References section cites internal (PRD 144, ADR-024, ADR-020, ADR-019, ADR-018, ADR-021, ADR-023, pipeline phase doc, control-categories.md, stride-categories-shared.md) + external (NIST canonical URLs + DOI)
- [ ] ADR-024 Related ADRs line appended with bidirectional ADR-025 back-reference

### Wave 7 Gate — US5 Delivered (Unregulated Adopter Non-Disruption Reader Test)

- [ ] T024 passes: `git diff main..HEAD -- schemas/ scripts/ .claude/agents/ examples/` is empty (SC-006 zero-drift)
- [ ] T025 passes: `SOURCE_DATE_EPOCH=1700000000 pytest test_backward_compatibility.py` returns 5/5 byte-identical under ADR-021 determinism baseline (SC-010)

### Wave 8 Gate — Exclusive-Or Conditionality (SC-009)

- [ ] Decision from ADR-025 is read and logged
- [ ] **Exactly one** of T027 or T028 was executed — never both, never neither
  - If Decision = Option B/C/hybrid: T027 executed, GitHub Issue exists with `stage:discover` label, 3-5 surfaces, option-specific effort estimate copied verbatim from ADR Alternatives Considered, Issue number written back into ADR-025 Consequences section
  - If Decision = Option A: T028 executed, PR description records "Decision: Option A (documentation-only mapping). No follow-on implementation Issue filed per FR-008 conditionality.", ADR-025 Consequences cites `nist-ai-rmf-mapping.md` maintenance commitment + When-to-Re-Evaluate trigger
- [ ] Conditionality invariant verified: Issue exists **iff** Decision is B/C/hybrid

### Wave 9 Gate — Zero-Drift Verification (all 14 gates pass)

All 14 verification commands must pass. Any failure halts PR.

- [ ] T029 passes: ADR-025 file exists at canonical path (SC-001)
- [ ] T030 passes: `**Status**: Accepted` grep returns exactly 1 (SC-002)
- [ ] T031 passes: Three Surface anchor tags present (SC-003)
- [ ] T032 passes: All Surface rows use Overlap/Gap/Conflict/"No equivalent" only (SC-004)
- [ ] T033 passes: SKILL.md section word count in [80, 200] (SC-005)
- [ ] T034 passes: Zero-drift git diff empty on 4 forbidden directories (SC-006)
- [ ] T035 passes: Decision-noun byte-equality with non-empty guard (SC-007)
- [ ] T036 passes: `nist-ai-rmf-mapping.md` exists with relative-path link to ADR-025 (SC-008)
- [ ] T037 passes: Conditional follow-on Issue status correct per SC-009
- [ ] T038 passes: Backward-compat pytest 5/5 byte-identical under `SOURCE_DATE_EPOCH=1700000000` (SC-010)
- [ ] T039 passes: ADR-024 back-reference to ADR-025 present (SC-011)
- [ ] T040 passes: All commits use `docs:` conventional commit prefix (SC-012)
- [ ] T041 passes: Wave 1 timebox outcome recorded (SC-013)
- [ ] T042 passes: No new runtime dependencies

### Wave 10 Gate — "Accepted at Merge" Attestation

- [ ] PR opened with title `docs(144): MAESTRO Companion — NIST AI RMF evaluation ADR` (conventional commit `docs:` per Constitution IX + SC-012)
- [ ] PR body includes: (a) link to ADR-025, (b) 2-3 bullet summary of three-surface comparison (one per Surface A/B/C), (c) recommended option (decision-noun from T013), (d) T034 zero-drift output as evidence, (e) Issue number from T027 (or "no follow-on Issue filed — Option A (docs-only)" if T028 path taken), (f) T038 pytest 5/5 PASS line
- [ ] Architect PR review returns **APPROVED** — serves as "Accepted at merge" attestation
- [ ] ADR-025 `**Date**: <merge-date-placeholder>` updated to actual YYYY-MM-DD merge date before squash-merge
- [ ] **Contingency honored**: if PR rejected, Status reverted to `Proposed` before rework; restored to `Accepted` only after next APPROVED verdict

---

## 4. Time Estimates Per Wave

Aggregate target: **9-11 hours wall-clock** (fits 1-day spike budget per PRD Milestone table and team-lead sign-off note "wall-clock estimate: 3h Wave 1 + 5-7h Wave 2 + 1h verification + PR cycle"). Longer than Feature 143's 7-hour envelope due to genuine scope growth (FR-007 tachi-shared artifact, 5 user stories vs 4, SC-011/SC-012/SC-013 gates new, NIST surface = AI RMF 1.0 + NIST AI 600-1 + 12 GAI risks).

| Wave | Tasks | Agent | Wall-Clock Estimate | Running Total | Notes |
|------|-------|-------|---------------------|---------------|-------|
| **Wave 1: Setup** | T001-T002 | senior-backend-engineer | 10 min | 0:10 | Trivial context re-read + branch check |
| **Wave 2: NIST Research** | T003-T006 | web-researcher | **≤ 3h (hard cap combined)** | 3:10 | 3-hour timebox is absolute; if breached → PM escalation + 3 contingency options (descope Surface B / defer FR-007 / escalate). Success path fits inside 3h. |
| **Wave 3: US1 MVP** | T007-T013 | architect | 2h | 5:10 | Skeleton + Context + Surfaces A/B/C + audit + Decision canonical-noun. **MVP stop-and-validate point.** Larger than Feature 143's Wave 2A (~45min) because 3 Surfaces vs 3 but wider scope (Functions, Subcategories, 12 GAI risks). |
| **Wave 4: US2 SKILL.md** | T014-T015 | architect | 30 min | 5:40 | 80-200 word section + byte-equality + non-empty guard verifier |
| **Wave 5: US3 Mapping Reference** | T016-T017 | architect | 45 min | 6:25 | Conditional content shape (full mapping ~45min for Option A; stub ~15min for B/C) + SC-008 verifier. Upper bound assumed. |
| **Wave 6: US4 Alternatives + Rationale + Consequences + ADR-024 Back-Ref** | T018-T023 | architect | 90 min | 7:55 | Rationale (5 criteria + ADR-024 comparison + sector compliance) + Options A/B/C (Pros/Cons/Effort/Compliance/Determinism/Rationale each) + Consequences + When-to-Re-Evaluate + References + ADR-024 back-ref single-line edit |
| **Wave 7: US5 Zero-Drift + Backward-Compat** | T024-T025 (parallel) | code-reviewer | 15 min (parallel dispatch) | 8:10 | Both gates dispatch in parallel; wall-clock is longest single gate (T025 pytest, ~5-10 min) |
| **Wave 8: Conditional Issue** | T026, T027 XOR T028 | product-manager | 20 min | 8:30 | Issue filing (Option B/C/hybrid) or PR-description note (Option A). T027 path is the upper bound. |
| **Wave 9: Verification Gates** | T029-T042 (all parallel) | code-reviewer | 15 min (parallel dispatch) | 8:45 | All 14 gates dispatch in parallel; wall-clock is longest single gate (T038 backward-compat pytest, ~5-10 min) |
| **Wave 10: PR + Attestation** | T043-T044 | architect | 45 min | **9:30** | PR open + body assembly + architect final review. Review may include a rework cycle if CHANGES REQUESTED. |

**Total**: ~9h 30min on the upper-bound path (all Surfaces fully populated, Option A mapping produces full-mapping table, Wave 6 runs ~90 min). Lower bound ~8h on Option B/C path where mapping file is a stub (~15min) and Wave 6 effort-estimate crispness is tighter.

**Margin accommodations**:
- Wave 2 timebox of 3h is **hard**, not a sliding estimate. If breached, halt for PM escalation per PRD Risk R1 + spec Edge Case 1.
- If Decision = Option A, Wave 5 runs 45 min (full mapping) and Wave 8 T028 adds ~10 min
- If Decision = Option B/C/hybrid, Wave 5 runs 15 min (stub) and Wave 8 T027 adds ~20 min (~net +0 to +10 min)
- Wave 7 and Wave 9 parallel dispatch are critical — sequential execution of all 14 Wave 9 gates would add 60-90 minutes
- Architect authoring continuity (Waves 3-6 + 10) preserves voice; splitting across multiple writers would introduce revision overhead not accounted for here
- Surface C abbreviation (architect scope-reduction authority per Edge Case 3) can shorten Wave 3 by ~30 min if GAI × STRIDE+AI matrix proves structurally intractable within the day budget

---

## Sign-off

**Team-Lead Sign-off**: APPROVED

- All 44 tasks mapped to exact Agent Registry names (zero generic labels, zero invented agents)
- Agent load balanced: architect ~48%, code-reviewer ~36%, no agent exceeds 80% utilization in single-day cycle
- Two-wave structure per PRD Milestone table preserved (Wave 1 research → Wave 2 authorship) with 10 execution waves for governance + parallelization
- Conditional exclusive-or logic (T027 XOR T028) explicitly encoded per FR-008
- Phase 9 parallel-dispatch model validated (14 independent verification gates + 2 Wave 7 backward-compat gates)
- 9-11h wall-clock total aligns with PRD feasibility envelope (1-day spike with margin)
- MVP stop-and-validate point at end of Wave 3 preserves compliance-officer primary product value
- Contingency clauses from architect + PM sign-off (architect C1 MEDIUM Issue-filing dependency, architect C2 MEDIUM non-empty guard, Edge Case 1 Wave 1 3-hour timebox, Edge Case 3 Surface C abbreviation authority) all surfaced in wave gate checklists
- Architect authoring continuity preserved across Waves 3-6 and 10 (voice consistency on ADR-025)
- T013 Decision task is the single source of truth for canonical decision-noun; all downstream references (T014, T016, T026, T027) trace back to T013 byte-identically (modulo case, per SC-007)

**Date**: 2026-04-15
**Agent**: team-lead
