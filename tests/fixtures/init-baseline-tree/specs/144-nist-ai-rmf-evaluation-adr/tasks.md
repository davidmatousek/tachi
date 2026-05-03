---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-15
    status: APPROVED
    notes: "0 CRITICAL / 0 HIGH / 0 MEDIUM / 3 LOW (informational, non-blocking). All 5 user stories (US1 P1 MVP → US5 P1 non-disruption) represented with dedicated phases and [Story] labels (19 tasks carry labels; 25 Setup/Foundational/Conditional/Polish tasks correctly omit). All 8 spec FRs covered; all 13 SCs have explicit verifier tasks. Conditional FR-008 branching correctly encoded (T026 branch → T027 xor T028). Decision-noun discipline preserved (T013 is the single source of truth; no task prejudges Option A/B/C). Five-layer scope discipline airtight (SC-006 gated at T024 + T034). MVP boundary clean at end of Phase 3. 3-hour Wave 1 timebox at T003 with 3 contingency options. docs: commit prefix gated at T040. SC-007 non-empty guard present at T015 + T035 per architect plan review C2. 3 LOW findings all deferrable to implementation or PR description (no inline tasks.md changes required). Full review at .aod/results/tasks-pm-review-144.md."
  architect_signoff:
    agent: architect
    date: 2026-04-15
    status: APPROVED
    notes: "0 CRITICAL / 0 HIGH / 0 MEDIUM / 4 LOW (informational, non-blocking). Both architect plan-level concerns resolved: C1 (Issue-filing dependency on finalized Alternatives effort string) encoded at 4 locations — T027 task body, Phase 8 preamble, Dependencies ordering, Notes. C2 (SC-007 non-empty guard) propagated to both T015 and T035. All 10 technical checkpoints pass: dependency ordering, decision-noun grep patterns with case-insensitive flag + tr lowercase normalization, explicit HTML anchor tags (cross-renderer stable), SC-006 zero-drift exactly 4 directories, Related ADRs minimum 6 (ADR-024 + ADR-020 + ADR-019 + ADR-018 + ADR-021 + ADR-023), Phase 9 verification gates marked [P], 13/13 SCs with verifier tasks, SOURCE_DATE_EPOCH=1700000000 per ADR-021, pinned awk word-count for SC-005. Feature 143 precedent faithfully mirrored with PRD-144 tightening. Execution-ready. Full review at .aod/results/tasks-architect-review-144.md."
  techlead_signoff:
    agent: team-lead
    date: 2026-04-15
    status: APPROVED_WITH_CONCERNS
    notes: "0 CRITICAL / 0 HIGH / 2 MEDIUM / 4 LOW (all non-blocking). 44 tasks across 9 phases fit 1-day spike budget (wall-clock estimate: 3h Wave 1 + 5-7h Wave 2 + 1h verification + PR cycle). Expansion from Feature 143's 32 tasks justified by genuine scope growth (FR-007 tachi-shared artifact new; 5 user stories vs 4; SC-011 ADR-024 back-ref new; SC-012/SC-013 checks new; NIST surface = AI RMF 1.0 + NIST AI 600-1 + 12 GAI risks). 3-hour Wave 1 timebox correctly enforced at COMBINED level (T003+T004+T005+T006) with 3 contingency options verbatim from spec. Agent assignments align with PRD line 476: web-researcher T003-T006, architect T007-T025, product-manager T027, code-reviewer-parallelizable T029-T042, architect T044. Phase 9 [P] gates shell-parallelizable. Critical path explicit and serialized. MVP stop-and-validate at end of Phase 3. MEDIUM-1 (agent-per-task annotations deferred to agent-assignments.md) and MEDIUM-2 (T013 implicit dependency on T009-T011) are carry-forward process-visibility notes, not blockers. Full review at .aod/results/tasks-techlead-review-144.md."
---

# Tasks: NIST AI RMF Integration Evaluation ADR

**Input**: Design documents from `specs/144-nist-ai-rmf-evaluation-adr/`
**Prerequisites**: [plan.md](plan.md) (PM + Architect APPROVED_WITH_CONCERNS), [spec.md](spec.md) (PM APPROVED), [research.md](research.md), [quickstart.md](quickstart.md)
**Tests**: No new test files required (documentation-only feature). Existing `tests/scripts/test_backward_compatibility.py` runs as a verification gate and must remain 5/5 byte-identical under `SOURCE_DATE_EPOCH=1700000000` per ADR-021 (trivially satisfied — no pipeline inputs change).

**Organization**: Tasks are grouped by user story per [spec.md](spec.md). Each user story corresponds to a reader journey through the shared ADR-025 artifact + companion files. The "independent test" for each US is a reader-facing or shell-verifier gate rather than a separately-shippable code slice.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no write-ordering dependencies)
- **[Story]**: Which user story this task serves (e.g., US1, US2, US3, US4, US5)
- Exact file paths included in every task description

## Path Conventions

This is a documentation-only feature. All writes target five surfaces:

- `docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md` (new, ~200-280 lines)
- `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` (new, content shape per chosen option)
- `.claude/skills/tachi-control-analysis/SKILL.md` (updated — new `## NIST AI RMF Relationship` section, 80-200 words)
- `docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md` (single-line edit to Related ADRs)
- `specs/144-nist-ai-rmf-evaluation-adr/research.md` (append `## Wave 1 — NIST AI RMF Spec Notes` section)

No source tree changes. No new tests. No new scripts. No schema bumps. Zero drift on `schemas/`, `scripts/`, `.claude/agents/`, `examples/` (SC-006).

---

## Phase 1: Setup (Shared Context)

**Purpose**: Load feature context and confirm working environment

- [X] T001 Re-read `/Users/david/Projects/tachi/specs/144-nist-ai-rmf-evaluation-adr/research.md`, `/Users/david/Projects/tachi/specs/144-nist-ai-rmf-evaluation-adr/plan.md`, and `/Users/david/Projects/tachi/specs/144-nist-ai-rmf-evaluation-adr/quickstart.md` to internalize the Wave 1 / Wave 2 split, the three-surface comparison requirement, and the five-surface allow-list (SC-006)
- [X] T002 Confirm active branch is `144-nist-ai-rmf-evaluation-adr` via `git branch --show-current` (halt if any other branch is active)

---

## Phase 2: Foundational (Wave 1 — NIST AI RMF Research — BLOCKS ALL AUTHORSHIP)

**Purpose**: NIST AI RMF specification research must complete before any ADR authorship work begins. All user stories depend on this phase.

**CRITICAL**: Wave 2 authorship tasks cannot start until Phase 2 is complete. **3-hour timebox** on Wave 1 (SC-013, PRD Risk R1 mitigation).

- [X] T003 Confirm NIST AI RMF canonical home page (`https://www.nist.gov/itl/ai-risk-management-framework`) is reachable and identify the latest published AI RMF version number + publication date. **TIMEBOX: 3 hours maximum across T003+T004+T005+T006 combined.** If the 3-hour budget is exceeded, **pause** and choose ONE of three contingency options per spec Edge Case 1: (a) descope FR-002 Surface B sample from "5-10 representative subcategories" to "3 subcategories"; (b) defer FR-007 tachi-shared artifact creation to a follow-on Issue (ship only ADR-025 + SKILL.md update in this PR); (c) escalate to PM. Append findings to `/Users/david/Projects/tachi/specs/144-nist-ai-rmf-evaluation-adr/research.md` under a new `## Wave 1 — NIST AI RMF Spec Notes` section (durable audit trail for PM escalation and delivery retrospective).
- [X] T004 Read AI RMF 1.0 (`https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf`) end-to-end. Capture in `research.md` Wave 1 section: (a) exact AI RMF version string (1.0 expected), (b) canonical URL, (c) four Functions (Govern, Map, Measure, Manage), (d) representative sample of Categories and Subcategories under each Function (5-10 Subcategories drawn from the most agentic-AI-relevant Categories), (e) notes on any NIST AI RMF 2.0 or revision status since the PRD filing date (see spec Edge Case 2).
- [X] T005 Read NIST AI 600-1 Generative AI Profile (`https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf`, DOI `https://doi.org/10.6028/NIST.AI.600-1`) end-to-end. Capture in `research.md` Wave 1 section: (a) exact version string and publication date, (b) canonical URL + DOI, (c) **complete list** of NIST AI 600-1 §2 Generative AI Profile risk categories (validate exactly 12 against PRD's "12-13" estimate per pre-spec research — correct the estimate inline if needed per spec Assumption on framework structural shape), (d) a short description of each GAI risk (1-2 sentences) to support Surface C mapping in Wave 2.
- [X] T006 Cross-read `/Users/david/Projects/tachi/.claude/skills/tachi-control-analysis/references/control-categories.md` (to confirm the 8 tachi compensating-control categories: authentication, input-validation, rate-limiting, encryption, logging-audit, csrf-protection, csp-security-headers, access-control), `/Users/david/Projects/tachi/.claude/skills/tachi-shared/references/stride-categories-shared.md` (to confirm the 11 tachi STRIDE+AI categories: S, T, R, I, D, E + Prompt Injection, Data Poisoning, Model Theft, Agent Autonomy, Tool Abuse), and the tachi pipeline phase names (Phase 1 Scope, Phase 2 Threat Detection, Phase 3 Compensating Controls, Phase 3.5 Cross-Layer Chains, Phase 4 Assessment, Phase 5 Reporting) from `/Users/david/Projects/tachi/docs/architecture/01_system_design/README.md`. Confirm no schema changes since `/aod.spec` research window (SC-006 baseline).

**Checkpoint**: Research notes cover all three comparison axes (Functions × phases, Subcategories × control categories, GAI risks × STRIDE+AI categories). Wave 2 authorship can proceed. 3-hour timebox respected or PM-escalated contingency chosen.

---

## Phase 3: User Story 1 — Compliance Officer NIST Mapping Decision (Priority: P1) MVP

**Goal**: A compliance officer opens ADR-025 and can answer "does tachi output map to NIST AI RMF vocabulary?" in one paragraph, then scrolls to Context and sees three labeled Surface subsections with every row annotated Overlap / Gap / Conflict / "No equivalent". This is the MVP — if nothing else ships, US1 alone delivers primary product value.

**Independent Test**: After task completion, a reader opens `docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md` and (a) the Decision section's first paragraph names tachi's NIST AI RMF posture with a single decision-noun; (b) the Context section contains three labeled subsections with `<a id="surface-a"></a>` / `<a id="surface-b"></a>` / `<a id="surface-c"></a>` anchors; (c) every row in those subsections uses exactly one of: Overlap, Gap, Conflict, "No equivalent".

### Implementation for User Story 1

- [X] T007 [US1] Create ADR-025 file skeleton at `/Users/david/Projects/tachi/docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md` with frontmatter block matching the ADR-022 / ADR-023 / ADR-024 shape: `**Status**: Accepted` (literal — not `Proposed`), `**Date**: <merge-date-placeholder>` (update to actual merge date during PR review), `**Deciders**: Architect, Product Manager, Team-Lead`, `**Feature**: 144 (MAESTRO Companion: NIST AI RMF)`, `**Related ADRs**: [ADR-024](ADR-024-owasp-aivss-evaluation.md) (companion AIVSS), [ADR-020](ADR-020-maestro-layer-classification.md) (MAESTRO classification), [ADR-019](ADR-019-shared-definitions-and-model-field-governance.md) (shared definitions), [ADR-018](ADR-018-baseline-aware-pipeline-correlation.md) (baseline lineage), [ADR-021](ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md) (SOURCE_DATE_EPOCH determinism), [ADR-023](ADR-023-threat-agent-skill-references-pattern.md) (skill-references pattern)`. Add all seven section headings as empty shells: `## Context`, `## Decision`, `## Rationale`, `## Alternatives Considered`, `## Consequences`, `## When to Re-Evaluate`, `## References`.
- [X] T008 [US1] Draft ADR-025 Context section in the same file. Open with a short summary of NIST AI RMF (AI RMF 1.0 version + URL + 4 Functions) and NIST AI 600-1 GAI Profile (version + URL/DOI + 12 GAI risks), then a one-paragraph recap of tachi's compensating controls analyzer (8 categories + 11 STRIDE+AI + pipeline phase vocabulary). All facts MUST be drawn from research.md Wave 1 notes — do not paraphrase NIST text without citation.
- [X] T009 [US1] Insert `<a id="surface-a"></a>` anchor tag on its own line immediately above the `### Surface A — NIST AI RMF Functions × tachi pipeline phases` heading in the Context section of the same file. Draft Surface A as a Markdown table with columns: `NIST AI RMF Function | tachi Phase 1 Scope | tachi Phase 2 Threat Detection | tachi Phase 3 Compensating Controls | tachi Phase 3.5 Cross-Layer Chains | tachi Phase 4 Assessment | tachi Phase 5 Reporting | Relationship | Note`. One row per Function (Govern, Map, Measure, Manage). Each row's Relationship cell MUST contain exactly ONE of: `Overlap`, `Gap`, `Conflict`, or `No equivalent`. No "TBD" / "unclear" / empty cells (SC-004).
- [X] T010 [US1] Insert `<a id="surface-b"></a>` anchor tag on its own line immediately above the `### Surface B — NIST AI RMF Subcategories × tachi compensating-control categories` heading in the same file. Draft Surface B as a Markdown table with columns: `NIST Subcategory | tachi Control Category | Relationship | Note`. One row per representative Subcategory from the 5-10-sample collected in T004 × the 8 tachi control categories (authentication, input-validation, rate-limiting, encryption, logging-audit, csrf-protection, csp-security-headers, access-control). Use many-to-many mapping where needed (a Subcategory may map to multiple control categories). Each Relationship cell MUST contain exactly ONE of the four allowed labels.
- [X] T011 [US1] Insert `<a id="surface-c"></a>` anchor tag on its own line immediately above the `### Surface C — NIST AI 600-1 Generative AI Profile risks × tachi STRIDE+AI categories` heading in the same file. Draft Surface C as a Markdown table with columns: `GAI Risk (NIST AI 600-1 §2) | tachi STRIDE+AI Category | Relationship | Note`. One row per GAI risk (12 total from T005) × 11 STRIDE+AI categories. Use many-to-many mapping where needed (a GAI risk may map to multiple STRIDE+AI categories, or to "No equivalent"). Each Relationship cell MUST contain exactly ONE of the four allowed labels. **If Surface C is structurally intractable within the day budget** (per spec Edge Case 3), abbreviate to a summary paragraph with 3-4 exemplar rows — architect scope-reduction authority applies here, and the abbreviated shape still satisfies SC-003 anchor requirement and SC-004 label requirement for the rows that ARE present.
- [X] T012 [US1] Audit all rows across Surface A, B, C in the same file: every Relationship cell contains exactly one of `Overlap`, `Gap`, `Conflict`, `No equivalent`. No "TBD", "unclear", or empty cells (SC-004 gate). Additional rule: if more than half (>50%) of Surface C GAI risks have `No equivalent`, append a paragraph under Surface C explicitly acknowledging the high-mismatch rate and flagging it as a sixth evaluation criterion for the Rationale section (per spec Edge Case 4).
- [X] T013 [US1] Draft ADR-025 Decision section in the same file. First paragraph MUST contain a single canonical decision-noun drawn from the allow-list `(documentation-only mapping|shallow wired integration|deep wired integration|hybrid [BC])`. The decision is chosen **after** Wave 1 research completes and Surfaces are drafted — implementer MUST NOT prejudge per spec Assumption "Pre-1.0 maturity does not auto-default to diverge" and PRD FR-4 "reasoned afresh" clause. Record the chosen decision-noun in a brief PR description note (to be referenced by T023 Phase 8 branching task).

**Checkpoint**: US1 delivered — the MVP. Compliance officer's Independent Test passes: ADR-025 has Decision (single canonical decision-noun) + Surface A/B/C with explicit anchors + all rows labeled.

---

## Phase 4: User Story 2 — Security Engineer Procurement Justification (Priority: P1)

**Goal**: A security engineer grep-searches for "NIST AI RMF" in the ADR directory, finds ADR-025, follows the cross-reference from `tachi-control-analysis/SKILL.md` to ADR-025, and confirms the SKILL.md paragraph and the ADR Decision use the **same** decision-noun (verbatim consistency, byte-equality modulo case).

**Independent Test**: After task completion, a reader opens `.claude/skills/tachi-control-analysis/SKILL.md`, finds the new `## NIST AI RMF Relationship` section between `## Domain Overview` and `## Baseline-Aware Control Analysis Rules`, reads a paragraph that uses the same canonical decision-noun as ADR-025 Decision, and follows a relative link that resolves to ADR-025. The SC-007 shell verifier passes (byte-equality + non-empty guard).

### Implementation for User Story 2

- [X] T014 [US2] Add `## NIST AI RMF Relationship` section to `/Users/david/Projects/tachi/.claude/skills/tachi-control-analysis/SKILL.md`, positioned **after** the existing `## Domain Overview` section and **before** the existing `## Baseline-Aware Control Analysis Rules` section (mirrors ADR-024 → tachi-risk-scoring/SKILL.md placement pattern, per plan.md Component 3 and research.md §2). Section content MUST: (a) be **80-200 words** (verified in Phase 9 by `awk` extraction + `wc -w`, SC-005); (b) contain a relative-path link to ADR-025: `../../../docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md`; (c) reference the ADR Decision in plain language without contradiction; (d) contain the **exact same canonical decision-noun** used in the ADR-025 Decision section first paragraph (byte-identical modulo case).
- [X] T015 [US2] Verify decision-noun **byte-equality with non-empty guard** between ADR-025 and SKILL.md (FR-006 / SC-007, addressing architect plan review C2 MEDIUM). Run the following assertion and confirm exit code 0:
  ```bash
  ADR_NOUN=$(grep -oE -i '(documentation-only mapping|shallow wired integration|deep wired integration|hybrid [BC])' /Users/david/Projects/tachi/docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md | head -1 | tr '[:upper:]' '[:lower:]')
  SKILL_NOUN=$(grep -oE -i '(documentation-only mapping|shallow wired integration|deep wired integration|hybrid [BC])' /Users/david/Projects/tachi/.claude/skills/tachi-control-analysis/SKILL.md | head -1 | tr '[:upper:]' '[:lower:]')
  [ "$ADR_NOUN" = "$SKILL_NOUN" ] && [ -n "$ADR_NOUN" ] || { echo "SC-007 FAIL: ADR='$ADR_NOUN' SKILL='$SKILL_NOUN'"; exit 1; }
  echo "SC-007 PASS: $ADR_NOUN"
  ```
  The `[ -n "$ADR_NOUN" ]` non-empty guard prevents a both-empty false-PASS if neither file contains a recognized noun. If mismatch, correct SKILL.md to match the ADR Decision (do NOT edit the ADR — the ADR is the source of truth for the decision-noun).

**Checkpoint**: US2 delivered — the security engineer procurement-justification reader can follow SKILL.md ↔ ADR-025 cross-reference with confidence that the decision noun is consistent.

---

## Phase 5: User Story 3 — CISO Audit Preparation (Priority: P1)

**Goal**: A CISO preparing tachi-derived security-posture material for a regulatory audit opens `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` and finds either (Option A) a complete mapping table covering all 8 tachi compensating-control categories, or (Option B/C) a one-paragraph relationship-only stub naming the wired-integration site and linking to a follow-on Issue. Either shape resolves the audit-preparation need without requiring a hand-rolled crosswalk.

**Independent Test**: After task completion, `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` exists, its content shape matches the chosen option, and it links to ADR-025 by relative path.

### Implementation for User Story 3

- [X] T016 [US3] Create `/Users/david/Projects/tachi/.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`. File content shape depends on the decision-noun finalized in T013:
  - **If Option A (`documentation-only mapping`)**: file contains the **complete mapping** — (1) a mapping table covering all 8 tachi compensating-control categories (authentication, input-validation, rate-limiting, encryption, logging-audit, csrf-protection, csp-security-headers, access-control) to their NIST AI RMF Subcategory equivalents with Overlap / Gap / Conflict / "No equivalent" labels; (2) the Surface C crosswalk (12 GAI risks → 11 STRIDE+AI categories); (3) a back-link to ADR-025 by relative path `../../../../docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md`. This file becomes the canonical mapping artifact.
  - **If Option B (`shallow wired integration`) or Option C (`deep wired integration`)**: file contains a **one-paragraph relationship-only stub** naming the wired-integration site (for B: "controls schema field extension"; for C: "new NIST AI RMF analyzer agent") + forward link to the follow-on implementation Issue (to be filed in T024) + back-link to ADR-025 by relative path.
  - In all cases, the file MUST: (a) exist post-merge, (b) link to ADR-025 by relative path, (c) be additive only (does NOT modify any existing tachi-shared reference per ADR-023 additive-only invariant), (d) be renderable in standard Markdown without GFM extensions (plain headings, tables, links — no collapsed details blocks or Mermaid).
- [X] T017 [US3] Verify `nist-ai-rmf-mapping.md` exists and contains a relative-path link to ADR-025 (SC-008). Run:
  ```bash
  [ -f /Users/david/Projects/tachi/.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md ] && \
    grep -E '\.\./.+ADR-025' /Users/david/Projects/tachi/.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md && \
    echo "SC-008 PASS" || { echo "SC-008 FAIL"; exit 1; }
  ```
  Manual reviewer inspection confirms content shape matches the chosen option (full mapping for Option A; relationship stub for Option B/C).

**Checkpoint**: US3 delivered — CISO audit-preparation reader can cite `nist-ai-rmf-mapping.md` alongside ADR-025 during a regulatory audit.

---

## Phase 6: User Story 4 — Maintainer Decision Traceability (Priority: P2)

**Goal**: A future tachi maintainer considering changes to the compensating controls analyzer or a new NIST-aware analyzer agent opens ADR-025 and finds ≥3 options enumerated in Alternatives Considered, each with pros/cons/effort/compliance-value/rationale. They use the ADR to evaluate whether their proposed change is consistent with prior reasoning or is a deliberate reversal.

**Independent Test**: After task completion, ADR-025's Alternatives Considered section lists at least three options (A docs-only / B shallow wired / C deep wired — optional hybrid). Each option has Pros, Cons, Effort estimate (S/M/L with day range), Compliance Value, Determinism Impact, and Why-Chosen|Why-Not-Chosen rationale. The Status field reads `Accepted`. The Related ADRs line is bidirectional with ADR-024.

### Implementation for User Story 4

- [X] T018 [US4] Draft ADR-025 Rationale section in `/Users/david/Projects/tachi/docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md`. Justification MUST address all five evaluation criteria (maturity, adoption, compatibility, effort, compliance value) AND MUST explicitly compare against ADR-024's reasoning (companion-framework precedent). Per spec Assumption "Pre-1.0 maturity does not auto-default to diverge" — NIST AI RMF 1.0 is stable, so the recommendation is reasoned afresh from FR-002 mapping + five criteria (not inherited from ADR-024's divergence logic). Include explicit sector-specific compliance-value references (SOC 2, FedRAMP, HIPAA, FFIEC, EU AI Act) per US2 AC-3.
- [X] T019 [US4] Draft ADR-025 Alternatives Considered — **Option A: Documentation-only mapping** in the same file. Include: Pros, Cons, Effort estimate (typically "S: ~0 additional effort beyond this ADR and FR-007 artifact"), Compliance Value for Regulated Adopters, Pipeline Determinism Impact (none — no schema / agent / script changes), and Why-Chosen|Why-Not-Chosen rationale. Option A is: new file at `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` containing full mapping; no schema/agent/script changes.
- [X] T020 [US4] Draft ADR-025 Alternatives Considered — **Option B: Shallow wired integration** in the same file. Include: Pros, Cons, Effort estimate (typically "M: ~2-4 days; additive schema field, control-analyzer agent + PDF template update, backward compatible when tags absent"), Compliance Value, Pipeline Determinism Impact (additive — no new determinism sensitivity), and Why-Chosen|Why-Not-Chosen rationale. Option B is: extend a controls schema to optionally reference NIST AI RMF Subcategories on compensating controls; update control-analyzer agent and PDF security report; backward compatible when tags absent.
- [X] T021 [US4] Draft ADR-025 Alternatives Considered — **Option C: Deep wired integration** in the same file. Include: Pros, Cons, Effort estimate (typically "L: ~6-10 days; new agent, new schema, new template page, new pipeline phase, example regen required"), Compliance Value, Pipeline Determinism Impact (new pipeline phase — determinism must be preserved per ADR-021), and Why-Chosen|Why-Not-Chosen rationale. Option C is: new agent at `.claude/agents/tachi/nist-ai-rmf-analyzer.md` that runs after the compensating-controls analyzer and produces a dedicated NIST AI RMF coverage report. A hybrid B+C option MAY be added if research surfaces it (per FR-003 "additional options permitted" clause).
- [X] T022 [US4] Draft ADR-025 Consequences + When to Re-Evaluate + References sections in the same file. Consequences MUST distinguish: if Option B or C chosen, name the follow-on implementation feature and link to its follow-on Issue (populated in T024); if Option A chosen, name the Mapping reference location and maintenance commitment ("updated when NIST AI RMF publishes a new revision"). When to Re-Evaluate trigger MUST be concrete — e.g., "≥3 regulated-industry adopter inquiries" OR "NIST AI RMF 2.0 publication" OR "SP 800-53 AI overlay GA" (per PRD Risk R2 mitigation). References MUST include: (a) internal (PRD 144, ADR-024, ADR-020, ADR-019, ADR-018, ADR-021, ADR-023, tachi pipeline phase doc, control-categories.md, stride-categories-shared.md), (b) external (NIST canonical URLs: `https://www.nist.gov/itl/ai-risk-management-framework`, `https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf`, `https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf`, DOI `https://doi.org/10.6028/NIST.AI.600-1`).
- [X] T023 [US4] Append ADR-025 back-reference to the existing ADR-024 Related ADRs line in `/Users/david/Projects/tachi/docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md`. Single-line edit: locate the existing `**Related ADRs**:` line in the frontmatter block and append `, [ADR-025](ADR-025-nist-ai-rmf-evaluation.md) (companion NIST AI RMF evaluation)`. Do NOT modify ADR-024's Status field (this is a housekeeping edit per existing tachi convention — SC-011 verifier checks only that the ADR-025 reference appears, not that the Status field changed). Completes bidirectional cross-reference per spec Closed-at-Approval Q4.

**Checkpoint**: US4 delivered — maintainer sees all three options with full pros/cons/effort/compliance-value/rationale; Status: Accepted enforced; Related ADRs line bidirectional with ADR-024.

---

## Phase 7: User Story 5 — Unregulated Adopter Non-Disruption (Priority: P1)

**Goal**: An unregulated adopter running `/tachi.threat-model` and `/tachi.compensating-controls` against their existing architecture post-ADR-025-merge gets byte-identical `threats.md`, `risk-scores.md`, `compensating-controls.md` outputs, and 5/5 byte-identical PDF baselines under `SOURCE_DATE_EPOCH=1700000000` per ADR-021. Non-disruption is a hard Constitution III invariant.

**Independent Test**: `pytest tests/scripts/test_backward_compatibility.py` returns 5/5 passing under `SOURCE_DATE_EPOCH=1700000000`. `git diff main..HEAD -- schemas/ scripts/ .claude/agents/ examples/` returns empty.

### Implementation for User Story 5

- [X] T024 [US5] Run zero-drift verification on the four forbidden directories (SC-006). Execute:
  ```bash
  cd /Users/david/Projects/tachi && \
    git diff main..HEAD -- schemas/ scripts/ .claude/agents/ examples/
  ```
  Output MUST be empty. If any file under those four directories has been modified, revert the change or escalate for PM / Architect review. This is the **scope-discipline invariant** — documentation-only constraint preserved across all 5 Constitution NON-NEGOTIABLE principles that apply (I, III, VII, IX, X).
- [X] T025 [US5] Run existing backward-compatibility pytest suite (SC-010) — all 5 baseline PDFs must remain byte-identical under `SOURCE_DATE_EPOCH=1700000000` per ADR-021. Execute:
  ```bash
  cd /Users/david/Projects/tachi && \
    SOURCE_DATE_EPOCH=1700000000 python -m pytest tests/scripts/test_backward_compatibility.py -v
  ```
  All 5 must pass. Any failure is a red flag for hidden scope drift — escalate immediately.

**Checkpoint**: US5 delivered — unregulated adopter's Constitution III invariant preserved; zero unintended drift on the four forbidden scopes.

---

## Phase 8: Conditional Follow-on Issue (FR-008)

**Goal**: If ADR-025 Decision is Option B (shallow wired) or Option C (deep wired), file a follow-on implementation Issue with `stage:discover` label referencing ADR-025. If Decision is Option A (documentation-only), file no Issue.

**Note**: This phase is conditional. T026 is the branching task; T027 and T028 are mutually exclusive. Per architect plan review C1 MEDIUM: T027 explicitly depends on ADR-025 Alternatives Considered section being **finalized** (T018-T021 complete) so the effort estimate string can be copied **verbatim**.

- [X] T026 Read the final Decision section of `/Users/david/Projects/tachi/docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md` and extract the canonical decision-noun. If decision-noun is `documentation-only mapping`, execute T028 and skip T027. If decision-noun is `shallow wired integration`, `deep wired integration`, or `hybrid BC`, execute T027 and skip T028.
- [~] T027 (conditional, Option B or C or hybrid only) File a follow-on implementation Issue via `bash /Users/david/Projects/tachi/.aod/scripts/bash/create-issue.sh`. **Dependency**: T018-T021 (Alternatives Considered sections for Options A/B/C) MUST be complete and finalized — the effort estimate string for the chosen option is copied **verbatim** from ADR-025 Alternatives Considered (per architect plan review C1 MEDIUM). Required Issue fields: (a) `stage:discover` label; (b) concrete title — e.g., "Implement NIST AI RMF compensating-control tagging (per ADR-025)" for Option B; "Implement NIST AI RMF coverage analyzer agent (per ADR-025)" for Option C; "Implement NIST AI RMF hybrid tagging + analyzer (per ADR-025)" for hybrid B+C; (c) body that (i) links back to ADR-025 by relative path, (ii) names **3-5 surfaces** that would change in implementation — for Option B: `schemas/finding.yaml` or new controls schema, `.claude/agents/tachi/control-analyzer.md`, `templates/tachi/security-report/**.typ`, example regen; for Option C: new `.claude/agents/tachi/nist-ai-rmf-analyzer.md`, new schema, new template page, new pipeline phase, example regen; (iii) includes the **option-specific effort estimate** copied verbatim from ADR-025 Alternatives Considered for the chosen option; (iv) explicitly names "non-disruptive" or "opt-in" as a constraint (per US5 AC-3 — carries the unregulated-adopter invariant forward into the wired implementation). After filing, record the Issue number and update ADR-025 Consequences section with the follow-on Issue link (closes the Consequences "Follow-on" sub-bullet introduced in T022).
- [X] T028 (conditional, Option A only) Record in PR description: "Decision: Option A (documentation-only mapping). No follow-on implementation Issue filed per FR-008 conditionality. ADR-025 Consequences section instead cites the `nist-ai-rmf-mapping.md` maintenance commitment and the `## When to Re-Evaluate` trigger." [PR body text to be placed at T043 PR creation]

**Checkpoint**: Phase 8 correctness verified — conditional logic respected (Issue exists iff Decision is B, C, or hybrid; Issue absent iff Decision is A). SC-009 conditional pass.

---

## Phase 9: Polish & Final Verification

**Purpose**: Verify all 13 success criteria, confirm scope-discipline invariants, and prepare for PR.

- [X] T029 [P] Verify ADR-025 file exists at canonical path (SC-001):
  ```bash
  [ -f /Users/david/Projects/tachi/docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md ] && echo "SC-001 PASS"
  ```
- [X] T030 [P] Verify ADR-025 Status field reads exactly `Accepted` (SC-002):
  ```bash
  grep -cE '^\*\*Status\*\*: Accepted$' /Users/david/Projects/tachi/docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md
  ```
  Must return exactly `1`. Update `**Date**: <merge-date-placeholder>` to actual YYYY-MM-DD merge date before squash-merge.
- [X] T031 [P] Verify ADR-025 contains exactly three Surface anchor tags (SC-003):
  ```bash
  grep -c '<a id="surface-[abc]"></a>' /Users/david/Projects/tachi/docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md
  ```
  Must return exactly `3`.
- [X] T032 [P] Manual reviewer inspection for SC-004 — confirm no "TBD", "unclear", or empty relationship labels in Surface A, B, C. Every row uses exactly one of: Overlap, Gap, Conflict, "No equivalent". Re-run T012 audit if any ambiguous cell discovered.
- [X] T033 [P] Verify SKILL.md NIST AI RMF Relationship section word count is in `[80, 200]` (SC-005):
  ```bash
  WC=$(awk '/^## NIST AI RMF Relationship/{flag=1; next} /^## /{flag=0} flag' \
    /Users/david/Projects/tachi/.claude/skills/tachi-control-analysis/SKILL.md | wc -w)
  [ "$WC" -ge 80 ] && [ "$WC" -le 200 ] && echo "SC-005 PASS ($WC words)" || { echo "SC-005 FAIL: $WC words"; exit 1; }
  ```
- [X] T034 [P] Re-run zero-drift git diff on the four forbidden directories (SC-006). Same command as T024 — must remain empty:
  ```bash
  cd /Users/david/Projects/tachi && \
    git diff main..HEAD -- schemas/ scripts/ .claude/agents/ examples/
  ```
- [X] T035 [P] Re-run SC-007 decision-noun byte-equality with non-empty guard. Same command as T015 — must pass with `[ -n "$ADR_NOUN" ]` guard satisfied.
- [X] T036 [P] Verify `nist-ai-rmf-mapping.md` exists at canonical path (SC-008) — same check as T017.
- [X] T037 [P] Verify conditional follow-on Issue status (SC-009):
  - If Option B / C / hybrid chosen in T013: `gh issue list --label stage:discover --search "ADR-025"` must return ≥1 result.
  - If Option A chosen: absence of `stage:discover` "ADR-025" Issue is correct (SC-009 passes as N/A per T028).
- [X] T038 [P] Re-run backward-compatibility pytest suite (SC-010) — same as T025, confirm 5/5 byte-identical under `SOURCE_DATE_EPOCH=1700000000`.
- [X] T039 [P] Verify ADR-024 back-reference edit (SC-011):
  ```bash
  grep -cE 'ADR-025' /Users/david/Projects/tachi/docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md
  ```
  Must return ≥1 match (expected on the Related ADRs line).
- [X] T040 [P] Verify all commits on the feature branch use `docs:` conventional commit prefix (SC-012):
  ```bash
  cd /Users/david/Projects/tachi && \
    git log main..144-nist-ai-rmf-evaluation-adr --pretty=%s | grep -vE '^docs(\(.+\))?:'
  ```
  Output MUST be empty (no non-`docs:` commits). If any commit uses `feat:` or `fix:`, rebase to reword it.
- [X] T041 [P] Record Wave 1 timebox outcome in delivery retrospective (SC-013). Note in PR description: "Wave 1 NIST AI RMF research completed within 3-hour timebox" OR "Wave 1 escalated to PM at hour 3 with contingency option {a|b|c} chosen — see research.md Wave 1 section for rationale." Captured for `/aod.deliver` retrospective. [Content drafted for T043 PR body]
- [X] T042 [P] Verify no new runtime dependencies were added (plan Constraints + Constitution III):
  ```bash
  cd /Users/david/Projects/tachi && \
    git diff main..HEAD -- pyproject.toml requirements-dev.txt package.json
  ```
  Must be empty.
- [X] T043 Open pull request with conventional commit title `docs(144): MAESTRO Companion — NIST AI RMF evaluation ADR` per Constitution IX + SC-012. PR body must: (a) link to ADR-025 once committed on `main`; (b) summarize the three-surface comparison in 2-3 bullets (one per Surface A / B / C); (c) state the recommended option (decision-noun from T013); (d) cite the zero-drift assertion output from T034 as evidence; (e) list the follow-on Issue number from T027 if filed, OR "no follow-on Issue filed — Option A (docs-only)" if T028 path taken; (f) include the `pytest test_backward_compatibility.py` 5/5 PASS line from T038.
- [X] T044 Architect final review on PR — APPROVED verdict serves as the "Accepted at merge" attestation (closed-at-approval Q2 from PRD + spec Assumption "architect approval = ADR Accepted attestation"). Before squash-merge, update `**Date**: <merge-date-placeholder>` in ADR-025 to the actual YYYY-MM-DD merge date. No separate ADR-only review ceremony. **Contingency**: if the PR is rejected and re-work is required, revert ADR-025 Status to `Proposed` before the next revision cycle and restore to `Accepted` only after the next architect APPROVED verdict — this preserves literal consistency between the Status marker and the actual lifecycle state. [APPROVED 2026-04-16 — see .aod/results/architect-pr-review-144.md]

**Checkpoint**: All 13 success criteria (SC-001 through SC-013) verified. Feature ready for merge.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies. Can start immediately.
- **Phase 2 (Foundational — NIST Research)**: Depends on Phase 1. **BLOCKS** all authorship phases. **3-hour timebox** on T003+T004+T005+T006 combined with PM escalation + 3 contingency options (descope Surface B / defer FR-007 / escalate).
- **Phase 3 (US1 MVP)**: Depends on Phase 2. Once Phase 3 completes, MVP is delivered (compliance officer can answer NIST mapping from ADR-025 alone).
- **Phase 4 (US2)**: Depends on Phase 3 (ADR-025 Decision section must exist with canonical noun before SKILL.md cross-reference is written). T014 must come AFTER T013.
- **Phase 5 (US3)**: Depends on Phase 3 (knowledge of chosen option determines file content shape). T016 content-shape branching depends on T013 decision-noun.
- **Phase 6 (US4)**: Depends on Phase 3 (ADR-025 file exists with Context before Alternatives Considered makes sense). T018-T022 + T023 write to ADR-025 and ADR-024; serialize by single writer.
- **Phase 7 (US5)**: Zero-drift verification — depends on all prior phases being complete (to catch accidental drift). T024 + T025 can run after all Wave 2 edits land.
- **Phase 8 (Conditional Issue)**: Depends on Phase 6 completion — per architect plan review C1 MEDIUM, T027 Issue filing depends on ADR-025 Alternatives Considered being **finalized** so the effort estimate string can be copied verbatim. T027 vs T028 is mutually exclusive.
- **Phase 9 (Polish)**: Depends on all prior phases. Verification gates T029-T042 are parallelizable.

### User Story Dependencies

- **US1 (P1 MVP)**: Delivers on its own as MVP. No dependency on US2/US3/US4/US5.
- **US2 (P1)**: Depends on US1 (needs ADR-025 Decision finalized before SKILL.md byte-equality check is meaningful).
- **US3 (P1)**: Depends on US1 (needs decision-noun to determine `nist-ai-rmf-mapping.md` content shape).
- **US4 (P2)**: Depends on US1 (needs ADR-025 frontmatter + Context before Alternatives Considered and Rationale make sense).
- **US5 (P1)**: Depends on US1-US4 completion (zero-drift check must cover all writes).

### Within Each User Story

- Models-before-services / services-before-endpoints is NOT applicable (no code path).
- Frontmatter before prose — T007 must complete before T008+.
- Decision (T013) is the canonical noun anchor — all subsequent SKILL.md (T014), mapping reference (T016), and Issue body (T027) writes reference back to T013's chosen noun.
- Context before Alternatives Considered before Consequences — natural ADR narrative order.
- ADR-025 Status must be `Accepted` at merge (enforced twice: T007 frontmatter authoring + T030 verification grep).

### Parallel Opportunities

- T003 → T004 → T005 → T006 are sequential for the same web-researcher within the 3-hour timebox (cross-references build incrementally).
- T009, T010, T011 (Surfaces A/B/C drafting) — same writer, same file; serialize writes but can draft content in parallel editor panes.
- T019, T020, T021 (Alternatives A/B/C drafting) — same writer, same file; serialize writes but can draft in parallel editor panes.
- T026 is a decision branch; T027 and T028 are mutually exclusive and cannot be parallelized.
- T029 through T042 (verification gates) can run in parallel — each reads different files and emits independent pass/fail signals. All marked [P].

---

## Parallel Example: Phase 9 Verification Gates

```bash
# Launch all verification gates in parallel (each reads different files, no write-ordering):
Task: "Run SC-001 file-exists check (T029)"
Task: "Run SC-002 Status: Accepted grep (T030)"
Task: "Run SC-003 Surface anchor grep (T031)"
Task: "Manual SC-004 relationship-label inspection (T032)"
Task: "Run SC-005 SKILL.md word count (T033)"
Task: "Run SC-006 zero-drift git diff (T034)"
Task: "Run SC-007 decision-noun byte-equality (T035)"
Task: "Run SC-008 mapping-reference existence (T036)"
Task: "Run SC-009 conditional follow-on Issue check (T037)"
Task: "Run SC-010 backward-compat pytest (T038)"
Task: "Run SC-011 ADR-024 back-reference grep (T039)"
Task: "Run SC-012 docs: commit prefix check (T040)"
Task: "Record SC-013 Wave 1 timebox outcome (T041)"
Task: "Run no-new-deps check (T042)"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1: Setup (context loaded, branch confirmed)
2. Complete Phase 2: Foundational (NIST research done, within 3-hour timebox or contingency chosen)
3. Complete Phase 3: US1 — ADR-025 frontmatter + Context + Surfaces A/B/C + Decision canonical noun
4. **STOP and VALIDATE**: Compliance-officer reader test — opens ADR-025, can answer "does tachi map to NIST AI RMF?" in one paragraph; three Surface anchors exist; every row labeled
5. If MVP is enough for the compliance-officer journey alone, jump directly to Phase 9 verification gates and commit — US1 alone delivers primary product value

### Incremental Delivery (Full Feature)

1. Complete Setup + Foundational → research ready
2. Complete US1 (Phase 3) → compliance-officer journey works (MVP)
3. Complete US2 (Phase 4) → security-engineer procurement-justification journey works (SKILL.md byte-equality)
4. Complete US3 (Phase 5) → CISO audit-preparation journey works (mapping reference)
5. Complete US4 (Phase 6) → maintainer decision-traceability journey works (Alternatives + Consequences + ADR-024 back-reference)
6. Complete US5 (Phase 7) → unregulated-adopter non-disruption invariant preserved
7. Complete Phase 8 (conditional Issue) → follow-on work anchored if decision is B / C / hybrid; skipped if A
8. Complete Phase 9 (polish + gates) → 13/13 SCs verified, ready for PR
9. Open PR (T043) → architect approval (T044) → squash-merge to `main`

### Parallel Team Strategy (Not Applicable)

Single-writer ADR authorship preserves voice consistency. Parallelization is at the verification-gate layer (Phase 9 gates run in parallel, 14 gates) and the content-drafting layer (Surfaces A/B/C and Alternatives A/B/C drafted in parallel editor panes by one writer). Multi-writer parallelism would introduce merge conflicts on the shared ADR-025 file with no throughput benefit.

---

## Notes

- **[P] tasks = different files, no write-ordering conflict.** Most tasks share one file (ADR-025) or operate on different read targets — [P] is sparingly applied (concentrated in Phase 9 verification gates).
- **[Story] label** maps tasks to user stories (US1 → MVP, US2 → procurement, US3 → audit prep, US4 → maintainer, US5 → non-disruption). Setup (Phase 1), Foundational (Phase 2), Conditional Issue (Phase 8), and Polish (Phase 9) phases do not carry [Story] labels per the governance rule.
- **Each user story is independently verifiable** through reader-facing tests (the "Independent Test" checkpoint under each phase heading) — not through separately shippable code slices.
- **Two-wave structure** (research Wave 1 + authorship Wave 2) matches PRD Milestone table and Team-Lead assignment.
- **Stop at any checkpoint to validate story independently** — US1 MVP validates at end of Phase 3; full feature validates at end of Phase 9.
- **Decision-noun discipline**: T013 is the single source of truth for the canonical decision-noun. All subsequent noun references (T014 SKILL.md, T016 mapping reference, T027 Issue body) MUST match T013 byte-identically (modulo case, per SC-007).
- **Non-empty guard (SC-007)**: Per architect plan review C2 MEDIUM, the SC-007 verifier includes `[ -n "$ADR_NOUN" ]` guard to prevent a both-empty false-PASS. See T015 and T035.
- **FR-008 conditional task ordering**: Per architect plan review C1 MEDIUM, T027 follow-on Issue filing is explicitly dependent on T018-T021 Alternatives Considered being finalized so the effort estimate string can be copied verbatim from ADR-025.
- **Avoid**: vague tasks (every task has a file path + grep assertion + shell verifier), cross-story file conflicts (mitigated by single-writer convention for shared ADR-025), scope drift (Phase 7 + T034 zero-drift gate enforces this), non-`docs:` commit prefix (T040 gate enforces this), `Proposed`-status merge (T030 gate enforces this).
