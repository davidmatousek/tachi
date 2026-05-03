---
prd_reference: docs/product/02_PRD/144-nist-ai-rmf-evaluation-adr-2026-04-15.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-15
    status: APPROVED
    notes: "0 CRITICAL / 0 HIGH / 0 MEDIUM / 3 LOW (all informational, deferred). All 8 PRD FRs mapped 1:1 to spec FRs (FR-001 to FR-008). All 5 PRD personas represented as 5 user stories (3 P1 + 1 P2 + 1 P1 non-disruption). All 4 Closed-at-Approval Qs encoded. All 5 PRD risks mapped to Edge Cases or Assumptions. Five-layer scope discipline airtight (FR-excludes + SC-006 git-diff + allow-list + Constraints + Assumptions). Spec tightens PRD in three areas: byte-equality SC-007 (PRD 143 lesson), 3-hour timebox SC-013, docs: commit SC-012 — improvements not scope creep. Decision-noun discipline preserved (no Option A/B/C prejudgment). C1 (LOW) priority notation P0→P1 cosmetic; C2 (LOW) FR-006 insertion-point unambiguous already; C3 (LOW) FR-002 Surface C complete-coverage default + Edge Case #3 architect scope-reduction authority self-consistent. Full review at .aod/results/spec-pm-review-144.md."
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: NIST AI RMF Integration Evaluation ADR

**Feature Branch**: `144-nist-ai-rmf-evaluation-adr`
**Created**: 2026-04-15
**Status**: Draft
**Input**: User description: "PRD: 144 - nist-ai-rmf-evaluation-adr"
**PRD**: [docs/product/02_PRD/144-nist-ai-rmf-evaluation-adr-2026-04-15.md](../../docs/product/02_PRD/144-nist-ai-rmf-evaluation-adr-2026-04-15.md)
**Research**: [research.md](research.md)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Compliance Officer NIST Mapping Decision (Priority: P1)

A compliance officer at a regulated organization (financial services, healthcare, public sector) opens tachi's ADR index to determine whether tachi outputs can be reported directly under NIST AI RMF vocabulary or must be translated by hand. They find a single ADR (ADR-025) whose Decision section answers the question in the first paragraph and whose Context section contains a structured mapping of NIST AI RMF Functions, Subcategories, and Generative AI Profile risks against tachi's pipeline phases, compensating-control categories, and STRIDE+AI threat categories.

**Why this priority**: The compliance officer is the proximate stakeholder whose unblocked workflow is the entire reason for this PRD. Without a single linkable ADR, every regulated adopter incurs the cost of reverse-engineering tachi's mapping themselves — a cost that scales with adopter count.

**Independent Test**: Open ADR-025 on `main`. Confirm that (a) the Decision section's first paragraph names tachi's NIST AI RMF posture in unambiguous terms, (b) the Context section contains three labeled mapping subsections (Surface A, B, C), and (c) every row in those subsections is annotated with one of: Overlap, Gap, Conflict, or "No equivalent". No tachi pipeline run is required.

**Acceptance Scenarios**:

1. **Given** ADR-025 is committed under [docs/architecture/02_ADRs/](../../docs/architecture/02_ADRs/), **When** a compliance officer opens the file, **Then** the Decision section's first paragraph contains a single decision-noun (e.g., "documentation-only mapping", "shallow wired integration", "deep wired integration") that names tachi's NIST AI RMF posture without ambiguity
2. **Given** the ADR is committed, **When** the compliance officer scrolls to the Context section, **Then** three labeled subsections exist — Surface A (NIST AI RMF Functions × tachi pipeline phases), Surface B (NIST AI RMF Subcategories × tachi compensating control categories), Surface C (NIST AI 600-1 Generative AI Profile risks × tachi STRIDE+AI categories) — and every row uses one of the four allowed labels: Overlap, Gap, Conflict, "No equivalent"
3. **Given** the compliance officer copies the ADR URL into a regulator-facing report, **When** they paste the link, **Then** it resolves to a stable file path matching `docs/architecture/02_ADRs/ADR-025-*.md` on `main` (not a draft, comment, PR review, or branch URL)

---

### User Story 2 - Security Engineer Procurement Justification (Priority: P1)

A security engineer at a regulated firm needs to justify tachi adoption to their compliance team. They search the ADR directory for "NIST AI RMF" and find exactly one ADR whose Decision section addresses the topic. They follow the cross-reference from `tachi-control-analysis/SKILL.md` to ADR-025 and confirm the SKILL.md paragraph and the ADR Decision use the same decision-noun (verbatim consistency, no synonyms or paraphrasing). They present the ADR to their compliance team as authoritative tachi guidance.

**Why this priority**: Procurement justification is the pre-requisite to adoption. A documented stance with verbatim consistency between the runtime-adjacent skill file and the canonical ADR removes the maintainer-as-source-of-truth dependency.

**Independent Test**: Grep `docs/architecture/02_ADRs/` for "NIST AI RMF" — exactly one ADR's Decision section addresses the topic (other ADRs may mention it only as a cross-reference). Open `.claude/skills/tachi-control-analysis/SKILL.md` — find the new "NIST AI RMF Relationship" section. Compare the decision-noun in SKILL.md against the decision-noun in ADR-025 — they must match byte-identically (modulo casing differences that are explicitly allowed).

**Acceptance Scenarios**:

1. **Given** ADR-025 is committed, **When** a security engineer searches `docs/architecture/02_ADRs/` for "NIST AI RMF", **Then** ADR-025 is the only ADR whose Decision section addresses NIST AI RMF (other ADRs may reference it only as a cross-reference to ADR-025)
2. **Given** the security engineer follows the cross-reference from [.claude/skills/tachi-control-analysis/SKILL.md](../../.claude/skills/tachi-control-analysis/SKILL.md) to ADR-025, **Then** the NIST AI RMF Relationship paragraph in SKILL.md contains the same decision-noun phrase as ADR-025's Decision section (verbatim string-equality check, modulo case)
3. **Given** the security engineer presents ADR-025 to their compliance team, **When** the team reads the Rationale section, **Then** the recommended option's compliance value for regulated adopters is explicitly addressed (sector references such as SOC 2, FedRAMP, HIPAA, FFIEC, EU AI Act named where relevant)

---

### User Story 3 - CISO Audit Preparation (Priority: P1)

A CISO at a regulated organization is preparing tachi-derived security-posture material for a regulatory audit. The auditor will use NIST AI RMF vocabulary. The CISO opens the new tachi-shared NIST AI RMF artifact (`.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`) and finds either a complete mapping table (Option A) or a relationship-only stub naming the wired-integration site and linking to a follow-on Issue (Option B/C). Either way, they have a single tachi-curated reference to cite alongside ADR-025 — no hand-rolled crosswalk required during the audit.

**Why this priority**: The audit-preparation use case is the highest-stakes regulated-adopter scenario. The PRD elevates this above PRD 143's S effort because the FR-7 tachi-shared artifact is the new addition for PRD 144 (PRD 143 had only the SKILL.md update + ADR).

**Independent Test**: Open `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`. If Option A: confirm the file contains a complete mapping table covering all 8 tachi compensating-control categories to their NIST AI RMF Subcategory equivalents. If Option B/C: confirm the file contains a one-paragraph relationship stub naming the wired-integration site (controls schema for B, new analyzer agent for C) and linking to the follow-on implementation Issue. Either way, the file resolves the link to ADR-025 by relative path and is renderable on `main` GitHub.

**Acceptance Scenarios**:

1. **Given** the chosen option is **A (docs-only)**, **When** the CISO opens [.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md](../../.claude/skills/tachi-shared/references/), **Then** the file contains a complete mapping table covering all 8 tachi compensating-control categories (authentication, input-validation, rate-limiting, encryption, logging-audit, csrf-protection, csp-security-headers, access-control) to their NIST AI RMF Subcategory equivalents
2. **Given** the chosen option is **B or C**, **When** the CISO opens the same file, **Then** the file contains a relationship-only stub (one paragraph + forward references) naming the wired-integration site (controls schema for Option B; new analyzer agent for Option C) and linking to the follow-on implementation Issue
3. **Given** any chosen option, **When** the CISO follows the link from `nist-ai-rmf-mapping.md` back to ADR-025, **Then** the link uses a relative path resolvable on `main` GitHub (no draft URLs, no PR-review URLs, no absolute filesystem paths)

---

### User Story 4 - Maintainer Decision Traceability (Priority: P2)

A future tachi maintainer is considering changes to the compensating controls analyzer or proposing a new NIST-aware analyzer agent. They search the ADR index for the original NIST AI RMF decision and find ADR-025 with at least three options (A, B, C) enumerated in Alternatives Considered, each with pros, cons, and a "Why Not Chosen" or "Why Chosen" rationale. They use the ADR to evaluate whether their proposed change is consistent with prior reasoning or constitutes a deliberate reversal.

**Why this priority**: The maintainer scenario is important but not user-facing — it's institutional traceability for future contributors. P2 is appropriate.

**Independent Test**: Open ADR-025. Confirm Alternatives Considered enumerates ≥3 options with pros/cons/effort/compliance-value/Why-Chosen|Why-Not-Chosen for each. Confirm Status reads "Accepted" (not "Proposed"). Confirm Related ADRs line cross-references ADR-024 (companion AIVSS evaluation).

**Acceptance Scenarios**:

1. **Given** ADR-025 is committed, **When** a future maintainer opens the Alternatives Considered section, **Then** ≥3 options are enumerated (Option A docs-only mapping, Option B shallow wired tagging, Option C deep wired analyzer agent — additional options like a hybrid B+C are permitted) with pros, cons, effort estimate (S/M/L), compliance value, and Why Not Chosen / Why Chosen rationale for each
2. **Given** ADR-025 is committed, **When** the maintainer reads the Status field, **Then** it reads exactly **Accepted** (not Proposed, not Draft, not Superseded)
3. **Given** the maintainer needs to understand the ADR-024 ↔ ADR-025 relationship, **When** they read either ADR's Related ADRs line, **Then** the other ADR is referenced as a companion MAESTRO-framework decision (bidirectional cross-reference)

---

### User Story 5 - Unregulated Adopter Non-Disruption (Priority: P1)

A security engineer at an unregulated organization is using tachi for general agentic threat modeling. They have no compliance pressure and don't want NIST vocabulary forced into their reports. After ADR-025 merges, they re-run `/tachi.threat-model` and `/tachi.compensating-controls` against their existing architecture description and confirm that the produced `threats.md`, `risk-scores.md`, and `compensating-controls.md` outputs are byte-identical to their pre-ADR-025 baselines (verified by `tests/scripts/test_backward_compatibility.py`). The PDF security report and infographic outputs are also byte-identical under `SOURCE_DATE_EPOCH=1700000000` (per ADR-021).

**Why this priority**: Non-disruption is a hard invariant for the documentation-only ADR scope. Failure here is a Constitution III backward-compatibility violation. The PRD's quinary persona (unregulated adopter) is explicitly protected by this acceptance criterion.

**Independent Test**: Run `pytest tests/scripts/test_backward_compatibility.py` against the merged ADR-025 branch. All 5 byte-identical baselines must pass under `SOURCE_DATE_EPOCH=1700000000`.

**Acceptance Scenarios**:

1. **Given** ADR-025 is merged to `main`, **When** an unregulated adopter runs `/tachi.threat-model` and `/tachi.compensating-controls` against their architecture, **Then** the produced `threats.md`, `risk-scores.md`, and `compensating-controls.md` outputs are byte-identical to their pre-ADR-025 versions
2. **Given** ADR-025 is merged, **When** `pytest tests/scripts/test_backward_compatibility.py` runs against the 5 example baselines under `SOURCE_DATE_EPOCH=1700000000`, **Then** all 5 baselines pass byte-identical comparison
3. **Given** the chosen option is **B or C**, **When** the follow-on implementation Issue is filed, **Then** the Issue body explicitly names "non-disruptive" or "opt-in" as a constraint for the implementation (so the unregulated-adopter invariant carries forward into the wired implementation)

---

### Edge Cases

- **Wave 1 research overrun**: If the implementer cannot confirm the latest NIST AI RMF + Generative AI Profile versions, URLs, and Function/Category/Subcategory hierarchy after 3 hours, they pause and choose one of: (a) descope Surface B Subcategory sample from "5-10 representative subcategories" to "3 subcategories", (b) defer FR-007 tachi-shared artifact creation to a follow-on Issue and ship only ADR-025 + SKILL.md update in this PR, or (c) escalate to PM. The 3-hour budget is strict (PRD Risk R1 mitigation).
- **NIST publishes a newer revision mid-implementation**: The ADR captures whichever version is current at research time, dated. If the newer revision materially changes scope (e.g., AI RMF 2.0 with renumbered Functions), the ADR notes the change and adapts the mapping accordingly. Default behavior: do NOT delay the PRD waiting for hypothetical NIST releases.
- **Surface C (Generative AI Profile risks × STRIDE+AI categories) is structurally intractable**: NIST GAI risks are domain-oriented (CBRN, content harms, IP) while tachi STRIDE+AI categories are mechanism-oriented. If full mapping proves intractable within the day budget, architect retains scope-reduction authority to abbreviate Surface C to a summary paragraph with 3-4 exemplar rows. PRD Risk R5 contingency.
- **"No equivalent" count exceeds 50% of GAI risks**: If more than half of the GAI Profile risks have no tachi equivalent, the ADR Rationale section explicitly addresses scope-alignment as a sixth trade-off input (beyond the standard five evaluation criteria) — high mismatch rate may inform the option choice (e.g., favor Option A docs-only because wired integration would have inherent coverage gaps; OR favor Option C deep-wired with a new analyzer agent that operates in NIST's domain ontology).
- **PR governance gate disagrees with chosen option**: Architect or team-lead may push for a different option than the one drafted. Up to 5 review iterations are budgeted (per `/aod.define` rules). If consensus cannot be reached, escalate to user with disagreement summarized.
- **ADR-024 back-reference edit conflicts with parallel work**: The one-line edit to ADR-024's Related ADRs line is trivial but ships in the same PR as ADR-025. If a parallel PR also touches ADR-024, this PR's author resolves the merge conflict by preserving both edits.
- **Decision-noun extracted from Decision section is ambiguous**: If multiple noun phrases match the regex `(documentation-only mapping|shallow wired integration|deep wired integration|hybrid [BC])` in the Decision section, the SC-007 verifier picks the FIRST match. Implementer is responsible for ensuring the Decision section's first paragraph contains a single canonical decision-noun.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST produce a research artifact summarizing the current NIST AI RMF specification (AI RMF 1.0, NIST AI 100-1) and the current NIST AI 600-1 Generative AI Profile, including: (a) the canonical landing page URLs, (b) the version numbers and publication dates, (c) the four Functions (Govern, Map, Measure, Manage), (d) a representative sample of Categories and Subcategories under each Function, and (e) the complete list of Generative AI Profile risk categories from NIST AI 600-1 §2. The research artifact MUST be appended to `specs/144-nist-ai-rmf-evaluation-adr/research.md` under a dedicated `## Wave 1 — NIST AI RMF Spec Notes` section so the spec's existing pre-research material is preserved.
- **FR-002**: System MUST produce a three-surface comparison in the ADR Context section, structured as three Markdown tables (or three labeled subsections) with explicit anchor tags (`<a id="surface-a"></a>`, `<a id="surface-b"></a>`, `<a id="surface-c"></a>`) for stable cross-references:
  - **Surface A — Functions × Pipeline Phases**: one row per NIST AI RMF Function (Govern, Map, Measure, Manage) mapped against tachi pipeline phases (Phase 1 Scope, Phase 2 Threat Detection, Phase 3 Compensating Controls, Phase 3.5 Cross-Layer Chains, Phase 4 Assessment, Phase 5 Reporting)
  - **Surface B — Subcategories × Compensating Control Categories**: a representative sample (5-10 NIST AI RMF Subcategories drawn from the most agentic-AI-relevant Categories) mapped against tachi's 8 compensating-control categories (authentication, input-validation, rate-limiting, encryption, logging-audit, csrf-protection, csp-security-headers, access-control)
  - **Surface C — Generative AI Profile Risks × STRIDE+AI Categories**: the complete list of NIST AI 600-1 Generative AI Profile risks mapped against tachi's 11 STRIDE+AI categories (Spoofing, Tampering, Repudiation, Info Disclosure, Denial of Service, Elevation of Privilege + Prompt Injection, Data Poisoning, Model Theft, Agent Autonomy, Tool Abuse)
  - Every row in every Surface MUST use exactly one relationship label: **Overlap**, **Gap**, **Conflict**, or **No equivalent**. No "TBD", "unclear", or empty-label rows are permitted.
- **FR-003**: System MUST enumerate at least three decision options in the ADR Alternatives Considered section: **Option A — Documentation-only mapping** (new file at `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` containing full mapping; no schema/agent/script changes); **Option B — Shallow wired integration** (extend a controls schema to optionally reference NIST AI RMF Subcategories on compensating controls; update control-analyzer agent and PDF security report; backward compatible when tags absent); **Option C — Deep wired integration** (new agent at `.claude/agents/tachi/nist-ai-rmf-analyzer.md` that runs after the compensating-controls analyzer and produces a dedicated NIST AI RMF coverage report). Each option MUST include: (a) Pros, (b) Cons, (c) Effort estimate (S/M/L with rough day estimate), (d) Compliance value for regulated adopters, (e) Pipeline determinism impact (per ADR-021), and (f) "Why Not Chosen" rationale (or "Why Chosen" for the recommended option). Additional options (e.g., hybrid B+C) MAY be added if research surfaces them.
- **FR-004**: System MUST select exactly one option as the recommendation in the ADR Decision and Rationale sections. The justification MUST address all five evaluation criteria (maturity, adoption, compatibility, effort, compliance value) AND MUST explicitly compare against ADR-024's reasoning (companion-framework precedent). The PRD's "AIVSS-divergence-by-pre-1.0-maturity" reasoning does NOT auto-default this ADR to "diverge" because NIST AI RMF 1.0 is stable — the recommendation MUST be reasoned afresh from the FR-002 mapping and the five criteria.
- **FR-005**: System MUST commit a new ADR file at `docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md` (filename pattern matches `docs/architecture/02_ADRs/ADR-025-*.md`). The ADR MUST: (a) have Status field reading exactly **Accepted** (not Proposed) at merge time, (b) have Date field reading the merge date in `YYYY-MM-DD` format, (c) include a Related ADRs line cross-referencing AT MINIMUM `ADR-024` (companion AIVSS evaluation), `ADR-020` (MAESTRO classification), `ADR-019` (shared cross-agent definitions), `ADR-018` (baseline-aware pipeline lineage), `ADR-021` (SOURCE_DATE_EPOCH determinism), and `ADR-023` (threat-agent skill-references pattern), and (d) follow the structural template of ADR-022, ADR-023, and ADR-024 (Decision, Rationale, Alternatives Considered, Consequences, Re-Evaluation Triggers, References sections).
- **FR-006**: System MUST add a new section titled "NIST AI RMF Relationship" (or equivalent unambiguous heading) to `.claude/skills/tachi-control-analysis/SKILL.md`, inserted after the existing `## Domain Overview` section and before the existing `## Baseline-Aware Control Analysis Rules` section (mirrors ADR-024 → tachi-risk-scoring/SKILL.md placement pattern). The section MUST: (a) be 80-200 words (verified by `awk '/^## NIST AI RMF Relationship/{flag=1; next} /^## /{flag=0} flag' .claude/skills/tachi-control-analysis/SKILL.md | wc -w`), (b) contain a relative-path link to ADR-025 (e.g., `../../../docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md`), and (c) contain a decision-noun phrase that is **byte-identical** (modulo case) to the decision-noun phrase in ADR-025's Decision section first paragraph (verified via shell equality check `[ "$(extract-noun ADR-025)" = "$(extract-noun SKILL.md)" ]`).
- **FR-007**: System MUST create a new file at `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` whose content shape depends on the chosen option:
  - **If Option A (docs-only)**: the file contains the complete mapping table covering all 8 tachi compensating-control categories to their NIST AI RMF Subcategory equivalents, plus the Surface C Generative AI Profile risks → STRIDE+AI categories crosswalk (this file becomes the canonical mapping artifact)
  - **If Option B (shallow wired)** or **Option C (deep wired)**: the file contains a one-paragraph relationship-only stub naming the wired-integration site (controls schema for Option B; new analyzer agent for Option C) and linking forward to the follow-on implementation Issue and back to ADR-025
  - In all cases, the file MUST: (a) exist post-merge, (b) link to ADR-025 by relative path, (c) be additive only (does NOT modify any existing tachi-shared reference file), and (d) be renderable in standard Markdown without GitHub-specific extensions
- **FR-008**: System MUST file a follow-on GitHub Issue using `bash .aod/scripts/bash/create-issue.sh` if and only if the chosen option is B (shallow wired) or C (deep wired). The Issue MUST: (a) have `stage:discover` label, (b) have a concrete title (e.g., "Implement NIST AI RMF compensating-control tagging (per ADR-025)" for Option B; "Implement NIST AI RMF coverage analyzer agent (per ADR-025)" for Option C), (c) have an Issue body that links back to ADR-025 and names the surfaces that would change in implementation (for Option B: schemas/finding.yaml or new controls schema, control-analyzer agent, security-report template, example regen; for Option C: new nist-ai-rmf-analyzer agent, new schema, new template page, new pipeline phase, example regen), (d) include the option-specific effort estimate (S/M/L + day estimate) copied verbatim from ADR-025 Alternatives Considered, and (e) explicitly name "non-disruptive" or "opt-in" as a constraint. If the chosen option is A (docs-only), this FR is **N/A** — no Issue is filed.

### Out-of-Scope Functional Requirements (Explicitly Excluded)

- **NO** changes to `schemas/finding.yaml` (currently v1.3) or `schemas/risk-scoring.yaml` (currently v1.1) or any other `schemas/*.yaml` file
- **NO** changes to `.claude/agents/tachi/control-analyzer.md` or any other agent file under `.claude/agents/tachi/` (all 17 agents are off-limits)
- **NO** new agent file at `.claude/agents/tachi/nist-ai-rmf-analyzer.md` (that is Option C's follow-on implementation, not part of this PRD)
- **NO** changes to scoring or controls scripts under `scripts/*.py` (runtime is unchanged)
- **NO** regeneration of example outputs under `examples/*/` (outputs are byte-identical pre/post merge per ADR-021)
- **NO** changes to existing tachi-shared references (`finding-format-shared.md`, `stride-categories-shared.md`, etc. — additive-only per ADR-023)
- **NO** updates to `README.md` or `docs/architecture/00_Tech_Stack/README.md` unless ADR-025 specifically requires a single anchor link (NOT a content rewrite)
- **NO** comparison to other process frameworks (ISO/IEC 23894, ISO/IEC 42001, EU AI Act, NIST CSF) — out of scope; this ADR is NIST-AI-RMF-specific
- **NO** code that produces NIST-AI-RMF-formatted output (that is the follow-on feature)
- **NO** migration tooling for existing `compensating-controls.md` outputs (that is the follow-on feature)
- **NO** decision on NIST AI RMF wired-integration breadth or scope beyond what ADR-025 captures (that is the follow-on feature's job)

### Key Entities *(include if feature involves data)*

- **ADR-025**: New Markdown file at `docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md`. Sections: Status/Date/Deciders/Feature/Related ADRs frontmatter, Context (with Surface A/B/C subsections), Decision, Rationale, Alternatives Considered, Consequences, When to Re-Evaluate, References. Length expected 200-280 lines (longer than ADR-024 due to NIST 4 Functions + GAI Profile surface area).
- **Surface A / B / C tables**: Markdown tables embedded in ADR-025 Context section. Each row has a relationship label drawn from {Overlap, Gap, Conflict, No equivalent}. Each table has an explicit `<a id="surface-{a,b,c}"></a>` anchor tag.
- **NIST AI RMF Mapping Reference**: New file at `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`. Content shape depends on chosen option (complete mapping table for Option A; relationship stub for Option B/C).
- **SKILL.md NIST AI RMF Relationship Section**: New section appended to `.claude/skills/tachi-control-analysis/SKILL.md`. 80-200 words, contains decision-noun byte-identical (modulo case) to ADR-025 Decision.
- **ADR-024 Back-Reference**: Single-line edit to `docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md` adding `ADR-025` to the Related ADRs line (bidirectional symmetry per Closed-at-Approval Q4 in PRD).
- **Follow-On Issue (conditional)**: New GitHub Issue filed only if Option B or C chosen; references ADR-025 in body.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: ADR-025 file exists at `docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md` on `main` after merge — verified by `[ -f docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md ]` returning 0
- **SC-002**: ADR-025 Status field reads exactly `Accepted` at merge — verified by `grep -E '^\*\*Status\*\*: Accepted$' docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md` returning 1 match
- **SC-003**: ADR-025 Context section contains all three Surface subsections with explicit anchor tags — verified by `grep -c '<a id="surface-[abc]"></a>' docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md` returning exactly 3
- **SC-004**: Every row in Surface A, B, C uses one of the four allowed relationship labels — verified by reviewer inspection that no row contains "TBD", "unclear", or empty cells in the relationship column
- **SC-005**: SKILL.md NIST AI RMF Relationship section is between 80 and 200 words — verified by `awk '/^## NIST AI RMF Relationship/{flag=1; next} /^## /{flag=0} flag' .claude/skills/tachi-control-analysis/SKILL.md | wc -w` returning a value in `[80, 200]`
- **SC-006**: Zero unintended drift in pipeline outputs — verified by `git diff main..144-nist-ai-rmf-evaluation-adr -- schemas/ scripts/ .claude/agents/ examples/` returning empty (zero lines changed in those four scopes). Allowed additive exceptions outside that diff scope: (a) `.claude/skills/tachi-control-analysis/SKILL.md` adds the FR-006 paragraph (existing file edit), (b) new file `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` (FR-007 artifact), (c) new file `docs/architecture/02_ADRs/ADR-025-*.md` (FR-005 ADR), (d) one-line edit to `docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md` Related ADRs line, (e) new files under `specs/144-nist-ai-rmf-evaluation-adr/` (spec/plan/tasks/research/checklists artifacts).
- **SC-007**: Decision-noun consistency between ADR-025 Decision section and SKILL.md NIST AI RMF Relationship section — verified by extracting the noun phrase from each surface and confirming byte-equality (modulo case) AND non-empty: `ADR_NOUN=$(grep -oE -i '(documentation-only mapping|shallow wired integration|deep wired integration|hybrid [BC])' docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md | head -1 | tr '[:upper:]' '[:lower:]'); SKILL_NOUN=$(grep -oE -i '(documentation-only mapping|shallow wired integration|deep wired integration|hybrid [BC])' .claude/skills/tachi-control-analysis/SKILL.md | head -1 | tr '[:upper:]' '[:lower:]'); [ "$ADR_NOUN" = "$SKILL_NOUN" ] && [ -n "$ADR_NOUN" ]`. The non-empty guard prevents both-empty false-PASS (per architect plan review C2 MEDIUM).
- **SC-008**: `tachi-shared/references/nist-ai-rmf-mapping.md` exists post-merge — verified by `[ -f .claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md ]` returning 0; content shape matches chosen option (full mapping for Option A; relationship stub for Option B/C — verified by reviewer inspection)
- **SC-009**: Follow-on Issue filed if Option B or C chosen — verified by `gh issue list --label stage:discover --search "ADR-025"` returning ≥1 result; **N/A** if Option A chosen (verified by absence in ADR-025 Decision section that no follow-on Issue is named)
- **SC-010**: Backward-compatibility test green — `pytest tests/scripts/test_backward_compatibility.py` returns 5/5 passing under `SOURCE_DATE_EPOCH=1700000000`
- **SC-011**: ADR-024 Related ADRs line back-reference edit committed — verified by `grep -E 'ADR-025' docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md` returning ≥1 match in the frontmatter Related ADRs line
- **SC-012**: All commits on the feature branch use `docs:` conventional commit prefix (not `feat:` or `fix:`) — verified by `git log main..144-nist-ai-rmf-evaluation-adr --pretty=%s | grep -vE '^docs(\(.+\))?:'` returning empty
- **SC-013**: Wave 1 research timebox respected — implementer reports research completion within 3 hours OR escalates to PM with one of the three contingency options chosen (descope Surface B, defer FR-007, or escalate). Captured in delivery retrospective.

## Assumptions

- **NIST AI RMF accessibility**: NIST AI 100-1 (AI RMF 1.0) and NIST AI 600-1 (Generative AI Profile) are publicly accessible without authentication at NIST canonical landing pages, validated during pre-spec research (https://www.nist.gov/itl/ai-risk-management-framework, https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf, https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf, DOI https://doi.org/10.6028/NIST.AI.600-1).
- **Framework structural shape**: NIST AI RMF has 4 Functions (Govern, Map, Measure, Manage) with a 3-level hierarchy (Function → Category → Subcategory). NIST AI 600-1 §2 contains 12 GAI risk categories (the PRD's "12-13" estimate tightens to exactly 12 during Wave 1 validation per pre-spec research).
- **Stable URLs**: NIST canonical landing pages and PDF URLs remain stable for at least the duration of this PRD's implementation cycle (validated 2026-04-15 by pre-spec research; a newer revision might ship between PRD filing and merge, mitigated by Risk R1 of PRD).
- **Existing tachi compensating-controls categories are the correct comparison baseline**: 8 categories (authentication, input-validation, rate-limiting, encryption, logging-audit, csrf-protection, csp-security-headers, access-control) per `.claude/skills/tachi-control-analysis/references/control-categories.md` are the canonical inputs for Surface B mapping work.
- **Pre-1.0 maturity does not auto-default to diverge**: Unlike ADR-024's reasoning (AIVSS is pre-1.0 → diverge), NIST AI RMF 1.0 is stable. The recommendation is reasoned afresh from FR-002 mapping + five criteria.
- **Architect approval of plan/tasks artifacts serves as ADR Accepted attestation**: Same precedent as ADR-022, ADR-023, ADR-024 (closed at PRD approval Q2). No separate ADR-only review ceremony.
- **Pre-spec research findings (research.md sections 1-5) are forward-looking guidance**, NOT canonical mapping content; Wave 1 (FR-001) implementer validates and corrects assumptions in research.md `## Wave 1 — NIST AI RMF Spec Notes` section if needed.

## Constraints

- **Documentation-only**: This is an ADR-only spike. Zero production code changes. No new runtime dependencies (zero diff on `requirements*.txt`, `pyproject.toml`, `package.json`).
- **ADR file format**: Must match existing ADRs (ADR-020 through ADR-024) for consistency.
- **Decision must be Accepted at merge**: Proposed-status ADRs do NOT satisfy SC-002. Same precedent as all prior tachi ADRs.
- **Companion-framework precedent (non-binding)**: ADR-024 chose to diverge for AIVSS. ADR-025 reasons independently because NIST AI RMF 1.0 is stable; the maturity criterion does NOT auto-default to diverge.
- **5-iteration governance budget**: Up to 5 review iterations per `/aod.define` rules. If consensus cannot be reached, escalate to user.
- **3-hour Wave 1 timebox**: FR-001 research is timeboxed to 3 hours (PRD Risk R1 mitigation). On overrun, scope-reduction options apply (see Edge Cases).
- **`docs:` conventional commit prefix**: All commits MUST use `docs:` (not `feat:` or `fix:`) per Constitution IX. Verified by SC-012.

## Dependencies

- **No internal dependencies**: Independent of any in-flight feature.
- **External dependency**: Public availability of NIST AI RMF 1.0 (NIST AI 100-1) and NIST AI 600-1 specifications. Risk R1 of PRD covers contingencies (timebox + scope-reduction fallbacks + escalation).
- **Forward dependency (conditional)**: If Option B or C chosen, follow-on implementation Issue (per FR-008) becomes the next deliverable in the NIST AI RMF lineage.
- **Bidirectional cross-reference**: ADR-024 Related ADRs line gains back-reference to ADR-025 in the same PR (per Closed-at-Approval Q4 in PRD).
