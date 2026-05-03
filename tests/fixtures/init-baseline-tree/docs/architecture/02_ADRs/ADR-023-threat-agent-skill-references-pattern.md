# ADR-023: Threat Agent Skill References — Sibling Variant of the Lean Pattern

**Status**: Accepted
**Date**: 2026-04-11
**Accepted**: 2026-04-11 (post Phase 1 combined checkpoint / T023, Feature 082 Wave 8)
**Deciders**: Architect, Product Manager, Team-Lead
**Related Feature**: Feature 082 — Threat Agent Skill References
**Related ADRs**: [ADR-014](ADR-014-gemini-api-optional-image-generation.md) (optional external APIs), [ADR-020](ADR-020-maestro-layer-classification.md) (MAESTRO orchestrator-owned classification), [ADR-021](ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md) (deterministic PDF comparison), [ADR-022](ADR-022-mmdc-hard-prerequisite.md) (first CLI prerequisite ADR precedent)

---

## Context

tachi ships 17 agents organized into two tiers with different load characteristics. The **infrastructure tier** — orchestrator, risk-scorer, control-analyzer, threat-report, threat-infographic, report-assembler — was migrated to a lean + skill references pattern across PRDs 029, 075, and 078. Each infrastructure agent file stays small (typically 60-120 lines) while the bulk of its domain knowledge lives in a companion `.claude/skills/tachi-<name>/references/` directory loaded on-demand via `**MANDATORY**: Read` directives. The Chroma "Context Rot" study (July 2025, cited in PRD 029) measured a ~30% instruction-following accuracy improvement from context reduction, which the infrastructure-tier refactor validated on 6 example architectures.

The **detection tier** — 6 STRIDE agents and 5 AI agents (11 total) — remained on a self-contained inline shape in which every detection pattern, severity hint, and finding template was embedded directly in the agent file. This was consistent with pre-PRD-029 conventions but diverged from the rest of the pipeline after 075 and 078 landed. Concrete line-count pressure at the time of this ADR: STRIDE agents range 113-141 lines, AI agents range 167-201 lines, aggregate 1,680 lines across the 11 files. Of the 11, 10 breach the tier-specific cap proposed in Feature 082 (STRIDE ≤120, AI ≤150), and 3 AI agents breach even the 180-line hard ceiling. Every new threat pattern added since 078 made the gap wider.

Feature 082 resolves the divergence by extending the lean pattern to the detection tier. The central design question was whether detection agents should reuse the control-analyzer **methodology variant** (phase-gated loads with `**MANDATORY**: Read` directives at each of 6 phases) or a new variant. Control-analyzer is a 6-phase pipeline (classification, evidence gathering, effectiveness assessment, residual-risk calculation, recommendation generation, output). Threat detection has no equivalent multi-phase structure: it is a single-pass operation that iterates dispatched components, matches them against patterns, constructs findings, and emits them. Forcing methodology-variant shape onto a single-pass agent would add no value, obscure the actual control flow, and confuse contributors.

This ADR records the decision to introduce the **detection variant** as a sibling to the methodology variant — a second documented lean-agent shape in tachi with its own naming rule, its own load point, and its own enforcement hooks. The four decisions below capture the variant's definition, its boundary with orchestrator-owned MAESTRO classification, its shared-reference edit discipline, and its producer/consumer audience separation in `finding-format-shared.md`.

A secondary driver is the `tachi-shared/references/*.md` fleet, which was authored during PRDs 075 and 078 as the canonical source for severity bands, STRIDE categories, finding format, and MAESTRO layers — consumed exclusively by the 6 infrastructure agents. Feature 082 causes the 11 threat agents to begin reading two of those files (`finding-format-shared.md` and `stride-categories-shared.md`) for the first time, which cross-wires the two tiers at the shared-reference layer. The blast radius of any shared-ref edit grows from 6 consumers to 17, and the edit discipline required to keep the infrastructure tier stable becomes a first-class design concern rather than an implementation detail. Decisions 3 and 4 codify that discipline; Decision 2 draws the MAESTRO hard line to prevent the cross-wiring from leaking into layer-inheritance logic.

---

## Decision

### Decision 1 — Sibling Variant with Single-Point Load

Detection agents adopt a **single-point load** variant of the lean + skill references pattern. Each of the 11 threat agent files contains exactly one `**MANDATORY**: Read` directive, placed at the start of a `## Detection Workflow` section, pointing at the companion `detection-patterns.md` reference file. The directive fires once per agent invocation — not once per phase, not once per component, not once per pattern — because detection is a single pass.

The section name `## Detection Workflow` is **mandatory** and distinct from the methodology variant's phase-oriented headings. Using `## Phase Workflow`, `## Methodology`, or any phase-implying name is forbidden because it would misrepresent the control flow and blur the boundary between the two variants. The name is the contributor-visible signal that the agent is single-pass, not multi-phase — a contributor opening an unfamiliar threat agent file should see `## Detection Workflow` and immediately know the load point is once-per-invocation and the pattern matching is a single pass. The same contributor opening a control-analyzer-style file should see numbered `## Phase N` headings and know the load points are phase-gated. The section heading is the first and cheapest form of documentation about the agent's shape, and it should never lie about the shape.

This creates exactly two documented lean-agent shapes in tachi:

1. **Methodology variant** (PRD 075, control-analyzer) — phase-gated loads, one `**MANDATORY**: Read` per phase, `## Phase N: <name>` section headings.
2. **Detection variant** (PRD 082, 11 threat agents) — single-point load, one `**MANDATORY**: Read` at workflow start, `## Detection Workflow` section heading.

Any future lean agent must select one of these two variants by matching its control-flow shape; introducing a third variant requires a new ADR.

**Enforcement**: FR-1 and FR-16 in the Feature 082 spec; structural diff check in Phase 3 Polish T054 verifies every threat agent has exactly one `**MANDATORY**: Read` directive under a `## Detection Workflow` heading.

### Decision 2 — MAESTRO Orchestrator-Owned Boundary

MAESTRO layer inheritance runs entirely in orchestrator Phase 3 (Table Assembly), as established by ADR-020. Threat agents MUST remain MAESTRO-agnostic. This boundary is re-affirmed and extended by Feature 082 as follows: **no MAESTRO references appear in any of the 11 threat agent files or in any of their companion `detection-patterns.md` reference files**. The 11 companion skill directories describe STRIDE or AI threat categories only — never MAESTRO layers.

A contributor who adds a MAESTRO reference (layer name, heading, lookup table, inheritance rule) to a threat agent file or to any file under `.claude/skills/tachi-<threat-agent>/references/` MUST have the change rejected in code review. The rationale is not stylistic: duplicating MAESTRO classification logic in multiple locations would create drift risk against the orchestrator-owned truth table, and the downstream table-assembly code would no longer be the single source of truth for layer inheritance.

The shared reference file `maestro-layers-shared.md` is explicitly **not** read by any threat agent. Even though it lives in `.claude/skills/tachi-shared/references/`, it stays consumed only by orchestrator, risk-scorer, control-analyzer, threat-report, and threat-infographic — the same set as before Feature 082.

**Enforcement**: FR-9 invariant. Grep check asserting zero MAESTRO matches across all 11 threat agent files AND their companion reference files runs in Phase 1a T014 (prototype gate) and Phase 3 Polish T054 (final sweep). A non-zero match count on either check is a hard failure — no exceptions.

This ADR re-affirms and extends ADR-020. ADR-020 established orchestrator-owned inheritance for the infrastructure tier; ADR-023 Decision 2 extends the same boundary to the threat-agent tier, closing a gap that did not exist before Feature 082 because the threat tier did not have companion reference files.

### Decision 3 — Additive-Only Shared Reference Edits

Edits to `.claude/skills/tachi-shared/references/*.md` files during Feature 082 are **additive-only by default** — this is a policy posture, not a contingency or a best-effort target. Existing sections remain **byte-identical** pre/post edit. New sections are appended with new `##` headings. Existing frontmatter may be augmented (e.g., expanding the `consumers:` list to include additional agents) but existing frontmatter keys retain their existing values.

If existing content MUST change — for example, if an existing section of `finding-format-shared.md` contains consumer-specific phrasing that would confuse a producer audience — the escalation path is to **create a new file alongside the existing one** (the `tachi-shared-threat/` directory contingency documented as R3 in the Feature 082 spec). In-place modification of existing shared-reference content is forbidden for the duration of Feature 082.

Rationale: `tachi-shared/references/*` is in active production use by the 6 infrastructure agents, all of which passed their Phase 1 regression gates in PRDs 029/075/078 with those files in their current shape. Any byte-level modification to existing content risks silently breaking the infrastructure tier — the failure mode would not appear until a downstream regression run on the 5 byte-deterministic example PDFs (per ADR-021). Feature 136 paid exactly this cost once already (5 PDFs re-baselined after the `maestro-layers-shared.md` edit). Treating additive-only as the default posture — rather than a contingency — reduces R3 risk from "possible, and mitigated by Phase 3 re-baseline" to "prevented by construction."

**Enforcement**: FR-5, C9, C10 in the Feature 082 spec. Phase 2/3 code review (reviewer compares byte-level diff of every existing section). Phase 6 T044 grep check (asserts every existing `## ` heading in `tachi-shared/references/*.md` is unchanged). Phase 7 T047 cross-agent overlap audit (confirms infrastructure agents still cite the same line ranges they cited pre-082).

### Decision 4 — Consumer/Producer Audience Separation in `finding-format-shared.md`

Shared reference files may legitimately serve two audiences simultaneously:

- **Consumers** — Agents that read findings produced by other agents. Today: orchestrator (for dispatch correlation), risk-scorer (for baseline score computation), control-analyzer (for mapping findings to controls). Consumers need validation rules, field-type contracts, and correlation semantics.
- **Producers** — Agents that generate findings. Today (post-082): the 11 threat agents. Producers need field-construction guidance, ID-prefix assignment tables, risk-level computation worked examples, and reference-linking conventions.

`finding-format-shared.md` was originally authored (PRD 078) as a **consumer-oriented validation spec**. Under this ADR, it gains a new appended section `## For Threat Agents (Producers)` (+40 to +60 lines, per plan §1.3) that covers producer-audience needs. The existing consumer content is byte-identical pre/post edit (Decision 3 applies). The file's frontmatter `consumers:` list is expanded from the 3 infrastructure consumers to the 3 infrastructure consumers plus 11 threat-agent producers.

The two audiences live in the same file via clearly separated `## ` section headings. Producer content is NOT duplicated into a separate `finding-format-producer.md` file.

Rationale: Splitting producer and consumer content into two files would create **format drift risk** — the same ID-prefix table, the same field-type contract, and the same risk-level formula would exist in two places, and a future edit to one copy could silently diverge from the other. Co-locating under clear section headings preserves single-source-of-truth semantics. Contributors editing the file are guided by the section headings on which audience they are serving with a given change.

**Enforcement**: Phase 6 T042 single-writer commit appends the producer section (one author, one commit, one reviewer — no parallelization on this one file). Phase 6 T043 updates all 11 threat agent `## Skill References` tables to cite `finding-format-shared.md` as a second Read target alongside the companion `detection-patterns.md`.

---

## Consequences

### Positive

- **Two documented lean-agent shapes**: tachi now has explicit, named variants for the two legitimate control-flow shapes (methodology multi-phase and detection single-pass). Future agent design has a vocabulary for discussing which shape fits.
- **All 17 agents on one architectural pattern**: After Feature 082, every tachi agent follows lean + skill references. No remaining self-contained inline-pattern agents.
- **Future threat enrichment is a one-file edit**: Adding a new detection pattern category is an append to the companion `detection-patterns.md` reference file, not an edit to the agent file. Reduces agent-file churn and enables parallel per-category contribution. Review surface area shrinks because an enrichment PR touches one reference file rather than an agent file plus inline patterns plus example sections.
- **Line-count pressure resolved at the tier level**: The 1,680-line aggregate across 11 threat agents drops to an expected ≤1,650 lines aggregate with STRIDE ≤120 each and AI ≤150 each (hard ceiling 180). All 10 agents currently over their tier cap return to compliance, and the 3 AI agents currently over the 180 hard ceiling come back under it.
- **MAESTRO boundary is now enforced at two tiers**: ADR-020 covered infrastructure. Decision 2 here extends the same boundary to detection. The invariant is grep-checkable across the entire agent+reference surface.
- **Shared reference blast radius is bounded by construction**: Decision 3 makes additive-only the default, not the fallback. Infrastructure-tier regression risk from Feature 082 drops from "possible, mitigated after-the-fact" to "prevented before-the-fact."

### Negative / Known Debt

- **No automated threat-agent test coverage** (Principle VI known debt): tachi has no per-agent pytest harness today, and this feature does not introduce one. Validation relies on content-level regression on 6 example architectures and the 5-PDF byte-deterministic baseline. Consistent with PRDs 029/075/078/084/091/104/128/136 — all predecessors shipped with the same test posture. A future PRD should evaluate a per-agent mock-harness, but the design is out of scope here.
- **Shared reference edits now require cross-tier review**: Because `finding-format-shared.md` gains a producer audience, any future edit must be reviewed by both infrastructure-tier and detection-tier agent owners. This raises review overhead on that file. Mitigation: the file's `consumers:` frontmatter now explicitly names both tiers so reviewers know whom to loop in.
- **Phase 2c shared-ref consolidation is single-writer and serial**: Per C10, the `finding-format-shared.md` producer section is committed by a single writer. Per-agent work (Phase 2a/2b) can parallelize across 5 STRIDE and 4 AI agents, but Phase 2c cannot. This is a deliberate trade-off for correctness.

### Neutral

- **`## Detection Workflow` is the mandatory section name**: All 11 threat agents use the identical heading. Contributors editing threat agents know what to look for. No per-agent creativity in section naming.
- **Tier-specific line targets persist**: STRIDE ≤120 lines, AI ≤150 lines, hard ceiling 180 for any threat agent. These targets are invariant properties of the refactored tier, tracked in FR-10 and SC-002.
- **Phase 3 re-baseline of 5 PDFs is expected**: Per ADR-021, shared reference edits flow through to infra agents and from there into the 5 byte-deterministic example PDFs. FR-17 and SC-008 make the re-baseline an expected Phase 3 outcome, not a test failure. Feature 136 set the precedent.
- **Prototype-first gate on 2 agents before the remaining 9**: Feature 082 validates Decisions 1 through 4 on `spoofing.md` (STRIDE) and `prompt-injection.md` (AI) in Phase 1a/1b before any work begins on the other 9 agents. The gate enforces this ADR's claims empirically — if any decision above is wrong, the cost of finding out is bounded to 2 agents, not 11. Max 2 gate iterations before escalation per C7.
- **ADR remains in Draft status until Phase 1b passes**: The header status stays `Draft` until the prototype gate on `spoofing.md` + `prompt-injection.md` completes successfully. T022 promotes the header to `Accepted`. If the gate fails and one or more decisions above must change, the ADR is revised in place while still in Draft — no version bump needed.

---

## Alternatives Considered

### Alternative 1 — Force methodology variant onto detection agents

- **Pros**: Single unified pattern, no need to introduce a second variant, no new section-naming rule.
- **Cons**: Wrong abstraction. Detection agents are single-pass (match → apply → emit). A phase-gated shape would require either inventing phases that do not exist (e.g., Phase 1: Match, Phase 2: Apply, Phase 3: Emit — none of which is a methodology phase in control-analyzer's sense) or reusing control-analyzer's 6-phase naming that has no natural mapping to detection. Contributors would be misled about the control flow. Loaded context would grow because the same reference file would be re-read at each fake phase boundary.
- **Rejected**.

### Alternative 2 — Frontmatter-only registration with no Read directive

- **Pros**: Implicit tool loading would be simpler for contributors who must author a new threat agent — they would only declare the reference file in frontmatter and the harness would load it.
- **Cons**: Relies on harness behavior that Claude Code does not currently support. Pre-PRD-075 agents tried this shape and the reference files were not loaded reliably — the agent invocation would start without the reference file in context, producing inconsistent detection output. The `**MANDATORY**: Read` directive pattern is explicit precisely because implicit loading is unreliable.
- **Rejected**.

### Alternative 3 — Eager in-place consolidation (modify existing shared references freely)

- **Pros**: Single-pass edit of shared references is faster than additive-only editing. Saves an estimated 1-2 hours of review and sequencing overhead in Phase 2c.
- **Cons**: Risk of silently breaking the 6 infrastructure agents in active production use. The failure mode is detected only at Phase 3 regression on the 5 byte-deterministic PDFs, at which point rollback is expensive. The 1-2 hour savings are not worth the blast radius.
- **Rejected** in favor of Decision 3.

---

## Phase 1 Validation

This section records the empirical outcomes of the Feature 082 Phase 1 prototype gate, on which this ADR's Draft → Accepted promotion is conditioned. The prototype extracted two threat agents — `spoofing.md` (STRIDE tier) and `prompt-injection.md` (AI tier) — in two sub-phases: Phase 1a (refactor-only, no enrichment) and Phase 1b (enrichment layered on the refactored prototypes). Both sub-phases were reviewed by joint architect + team-lead gates (T015 and T021 respectively). The six findings below — two from Phase 1a, four from Phase 1b — represent the joint ruling consensus. No fifth ADR decision was required; the decisions above stand as authored.

### From T015 (Phase 1a Gate Ruling)

1. **Sibling variant structurally validated on n=2 across tiers.** Decision 1 (single-point load at the start of `## Detection Workflow`) was applied to one STRIDE agent (spoofing: 113 → 51 lines, a 55% reduction) and one AI agent (prompt-injection: 167 → 95 lines, a 43% reduction, post-prototype-consistency fix). Both refactored agents passed T012 regression via the Option B content-equivalence methodology — verbatim preservation of detection patterns in the companion reference file, MANDATORY Read delegation, and shared-ref sourcing of the OWASP 3×3 matrix and finding template — proving zero content delta against the pre-refactor baselines. T014 zero-MAESTRO grep across the 4 touched files (2 agents + 2 companion refs) returned zero matches, confirming Decision 2 holds at the prototype. The sibling variant pattern generalizes structurally to both tiers; a full n=11 generalization is deferred to Phase 4+5 (Waves 9-11) empirically.

2. **Canonical agent shape is 5 sections, not 7 (Option A ruling).** The T015 joint review ratified that the canonical shape is **5 sections** in order: (1) YAML frontmatter, (2) metadata YAML block, (3) `## Purpose`, (4) `## Skill References` table, (5) `## Detection Workflow`. AI-tier agents append an inline `## Example Findings` section as a 6th section per Q7 default. `## Empty Results Handling` and `## Output Handoff` are explicitly NOT in the canonical shape — the pre-refactor source did not contain these sections at level 2 in any of the 11 threat agent files, the plan.md §1.1 "preserve as-is from today" claim was inaccurate, and a corresponding retraction now lives in plan.md §1.1. Empty-results behavior is inherited from the Detection Workflow component-iteration step (zero components match → zero findings produced); handoff semantics are owned by the orchestrator Phase 3 Table Assembly contract per ADR-020 (agents are pulled from by the orchestrator, they do not push). Option A was preferred over Option B (mandate the 2 sections + backfill stub content on all 11) because the latter would have expanded scope on a refactor-only feature, added +1.5-2h to the critical path, compounded the Phase 6 single-writer bottleneck, and risked MAESTRO-isolation boundary violations on the handoff stubs.

### From T021 (Phase 1b Gate Ruling)

3. **±2 tolerance interpretation (b) ratified.** The Phase 1b gate criteria "finding count per category within ±2" is interpreted as applying to *pre-existing-category finding drift*, not to *new-category count*. Under interpretation (a), any enrichment adding more than 2 new categories per agent would structurally fail the regression gate (prompt-injection added 3 categories in T017, which would false-positive under (a)) — this would make the feature's ≥2-per-agent enrichment floor incompatible with its own regression gate, an unreasonable gate-design outcome. Interpretation (b) aligns with the gate's purpose per FR-14 and Decision 3 above: regression *prevention* on pre-existing signals, not an absolute cap on category count. The interpretation has been documented in plan.md Technical Context §Testing (one-sentence clarification) as of Wave 8 pre-T022 housekeeping, and will be in place before T049 (Wave 14 aggregate enrichment floor check) and T050 (Wave 15 full regression gate) to prevent ambiguity from recurring during Phase 7+8.

4. **Option B methodology: valid with an asymmetry caveat.** The Option B content-equivalence and DFD-vs-pattern cross-reference proof methodology is accepted for Phase 1 prototype scale (n=2 agents, ~5-10 new categories). It is strong on "no existing findings dropped" (byte-preservation of pre-existing patterns is a deterministic proof) but weaker on "≥1 new finding surfaces from enrichment" — the proof shows only that the conditions for a new finding are met on specific DFD elements in specific examples, not that findings empirically emerge under a live `/tachi.threat-model` invocation. For the prototype scale and the resource-constrained subagent environment in which gate verification is performed, the asymmetry is acceptable. **At T047 (Phase 7 cross-agent audit) and T050 (Phase 8 full regression gate), Option A (live `/tachi.threat-model` invocation against the 6 example architectures, diffed against T001 baselines) is preferred over Option B if operationally feasible** — the aggregate n=11 agent scale warrants empirical rather than structural proof.

5. **Detection category overlap is acceptable at enrichment time; re-audit at T047 via additive-signal test.** The Phase 1b prototype produced two pattern categories (Spoofing C7 "Cloud IAM Role Assumption Chain Abuse" and Prompt-Injection C6 "Direct Injection and Jailbreaks — Evolved Variants") that partially overlap with existing categories in the same reference file. The T021 ruling permits overlap now — it does not block or iterate the gate — subject to a mandatory re-audit at T047 (Wave 13 cross-agent overlap audit) via the **additive-signal test**: does the new category add detection indicators that the existing category lacks? All 5 new categories added in T016/T017 pass this test on first-principles security-analyst reading per the T020 spot-check. T047 will formally apply the additive-signal test across all 11 agents' enriched reference files and assign canonical owners where overlap is not additive.

6. **Exit criterion E-4 partially validated.** E-4 requires the sibling load-shape variant to be declared in ADR-023 (this document — Decision 1). The Phase 1 prototype proves the variant works structurally on n=2 across both the STRIDE tier (spoofing) and the AI tier (prompt-injection) — which is what Phase 1 was scoped to prove. **Full n=11 generalization is explicitly out of Phase 1's scope** and is what Phase 4+5 (Waves 9-11) will prove empirically via the 9 remaining agent extractions. If Waves 9-11 surface an agent whose detection control flow does not fit the single-point-load shape (no such risk identified in the pre-refactor source audit, but not definitively ruled out), the E-4 claim must be revisited and Decision 1 potentially amended. The T023 Phase 1 Combined Checkpoint records Phase 1 as complete on this partial-validation footing, and Phase 4+5 gates will upgrade the validation scope as they progress.

---

## References

- **Feature 082 PRD**: [docs/product/02_PRD/082-threat-agent-skill-references-2026-04-11.md](../../product/02_PRD/082-threat-agent-skill-references-2026-04-11.md)
- **Feature 082 Spec**: [specs/082-threat-agent-skill/spec.md](../../../specs/082-threat-agent-skill/spec.md)
- **Feature 082 Plan**: [specs/082-threat-agent-skill/plan.md](../../../specs/082-threat-agent-skill/plan.md) — specifically §1.1 (agent redesign), §1.2 (companion skill layout), §1.3 (shared reference additive edits), §1.4 (this ADR outline)
- **PRD 029** — Original lean + skill references pattern introduction (infrastructure tier)
- **PRD 075** — Lean pattern extension via control-analyzer methodology variant (first named variant)
- **PRD 078** — Lean pattern validation and `finding-format-shared.md` authoring (original consumer-only surface; T014 clamping-bug discovery precedent)
- **ADR-020**: MAESTRO layer classification — established orchestrator-owned inheritance. Decision 2 above re-affirms and extends that boundary to the threat-agent tier.
- **ADR-021**: SOURCE_DATE_EPOCH for deterministic PDF comparison — used by Phase 3 re-baseline of the 5 byte-deterministic example PDFs.
- **ADR-022**: First CLI prerequisite ADR — precedent for the ADR-NNN sequence and the fail-loud posture on missing dependencies. Referenced here for the ADR sequencing convention and the explicit-enforcement-hook style borrowed by this ADR.

---

## Future Work

- **Load-shape frontmatter field**: Evaluate extracting a `load_shape: phase-gated | single-point | inline` field into agent-file frontmatter if a third sibling variant ever appears. Currently deferred — with n=2 variants, the field would be premature abstraction. Revisit when a third lean-agent control-flow shape is proposed.
- **Automated threat-agent test coverage**: Principle VI known debt declared in this ADR's "Negative / Known Debt" section should be addressed by a follow-up PRD. A per-agent mock harness that stubs the orchestrator dispatch interface and validates detection output on fixture component lists would reduce reliance on the 6-example regression. Out of scope for Feature 082.
- **Reusable shared-reference edit helper**: If a third feature requires additive-only edits to `tachi-shared/references/` files, consider extracting a byte-level diff validator into `scripts/` (analogous to ADR-022's deferred `scripts/preflight.sh` helper — same three-consumer threshold).
- **Producer/consumer split across more shared references**: If `severity-bands-shared.md` or `stride-categories-shared.md` grows a need for producer-audience content beyond what already exists, Decision 4's section-level split pattern should be reused (co-located `## For Threat Agents (Producers)` section inside the same file). Do not preemptively add such sections before the need is concrete — the current files are already producer-compatible for the purposes of Feature 082.
- **Contributor-visible variant selection doc**: A short "which variant should my agent use?" decision table belongs alongside this ADR, likely in `docs/architecture/` or as a section inside a future agent-authoring guide. The table would map control-flow shapes (single-pass, phase-gated, hybrid) to variant names (detection, methodology) with one example each. Out of scope for Feature 082 itself; opens as a documentation debt item.
