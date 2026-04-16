---
prd:
  number: 144
  topic: nist-ai-rmf-evaluation-adr
  created: 2026-04-15
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-04-15, status: APPROVED_WITH_CONCERNS, notes: "0 CRITICAL / 0 HIGH / 2 MEDIUM / 5 LOW. C1 (US-144-2 discovery-item re-scope alignment note) fixed inline. C2 (Success Criteria + Metric 4 allow-list expanded to cover SKILL.md edit, tachi-shared/nist-ai-rmf-mapping.md new file, ADR-025 new file, ADR-024 back-ref edit) fixed inline. C3 (Timeline narrative clarified: 1 working day implementation + brief PR cycle). C4-C7 (LOW) deferred to architect/team-lead review or tasks. Best-in-class scope discipline: 5 reinforcing enforcement layers + git-diff post-condition. Quinary unregulated-adopter persona properly protected via US-144-5 byte-identical AC."}
  architect_signoff: {agent: architect, date: 2026-04-15, status: APPROVED_WITH_CONCERNS, notes: "0 CRITICAL / 0 HIGH / 3 MEDIUM / 5 LOW. C1 (FR-5 cross-ref list expanded to add ADR-018, ADR-021, ADR-023) fixed inline. C2 (Metric 4 diff-check wording explicitly permits new files) fixed inline. C3 (R5 Contingency: scope-alignment signal if 'No equivalent' >50% of Generative AI Profile risks) fixed inline. C4-C8 (LOW: FR-6 additive-only invariant, FR-4 ADR-021 determinism gating for Option C, FR-6 reviewer-checklist mechanism, Surface A phase-vs-agent clarification, Option B schema placement preference) deferred to spec/tasks. Three-surface comparison structurally sound. Maturity-analogy guard correctly prevents 'default to diverge by analogy to ADR-024'. SKILL.md target choice (tachi-control-analysis) technically correct. FR-7 conditional artifact shape architecturally sound."}
  techlead_signoff: {agent: team-lead, date: 2026-04-15, status: APPROVED_WITH_CONCERNS, notes: "0 CRITICAL / 1 HIGH / 3 MEDIUM / 4 LOW. HIGH-1 (FR-1 3-hour timebox + scope-reduction fallbacks for Wave 1 overrun) fixed inline in Risk R1. MEDIUM-1 (Timeline section calls out 3-deliverable shape vs PRD 143's 2-deliverable shape) fixed inline. MEDIUM-2 (R5 architect scope-reduction authority for Surface C abbreviation) fixed inline. LOW-1 (Open Question 2 promoted to Closed-at-Approval Q4 with default YES on ADR-024 back-reference edit) fixed inline. LOW-3 (FR-8 milestone row marked 'Pending (N/A if Option A chosen)') fixed inline. MEDIUM-3 (self-review topology footnote) + LOW-2 (Wave 2 sequence) deferred to tasks.md. Two waves: Wave 1 research (3-4h, web-researcher) → Wave 2 authorship (4-6h, architect, ADR→SKILL→tachi-shared sequence). 7-10h total wall-clock vs PRD 143's 4.5-7h actual; 1-day cycle feasible with FR-1 timebox protecting Wave 2. Agent assignments validate against .claude/agents/ — senior-backend-engineer correctly excluded."}
source:
  idea_id: 144
  story_id: null
---

# MAESTRO Companion: NIST AI RMF Integration Evaluation ADR — Product Requirements Document

**Status**: Approved
**Created**: 2026-04-15
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1 (High) — MAESTRO compliance companion (regulated-adopter alignment)
**Parent Discovery**: [#144](https://github.com/davidmatousek/tachi/issues/144) (umbrella discovery [#136](https://github.com/davidmatousek/tachi/issues/136))

---

## Executive Summary

### The One-Liner
Evaluate NIST AI Risk Management Framework (AI RMF) against tachi's compensating controls analyzer and commit the decision as an ADR — documentation-only mapping, shallow wired integration, or deep wired integration — so regulated adopters comparing tachi to other agentic threat modeling tools have a single, traceable answer to "does this support a NIST AI RMF compliance narrative?"

### Problem Statement
Canonical CSA MAESTRO sources reference NIST AI RMF as one of two complementary frameworks for agentic AI risk management (the other is OWASP AIVSS, addressed separately in [PRD 143](143-maestro-aivss-evaluation-adr-2026-04-14.md) / [ADR-024](../../docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md)). Tachi today references neither. There is no ADR explaining the relationship between tachi's compensating controls analyzer and NIST AI RMF Functions (Govern, Map, Measure, Manage), no mapping of tachi control categories to NIST AI RMF Subcategories, and no documented stance for regulated adopters who need NIST alignment to defend tachi adoption to their compliance teams.

A security engineer at a financial services firm cannot justify tachi adoption to their compliance team without being able to point to NIST AI RMF alignment. CISOs in regulated industries (healthcare, finance, public sector), compliance officers reporting to regulators, and security engineers preparing for audits all face the same gap: tachi ships canonical MAESTRO labels (post-PRD 136), cross-layer attack chains (post-PRD 141), agentic threat detection patterns (post-PRD 082), and an AIVSS-divergence ADR (post-PRD 143), but the regulated-adopter leg of the MAESTRO practitioner stool — NIST AI RMF alignment — has no documented stance.

### Proposed Solution
A documentation-first ADR spike. Research the current NIST AI RMF specification (AI RMF 1.0 plus the 2024 Generative AI Profile), build a structured mapping comparing NIST AI RMF Functions / Categories / Subcategories against tachi's compensating controls analyzer surfaces, enumerate at least three options (documentation-only mapping, shallow wired integration tagging compensating controls with NIST references, deep wired integration adding a new analyzer agent), recommend one with justification, and commit the decision as a new ADR (next available number is **ADR-025** at [docs/architecture/02_ADRs/](../../docs/architecture/02_ADRs/)). Add a one-paragraph NIST AI RMF relationship statement to a tachi-shared reference (Option A artifact OR a relationship-only stub for Options B / C). **No production code changes** to the compensating controls pipeline in this PRD — implementation, if the decision is to wire (Option B or C), is an explicit follow-on feature filed as a separate GitHub Issue.

### Success Criteria
- The current NIST AI RMF specification (AI RMF 1.0, January 2023) and the **NIST AI 600-1 Generative AI Profile** (July 2024) are read end-to-end with version numbers captured in the ADR (handle the case where a newer revision has shipped between research and merge — see Risk R1 below)
- A structured three-surface mapping in the ADR Context section compares (A) NIST AI RMF Functions to tachi pipeline phases, (B) NIST AI RMF Subcategories to tachi compensating control categories, and (C) NIST AI RMF Generative AI Profile risks to tachi STRIDE+AI threat categories — each with **Overlap**, **Gap**, **Conflict**, or **No equivalent** labels
- ADR-025 is committed under [docs/architecture/02_ADRs/](../../docs/architecture/02_ADRs/) with at least three evaluated options and one recommended decision; status is **Accepted** at merge time (not Proposed)
- A tachi-shared NIST AI RMF artifact exists post-merge: either [.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md](../../.claude/skills/tachi-shared/references/) (full mapping if Option A) **or** a one-paragraph relationship stub in an existing or new tachi-shared reference linking to ADR-025 (if Options B / C)
- If the decision is **Option B (shallow wired)** or **Option C (deep wired)**: a follow-on implementation feature is filed as a separate GitHub Issue and referenced from the ADR Consequences section
- If the decision is **Option A (docs-only)**: the mapping reference file is the artifact, no follow-on Issue is filed
- Zero changes to [schemas/finding.yaml](../../schemas/finding.yaml), [schemas/risk-scoring.yaml](../../schemas/risk-scoring.yaml), [scripts/](../../scripts/), or `.claude/agents/` **except** the following allow-listed additions: (a) one-paragraph cross-reference appended to [.claude/skills/tachi-control-analysis/SKILL.md](../../.claude/skills/tachi-control-analysis/SKILL.md) (FR-6), (b) new file created at [.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md](../../.claude/skills/tachi-shared/references/) (FR-7), and (c) new file created at `docs/architecture/02_ADRs/ADR-025-*.md` (FR-5) — verified by post-merge `git diff` check
- README.md and [docs/architecture/00_Tech_Stack/README.md](../../docs/architecture/00_Tech_Stack/README.md) are unchanged unless the ADR specifically requires a cross-reference (in which case the change is a single anchor link, not a content rewrite)

### Timeline
~1 working day of active implementation work (research + ADR authorship + SKILL/shared-artifact updates) followed by a brief PR/governance cycle (~half-day). Larger surface area than PRD 143 (AIVSS): AI RMF 1.0 + Generative AI Profile + 4 Functions × multiple Categories × multiple Subcategories — research and authorship effort runs ~50-70% higher than PRD 143's actual delivery time. The 1-day cycle is feasible with the FR-1 timebox (Risk R1 mitigation) protecting Wave 2 authorship from Wave 1 research overrun.

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](../01_Product_Vision/product-vision.md)

Tachi's vision is to be *"the default threat modeling toolkit for any team building agentic AI applications."* The default toolkit must answer the questions that agentic AI security teams in **regulated industries** are actually asking. CSA MAESTRO is the published taxonomy framework; OWASP AIVSS is the published scoring framework practitioners pair with it (addressed in ADR-024); **NIST AI RMF is the published risk-management process framework that regulated adopters must demonstrate alignment with** to justify tachi adoption to compliance, audit, and procurement gates. Shipping canonical MAESTRO labels (PRD 136) and an AIVSS-divergence ADR (ADR-024) without a documented stance on NIST AI RMF leaves a gap that regulated adopters must close themselves — by reading the compensating-controls analyzer agent definition and reverse-engineering whether tachi's controls map to NIST AI RMF Subcategories. A traceable ADR closes that gap with a single linkable decision.

### Roadmap Fit
This is a **MAESTRO compliance companion** to the now-closed Phase 4 ADR-024 (AIVSS evaluation). The umbrella MAESTRO compliance discovery captured in [#136](https://github.com/davidmatousek/tachi/issues/136) is closed as of PRD 143 delivery (2026-04-15), but ADR-024's "Related ADRs" line and the discovery item for #144 explicitly call out NIST AI RMF as the **paired companion framework** that MAESTRO sources reference alongside AIVSS. PRD 144 closes the regulated-adopter half of the MAESTRO companion-framework decision space:

- **Phase 1**: [PRD 136](136-maestro-canonical-layer-correctness-fix-2026-04-10.md) — Canonical layer correctness fix — **Delivered**
- **Phase 2**: [PRD 141](141-maestro-cross-layer-attack-chains-2026-04-12.md) — Cross-layer attack chain analysis — **Delivered**
- **Phase 3**: [PRD 082](082-threat-agent-skill-references-2026-04-11.md) — Threat agent skill references / agentic threat pattern expansion — **Delivered**
- **Phase 4**: [PRD 143](143-maestro-aivss-evaluation-adr-2026-04-14.md) — OWASP AIVSS evaluation ADR — **Delivered**
- **Companion (this PRD)**: NIST AI RMF integration evaluation ADR — **In review**

After PRD 144 closes, the regulated-adopter compliance posture for both MAESTRO companion frameworks is documented and traceable.

### Dependency Posture
- **Independent of any unshipped feature**: this PRD does not require any other feature in flight to land first
- **Does not block any feature in flight**: no downstream feature is waiting on the ADR decision
- **If the ADR decides to wire (Option B or C)**: the follow-on implementation feature should land **after** PRD 136 (already delivered), so canonical MAESTRO layer names are in place when NIST-annotated outputs reference them
- **Schema impact**: zero in this PRD. [schemas/finding.yaml](../../schemas/finding.yaml) and [schemas/risk-scoring.yaml](../../schemas/risk-scoring.yaml) are not modified
- **ADR-024 cross-reference**: ADR-025 cross-references ADR-024 because the two ADRs are companion decisions on MAESTRO-referenced external frameworks; readers landing on either ADR should find the other in the Related ADRs line

---

## Target Users & Personas

### Primary Persona: Compliance Officer at a Regulated Organization
- **Role**: Maps tool outputs to NIST AI RMF Functions, Categories, and Subcategories for regulator reporting (SOC 2, FedRAMP, HIPAA, FFIEC, EU AI Act, sector-specific frameworks that reference NIST AI RMF)
- **Goal**: Build a NIST AI RMF compliance narrative from tachi outputs without manual cross-referencing or commissioning an analyst to reverse-engineer the mapping
- **Pain Point**: Today they must read [.claude/agents/tachi/control-analyzer.md](../../.claude/agents/tachi/control-analyzer.md), [.claude/skills/tachi-control-analysis/references/control-categories.md](../../.claude/skills/tachi-control-analysis/references/control-categories.md), and [.claude/skills/tachi-control-analysis/references/evidence-criteria.md](../../.claude/skills/tachi-control-analysis/references/evidence-criteria.md) and produce their own crosswalk to NIST AI RMF Subcategories — and even then, the answer is "no documented tachi stance"

### Secondary Persona: Security Engineer at a Financial Services Firm
- **Role**: Selects threat modeling tooling that the firm's compliance team will accept
- **Goal**: Justify tachi adoption to compliance by pointing to a public ADR that states tachi's NIST AI RMF posture
- **Pain Point**: Compliance teams in regulated industries treat NIST AI RMF as a baseline expectation for any AI-related security tooling; tachi's silence on it is a procurement blocker even when the tool's threat modeling output quality is strong

### Tertiary Persona: CISO Preparing for a Regulatory Audit
- **Role**: Presents tachi-derived security posture to auditors who use NIST AI RMF vocabulary
- **Goal**: Reference NIST AI RMF Subcategories directly in tachi PDF security report citations rather than translating tachi's STRIDE+AI categories into NIST vocabulary on the fly during the audit
- **Pain Point**: Translation work during an audit is high-risk (errors invite findings); a documented mapping or wired integration removes the translation step from the critical path

### Quaternary Persona: Tachi Maintainer (Future)
- **Role**: Future contributor considering changes to the compensating controls analyzer
- **Goal**: Have a traceable baseline for "why does tachi reference (or not reference) NIST AI RMF in compensating controls?" before proposing modifications
- **Pain Point**: With no ADR, future control-analyzer changes risk silently diverging from regulated-adopter expectations because the original posture was undocumented

### Quinary Persona: Security Engineer in an Unregulated Environment
- **Role**: Adopts tachi for general-purpose agentic AI threat modeling, no compliance pressure
- **Goal**: NIST AI RMF integration must be optional and non-disruptive — pipeline output should be unchanged for adopters who don't need NIST alignment
- **Pain Point**: A wired integration that forces NIST vocabulary into every output increases reading overhead for adopters who don't need it; this PRD's success criteria explicitly require no production pipeline changes in the ADR-only scope (and any follow-on Option B / C implementation must be opt-in or non-disruptive by design)

---

## User Stories

### US-144-1: Compliance Officer NIST Mapping Decision
**When** I am a compliance officer at a regulated organization deciding whether to report tachi outputs directly or translate them to NIST AI RMF Subcategories,
**I want to** read a single ADR that states tachi's NIST AI RMF posture (docs-only mapping, shallow wired, or deep wired) with a structured mapping table,
**So I can** make the report-vs-translate decision based on a documented tachi stance rather than reverse-engineering the compensating controls analyzer.

**Acceptance Criteria**:
- **Given** ADR-025 is committed and visible in [docs/architecture/02_ADRs/](../../docs/architecture/02_ADRs/), **when** a compliance officer opens the ADR, **then** the Decision section answers "what is tachi's NIST AI RMF posture?" in the first paragraph
- **Given** the ADR is committed, **when** the compliance officer reads the Context section, **then** the three-surface mapping table is present (NIST AI RMF Functions × tachi pipeline phases; NIST AI RMF Subcategories × tachi compensating control categories; NIST AI RMF Generative AI Profile risks × tachi STRIDE+AI categories) with every row annotated with one of: **Overlap**, **Gap**, **Conflict**, or **No equivalent**
- **Given** the compliance officer copies the ADR URL into a regulator-facing report, **when** they do so, **then** the URL points to a stable file path under `docs/architecture/02_ADRs/ADR-025-*.md` (not a draft, not a comment, not a PR review URL)

**Priority**: P0
**Effort**: M

### US-144-2: Security Engineer Procurement Justification
**When** I am a security engineer at a regulated firm needing to justify tachi adoption to my compliance team,
**I want to** read a public ADR confirming tachi's awareness of NIST AI RMF and stating its alignment posture,
**So I can** point to an authoritative source rather than committing tachi's maintainer to an answer over email.

> **Discovery-item alignment note**: The discovery item's second user story originally referenced *"flagging NIST AI RMF control gaps so I can prioritize remediation."* That outcome is an Option B/C *implementation-level* capability (not an ADR-level deliverable) and is captured in the FR-8 follow-on Issue acceptance criteria when wired integration is the chosen option. The ADR-level outcome — what this PRD delivers — is the procurement-justification ADR itself, which unlocks the wired-integration follow-on if and only if the recommendation is Option B or C.

**Acceptance Criteria**:
- **Given** ADR-025 is committed, **when** the security engineer searches for "NIST AI RMF" in [docs/architecture/02_ADRs/](../../docs/architecture/02_ADRs/), **then** ADR-025 is the only ADR whose Decision section addresses NIST AI RMF (other ADRs may mention NIST AI RMF only as a cross-reference to ADR-025)
- **Given** ADR-025 is committed, **when** the security engineer follows the cross-reference from [tachi-control-analysis/SKILL.md](../../.claude/skills/tachi-control-analysis/SKILL.md), **then** the NIST AI RMF Relationship paragraph in SKILL.md matches the ADR decision verbatim (single source of truth, no drift) — analogous to ADR-024 ↔ tachi-risk-scoring/SKILL.md pattern
- **Given** the security engineer presents the ADR to their compliance team, **when** the team reads it, **then** the recommended option's compliance value for regulated adopters is explicitly addressed in the Rationale section

**Priority**: P0
**Effort**: S

### US-144-3: CISO Audit Preparation
**When** I am a CISO preparing tachi-derived output for a regulatory audit using NIST AI RMF vocabulary,
**I want to** reference the tachi-shared NIST AI RMF mapping artifact (or the Option A mapping file directly),
**So I can** cite NIST AI RMF Subcategories alongside tachi findings without inventing my own crosswalk during the audit.

**Acceptance Criteria**:
- **Given** the chosen option is **A (docs-only)**, **when** a CISO opens [.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md](../../.claude/skills/tachi-shared/references/), **then** the file contains a complete mapping table covering all tachi compensating control categories to their NIST AI RMF Subcategory equivalents
- **Given** the chosen option is **B or C**, **when** the CISO reads the tachi-shared NIST AI RMF relationship stub, **then** the stub names the wired-integration site (compensating controls schema for Option B; new analyzer agent for Option C) and links to the follow-on implementation Issue
- **Given** any chosen option, **when** the CISO follows references from the tachi-shared artifact back to ADR-025, **then** the link uses a relative path resolvable on `main` (no draft URLs, no PR-review URLs, no absolute filesystem paths)

**Priority**: P1
**Effort**: S

### US-144-4: Maintainer Decision Traceability
**When** I am a future tachi maintainer considering changes to the compensating controls analyzer or proposing a new NIST-aware analyzer agent,
**I want to** find a single ADR that documents the original NIST AI RMF decision with the options that were considered,
**So I can** evaluate whether the proposed change is consistent with prior reasoning or constitutes a deliberate reversal.

**Acceptance Criteria**:
- **Given** ADR-025 is committed, **when** a future maintainer reads the Alternatives Considered section, **then** at least three options are enumerated (Option A docs-only mapping; Option B shallow wired tagging; Option C deep wired analyzer agent) with pros, cons, and a "Why Not Chosen" explanation for each non-recommended option
- **Given** ADR-025 is committed, **when** the maintainer reads the Status field, **then** it reads **Accepted** (not Proposed) at merge time
- **Given** the maintainer needs to understand the relationship between ADR-024 (AIVSS) and ADR-025 (NIST AI RMF), **when** they read either ADR's Related ADRs line, **then** the other ADR is referenced as a companion MAESTRO framework decision

**Priority**: P1
**Effort**: S

### US-144-5: Unregulated Adopter Non-Disruption
**When** I am a security engineer in an unregulated environment using tachi for general agentic threat modeling,
**I want to** confirm that the NIST AI RMF ADR does not change tachi's pipeline output or impose NIST vocabulary on my reports,
**So I can** continue using tachi as a lightweight tool without compliance overhead.

**Acceptance Criteria**:
- **Given** ADR-025 is merged, **when** a security engineer in an unregulated environment runs `/tachi.threat-model` and `/tachi.compensating-controls` on their architecture, **then** the produced `threats.md`, `risk-scores.md`, and `compensating-controls.md` outputs are byte-identical to pre-ADR-025 outputs (verified by [tests/scripts/test_backward_compatibility.py](../../tests/scripts/test_backward_compatibility.py))
- **Given** the chosen option is **B or C**, **when** the follow-on implementation Issue is filed, **then** the Issue body explicitly names "non-disruptive" or "opt-in" as a constraint for the implementation

**Priority**: P1
**Effort**: S

---

## Functional Requirements

### Core Capabilities

#### FR-1: NIST AI RMF Specification Research
**Description**: Read the current NIST AI RMF specification end-to-end (AI RMF 1.0 plus the 2024 Generative AI Profile, NIST AI 600-1), capture version numbers, list Functions / Categories / Subcategories, and document the relationship between AI RMF 1.0 and the Generative AI Profile.

**Inputs**: Public NIST documentation: [NIST AI RMF 1.0 (NIST AI 100-1)](https://www.nist.gov/itl/ai-risk-management-framework) and [NIST AI 600-1 Generative AI Profile (July 2024)](https://www.nist.gov/itl/ai-risk-management-framework) (canonical URLs to be confirmed during research — see Risk R1)
**Processing**: Read, summarize, capture version metadata; enumerate the four Functions (Govern, Map, Measure, Manage), their Categories, and a representative sample of Subcategories relevant to agentic AI
**Outputs**: A research summary embedded in the ADR Context section, capturing: NIST AI RMF version (1.0 + Profile version), URLs of canonical specifications, the Function / Category / Subcategory hierarchy, and notes on which parts of the framework are most relevant to tachi's compensating controls analyzer

**Business Rules**:
- The canonical home of NIST AI RMF is confirmed during research (NIST has a stable URL but documents are versioned independently)
- The Generative AI Profile (NIST AI 600-1) is treated as the agentic-AI-relevant overlay — its risks (CBRN information, confabulation, dangerous/violent/hateful content, data privacy, etc.) map most directly to tachi's STRIDE+AI threat categories
- The version numbers captured in the ADR match the specification versions observed at research time (date-stamped)
- If a newer NIST AI RMF revision has shipped since this PRD was filed, the ADR notes the latest version available at research time and flags any material change in scope

#### FR-2: Three-Surface Comparison Across NIST AI RMF and Tachi
**Description**: Build a three-surface comparison covering NIST AI RMF's process-framework structure versus tachi's threat-detection-plus-controls-analysis structure. A single-surface comparison would either over-simplify NIST AI RMF's hierarchy (Functions → Categories → Subcategories) or miss the structural divergence between a process framework (NIST AI RMF) and a detection-plus-scoring pipeline (tachi).

**Inputs**: Tachi's pipeline phases from [.claude/agents/tachi/orchestrator.md](../../.claude/agents/tachi/orchestrator.md), compensating control categories from [.claude/skills/tachi-control-analysis/references/control-categories.md](../../.claude/skills/tachi-control-analysis/references/control-categories.md), threat categories from [.claude/skills/tachi-shared/references/stride-categories-shared.md](../../.claude/skills/tachi-shared/references/stride-categories-shared.md); NIST AI RMF equivalents from FR-1 research

**Processing**: Three labeled comparison subsections in the ADR Context section, each annotated with relationship labels (Overlap, Gap, Conflict, No equivalent)

**Outputs**: Three Markdown tables (or three subsections) in the ADR Context section:
- **Surface A — Functions × Pipeline Phases**: one row per NIST AI RMF Function (Govern, Map, Measure, Manage) mapped to tachi pipeline phases (orchestration, threat detection, risk scoring, compensating-controls analysis, threat reporting)
- **Surface B — Subcategories × Tachi Compensating Control Categories**: a sample of NIST AI RMF Subcategories (drawn from the most agentic-AI-relevant Categories under each Function) mapped to tachi compensating control categories
- **Surface C — Generative AI Profile Risks × Tachi STRIDE+AI Categories**: NIST AI 600-1 Generative AI Profile risks (CBRN, confabulation, content harms, data privacy, environmental, human-AI configuration, IP, obscene/abusive content, info security, info integrity, value chain, AI lifecycle) mapped to tachi STRIDE+AI categories (spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, agentic, llm)

**Business Rules**:
- Every NIST AI RMF Function appears in Surface A with a non-ambiguous relationship label (no "TBD" or "unclear")
- Surface B does **not** require exhaustive Subcategory coverage (that is the work of an Option A docs-only mapping in the FOLLOW-on artifact); a representative sample (5–10 Subcategories) suffices for the ADR
- Surface C must address all Generative AI Profile risks listed in NIST AI 600-1 §2 (do not silently elide risks that have no tachi equivalent — annotate as "No equivalent")
- Conflicts (same name, different meaning) are called out explicitly with a one-line explanation each
- The mapping does **not** silently elide structural divergence (process framework vs detection pipeline) behind a "categories overlap" headline

#### FR-3: Options Enumeration
**Description**: Enumerate at least three decision options with pros, cons, and trade-off analysis.

**Inputs**: Mapping from FR-2; project constraints (zero-dependency runtime per repo conventions, deterministic pipeline per ADR-021, agent-decomposition pattern per ADR-023, ADR-024 AIVSS-divergence precedent for "diverge by default when external framework is pre-1.0 or low-adoption")

**Processing**: Structured options analysis

**Outputs**: ADR Alternatives Considered section with at least three options:
- **Option A — Documentation-only mapping**: A new reference file at `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` containing a full Subcategory-to-tachi-control-category mapping table. No schema changes, no agent changes, no script changes. Adopters do their own runtime alignment using the mapping.
- **Option B — Shallow wired integration**: Extend [schemas/finding.yaml](../../schemas/finding.yaml) (or a dedicated controls schema) to optionally reference NIST AI RMF Subcategories on compensating controls. Update [.claude/agents/tachi/control-analyzer.md](../../.claude/agents/tachi/control-analyzer.md) to tag controls with NIST references where applicable. The PDF security report surfaces NIST references in the controls section when present. Backward compatible: existing outputs unchanged when NIST tags are absent.
- **Option C — Deep wired integration**: Add a new agent (`.claude/agents/tachi/nist-ai-rmf-analyzer.md`) that runs after the compensating controls analyzer and produces a dedicated NIST AI RMF coverage report (`nist-ai-rmf-coverage.md`). New schema artifact, new output file, new PDF page in the security report. Largest change to the pipeline.
- Additional options may be added if research surfaces them (e.g., a hybrid Option B+C tagging-plus-coverage-report)

**Business Rules**:
- Each option includes pros, cons, and a "Why Not Chosen" rationale (for non-recommended options) or a "Why Chosen" rationale (for the recommended option)
- Each option's effort estimate is concrete (S/M/L with rough day estimate) — Option A is S (single docs file + ADR), Option B is M (schema bump + agent update + template update + example regen), Option C is L (new agent + new schema + new template + new pipeline phase + example regen)
- Each option's compliance value for regulated adopters is explicitly addressed
- Each option's pipeline determinism impact is addressed (Option A and B preserve ADR-021 determinism with zero changes; Option C requires verifying determinism is preserved when the new analyzer agent runs)

#### FR-4: Recommendation with Justification
**Description**: Pick one option with a defensible justification considering NIST AI RMF maturity, adoption in the regulated-adopter market, compatibility with the current compensating controls analyzer, effort to wire in, and compliance value for tachi's target adopter base.

**Inputs**: Options from FR-3

**Processing**: Trade-off analysis using the five evaluation criteria (mirroring the ADR-024 framework for cross-ADR consistency)

**Outputs**: ADR Decision and Rationale sections naming the chosen option and justifying it

**Business Rules**:
- The justification addresses all five evaluation criteria (maturity, adoption, compatibility, effort, compliance value)
- If the recommended option is **B or C** (wired), the Consequences section names the follow-on implementation feature and links to its GitHub Issue (filed as part of this PRD's delivery)
- If the recommended option is **A** (docs-only), the Rationale explicitly addresses why a wired integration is not warranted at this time — informed by signals such as: tachi's current adopter base is dominated by general-purpose adopters not regulated-industry adopters; the docs-only mapping is sufficient for an adopter to do their own NIST crosswalk; a wired integration adds reading overhead for non-regulated adopters; the pre-1.0 caution that ADR-024 applied to AIVSS does **not** apply here because NIST AI RMF 1.0 is stable and NIST AI 600-1 Generative AI Profile is a final document
- The recommendation's compatibility section explicitly addresses ADR-021 (determinism), ADR-023 (agent-shape decomposition), and ADR-024 (companion-framework precedent)

#### FR-5: ADR-025 Commit
**Description**: Commit the decision as ADR-025 in the established ADR format under [docs/architecture/02_ADRs/](../../docs/architecture/02_ADRs/).

**Inputs**: All sections from FR-1 through FR-4

**Processing**: Format per existing ADR conventions (see ADR-020, ADR-021, ADR-022, ADR-023, ADR-024 for shape — ADR-024 is the closest structural analog)

**Outputs**: New file `docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md`

**Business Rules**:
- File path matches `docs/architecture/02_ADRs/ADR-025-*.md`
- Status field reads **Accepted** at merge time (not Proposed)
- Date field reads the merge date (not the draft date)
- Cross-references at minimum: ADR-024 (companion AIVSS evaluation), ADR-020 (MAESTRO classification), ADR-019 (shared cross-agent definitions), **ADR-018 (baseline-aware pipeline lineage — relevant if Option B/C extends the controls baseline), ADR-021 (SOURCE_DATE_EPOCH determinism — any wired integration must preserve byte-determinism), ADR-023 (threat-agent skill-references pattern — Option C follow-on agent must use the lean+skill-references decomposition)**, and the broader compensating-controls lineage if applicable (PRD 036)

#### FR-6: SKILL.md Cross-Reference Update
**Description**: Add a one-paragraph NIST AI RMF Relationship section to [.claude/skills/tachi-control-analysis/SKILL.md](../../.claude/skills/tachi-control-analysis/SKILL.md) (analogous to the AIVSS Relationship section ADR-024 added to `tachi-risk-scoring/SKILL.md`).

**Inputs**: ADR-025 decision text

**Processing**: Insert a new section (recommended placement: after "Domain Overview", before any specific control-analysis methodology section); link to ADR-025 by relative path

**Outputs**: Updated SKILL.md with the new section

**Business Rules**:
- The paragraph mirrors the ADR Decision in plain language (no contradictions; if the ADR says "docs-only" the SKILL must not imply wired integration)
- The paragraph contains an explicit link to ADR-025 by relative path
- The paragraph length is between 80 and 200 words (not a deep dive; pointer to the ADR — same constraint as ADR-024 → tachi-risk-scoring/SKILL.md)
- Decision-noun consistency between ADR-025 and SKILL.md is verified at PR time (e.g., if the ADR uses the noun phrase "documentation-only mapping", SKILL.md uses the same noun phrase — no synonyms)

#### FR-7: Tachi-Shared NIST AI RMF Artifact (Conditional Shape)
**Description**: Create or update a tachi-shared NIST AI RMF artifact whose content depends on the chosen option.

**Inputs**: ADR decision

**Processing**:
- **If Option A (docs-only)**: Create `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` containing the full Subcategory-to-tachi-control-category mapping table (the Option A artifact). This file becomes the canonical NIST AI RMF mapping for adopters.
- **If Option B (shallow wired)** or **Option C (deep wired)**: Create the same `nist-ai-rmf-mapping.md` file but populate it with a relationship-only stub (one paragraph + a forward reference to the follow-on implementation Issue and to ADR-025). The full mapping is deferred to the follow-on implementation feature (Option B: it lives in the controls schema documentation; Option C: it lives in the new analyzer agent's reference files).

**Outputs**: New file `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` with content shape determined by the chosen option

**Business Rules**:
- The file exists post-merge regardless of chosen option (per discovery item: "Shared reference (`tachi-shared/references/`) updated with a one-paragraph NIST AI RMF relationship statement regardless of chosen option")
- The file links to ADR-025 by relative path
- The file is **additive only** — does not modify any existing tachi-shared reference (no edits to `finding-format-shared.md`, `stride-categories-shared.md`, etc.)
- For Option A, the mapping table is renderable in standard Markdown (no extensions required)

#### FR-8: Follow-On Issue (Conditional)
**Description**: If the decision is to wire (Option B or Option C), file a follow-on implementation feature as a separate GitHub Issue and reference it from the ADR Consequences section.

**Inputs**: ADR decision

**Processing**: Use `bash .aod/scripts/bash/create-issue.sh` (see [.aod/scripts/bash/](../../.aod/scripts/bash/)) to create a new Issue with `stage:discover` label and ICE score scoped to implementation effort

**Outputs**: A new GitHub Issue number referenced in ADR-025

**Business Rules**:
- Only fired if the recommended decision is Option B (shallow wired) or Option C (deep wired)
- The Issue title is concrete: e.g., "Implement NIST AI RMF compensating-control tagging (per ADR-025)" for Option B, or "Implement NIST AI RMF coverage analyzer agent (per ADR-025)" for Option C
- The Issue body links back to ADR-025 and **at minimum names the surfaces that would change in implementation** — for Option B: `schemas/finding.yaml` (or new controls schema), `.claude/agents/tachi/control-analyzer.md`, `templates/tachi/security-report/compensating-controls.typ`, example regen; for Option C: new `.claude/agents/tachi/nist-ai-rmf-analyzer.md`, new schema, new template page, new pipeline phase, example regen
- The Issue body **includes the option-specific effort estimate** copied verbatim from the ADR-025 Alternatives Considered section for the chosen option (Option B and Option C have materially different effort profiles)
- If the decision is Option A (docs-only), this FR is skipped — no follow-on Issue is filed (analogous to ADR-024 Option C)

### Out-of-Scope Functional Requirements (Explicitly Excluded)

- **No changes to [schemas/finding.yaml](../../schemas/finding.yaml) or [schemas/risk-scoring.yaml](../../schemas/risk-scoring.yaml)** — schema bumps are an implementation concern, not an ADR concern
- **No changes to [.claude/agents/tachi/control-analyzer.md](../../.claude/agents/tachi/control-analyzer.md) or any other agent file** — agents are unchanged by this ADR
- **No new agent file `.claude/agents/tachi/nist-ai-rmf-analyzer.md`** — that is Option C's follow-on implementation, not part of this PRD
- **No changes to scoring or controls scripts under [scripts/](../../scripts/)** — runtime is unchanged
- **No regeneration of example outputs** under [examples/](../../examples/) — outputs are unchanged
- **No release-please version bump beyond what an ADR file addition would naturally trigger** — ADR-only changes typically land as a `docs:` commit, not a `feat:` or `fix:`

---

## Non-Functional Requirements

### Documentation Quality
- ADR follows the structural pattern established by ADR-020 through ADR-024 (Context, Decision, Rationale, Alternatives Considered, Consequences sections at minimum)
- Mapping tables are renderable in standard Markdown (no extensions required)
- All cross-references use relative paths (no absolute paths or external URLs except for the NIST canonical specification links)

### Traceability
- ADR-025 references the parent discovery item ([#144](https://github.com/davidmatousek/tachi/issues/144)) and the umbrella MAESTRO compliance discovery ([#136](https://github.com/davidmatousek/tachi/issues/136))
- ADR-025 cross-references ADR-024 (companion AIVSS evaluation) at minimum
- The follow-on implementation Issue (if filed) references ADR-025 as its decision baseline
- ADR-024's "Related ADRs" line **may** be updated to add ADR-025 as a back-reference (optional housekeeping; not required for ADR-025 to ship)

### Accessibility / Audit
- ADR-025 is committed under version control (Git history is the audit trail)
- ADR Status field is unambiguous: **Accepted** at merge, dated to merge day
- Future maintainers can find the NIST AI RMF decision via either: search ADRs for "NIST AI RMF", search tachi-control-analysis/SKILL.md for "NIST AI RMF", or follow the chain from ADR-024 (companion framework cross-reference)

### Backward Compatibility
- All five existing example outputs ([examples/web-app/](../../examples/web-app/), [examples/microservices/](../../examples/microservices/), [examples/ascii-web-api/](../../examples/ascii-web-api/), [examples/mermaid-agentic-app/](../../examples/mermaid-agentic-app/), [examples/free-text-microservice/](../../examples/free-text-microservice/)) remain byte-identical to their pre-ADR-025 versions when regenerated under `SOURCE_DATE_EPOCH=1700000000` (per ADR-021)
- The agentic-app example baseline (regenerated by Feature 128) remains valid; ADR-025 does not invalidate it
- Existing `tests/scripts/test_backward_compatibility.py` passes 5/5 byte-identical against committed baselines

---

## Success Metrics

### Primary Metrics

**Metric 1**: ADR-025 committed and merged with status **Accepted**
- **Definition**: Boolean — file exists at `docs/architecture/02_ADRs/ADR-025-*.md` on `main` with Status: Accepted
- **Baseline**: 0 (no NIST AI RMF ADR exists today)
- **Target**: 1
- **Timeline**: At PRD delivery
- **Owner**: product-manager (delivery), architect (review)

**Metric 2**: tachi-control-analysis/SKILL.md NIST AI RMF Relationship section present
- **Definition**: Boolean — `.claude/skills/tachi-control-analysis/SKILL.md` contains a section titled "NIST AI RMF Relationship" (or equivalent) with a link to ADR-025
- **Baseline**: 0 (no NIST AI RMF mention in SKILL.md today)
- **Target**: 1
- **Timeline**: At PRD delivery
- **Owner**: product-manager (decision noun consistency check at PR time)

**Metric 3**: tachi-shared NIST AI RMF artifact present
- **Definition**: Boolean — `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` exists post-merge with content shape matching the chosen option
- **Baseline**: 0 (file does not exist today)
- **Target**: 1
- **Timeline**: At PRD delivery
- **Owner**: architect (FR-7)

### Secondary Metrics

**Metric 4**: Zero unintended drift in pipeline outputs
- **Definition**: `git diff main..feature-branch -- schemas/ scripts/ .claude/agents/ examples/` returns empty. Allowed additive exceptions outside that diff scope: (a) `.claude/skills/tachi-control-analysis/SKILL.md` adds the FR-6 paragraph (existing file edit), (b) new file `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` (FR-7 artifact), (c) new file `docs/architecture/02_ADRs/ADR-025-*.md` (FR-5 ADR), and (d) one-line edit to `docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md` Related ADRs line adding back-reference to ADR-025
- **Baseline**: 0 lines changed expected in `schemas/`, `scripts/`, `.claude/agents/`, `examples/`
- **Target**: 0 lines changed actual in those four scopes
- **Timeline**: At PR review
- **Owner**: code-reviewer

**Metric 5**: Follow-on Issue filed (conditional)
- **Definition**: If ADR decides Option B or C, a new GitHub Issue exists with `stage:discover` label referencing ADR-025
- **Baseline**: 0
- **Target**: 1 if Option B/C; 0 if Option A
- **Timeline**: At PRD delivery
- **Owner**: product-manager

**Metric 6**: Backward-compatibility test green
- **Definition**: `pytest tests/scripts/test_backward_compatibility.py` returns 5/5 passing
- **Baseline**: 5/5 passing (current state)
- **Target**: 5/5 passing post-merge
- **Timeline**: At PR review
- **Owner**: code-reviewer

### Lagging Metrics (Tracked Post-Delivery)

- Number of times ADR-025 is cited externally (procurement briefs, audit reports, regulator-facing documents) — qualitative
- Number of times the follow-on implementation Issue (if filed) is upvoted or commented on — used to inform priority of follow-on work
- Number of regulated-industry adopter inquiries that reference ADR-025 by URL — qualitative signal of regulated-adopter market engagement

---

## Scope & Boundaries

### In Scope (Must Have, P0)
- **Research**: Read the current NIST AI RMF specification (AI RMF 1.0 + Generative AI Profile NIST AI 600-1) with versions captured (FR-1)
- **Mapping**: Three-surface comparison in the ADR Context section (FR-2): Functions × Pipeline Phases, Subcategories × Compensating Control Categories, Generative AI Profile Risks × STRIDE+AI Categories
- **Options**: At least three decision options enumerated with pros, cons, "Why Not Chosen" / "Why Chosen" (FR-3)
- **Recommendation**: One option chosen with five-criteria justification (FR-4)
- **ADR-025 commit**: Committed with status **Accepted** at merge (FR-5)
- **SKILL.md update**: NIST AI RMF Relationship section added to `tachi-control-analysis/SKILL.md` (FR-6)
- **Tachi-shared artifact**: `nist-ai-rmf-mapping.md` created with content shape matching chosen option (FR-7)
- **Follow-on Issue (conditional)**: Filed only if the decision is to wire (Option B or C, per FR-8)

### Should Have (P1)
- ADR-025 cross-references ADR-024 (companion AIVSS), ADR-020 (MAESTRO classification), and ADR-019 (shared definitions)
- The mapping tables include a "tachi gap" column noting any NIST AI RMF Subcategory or Generative AI Profile risk that has no tachi equivalent
- The Rationale section explicitly addresses sector-specific compliance value (SOC 2, FedRAMP, HIPAA, FFIEC, EU AI Act mentions where NIST AI RMF is referenced by these frameworks)
- ADR-024's "Related ADRs" line is updated to add ADR-025 as a back-reference (housekeeping; not blocking)

### Out of Scope (Explicitly Excluded)
- **Implementation of any NIST AI RMF wired integration** — explicitly deferred to follow-on feature if the decision is Option B or C
- **Schema changes** to [schemas/finding.yaml](../../schemas/finding.yaml) or [schemas/risk-scoring.yaml](../../schemas/risk-scoring.yaml) — none in this PRD
- **New agent file** `.claude/agents/tachi/nist-ai-rmf-analyzer.md` — that is Option C's follow-on, not this PRD
- **Agent file changes** under [.claude/agents/tachi/](../../.claude/agents/tachi/) — none in this PRD (tachi-control-analysis/SKILL.md is a skill, not an agent)
- **Script changes** under [scripts/](../../scripts/) — none in this PRD
- **Example output regeneration** under [examples/](../../examples/) — none in this PRD
- **Release-please feat:/fix: commits** — this is documentation-only; commits should be `docs:` per Conventional Commits
- **Updates to README.md or [docs/architecture/00_Tech_Stack/README.md](../../docs/architecture/00_Tech_Stack/README.md)** — only if the ADR specifically requires a cross-reference link (single anchor, not a content rewrite)
- **Decision on NIST AI RMF wired-integration breadth or scope** beyond what the ADR captures — that is the follow-on feature's job

### Won't Have
- **Comparison to other process frameworks** (ISO/IEC 23894, ISO/IEC 42001, EU AI Act high-risk system requirements) — out of scope; this ADR is NIST-AI-RMF-specific
- **Code that produces NIST-AI-RMF-formatted output** — that is the follow-on feature
- **Migration tooling for existing compensating-controls.md outputs** — that is the follow-on feature
- **A NIST CSF (Cybersecurity Framework) mapping** — distinct framework; out of scope. NIST CSF is a separate document from NIST AI RMF and is not addressed by this PRD even though both are NIST publications.

### Assumptions
- NIST AI RMF 1.0 (NIST AI 100-1) and NIST AI 600-1 (Generative AI Profile) are stable and accessible without authentication (validated during FR-1 research)
- NIST publishes its AI RMF documents at stable URLs that can be cited in the ADR (validated during FR-1 research)
- Tachi's existing compensating controls analyzer architecture (control categories + evidence criteria + residual risk) is the correct comparison baseline (validated against [.claude/skills/tachi-control-analysis/](../../.claude/skills/tachi-control-analysis/) and [.claude/agents/tachi/control-analyzer.md](../../.claude/agents/tachi/control-analyzer.md))
- The discovery item's three-option enumeration (A docs-only, B shallow wired, C deep wired) is a reasonable starting point; FR-3 may add a hybrid option if research surfaces one (e.g., Option B+C tagging-plus-coverage-report)

### Constraints
- **No production code changes** — this is an ADR-only spike (constitutional principle: backward compatibility per Constitution III)
- **No new runtime dependencies** — documentation-only changes do not add to `requirements*.txt`, `pyproject.toml`, or `package.json`
- **ADR file format** must match existing ADRs (ADR-020 through ADR-024) for consistency
- **Decision must be Accepted at merge** — Proposed-status ADRs do not satisfy the success criterion (per existing ADR conventions in tachi)
- **Companion-framework precedent**: ADR-024 (AIVSS) chose to diverge in part because AIVSS is pre-1.0; NIST AI RMF 1.0 is stable, so the maturity criterion does **not** automatically default this ADR to "diverge". The recommendation is reasoned afresh from the FR-2 mapping and FR-4 trade-offs.

---

## Timeline & Milestones

Single-day implementation cycle with brief PR/governance follow-up. ADR-only feature with **3 deliverables** (ADR-025, SKILL.md update, tachi-shared NIST AI RMF artifact) vs PRD 143's 2 deliverables (ADR-024 + SKILL.md update only) — the FR-7 tachi-shared artifact is the new addition for PRD 144. Larger surface area than ADR-024 because NIST AI RMF has 4 Functions × multiple Categories × multiple Subcategories plus the Generative AI Profile (NIST AI 600-1). Two implementation waves: Wave 1 = research (FR-1, web-researcher); Wave 2 = ADR authorship + tachi-shared artifact + SKILL.md update (FR-2 through FR-7, architect, in that explicit sequence to ensure SKILL.md and tachi-shared artifact reference the *final* ADR decision text rather than draft text).

| Milestone | Target | Owner | Status |
|-----------|--------|-------|--------|
| PRD Approval | 2026-04-15 | product-manager | In Review |
| Spec Complete | 2026-04-16 | architect (via /aod.spec) | Pending |
| Plan Complete | 2026-04-16 | architect (via /aod.project-plan) | Pending |
| Tasks Complete | 2026-04-16 | team-lead (via /aod.tasks) | Pending |
| ADR-025 Research (FR-1: NIST AI RMF spec discovery, version, URL, Function/Category/Subcategory enumeration) | 2026-04-16 | **web-researcher** | Pending |
| ADR-025 Drafted (FR-2 mapping → FR-3 options → FR-4 recommendation → FR-5 commit) | 2026-04-16 | **architect** | Pending |
| Tachi-shared artifact created (FR-7) | 2026-04-16 | **architect** (same agent as FR-5 for decision-noun consistency) | Pending |
| SKILL.md updated (FR-6) | 2026-04-16 | **architect** (same agent as FR-5 to enforce US-144-2 AC-2 verbatim consistency) | Pending |
| Follow-on Issue filed (conditional, FR-8) | 2026-04-16 | **product-manager** | Pending (N/A if Option A chosen) |
| ADR-024 Related ADRs line back-reference edit (per Closed-at-Approval Q4) | 2026-04-16 | **architect** (single-line edit; ships in same PR) | Pending |
| ADR-025 reviewed (architect approval = "Accepted at merge" attestation) | 2026-04-16 | architect | Pending |
| PR Merged | 2026-04-17 | team-lead | Pending |

**Agent assignment rationale**: senior-backend-engineer is **not** assigned to any task in this PRD because there are zero backend code changes. FR-1 is a web-research task (external-source discovery with version-stability handling for Risk R1); FR-2 through FR-7 are architect-led trade-off analysis, ADR authorship, and tachi-shared artifact creation; FR-8 is a product-manager scoping activity (Issue filing). Same agent assignment shape as PRD 143.

---

## Risks & Dependencies

### Risk R1 — Wave 1 Research Surface Overrun (NIST AI RMF Revision Drift OR Hierarchy Enumeration Time)
- **Description**: Two intertwined sub-risks:
  - **R1a (revision drift)**: NIST publishes AI RMF documents on its own cadence; a newer revision (e.g., AI RMF 1.1 or a newer Generative AI Profile) may have shipped between this PRD's filing and FR-1 research
  - **R1b (research surface)**: The total research surface (AI RMF 1.0 + NIST AI 600-1 end-to-end + Function/Category/Subcategory enumeration + Generative AI Profile risks enumeration) takes longer than expected and squeezes Wave 2 authorship time
- **Likelihood**: Low-Medium for R1a; Medium for R1b
- **Impact**: Low for R1a (the ADR captures whichever version is current at research time); Medium for R1b (compresses Wave 2 below safe margin for a 1-day cycle)
- **Mitigation**: First task of implementation is to confirm the latest NIST AI RMF and Generative AI Profile versions via NIST's main AI RMF landing page. Capture URL and version in the ADR. **A concrete 3-hour timebox is enforced via tasks.md for the FR-1 research spike**: if the latest NIST AI RMF + Generative AI Profile versions, URLs, and Function/Category/Subcategory hierarchy are not confirmed and captured after ≤3 hours, the implementer pauses and escalates to PM. The 3-hour budget (vs PRD 143's 2-hour for AIVSS) reflects NIST's larger document set: AI RMF 1.0 + NIST AI 600-1 + hierarchy enumeration vs AIVSS's single spec
- **Contingency**: If FR-1 overruns 3h, the implementer pauses and chooses one of: (a) **descope Surface B Subcategory sample** from "5–10 representative subcategories" to "3 subcategories" to fit Wave 2 in remaining day, OR (b) **defer FR-7 tachi-shared artifact creation** to a follow-on Issue and ship only ADR-025 (FR-5) + SKILL.md update (FR-6) in this PRD, OR (c) escalate to PM for a PRD-close decision per Risk R1a contingency. If a newer NIST revision has materially changed scope (unlikely for a stable framework), the ADR notes the change and adapts the mapping accordingly

### Risk R2 — Mapping Reveals a Gap in Tachi's Compensating Controls Coverage
- **Description**: The Subcategory mapping in FR-2 may reveal that tachi's compensating control categories miss a NIST AI RMF Subcategory that is operationally important for regulated adopters (e.g., Govern-1.4 "policies and procedures" or Manage-2.4 "incident response")
- **Likelihood**: Medium (NIST AI RMF has broader process-oriented coverage than tachi's detection-focused controls)
- **Impact**: Medium — could trigger a separate corrective PRD for the compensating-controls analyzer
- **Mitigation**: If a gap is identified, this PRD's ADR documents it and files a separate follow-up Issue (not this PRD's responsibility to fix); the Rationale section notes the gap as a "post-ADR backlog item"
- **Contingency**: This PRD does not change scope; the gap becomes a new discovery item

### Risk R3 — ADR Decision Is Controversial Among Reviewers
- **Description**: Architect or team-lead may disagree with the recommended option (e.g., team-lead prefers Option A for low effort, architect prefers Option B for stronger compliance value)
- **Likelihood**: Low-Medium (this PRD is the first wired-integration evaluation in the MAESTRO companion ADRs; ADR-024 was a clear "diverge" call because of pre-1.0 maturity)
- **Impact**: Low — disagreement is healthy and the review loop handles it
- **Mitigation**: PRD ships with the trade-off framework (five evaluation criteria); reviewers can challenge the weighting rather than the conclusion. Up to 5 review iterations are budgeted (per `/aod.define` rules)
- **Contingency**: If consensus cannot be reached, escalate to user with the disagreement summarized; user picks the option

### Risk R4 — Tachi's Adopter Base Mix Is Hard to Quantify
- **Description**: The recommendation hinges in part on whether tachi's adopter base skews regulated or non-regulated; this is qualitative signal only (no analytics today)
- **Likelihood**: High (this is a known qualitative-only signal)
- **Impact**: Low — the ADR can still be written with a reasoned default (the discovery item already provides one: "default to Option A docs-only unless evidence supports wired integration")
- **Mitigation**: ADR text explicitly states the qualitative basis for the adopter-mix assumption and names a "When to Re-Evaluate" trigger (e.g., "≥3 regulated-industry adopter inquiries reference NIST AI RMF integration as a procurement gate")
- **Contingency**: ADR is committed with the chosen option and a re-evaluation clause; no other action

### Risk R5 — NIST AI 600-1 Generative AI Profile Risks Don't Cleanly Map to STRIDE+AI Categories
- **Description**: NIST's Generative AI Profile risks are domain-oriented (CBRN information, content harms, IP) while tachi's STRIDE+AI categories are mechanism-oriented (spoofing, tampering, prompt injection); the mapping in FR-2 Surface C may have many "No equivalent" rows
- **Likelihood**: Medium-High
- **Impact**: Low for output quality; Medium for Wave 2 timeline (if mapping requires reframe mid-authorship)
- **Mitigation**: Surface C explicitly annotates each Generative AI Profile risk with one of: Overlap (a tachi STRIDE+AI category covers the same mechanism), Gap (tachi has partial coverage), Conflict (tachi addresses the same domain differently), or No equivalent (tachi does not address this domain at all). **Architect retains scope-reduction authority**: if the full GAI-risk × STRIDE+AI mapping proves structurally intractable within the day budget, Surface C may be abbreviated to a summary paragraph with 3-4 exemplar rows rather than attempting full coverage — this is a permitted scope reduction, not a rule change (FR-2 Business Rules already permit "No equivalent" annotations)
- **Contingency**: A "No equivalent" row count >5 is documented in the ADR Rationale as a structural observation, not a tachi defect. **If "No equivalent" count exceeds 50% of Generative AI Profile risks**, the ADR Rationale section explicitly addresses scope-alignment as an additional trade-off input beyond the five evaluation criteria — a high mismatch rate may inform the option choice (e.g., favor Option A docs-only because wired integration would have inherent coverage gaps; OR favor Option C deep-wired with a new analyzer agent that operates in NIST's domain ontology rather than retrofitting STRIDE+AI tags)

### Dependencies
- **No internal dependencies** — this PRD is independent of any in-flight feature
- **External dependency**: Public availability of NIST AI RMF 1.0 and NIST AI 600-1 specifications (Risk R1 covers the contingencies)

---

## Open Questions

- [ ] Does the ADR commit to a specific calendar date for re-evaluation, or wait for an adopter-mix signal? — **Owner**: PM/Architect — **Due**: at ADR review — **Status**: Open (default: re-evaluate when ≥3 regulated-industry adopter inquiries reference NIST AI RMF integration as a procurement gate, OR at NIST AI RMF 2.0 publication, whichever comes first)

## Closed at PRD Approval

- **Should ADR-025 cross-reference ADR-019 (shared definitions)?** — **Resolution: YES.** ADR-019 governs shared cross-agent definitions; if Option A is adopted, the new `nist-ai-rmf-mapping.md` lands under tachi-shared discipline. If Option B or C is adopted, the follow-on implementation may add NIST-related shared references (e.g., Subcategory definitions, Function definitions). Cross-referencing ADR-019 in ADR-025's Related ADRs line is required regardless of the decision direction (cross-ref is forward-looking documentation, not a commitment to add a shared ref).
- **Does architect approval during plan/tasks review serve as the ADR "Accepted at merge" attestation?** — **Resolution: YES.** Same precedent as ADR-022, ADR-023, and ADR-024. No separate sign-off ceremony is required. The architect's APPROVED verdict on the plan/tasks artifacts (and on the PR review) is the attestation that ADR-025 ships with `Status: Accepted` (not Proposed).
- **Is the SKILL.md update target `tachi-control-analysis` (controls) or `tachi-risk-scoring` (scoring)?** — **Resolution: tachi-control-analysis.** NIST AI RMF is fundamentally a risk-management process framework with strong control taxonomy; the natural home is the control-analysis skill. ADR-024 chose `tachi-risk-scoring` because AIVSS is fundamentally a scoring framework. The two ADRs land their SKILL paragraphs in the most semantically appropriate skill, not in the same one.
- **Should ADR-024 be edited to add ADR-025 to its Related ADRs line, or is the back-reference one-way only?** — **Resolution: YES, add bidirectional back-reference.** A one-line edit to ADR-024's Related ADRs line adding `[ADR-025](ADR-025-nist-ai-rmf-evaluation.md)` (companion NIST AI RMF evaluation) ships in the same PR as ADR-025 itself. The edit does not invalidate ADR-024's Accepted status (ADRs allow housekeeping edits to cross-references without status change per existing tachi convention). Symmetry: readers landing on either ADR find the companion in the Related ADRs line. Effort: trivial single-line edit, scoped under FR-5.

---

## References

### Internal
- [Issue #144](https://github.com/davidmatousek/tachi/issues/144) — Discovery item for this PRD
- [Issue #136](https://github.com/davidmatousek/tachi/issues/136) — Umbrella MAESTRO compliance discovery
- [PRD 143 — MAESTRO Phase 4: OWASP AIVSS Evaluation ADR](143-maestro-aivss-evaluation-adr-2026-04-14.md) — Companion framework PRD
- [PRD 036 — Compensating Controls](036-compensating-controls-2026-03-27.md) — Original compensating controls analyzer PRD
- [PRD 136 — MAESTRO Canonical Layer Correctness Fix](136-maestro-canonical-layer-correctness-fix-2026-04-10.md) — Phase 1
- [PRD 141 — MAESTRO Cross-Layer Attack Chains](141-maestro-cross-layer-attack-chains-2026-04-12.md) — Phase 2
- [PRD 082 — Threat Agent Skill References](082-threat-agent-skill-references-2026-04-11.md) — Phase 3
- [schemas/finding.yaml](../../schemas/finding.yaml) — Current finding IR (v1.3)
- [schemas/risk-scoring.yaml](../../schemas/risk-scoring.yaml) — Current scoring schema (v1.1)
- [.claude/skills/tachi-control-analysis/](../../.claude/skills/tachi-control-analysis/) — Control analysis skill domain knowledge
- [.claude/skills/tachi-control-analysis/references/control-categories.md](../../.claude/skills/tachi-control-analysis/references/control-categories.md) — Control category definitions
- [.claude/skills/tachi-control-analysis/references/evidence-criteria.md](../../.claude/skills/tachi-control-analysis/references/evidence-criteria.md) — Evidence criteria definitions
- [.claude/skills/tachi-control-analysis/references/residual-risk.md](../../.claude/skills/tachi-control-analysis/references/residual-risk.md) — Residual risk classification
- [.claude/agents/tachi/control-analyzer.md](../../.claude/agents/tachi/control-analyzer.md) — Compensating controls analyzer agent
- [.claude/skills/tachi-shared/references/](../../.claude/skills/tachi-shared/references/) — Shared cross-agent references
- [docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md](../../docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md) — Companion AIVSS ADR
- [docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md](../../docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md) — MAESTRO classification ADR
- [docs/architecture/02_ADRs/ADR-019-shared-definitions-and-model-field-governance.md](../../docs/architecture/02_ADRs/ADR-019-shared-definitions-and-model-field-governance.md) — Shared definitions ADR
- [docs/architecture/02_ADRs/](../../docs/architecture/02_ADRs/) — ADR home

### External (To Be Verified During FR-1)
- [NIST AI Risk Management Framework (NIST AI 100-1, AI RMF 1.0)](https://www.nist.gov/itl/ai-risk-management-framework) — primary canonical specification
- [NIST AI 600-1 — Generative AI Profile (July 2024)](https://www.nist.gov/itl/ai-risk-management-framework) — generative-AI overlay applicable to agentic systems
- [CSA Blog: Agentic AI Threat Modeling Framework — MAESTRO (2025-02-06)](https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro)
- [Snyk Labs: MAESTRO — Layered Threat Modeling for Agentic AI Ecosystems](https://labs.snyk.io/resources/maestro-threat-modeling/)

---

## Appendix A: ADR-025 Skeleton (For Implementation Reference)

The implementation will produce an ADR roughly matching this skeleton (content TBD by the research and decision):

```markdown
# ADR-025: NIST AI Risk Management Framework Evaluation and Tachi Compensating Controls Posture

**Status**: Accepted
**Date**: 2026-04-XX
**Deciders**: Architect, Product Manager, Team-Lead
**Feature**: 144 (MAESTRO Companion: NIST AI RMF)
**Related ADRs**: ADR-024 (companion AIVSS evaluation), ADR-020 (MAESTRO classification), ADR-019 (shared cross-agent definitions), ADR-018 (baseline-aware pipeline correlation)

---

## Context

[NIST AI RMF specification summary, AI RMF 1.0 + Generative AI Profile versions captured]
[Tachi compensating controls analyzer recap]
[Three-surface comparison: Surface A (Functions × Pipeline Phases), Surface B (Subcategories × Compensating Control Categories), Surface C (Generative AI Profile Risks × STRIDE+AI Categories) — each with Overlap/Gap/Conflict/No-equivalent labels]

---

## Decision

[One-paragraph statement: docs-only-mapping (Option A) / shallow-wired-integration (Option B) / deep-wired-integration (Option C)]

---

## Rationale

[Five-criteria justification: maturity, adoption, compatibility, effort, compliance value]
[Adopter-mix qualitative basis explicitly stated]
[Note on companion-framework precedent: ADR-024 chose diverge for AIVSS because of pre-1.0 maturity; ADR-025's reasoning is independent because NIST AI RMF 1.0 is stable]

---

## Alternatives Considered

### Alternative A: Documentation-only Mapping
**Pros**: Lowest effort (S); zero runtime impact; preserves backward compatibility absolutely; gives adopters a starting point for their own NIST crosswalk; pattern matches ADR-024 Option C precedent for "framework awareness without runtime change"
**Cons**: Adopters must do the runtime translation themselves; less procurement-friendly for regulated firms expecting wired output; mapping file needs maintenance as NIST AI RMF revisions ship
**Why Not Chosen**: ...

### Alternative B: Shallow Wired Integration (Tag Compensating Controls)
**Pros**: Backward compatible (NIST tags optional); regulators can read NIST references directly in tachi PDF report; medium effort (M)
**Cons**: Schema bump touches finding.yaml or new controls schema; control-analyzer agent updates required; example regen required; reading overhead for non-regulated adopters when tags are present
**Why Not Chosen**: ...

### Alternative C: Deep Wired Integration (New NIST AI RMF Analyzer Agent)
**Pros**: Strongest compliance narrative; dedicated coverage report; cleanest separation of concerns (NIST analysis is its own agent, not bolted onto controls)
**Cons**: Largest change to pipeline (L); new agent + new schema + new template + new pipeline phase; example regen required; new agent must satisfy ADR-021 determinism and ADR-023 agent-shape conventions
**Why Not Chosen**: ...

(Recommended option includes "Why Chosen" instead of "Why Not Chosen")

---

## Consequences

[If wired (B or C): link to follow-on implementation Issue]
[If docs-only (A): name the artifact location and the maintenance commitment]
[Note that ADR-024 Related ADRs line will be updated to back-reference ADR-025 (single-line edit)]

---

## When to Re-Evaluate

[Concrete trigger, e.g., "≥3 regulated-industry adopter inquiries reference NIST AI RMF integration as a procurement gate" OR "NIST AI RMF 2.0 publication" — whichever comes first]
```

---

## Stakeholder Sign-off

Triad sign-offs are recorded in the YAML frontmatter at the top of this PRD.

- **Product Manager**: APPROVED_WITH_CONCERNS (2026-04-15) — see frontmatter `triad.pm_signoff.notes`
- **Architect**: APPROVED_WITH_CONCERNS (2026-04-15) — see frontmatter `triad.architect_signoff.notes`
- **Team-Lead**: APPROVED_WITH_CONCERNS (2026-04-15) — see frontmatter `triad.techlead_signoff.notes`

All 3 MEDIUM concerns (PM C1+C2, Architect C1+C2+C3) and 1 HIGH concern (Team-Lead HIGH-1) addressed inline. Remaining LOW concerns deferred to spec/tasks per individual reviewer notes. PRD ready to advance to `/aod.plan PRD: 144 - nist-ai-rmf-evaluation-adr`.
