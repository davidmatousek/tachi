---
prd_reference: docs/product/02_PRD/143-maestro-aivss-evaluation-adr-2026-04-14.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-15
    status: APPROVED
    notes: "Exemplary spec — all 7 PRD FRs covered, all 4 USs preserved with priority ordering, all four LOW-concern items (PM C1, PM C3, Architect LOW-4, Team-Lead Rec #2) resolved inline, five-layer scope discipline (FR-008 + SC-006 + Constraints + Out-of-Scope + Assumptions), zero drift gates, SC-008 correctly encodes conditional success for follow-on Issue. 4 minor non-blocking observations recorded in .aod/results/product-manager.md. Ready for plan.md."
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: MAESTRO Phase 4 — OWASP AIVSS Evaluation ADR

**Feature Branch**: `143-maestro-aivss-evaluation-adr`
**Created**: 2026-04-15
**Status**: Draft
**Input**: User description: "PRD: 143 - maestro-aivss-evaluation-adr"
**PRD**: [docs/product/02_PRD/143-maestro-aivss-evaluation-adr-2026-04-14.md](../../docs/product/02_PRD/143-maestro-aivss-evaluation-adr-2026-04-14.md)
**Parent Discovery**: [#143](https://github.com/davidmatousek/tachi/issues/143) (umbrella MAESTRO discovery [#136](https://github.com/davidmatousek/tachi/issues/136))

## Overview

This is a **documentation-only ADR spike**: evaluate OWASP AIVSS against tachi's four-dimensional composite score and commit the decision as **ADR-024** — adopt as primary, adopt as supplementary field, or document divergence with rationale. Add a 80-200 word AIVSS Relationship section to the tachi-risk-scoring skill file reflecting the decision. If the decision is "adopt", file a follow-on implementation feature as a separate GitHub Issue. **Zero production code changes** — no schemas, scripts, agents, or example outputs are modified in this feature.

Feature 143 is the fourth and final phase of the MAESTRO compliance initiative (Phases 1-3 delivered in PRDs 136, 141, 082). After 143 closes, the umbrella MAESTRO compliance discovery [#136](https://github.com/davidmatousek/tachi/issues/136) can be closed.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - CISO Procurement Brief via Single Linkable ADR (Priority: P1)

A CISO evaluating tachi for organizational adoption needs to brief their team on tachi's scoring methodology in one paragraph with a clear citation to the public OWASP AIVSS standard. Today they must read the risk-scoring schema plus the tachi-risk-scoring skill files to answer "is this AIVSS-aligned?" — and even then, there is no documented stance to cite. This feature closes that gap with a single linkable ADR that states tachi's relationship with AIVSS explicitly.

**Why this priority**: This is the feature's primary product value — a CISO or procurement reviewer must be able to answer "does tachi align with AIVSS?" in under five minutes by reading one file. Without this, every procurement evaluation becomes a reverse-engineering exercise or a guess. No other user story can replace this one as the MVP delivery.

**Independent Test**: Verifiable by opening [ADR-024](../../docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md) in a plain Markdown viewer after merge: the Decision section's first paragraph must answer the alignment question without requiring the reader to open any other file.

**Acceptance Scenarios**:

1. **Given** ADR-024 is committed and merged with `Status: Accepted`, **when** a CISO opens the file at `docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md`, **then** the Decision section's first paragraph answers "does tachi align with AIVSS?" without referring the reader to additional files
2. **Given** the ADR is committed, **when** the CISO follows the cross-reference from [.claude/skills/tachi-risk-scoring/SKILL.md](../../.claude/skills/tachi-risk-scoring/SKILL.md), **then** the AIVSS Relationship paragraph in SKILL.md reflects the same decision as ADR-024 (no contradiction between the two surfaces — verified by at least one decision-noun token appearing in both, e.g., both say "diverge" or both say "adopt")
3. **Given** the CISO copies the ADR URL into a procurement brief, **when** they do so, **then** the URL points to a stable file path matching `docs/architecture/02_ADRs/ADR-024-*.md` on the `main` branch (not a draft, not a PR URL, not a review comment)

---

### User Story 2 - Compliance Officer Report-vs-Translate Decision (Priority: P1)

A compliance officer at a regulated organization must decide whether to report tachi scores directly to regulators (SOC 2, FedRAMP, EU AI Act, sector-specific) or translate them into AIVSS format. Today the compliance officer has no documented dimension mapping to work from — they must either commission a manual crosswalk or make the decision based on guesswork. This feature delivers a three-surface side-by-side comparison (dimensions, composite formula, severity bands) so the report-vs-translate decision is grounded in documented alignment.

**Why this priority**: Compliance value is one of the five evaluation criteria in the Rationale section and the primary driver for adopters in regulated industries. A dimension-only comparison would hide formula and band divergence that produces different scores for the same finding — the three-surface comparison is the compliance officer's decision tool.

**Independent Test**: Verifiable by a compliance officer reading ADR-024's Context section: the three surface tables (Surface A dimensions, Surface B formula weights, Surface C severity bands) are present, every row is annotated with a relationship label (Overlap / Gap / Conflict / No equivalent), and no "TBD" or "unclear" labels remain.

**Acceptance Scenarios**:

1. **Given** ADR-024 is committed, **when** the compliance officer reads the Context section, **then** three distinct Markdown tables (or three subsections) are present: Surface A (Dimension Set), Surface B (Composite Formula Weights), Surface C (Severity Band Thresholds)
2. **Given** the three tables exist, **when** the officer reads each row, **then** every row is labeled with exactly one of: **Overlap** (dimensions measure the same thing), **Gap** (one framework measures something the other does not), **Conflict** (same name, different meaning), or **No equivalent** (the other framework does not include this surface)
3. **Given** the recommended decision is "diverge", **when** the officer reads the Rationale section, **then** at least two worked examples quantify a finding where AIVSS would produce a measurably different score than tachi (both scores numerically stated)

---

### User Story 3 - Future Maintainer Decision Traceability (Priority: P2)

A future tachi maintainer considering changes to the scoring pipeline needs to find a single ADR that documents the original AIVSS decision with the options that were considered, so they can evaluate whether a proposed change is consistent with prior reasoning or constitutes a deliberate reversal. Without the ADR, future scoring changes risk silently diverging from MAESTRO practitioner expectations.

**Why this priority**: Traceability is an architectural-invariant concern, not a customer-visible feature. It matters at future decision points but does not directly block any current stakeholder. P2 reflects this — important, but not the primary deliverable.

**Independent Test**: Verifiable by grepping `docs/architecture/02_ADRs/` for "AIVSS" and confirming ADR-024 is the only ADR whose Decision section addresses AIVSS directly.

**Acceptance Scenarios**:

1. **Given** ADR-024 is committed, **when** a future maintainer searches `docs/architecture/02_ADRs/` for "AIVSS", **then** ADR-024 is the only ADR whose Decision section addresses AIVSS (other ADRs may mention AIVSS only via cross-reference to ADR-024 — those are permitted)
2. **Given** ADR-024 is committed, **when** the maintainer reads the Alternatives Considered section, **then** at least three options are enumerated (adopt as primary, adopt as supplementary field, document divergence) with Pros, Cons, and a "Why Not Chosen" (for rejected options) or "Why Chosen" (for the recommended option) rationale for each
3. **Given** the ADR is committed, **when** the maintainer reads the Status field in the frontmatter, **then** it reads `**Status**: Accepted` (not `Proposed`) at merge time — verified by a grep assertion in post-merge validation

---

### User Story 4 - Security Engineer Dimension Crosswalk (Priority: P2)

A security engineer comparing agentic threat modeling tools must explain tachi's composite risk score to stakeholders who already know AIVSS. Without an explicit dimension-by-dimension mapping in a public artifact, the engineer must invent their own crosswalk — which is error-prone and not durable across tachi releases.

**Why this priority**: Useful for tool-comparison workflows but serves a narrower audience than the CISO (US1) or compliance officer (US2). A competent engineer can answer it once US2's Surface A table exists — US4 mostly asserts the table's shape and anchor-link usability.

**Independent Test**: Verifiable by the security engineer copying the URL with an anchor to the Surface A table heading and opening it in another browser — the anchor must resolve directly to the mapping table heading.

**Acceptance Scenarios**:

1. **Given** ADR-024 is committed, **when** the engineer reads Surface A, **then** each tachi dimension (CVSS 3.1 base, exploitability, reachability, scalability) is mapped to either a specific AIVSS dimension, a combination of AIVSS dimensions, or explicitly "no AIVSS equivalent" (no row left ambiguous)
2. **Given** the engineer needs to cite the mapping in external documentation, **when** they copy the Surface A section URL with a heading anchor, **then** the anchor resolves directly to the Surface A heading in a standard Markdown viewer
3. **Given** the mapping table is committed, **when** the engineer reads it, **then** the CVSS version gap is explicitly called out (tachi uses CVSS 3.1; AIVSS v0.8 builds on CVSS v4.0 — this is a Conflict row, not an Overlap row)

---

### Edge Cases

- **AIVSS canonical home has restructured** (PRD Risk R1): If the published AIVSS spec cannot be located within a 2-hour timebox on first research task, the implementer pauses and escalates to PM for a close-without-delivery decision. The fallback is replacing this PRD with a new PRD covering the successor framework (if one exists).
- **AIVSS is pre-1.0 at research time** (PRD Risk R2): If AIVSS has no stable 1.0, the ADR explicitly says so, captures the observed version (at time of research, AIVSS v0.8 with public review period opening 2026-04-16), and defaults to Option C (document divergence) with a "When to Re-Evaluate" trigger tied to AIVSS 1.0 publication plus at least one external adopter case study.
- **AIVSS dimensions fully overlap with tachi dimensions** (unlikely per research — AARS is agentic-specific, tachi's scalability is automation-agnostic): If Surface A shows complete dimension overlap but Surfaces B and C diverge, the three-surface shape still prevents an incorrect "all aligned" conclusion — the ADR must state the formula/band divergence explicitly.
- **Mapping reveals a bug in tachi's composite** (PRD Risk R4): If dimension comparison surfaces a methodological flaw in tachi's composite (e.g., missing dimension; double-counting), this PRD documents it and files a separate corrective Issue. This PRD's scope does not change — the flaw becomes a new discovery item.
- **Reviewer disagreement on the recommended option** (PRD Risk R3): Up to 5 review iterations are available before escalation to user. Reviewers can challenge the weighting of the five evaluation criteria (maturity, adoption, compatibility, effort, compliance value) rather than the conclusion.
- **Decision changes between draft and merge**: If the implementer's recommended option changes during review (e.g., draft says Option C, reviewer argues for Option B and wins consensus), the SKILL.md paragraph must be updated to match the final ADR decision before merge — verified by the single-source-of-truth grep check (see SC-007).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST capture the current OWASP AIVSS specification as read end-to-end, including the observed version number (handle pre-1.0 cases explicitly), canonical specification URL, dimension list, severity band thresholds if defined, and composite formula if defined. The version number recorded in ADR-024 MUST match the specification version observed at research time (date-stamped).

- **FR-002**: System MUST produce a three-surface side-by-side comparison in the ADR Context section. A dimension-only mapping is insufficient because it can hide divergence in formula shape and band thresholds:
  - **Surface A — Dimension Set**: one row per tachi composite dimension (CVSS 3.1 base, exploitability, reachability, scalability), mapped to AIVSS equivalents
  - **Surface B — Composite Formula Weights**: tachi's `(0.35 × CVSS) + (0.30 × Exploitability) + (0.20 × Reachability) + (0.15 × Scalability)` versus the AIVSS composite formula (or "no AIVSS equivalent" if none is defined)
  - **Surface C — Severity Band Thresholds**: tachi's Critical / High / Medium / Low cutoffs versus AIVSS bands (or "no AIVSS equivalent" if AIVSS does not define bands)

  Every row in Surface A MUST be labeled with exactly one of: Overlap, Gap, Conflict, or No equivalent. Surfaces B and C MUST be included even if AIVSS lacks a published composite formula or severity bands (the "No equivalent" annotation is the correct response in that case). Conflicts (same name, different meaning) MUST be called out with a one-line explanation. The mapping MUST NOT silently elide formula-or-band divergence behind a "dimensions overlap" headline.

- **FR-003**: System MUST enumerate at least three decision options in the ADR Alternatives Considered section:
  - **Option A — Adopt AIVSS as primary scoring replacement**
  - **Option B — Adopt AIVSS as a supplementary field alongside the existing composite** (additive, no breaking change)
  - **Option C — Document divergence with rationale** (no schema change; ADR explains posture)

  Each option MUST include pros, cons, an option-specific effort estimate (S/M/L with rough day range), and a "Why Not Chosen" (rejected) or "Why Chosen" (recommended) rationale. Each option's compliance value for regulated adopters MUST be explicitly addressed. Additional options may be added if research surfaces them.

- **FR-004**: System MUST pick one recommended option in the ADR Decision section with a justification that addresses all five evaluation criteria: AIVSS maturity, adoption in the wild, compatibility with tachi's current composite, effort to wire in, and compliance value. If the recommended option is adopt (A or B), the Consequences section MUST name the follow-on implementation feature and link to its GitHub Issue (filed per FR-007). If the recommended option is diverge (C), the Rationale section MUST include at least two worked examples where AIVSS would produce a measurably different score than tachi for the same finding (with both scores numerically quantified).

- **FR-005**: System MUST commit the decision as ADR-024 in the existing ADR format at `docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md`. The ADR MUST use the section shape established by ADR-020 through ADR-023 (Context, Decision, Rationale, Alternatives Considered, Consequences as a minimum). The Status field MUST read `Accepted` at merge time (not Proposed). The Date field MUST reflect the merge date. The Related ADRs list in the frontmatter MUST include at minimum **ADR-020** (MAESTRO classification), **ADR-019** (shared cross-agent definitions — forward-looking for any follow-on), and **ADR-018** (baseline-aware pipeline, scoring lineage).

- **FR-006**: System MUST add a new `## AIVSS Relationship` section to [.claude/skills/tachi-risk-scoring/SKILL.md](../../.claude/skills/tachi-risk-scoring/SKILL.md) positioned **after `## Domain Overview` and before `## Baseline-Aware Scoring Rules`**. The paragraph MUST:
  - Be between 80 and 200 words
  - Reflect the ADR-024 decision in plain language without contradicting it (if ADR-024 says "diverge", SKILL.md must not imply alignment; verified by at least one decision-noun token appearing in both surfaces)
  - Contain an explicit relative-path link to ADR-024 (`../../docs/architecture/02_ADRs/ADR-024-*.md`)

- **FR-007**: System MUST conditionally file a follow-on implementation Issue **only if the recommended decision is Option A or Option B**. If filed:
  - Use `bash .aod/scripts/bash/create-issue.sh` with the `stage:discover` label
  - Issue title is concrete (e.g., "Implement OWASP AIVSS supplementary scoring (per ADR-024)")
  - Issue body links back to ADR-024 and **at minimum names the surfaces that would change in implementation** (3-5 bullet surface overview sufficient — e.g., `schemas/risk-scoring.yaml`, `.claude/skills/tachi-risk-scoring/references/`, `templates/tachi/**.typ`). Full ICE-scored breakdown is deferred to the follow-on PRD's own discovery cycle.
  - Issue body includes the **option-specific effort estimate copied verbatim** from ADR-024 Alternatives Considered (Option A and Option B have materially different effort profiles — A is a schema-breaking change with example regeneration; B is additive)
  - If the recommended decision is Option C, FR-007 is skipped entirely — no follow-on Issue is filed

- **FR-008**: System MUST preserve zero drift in scoring pipeline outputs. No files under `schemas/`, `scripts/`, `.claude/agents/`, or `examples/` may be modified. Verified by a post-merge `git diff main..feature-branch -- schemas/ scripts/ .claude/agents/ examples/` assertion returning empty. `README.md` and `docs/architecture/00_Tech_Stack/README.md` may only be modified if the ADR decision requires a cross-reference anchor link (a single-link change, not a content rewrite).

### Out-of-Scope Requirements (Explicitly Excluded)

- **No changes to `schemas/risk-scoring.yaml`** — schema evolution is the follow-on implementation's concern
- **No changes to any file under `.claude/agents/`** — agents are unchanged by this ADR
- **No changes to any file under `scripts/`** — runtime is unchanged
- **No regeneration of example outputs under `examples/`** — outputs are unchanged; backward-compatibility PDF baselines remain byte-identical under `SOURCE_DATE_EPOCH=1700000000` (ADR-021) trivially because no pipeline inputs change
- **No comparison to frameworks other than AIVSS** (DREAD, OWASP Risk Rating, FAIR) — this ADR is AIVSS-specific by PRD scope
- **No `feat:` or `fix:` commits** — documentation-only commits use `docs:` per Conventional Commits

### Key Entities *(include if feature involves data)*

- **ADR-024 document**: The new file at `docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md`. Key attributes: `Status: Accepted`, `Date: {merge date}`, Deciders (Architect, PM, Team-Lead), Related ADRs frontmatter line, Context with three surface comparison tables, Decision, Rationale, Alternatives Considered (≥3), Consequences, When to Re-Evaluate.

- **SKILL.md AIVSS Relationship section**: The new 80-200 word section in `.claude/skills/tachi-risk-scoring/SKILL.md` between Domain Overview and Baseline-Aware Scoring Rules. Key attribute: relative-path link to ADR-024; decision-noun consistency with ADR-024.

- **Follow-on implementation Issue (conditional)**: A new GitHub Issue with the `stage:discover` label, referenced from the ADR-024 Consequences section. Only exists if the decision is Option A or Option B.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md` exists on `main` after PR merge (boolean: 0 → 1)
- **SC-002**: The ADR-024 Status field reads `Accepted` at merge time — verified by `grep -c '^\*\*Status\*\*: Accepted' docs/architecture/02_ADRs/ADR-024-*.md` returning `1`
- **SC-003**: The ADR-024 Context section contains three labeled tables/subsections: Surface A (Dimension Set), Surface B (Composite Formula Weights), Surface C (Severity Band Thresholds), with every Surface A row annotated with exactly one of Overlap / Gap / Conflict / No equivalent
- **SC-004**: The ADR-024 Alternatives Considered section lists at least three options (primary, supplementary, diverge), each with Pros, Cons, an S/M/L effort estimate, and a "Why Not Chosen" / "Why Chosen" rationale
- **SC-005**: `.claude/skills/tachi-risk-scoring/SKILL.md` contains an `## AIVSS Relationship` section located after `## Domain Overview` and before `## Baseline-Aware Scoring Rules`, between 80 and 200 words long, containing a relative link to ADR-024
- **SC-006**: `git diff main..feature-branch -- schemas/ scripts/ .claude/agents/ examples/` returns empty — verified as the final gate before PR merge
- **SC-007**: The decision stated in SKILL.md matches ADR-024 — verified by at least one decision-noun token (e.g., `adopt`, `supplement`, `diverge`) appearing in both surfaces, with no contradictory phrasing
- **SC-008**: If the recommended decision is Option A or B, a new GitHub Issue exists on `github.com/davidmatousek/tachi/issues` with the `stage:discover` label and a body referencing ADR-024. If the decision is Option C, no such Issue is filed (success is correct conditionality — not unconditional existence)
- **SC-009**: ADR-024 cross-references at minimum ADR-020 (MAESTRO classification), ADR-019 (shared cross-agent definitions), and ADR-018 (baseline-aware pipeline) in its frontmatter Related ADRs list

### Assumptions

- OWASP AIVSS has a publicly accessible specification without authentication at [aivss.owasp.org](https://aivss.owasp.org/) (validated during FR-001 research)
- Tachi's existing four-dimensional composite is the correct baseline for comparison (validated by `schemas/risk-scoring.yaml:43-46` and `.claude/skills/tachi-risk-scoring/references/scoring-dimensions.md`)
- The architect's APPROVED verdict on the plan/tasks artifacts (and on the PR review) **is** the attestation that ADR-024 ships with `Status: Accepted` — no separate sign-off ceremony (closed in PRD Open Questions)
- The feature branch name used throughout this spec is `143-maestro-aivss-evaluation-adr` (the branch existed before `/aod.spec` was invoked, aligned to PRD 143)

### Dependencies

- **External** (must remain available during implementation): [aivss.owasp.org](https://aivss.owasp.org/) OWASP canonical specification home. Mitigation: PRD Risk R1 contingency for canonical-home restructuring.
- **Internal**: None. This feature does not depend on any in-flight feature and does not block any in-flight feature.

### Constraints

- **ADR file format**: must match ADR-019 through ADR-023 (frontmatter + Context + Decision + Rationale + Alternatives Considered + Consequences minimum)
- **No runtime dependencies**: `pyproject.toml`, `requirements*.txt`, `package.json` are not modified (documentation-only feature)
- **Determinism (ADR-021)**: no pipeline output changes; backward-compatibility PDF baselines remain byte-identical (trivially satisfied — no pipeline inputs change)
- **Backward compatibility (Constitution III)**: zero schema shape change, zero breaking change
- **Conventional Commits (Constitution IX)**: `docs:` commit type for ADR-only additions
- **Timebox on FR-001 canonical-home research**: maximum 2 hours before escalation to PM (PRD Risk R1 mitigation)
