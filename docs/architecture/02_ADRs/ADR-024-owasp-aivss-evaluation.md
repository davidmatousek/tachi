# ADR-024: OWASP AIVSS Evaluation and Tachi Composite Scoring Posture

**Status**: Accepted
**Date**: 2026-04-15
**Deciders**: Architect, Product Manager, Team-Lead
**Feature**: 143 (MAESTRO Phase 4)
**Related ADRs**: [ADR-020](ADR-020-maestro-layer-classification.md) (MAESTRO classification), [ADR-019](ADR-019-shared-definitions-and-model-field-governance.md) (shared cross-agent definitions), [ADR-018](ADR-018-baseline-aware-pipeline-correlation.md) (baseline-aware scoring lineage), [ADR-025](ADR-025-nist-ai-rmf-evaluation.md) (companion NIST AI RMF evaluation)

---

## Decision

**Tachi will diverge from OWASP AIVSS at the present time.** The existing four-dimensional weighted-sum composite (`(0.35 × CVSS 3.1) + (0.30 × Exploitability) + (0.20 × Reachability) + (0.15 × Scalability)`) remains the canonical scoring model. AIVSS v0.8 is documented in this ADR as a peer agentic-AI scoring framework that tachi is aware of and intentionally non-aligned with. The decision is to **diverge** rather than adopt — neither as a primary scoring replacement (Option A) nor as a supplementary field (Option B). Tachi will re-evaluate when AIVSS publishes a stable v1.0 with at least one external adopter case study (see *When to Re-Evaluate*).

---

## Context

OWASP AIVSS (AI Vulnerability Scoring System) is the agentic-AI scoring framework jointly published by OWASP AIVSS, AIUC-1, OWASP AI Exchange, and the OWASP Citizen Development Top 10 project. The latest published version at the time of this ADR is **v0.8** ("AIVSS Scoring System For OWASP Agentic AI Core Security Risks v0.8"; canonical home [aivss.owasp.org](https://aivss.owasp.org/)), released ahead of the public review period that opens 2026-04-16. CSA MAESTRO explicitly references AIVSS as the companion scoring approach for agentic AI risks, which makes the framework strategically relevant to tachi after the MAESTRO Phase 1–3 work landed under ADR-020.

Tachi already ships a four-dimensional composite risk scoring model under [`schemas/risk-scoring.yaml`](../../../schemas/risk-scoring.yaml) and the [`tachi-risk-scoring`](../../../.claude/skills/tachi-risk-scoring/SKILL.md) skill. The model has been stable across PRDs 075, 078, 084, and the MAESTRO compliance series (Phases 1–3 in PRDs 136, 141, 082). Adopting AIVSS — fully or partially — would require either restructuring the composite formula, upgrading from CVSS 3.1 to CVSS 4.0, or both. This ADR evaluates the trade-off across three surfaces (dimensions, composite formula, severity bands), enumerates the available options, and records the chosen posture.

The evaluation must avoid two common failure modes. First, a **dimension-only mapping** would surface the agentic-vs-operational dimension overlap and miss the structural divergence in formula shape and the CVSS-base version gap. Second, a **headline-driven adoption** would overweight AIVSS's CSA-MAESTRO endorsement and underweight the maturity signal (AIVSS v0.8 is pre-1.0, with public review opening 2026-04-16 and no external adopter case studies yet). The three-surface comparison below is structured to surface both classes of issue explicitly.

<a id="surface-a"></a>
### Surface A — Dimension Set

Each row maps a tachi composite dimension to its closest AIVSS construct. The Relationship cell is exactly one of `Overlap`, `Gap`, `Conflict`, or `No equivalent` (boundary established by spec FR-002 and verified by Phase 6 task T019). The CVSS row is explicitly a Conflict and not an Overlap because the CVSS-base versions differ (tachi CVSS 3.1 vs AIVSS CVSS v4.0); collapsing this into an Overlap would silently elide a concrete adoption blocker.

| Tachi Dimension | Weight | AIVSS Equivalent | Relationship | Note |
|-----------------|--------|------------------|--------------|------|
| CVSS 3.1 base | 0.35 | CVSS v4.0 base | **Conflict** | Tachi uses CVSS 3.1; AIVSS v0.8 §3.1.1 *requires* CVSS v4.0 ("Practitioners should not use CVSS v3.1 scores as inputs to the AIVSS formula"). The vector format and Subsequent System metrics are not directly comparable. |
| Exploitability | 0.30 | None — partially overlaps with `Non-Determinism` and `Opacity` AARFs | **Gap** | AIVSS has no operational exploitability dimension. The closest agentic factors describe model behavior (variance, traceability), not attack feasibility. Tachi's exploitability captures Known Techniques + Attack Complexity + Tooling Availability + Skill Level, none of which AIVSS scores. |
| Reachability | 0.20 | None | **No equivalent** | AIVSS has no architecture-aware attack surface dimension. Tachi's Reachability is derived from trust-zone position and architecture barriers — concepts AIVSS does not surface in its 10 AARFs. |
| Scalability | 0.15 | Partially overlaps with `Multi-Agent` and `Tools` AARFs | **Gap** | Tachi's Scalability scores Scriptability + Target Scope + Resource Requirements + Detection Difficulty (automation-agnostic blast radius). AIVSS Multi-Agent (coordination dependencies) and Tools (external API surface) cover related blast-radius signals but operationalize them differently. |
| (no tachi equivalent) | n/a | 10 AARFs (Autonomy, Tools, Language, Context, Non-Determinism, Opacity, Persistence, Identity, Multi-Agent, Self-Mod) | **No equivalent** | AIVSS's full agentic amplification set has no analog in tachi's four-dimensional composite. Tachi treats agentic concerns categorically (the `agentic` and `llm` STRIDE-adjacent threat categories) rather than as continuous amplification factors. |

### Surface B — Composite Formula Weights

Tachi's composite formula is a weighted sum of four operational dimensions, total weight 1.0, naturally bounded 0.0–10.0:

```
composite_score = (0.35 × CVSS 3.1) + (0.30 × Exploitability) + (0.20 × Reachability) + (0.15 × Scalability)
```

AIVSS v0.8 uses an **amplification model** in which the agentic uplift consumes the headroom between the CVSS base score and the 10.0 ceiling, then a mitigation factor scales the result (v0.8 §3.4):

```
AIVSS = (CVSS_Base + AARS) × Mitigation_Factor
  where:
    AARS = (10 - CVSS_Base) × (Factor_Sum / 10) × ThM
    Factor_Sum  = sum of 10 AARFs, each ∈ {0.0, 0.5, 1.0}, range 0.0–10.0
    ThM         = Threat Multiplier (Attacked = 1.00, Proof-of-Concept = 0.97 default, Unreported = 0.50)
    Mitigation_Factor = 1.00 (None, default), 0.83 (Partial), or 0.67 (Strong)
```

**Structural difference**: tachi is a weighted sum across 4 dimensions where each dimension contributes independently and the weights determine relative importance. AIVSS is an amplification model where 10 agentic factors uplift a CVSS baseline up to the 10.0 ceiling, then a mitigation factor scales down. The two formulas cannot produce equivalent scores even with identical CVSS inputs, because the operational dimensions tachi weights (Exploitability, Reachability, Scalability) and the agentic amplifiers AIVSS uplifts (Autonomy, Tools, Language, Context, Non-Determinism, Opacity, Persistence, Identity, Multi-Agent, Self-Mod) measure different things. AIVSS does not express its model as weighted operational dimensions, and tachi does not express its model as agentic uplift consuming CVSS headroom.

### Surface C — Severity Band Thresholds

| Band | Tachi (`schemas/risk-scoring.yaml:129-133`) | AIVSS v0.8 §3.5.2 | Relationship |
|------|---------------------------------------------|--------------------|--------------|
| Critical | 9.0 – 10.0 | 9.0 – 10.0 | Overlap |
| High | 7.0 – 8.9 | 7.0 – 8.9 | Overlap |
| Medium | 4.0 – 6.9 | 4.0 – 6.9 | Overlap |
| Low | 0.0 – 3.9 | 0.1 – 3.9 | Overlap (operationally indistinguishable at one-decimal rounding) |

AIVSS v0.8 §3.5.2 explicitly notes: *"These thresholds are adopted from CVSS severity band conventions for cross-framework consistency."* Tachi's bands derive from the same convention. **Surface C is the single point of structural alignment between the two frameworks** — the input signals differ (Surfaces A and B), but downstream consumers of the severity band (governance fields, SLAs, color coding) would behave identically across either framework's output.

---

## Rationale

The recommendation to **diverge** rests on the five evaluation criteria established in PRD 143 (maturity, adoption, compatibility, effort, compliance value), reinforced by two worked examples that demonstrate measurable score divergence on the same finding.

### Five-Criteria Justification

| Criterion | Assessment | Weight in Decision |
|-----------|------------|--------------------|
| **AIVSS Maturity** | v0.8 is pre-1.0; public review opens 2026-04-16 (the day after planned ADR merge); 1.0 target end of 2026; no industry stability commitments yet | **Heavy** — adopting a pre-1.0 scoring framework into a stable pipeline introduces churn risk |
| **Adoption in the Wild** | No external adopter case studies published; CSA MAESTRO references AIVSS as a companion approach but does not require it; tachi would be among the first adopters with no peer signal to calibrate against | **Moderate** — first-adopter risk on a scoring framework is high because consumers compare across vendors |
| **Compatibility with Tachi** | Surface A shows 1 Conflict + 2 Gaps + 2 No-equivalents; Surface B shows fundamentally different formula shape; Surface C is the only Overlap. The CVSS 3.1 → 4.0 upgrade is itself effort-multiplying | **Heavy** — adoption is structurally non-trivial, not a labeling exercise |
| **Effort to Wire In** | Option A (primary): L (~5–8 days, schema-breaking change with example regeneration). Option B (supplementary): M (~2–3 days, additive). Option C (diverge): S (~0 days beyond this ADR) | **Moderate** — effort is bounded but non-trivial for adoption paths |
| **Compliance Value for Regulated Adopters** | AIVSS is not yet referenced by SOC 2, FedRAMP, or EU AI Act guidance. CSA MAESTRO endorses AIVSS as a companion approach but does not mandate it. Tachi's existing four-dimensional model already produces severity bands aligned with AIVSS bands (Surface C), so report-vs-translate decisions favor "report" over "translate" | **Moderate** — compliance asks for severity bands and mappings, both of which tachi already produces |

The decisive inputs are **maturity** (pre-1.0 with imminent public review) and **compatibility** (CVSS-version conflict + formula-shape divergence). Together these argue against adoption at the present time even though Surface C alignment makes downstream consumption equivalent.

### Worked Examples — Score Divergence on the Same Finding

The two examples below are drawn from the AIVSS v0.8 §3.6 worked-example scenarios. Each constructs the equivalent finding under tachi's composite and quantifies the score difference. These examples make the formula-shape divergence concrete: the same underlying finding produces a different composite score and, in Example 1, a different severity band.

**Example 1 — Agentic AI Tool Misuse** (AIVSS v0.8 §3.6.1)

Scenario: an attacker injects malicious instructions into an externally available agent. The agent has high autonomy and access to internal code generation tools, and acts on the instructions to infect internal systems.

| Framework | Inputs | Calculation | Final Score | Band |
|-----------|--------|-------------|-------------|------|
| AIVSS v0.8 | CVSS v4.0 = 9.4 (Critical); Factor_Sum = 9.0; ThM = 0.97 | `AARS = (10 − 9.4) × 0.90 × 0.97 = 0.5238`; `AIVSS_raw = (9.4 + 0.5238) × 1.0 = 9.9238` → rounds to **9.9** | **9.9** | Critical |
| Tachi | CVSS 3.1 = 9.0 (agentic category default per `risk-scoring.yaml:118`); Exploitability = 5.0 (AI-specific guidance, `scoring-dimensions.md:38`); Reachability = 7.0 (high trust zone); Scalability = 5.8 (agentic guidance, `scoring-dimensions.md:76`) | `composite = (0.35 × 9.0) + (0.30 × 5.0) + (0.20 × 7.0) + (0.15 × 5.8) = 3.15 + 1.50 + 1.40 + 0.87 = 6.92` → rounds to **6.9** | **6.9** | Medium |

**Difference**: AIVSS scores 9.9 (Critical); tachi scores 6.9 (Medium). The two frameworks disagree on both the score and the severity band. AIVSS's amplification model treats the agentic capabilities as severity multipliers that consume nearly all of the CVSS-base headroom (the AARS uplift of 0.52 nearly maxes out the 0.6-point gap between CVSS 9.4 and 10.0). Tachi's weighted-sum model treats exploitability, reachability, and scalability as moderating dimensions that pull the composite *toward* the average rather than uplifting it toward the ceiling.

**Example 2 — Agent Cascading Failures** (AIVSS v0.8 §3.6.3)

Scenario: a crafted injection message causes downstream agents to enter error states, producing availability and data integrity issues.

| Framework | Inputs | Calculation | Final Score | Band |
|-----------|--------|-------------|-------------|------|
| AIVSS v0.8 | CVSS v4.0 = 7.1 (High); Factor_Sum = 8.0; ThM = 0.97 | `AARS = (10 − 7.1) × 0.80 × 0.97 = 2.2504`; `AIVSS_raw = (7.1 + 2.2504) × 1.0 = 9.3504` → rounds to **9.4** | **9.4** | Critical |
| Tachi | CVSS 3.1 = 7.5 (DoS category default per `risk-scoring.yaml:116`, derived); Exploitability = 6.0 (moderate); Reachability = 6.0 (downstream agent surface); Scalability = 7.0 (cascade is multi-system) | `composite = (0.35 × 7.5) + (0.30 × 6.0) + (0.20 × 6.0) + (0.15 × 7.0) = 2.625 + 1.80 + 1.20 + 1.05 = 6.675` → rounds to **6.7** | **6.7** | Medium |

**Difference**: AIVSS scores 9.4 (Critical); tachi scores 6.7 (Medium). Same band-crossing pattern as Example 1: AIVSS's amplification of agentic factors pushes a moderate-CVSS finding into Critical, while tachi's weighted sum holds it in Medium. The score gaps (3.0 for Example 1, 2.7 for Example 2) are large but not proportional to each other — demonstrating that the two frameworks cannot be reconciled by a simple offset or scaling factor. The divergence is structural.

These two examples are sufficient to establish that tachi and AIVSS produce measurably different outputs on the same agentic finding. A "translate" workflow that converts tachi scores into AIVSS scores (or vice versa) is therefore **not viable** without re-running the full assessment under the target framework's dimensions. This reinforces the decision to diverge rather than adopt-as-supplementary: a supplementary AIVSS field that disagrees with the canonical tachi field by 2–3 points on the 0–10 scale would create more confusion than value for downstream consumers.

---

## Alternatives Considered

### Option A — Adopt AIVSS as Primary Scoring Replacement

**Description**: Replace tachi's four-dimensional composite with AIVSS as the canonical scoring model. Migrate `schemas/risk-scoring.yaml` from CVSS 3.1 to CVSS 4.0, replace the four-dimensional weights table with the 10-AARF amplification model, regenerate all 6 example outputs under the new schema, and rewrite the `tachi-risk-scoring` skill end-to-end.

**Pros**:
- Aligns tachi with the OWASP-published agentic-AI scoring standard endorsed by CSA MAESTRO
- Single canonical score per finding, no parallel models to maintain
- Compliance officers can report tachi outputs directly into AIVSS-aware regulatory frameworks once those frameworks ratify AIVSS
- Eliminates the "report-vs-translate" decision surface

**Cons**:
- Schema-breaking change — every consumer of `composite_score`, `cvss_vector`, and the four dimension fields must be updated
- Loses tachi-specific dimensions (Reachability, Scalability) that have no AIVSS equivalent — architecture-aware scoring would degrade
- AIVSS v0.8 is pre-1.0; adopting now means re-doing the work when v1.0 lands, with risk of v1.0 introducing breaking changes versus v0.8
- CVSS 3.1 → 4.0 migration is a parallel effort-multiplier: every existing CVSS vector in `category_defaults` and downstream scoring must be re-cast
- All 6 backward-compatibility PDF baselines invalidated; example regeneration cycle required
- First-adopter risk: no peer signal to calibrate weights against; tachi outputs cannot be benchmarked against other AIVSS-using vendors until adopters appear

**Effort**: **L (~5–8 days)** — schema-breaking change with parallel CVSS upgrade, full example regeneration, downstream agent updates (risk-scorer, control-analyzer, threat-report, threat-infographic, report-assembler), and SKILL.md rewrite.

**Compliance Value for Regulated Adopters**: High *eventually* — but contingent on AIVSS reaching v1.0 and on regulators adopting AIVSS as a reference framework. Neither has happened at the present time.

**Why Not Chosen**: The combination of pre-1.0 maturity, schema-breaking effort, parallel CVSS 3.1 → 4.0 upgrade requirement, loss of architecture-aware dimensions, and absence of regulatory mandates makes this option premature. The work is non-trivial and would have to be partially redone when AIVSS v1.0 lands. The decision criteria favor waiting for the maturity signal to clear.

### Option B — Adopt AIVSS as Supplementary Field

**Description**: Keep tachi's four-dimensional composite as the canonical score. Add a new `aivss_score` field to `schemas/risk-scoring.yaml` (additive, no schema-breaking change). The risk-scorer agent computes both scores; `composite_score` remains the field that drives severity bands, governance, and downstream pipeline behavior. The AIVSS field is informational — surfaced in `risk-scores.md`, `risk-scores.sarif`, and the PDF report for cross-framework comparison without affecting pipeline decisions.

**Pros**:
- Additive change — no breaking impact on existing consumers; backward-compatibility PDFs remain byte-identical except for the new column
- Provides a peer signal: external readers familiar with AIVSS can see both frameworks' scores side-by-side without re-running the assessment
- Hedges against AIVSS adoption: if AIVSS reaches v1.0 with industry traction, the supplementary field becomes a step toward Option A
- Smaller blast radius than Option A — one new field, no schema migration, no loss of existing dimensions

**Cons**:
- Per the worked examples above, `composite_score` and `aivss_score` will frequently disagree by 2–3 points on the 0–10 scale and may even fall in different severity bands. Two side-by-side scores that disagree create reader confusion ("which one is right?")
- The CVSS 3.1 vs CVSS 4.0 input gap means the supplementary AIVSS field is not faithful to AIVSS v0.8 unless tachi also computes a CVSS 4.0 vector for every finding — doubling the CVSS authoring effort per finding
- Doubles the per-finding scoring cost (assess against tachi's 4 dimensions AND against AIVSS's 10 AARFs) without doubling the decision-driving signal
- Pre-1.0 churn: AIVSS field implementation must track AIVSS spec changes through v1.0; every spec revision is a potential pipeline change
- Creates an internal inconsistency where the documented "primary" score and the documented "supplementary" score routinely disagree

**Effort**: **M (~2–3 days)** — additive schema field, risk-scorer extension to compute the AIVSS formula, downstream surface updates (risk-scores.md template + SARIF + Typst report), no schema-breaking change.

**Compliance Value for Regulated Adopters**: Moderate — provides the AIVSS score as an informational data point alongside the canonical tachi score. Useful for adopters who must report both, but creates the side-by-side-disagreement problem.

**Why Not Chosen**: The structural divergence between the two scoring models (Surface B) means a supplementary AIVSS field would frequently disagree with the canonical tachi score by 2–3 points. The worked examples in the Rationale section demonstrate this pattern: identical findings produce 9.9 vs 6.9 (Example 1) and 9.4 vs 6.7 (Example 2). Surfacing both scores side-by-side asks downstream consumers to reconcile a divergence that the two frameworks themselves cannot reconcile structurally. The supplementary value does not outweigh the confusion cost. The CVSS 3.1 vs CVSS 4.0 input gap further degrades the AIVSS field's faithfulness — it would not be a "true" AIVSS score unless tachi also adopts CVSS 4.0 for the AIVSS computation, which collapses Option B into a partial Option A.

### Option C — Document Divergence with Rationale (Chosen)

**Description**: No schema change. No new field. This ADR-024 explicitly documents tachi's posture as non-aligned with AIVSS at the present time, names the structural reasons (CVSS-version conflict, formula-shape divergence, dimension-space divergence), and establishes a concrete trigger for re-evaluation. The `tachi-risk-scoring` SKILL.md gains a short cross-reference section pointing readers to this ADR. Downstream consumers see no behavioral change.

**Pros**:
- Zero implementation effort beyond authoring this ADR — no schema change, no agent updates, no example regeneration
- Preserves tachi's architecture-aware dimensions (Reachability, Scalability) that have no AIVSS equivalent
- Avoids first-adopter risk on a pre-1.0 framework; lets the public review period (opening 2026-04-16) and the v1.0 release cycle play out before re-evaluating
- Establishes a discoverable, single-source-of-truth ADR for procurement reviewers, compliance officers, and future maintainers — the alignment question is answered without requiring readers to reconstruct the analysis
- Does not preclude adoption later; the re-evaluation trigger is concrete and scoped
- Preserves backward-compatibility PDF baselines under `SOURCE_DATE_EPOCH=1700000000` (ADR-021) trivially — no pipeline inputs change

**Cons**:
- Tachi remains visibly non-aligned with the OWASP-published agentic-AI scoring standard for the duration of this ADR's validity
- Compliance officers in jurisdictions that ratify AIVSS as a reference framework would need to either translate tachi scores manually or wait for tachi to re-evaluate
- Surface C alignment (severity bands) is preserved but does not constitute "AIVSS compliance" in any formal sense
- If AIVSS v1.0 lands quickly with strong adoption, the re-evaluation lag could become a competitive disadvantage versus tools that adopt earlier

**Effort**: **S (~0 additional effort beyond this ADR and the SKILL.md cross-reference paragraph)** — pure documentation. No schema, no script, no agent, no example output changes.

**Compliance Value for Regulated Adopters**: Moderate — tachi's existing severity bands already align with AIVSS bands (Surface C), so most compliance reporting workflows can use tachi outputs directly. The non-alignment matters only if the regulator requires the *AIVSS scoring methodology* (not just AIVSS-compatible bands), which no regulator does at the present time.

**Why Chosen**: This is the lowest-cost option that preserves tachi's existing model, surfaces the alignment posture explicitly for stakeholders, and does not commit to a pre-1.0 framework. The two structural blockers (CVSS-version conflict and formula-shape divergence) make Options A and B disproportionately effortful relative to the present compliance value. The maturity signal (pre-1.0, public review opening, no external adopters) argues for waiting. The re-evaluation trigger ensures the decision is revisited at a concrete future milestone rather than left indefinite.

---

## Consequences

### Positive

- The alignment question is documented in a single linkable artifact — CISO procurement reviews, compliance officer report-vs-translate decisions, and future maintainer change reviews all anchor here
- Zero pipeline change; zero risk to existing scoring outputs; backward-compatibility PDF baselines (per ADR-021) remain trivially byte-identical
- Tachi retains architecture-aware dimensions (Reachability, Scalability) that have no AIVSS analog
- The `tachi-risk-scoring` skill gains a cross-reference paragraph that downstream consumers (the risk-scorer agent and any developer reading the skill) can use to answer the AIVSS question without leaving the skill file

### Negative

- Tachi is documented as visibly non-aligned with the OWASP-published agentic-AI scoring standard for the duration of this ADR's validity
- A compliance officer at a regulated organization who is mandated to use AIVSS specifically (not just AIVSS-compatible bands) would need to translate tachi scores manually — though no current regulator imposes this mandate
- This decision will need to be revisited within the next 12–18 months as AIVSS matures toward v1.0; the cost of revisiting is bounded by the re-evaluation trigger described below

### Mitigation

- The re-evaluation trigger (AIVSS publishes stable v1.0 with at least one external adopter case study) is concrete and scoped, preventing the decision from becoming an indefinite "no" that ages out of relevance
- The SKILL.md cross-reference makes the divergence visible to every developer working on the risk-scorer pipeline, so future scoring changes are evaluated against this ADR rather than being made in ignorance of it
- The three-surface comparison in this ADR is preserved as a baseline that the next evaluation can refine rather than reconstruct from scratch

### Follow-on Implementation

**No follow-on implementation Issue is filed.** This is a deliberate consequence of choosing Option C per spec FR-007 conditionality: a follow-on Issue is filed only if the decision is Option A or Option B. The re-evaluation trigger described below replaces the follow-on Issue as the anchor for future work.

---

## When to Re-Evaluate

This ADR's posture is valid until **OWASP AIVSS publishes a stable v1.0 release with at least one external adopter case study published in either the AIVSS canonical home, an OWASP project page, or a peer-reviewed industry forum.** When both conditions are met, the architect (or a future equivalent role) should:

1. Re-read the AIVSS v1.0 specification end-to-end and re-run the three-surface comparison in this ADR (Surfaces A, B, C) against the v1.0 dimensions, formula, and bands
2. Reassess the five evaluation criteria (maturity, adoption, compatibility, effort, compliance value) — particularly the maturity and adoption inputs that drove the present Option C decision
3. Re-author this ADR's Decision section, or supersede this ADR with a new ADR if the chosen option changes
4. If the new decision is Option A or Option B, file the follow-on implementation Issue per the FR-007 conditionality preserved across this ADR's lineage

The re-evaluation does not require waiting for a periodic schedule — it is event-triggered. If v1.0 ships and external adopter case studies appear, the trigger fires; otherwise the present posture remains valid.

---

## References

- OWASP AIVSS: [aivss.owasp.org](https://aivss.owasp.org/)
- AIVSS v0.8 specification PDF: [AIVSS Scoring System For OWASP Agentic AI Core Security Risks v0.8](https://aivss.owasp.org/assets/publications/AIVSS%20Scoring%20System%20For%20OWASP%20Agentic%20AI%20Core%20Security%20Risks%20v0.8.pdf)
- CSA MAESTRO reference architecture (companion to AIVSS): [Cloud Security Alliance — MAESTRO](https://cloudsecurityalliance.org/research/working-groups/ai-controls)
- Tachi composite scoring schema: [`schemas/risk-scoring.yaml`](../../../schemas/risk-scoring.yaml)
- Tachi severity bands shared reference: [`.claude/skills/tachi-shared/references/severity-bands-shared.md`](../../../.claude/skills/tachi-shared/references/severity-bands-shared.md)
- Tachi risk scoring skill: [`.claude/skills/tachi-risk-scoring/SKILL.md`](../../../.claude/skills/tachi-risk-scoring/SKILL.md)
- PRD 143: [docs/product/02_PRD/143-maestro-aivss-evaluation-adr-2026-04-14.md](../../product/02_PRD/143-maestro-aivss-evaluation-adr-2026-04-14.md)
- Spec 143: [specs/143-maestro-aivss-evaluation-adr/spec.md](../../../specs/143-maestro-aivss-evaluation-adr/spec.md)
- ADR-018 (baseline-aware pipeline correlation — scoring lineage)
- ADR-019 (shared definitions and model field governance — forward-looking for any follow-on)
- ADR-020 (MAESTRO layer classification — taxonomy context)
- ADR-021 (SOURCE_DATE_EPOCH for deterministic PDF comparison — invariant preserved trivially by this ADR)
