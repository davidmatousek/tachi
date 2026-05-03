---
prd:
  number: 143
  topic: maestro-aivss-evaluation-adr
  created: 2026-04-14
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-04-14, status: APPROVED_WITH_CONCERNS, notes: "4 LOW concerns. C4 (R3→R2 typo) fixed inline. C1 (US-143-3 AC-1 softening) fixed inline. C3 (FR-7 fidelity level) fixed inline. C2 (grep assertion for Status: Accepted) deferred to tasks.md. Best-in-class scope discipline for ADR-only spike — five independent enforcement layers plus automated git-diff post-condition."}
  architect_signoff: {agent: architect, date: 2026-04-14, status: APPROVED_WITH_CONCERNS, notes: "1 MEDIUM (FR-2 mapping expanded to 3 surfaces — dimensions, formula, bands — fixed inline) + 5 LOW. LOW-1 Deciders triad roster + LOW-2 Related ADRs frontmatter + LOW-3 Open Question 3 (ADR-019 cross-ref closed YES) all fixed inline in Appendix A skeleton. LOW-4 (option-specific effort estimate in FR-7) fixed inline. LOW-5 (SKILL.md placement) deferred to implementer's call. Architectural invariants preserved: ADR-021 determinism, ADR-023 detection-variant agent shape, ADR-019 shared-ref discipline, Constitution III backward compat."}
  techlead_signoff: {agent: team-lead, date: 2026-04-14, status: APPROVED_WITH_CONCERNS, notes: "0 CRITICAL / 0 HIGH / 3 MEDIUM / 3 LOW. Rec #1 (agent assignments — web-researcher FR-1, architect FR-2-FR-6, product-manager FR-7; senior-backend-engineer NOT appropriate) fixed inline. Rec #2 (R1 2-hour timebox) added inline to Risk R1 mitigation. Rec #4 (Appendix A Deciders triad) fixed inline. Rec #3 (architect approval = Accepted attestation) closed at PRD approval. Two-wave structure: Wave 1 research, Wave 2 ADR authorship. ~3-4.5h wall-clock realistic; 1-day cycle has margin."}
source:
  idea_id: 143
  story_id: null
---

# MAESTRO Phase 4: OWASP AIVSS Evaluation ADR — Product Requirements Document

**Status**: Approved
**Created**: 2026-04-14
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1 (High) — MAESTRO compliance closure
**Parent Discovery**: [#143](https://github.com/davidmatousek/tachi/issues/143) (umbrella discovery #136)

---

## Executive Summary

### The One-Liner
Evaluate OWASP AIVSS against tachi's four-dimensional composite score and commit the decision as an ADR — adopt, supplement, or diverge — so adopters comparing tachi to other agentic threat modeling tools have a single, traceable answer to "does this align with the OWASP AI scoring standard?"

### Problem Statement
Canonical CSA MAESTRO explicitly references OWASP AIVSS as the companion scoring approach for agentic AI: *"These risk profiles can be benchmarked using OWASP's AI Vulnerability Scoring System (AIVSS)."* Tachi today uses CVSS 3.1 plus a custom four-dimensional composite (CVSS 0.35, exploitability 0.30, reachability 0.20, scalability 0.15) defined in [schemas/risk-scoring.yaml](../../schemas/risk-scoring.yaml) and [.claude/skills/tachi-risk-scoring/](../../.claude/skills/tachi-risk-scoring/). There is no ADR explaining the relationship between this composite and AIVSS, no comparison of dimensions, no documented rationale for why we use CVSS 3.1 rather than AIVSS, and no guidance for adopters who need AIVSS-aligned outputs for compliance reasons.

CISOs evaluating tachi for procurement, compliance officers reporting to regulators, and security engineers comparing tools all face the same gap: tachi ships canonical MAESTRO labels (post-PRD 136) and cross-layer attack chains (post-PRD 141), but the third leg of the MAESTRO practitioner stool — AIVSS-aligned scoring — has no documented stance.

### Proposed Solution
A documentation-only ADR spike. Research the current OWASP AIVSS specification, build a side-by-side comparison against tachi's existing four-dimensional composite, enumerate at least three options (adopt as primary, adopt as supplementary field, document divergence with rationale), recommend one with justification, and commit the decision as a new ADR (next available number is **ADR-024** at [docs/architecture/02_ADRs/](../../docs/architecture/02_ADRs/)). Add a one-paragraph AIVSS relationship statement to [tachi-risk-scoring/SKILL.md](../../.claude/skills/tachi-risk-scoring/SKILL.md) reflecting the ADR decision. **No production code changes** to the risk-scoring pipeline in this feature — implementation, if the decision is to adopt, is an explicit follow-on feature filed as a separate GitHub Issue.

### Success Criteria
- The current OWASP AIVSS specification is read end-to-end with version number captured in the ADR (handle the case where AIVSS lacks a stable 1.0 — see Risk R2 below)
- A side-by-side mapping table compares tachi's four composite dimensions to AIVSS dimensions, identifying overlaps, gaps, and conflicts
- ADR-024 is committed under [docs/architecture/02_ADRs/](../../docs/architecture/02_ADRs/) with at least three evaluated options and one recommended decision; status is **Accepted** at merge time (not Proposed)
- [tachi-risk-scoring/SKILL.md](../../.claude/skills/tachi-risk-scoring/SKILL.md) gains a one-paragraph AIVSS Relationship section reflecting the ADR decision
- If the decision is **adopt** (primary or supplementary): a follow-on implementation feature is filed as a separate GitHub Issue and referenced from the ADR Consequences section
- If the decision is **diverge**: rationale is concrete with at least two worked examples of where AIVSS would produce a different score than tachi for the same finding
- Zero changes to [schemas/risk-scoring.yaml](../../schemas/risk-scoring.yaml), [scripts/](../../scripts/), or any agent file under [.claude/agents/](../../.claude/agents/) — verified by post-merge `git diff` check
- README.md and [docs/architecture/00_Tech_Stack/README.md](../../docs/architecture/00_Tech_Stack/README.md) are unchanged unless the ADR specifically requires a cross-reference (in which case the change is a single anchor link, not a content rewrite)

### Timeline
Single short ADR cycle: ~1 working day end-to-end (research, mapping table, ADR draft, skill update, governance review).

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](../01_Product_Vision/product-vision.md)

Tachi's vision is to be *"the default threat modeling toolkit for any team building agentic AI applications."* The default toolkit must answer the questions that agentic AI security teams are actually asking. CSA MAESTRO is the published taxonomy framework; OWASP AIVSS is the published scoring framework practitioners pair with it. Shipping canonical MAESTRO labels (PRD 136) without a documented stance on AIVSS leaves a gap that adopters must close themselves — by reading the risk-scoring schema and reverse-engineering whether tachi's composite is "AIVSS-aligned." A traceable ADR closes that gap with a single linkable decision.

### Roadmap Fit
This is the **fourth and final phase** of the MAESTRO compliance initiative captured in the umbrella discovery [#136](https://github.com/davidmatousek/tachi/issues/136):

- **Phase 1**: [PRD 136](136-maestro-canonical-layer-correctness-fix-2026-04-10.md) — Canonical layer correctness fix — **Delivered**
- **Phase 2**: [PRD 141](141-maestro-cross-layer-attack-chains-2026-04-12.md) — Cross-layer attack chain analysis — **Delivered**
- **Phase 3**: [PRD 082](082-threat-agent-skill-references-2026-04-11.md) — Threat agent skill references / agentic threat pattern expansion — **Delivered**
- **Phase 4 (this PRD)**: OWASP AIVSS evaluation ADR — **In review**

After Phase 4 closes, the umbrella MAESTRO compliance discovery item can be closed.

### Dependency Posture
- **Independent of any unshipped feature**: this PRD does not require any other feature in flight to land first
- **Does not block any feature in flight**: no downstream feature is waiting on the ADR decision
- **If the ADR decides to adopt AIVSS**: the follow-on implementation feature should land **after** PRD 136 (already delivered), so canonical layer names are in place when AIVSS-aligned scoring outputs reference them
- **Schema impact**: zero. [schemas/risk-scoring.yaml](../../schemas/risk-scoring.yaml) is not modified by this PRD

---

## Target Users & Personas

### Primary Persona: CISO Evaluating Tachi for Procurement
- **Role**: Senior security leader evaluating threat modeling tools for organizational adoption
- **Goal**: Brief their team on tachi's scoring methodology in one paragraph, with a clear citation to a public standard
- **Pain Point**: Today they must read [schemas/risk-scoring.yaml](../../schemas/risk-scoring.yaml) plus the [tachi-risk-scoring](../../.claude/skills/tachi-risk-scoring/) skill files to answer "is this AIVSS-aligned?" — and even then, the answer is "no documented stance"

### Secondary Persona: Compliance Officer at a Regulated Organization
- **Role**: Maps tool outputs to regulatory frameworks (SOC 2, FedRAMP, EU AI Act, sector-specific)
- **Goal**: Know whether tachi scores can be reported to regulators as-is or require translation to a recognized standard
- **Pain Point**: AIVSS is the scoring standard MAESTRO practitioners reference; without a tachi ADR on AIVSS, the compliance officer must manually translate tachi scores or commission an analyst to reverse-engineer the mapping

### Tertiary Persona: Tachi Maintainer (Future)
- **Role**: Future contributor considering changes to the scoring pipeline
- **Goal**: Have a traceable baseline for "why do we use this composite and not AIVSS?" before proposing modifications
- **Pain Point**: With no ADR, future scoring changes risk silently diverging from MAESTRO practitioner expectations because the original posture was undocumented

### Quaternary Persona: Security Engineer Comparing Tools
- **Role**: Evaluates multiple agentic threat modeling tools side-by-side
- **Goal**: Explain tachi's composite output to stakeholders who already know AIVSS
- **Pain Point**: Without an explicit dimension mapping, the security engineer must build the comparison themselves — which is error-prone and not durable across tachi releases

---

## User Stories

### US-143-1: CISO Procurement Brief
**When** I am evaluating tachi for organizational adoption and need to explain its scoring methodology to my team in one paragraph,
**I want to** read a single ADR that states tachi's relationship with OWASP AIVSS (adopt, supplement, or diverge with rationale),
**So I can** brief my team without reverse-engineering the risk-scoring schema or speculating about alignment.

**Acceptance Criteria**:
- **Given** ADR-024 is committed and visible in [docs/architecture/02_ADRs/](../../docs/architecture/02_ADRs/), **when** a CISO opens the ADR, **then** the Decision section answers "does tachi align with AIVSS?" in the first paragraph
- **Given** the ADR is committed, **when** the CISO follows the cross-reference from [tachi-risk-scoring/SKILL.md](../../.claude/skills/tachi-risk-scoring/SKILL.md), **then** the AIVSS Relationship paragraph in SKILL.md matches the ADR decision verbatim (single source of truth, no drift)
- **Given** the CISO copies the ADR URL into a procurement brief, **when** they do so, **then** the URL points to a stable file path under `docs/architecture/02_ADRs/ADR-024-*.md` (not a draft, not a comment, not a PR review URL)

**Priority**: P0
**Effort**: S

### US-143-2: Compliance Officer Reporting Decision
**When** I need to decide whether to report tachi scores directly to regulators or translate them to AIVSS,
**I want to** read a side-by-side mapping of tachi's four composite dimensions against AIVSS dimensions with overlaps, gaps, and conflicts called out,
**So I can** make the report-vs-translate decision based on documented dimension alignment rather than guesswork.

**Acceptance Criteria**:
- **Given** ADR-024 is committed, **when** a compliance officer reads the ADR, **then** the Context section contains a side-by-side mapping table with rows for each tachi composite dimension (CVSS, exploitability, reachability, scalability) and AIVSS dimensions
- **Given** the mapping table exists, **when** the compliance officer reads each row, **then** every row is annotated with one of: **Overlap** (dimensions measure the same thing), **Gap** (AIVSS measures something tachi does not, or vice versa), or **Conflict** (dimensions have the same name but measure different things)
- **Given** the recommended decision is "diverge", **when** the compliance officer reads the Rationale section, **then** at least two worked examples show a finding where AIVSS would produce a measurably different score than tachi (with both scores quantified)

**Priority**: P0
**Effort**: M

### US-143-3: Maintainer Decision Traceability
**When** I am a future tachi maintainer considering changes to the scoring pipeline,
**I want to** find a single ADR that documents the original AIVSS decision with the options that were considered,
**So I can** evaluate whether the proposed change is consistent with prior reasoning or constitutes a deliberate reversal.

**Acceptance Criteria**:
- **Given** ADR-024 is committed, **when** a future maintainer searches for "AIVSS" in [docs/architecture/02_ADRs/](../../docs/architecture/02_ADRs/), **then** ADR-024 is the only ADR whose Decision section addresses AIVSS (other ADRs may mention AIVSS only as a cross-reference to ADR-024)
- **Given** ADR-024 is committed, **when** the maintainer reads the Alternatives Considered section, **then** at least three options are enumerated (adopt as primary, adopt as supplementary field, document divergence) with pros, cons, and a "Why Not Chosen" explanation for each non-recommended option
- **Given** the ADR is committed, **when** the maintainer reads the Status field, **then** it reads **Accepted** (not Proposed) at merge time

**Priority**: P1
**Effort**: S

### US-143-4: Security Engineer Dimension Mapping
**When** I am explaining tachi's risk score to a stakeholder familiar with AIVSS,
**I want to** read an explicit dimension-by-dimension mapping in a public ADR that I can link to,
**So I can** translate tachi's composite into AIVSS terms without inventing my own crosswalk.

**Acceptance Criteria**:
- **Given** ADR-024 is committed, **when** a security engineer reads the side-by-side table, **then** each tachi dimension is mapped to either an AIVSS dimension, a combination of AIVSS dimensions, or "no AIVSS equivalent" (no row left ambiguous)
- **Given** the engineer needs to cite the mapping in external documentation, **when** they copy the ADR section URL with a heading anchor, **then** the anchor links directly to the mapping table heading

**Priority**: P1
**Effort**: S

---

## Functional Requirements

### Core Capabilities

#### FR-1: AIVSS Specification Research
**Description**: Read the current OWASP AIVSS specification end-to-end, capture version number, list scoring dimensions, document severity bands and any composite formula.

**Inputs**: Public OWASP documentation (canonical home to be confirmed during research — see Risk R1)
**Processing**: Read, summarize, capture version metadata
**Outputs**: A research summary embedded in the ADR Context section, capturing: AIVSS version (or "no stable 1.0 yet"), URL of the canonical specification, dimension list, severity band thresholds, composite formula (if defined)

**Business Rules**:
- The canonical home of AIVSS is confirmed during research (do not link to a project that has been archived or renamed)
- If AIVSS lacks a stable 1.0 specification, the ADR notes that explicitly and adopts a default of "document divergence with a commitment to re-evaluate at AIVSS 1.0"
- The version number captured in the ADR matches the specification version observed at research time (date-stamped)

#### FR-2: Side-by-Side Comparison Across Three Scoring Surfaces
**Description**: Build a three-surface comparison covering tachi's full scoring model versus AIVSS — not just dimensions, but also composite formula weights and severity band thresholds. A dimension-only mapping could conclude "all dimensions overlap" while still hiding formula and band divergence that produces different scores for the same finding.

**Inputs**: Tachi's four composite dimensions from [schemas/risk-scoring.yaml](../../schemas/risk-scoring.yaml), composite formula weights and severity bands from the same schema and [severity-bands-shared.md](../../.claude/skills/tachi-shared/references/severity-bands-shared.md), and the dimension definitions in [tachi-risk-scoring/references/scoring-dimensions.md](../../.claude/skills/tachi-risk-scoring/references/scoring-dimensions.md); AIVSS equivalents from FR-1 research
**Processing**: Three labeled comparison subsections in the ADR Context section, each annotated with relationship labels (Overlap, Gap, Conflict, No equivalent)
**Outputs**: Three Markdown tables (or three subsections) in the ADR Context section:
- **Surface A — Dimension Set**: one row per tachi dimension (CVSS 3.1 base, exploitability, reachability, scalability) mapped to AIVSS equivalents
- **Surface B — Composite Formula Weights**: tachi's `(0.35×CVSS) + (0.30×Exploitability) + (0.20×Reachability) + (0.15×Scalability)` versus AIVSS composite formula (or "AIVSS does not define a composite" if research confirms that)
- **Surface C — Severity Band Thresholds**: tachi's Critical/High/Medium/Low cutoffs versus AIVSS bands

**Business Rules**:
- Every tachi dimension appears in Surface A with a non-ambiguous relationship label (no "TBD" or "unclear")
- Surface B is included even if AIVSS lacks a published composite formula — explicitly state "no AIVSS equivalent" in that case
- Surface C is included even if AIVSS does not define severity bands — explicitly state "no AIVSS equivalent" in that case
- Conflicts (same name, different meaning) are called out explicitly with a one-line explanation each
- The mapping does **not** silently elide formula-or-band divergence behind a "dimensions overlap" headline

#### FR-3: Options Enumeration
**Description**: Enumerate at least three decision options with pros, cons, and trade-off analysis.

**Inputs**: Mapping from FR-2; project constraints (zero-dependency runtime per repo conventions, deterministic pipeline per ADR-021)
**Processing**: Structured options analysis
**Outputs**: ADR Alternatives Considered section with at least three options:
- **Option A**: Adopt AIVSS as primary scoring replacement (replaces composite)
- **Option B**: Adopt AIVSS as supplementary field alongside existing composite (additive, no breaking change)
- **Option C**: Document divergence with rationale (no schema change; ADR explains posture)
- Additional options may be added if research surfaces them

**Business Rules**:
- Each option includes pros, cons, and a "Why Not Chosen" rationale (for non-recommended options) or a "Why Chosen" rationale (for the recommended option)
- Each option's effort estimate is concrete (S/M/L with rough day estimate)
- Each option's compliance value for regulated adopters is explicitly addressed

#### FR-4: Recommendation with Justification
**Description**: Pick one option with a defensible justification considering AIVSS maturity, adoption in the wild, compatibility with the current composite, effort to wire in, and compliance value.

**Inputs**: Options from FR-3
**Processing**: Trade-off analysis using the five evaluation criteria
**Outputs**: ADR Decision and Rationale sections naming the chosen option and justifying it

**Business Rules**:
- The justification addresses all five evaluation criteria (maturity, adoption, compatibility, effort, compliance value)
- If the recommended option is **adopt**, the Consequences section names the follow-on implementation feature and links to its GitHub Issue (filed as part of this PRD's delivery)
- If the recommended option is **diverge**, the Rationale section includes at least two worked examples of where AIVSS would produce a different score than tachi for the same finding

#### FR-5: ADR-024 Commit
**Description**: Commit the decision as ADR-024 in the established ADR format under [docs/architecture/02_ADRs/](../../docs/architecture/02_ADRs/).

**Inputs**: All sections from FR-1 through FR-4
**Processing**: Format per existing ADR conventions (see ADR-020, ADR-021, ADR-022, ADR-023 for shape)
**Outputs**: New file `docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md`

**Business Rules**:
- File path matches `docs/architecture/02_ADRs/ADR-024-*.md`
- Status field reads **Accepted** at merge time (not Proposed)
- Date field reads the merge date (not the draft date)
- Cross-references existing related ADRs at minimum: ADR-020 (MAESTRO classification) and the broader risk-scoring lineage if applicable

#### FR-6: SKILL.md Cross-Reference Update
**Description**: Add a one-paragraph AIVSS Relationship section to [tachi-risk-scoring/SKILL.md](../../.claude/skills/tachi-risk-scoring/SKILL.md).

**Inputs**: ADR-024 decision text
**Processing**: Insert a new section (recommended placement: after "Domain Overview", before "Baseline-Aware Scoring Rules"); link to ADR-024
**Outputs**: Updated SKILL.md with the new section

**Business Rules**:
- The paragraph mirrors the ADR Decision in plain language (no contradictions; if the ADR says "diverge" the SKILL must not imply alignment)
- The paragraph contains an explicit link to ADR-024 by relative path
- The paragraph length is between 80 and 200 words (not a deep dive; pointer to the ADR)

#### FR-7: Follow-On Issue (Conditional)
**Description**: If the decision is to adopt (Option A or B), file a follow-on implementation feature as a separate GitHub Issue and reference it from the ADR Consequences section.

**Inputs**: ADR decision
**Processing**: Use `bash .aod/scripts/bash/create-issue.sh` (see [.aod/scripts/bash/](../../.aod/scripts/bash/)) to create a new Issue with `stage:discover` label and ICE score scoped to implementation effort
**Outputs**: A new GitHub Issue number referenced in ADR-024

**Business Rules**:
- Only fired if the recommended decision is Option A (primary) or Option B (supplementary)
- The Issue title is concrete: e.g., "Implement OWASP AIVSS supplementary scoring (per ADR-024)"
- The Issue body links back to ADR-024 and **at minimum names the surfaces that would change in implementation** (e.g., `schemas/risk-scoring.yaml`, `.claude/skills/tachi-risk-scoring/references/`, `templates/tachi/**.typ`) — a 3-5 bullet surface overview suffices; full ICE-scored breakdown is deferred to the follow-on PRD's own discovery cycle
- The Issue body **includes the option-specific effort estimate** copied verbatim from the ADR-024 Alternatives Considered section for the chosen option (Option A and Option B have materially different effort profiles — A is a schema-breaking change with example regen, B is additive)
- If the decision is Option C (diverge), this FR is skipped — no follow-on issue is filed

### Out-of-Scope Functional Requirements (Explicitly Excluded)

- **No changes to [schemas/risk-scoring.yaml](../../schemas/risk-scoring.yaml)** — schema bumps are an implementation concern, not an ADR concern
- **No changes to [.claude/agents/tachi/risk-scorer.md](../../.claude/agents/tachi/risk-scorer.md) or any other agent file** — agents are unchanged by this ADR
- **No changes to scoring scripts under [scripts/](../../scripts/)** — runtime is unchanged
- **No regeneration of example outputs** under [examples/](../../examples/) — outputs are unchanged
- **No release-please version bump beyond what an ADR file addition would naturally trigger** — ADR-only changes typically land as a `docs:` commit, not a `feat:` or `fix:`

---

## Non-Functional Requirements

### Documentation Quality
- ADR follows the structural pattern established by ADR-020 through ADR-023 (Context, Decision, Rationale, Alternatives Considered, Consequences sections at minimum)
- Mapping table is renderable in standard Markdown (no extensions required)
- All cross-references use relative paths (no absolute paths or external URLs except for the AIVSS canonical specification link)

### Traceability
- ADR-024 references the parent discovery item (#143) and the umbrella MAESTRO compliance discovery (#136)
- ADR-024 cross-references at minimum ADR-020 (MAESTRO classification) for taxonomy context
- The follow-on implementation Issue (if filed) references ADR-024 as its decision baseline

### Accessibility / Audit
- ADR-024 is committed under version control (Git history is the audit trail)
- ADR Status field is unambiguous: **Accepted** at merge, dated to merge day
- Future maintainers can find the AIVSS decision via either: search ADRs for "AIVSS", search SKILL.md for "AIVSS", or follow the chain from MAESTRO Phase 4 PRD (this document)

---

## Success Metrics

### Primary Metrics

**Metric 1**: ADR-024 committed and merged with status **Accepted**
- **Definition**: Boolean — file exists at `docs/architecture/02_ADRs/ADR-024-*.md` on `main` with Status: Accepted
- **Baseline**: 0 (no AIVSS ADR exists today)
- **Target**: 1
- **Timeline**: At PRD delivery
- **Owner**: product-manager (delivery), architect (review)

**Metric 2**: SKILL.md AIVSS Relationship section present
- **Definition**: Boolean — `.claude/skills/tachi-risk-scoring/SKILL.md` contains a section titled "AIVSS Relationship" (or equivalent) with a link to ADR-024
- **Baseline**: 0 (no AIVSS mention in SKILL.md today)
- **Target**: 1
- **Timeline**: At PRD delivery
- **Owner**: product-manager

### Secondary Metrics

**Metric 3**: Zero unintended drift in scoring outputs
- **Definition**: `git diff main..feature-branch -- schemas/ scripts/ .claude/agents/ examples/` returns empty
- **Baseline**: 0 lines changed expected
- **Target**: 0 lines changed actual
- **Timeline**: At PR review
- **Owner**: code-reviewer

**Metric 4**: Follow-on Issue filed (conditional)
- **Definition**: If ADR decides Option A or B, a new GitHub Issue exists with `stage:discover` label referencing ADR-024
- **Baseline**: 0
- **Target**: 1 if Option A/B; 0 if Option C
- **Timeline**: At PRD delivery
- **Owner**: product-manager

### Lagging Metrics (Tracked Post-Delivery)

- Number of times ADR-024 is cited externally (procurement briefs, comparison docs) — qualitative
- Number of times the follow-on implementation Issue (if filed) is upvoted or commented on — used to inform priority of follow-on work
- Whether AIVSS ships a stable 1.0 (triggers ADR-024 re-evaluation per Risk R2 mitigation)

---

## Scope & Boundaries

### In Scope (Must Have, P0)
- **Research**: Read the current OWASP AIVSS specification with version captured (FR-1)
- **Mapping**: Side-by-side comparison table of tachi's four composite dimensions vs AIVSS dimensions (FR-2)
- **Options**: At least three decision options enumerated with pros, cons, "Why Not Chosen" / "Why Chosen" (FR-3)
- **Recommendation**: One option chosen with five-criteria justification (FR-4)
- **ADR-024 commit**: Committed with status **Accepted** at merge (FR-5)
- **SKILL.md update**: AIVSS Relationship section added (FR-6)
- **Follow-on Issue (conditional)**: Filed only if the decision is to adopt (FR-7)

### Should Have (P1)
- ADR-024 cross-references ADR-020 (MAESTRO classification) and any other relevant ADRs surfaced during research
- The mapping table includes a "tachi gap" column noting any AIVSS dimension that has no tachi equivalent
- The Rationale section explicitly addresses CISA KEV alignment, NIST AI RMF alignment, and EU AI Act compliance value (where AIVSS may be referenced by these frameworks)

### Out of Scope (Explicitly Excluded)
- **Implementation of any AIVSS scoring code** — explicitly deferred to follow-on feature if the decision is to adopt
- **Schema changes** to [schemas/risk-scoring.yaml](../../schemas/risk-scoring.yaml) — none in this PRD
- **Agent file changes** under [.claude/agents/tachi/](../../.claude/agents/tachi/) — none in this PRD
- **Script changes** under [scripts/](../../scripts/) — none in this PRD
- **Example output regeneration** under [examples/](../../examples/) — none in this PRD
- **Release-please feat:/fix: commits** — this is documentation-only; commits should be `docs:` per Conventional Commits
- **Updates to README.md or [docs/architecture/00_Tech_Stack/README.md](../../docs/architecture/00_Tech_Stack/README.md)** — only if the ADR specifically requires a cross-reference link (single anchor, not a content rewrite)
- **Decision on AIVSS adoption breadth or scope** beyond what the ADR captures — that is the follow-on feature's job

### Won't Have
- **Comparison to other scoring frameworks** (DREAD, OWASP Risk Rating, FAIR) — out of scope; this ADR is AIVSS-specific
- **Code that produces AIVSS-formatted output** — that is the follow-on feature
- **Migration tooling for existing risk-scores.md outputs** — that is the follow-on feature

### Assumptions
- OWASP AIVSS has a documented specification accessible without authentication (validated during FR-1 research)
- The OWASP AIVSS canonical home is discoverable through standard web search (validated during FR-1 research)
- Tachi's existing four-dimensional composite is the correct comparison baseline (validated against [schemas/risk-scoring.yaml](../../schemas/risk-scoring.yaml) and [scoring-dimensions.md](../../.claude/skills/tachi-risk-scoring/references/scoring-dimensions.md))

### Constraints
- **No production code changes** — this is an ADR-only spike (constitutional principle: backward compatibility)
- **No new runtime dependencies** — documentation-only changes do not add to `requirements*.txt`, `pyproject.toml`, or `package.json`
- **ADR file format** must match existing ADRs (ADR-020 through ADR-023) for consistency
- **Decision must be Accepted at merge** — Proposed-status ADRs do not satisfy the success criterion (per existing ADR conventions in tachi)

---

## Timeline & Milestones

Single-day cycle expected. ADR-only feature. Two implementation waves: Wave 1 = research; Wave 2 = ADR authorship.

| Milestone | Target | Owner | Status |
|-----------|--------|-------|--------|
| PRD Approval | 2026-04-14 | product-manager | In Review |
| Spec Complete | 2026-04-15 | architect (via /aod.spec) | Pending |
| Plan Complete | 2026-04-15 | architect (via /aod.project-plan) | Pending |
| Tasks Complete | 2026-04-15 | team-lead (via /aod.tasks) | Pending |
| ADR-024 Research (FR-1: AIVSS spec discovery, version, URL) | 2026-04-15 | **web-researcher** | Pending |
| ADR-024 Drafted (FR-2 mapping → FR-3 options → FR-4 recommendation → FR-5 commit) | 2026-04-15 | **architect** | Pending |
| SKILL.md Updated (FR-6) | 2026-04-15 | **architect** (same agent as FR-5 to enforce US-143-1 AC-2 verbatim consistency) | Pending |
| Follow-on Issue Filed (conditional, FR-7) | 2026-04-15 | **product-manager** | Pending |
| ADR-024 Reviewed (architect approval = "Accepted at merge" attestation) | 2026-04-15 | architect | Pending |
| PR Merged | 2026-04-16 | team-lead | Pending |

**Agent assignment rationale**: senior-backend-engineer is **not** assigned to any task in this PRD because there are zero backend code changes. FR-1 is a web-research task (external-source discovery with authentication-posture handling for Risk R1); FR-2 through FR-6 are architect-led trade-off analysis and ADR authorship; FR-7 is a product-manager scoping activity (Issue filing).

---

## Risks & Dependencies

### Risk R1 — AIVSS Canonical Home Has Restructured
- **Description**: OWASP's AI-related projects have undergone restructuring; the canonical home of AIVSS may be archived, renamed, or migrated since the parent discovery item was filed
- **Likelihood**: Medium
- **Impact**: Medium — could delay FR-1 research by half a day if the spec is hard to locate
- **Mitigation**: First task of implementation is to confirm the AIVSS canonical home via OWASP's main project listing and capture the URL in the ADR. If the only published artifact is a draft or pre-1.0, the ADR explicitly says so and recommends Option C (divergence with re-evaluation commitment). **A concrete 2-hour timebox** is enforced via tasks.md: if no authoritative AIVSS spec is located after ≤2 hours of canonical-home research, the implementer pauses and escalates to PM for a PRD-close decision (per Risk R1 contingency)
- **Contingency**: If AIVSS is confirmed archived or replaced by another OWASP project, this PRD is closed without delivery and replaced with a new PRD covering the successor framework

### Risk R2 — AIVSS Lacks a Stable 1.0 Specification
- **Description**: AIVSS may still be in pre-1.0 / draft state, in which case adopting it would be premature
- **Likelihood**: Medium-High (per the discovery item watchout)
- **Impact**: Low — the ADR can still be written; the recommendation simply defaults to Option C with a re-evaluation clause
- **Mitigation**: ADR text includes a "When to Re-Evaluate" subsection naming the trigger ("AIVSS publishes a stable 1.0 with at least one external adopter case study"). PM monitors the OWASP AI project list quarterly
- **Contingency**: ADR is committed with Option C and a re-evaluation clause; no other action

### Risk R3 — ADR Decision Is Controversial Among Reviewers
- **Description**: Architect or team-lead may disagree with the recommended option
- **Likelihood**: Low
- **Impact**: Low — disagreement is healthy and the review loop handles it
- **Mitigation**: PRD ships with the trade-off framework (five evaluation criteria); reviewers can challenge the weighting rather than the conclusion. Up to 5 review iterations are budgeted (per `/aod.define` rules)
- **Contingency**: If consensus cannot be reached, escalate to user with the disagreement summarized; user picks the option

### Risk R4 — AIVSS Mapping Reveals a Bug in Tachi's Composite
- **Description**: The dimension comparison may reveal that tachi's existing composite has a methodological flaw (e.g., missing dimension that AIVSS catches; double-counting; etc.)
- **Likelihood**: Low (PRD 035 went through Triad sign-off)
- **Impact**: Medium — could trigger a separate corrective PRD
- **Mitigation**: If a flaw is identified, this PRD's ADR documents it and files a separate corrective Issue (not this PRD's responsibility to fix)
- **Contingency**: This PRD does not change scope; the flaw becomes a new discovery item

### Dependencies
- **No internal dependencies** — this PRD is independent of any in-flight feature
- **External dependency**: Public availability of the OWASP AIVSS specification (Risk R1, R2 cover the contingencies)

---

## Open Questions

- [ ] Will the AIVSS canonical home be confirmed as the OWASP main site, or will research surface an alternative (CSA-hosted, GitHub-hosted)? — **Owner**: implementer (FR-1 task) — **Due**: at draft time — **Status**: Researching
- [ ] If AIVSS is pre-1.0, does the ADR commit to re-evaluation at a specific calendar date or wait for AIVSS to publish 1.0? — **Owner**: PM/Architect — **Due**: at ADR review — **Status**: Open (default: re-evaluate at AIVSS 1.0)

## Closed at PRD Approval

- **Should ADR-024 cross-reference ADR-019 (shared definitions)?** — **Resolution: YES.** ADR-019 governs shared cross-agent definitions; if Option A or Option B is adopted in the follow-on, any new AIVSS-related shared reference (e.g., dimension definitions, score formula) would land under `tachi-shared/` discipline. Cross-referencing ADR-019 in ADR-024's Related ADRs line is required regardless of the decision direction (cross-ref is forward-looking documentation, not a commitment to add a shared ref).
- **Does architect approval during plan/tasks review serve as the ADR "Accepted at merge" attestation?** — **Resolution: YES.** No separate sign-off ceremony is required. The architect's APPROVED verdict on the plan/tasks artifacts (and on the PR review) is the attestation that ADR-024 ships with `Status: Accepted` (not Proposed). This matches the practice for ADR-022 and ADR-023.

---

## References

### Internal
- [Issue #143](https://github.com/davidmatousek/tachi/issues/143) — Discovery item for this PRD
- [Issue #136](https://github.com/davidmatousek/tachi/issues/136) — Umbrella MAESTRO compliance discovery
- [PRD 035 — Quantitative Risk Scoring](035-quantitative-risk-scoring-2026-03-27.md) — Original composite scoring PRD
- [PRD 136 — MAESTRO Canonical Layer Correctness Fix](136-maestro-canonical-layer-correctness-fix-2026-04-10.md) — Phase 1
- [PRD 141 — MAESTRO Cross-Layer Attack Chains](141-maestro-cross-layer-attack-chains-2026-04-12.md) — Phase 2
- [PRD 082 — Threat Agent Skill References](082-threat-agent-skill-references-2026-04-11.md) — Phase 3
- [schemas/risk-scoring.yaml](../../schemas/risk-scoring.yaml) — Current scoring schema (v1.1)
- [.claude/skills/tachi-risk-scoring/](../../.claude/skills/tachi-risk-scoring/) — Scoring skill domain knowledge
- [.claude/skills/tachi-risk-scoring/references/scoring-dimensions.md](../../.claude/skills/tachi-risk-scoring/references/scoring-dimensions.md) — Detailed dimension definitions
- [.claude/agents/tachi/risk-scorer.md](../../.claude/agents/tachi/risk-scorer.md) — Risk scorer agent
- [docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md](../../docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md) — Pattern for cross-referencing
- [docs/architecture/02_ADRs/](../../docs/architecture/02_ADRs/) — ADR home (note: NOT `decisions/`)

### External (To Be Verified During FR-1)
- OWASP AIVSS canonical specification (URL captured during research)
- [CSA Blog: Agentic AI Threat Modeling Framework — MAESTRO (2025-02-06)](https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro)
- [Snyk Labs: MAESTRO — Layered Threat Modeling for Agentic AI Ecosystems](https://labs.snyk.io/resources/maestro-threat-modeling/)
- [Practical DevSecOps: MAESTRO — An Agentic AI Threat Modeling Framework](https://www.practical-devsecops.com/maestro-agentic-ai-threat-modeling-framework/)

---

## Appendix A: ADR-024 Skeleton (For Implementation Reference)

The implementation will produce an ADR roughly matching this skeleton (content TBD by the research and decision):

```markdown
# ADR-024: OWASP AIVSS Evaluation and Tachi Composite Scoring Posture

**Status**: Accepted
**Date**: 2026-04-XX
**Deciders**: Architect, Product Manager, Team-Lead
**Feature**: 143 (MAESTRO Phase 4)
**Related ADRs**: ADR-020 (MAESTRO classification), ADR-019 (shared cross-agent definitions), ADR-018 (baseline-aware pipeline correlation)

---

## Context

[AIVSS specification summary, version, dimensions]
[Tachi composite recap]
[Three-surface comparison: Surface A (dimensions), Surface B (composite formula weights), Surface C (severity band thresholds) — each with Overlap/Gap/Conflict/No-equivalent labels]

---

## Decision

[One-paragraph statement: adopt-as-primary / adopt-as-supplementary / diverge-with-rationale]

---

## Rationale

[Five-criteria justification: maturity, adoption, compatibility, effort, compliance value]
[If diverge: at least two worked examples of score difference]

---

## Alternatives Considered

### Alternative A: Adopt AIVSS as Primary Scoring Replacement
**Pros**: ...
**Cons**: ...
**Why Not Chosen**: ...

### Alternative B: Adopt AIVSS as Supplementary Field
**Pros**: ...
**Cons**: ...
**Why Not Chosen**: ...

### Alternative C: Document Divergence with Rationale
**Pros**: ...
**Cons**: ...
**Why Not Chosen**: ...

(Recommended option includes "Why Chosen" instead of "Why Not Chosen")

---

## Consequences

[If adopt: link to follow-on implementation Issue]
[If diverge: re-evaluation trigger]

---

## When to Re-Evaluate

[Concrete trigger, e.g., "AIVSS publishes stable 1.0 with at least one external adopter case study"]
```
