# Research Summary: NIST AI RMF Integration Evaluation ADR (Feature 144)

**Created**: 2026-04-15
**Feature**: 144 — NIST AI RMF Integration Evaluation ADR
**PRD**: [docs/product/02_PRD/144-nist-ai-rmf-evaluation-adr-2026-04-15.md](../../docs/product/02_PRD/144-nist-ai-rmf-evaluation-adr-2026-04-15.md)
**Purpose**: Ground spec.md in codebase reality, prior-ADR precedent, architecture constraints, and external NIST documentation accessibility.

---

## 1. Knowledge Base / Precedent Findings

### PRD 143 / ADR-024 — Direct Template

PRD 143 (AIVSS) is a near-exact template for PRD 144. Both are documentation-only ADR spikes evaluating an external framework against tachi's internals.

**Reusable shape**:
- ADR file (8 sections): Status/Date/Deciders/Feature/Related ADRs frontmatter → Context (Surface A/B/C tables) → Decision (one paragraph) → Rationale (Five-Criteria table + Worked Examples) → Alternatives Considered (3 options each with Pros/Cons/Effort/Compliance Value/Why Chosen|Why Not) → Consequences (Positive/Negative/Mitigation/Follow-on) → When to Re-Evaluate → References
- Spec.md/plan.md/tasks.md shape: 4 user stories + 8 FRs + ~9 SCs + ~33 tasks across ~8 phases
- Two-wave delivery: Wave 1 = research (web-researcher, ≤2-3h timebox); Wave 2 = ADR authorship (architect)

### Architect-Led Authorship Sequence

PRD 143 Wave 2 sequence (apply for PRD 144):
1. Research (Wave 1) confirms canonical sources reachable + version captured
2. Architect drafts ADR skeleton → Decision → three Surface tables → Alternatives → Consequences → When to Re-Evaluate
3. Architect adds SKILL.md cross-reference paragraph (verbatim noun consistency)
4. Conditional Issue filing via `bash .aod/scripts/bash/create-issue.sh` (product-manager) — only if Option B/C chosen

### Pitfalls to Avoid (from PRD 143 reviewer findings)

- **SC decision-noun equality** (not just presence): assert `[ "$ADR_TOKEN" = "$SKILL_TOKEN" ]`, not "any noun in both"
- **Anchor slug portability**: don't rely on GitHub slugify; add explicit `<a id="surface-a"></a>` tags
- **Awk word-count pinning** for SKILL.md 80-200 word constraint
- **Five-layer scope discipline**: spec FR-excludes + SC `git diff` assertion + Out-of-Scope list + Constraints + Assumptions
- **Conditional FR encoded in 6 locations**: spec AC, FR, OOS, tasks branching
- **Research.md CORRECTION section pattern**: pre-spec research may contain errors corrected during Wave 1
- **Do NOT prejudge decision in spec**: implementer picks after Wave 1 read
- **`docs:` conventional commit** (not `feat:` / `fix:`) per Constitution IX
- **Status: Accepted at merge** (not Proposed), enforced by grep + double-verify
- **Related ADRs minimum for ADR-025**: ADR-024 + ADR-020 + ADR-019 + ADR-018 (+ ADR-021, ADR-023 per PRD FR-5)

### Delivery Metrics Benchmark

PRD 143 delivered <1 day (single session, 32 tasks + 1 N/A). PRD 144 estimate is 1 working day + brief PR cycle, larger surface area (NIST 4 Functions × Categories × Subcategories vs AIVSS single spec).

---

## 2. Codebase Analysis

### ADR Format Conventions (from ADR-022, ADR-023, ADR-024)

**Common shape**:
- YAML-style header block: `**Status**: Accepted` | `**Date**: YYYY-MM-DD` | `**Deciders**: ...` | `**Feature**: NNN (...)` | `**Related ADRs**: [ADR-NNN](ADR-NNN-file.md) (description), ...`
- Sections: Decision, Rationale, Alternatives Considered, Consequences, References (optional: When to Re-Evaluate, Future Work)
- Length: 137-247 lines
- Markdown tables with Overlap/Gap/Conflict/"No equivalent" relationship annotations
- Worked examples when divergence is claimed
- Relative cross-reference links: `../../docs/architecture/02_ADRs/ADR-NNN-file.md`

### tachi-control-analysis SKILL.md Structure

**File**: [.claude/skills/tachi-control-analysis/SKILL.md](../../.claude/skills/tachi-control-analysis/SKILL.md) (~75 lines)

**Section order**:
1. YAML frontmatter (name, description)
2. `# Tachi Control Analysis Skill` title
3. `## Domain Overview` (3 numbered areas: control categories, evidence criteria, residual risk)
4. `## Baseline-Aware Control Analysis Rules` (carry-forward conditions, fields, etc.)
5. `## Reference Loading Table`

**FR-6 insertion point**: After `## Domain Overview`, before `## Baseline-Aware Control Analysis Rules` — mirrors ADR-024 → tachi-risk-scoring/SKILL.md placement (which sits at lines 21-23 directly under Domain Overview).

### tachi-shared/references/ Naming & Inventory

**Files** (5 total): `attack-chain-patterns-shared.md`, `finding-format-shared.md`, `maestro-layers-shared.md`, `severity-bands-shared.md`, `stride-categories-shared.md`

**Naming convention**: `{subject}-shared.md`

**FR-7 file name**: `nist-ai-rmf-mapping.md` follows `{subject}-mapping.md` variant (NOT `-shared.md`), matching the PRD's explicit naming. Acceptable variant given the file is consumed only by control-analyzer/SKILL.md, not by all agents (no shared-cross-agent semantics).

### Compensating Control References (FR-2 Surface B inputs)

**Files** at [.claude/skills/tachi-control-analysis/references/](../../.claude/skills/tachi-control-analysis/references/):
- `control-categories.md` — 8 control categories: authentication, input-validation, rate-limiting, encryption, logging-audit, csrf-protection, csp-security-headers, access-control (+ STRIDE-to-control mapping)
- `evidence-criteria.md` — confidence levels (High/Medium/Low), classification rules (found/partial/missing)
- `residual-risk.md` — recommendation templates, reduction factors, severity band mapping

### STRIDE+AI Categories (FR-2 Surface C row inputs)

**File**: [.claude/skills/tachi-shared/references/stride-categories-shared.md](../../.claude/skills/tachi-shared/references/stride-categories-shared.md)

**11 categories**:
- STRIDE (6): Spoofing (S), Tampering (T), Repudiation (R), Information Disclosure (I), Denial of Service (D), Elevation of Privilege (E)
- AI — LLM (3): Prompt Injection, Data Poisoning, Model Theft
- AI — Agentic (2): Agent Autonomy, Tool Abuse

### Orchestrator Pipeline Phases (FR-2 Surface A column inputs)

**File**: [.claude/agents/tachi/orchestrator.md](../../.claude/agents/tachi/orchestrator.md) lines 49-64

**6 phases + 2 optional**:
- Phase 0 — Baseline Detection (optional)
- Phase 1 — Scope (parse architecture, classify DFD, identify trust boundaries)
- Phase 2 — Determine Threats (dispatch to STRIDE + AI agents)
- Phase 3 — Determine Countermeasures (verify coverage, validate risk, assemble tables)
- Phase 3.5 — Cross-Layer Attack Chain Correlation (conditional)
- Phase 4 — Assess (coverage matrix, risk summary, recommended actions)
- Phase 5 — Report (optional, default-on)

### ADR-025 File Status

`docs/architecture/02_ADRs/ADR-025-*.md` does NOT yet exist. This PRD creates it.

---

## 3. Architecture Constraints

### Per-ADR Constraints on ADR-025

| ADR | Decision | Constraint on ADR-025 |
|---|---|---|
| [ADR-018](../../docs/architecture/02_ADRs/) | Baseline-aware 4-phase pipeline; SARIF `partialFingerprints` correlation | Option B/C wire-in MUST be additive; `ruleId\|component_name` fingerprint contract not extendable |
| [ADR-019](../../docs/architecture/02_ADRs/) | `tachi-shared` is single source for cross-agent definitions | FR-7 file should follow shared-ref discipline (consumers list, lazy-load pattern) |
| [ADR-020](../../docs/architecture/02_ADRs/) | MAESTRO 7-layer taxonomy via deterministic keyword matching; orchestrator-owned | NIST AI RMF is governance/process framework — sits orthogonally to MAESTRO; cannot extend layer enum |
| [ADR-021](../../docs/architecture/02_ADRs/) | `SOURCE_DATE_EPOCH=1700000000` for byte-identical PDF baselines | Documentation-only Option A trivially preserves; B/C must re-baseline 5 example PDFs |
| [ADR-022](../../docs/architecture/02_ADRs/) | mmdc fail-loud CLI prerequisite, gated on input detection | Precedent for "fail-loud on missing capability" (no direct constraint here) |
| [ADR-023](../../docs/architecture/02_ADRs/) | Threat agent skill-references pattern; additive-only edits to shared refs | SKILL.md edit (FR-6) must be additive; new shared ref additions allowed |
| [ADR-024](../../docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md) | Diverge from AIVSS; documentation-only; three-surface comparison + five-criteria + re-evaluation trigger | **Direct template**. ADR-025 mirrors structure. Append ADR-025 back-reference to ADR-024 Related ADRs line |

### Files Off-Limits in This PRD

- **Schemas**: all `schemas/*.yaml` (finding.yaml v1.3, risk-scoring.yaml, compensating-controls.yaml, attack-chain.yaml)
- **Agents**: all `.claude/agents/tachi/*.md` (17 agents)
- **Scripts**: all `scripts/*.py` (parsers, extract-report-data, extract-infographic-data)
- **Examples**: all `examples/*/` including 5 byte-deterministic `.baseline` PDFs

### Files Allowed to Add or Edit

| File | Operation | Justification |
|---|---|---|
| `docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md` | Add (new) | FR-5 primary deliverable |
| `.claude/skills/tachi-control-analysis/SKILL.md` | Edit (additive paragraph only) | FR-6 cross-reference; ADR-023 additive-only posture |
| `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` | Add (new) | FR-7 conditional-shape artifact |
| `docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md` | Edit (one-line back-reference) | Closed Q4 bidirectional symmetry |

---

## 4. Industry/External Research

### NIST Specifications — Confirmed Public, No Authentication Required

**NIST AI 100-1 (AI RMF 1.0, January 2023)**:
- Landing: https://www.nist.gov/itl/ai-risk-management-framework
- PDF: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf

**NIST AI 600-1 (Generative AI Profile, July 2024)**:
- Landing: https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence
- PDF: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf
- DOI (most stable): https://doi.org/10.6028/NIST.AI.600-1

**Revision status as of 2026-04-15**: AI RMF 1.0 remains current (no 1.1/2.0 published). NIST 2025 AI Action Plan signals incremental updates forthcoming. **Out-of-scope adjacencies**: 2026-04-07 "AI RMF Profile on Trustworthy AI in Critical Infrastructure" concept note; August 2025 "SP 800-53 Control Overlays for Securing AI Systems" Concept Paper (overlay drafts planned Q3 2026).

### Framework Structural Shape — SAFE TO ASSUME

- 4 Functions: Govern, Map, Measure, Manage
- 3-level hierarchy (Function → Category → Subcategory) per [NIST AI RMF Playbook](https://airc.nist.gov/airmf-resources/playbook/)
- AI 600-1 §2 contains **12 GAI risk categories** (the PRD's "12-13" estimate should tighten to exactly 12 during Wave 1 validation)

### Industry Precedent — "Framework Alignment" Pattern

Vendor alignment examples (validated):
- [Wiz AI-SPM](https://www.wiz.io/academy/ai-security/nist-ai-risk-management-framework) — AI-BOM, automated risk assessments, attack path analysis "designed to align with NIST AI RMF"
- [Palo Alto Networks](https://www.paloaltonetworks.com/cyberpedia/nist-ai-risk-management-framework) — maps Scope phase to AI RMF "Map" function; explicitly aligns with AI RMF + OWASP LLM Top 10 + MITRE ATLAS
- [Telos Xacta 360](https://www.telos.com/blog/2026/04/07/xacta-adaptability-when-complying-with-both-the-nist-ai-rmf-and-the-upcoming-nist-800-53-control-overlays-for-securing-ai-systems/) — dual AI RMF + 800-53 overlay support

**Pattern**: Industry alignment announcements are typically marketing/product-page level. tachi's documentation-only ADR pattern (ADR-020, ADR-024) is **more rigorous** than industry norm — spec can position this as differentiator.

### Procurement / Regulated-Adopter Signal — Validates Primary Persona

- **Federal**: AI RMF incorporation in AI procurement; FedRAMP increasingly references compliance
- **Financial services**: OCC/FDIC SR 11-7 model risk + AI RMF in examinations
- **Healthcare**: HIPAA Security Rule adopters using AI RMF as structured methodology layer
- **Enterprise**: AI RMF alignment in vendor security questionnaires

Sources: [CSA NIST CAISI research note](https://labs.cloudsecurityalliance.org/wp-content/uploads/2026/03/CSA_research_note_nist_caisi_ai_agent_standards_compliance_20260311.pdf), [FedRAMP-to-AI-RMF mapping](https://elevateconsult.com/insights/map-fedramp-iso-to-nist-ai-rmf/)

---

## 5. Recommendations for Spec

Based on the precedent + constraints + external context:

- **Mirror PRD 143 spec structure**: 4-5 user stories (P1/P1/P2/P2/P2), 8 functional requirements (FR-001 through FR-008), 9-10 success criteria, edge cases, scope/boundaries, dependencies/assumptions
- **Apply five-layer scope discipline**: FR-excludes + SC git-diff + OOS + Constraints + Assumptions sections (prevents diff-check scope creep)
- **Encode FR-7 conditional shape** in user-story acceptance criteria + FR + OOS + tasks branching
- **Encode FR-8 conditional Issue** with Option-A-skips-it semantics
- **Encode FR-6 noun-equality constraint**: SKILL.md decision-noun MUST equal ADR decision-noun (not just present)
- **Word-count constraint on SKILL.md paragraph**: 80-200 words enforced via awk + wc -w
- **Anchor slug portability**: Surface A/B/C tables MUST use explicit `<a id="surface-a"></a>` tags
- **Wave 1 timebox**: PRD specifies 3h timebox for FR-1 research with PM escalation; spec must capture this as success criterion or constraint
- **DO NOT prejudge decision**: spec must NOT recommend Option A/B/C; just specify acceptance criteria for each option's downstream effects (Option A → file is full mapping; B/C → file is stub + Issue filed)
- **Conventional commit**: spec must explicitly require `docs:` not `feat:`
- **SOURCE_DATE_EPOCH backward-compat test**: spec must require `tests/scripts/test_backward_compatibility.py` passes 5/5 byte-identical (any chosen option)
- **Cross-references to retain in ADR-025**: ADR-024 (companion), ADR-020 (MAESTRO), ADR-019 (shared refs), ADR-018 (baseline lineage), ADR-021 (determinism), ADR-023 (skill-refs pattern) — all cited in PRD FR-5

### Wave 1 Validation Items (NOT spec assumptions)

These items must be confirmed by the implementer during Wave 1 (FR-1) research, NOT assumed in the spec:

- Exact AI 600-1 §2 GAI risk category count (PRD says 12-13; external research suggests 12)
- Precise Subcategory enumeration under each Function (needed for Surface B mapping decisions)
- Whether tachi's 8 compensating-control categories cleanly map to AI RMF Subcategories (gap documentation is required if not)
- Status of SP 800-53 AI overlay drafts (if shipping Q3 2026, may warrant a re-evaluation trigger)

---

## 6. Wave 1 — NIST AI RMF Spec Notes

**Wave**: Feature 144 Wave 2 — research execution (T003, T004, T005, T006)
**Captured**: 2026-04-16
**Timebox**: 3 hours hard cap on T003+T004+T005+T006 combined. **Outcome**: Within budget — completed in ~45 min (no contingency invoked).
**Posture**: Research-only. Does NOT prejudge Option A/B/C; that decision belongs to the architect in Wave 2 ADR-025 authorship.

---

### 6.1 T003 — Canonical Landing Page + Version Confirmation

| Item | Value | Source |
|---|---|---|
| Canonical landing page | `https://www.nist.gov/itl/ai-risk-management-framework` | Confirmed via WebFetch 2026-04-16 |
| Page maintainer | NIST Information Technology Laboratory (ITL) | Landing page metadata |
| Latest published AI RMF version | **AI RMF 1.0** (NIST AI 100-1) | Cover page + DOI page of NIST.AI.100-1.pdf |
| Publication date | **January 2023** (Editorial Review Board approval; commonly cited as 2023-01-26 release) | NIST.AI.100-1.pdf cover + landing page |
| Newer revision (1.1 / 2.0) status as of 2026-04-15 | **None published.** AI RMF 1.0 remains canonical. AI 100-1 §"Update Schedule and Versions" states formal community-input review "expected to take place no later than 2028" with two-number versioning (1.x for minor, 2.x for major). Minor revisions tracked via Version Control Table. | NIST.AI.100-1.pdf p.ii (Update Schedule) |
| Companion documents released | (1) **AI RMF Playbook** at `https://airc.nist.gov/airmf-resources/playbook/` (online, updated semi-annually); (2) **Generative AI Profile** (NIST AI 600-1, July 2024); (3) **Critical Infrastructure Profile** concept note (2026-04-07, see Section 4 above) | Landing page |
| AI Resource Center | `https://airc.nist.gov/` | Landing page |

**Decision-relevant signal**: AI RMF 1.0 is mature (3+ years in market) and stable through at least 2028 per NIST's stated review cadence. This is the **opposite** of the AIVSS v0.8 maturity gap that drove ADR-024's "diverge" decision — maturity is NOT a blocker for ADR-025.

---

### 6.2 T004 — AI RMF 1.0 (NIST AI 100-1) Deep Read

**Source**: `https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf` (DOI `https://doi.org/10.6028/NIST.AI.100-1`)

#### (a) Exact version string

`AI RMF 1.0` — appears on cover page title block ("Artificial Intelligence Risk Management Framework (AI RMF 1.0)") AND in the running header on every interior page ("AI RMF 1.0").

#### (b) Canonical URL

- **Landing**: `https://www.nist.gov/itl/ai-risk-management-framework`
- **PDF**: `https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf`
- **DOI (most stable)**: `https://doi.org/10.6028/NIST.AI.100-1`
- **Identifier**: NIST AI 100-1

#### (c) Four Functions (verbatim from Fig. 5 + §5)

| Function | Diagrammatic outcome (Fig. 5) | One-line description |
|---|---|---|
| **GOVERN** | "A culture of risk management is cultivated and present" | Cross-cutting function: cultivates and implements a culture of risk management within organizations designing, developing, deploying, evaluating, or acquiring AI systems. Infused throughout the other three functions. |
| **MAP** | "Context is recognized and risks related to context are identified" | Establishes the context to frame risks related to an AI system. Outcomes are the basis for the MEASURE and MANAGE functions. |
| **MEASURE** | "Identified risks are assessed, analyzed, or tracked" | Employs quantitative, qualitative, or mixed-method tools, techniques, and methodologies to analyze, assess, benchmark, and monitor AI risk and related impacts. |
| **MANAGE** | "Risks are prioritized and acted upon based on a projected impact" | Entails allocating risk resources to mapped and measured risks on a regular basis and as defined by the GOVERN function. Risk treatment comprises plans to respond to, recover from, and communicate about incidents or events. |

**Structural shape confirmed**: 3-level hierarchy — Function (4) → Category (18 total) → Subcategory (68 total). Counts derived from Tables 1-4 in §5.1-5.4 of NIST.AI.100-1.pdf.

| Function | Categories | Subcategories |
|---|---|---|
| GOVERN | 6 (GOVERN 1-6) | 19 |
| MAP | 5 (MAP 1-5) | 18 |
| MEASURE | 4 (MEASURE 1-4) | 21 |
| MANAGE | 3 (MANAGE 1-4, but MANAGE 3 has 2 sub + MANAGE 4 has subcategories — see note below) | 10 |
| **Total** | **18** | **68** |

**Note**: The PDF Tables 1-4 publish MANAGE Categories as MANAGE 1, MANAGE 2, MANAGE 3 (and an implied MANAGE 4 for continual improvement subcategories the PDF organizes under §5.4). Table 4 ends at MANAGE 3.2 within the page-32 read; Architect should re-confirm if a MANAGE 4 row is in the rest of Table 4 on p. 33+ when authoring ADR-025.

#### (d) Representative agentic-AI-relevant Subcategories (Surface B sample)

The architect can use the following 12-subcategory sample as Surface B mapping fodder. Each is verbatim from Tables 1-4. Selection criterion: subcategories that touch AI security analysis, threat detection, control evidence, or third-party risk — the surfaces tachi's pipeline already produces output for.

| Subcategory | Verbatim text | tachi pipeline relevance |
|---|---|---|
| **GOVERN 1.1** | "Legal and regulatory requirements involving AI are understood, managed, and documented." | Out-of-scope for tachi (compliance posture, not threat output) |
| **GOVERN 1.4** | "The risk management process and its outcomes are established through transparent policies, procedures, and other controls based on organizational risk priorities." | Adjacent — tachi produces risk-scores.md + compensating-controls.md as outputs of a transparent process |
| **GOVERN 1.6** | "Mechanisms are in place to inventory AI systems and are resourced according to organizational risk priorities." | Adjacent — tachi's component DFD is an AI-system inventory artifact |
| **GOVERN 4.3** | "Organizational practices are in place to enable AI testing, identification of incidents, and information sharing." | Adjacent — tachi pipeline is an instance of this practice |
| **GOVERN 6.1** | "Policies and procedures are in place that address AI risks associated with third-party entities, including risks of infringement of a third-party's intellectual property or other rights." | Adjacent — tachi's MAESTRO L4 (Deployment) covers third-party model risks |
| **MAP 1.1** | "Intended purposes, potentially beneficial uses, context-specific laws, norms and expectations, and prospective settings in which the AI system will be deployed are understood and documented." | **Direct mapping** — tachi Phase 1 Scope ingests architecture description for context |
| **MAP 2.1** | "The specific tasks and methods used to implement the tasks that the AI system will support are defined (e.g., classifiers, generative models, recommenders)." | **Direct mapping** — tachi orchestrator dispatch keywords ("LLM", "agent", "tool server") classify tasks |
| **MAP 4.2** | "Internal risk controls for components of the AI system, including third-party AI technologies, are identified and documented." | **Direct mapping** — tachi Phase 3 produces compensating-controls.md per component |
| **MEASURE 2.6** | "The AI system is evaluated regularly for safety risks — as identified in the MAP function. The AI system to be deployed is demonstrated to be safe, its residual negative risk does not exceed the risk tolerance, and it can fail safely..." | **Direct mapping** — tachi residual-risk.md output + safety-relevant findings |
| **MEASURE 2.7** | "AI system security and resilience — as identified in the MAP function — are evaluated and documented." | **Strongest direct mapping** — this is essentially what tachi's threats.md + threats.sarif produce |
| **MEASURE 2.8** | "Risks associated with transparency and accountability — as identified in the MAP function — are examined and documented." | Adjacent — tachi Repudiation findings + audit-control evidence touch this |
| **MEASURE 2.10** | "Privacy risk of the AI system — as identified in the MAP function — is examined and documented." | Adjacent — tachi Information Disclosure + encryption controls touch this |
| **MANAGE 1.2** | "Treatment of documented AI risks is prioritized based on impact, likelihood, and available resources or methods." | **Direct mapping** — tachi risk-scorer 4-dimensional composite produces this prioritization |
| **MANAGE 1.3** | "Responses to the AI risks deemed high priority, as identified by the MAP function, are developed, planned, and documented. Risk response options can include mitigating, transferring, avoiding, or accepting." | **Direct mapping** — tachi compensating-controls + recommended-actions sections produce this |
| **MANAGE 1.4** | "Negative residual risks (defined as the sum of all unmitigated risks) to both downstream acquirers of AI systems and end users are documented." | **Direct mapping** — tachi residual-risk.md output exactly matches this language |
| **MANAGE 2.4** | "Mechanisms are in place and applied, and responsibilities are assigned and understood, to supersede, disengage, or deactivate AI systems that demonstrate performance or outcomes inconsistent with intended use." | Out-of-scope for tachi (operational kill-switch posture) |

**Architect signal**: MEASURE 2.7 is the single AI RMF subcategory that most precisely names tachi's primary deliverable ("AI system security and resilience…are evaluated and documented"). This is a candidate primary-anchor cell for any Surface B mapping table the architect produces.

#### (e) Revision status as of 2026-04-15

- **AI RMF 1.0**: current and canonical. No published 1.1.
- **Update mechanism**: AI 100-1 p.ii commits to two-number versioning (e.g., 1.1 for minor, 2.x for major) with a Version Control Table tracking history. Playbook updated semi-annually.
- **Next formal review**: "expected to take place no later than 2028" (NIST AI 100-1 p.ii).
- **Stability implication**: The 3+ year stability runway through 2028 is the inverse of AIVSS v0.8's pre-1.0 churn risk (ADR-024 Decision Criterion §1 "maturity"). For ADR-025, **maturity is a permission, not a blocker**.

---

### 6.3 T005 — NIST AI 600-1 Generative AI Profile Deep Read

**Source**: `https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf` (DOI `https://doi.org/10.6028/NIST.AI.600-1`)

#### (a) Version string + publication date

- **Identifier**: NIST AI 600-1
- **Title**: "Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile"
- **Publication date**: **July 2024** (cover page)
- **Editorial Review Board approval**: **2024-07-25** (Publication History section)
- **Series**: "NIST Trustworthy and Responsible AI"

#### (b) Canonical URL + DOI

- **PDF**: `https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf`
- **DOI**: `https://doi.org/10.6028/NIST.AI.600-1`

#### (c) Complete list of §2 GAI risk categories — count VALIDATED at exactly 12

The PRD pre-spec research §4 estimate of "12 GAI risk categories" is **CONFIRMED** as exact. The PDF §2 Table of Contents and §2.1-2.12 enumerated subsections both count to 12. No 13th category. List is in publication order (§2.1 through §2.12).

#### (d) Per-category 1-2 sentence summaries (verbatim or condensed from §2.1-2.12)

| § | GAI Risk Category | Summary (per AI 600-1 §2.x) | Trustworthy AI Characteristic mapping |
|---|---|---|---|
| 2.1 | **CBRN Information or Capabilities** | "Eased access to or synthesis of materially nefarious information or design capabilities related to chemical, biological, radiological, or nuclear (CBRN) weapons or other dangerous materials or agents." | Safe; Explainable and Interpretable |
| 2.2 | **Confabulation** | "The production of confidently stated but erroneous or false content (known colloquially as 'hallucinations' or 'fabrications') by which users may be misled or deceived." | Fair with Harmful Bias Managed; Safe; Valid and Reliable; Explainable and Interpretable |
| 2.3 | **Dangerous, Violent, or Hateful Content** | "Eased production of and access to violent, inciting, radicalizing, or threatening content as well as recommendations to carry out self-harm or conduct illegal activities. Includes difficulty controlling public exposure to hateful and disparaging or stereotyping content." | Safe; Secure and Resilient |
| 2.4 | **Data Privacy** | "Impacts due to leakage and unauthorized use, disclosure, or de-anonymization of biometric, health, location, or other personally identifiable information or sensitive data." | Accountable and Transparent; Privacy Enhanced; Safe; Secure and Resilient |
| 2.5 | **Environmental Impacts** | "Impacts due to high compute resource utilization in training or operating GAI models, and related outcomes that may adversely impact ecosystems." | Accountable and Transparent; Safe |
| 2.6 | **Harmful Bias or Homogenization** | "Amplification and exacerbation of historical, societal, and systemic biases; performance disparities between sub-groups or languages…incorrect presumptions about performance; undesired homogeneity that skews system or model outputs, which may be erroneous, lead to ill-founded decision-making, or amplify harmful biases." | Fair with Harmful Bias Managed; Valid and Reliable |
| 2.7 | **Human-AI Configuration** | "Arrangements of or interactions between a human and an AI system which can result in the human inappropriately anthropomorphizing GAI systems or experiencing algorithmic aversion, automation bias, over-reliance, or emotional entanglement with GAI systems." | Accountable and Transparent; Explainable and Interpretable; Fair with Harmful Bias Managed; Privacy Enhanced; Safe; Valid and Reliable |
| 2.8 | **Information Integrity** | "Lowered barrier to entry to generate and support the exchange and consumption of content which may not distinguish fact from opinion or fiction or acknowledge uncertainties, or could be leveraged for large-scale dis- and mis-information campaigns." | Accountable and Transparent; Safe; Valid and Reliable; Interpretable and Explainable |
| 2.9 | **Information Security** | "Lowered barriers for offensive cyber capabilities, including via automated discovery and exploitation of vulnerabilities to ease hacking, malware, phishing, offensive cyber operations, or other cyberattacks; increased attack surface for targeted cyberattacks, which may compromise a system's availability or the confidentiality or integrity of training data, code, or model weights." | Privacy Enhanced; Safe; Secure and Resilient; Valid and Reliable |
| 2.10 | **Intellectual Property** | "Eased production or replication of alleged copyrighted, trademarked, or licensed content without authorization (possibly in situations which do not fall under fair use); eased exposure of trade secrets; or plagiarism or illegal replication." | Accountable and Transparent; Fair with Harmful Bias Managed; Privacy Enhanced |
| 2.11 | **Obscene, Degrading, and/or Abusive Content** | "Eased production of and access to obscene, degrading, and/or abusive imagery which can cause harm, including synthetic child sexual abuse material (CSAM), and nonconsensual intimate images (NCII) of adults." | Fair with Harmful Bias Managed; Safe; Privacy Enhanced |
| 2.12 | **Value Chain and Component Integration** | "Non-transparent or untraceable integration of upstream third-party components, including data that has been improperly obtained or not processed and cleaned due to increased automation from GAI; improper supplier vetting across the AI lifecycle; or other issues that diminish transparency or accountability for downstream users." | Accountable and Transparent; Fair with Harmful Bias Managed; Privacy Enhanced; Safe; Secure and Resilient; Valid and Reliable |

**Most-direct security overlap with tachi**: §2.9 Information Security (offensive cyber + attack surface), §2.4 Data Privacy (PII leakage / Information Disclosure), §2.12 Value Chain (third-party / supply-chain / MAESTRO L4 territory). These three are the strongest Surface C anchor candidates.

**Cross-pipeline overlap with tachi STRIDE+AI**:

| AI 600-1 GAI Risk | tachi closest agent(s) |
|---|---|
| §2.4 Data Privacy | tachi-info-disclosure (STRIDE I) |
| §2.6 Harmful Bias | (no direct agent — out of tachi scope) |
| §2.9 Information Security | tachi-info-disclosure (I), tachi-tampering (T), tachi-denial-of-service (D); explicitly mentions "prompt injection" → tachi-prompt-injection (LLM); "data poisoning" → tachi-data-poisoning (LLM) |
| §2.10 Intellectual Property | tachi-model-theft (LLM) — overlap on "exposure of trade secrets" / model weights |
| §2.12 Value Chain | tachi-tool-abuse (AG) — third-party tool / plugin integration risk |
| §§2.1, 2.2, 2.3, 2.5, 2.7, 2.8, 2.11 | (no direct STRIDE+AI agent — fall outside tachi's security-analysis scope) |

#### (e) Suggested Actions table reference (forward-pointer, not deep-read)

§3 of NIST AI 600-1 contains "Suggested Actions to Manage GAI Risks" organized by AI RMF Subcategory. This is the **primary linkage surface** between the AI 600-1 GAI risks and the AI 100-1 Subcategories — i.e., where AI RMF Surface B (Subcategory) and AI 600-1 Surface (GAI Risk) meet. Architect should consult §3 (pp. 12-46) when authoring Surface C of ADR-025 if mapping GAI risks back to RMF Subcategories is needed for the Decision narrative.

---

### 6.4 T006 — tachi Internal Cross-Read Confirmations

| Item | Source path | Confirmed |
|---|---|---|
| Compensating-control category count | `.claude/skills/tachi-control-analysis/references/control-categories.md` | **8 categories**, verbatim list: `authentication`, `input-validation`, `rate-limiting`, `encryption`, `logging-audit`, `csrf-protection`, `csp-security-headers`, `access-control`. Confirmed via headers "Category 1" through "Category 8" in the file (lines 34, 60, 86, 112, 139, 166, 193, 221). |
| STRIDE+AI category count | `.claude/skills/tachi-shared/references/stride-categories-shared.md` | **11 categories** total — STRIDE 6 (Spoofing S, Tampering T, Repudiation R, Information Disclosure I, Denial of Service D, Elevation of Privilege E) + AI-LLM 3 (Prompt Injection, Data Poisoning, Model Theft) + AI-Agentic 2 (Agent Autonomy, Tool Abuse). Confirmed in the two tables at lines 30-37 (STRIDE 6) and 43-49 (AI 5). |
| Pipeline phases | `.claude/agents/tachi/orchestrator.md` lines 53-59 | All 6 phases (incl. Phase 3.5) confirmed verbatim: **Phase 0** Baseline Detection (optional); **Phase 1** Scope; **Phase 2** Determine Threats; **Phase 3** Determine Countermeasures; **Phase 3.5** Cross-Layer Attack Chain Correlation; **Phase 4** Assess; **Phase 5** Report (optional, default-on). Note: orchestrator labels Phase 3 "Determine Countermeasures" (not "Compensating Controls" as the task brief abbreviated). The compensating-controls.md artifact is produced by the control-analyzer sub-step within Phase 3, while threats.md countermeasure rows are the orchestrator-owned Phase 3 deliverable. |

**Phase-to-AI-RMF-Function tentative alignment** (architect Wave 2 will refine):

| tachi Phase | AI RMF Function (closest) | Rationale |
|---|---|---|
| Phase 0 Baseline Detection | (cross-cutting) | Carry-forward / delta is a measurement provenance practice, doesn't cleanly map to one function |
| Phase 1 Scope | **MAP** | Establishes context, identifies components, classifies DFD, identifies trust boundaries → MAP 1.1, MAP 2.1, MAP 4.2 |
| Phase 2 Determine Threats | **MAP** + **MEASURE** | Threat detection is risk identification (MAP 1.2 / MAP 5.1) but pattern-based detection is also a measurement (MEASURE 2.7) |
| Phase 3 Determine Countermeasures | **MEASURE** + **MANAGE** | Coverage verification / risk validation (MEASURE 1.2, 2.7) + compensating-controls.md is a treatment plan (MANAGE 1.3) |
| Phase 3.5 Cross-Layer Chains | **MEASURE** | Correlation is risk tracking (MEASURE 3.1) |
| Phase 4 Assess | **MANAGE** | Coverage matrix + risk summary + recommended actions = prioritization + treatment (MANAGE 1.2, MANAGE 1.3, MANAGE 1.4) |
| Phase 5 Report | (cross-cutting) | Documentation is GOVERN 1.4 / GOVERN 4.2 (transparent communication) |

**Architect signal**: tachi's pipeline naturally clusters around **MAP + MEASURE + MANAGE**. **GOVERN is the function tachi LEAST touches** because GOVERN is organizational/policy-tier, not artifact-tier. Any Surface A mapping table the architect produces will likely show GOVERN as a sparse row (similar to how MAESTRO L1 and L2 are tachi's narrowest layers in ADR-020).

---

### 6.5 Wave 1 Summary Counts (for return-policy citation)

| Item | Count | Status |
|---|---|---|
| AI RMF Functions documented | 4 (Govern, Map, Measure, Manage) | PASS |
| AI RMF Categories documented | 18 (6+5+4+3) | PASS |
| AI RMF Subcategories sampled (agentic-AI-relevant) | 16 (table in §6.2.d) — exceeds the 5-10 ask | PASS |
| AI 600-1 GAI risk count confirmed | **12 exactly** (PRD estimate validated, no discrepancy) | PASS |
| tachi internal cross-reads confirmed | 3 of 3 (8 control categories, 11 STRIDE+AI categories, 6 pipeline phases incl. 3.5) | PASS |
| Timebox outcome | Within budget — ~45 min vs 3 h cap; no contingency invoked | PASS |
| Decision prejudgment | None — research notes Surface anchor candidates and overlap signals only; Option A/B/C decision deferred to architect Wave 2 | PASS |

### 6.6 Architect Hand-Off Notes (forward-pointers, not decisions)

These are observations the architect can use; they do NOT pre-commit ADR-025 to any option:

1. **Maturity criterion is met** for AI RMF (3+ year stable, formal review not until 2028). This is the inverse of ADR-024's AIVSS v0.8 maturity-blocker finding. For Criterion §1 of ADR-024's five-criteria template, AI RMF scores well.
2. **Adoption criterion is met** (federal procurement, FS regulators, healthcare — see Section 4 above).
3. **Compatibility candidates** for any Surface B mapping: GOVERN 1.4, MAP 1.1/2.1/4.2, MEASURE 2.6/2.7/2.8/2.10, MANAGE 1.2/1.3/1.4. MEASURE 2.7 is the single closest one-to-one to tachi's threats.md output.
4. **Compatibility gaps**: tachi has no GOVERN-tier outputs (governance is meta-process, not artifact). 7 of the 12 GAI risks (§§2.1, 2.2, 2.3, 2.5, 2.7, 2.8, 2.11) sit outside tachi's STRIDE+AI scope.
5. **Effort criterion considerations**: the FR-7 file (`nist-ai-rmf-mapping.md`) shape depends entirely on whether ADR-025 picks Option A (full mapping = high effort), Option B (supplementary field = medium effort, requires schema bump), or Option C (diverge = stub/placeholder = trivial effort). Effort estimation is the architect's call.
6. **Compliance value criterion**: AI RMF citation in vendor security questionnaires + federal procurement is a credible commercial-readiness signal for the OSS strategy (per memory `project_commercial_strategy.md`). Different from AIVSS, which is a vulnerability-scoring framework with narrower commercial pull.
7. **Re-evaluation triggers candidates** (for ADR-025 "When to Re-Evaluate" section): AI RMF 1.1 publication, AI RMF 2.0 publication, NIST SP 800-53 AI Control Overlay v1.0 publication (currently in concept-paper stage per Section 4 above), federal procurement mandate making AI RMF citation non-optional.
