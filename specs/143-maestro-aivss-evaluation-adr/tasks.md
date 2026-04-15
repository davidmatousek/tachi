---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-15
    status: APPROVED
    notes: "8 dimensions PASS, 0 blockers, 2 LOW non-blocking. All 4 user stories (US1 CISO MVP → US4 security engineer polish) mapped to phases with priority preserved; all 8 spec FRs covered; conditional Issue logic (T022 branch, T023 Option A/B, T024 Option C) correctly encoded mutually-exclusively; PM concern C2 (Status: Accepted grep) addressed twice at T018 + T026; 2-hour timebox at T003 preserved from Team-Lead Rec #2; five-layer scope discipline maintained; MVP boundary clean at end of Phase 3."
  architect_signoff:
    agent: architect
    date: 2026-04-15
    status: APPROVED_WITH_CONCERNS
    notes: "5 findings (2 MED + 3 LOW, 0 blocking) — all addressed inline. MED-1 T009 decision-noun grep tightened to enforce token equality (not just presence); MED-2 T021 anchor slug changed to explicit HTML anchor `<a id=surface-a></a>` for cross-renderer stability; LOW-1 T028 word-count awk command pinned; LOW-2 T003/T004 agent notes output channel specified as research.md ## Wave 1 AIVSS Spec Notes section; LOW-3 T033 gained rejected-PR contingency for Status: Proposed revert. ADR-024 structure fidelity, three-surface rigor (CVSS 3.1-vs-4.0 as Conflict row at T020), zero-drift gate (T025 exact 4 directories), conditional Phase 7 logic, Related ADRs double-verification (T006 + T029), and granularity (33 tasks for 1-day spike) all PASS."
  techlead_signoff:
    agent: team-lead
    date: 2026-04-15
    status: APPROVED
    notes: "4 LOW non-blocking observations. Timeline 4.5-7h wall-clock fits 1-day cycle with margin; 2-hour T003 timebox enforced at 4 locations; two-wave structure matches PRD Milestone table; agent mapping aligns with PRD Team-Lead Rec #1 (web-researcher T003-005, architect T006-021 + T033, product-manager T022-024, code-reviewer T025-031; senior-backend-engineer correctly excluded); Phase 3 MVP stop-and-validate point is valid; Phase 8 verification gates correctly parallel-dispatchable; no hidden critical-path gotchas."
---

# Tasks: MAESTRO Phase 4 — OWASP AIVSS Evaluation ADR

**Input**: Design documents from `specs/143-maestro-aivss-evaluation-adr/`
**Prerequisites**: [plan.md](plan.md) (PM + Architect APPROVED), [spec.md](spec.md) (PM APPROVED), [research.md](research.md)
**Tests**: No new test files required (documentation-only feature). Existing backward-compatibility test suite (`tests/scripts/test_backward_compatibility.py`) runs as a verification gate and must remain green byte-identical under `SOURCE_DATE_EPOCH=1700000000` (trivially satisfied — no pipeline inputs change).

**Organization**: Tasks are grouped by user story per [spec.md](spec.md). Each user story corresponds to a reader journey through the shared ADR artifact. The "independent test" for each US is a reader-facing verification gate rather than a separately-shippable code slice.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no write-ordering dependencies)
- **[Story]**: Which user story this task serves (e.g., US1, US2, US3, US4)
- Exact file paths included in every task description

## Path Conventions

This is a documentation-only feature. All writes target two surfaces:
- `docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md` (new)
- `.claude/skills/tachi-risk-scoring/SKILL.md` (updated)

No source tree changes. No new tests. No new scripts.

---

## Phase 1: Setup (Shared Context)

**Purpose**: Load feature context and confirm working environment

- [X] T001 Re-read `/Users/david/Projects/tachi/specs/143-maestro-aivss-evaluation-adr/research.md` and `/Users/david/Projects/tachi/specs/143-maestro-aivss-evaluation-adr/plan.md` to internalize the Wave 1 / Wave 2 split and the three-surface comparison requirement
- [X] T002 Confirm active branch is `143-maestro-aivss-evaluation-adr` via `git branch --show-current` (halt if any other branch is active)

---

## Phase 2: Foundational (Wave 1 — AIVSS Research — BLOCKS ALL AUTHORSHIP)

**Purpose**: AIVSS specification research must complete before any ADR authorship work begins. All user stories depend on this phase.

**CRITICAL**: Wave 2 authorship tasks cannot start until Phase 2 is complete.

- [X] T003 Confirm OWASP AIVSS canonical home (e.g., `aivss.owasp.org`) is reachable and identify the latest published version number. **TIMEBOX: 2 hours maximum.** If no authoritative AIVSS specification is located within 2 hours, **halt** and escalate to PM for a PRD close-without-delivery decision per PRD Risk R1 contingency. Append findings to `/Users/david/Projects/tachi/specs/143-maestro-aivss-evaluation-adr/research.md` under a new `## Wave 1 AIVSS Spec Notes` section (durable audit trail for PM escalation).
- [X] T004 Read the current AIVSS specification end-to-end (v0.8 expected per research.md, but implementer must confirm latest observed version at `aivss.owasp.org`). Capture: (a) exact version string, (b) canonical URL, (c) full dimension list (10 AARFs), (d) composite formula (`AIVSS_Score = ((CVSS_Base_Score + AARS) / 2) × ThM` per research), (e) severity band thresholds if defined (or confirm none defined), (f) the CVSS base version AIVSS builds on (v4.0 expected). Append findings to `/Users/david/Projects/tachi/specs/143-maestro-aivss-evaluation-adr/research.md` under the `## Wave 1 AIVSS Spec Notes` section created in T003.
- [X] T005 Cross-read `/Users/david/Projects/tachi/schemas/risk-scoring.yaml` and `/Users/david/Projects/tachi/.claude/skills/tachi-shared/references/severity-bands-shared.md` and `/Users/david/Projects/tachi/.claude/skills/tachi-risk-scoring/references/scoring-dimensions.md` to confirm tachi's current composite model (CVSS 3.1 × 0.35 + Exploitability × 0.30 + Reachability × 0.20 + Scalability × 0.15; bands Critical ≥9.0 / High 7.0-8.9 / Medium 4.0-6.9 / Low <4.0). Confirm no schema changes since `/aod.spec` research window.

**Checkpoint**: Research notes cover all four comparison axes (dimensions, composite formula, severity bands, CVSS base version). Wave 2 authorship can proceed.

---

## Phase 3: User Story 1 — CISO Procurement Brief (Priority: P1) MVP

**Goal**: A CISO opens ADR-024 and can answer "does tachi align with AIVSS?" in one paragraph, then follows the cross-reference to SKILL.md and sees the same decision. This is the MVP — if nothing else ships, US1 still delivers primary product value.

**Independent Test**: After task completion, a reader opens `docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md` and the first paragraph of the Decision section answers the alignment question without requiring any other file. Separately, a reader opens `.claude/skills/tachi-risk-scoring/SKILL.md`, finds the `## AIVSS Relationship` section between `## Domain Overview` and `## Baseline-Aware Scoring Rules`, and the decision there matches the ADR.

### Implementation for User Story 1

- [X] T006 [US1] Create ADR-024 file skeleton at `/Users/david/Projects/tachi/docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md` with frontmatter block matching the ADR-022 / ADR-023 shape: `**Status**: Accepted` (literal — not `Proposed`), `**Date**: 2026-04-16` (placeholder; update to actual merge date during PR review), `**Deciders**: Architect, Product Manager, Team-Lead` (per PRD Appendix A LOW-1 fix), `**Feature**: 143 (MAESTRO Phase 4)`, `**Related ADRs**: [ADR-020](ADR-020-maestro-layer-classification.md) (MAESTRO classification), [ADR-019](ADR-019-shared-definitions-and-model-field-governance.md) (shared cross-agent definitions), [ADR-018](ADR-018-baseline-aware-pipeline-correlation.md) (baseline-aware scoring lineage)`.
- [X] T007 [US1] Write ADR-024 Decision section at the same file — a single paragraph that names the chosen option (Adopt as primary / Adopt as supplementary / Diverge with rationale) and states the alignment answer in plain language. Must be readable without any other section loaded.
- [X] T008 [US1] Add `## AIVSS Relationship` section to `/Users/david/Projects/tachi/.claude/skills/tachi-risk-scoring/SKILL.md`, positioned **after** `## Domain Overview` (currently ends at line 19) and **before** `## Baseline-Aware Scoring Rules` (currently starts at line 21). Paragraph length must be **80-200 words**. Content must (a) reflect the ADR-024 Decision in plain language without contradiction, (b) contain a relative-path link to ADR-024 (`../../../docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md` — resolve path depth from SKILL.md location), (c) match at least one decision-noun token with the ADR (e.g., both say "diverge" or both say "adopt").
- [X] T009 [US1] Verify decision-noun **equality** (not just presence) between ADR-024 and SKILL.md (FR-6 / SC-007 single-source-of-truth rule). Run the following assertion and confirm exit code 0:
  ```bash
  ADR_TOKEN=$(grep -oE '(adopt|supplement|diverge)' /Users/david/Projects/tachi/docs/architecture/02_ADRs/ADR-024-*.md | head -1)
  SKILL_TOKEN=$(grep -oE '(adopt|supplement|diverge)' /Users/david/Projects/tachi/.claude/skills/tachi-risk-scoring/SKILL.md | head -1)
  [ "$ADR_TOKEN" = "$SKILL_TOKEN" ] || { echo "decision-noun mismatch: ADR=$ADR_TOKEN SKILL=$SKILL_TOKEN"; exit 1; }
  ```
  Mere presence of any decision-noun in both files is insufficient — the **same** token must appear in both. If mismatch, correct SKILL.md to match the ADR before checkpoint.

**Checkpoint**: US1 delivered — the CISO procurement brief user can answer alignment in under five minutes using only the ADR and SKILL.md. The ADR has Status: Accepted, Related ADRs frontmatter, Decision paragraph. SKILL.md has the relationship section.

---

## Phase 4: User Story 2 — Compliance Officer Report-vs-Translate (Priority: P1)

**Goal**: A compliance officer reads the three-surface comparison (dimensions, composite formula, severity bands) and makes a report-vs-translate decision based on documented alignment rather than guesswork.

**Independent Test**: After task completion, a reader opens ADR-024 and the Context section contains three distinct, labeled tables/subsections (Surface A, Surface B, Surface C). Every row in Surface A is annotated with exactly one of Overlap / Gap / Conflict / No equivalent. No "TBD" or "unclear" labels remain.

### Implementation for User Story 2

- [X] T010 [US2] Draft ADR-024 Context Surface A (Dimension Set) in `/Users/david/Projects/tachi/docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md`. Markdown table with columns: `Tachi Dimension | Weight | AIVSS Equivalent | Relationship | Note`. One row per tachi dimension: CVSS 3.1 base (0.35), Exploitability (0.30), Reachability (0.20), Scalability (0.15). Each row's Relationship cell must contain exactly one of: `Overlap`, `Gap`, `Conflict`, or `No equivalent`. CVSS row Relationship must be `Conflict` because AIVSS uses CVSS v4.0 vs tachi CVSS 3.1 (version gap is a concrete conflict).
- [X] T011 [US2] Draft ADR-024 Context Surface B (Composite Formula Weights) in the same file. Side-by-side comparison: tachi's `composite_score = (0.35 × CVSS) + (0.30 × Exploitability) + (0.20 × Reachability) + (0.15 × Scalability)` versus AIVSS's `AIVSS_Score = ((CVSS_Base_Score + AARS) / 2) × ThM`. Include a one-line annotation explaining the structural difference: tachi weighted-sum across 4 dimensions, AIVSS averaged sum of 2 terms × optional multiplier. If AIVSS lacks a published composite formula at observed version, explicitly state "no AIVSS equivalent" instead of glossing over.
- [X] T012 [US2] Draft ADR-024 Context Surface C (Severity Band Thresholds) in the same file. Side-by-side table of tachi bands (`Critical ≥ 9.0`, `High 7.0-8.9`, `Medium 4.0-6.9`, `Low < 4.0`) versus AIVSS bands (if defined at observed version; otherwise explicitly state "no AIVSS severity bands defined in v{observed}").
- [X] T013 [US2] IF the decision reached in Phase 5 is `diverge` (Option C), add the Rationale worked-examples sub-section in ADR-024 Rationale. Provide at least **two** concrete findings where tachi and AIVSS produce measurably different composite scores. Both scores must be numerically quantified (e.g., "tachi 7.4 vs AIVSS 5.9 for {finding description}"). If the decision is `adopt` (Option A or B), T013 is skipped — Rationale instead focuses on the five-criteria justification (maturity, adoption, compatibility, effort, compliance value) without worked examples.

**Checkpoint**: US2 delivered — the compliance officer can review the three surfaces, see every dimension labeled, and make the report-vs-translate decision.

---

## Phase 5: User Story 3 — Maintainer Decision Traceability (Priority: P2)

**Goal**: A future maintainer finds ADR-024 and sees at least three options enumerated with rationale, so they can evaluate whether a proposed change is consistent with prior reasoning or constitutes a deliberate reversal.

**Independent Test**: After task completion, ADR-024's Alternatives Considered section lists at least three options. Each option has Pros, Cons, an S/M/L effort estimate, a compliance-value note, and a "Why Not Chosen" (for rejected options) or "Why Chosen" (for the recommended option) rationale. The Status field reads `Accepted` (not `Proposed`).

### Implementation for User Story 3

- [X] T014 [US3] Draft ADR-024 Alternatives Considered — **Option A: Adopt AIVSS as Primary Scoring Replacement** in `/Users/david/Projects/tachi/docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md`. Include: Pros, Cons, Effort (S/M/L with rough day range — e.g., "L: ~5-8 days; schema-breaking change with example regeneration"), Compliance Value for Regulated Adopters, and "Why Not Chosen" rationale (or "Why Chosen" if Option A is the recommended option).
- [X] T015 [US3] Draft ADR-024 Alternatives Considered — **Option B: Adopt AIVSS as Supplementary Field** in the same file. Additive change (no schema break). Include: Pros, Cons, Effort (S/M/L — e.g., "M: ~2-3 days; additive schema field, no example regeneration"), Compliance Value, and "Why Not Chosen" / "Why Chosen" rationale.
- [X] T016 [US3] Draft ADR-024 Alternatives Considered — **Option C: Document Divergence with Rationale** in the same file. No schema change; ADR explains posture. Include: Pros, Cons, Effort (S/M/L — typically "S: ~0 additional effort beyond this ADR"), Compliance Value, and "Why Not Chosen" / "Why Chosen" rationale.
- [X] T017 [US3] Draft ADR-024 Consequences + When to Re-Evaluate sections in the same file. Consequences must distinguish: if Option A or B chosen, name the follow-on implementation feature and link to its GitHub Issue (populated in Phase 7); if Option C chosen, state "no further action" and cite the re-evaluation trigger. When to Re-Evaluate trigger must be concrete: "AIVSS publishes stable v1.0 with at least one external adopter case study" (per PRD Risk R2 mitigation).
- [X] T018 [US3] Verify frontmatter `**Status**: Accepted` (not `Proposed`) at the top of `/Users/david/Projects/tachi/docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md`. Run `grep -c '^\*\*Status\*\*: Accepted' /Users/david/Projects/tachi/docs/architecture/02_ADRs/ADR-024-*.md` — must return `1`. This closes PM concern C2 from PRD approval (deferred to tasks.md).

**Checkpoint**: US3 delivered — the maintainer sees all three options with full documentation, Status: Accepted enforced.

---

## Phase 6: User Story 4 — Security Engineer Dimension Mapping Polish (Priority: P2)

**Goal**: A security engineer copies a URL-with-anchor to the Surface A heading, pastes it into external documentation, and the anchor resolves to the dimension mapping table.

**Independent Test**: After task completion, every Surface A row is unambiguously labeled (no "TBD" or "unclear"); the CVSS 3.1 vs 4.0 version gap is explicitly called out as a Conflict row; and a URL with heading anchor `#surface-a-dimension-set` (or equivalent Markdown-generated anchor) resolves directly to the Surface A heading when the ADR is rendered by a standard Markdown viewer.

### Implementation for User Story 4

- [X] T019 [US4] Audit Surface A rows in `/Users/david/Projects/tachi/docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md`: every row's Relationship cell contains exactly one of `Overlap`, `Gap`, `Conflict`, `No equivalent`. No "TBD", "unclear", or empty cells. If any cell is ambiguous, resolve via re-reading Wave 1 research notes.
- [X] T020 [US4] Verify the CVSS row in Surface A is explicitly labeled `Conflict` with a Note cell citing the CVSS version gap: "tachi uses CVSS 3.1; AIVSS v{observed} builds on CVSS v4.0". This is the concrete Conflict row surfaced in research.md and should not be silently collapsed into an "Overlap" headline (PRD FR-2 business rule).
- [X] T021 [US4] Add a renderer-independent HTML anchor tag immediately before the Surface A heading to guarantee cross-renderer stability. Insert `<a id="surface-a"></a>` on its own line immediately above `### Surface A — Dimension Set` (or equivalent heading). The explicit anchor `#surface-a` is then renderer-independent — it does not depend on the GitHub slugify algorithm's handling of em-dash, whitespace, or non-ASCII characters. Verify the anchor resolves by previewing the ADR in at least two Markdown renderers (GitHub preview + any other — VS Code preview, pandoc, or Docusaurus are acceptable).

**Checkpoint**: US4 delivered — security engineer can cite a stable anchor link; CVSS version gap is a first-class Conflict row.

---

## Phase 7: Conditional Follow-on Issue (FR-007)

**Goal**: If the ADR-024 Decision is `adopt` (Option A or B), file a follow-on implementation Issue with `stage:discover` label referencing ADR-024. If the Decision is `diverge` (Option C), file no Issue.

**Note**: This phase is conditional. T022 is the branching task; T023 and T024 are mutually exclusive.

- [X] T022 Read the final Decision section of `/Users/david/Projects/tachi/docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md`. If decision is Option A or B, execute T023 and skip T024. If decision is Option C, execute T024 and skip T023.
- [N/A] T023 (conditional, Option A or B only — skipped: Option C chosen) File a follow-on implementation Issue via `bash /Users/david/Projects/tachi/.aod/scripts/bash/create-issue.sh`. Required fields: title (concrete — e.g., "Implement OWASP AIVSS supplementary scoring (per ADR-024)"), label `stage:discover`, body that (a) links back to ADR-024 by relative path, (b) names **3-5 surfaces** that would change in implementation (e.g., `schemas/risk-scoring.yaml`, `.claude/skills/tachi-risk-scoring/references/`, `templates/tachi/**.typ`, `scripts/extract-*.py`) — full ICE-scored breakdown is **deferred** to the follow-on PRD's own discovery cycle per PRD FR-7 fidelity rule, (c) includes the **option-specific effort estimate copied verbatim** from ADR-024 Alternatives Considered for the chosen option. After filing, record the Issue number and update ADR-024 Consequences section with the Issue link.
- [X] T024 (conditional, Option C only) Record in PR description: "Decision: Option C (diverge). No follow-on implementation Issue filed per FR-007 conditionality." ADR-024 Consequences section instead cites the re-evaluation trigger.

**Checkpoint**: Phase 7 correctness verified — conditional logic respected (Issue exists iff decision is A or B).

---

## Phase 8: Polish & Zero-Drift Verification

**Purpose**: Verify the scope-discipline invariants (zero production code changes), word counts, grep assertions, and file integrity.

- [X] T025 Run `git diff main..HEAD -- schemas/ scripts/ .claude/agents/ examples/` from the repository root. Output **must be empty**. If any file under those four directories has been modified, revert the change or escalate for PM / Architect review (FR-008, SC-006).
- [X] T026 Run `grep -c '^\*\*Status\*\*: Accepted' /Users/david/Projects/tachi/docs/architecture/02_ADRs/ADR-024-*.md` — must return exactly `1` (SC-002 enforcement, closes PM concern C2 from PRD approval).
- [X] T027 Run `grep -c 'ADR-024' /Users/david/Projects/tachi/.claude/skills/tachi-risk-scoring/SKILL.md` — must return `≥ 1` (SC-005 enforcement).
- [X] T028 Verify SKILL.md AIVSS Relationship section word count is between 80 and 200 words (SC-005). Run the pinned command:
  ```bash
  awk '/^## AIVSS Relationship/{flag=1; next} /^## /{flag=0} flag' \
    /Users/david/Projects/tachi/.claude/skills/tachi-risk-scoring/SKILL.md | wc -w
  ```
  The awk filter excludes both the start and end `##` heading lines and counts body words only. Confirm the printed count is ≥ 80 and ≤ 200.
- [X] T029 Verify ADR-024 frontmatter Related ADRs list includes at minimum `ADR-020`, `ADR-019`, `ADR-018` (SC-009). Run `grep -E 'ADR-020|ADR-019|ADR-018' /Users/david/Projects/tachi/docs/architecture/02_ADRs/ADR-024-*.md | head -5` and confirm all three appear.
- [X] T030 Run the existing backward-compatibility test suite: `cd /Users/david/Projects/tachi && SOURCE_DATE_EPOCH=1700000000 python -m pytest tests/scripts/test_backward_compatibility.py -v`. All 5 baseline PDFs must remain byte-identical (trivially satisfied — no pipeline inputs change). Any failure is a red flag for scope drift.
- [X] T031 Verify no new runtime dependencies were added: `git diff main..HEAD -- pyproject.toml requirements*.txt package.json` must be empty (Constraint from spec.md).
- [X] T032 Open the pull request with title `docs(143): MAESTRO Phase 4 — OWASP AIVSS evaluation ADR` (conventional commit `docs:` type per Constitution IX). PR body must (a) link to ADR-024 once committed on main, (b) summarize the three-surface comparison in 2-3 bullets, (c) state the recommended option, (d) cite the zero-drift assertion output from T025 as evidence, (e) list the Issue number from T023 if filed (or "no follow-on Issue filed — Option C" if T024 path taken).
- [X] T033 Architect final review on PR — APPROVED verdict serves as the "Accepted at merge" attestation (closed in PRD Open Questions). Update ADR-024 Date field to actual merge date before squash-merge. No separate sign-off ceremony. **Contingency**: if the PR is rejected and re-work is required, revert ADR-024 Status to `Proposed` before the next revision cycle and restore to `Accepted` only after the next architect APPROVED verdict — this preserves the literal consistency between the Status marker and the actual lifecycle state.

**Checkpoint**: All 9 success criteria (SC-001 through SC-009) verified. Feature ready for merge.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies. Can start immediately.
- **Phase 2 (Foundational — AIVSS Research)**: Depends on Phase 1. **BLOCKS** all authorship phases. 2-hour timebox on T003 with PM escalation checkpoint.
- **Phase 3 (US1 MVP)**: Depends on Phase 2. Once Phase 3 completes, MVP is delivered (CISO can answer alignment question from one file).
- **Phase 4 (US2)**: Depends on Phase 3 (ADR file exists with frontmatter). Surface A, B, C can be written in parallel — T010/T011/T012 are [P]-compatible if different editors work different sections, but they share one file so serialization via patch-style edits is recommended.
- **Phase 5 (US3)**: Depends on Phases 3 and 4 (ADR context must exist before Alternatives Considered makes sense). Options A/B/C (T014/T015/T016) can be drafted in parallel by one writer but share one file.
- **Phase 6 (US4)**: Depends on Phase 4 (Surface A must exist before polish). T019, T020, T021 are sequential refinements to Surface A.
- **Phase 7 (Conditional Issue)**: Depends on Phase 5 (Decision must be finalized). T023 vs T024 is an exclusive-or.
- **Phase 8 (Polish)**: Depends on all prior phases. Verification gates.

### User Story Dependencies

- **US1 (P1)**: Delivers on its own as MVP. No dependency on US2/US3/US4.
- **US2 (P1)**: Delivers alongside or after US1. Shares the same file surface (ADR-024), so US2 and US1 are ordered rather than truly parallel.
- **US3 (P2)**: Depends on US2 (needs Context to reference from Alternatives Considered).
- **US4 (P2)**: Depends on US2 (polishes Surface A).

### Within Each User Story

- Models-before-services / services-before-endpoints is NOT applicable to this feature (no code path).
- Frontmatter before prose — T006 must complete before T007.
- Context before Alternatives Considered before Decision finalization.
- SKILL.md AIVSS Relationship section must match ADR Decision (T008 after T007, or revise T008 if Decision changes during review).

### Parallel Opportunities

- T003, T004, T005 in Wave 1 are sequential for the same researcher (T003 confirms home → T004 reads spec → T005 cross-reads tachi).
- T010, T011, T012 (Surface A/B/C drafting) — same writer, same file; serialize writes but can draft content in parallel editors.
- T014, T015, T016 (Options A/B/C drafting) — same writer, same file; serialize writes but can draft content in parallel editors.
- T022 is a decision branch; T023 and T024 are mutually exclusive and cannot be parallelized.
- T025 through T031 (verification gates) can run in parallel — each reads different files and emits independent pass/fail signals.

---

## Parallel Example: Phase 8 Verification Gates

```bash
# Run all verification gates in parallel (each reads different files, no write-ordering):
Task: "Run git diff assertion (T025) — output must be empty"
Task: "Run Status: Accepted grep (T026) — must return exactly 1"
Task: "Run ADR-024 reference grep in SKILL.md (T027) — must return >= 1"
Task: "Verify SKILL.md word count 80-200 (T028)"
Task: "Verify Related ADRs list includes ADR-020, ADR-019, ADR-018 (T029)"
Task: "Run backward-compat test suite (T030) — must be byte-identical"
Task: "Verify no new runtime deps (T031) — must be empty diff"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1: Setup (context loaded)
2. Complete Phase 2: Foundational (AIVSS research done, within 2-hour timebox)
3. Complete Phase 3: US1 — ADR frontmatter + Decision + SKILL.md cross-reference
4. **STOP and VALIDATE**: CISO-reader test — opens ADR-024, answers "does tachi align with AIVSS?" in one paragraph; opens SKILL.md, sees matching decision
5. If MVP is enough, skip to Phase 8 and commit — US1 alone delivers primary product value

### Incremental Delivery (Full Feature)

1. Complete Setup + Foundational → research ready
2. Complete US1 (Phase 3) → CISO journey works (MVP)
3. Complete US2 (Phase 4) → compliance officer journey works (three surfaces)
4. Complete US3 (Phase 5) → maintainer journey works (alternatives documented)
5. Complete US4 (Phase 6) → security engineer journey works (Surface A polish + anchor)
6. Complete Phase 7 (conditional Issue) → follow-on work anchored if decision is A or B
7. Complete Phase 8 (polish + gates) → ready for PR
8. Open PR and obtain architect approval → merge

### Parallel Team Strategy (Not Applicable)

Single writer for ADR authorship preserves voice consistency. Parallelization is at the verification-gate layer (Phase 8 gates run in parallel) and the content-drafting layer (Surfaces A/B/C drafted in parallel editors by one writer). Multi-writer parallelism would introduce merge conflicts on the shared ADR file with no throughput benefit.

---

## Notes

- **[P] tasks = different files, no write-ordering conflict.** Most tasks here share one file (ADR-024) or operate on different read targets — [P] is sparingly applied.
- **[Story] label** maps tasks to user stories (US1 → MVP, US4 → polish layer). Setup (Phase 1), Foundational (Phase 2), Conditional Issue (Phase 7), and Polish (Phase 8) phases do not carry [Story] labels per the governance rule.
- **Each user story is independently verifiable** through reader-facing tests (the "Independent Test" checkpoint under each phase heading) — not through separately shippable code.
- **Two-wave structure** (research + authorship) matches PRD Milestone table and Team-Lead assignment.
- **Stop at any checkpoint to validate story independently** — US1 MVP validates at the end of Phase 3; full feature validates at the end of Phase 8.
- **Avoid**: vague tasks (every task has a file path or grep assertion), cross-story file conflicts (mitigated by single-writer convention for shared ADR), scope drift (Phase 8 zero-drift gate enforces this).
