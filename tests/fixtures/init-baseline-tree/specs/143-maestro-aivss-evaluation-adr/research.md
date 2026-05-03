# Research Summary: MAESTRO Phase 4 — OWASP AIVSS Evaluation ADR

**Feature**: 143
**Date**: 2026-04-15
**PRD**: [docs/product/02_PRD/143-maestro-aivss-evaluation-adr-2026-04-14.md](../../docs/product/02_PRD/143-maestro-aivss-evaluation-adr-2026-04-14.md)

---

## Knowledge Base Findings

No pre-existing KB entries specific to AIVSS, but the pattern "documentation-only ADR spike with governance gate" is established through **ADR-022** (mmdc hard prerequisite) and **ADR-023** (threat agent skill references pattern) — both delivered as the ADR artifact of a feature PRD. Feature 082 delivered ADR-023; Feature 130 delivered ADR-022. Same shape applies here: feature PRD → ADR artifact + minimal skill doc update, no production code changes, no example regeneration.

**Key lessons carried forward**:
- ADRs land with `Status: Accepted` at merge (not Proposed) — grep post-condition enforced
- Zero schema / script / agent changes verified by `git diff` at PR review
- Cross-references go in both directions: ADR references related ADRs in frontmatter; skill file references ADR inline
- `docs:` conventional commit type (ADR-only changes do not trigger `feat:` semantic version bumps)

---

## Codebase Analysis

### ADR Ecosystem (docs/architecture/02_ADRs/)

- **23 existing ADRs** (ADR-001 through ADR-023), all in `Status: Accepted`
- **Next available number**: **ADR-024** — no collision, verified by directory listing
- **Zero existing ADRs mention AIVSS** — verified via grep across the directory. ADR-024 will be the canonical AIVSS decision document
- **Most recent ADRs establishing modern format**: ADR-019 (shared definitions), ADR-020 (MAESTRO classification), ADR-021 (deterministic PDF comparison), ADR-022 (mmdc prerequisite), ADR-023 (threat agent skill references)

### Modern ADR Format (per ADR-019 through ADR-023)

Sections in order:
1. **Frontmatter block** — Status, Date, Deciders, Feature, Related ADRs
2. **Context** — problem statement, current state, constraints
3. **Decision** — chosen option stated clearly (one paragraph)
4. **Rationale** — criteria-based justification
5. **Alternatives Considered** — ≥3 options with Pros/Cons and "Why Not Chosen" / "Why Chosen"
6. **Consequences** — Positive / Negative / Mitigation
7. **Related Decisions** (optional) — links to ADRs with relationship labels
8. **When to Re-Evaluate** (optional) — concrete trigger for revisiting
9. **References** — external links, PRDs, related discovery items

### Tachi's Current Risk Scoring Model (three surfaces)

**Surface A — Dimensions** (canonical: `schemas/risk-scoring.yaml:121-126`, defined in `scoring-dimensions.md`):

| Dimension | Weight | Range | Purpose |
|-----------|--------|-------|---------|
| CVSS 3.1 Base | 0.35 | 0.0–10.0 | Standard technical severity (AI-specific vector defaults for 8 threat categories) |
| Exploitability | 0.30 | 0.0–10.0 | Attack feasibility (avg of 4 sub-dims: Known Techniques, Attack Complexity, Tooling, Skill) |
| Reachability | 0.20 | 0.0–10.0 | Architecture-aware surface (trust zone + barriers) |
| Scalability | 0.15 | 0.0–10.0 | Blast radius (avg of 4 sub-dims: Scriptability, Scope, Resources, Detection) |

**Surface B — Composite formula** (`schemas/risk-scoring.yaml:43-46`):
```
composite_score = (0.35 × CVSS) + (0.30 × Exploitability) + (0.20 × Reachability) + (0.15 × Scalability)
```

**Surface C — Severity bands** (canonical: `.claude/skills/tachi-shared/references/severity-bands-shared.md:25-30`):

| Band | Score Range | SLA | Disposition |
|------|-------------|-----|-------------|
| Critical | ≥ 9.0 | 24h | Mitigate |
| High | 7.0 – 8.9 | 7d | Mitigate |
| Medium | 4.0 – 6.9 | 30d | Review |
| Low | < 4.0 | 90d | Review |

### SKILL.md Target for FR-6

File: `.claude/skills/tachi-risk-scoring/SKILL.md` (v1.0.0)
Current sections: `## Domain Overview` (lines 10-19) → `## Baseline-Aware Scoring Rules` (lines 21-92) → `## Loading Table` (lines 94-105).
**Insertion point for `## AIVSS Relationship`**: after line 19 (after Domain Overview), before line 21 (Baseline-Aware Scoring Rules). Matches PRD FR-6 placement directive.

### Prior MAESTRO Phase Delivery Shape

| Phase | PRD | Delivery shape | Timeline |
|-------|-----|----------------|----------|
| Phase 1 | PRD 136 | Enum rename + 14 foundation files + 5 PDF re-baselines | ~1 day |
| Phase 2 | PRD 141 | New schema + new reference + new Typst template + new parser | ~3-4 days (11 waves) |
| Phase 3 | PRD 082 | Lean agent refactor + ADR-023 + 11 skill dirs | ~25h (18 waves) |
| **Phase 4 (this)** | PRD 143 | **ADR-024 + SKILL.md paragraph + conditional follow-on Issue** | **~1 day (2 waves)** |

Phase 4 is the lightest of the four: documentation-only, no production code, no example regeneration.

---

## Architecture Constraints

### Invariants (per constitution + recent ADRs)

- **ADR-021 determinism**: no changes to pipeline outputs; backward-compat PDF baselines must remain byte-identical under `SOURCE_DATE_EPOCH=1700000000` (trivially satisfied — this feature changes no pipeline inputs)
- **ADR-023 detection-variant shape**: no threat agent files touched
- **ADR-019 shared-ref discipline**: if a follow-on adopts AIVSS, any new shared definition (e.g., AIVSS dimension definitions) lands under `tachi-shared/` — but this is a future feature concern, flagged only as a cross-reference from ADR-024
- **Constitution III backward compatibility**: zero schema change, zero breaking change
- **Constitution IX conventional commits**: `docs:` type appropriate for ADR-only commits

### Verification Gates

- Post-PR `git diff main..feature-branch -- schemas/ scripts/ .claude/agents/ examples/` → **must return empty**
- ADR status grep: `grep '^\*\*Status\*\*: Accepted' docs/architecture/02_ADRs/ADR-024-*.md` → **must return 1 match**
- SKILL.md grep: `grep -c 'ADR-024' .claude/skills/tachi-risk-scoring/SKILL.md` → **must return ≥ 1**
- README.md and tech-stack README untouched unless ADR decision requires a cross-reference anchor link

---

## Industry Research

### OWASP AIVSS Current State (as of research window 2026-04-14 to 2026-04-15)

- **Canonical home**: [aivss.owasp.org](https://aivss.owasp.org/) (OWASP Foundation)
- **GitHub**: [OWASP/www-project-artificial-intelligence-vulnerability-scoring-system](https://github.com/OWASP/www-project-artificial-intelligence-vulnerability-scoring-system)
- **Latest version**: **v0.8** (released 2026-03-19) — **pre-1.0**, public review period opens **2026-04-16**
- **Target 1.0**: by end of 2026
- **Scope**: focused on agentic AI systems (not general AI/ML vulnerabilities)

### AIVSS Scoring Model (v0.8)

Formula:
```
AIVSS_Score = ((CVSS_Base_Score + AARS) / 2) × ThM
```

Components:
- **CVSS Base Score**: standard **CVSS v4.0** vector (note: tachi uses **CVSS 3.1** — version mismatch is a concrete comparison point for FR-2 Surface A)
- **AARS (Agentic AI Risk Score)**: sum of 10 **AARFs (Agentic Risk Amplification Factors)** each scored 0.0 / 0.5 / 1.0, range 0–10
- **ThM (Threat Multiplier)**: optional real-world exploitability factor

### AARF List (10 factors in v0.8 publication)

AIVSS's 10 AARFs represent agentic properties that amplify underlying technical severity:
1. Autonomy
2. Tool use
3. Dynamic identity
4. Persistent memory
5. Self-modification
6. (+5 additional factors surveyed in v0.8; exact labeling and operationalization to be read in full during implementation FR-1)

**Conflict flag for FR-2**: AIVSS AARS (agentic amplification) has no direct tachi analog — tachi's `scalability` dimension captures automation blast radius but is agnostic to "agentic" properties. This is a concrete **Gap** row in Surface A.

### Severity Bands

v0.8 publication on `aivss.owasp.org` shows the composite score in the 0–10 range; discrete severity band thresholds were not fully surfaced in web search results — **Surface C comparison must read the v0.8 PDF specification directly during FR-1 research** and capture the cutoffs (if bands are defined) or report "no AIVSS severity bands defined" (if they are not).

### AIVSS Relationship with MAESTRO

CSA MAESTRO explicitly references AIVSS as the companion scoring approach for agentic AI: *"These risk profiles can be benchmarked using OWASP's AI Vulnerability Scoring System (AIVSS)."* — this is the anchor that makes AIVSS strategically relevant to tachi (which ships canonical MAESTRO layers post-Phase 1).

### Composite Formula Divergence (Surface B)

- **Tachi**: weighted sum of 4 dimensions, total weight = 1.0, bounded 0–10
- **AIVSS**: averaged sum of CVSS + AARS (2 terms), scaled by optional ThM, bounded 0–10

The **structural shapes differ**: tachi mixes a technical base (CVSS) with operational dimensions (exploitability, reachability, scalability) via weighting; AIVSS mixes a technical base (CVSS 4.0) with agentic amplification (AARS) via averaging and multiplication. They are **not equivalent formulas** even if the AARF list overlapped conceptually with tachi's dimensions — which it does not.

### CVSS Version Gap

**Material finding**: AIVSS v0.8 builds on **CVSS v4.0**; tachi builds on **CVSS 3.1**. Any "adopt AIVSS" option must confront the CVSS version upgrade simultaneously — this is effort-multiplying and belongs in the Option A / Option B pros/cons table.

### Maturity Signal for Recommendation

- AIVSS v0.8 is pre-1.0 with a **public review period opening 2026-04-16** (the day after planned merge for this PRD)
- No external adopter case studies published
- 1.0 target: end of 2026

Maturity is a decisive input for **Option C (diverge with re-evaluation clause)** as the likely recommendation, with the re-evaluation trigger tied to AIVSS 1.0 publication + at least one external adopter case study.

---

## Recommendations for Spec

1. **Treat this as an ADR-only spike feature** — the spec must mirror the PRD's scope boundaries explicitly. Zero schema, script, agent, or example changes.
2. **Use the three-surface comparison shape** from PRD FR-2 — dimensions, formula weights, severity bands. Do not collapse to a dimension-only mapping (would hide CVSS version gap and formula shape gap).
3. **Capture the CVSS version gap (3.1 vs 4.0) explicitly** in Surface A — this is a concrete conflict row, not an overlap.
4. **Anticipate the likely Option C recommendation** based on AIVSS maturity — v0.8 is pre-1.0, no external adopters, 1.0 target end of 2026. But do not prejudge; implementer picks after reading the full v0.8 spec during FR-1.
5. **Include the "When to Re-Evaluate" trigger** aligned to AIVSS 1.0 publication + external adopter case study — this is the PRD Risk R2 mitigation text.
6. **File the follow-on issue conditionally** only if Option A or B is chosen — no premature issue filing. The Issue body must include the option-specific effort estimate verbatim from ADR-024 Alternatives Considered (FR-7 business rule).
7. **Preserve five enforcement layers for scope discipline** (per PRD): spec FR excludes, success criteria, out-of-scope list, constraints, post-merge `git diff` assertion.
8. **Related ADRs in frontmatter**: minimum ADR-020 (MAESTRO taxonomy) + ADR-019 (shared refs — forward-looking for follow-on) + ADR-018 (baseline-aware pipeline, scoring lineage).
9. **SKILL.md placement**: after `## Domain Overview` (line 19), before `## Baseline-Aware Scoring Rules` (line 21). Paragraph 80-200 words, matches ADR decision verbatim, contains relative link to ADR-024.
10. **Governance checkpoint**: architect approval on tasks.md **is** the "Accepted at merge" attestation (closed in PRD Open Questions). No separate sign-off ceremony.

## Key References

**Internal**:
- PRD: [docs/product/02_PRD/143-maestro-aivss-evaluation-adr-2026-04-14.md](../../docs/product/02_PRD/143-maestro-aivss-evaluation-adr-2026-04-14.md)
- Schema: [schemas/risk-scoring.yaml](../../schemas/risk-scoring.yaml)
- Current SKILL target: [.claude/skills/tachi-risk-scoring/SKILL.md](../../.claude/skills/tachi-risk-scoring/SKILL.md)
- Severity bands: [.claude/skills/tachi-shared/references/severity-bands-shared.md](../../.claude/skills/tachi-shared/references/severity-bands-shared.md)
- Pattern reference: [ADR-022](../../docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md), [ADR-023](../../docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md)

**External** (to be verified end-to-end during FR-1):
- [aivss.owasp.org](https://aivss.owasp.org/) — AIVSS canonical home
- [AIVSS v0.5 specification PDF](https://aivss.owasp.org/assets/publications/AIVSS%20Scoring%20System%20For%20OWASP%20Agentic%20AI%20Core%20Security%20Risks%20v0.5.pdf) — last archived published draft
- [OWASP project page](https://github.com/OWASP/www-project-artificial-intelligence-vulnerability-scoring-system) — GitHub repository

---

## Wave 1 AIVSS Spec Notes

**Research date**: 2026-04-15
**Conducted by**: web-researcher (Wave 1 of /aod.build, T003-T005)
**Source verified**: aivss.owasp.org reachable; v0.8 PDF accessible
**Timebox status**: Completed within 2-hour cap; no PM escalation required

### Canonical Identification (T003)

- **Latest published version**: **v0.8** (titled "AIVSS Scoring System For OWASP Agentic AI Core Security Risks v0.8")
- **Canonical URL**: https://aivss.owasp.org/
- **PDF**: https://aivss.owasp.org/assets/publications/AIVSS%20Scoring%20System%20For%20OWASP%20Agentic%20AI%20Core%20Security%20Risks%20v0.8.pdf
- **Joint publishers**: OWASP AIVSS, AIUC-1, OWASP AI Exchange, OWASP Citizen Development Top 10
- **Public review**: opens 2026-04-16 (day after planned merge)

### End-to-End Read (T004) — Four Comparison Axes

#### (a) Exact version string
`AIVSS Scoring System For OWASP Agentic AI Core Security Risks v0.8`

#### (b) Canonical URL
https://aivss.owasp.org/

#### (c) Full dimension list (10 AARFs — exact names from v0.8 §2.2)

The AARFs are scored on a 3-point scale (0.0 / 0.5 / 1.0) per v0.8 Table 1:

1. **Execution Autonomy (Autonomy)** — ability to execute actions without human verification
2. **External Tool Control Surface (Tools)** — breadth and privilege of external APIs/tools
3. **Natural Language Interface (Language)** — reliance on unstructured NL for goal formulation
4. **Contextual Awareness (Context)** — utilization of environmental sensors or broad data context
5. **Behavioral Non-Determinism (Non-Determinism)** — variance in output/action for identical inputs
6. **Opacity & Reflexivity (Opacity)** — lack of internal visibility / inability to audit decisions
7. **Persistent State Retention (Persistence)** — ability to retain memory/state across sessions
8. **Dynamic Identity (Identity)** — ability to assume different user roles or permissions at runtime
9. **Multi-Agent Interactions (Multi-Agent)** — coordination or dependencies on other agents
10. **Self-Modification (Self-Mod)** — ability to alter its own code, prompts, or tool configurations

#### (d) Composite formula (CORRECTED from pre-research notes)

The formula in the original `research.md` industry research section (`AIVSS_Score = ((CVSS_Base_Score + AARS) / 2) × ThM`) is **incorrect** and must be discarded. The actual v0.8 formula per §3.4 is:

```
AIVSS = (CVSS_Base + AARS) * Mitigation_Factor
AIVSS_final = RoundHalfUp(AIVSS, 1)
```

Where:
- `CVSS_Base` = CVSS v4.0 base score (0.0–10.0)
- `AARS` = `(10 - CVSS_Base) * (Factor_Sum / 10) * ThM` — the agentic uplift
- `Factor_Sum` = sum of all 10 AARFs (range 0.0–10.0)
- `ThM` = Threat Multiplier (Attacked=1.00, Proof-of-Concept=0.97 default, Unreported=0.50)
- `Mitigation_Factor` = 1.00 (None/Weak, default), 0.83 (Partial), or 0.67 (Strong)

The AARS is an **uplift term**: it consumes the "remaining gap" between CVSS_Base and 10.0, scaled by the proportion of agentic factors present. AARFs alone cannot drive the score above 10.0; they amplify the technical baseline up to the ceiling.

#### (e) Severity bands (DEFINED in v0.8 §3.5.2)

The pre-research note that "severity band thresholds were not fully surfaced" is **wrong**. v0.8 §3.5.2 defines bands explicitly:

| Band | Range |
|------|-------|
| Critical | 9.0 – 10.0 |
| High | 7.0 – 8.9 |
| Medium | 4.0 – 6.9 |
| Low | 0.1 – 3.9 |

Per v0.8: "These thresholds are adopted from CVSS severity band conventions for cross-framework consistency."

**Material observation**: AIVSS bands are **essentially identical** to tachi's bands (`Critical ≥ 9.0 / High 7.0–8.9 / Medium 4.0–6.9 / Low < 4.0`). The only edge difference is the lower bound of Low (AIVSS uses 0.1; tachi uses 0.0) — operationally indistinguishable at one-decimal rounding. **Surface C is therefore Overlap, not Conflict, despite the divergent CVSS-base versions and composite formulas.**

#### (f) CVSS base version

**CVSS v4.0** is an explicit requirement per v0.8 §3.1.1: *"AIVSS requires CVSS v4.0 as its baseline scoring input. Practitioners should not use CVSS v3.1 scores as inputs to the AIVSS formula, as the metric structures are not directly comparable."*

Tachi uses **CVSS 3.1**. This is the concrete **Conflict row** in Surface A.

### Tachi Cross-Read Confirmation (T005)

Verified the following surfaces in tachi's current state — no schema changes since the `/aod.spec` research window:

- `schemas/risk-scoring.yaml:43-46`: composite formula `(0.35 × CVSS) + (0.30 × Exploitability) + (0.15 × Scalability) + (0.20 × Reachability)` — total weight 1.0
- `schemas/risk-scoring.yaml:122-126`: weights map confirms cvss_base=0.35, exploitability=0.30, scalability=0.15, reachability=0.20
- `schemas/risk-scoring.yaml:129-133`: severity bands Critical (9.0-10.0), High (7.0-8.9), Medium (4.0-6.9), Low (0.0-3.9)
- `.claude/skills/tachi-shared/references/severity-bands-shared.md:25-30`: same bands, with boundary precision rule (boundary maps to higher band)
- `.claude/skills/tachi-risk-scoring/references/scoring-dimensions.md:21`: Exploitability = avg(Known Techniques, Attack Complexity, Tooling Availability, Skill Level) / 4
- `.claude/skills/tachi-risk-scoring/references/scoring-dimensions.md:55`: Scalability = avg(Scriptability, Target Scope, Resource Requirements, Detection Difficulty) / 4

### Decision Implication Summary (input for Wave 2)

Three structural divergences make adopt-as-primary (Option A) high-effort and adopt-as-supplementary (Option B) of limited marginal value:

1. **CVSS version gap** (3.1 vs 4.0) — Option A would require a parallel CVSS 3.1→4.0 schema migration; Option B would create internal inconsistency
2. **Composite shape divergence** — tachi's weighted-sum model bounded by inputs vs AIVSS's amplification model that consumes the CVSS-base headroom; the two models cannot produce equivalent scores even with identical inputs
3. **Dimension space divergence** — tachi has 4 operational dimensions (one technical + three operational); AIVSS has 1 technical dimension + 10 agentic amplification factors; only Multi-Agent and Tools loosely overlap with tachi's Scalability inputs

The maturity signal (pre-1.0, no external adopter case studies, public review opens 2026-04-16) compounds the structural divergence into a clear **Option C (Document Divergence with Rationale)** recommendation, with re-evaluation tied to AIVSS 1.0 + external adopter case study.
