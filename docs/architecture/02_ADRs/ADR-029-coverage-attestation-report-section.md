# ADR-029: Coverage Attestation Report Section

**Status**: Accepted
**Date**: 2026-04-18 (Proposed) / 2026-04-23 (Accepted, provisional pending PR merge)
**Accepted-commit-SHA**: `<pending-post-merge-fill>`
**Deciders**: Architect, Product Manager, Team-Lead
**Feature**: 194 (F-B Coverage Attestation Report Section — BLP-01 Coverage Attestation Reporting tier)
**Related ADRs**: [ADR-021](ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md) (SOURCE_DATE_EPOCH determinism), [ADR-022](ADR-022-mmdc-hard-prerequisite.md) (CLI fail-loud), [ADR-023](ADR-023-threat-agent-skill-references-pattern.md) (22-file zero-edit invariant), [ADR-026](ADR-026-pattern-classification-mechanism.md) (schema versioning rule), [ADR-027](ADR-027-taxonomy-crosswalk-schema.md) (F-A1 taxonomy schema), [ADR-028](ADR-028-source-attribution-schema-extension.md) (F-A2 source_attribution contract — direct predecessor)

---

## Context

Tachi's agentic-AI threat-modeling pipeline produces a multi-artifact output set rendered as a branded PDF security report (`security-report.pdf`). The report today carries a Cover + Executive Summary + Attack Path pages (Feature 112) + per-category threat narratives + risk-score tables + compensating-control analysis + optional infographics (Features 084 / 091 / 128 / 141). Every new report section is gated behind a deterministic `has-<x>` boolean computed by `scripts/extract-report-data.py` so that architectures lacking the underlying signal regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000` per ADR-021. This convention has been exercised four times: Feature 084 (`has-maestro-data`), Feature 128 (`has-infographic-<template>`), Feature 141 (`has-attack-chains`), and Feature 112 (`has-attack-trees`). Each feature added a new Typst page template + an orchestrator-computed boolean + a `detect_*` function in `extract-report-data.py` and preserved the byte-identity harness by construction.

Feature 180 (F-A1) shipped 2026-04-17 (squash-merge commit `8b7c7bf`) delivering 7 machine-readable taxonomy catalogs under `schemas/taxonomy/` plus a 526-edge cross-framework `crosswalk.yaml`, governed by ADR-027. Feature 189 (F-A2) shipped same-day 2026-04-17 (squash-merge commit `6d5d890`) extending `schemas/finding.yaml` with an optional list-of-RECORD `source_attribution` field (schema 1.4 → 1.5), governed by ADR-028. Together F-A1 + F-A2 publish both sides of the coverage-attestation data contract: F-A1 the framework-ID vocabulary, F-A2 the finding-level citation field. Neither feature populates attributions on real findings (F-A3 is the populator feature) and neither feature wires the downstream consumer that renders coverage claims to the end user.

Feature 194 (F-B — this ADR) is the **consumer-side bridge** of the BLP-01 attestation initiative. F-B consumes `threats.md` Section 9 (F-A2's serialization surface) and aggregates `source_attribution` arrays across findings to produce per-framework coverage-matrix pages in the PDF security report. The output surfaces as a new conditional section in `security-report.pdf` — gated by a `has-source-attribution` boolean computed at extraction time — with one page per external framework showing Covered / Partial / Gap classifications for every framework item in the F-A1 catalog. F-B does NOT populate attributions on any finding (F-A3 scope), does NOT consult `schemas/taxonomy/crosswalk.yaml` (cross-framework JOIN deferred), does NOT modify `schemas/finding.yaml` or any F-A1 catalog YAML (read-only consumer), and does NOT edit any of the 22 detection-tier files ADR-023 stabilized and ADR-028 extended (populator scope is F-A3).

F-B is the second of the 3-feature BLP-01 reporting initiative: F-A3 (threat-agent populators that emit `source_attribution` during detection — touches the 22-file detection tier), F-B (this feature — the PDF attestation section renderer over already-landed F-A2 contract data), F-C (cross-framework JOIN via `crosswalk.yaml`, deferred). F-B is deliberately orderable BEFORE F-A3 because the `has-source-attribution` gate means F-B is a no-op on any architecture whose findings carry no attributions — including all 5 non-agentic baselines tachi ships today. F-B can merge, exercise its gate on a fixture-authored attribution payload, and wait for F-A3 to populate real-world coverage data on real architectures without regressing SC-002 byte-identity on the 5 baselines.

PRD 194 was approved 2026-04-18 with full Triad sign-off; the spec was triple-signed APPROVED same day with 19 FRs and 12 SCs. The PRD and spec preserve the three resolved PRD questions (Q1-A 3-value classification, Q2-A denominator authority, Q6-D Out-of-Scope deferral) and defer Q5 visual treatment to an architect-authored fallback memo (see `specs/194-coverage-attestation-report-section/q5-visual-treatment-architect-fallback.md`) pending ux-ui-designer input Day 2 AM. All seven decision surfaces enumerated in FR-013 are resolved in this ADR.

### Constraints

- **SC-002 byte-identity BLOCKER** (spec SC-002, FR-011, FR-012): the 5 non-agentic example baselines (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) MUST regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000` per ADR-021 against `tests/scripts/test_backward_compatibility.py`. All 5 baselines have absent `source_attribution` on every finding today; F-B preserves this by gating the entire section behind `has-source-attribution: false` on every baseline. Any code path that emits a PDF byte when the gate is false regresses SC-002.
- **SC-009 22-file zero-edit invariant BLOCKER** (spec SC-009, FR-014): F-B MUST NOT edit any file under `.claude/agents/tachi/stride/*.md` (6 files), `.claude/agents/tachi/ai/*.md` (5 files), or `.claude/skills/tachi-{agent-name}/references/detection-patterns.md` (11 files). ADR-023 Decision 2 stabilized this 22-file scope; ADR-028 Decision 6 extended the pattern to F-A2; F-B extends it a third time. The invariant is grep-auditable at PR pre-merge per SC-009.
- **FR-015 zero schema changes BLOCKER**: F-B MUST NOT modify `schemas/finding.yaml` or any file under `schemas/taxonomy/`. F-B is a renderer + aggregator over schemas that already landed in Feature 180 (F-A1 catalogs) and Feature 189 (F-A2 `source_attribution` field). Empty diffs on these paths are verified at PR pre-merge.
- **FR-016 zero new runtime dependencies**: empty diffs on `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, and `package.json`. `pyyaml` and `pytest` remain developer-only per Feature 128 precedent. Typst is already the PDF render engine (Features 112 / 128 / 141); no new CLI prerequisite is introduced.
- **FR-017 zero-crosswalk-JOIN scope boundary**: F-B MUST NOT consult `schemas/taxonomy/crosswalk.yaml`. Coverage reasoning in F-B is **intra-framework only** — each per-framework page aggregates attributions to items in that one framework's catalog. Cross-framework JOIN (e.g., "findings citing OWASP LLM05 imply coverage of CWE-1426 via the crosswalk") is deferred to a follow-on feature. This is a hard scope line, not a deferred implementation detail.
- **ADR-021 determinism**: any aggregator helper introduced by F-B MUST be a pure function of its inputs — no HTTP fetches, no timestamps beyond what Typst already reads, no environment reads beyond `SOURCE_DATE_EPOCH`. The `extract-report-data.py` helper reads `schemas/taxonomy/*.yaml` at extraction time; per-invocation cache scoped to a local dict only (ADR-028 Decision 5 precedent).
- **ADR-027 referential anchor**: F-B reads F-A1 catalogs at extraction time to compute denominators and item lists. F-B MUST NOT modify any file under `schemas/taxonomy/` — F-A1 remains the authoritative source. F-B consumes the read-only contract.
- **ADR-028 referential anchor**: F-B reads F-A2's `source_attribution` field from `threats.md` Section 9 via the existing `parse_threats_findings` parser (extended in F-A2 at `scripts/tachi_parsers.py:621` with the conditional-key round-trip). F-B MUST NOT modify the parser contract.
- **Cold-start adopter UX**: on any architecture whose findings carry no attributions (all 5 baselines today, and every pre-F-A3 real-world architecture), the `has-source-attribution` gate is `false` and the attestation section is omitted. Adopters see no new pages until F-A3 populates attributions OR the adopter's own toolchain writes `source_attribution` into `threats.md`.

---

## Decision

We adopt the **F-B Coverage Attestation Report Section** as specified below. A new conditional section is rendered in the PDF security report, gated by a `has-source-attribution` boolean computed by `scripts/extract-report-data.py`, with one page per external framework aggregating finding-level attributions into Covered / Partial / Gap classifications against the F-A1 catalog denominator. Seven numbered decisions below document the contract.

### Decision 1 — Typst template + aggregator + `has-source-attribution` boolean (Feature 141 + Feature 128 precedent)

F-B adopts the established tachi pattern for conditional PDF report sections: a **new Typst page template** rendered conditionally based on a **new `has-<signal>` boolean** computed by a **new aggregator function in `extract-report-data.py`**. The pattern has been exercised four times and is the canonical shape for new PDF sections in tachi.

**Feature 141 precedent — `has-attack-chains`**: Feature 141 (cross-layer attack chains) added a new conditional section to the threat report with a `has-attack-chains: bool` data variable gating rendering at `templates/tachi/security-report/main.typ:246`. The main template inspects the boolean and conditionally includes the attack-chain page template. When no chains are surfaced, the boolean is `false` and the main template emits zero bytes for the section — preserving byte-identity on baseline architectures lacking chain signal.

**Feature 128 precedent — infographic boolean + new Typst page**: Feature 128 (executive-architecture infographic) added a new page with `detect_images()` returning a boolean gate consumed by `main.typ`'s `infographic-page()` function. The detect helper at `scripts/extract-report-data.py:1362` scanned for the JPEG output of the extraction pipeline and emitted `has-infographic-executive-architecture: bool` as a data variable. The pattern isolated all byte-sensitive logic to a single deterministic helper.

**F-B adoption**: F-B introduces three artifacts following the established pattern:
1. **New Typst template `templates/tachi/security-report/coverage-attestation.typ`** — renders a section header page plus one page per external framework (5 frameworks from the F-A2 enum). Each per-framework page contains: framework name + denominator + coverage headline (per Decision 7 Partial disclosure rule), Covered / Partial / Gap matrix of framework items, per-item finding-ID citation list where applicable.
2. **New aggregator function `aggregate_coverage_attestation()` in `scripts/extract-report-data.py`** — reads the `source_attribution` arrays off parsed findings (using the F-A2 parser round-trip), reads the 5 F-A1 external-framework catalog YAMLs (using `yaml.safe_load` with per-invocation local-dict caching per ADR-028 Decision 5), computes per-framework-per-item classification (Covered / Partial / Gap per Decision 2), and emits a structured data dict consumed by the Typst template.
3. **New `has-source-attribution: bool` data variable** — set to `true` iff at least one finding in the current threat model carries a non-empty `source_attribution` array. Main template at `templates/tachi/security-report/main.typ` inspects the boolean and conditionally includes the coverage-attestation template. When `false`, zero bytes emit for the section.

**Gating rule** (Feature 141 `has-attack-chains` / ADR-028 Decision 2 precedent): the orchestrator computes `has-source-attribution` at extraction time. The boolean is `true` iff any finding in the current threat model carries a non-empty `source_attribution` array. On all 5 non-agentic baselines today, the boolean is `false` because every baseline finding has absent `source_attribution`. The coverage-attestation section is therefore omitted entirely from every baseline PDF — no section header, no per-framework pages, no trailing separator, no TOC entry. This is the direct Feature 141 Section 6 convention, extended a fourth time.

**Why this pattern over alternatives**: PRD 194 considered integrating attestation into an existing section (e.g., as a subsection of the threat report or risk-score page). The new-page pattern was selected because (a) the attestation payload is large enough (5 framework pages × ~30-50 items each in real-world architectures) that embedding it as a subsection would displace existing content tables, (b) the conditional gating shape is proven at byte-identity across Features 084 / 091 / 112 / 128 / 141 / 112, and (c) separating the section behind its own template keeps the byte-sensitive logic isolated to a single file where it can be audited at PR review.

### Decision 2 — Q1-A 3-value classification rule (Covered / Partial / Gap)

The coverage-matrix page classifies every item in each per-framework catalog into exactly **3 values**:

| Classification | Condition |
|----------------|-----------|
| **Covered** | At least one finding cites the framework item with `relationship: primary` |
| **Partial** | Zero primary attributions AND at least one `related` or `derived` attribution |
| **Gap** | Zero attributions (no finding cites the item at all) |

This is the **Q1-A resolution** from PRD 194. Alternatives Q1-B (4-value with an explicit "Out-of-Scope" classification distinct from Gap) and Q1-C (2-value collapse of Partial into Covered) were considered and rejected at PRD time.

**Why 3-value over 4-value**: a 4-value classification would introduce "Out-of-Scope" as a first-class adopter-visible distinction — e.g., items that are tachi-architecturally-inapplicable (a cloud-provider OWASP item on a single-node local app) would be classified separately from items genuinely uncovered. The 4-value classification requires a per-framework-per-item scoping mechanism, which in turn requires either (a) F-A1 YAML extensions carrying `applicable_contexts` metadata, or (b) per-threat-model architect annotation. Both options are non-trivial scope expansions and neither is visible in adopter demand today. Q6-D deferral (Decision 5 below) resolves the Out-of-Scope question space by collapsing it into Gap in MVP.

**Why 3-value over 2-value**: collapsing Partial into Covered would hide a meaningful adopter-visible distinction. A framework item cited by one finding with `relationship: related` is not the same attestation claim as a framework item cited by one finding with `relationship: primary` — the canonical mapping vs the adjacent mapping is exactly the distinction ADR-028 Decision 4 closed-enum'd at the finding-level. Surfacing only 2 values at the coverage tier would erase the enum distinction and mislead adopters counting "coverage percentage" (a Partial-only item is not fully covered; a Covered item is).

**Partial-only edge case** (documented in spec): if a framework item has attributions on multiple findings — some `related`, some `derived`, zero `primary` — it classifies as Partial per the rule above. The `related`-vs-`derived` distinction is NOT surfaced at the coverage-matrix tier (both collapse to Partial); it remains visible on the per-finding citation list within each matrix cell via bold-vs-plain rendering. Visual treatment is governed by the Q5 fallback memo or the ux-ui-designer memo if it lands Day 2 AM.

**Classification determinism**: the classification function is a pure function of `(framework_item_id, {all findings with source_attribution}, framework_catalog_ids)`. No LLM judgment, no heuristics, no configuration knobs. Identical inputs yield identical classifications across runs.

### Decision 3 — Q2-A denominator authority

The **coverage-percentage denominator** for each external framework is `len(yaml.safe_load(schemas/taxonomy/{framework}.yaml))` — the count of top-level items in the F-A1 catalog YAML for that framework. The denominator is computed **once per framework at extraction time** and cached in the local-dict per-invocation cache (ADR-028 Decision 5 precedent).

This is the **Q2-A resolution** from PRD 194.

**Explicit 5-framework scope**: denominators are computed for exactly the **5 external frameworks** from the ADR-028 Decision 3 enum: `owasp`, `mitre-attack`, `mitre-atlas`, `nist-ai-rmf`, `cwe`. The 2 internal tachi taxonomies from ADR-027 Decision 3 (`tachi-control-category`, `tachi-stride-ai-category`) are **deliberately EXCLUDED** per FR-018. Rendering internal-taxonomy coverage pages would be a self-referential claim: tachi attesting coverage of its own output vocabulary is definitionally trivial (every finding is categorized under `tachi-stride-ai-category` via the existing schema 1.0 `category` field). The 5-framework scope in F-B mirrors the 5-value `taxonomy` enum in ADR-028 Decision 3 exactly — no adopter-visible inconsistency between what findings can cite (5 external frameworks per ADR-028) and what F-B reports coverage of (5 external frameworks per this ADR).

**Why denominator = catalog length, not crosswalk-derived**: an alternative denominator authority considered at PRD time was "the count of framework items reachable from tachi's STRIDE+AI category set via `crosswalk.yaml` primary edges." That denominator would be **smaller** (a subset of the full catalog), yielding **higher coverage percentages**. It was rejected on two grounds: (a) coverage percentages become incomparable across architectures whose finding distributions exercise different subsets of the crosswalk — a real-world adopter comparing two reports would see percentages that depend on crosswalk coverage rather than on finding-attribution coverage, and (b) the crosswalk-derived denominator requires `crosswalk.yaml` JOIN, violating FR-017's zero-crosswalk-JOIN scope boundary.

**Denominator stability across framework versions**: when F-A1 catalog YAMLs are revised (e.g., OWASP LLM Top 10 ships a 2027 edition adding 2 items), the denominator changes automatically on the next report run. No F-B code changes required. This is the intended shape — F-B consumes F-A1 as a read-only contract and inherits F-A1's versioning story.

**Computation cost**: 5 YAML reads per report generation, each YAML under 50 records for OWASP / MITRE ATLAS and under 400 records for CWE (F-A1 catalog sizes verified at F-A1 merge). Aggregate cost is sub-100ms on commodity hardware per the F-A1 SC-013 performance bound. Cached per-invocation in the local dict; no cross-invocation memoization (ADR-021 determinism preservation).

### Decision 4 — Zero-crosswalk-JOIN scope boundary (FR-017)

F-B does **NOT** consult `schemas/taxonomy/crosswalk.yaml`. The coverage matrix is **intra-framework only** — each per-framework page aggregates finding-level attributions to items in that one framework's catalog. Cross-framework JOIN (e.g., "findings citing OWASP LLM05 imply coverage of CWE-1426 via the crosswalk primary edge") is deferred to a follow-on feature.

**What "intra-framework only" means concretely**:
- A finding cites `{taxonomy: owasp, id: LLM05, relationship: primary}`. F-B increments the Covered count on OWASP page for item LLM05. F-B does NOT traverse the crosswalk to find adjacent CWE or MITRE ATLAS items and does NOT increment coverage on any other framework page from this citation.
- A finding cites three records `{owasp, LLM05, primary}`, `{cwe, CWE-1426, primary}`, `{mitre-atlas, AML.T0051, related}`. F-B increments Covered on OWASP (LLM05) and CWE (CWE-1426) and Partial on MITRE ATLAS (AML.T0051). Each framework page is computed independently from the attributions that name that framework.
- On the OWASP page, items without a direct OWASP citation are classified Gap — even if the same finding cites a CWE item that is crosswalk-linked to the missing OWASP item. The crosswalk relationship is invisible to F-B.

**Why this scope line**: cross-framework JOIN is structurally a separate feature because (a) it introduces a new "inferred coverage" concept distinct from the direct-attribution coverage F-B attests, (b) the inferred-coverage concept has confidence-calibration implications (ADR-027 Decision 5 anti-drift rule is per-edge; propagating confidence to inferred framework coverage requires a new aggregation policy), and (c) adopter UX around inferred coverage is unclear — should inferred-coverage items visually render identical to direct-coverage items, or distinct? The feature that resolves these questions is a follow-on; F-B ships the direct-attribution attestation first.

**Crosswalk JOIN follow-on**: the follow-on feature (tentatively F-C in the BLP-01 reporting initiative, not yet filed as a PRD) is explicitly authorized by FR-017. F-C will consume `crosswalk.yaml` in addition to the F-A1 catalogs and F-A2 `source_attribution` arrays. F-C will re-evaluate coverage classifications with inferred-coverage rules. F-C is not blocked on F-A3 populator completion — F-C can iterate on fixture-authored attribution payloads after F-B ships.

**Architect invariant**: the crosswalk-JOIN boundary is a **hard scope line**, not a deferred implementation detail. Adding crosswalk consumption to F-B later would change the meaning of coverage classifications retroactively, regressing any adopter who deployed F-B at Covered/Partial/Gap semantics and then saw percentages shift under them. The correct path is a named follow-on feature with its own PRD, ADR, and a decision record whether F-B's intra-framework-only attestation continues to exist alongside or is superseded.

### Decision 5 — Q6-D Out-of-Scope deferral

All non-cited items classify as **Gap** in MVP. No 4th adopter-visible "Out-of-Scope" classification exists. Adopter-visible Out-of-Scope treatment is deferred to a follow-on feature once demand is visible.

This is the **Q6-D resolution** from PRD 194.

**What Out-of-Scope would mean if introduced**: a 4th classification would distinguish items that are *structurally inapplicable* to the current architecture (e.g., "OWASP LLM03 Training Data Poisoning" on an architecture that does no model training) from items that are *architecturally applicable but uncovered* (e.g., same LLM03 on an architecture that does fine-tune but for which no finding cites LLM03). Both of these classify as Gap in MVP.

**Why deferral rather than implementation**:
1. **Scoping mechanism is non-trivial**: Out-of-Scope requires either (a) F-A1 YAML extensions with `applicable_contexts` metadata per catalog item, (b) per-threat-model architect annotation of which items apply, or (c) LLM-judgment over architecture-item applicability. Each option is a larger scope than MVP justifies.
2. **Adopter demand not visible**: no feature-request, Issue, or forum post surfaced the Out-of-Scope question-space in the BLP-01 requirements-gathering phase. The Q6-D resolution is explicitly "defer until demand is visible" — consistent with the tachi principle of shipping the MVP decision and widening on measured demand.
3. **Gap classification is honest in MVP**: adopters seeing "Gap" on an item that is genuinely inapplicable can read the item description and understand it doesn't apply to their architecture. The classification label slightly understates coverage, but does not mislead — it errs on the side of under-claiming coverage rather than over-claiming, which is the conservative direction for a security attestation.
4. **Visual treatment already conveys the distinction informally**: the per-framework page renders both the classification (Covered / Partial / Gap) and the per-item finding-citation list. An adopter scanning the Gap items can visually check whether any finding cites adjacent items (a proxy for architectural applicability) without requiring an explicit fourth classification.

**Deferral target**: the follow-on feature (tentatively F-D in the BLP-01 reporting initiative, not yet filed) will evaluate the scoping-mechanism options against adopter demand signals visible after F-B + F-A3 ship. F-D is not blocked on F-B or F-A3; it is blocked on demand visibility.

### Decision 6 — 22-file zero-edit invariant preservation (ADR-023 / ADR-028 lineage)

F-B MUST NOT edit any file in the 22-file zero-edit scope. The scope is identical to the ADR-023 Decision 2 enumeration preserved by ADR-028 Decision 6:

**STRIDE agent files (6)** — under `.claude/agents/tachi/`:
- `.claude/agents/tachi/spoofing.md`
- `.claude/agents/tachi/tampering.md`
- `.claude/agents/tachi/repudiation.md`
- `.claude/agents/tachi/info-disclosure.md`
- `.claude/agents/tachi/denial-of-service.md`
- `.claude/agents/tachi/privilege-escalation.md`

**AI agent files (5)** — under `.claude/agents/tachi/`:
- `.claude/agents/tachi/prompt-injection.md`
- `.claude/agents/tachi/data-poisoning.md`
- `.claude/agents/tachi/model-theft.md`
- `.claude/agents/tachi/tool-abuse.md`
- `.claude/agents/tachi/agent-autonomy.md`

**Skill-reference files (11)** — one per agent above:
- `.claude/skills/tachi-spoofing/references/detection-patterns.md`
- `.claude/skills/tachi-tampering/references/detection-patterns.md`
- `.claude/skills/tachi-repudiation/references/detection-patterns.md`
- `.claude/skills/tachi-info-disclosure/references/detection-patterns.md`
- `.claude/skills/tachi-denial-of-service/references/detection-patterns.md`
- `.claude/skills/tachi-privilege-escalation/references/detection-patterns.md`
- `.claude/skills/tachi-prompt-injection/references/detection-patterns.md`
- `.claude/skills/tachi-data-poisoning/references/detection-patterns.md`
- `.claude/skills/tachi-model-theft/references/detection-patterns.md`
- `.claude/skills/tachi-tool-abuse/references/detection-patterns.md`
- `.claude/skills/tachi-agent-autonomy/references/detection-patterns.md`

**Rationale — ADR-023 / ADR-028 sibling-pattern governance**: ADR-023 stabilized the 11-agent skill-references pattern in Feature 082. ADR-028 Decision 6 was the first extension preserving the invariant in F-A2 (the F-A2 contract feature). This ADR is the **second extension** preserving the invariant in F-B (the F-B consumer feature). The pattern is: features that do not populate `source_attribution` do not edit detection-tier files. Population is explicitly F-A3 scope.

**Scope boundary — F-B renderer vs F-A3 populator**:
- F-B (this feature) ships the Typst template, the aggregator helper, the `has-source-attribution` boolean, and the ADR. It does NOT edit any detection-tier file. It consumes whatever attributions F-A3 has (or has not) populated.
- F-A3 (follow-on feature) wires populators — threat-detection agents emit `source_attribution` values during detection. F-A3 MAY edit the 22 files. F-A3 is governed by its own PRD and ADR.

**Enforcement — grep-auditable**: the F-B PR is blocked from merge if `git diff main..HEAD --name-only` returns any file in the 22-file scope. This is enforced at PR review time by the team-lead per spec SC-009.

**Downstream silence — F-B renderer is read-only on F-A2 contract surfaces**: the F-A2 schema (`schemas/finding.yaml` at version 1.5), the F-A1 catalogs (`schemas/taxonomy/*.yaml`), the F-A2 parser round-trip (`scripts/tachi_parsers.py::parse_threats_findings` and `validate_source_attribution`) are all read-only from F-B's perspective. F-B neither modifies the schema nor the parser. F-B introduces ONLY the Typst template, the aggregator in `extract-report-data.py`, and the main template conditional include at `main.typ`.

### Decision 7 — R9/MED-3 Partial disclosure rule

Each per-framework coverage-matrix page MUST render the **Partial count alongside the coverage percentage with equal visual weight**. The headline format is:

```
{Framework Name}
Covered: {covered_count} / {denominator} = {coverage_percentage}% · Partial: {partial_count} · Gap: {gap_count}
```

**Concrete example** (illustrative — actual numbers depend on finding population):

```
OWASP LLM Top 10
Covered: 12 / 38 = 31.6% · Partial: 3 · Gap: 23
```

The Partial count MUST be visible to any reader who sees the coverage percentage. Visual weight equality means: font size, font weight, color, and placement must not make Partial subordinate to Covered or Gap. The three counts render on the same typographic line or in a three-column table with equal column weights.

**Rationale — prevent adopter misreading of percentage semantics**: without the Partial disclosure rule, an adopter reading "31.6% coverage" would reasonably assume that the remaining 68.4% of items have no attribution at all. In the example above, 3 of the 23 remaining items actually have Partial attributions (related or derived citations). A security attestation reader who aggregates "coverage %" across multiple frameworks in a dashboard could form a misleading picture of tachi's attribution density. The Partial disclosure corrects this by surfacing the middle classification at equal visual weight.

**R9/MED-3 risk reference**: PRD 194 Risk R9 identified a MED-3 (medium severity, detection gap) risk that adopters conflate Covered + Partial as "70%-ish coverage" when presented only the Covered percentage. Mitigation MED-3 is this exact disclosure rule: the headline presents all three counts, not the percentage alone.

**Why not a single "overall coverage score" that weights Partial at 0.5 or similar**: weighting schemes introduce a confidence-calibration parameter that requires architect decision (what weight? why?) and opens adopter questions about whether `related` and `derived` should weight equally into Partial. The weighted-score alternative was rejected at PRD time on the grounds that (a) any weight is arbitrary, (b) weight choices are adopter-dependent (a compliance-focused adopter may weight Partial at 0.25; a threat-hunting adopter may weight at 0.75), and (c) the 3-count raw presentation gives the adopter the data to compute their own weighted score if needed. The headline is the raw-data presentation; no weighted aggregation is computed.

**Typography requirement**: the Q5 visual treatment memo (ux-ui-designer input Day 2 AM, or the architect fallback at `specs/194-coverage-attestation-report-section/q5-visual-treatment-architect-fallback.md`) specifies the color and icon treatment for Covered / Partial / Gap per-item cells. The Decision 7 disclosure rule governs the page-header counts — the top-of-page headline row is independent from the per-item-cell visual treatment, but both conventions must render Partial at equal visual prominence with Covered and Gap.

---

## Alternatives Considered

### Alternative 1 — Subsection of the threat report (no new Typst template)

Render the coverage attestation as a new subsection within the existing threat report rather than as a new top-level section with its own Typst template.

**Pros**:
- Reuses the existing threat-report Typst template surface; no new template file
- Co-locates attestation with threat findings (same page, continuous reading)
- Smaller diff; faster initial review

**Cons**:
- Attestation payload on real-world architectures is large (5 framework pages × ~30-50 items each); embedding as a subsection would displace existing threat-report content and regress the visual cadence of that section
- The `has-source-attribution` gating rule becomes harder to isolate at byte-identity audit time if it is a sub-template conditional within a larger template; separating to its own template keeps the byte-sensitive logic in one file
- Section-level TOC entry is cleaner than subsection-level; adopters scanning the PDF cover for attestation jump directly to a top-level section

**Why Not Chosen**: the new-template pattern is the established tachi convention (Features 084 / 091 / 112 / 128 / 141) and isolates byte-sensitive logic. The subsection alternative optimizes for initial-review speed at the cost of long-term auditability.

### Alternative 2 — Inline attestation on each finding row

Render attestation as a new column on the Section 7 finding table in `threats.md` AND the corresponding PDF threat report table, showing per-finding framework citations inline.

**Pros**:
- No new page; additive to existing table surface
- Per-finding granularity visible without jumping to a separate section

**Cons**:
- Does not produce the **per-framework coverage view** adopters actually need — the question "what % of OWASP does tachi attest coverage of?" cannot be answered from per-row citations
- Column widening on §7 / threat-report tables historically triggers byte-identity sensitivity (§7 renders on every threat model); SC-002 preservation would require careful conditional-column logic
- Per-finding inline display is already handled by the §9 YAML block in `threats.md` (F-A2 Decision 2) — adding a §7 column duplicates the information in a less machine-readable form

**Why Not Chosen**: adopter need is per-framework aggregation, not per-finding enrichment. The per-finding surface exists (F-A2 Section 9); F-B is the per-framework aggregation feature. Adding the per-framework coverage view to the per-finding surface does not satisfy the aggregation use case.

### Alternative 3 — Crosswalk-JOIN at MVP (FR-017 rejection)

Consume `schemas/taxonomy/crosswalk.yaml` at MVP to produce inferred-coverage classifications alongside direct-attribution classifications. A finding citing OWASP LLM05 would confer inferred coverage on CWE-1426 via the crosswalk primary edge; the CWE page would show the inferred coverage with a distinct visual treatment.

**Pros**:
- Richer coverage story at first-ship — adopters see cross-framework coverage inferences immediately
- Closes the F-C follow-on feature at F-B ship-time; one fewer follow-on to file

**Cons**:
- Introduces a new "inferred coverage" concept that has unresolved confidence-calibration semantics (per-edge confidence vs inferred-coverage confidence propagation rules)
- Adopter UX around inferred-vs-direct coverage is uncharted; no adopter has asked for inferred coverage in the BLP-01 requirements phase
- Changes the meaning of F-B coverage classifications retroactively if the crosswalk data changes — a crosswalk revision would shift inferred coverage percentages across every previously-generated report
- Violates the MVP discipline of shipping the direct-attribution attestation first and widening on measured demand
- Is incompatible with FR-017 as explicitly written in the spec

**Why Not Chosen**: FR-017 is an explicit hard scope line, not a deferred implementation detail. The crosswalk-JOIN alternative is structurally a separate feature (F-C) because it introduces new semantic concepts that require their own decision records. Attempting to embed it in F-B MVP would conflate two features and make F-B's decision surface non-reviewable in isolation.

### Alternative 4 — 4-value classification with explicit Out-of-Scope (FR-019 rejection)

Render a 4-value coverage matrix with Covered / Partial / Gap / Out-of-Scope, where Out-of-Scope items are distinguished from Gap on architectural-applicability grounds.

**Pros**:
- More honest coverage percentage — Gap is narrowed to items that are applicable-but-uncovered, separating from items that are definitionally inapplicable
- Adopter UX acknowledges that some framework items may not apply to a given architecture

**Cons**:
- Requires a scoping mechanism (F-A1 YAML extensions with `applicable_contexts`, OR per-threat-model annotation, OR LLM judgment) — all three options are substantially larger scope than MVP
- No adopter demand has surfaced the Out-of-Scope question-space in the BLP-01 requirements phase
- Introduces a new architect decision (how is applicability determined?) that has not been made at PRD time
- Is incompatible with FR-019 as explicitly written in the spec

**Why Not Chosen**: Q6-D deferral (Decision 5 above) is the correct posture for MVP. The Out-of-Scope question-space is real but not yet demand-visible; the follow-on feature (F-D) is the right scope for resolving it. Collapsing non-cited items into Gap in MVP is conservative (under-claiming coverage rather than over-claiming) and is the honest shape for a security attestation.

---

## Consequences

### Positive

- **Per-framework coverage attestation shipped to adopters**. Adopters see Covered / Partial / Gap classifications against each of the 5 external frameworks (OWASP / MITRE ATT&CK / MITRE ATLAS / NIST AI RMF / CWE), aggregated from finding-level attributions. The attestation is machine-readable via the underlying F-A2 YAML contract and human-readable via the PDF rendering.
- **SC-002 byte-identity preserved by construction**. The `has-source-attribution` gate is `false` on all 5 non-agentic baselines today (every baseline finding has absent `source_attribution`). The coverage-attestation section is omitted entirely from every baseline PDF. Every byte of every baseline artifact is unchanged. SC-002 is green at merge without any special-case harness work.
- **SC-009 22-file zero-edit invariant preserved**. ADR-023 stabilization holds. ADR-028 extension holds. F-B is the second extension of the invariant, continuing the pattern of "features that do not populate source_attribution do not edit detection-tier files." F-A3 bears the regression risk of reopening the detection tier.
- **FR-015 zero schema changes preserved**. Empty diffs on `schemas/finding.yaml` and every file under `schemas/taxonomy/`. F-B is a pure renderer + aggregator over already-landed schemas.
- **FR-016 zero new runtime dependencies preserved**. Empty diffs on `pyproject.toml`, `requirements*.txt`, and `package.json`. Typst and pyyaml (already present) are the only runtime surfaces touched.
- **FR-017 zero-crosswalk-JOIN scope boundary preserved**. F-B never reads `crosswalk.yaml`. Cross-framework inference is deferred to F-C (follow-on feature); F-B's decision surface is reviewable in isolation.
- **Cold-start adopter UX is graceful**. On any architecture whose findings carry no attributions (including all 5 baselines and every pre-F-A3 real-world adopter run), the gate is `false` and the section is omitted. Adopters see no new pages until attributions are populated — no empty-table placeholder, no "0% coverage" headline that would mislead.
- **Forward-compatible with F-A3 population**. When F-A3 wires threat-detection agents to emit `source_attribution` during detection, the gate flips to `true` on any architecture with attributions and the section renders automatically. No F-B code changes required at F-A3 merge.
- **R9/MED-3 Partial disclosure rule prevents coverage misreading**. The headline format ensures adopters never see a coverage percentage without the Partial count alongside. Dashboard aggregators pulling from PDF OCR or from the underlying YAML aggregation see all three counts and can compute adopter-specific weighted scores.
- **ADR-021 determinism preserved**. The aggregator helper is a pure function with per-invocation local-dict caching (ADR-028 Decision 5 precedent). No HTTP, no timestamps, no environment reads beyond what the existing Typst harness consumes. The SC-002 byte-identity harness needs no new knobs.

### Negative

- **Coverage claims on pre-F-A3 architectures read as 0%**. Until F-A3 populates `source_attribution` on real findings, the attestation section never renders for real-world adopter runs — F-B is effectively invisible until F-A3 ships. Mitigated by the fixture-authored attribution payload in the F-B test suite, which exercises the renderer end-to-end without requiring F-A3.
- **F-B MUST be re-validated at F-A3 merge**. When F-A3 populates attributions on real findings, the `agentic-app` baseline (which F-A3 will regenerate) and any new baselines carrying attribution will surface coverage-attestation sections. Rendering determinism under `SOURCE_DATE_EPOCH=1700000000` across F-A3-populated baselines needs a second round of SC-002 verification. Mitigated by the ADR-028 Decision 5 local-dict caching pattern and by the Feature 141 `has-attack-chains` precedent, which has already proven rendering determinism for conditional YAML-sourced sections.
- **Cross-framework coverage claims are deferred**. An adopter asking "if my finding cites OWASP LLM05, does that confer coverage on CWE-1426?" sees Gap on CWE-1426 in F-B output even though the crosswalk primary edge exists. Mitigated by the FR-017 scope line (documented) and by the planned F-C follow-on.
- **Out-of-Scope items render as Gap**. Adopters whose architectures don't exercise certain framework items (e.g., LLM03 Training Data Poisoning on a non-training architecture) see those items classified as Gap. Mitigated by the Q6-D deferral rationale (Decision 5) and by the per-item finding-citation list that allows adopters to visually distinguish inapplicable Gaps from applicable-but-uncovered Gaps.
- **Aggregator I/O cost at report generation**. F-B's aggregator reads 5 YAML files at extraction time per report generation. Aggregate cost is sub-100ms per F-A1 SC-013 bound; negligible relative to the multi-minute threat-model generation, but non-zero. Mitigated by per-invocation local-dict caching within a single aggregate call.
- **New Typst template surface**. `coverage-attestation.typ` is a new template file with its own rendering logic, adding to the Typst template surface area tachi maintains. Any future change to the coverage-page layout requires Typst-language familiarity. Mitigated by mirroring the established Feature 141 `attack-chain.typ` shape.

### Neutral

- **Q5 visual treatment is pending**. The color and icon treatment for Covered / Partial / Gap cells (FR-010) is governed by a ux-ui-designer memo expected Day 2 AM, with the architect-authored fallback at `specs/194-coverage-attestation-report-section/q5-visual-treatment-architect-fallback.md` pre-approved to activate if the memo slips. The Decision 7 Partial disclosure rule governs headline typography and is independent of the Q5 per-cell visual treatment; both conventions must satisfy WCAG AA color-blind accessibility.
- **Renderer + aggregator over an F-A3-less codebase**. F-B's acceptance test suite exercises the renderer on fixture-authored attribution payloads (not on real F-A3-populated findings), because F-A3 has not shipped. This is a deliberate scope-ordering choice — F-B is the consumer-side bridge that is ready the moment F-A3 ships, not a feature that blocks on F-A3.
- **Adopter UX will evolve**. The 3-value classification (Decision 2) and the 5-framework scope (Decision 3) are MVP choices reviewable as adopter demand accumulates. Future ADRs may extend the classification to 4 values (Decision 5 deferral) or extend the framework scope to include future external frameworks (Decision 3 forward compatibility). Neither extension requires F-B redesign — both fit additive to the Typst template + aggregator + boolean pattern.

---

## Governance Protocol (Proposed → Accepted dual-commit)

This ADR is authored in **Status: Proposed** at Day 1 Wave 1.0 of the F-B implementation (2026-04-18). The Proposed commit serves as the decision-lock point that unblocks parallel authoring in Wave 2.0 and beyond — the Typst template (`coverage-attestation.typ`), the aggregator function in `extract-report-data.py`, the fixture authoring, and the test suite can all begin once the seven decisions above are resolved in this ADR's Proposed commit.

**Protocol** (mirrors ADR-027 Decision 8 / ADR-028 Decision 7):
- **Day 1 Wave 1.0 (2026-04-18)** — ADR authored with `Status: Proposed`, `Accepted-commit-SHA: <pending-post-merge-fill>`. This commit lands on the feature branch and is the decision-lock signal. All 7 Decision sections are fully populated at Proposed time; no Decision field is deferred to Accepted.
- **Day 3 Wave 6.1 (pre-merge)** — ADR transitions to `Status: Accepted` with provisional date. The `<pending-post-merge-fill>` placeholder remains.
- **Post-merge SHA fill** — the `<pending-post-merge-fill>` placeholder is replaced with the actual squash-merge commit SHA. Per Feature 180 / Feature 189 precedent, the provisional Accepted-date is NOT retroactively corrected if merge slips.

**Prior art**: this protocol mirrors ADR-027 Decision 8 (F-A1), ADR-028 Decision 7 (F-A2 — direct predecessor), and the earlier ADR-024 / ADR-025 dual-commit precedent. The dual-commit pattern has three concrete benefits: (1) the Day 1 Proposed commit is an authoritative decision-lock point that unblocks parallel work without waiting for PR merge, (2) the Accepted commit at merge captures the final decision record with the specific decisions ratified, and (3) the post-merge SHA fill completes the provenance chain.

---

## Related Decisions

- [ADR-021](ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md): SOURCE_DATE_EPOCH determinism. F-B's aggregator preserves ADR-021 by construction: pure-function evaluation, per-invocation local-dict cache only, no HTTP/timestamps/env reads beyond what Typst already consumes. The SC-2 byte-identity gate at `tests/scripts/test_backward_compatibility.py` is reused unmodified; no new determinism knobs introduced.
- [ADR-022](ADR-022-mmdc-hard-prerequisite.md): CLI fail-loud precedent. F-B introduces no new CLI prerequisite (Typst is already present per Features 112 / 128). ADR-022's fail-loud pattern applies only when F-B's aggregator hits a missing-dependency condition at runtime — which is explicitly out of scope for F-B (no new dependencies per FR-016).
- [ADR-023](ADR-023-threat-agent-skill-references-pattern.md): 22-file zero-edit invariant on the 11 threat-detection agents plus their 11 companion skill-reference files. F-B preserves this invariant by construction — the feature is Typst template + aggregator + main-template include, with no acceptance criterion requiring detection-agent edits. F-A3 is the feature that may reopen the 22-file scope.
- [ADR-026](ADR-026-pattern-classification-mechanism.md): minor-bump rule for schema evolution. F-B does NOT bump any schema (FR-015 zero-schema-change), so ADR-026 does not apply directly. F-B's MVP classification scheme (3-value Covered / Partial / Gap per Decision 2) is a renderer-tier concept, not a schema-tier concept — future extensions (e.g., 4-value per Decision 5 deferral) would be renderer-tier evolutions and would not trigger ADR-026 schema-bump governance.
- [ADR-027](ADR-027-taxonomy-crosswalk-schema.md): F-A1 taxonomy schema. F-B reads F-A1 catalogs at extraction time to compute denominators (Decision 3). F-B does NOT consult `crosswalk.yaml` (Decision 4). F-A1 remains the authoritative source of framework IDs and counts; F-B consumes the read-only contract.
- [ADR-028](ADR-028-source-attribution-schema-extension.md): F-A2 source_attribution contract — direct predecessor. F-B consumes F-A2's `source_attribution` field via the existing parser round-trip at `scripts/tachi_parsers.py:621` with the F-A2-extended conditional-key emission. F-B's 5-framework scope (Decision 3) mirrors ADR-028 Decision 3's 5-value `taxonomy` enum exactly. F-B's 22-file zero-edit invariant preservation (Decision 6) mirrors ADR-028 Decision 6 exactly. This ADR's dual-commit governance (above) mirrors ADR-028 Decision 7 exactly.

---

## Future Work

- **F-A3 populator feature** (not yet filed as a PRD). Wires threat-detection agents to emit `source_attribution` values during detection. Touches the 22-file detection tier (may edit, per ADR-023 / ADR-028 / ADR-029 lineage). Unblocks F-B on real-world adopter architectures.
- **F-C crosswalk-JOIN follow-on feature** (not yet filed as a PRD). Consumes `crosswalk.yaml` to produce cross-framework inferred coverage alongside F-B's direct-attribution coverage. Requires architect decision on inferred-coverage confidence propagation rules. Independent of F-A3 population status — can iterate on fixture-authored attribution payloads after F-B ships.
- **F-D Out-of-Scope classification follow-on feature** (not yet filed as a PRD). Introduces a 4th adopter-visible classification distinguishing architecturally-inapplicable items from applicable-but-uncovered items. Requires a scoping mechanism decision (F-A1 YAML extensions, per-threat-model annotation, or LLM judgment). Blocked on adopter demand visibility; Q6-D deferral rationale in Decision 5 above.
- **Q5 visual treatment memo integration**. If the ux-ui-designer memo lands Day 2 AM, it supersedes the architect-authored fallback at `specs/194-coverage-attestation-report-section/q5-visual-treatment-architect-fallback.md`. If the memo slips, the architect fallback activates per spec FR-010 and SC-008.
- **Coverage attestation schema formalization** (possible future ADR). F-B emits per-framework coverage data as a structured dict into the Typst data variables at extraction time. If ecosystem integrators request a machine-readable coverage-attestation artifact (analogous to SARIF for findings), a future feature may formalize the coverage data as a published schema under `schemas/coverage-attestation.yaml`. Not in F-B scope; demand-gated.

---

## References

- Spec: [`specs/194-coverage-attestation-report-section/spec.md`](../../../specs/194-coverage-attestation-report-section/spec.md) — FR-001 through FR-019, SC-001 through SC-012, US-1/US-2/US-3
- Plan: [`specs/194-coverage-attestation-report-section/plan.md`](../../../specs/194-coverage-attestation-report-section/plan.md) — components, data flow, delivery milestones
- Tasks: [`specs/194-coverage-attestation-report-section/tasks.md`](../../../specs/194-coverage-attestation-report-section/tasks.md) — triple sign-off APPROVED
- Q5 architect fallback: [`specs/194-coverage-attestation-report-section/q5-visual-treatment-architect-fallback.md`](../../../specs/194-coverage-attestation-report-section/q5-visual-treatment-architect-fallback.md)
- PRD: [`docs/product/02_PRD/194-coverage-attestation-report-section-2026-04-18.md`](../../product/02_PRD/194-coverage-attestation-report-section-2026-04-18.md)
- F-A1 PRD: [`docs/product/02_PRD/180-taxonomy-crosswalk-collection-2026-04-17.md`](../../product/02_PRD/180-taxonomy-crosswalk-collection-2026-04-17.md)
- F-A2 PRD (direct predecessor): [`docs/product/02_PRD/189-source-attribution-schema-extension-2026-04-17.md`](../../product/02_PRD/189-source-attribution-schema-extension-2026-04-17.md)
- Typst main template: [`templates/tachi/security-report/main.typ`](../../../templates/tachi/security-report/main.typ) — conditional-section include site; Feature 141 `has-attack-chains` precedent at line 246
- Aggregator target: [`scripts/extract-report-data.py`](../../../scripts/extract-report-data.py) — Feature 128 `detect_images()` boolean precedent at line 1362
- F-A1 catalog YAMLs (read-only at extraction time): [`schemas/taxonomy/owasp.yaml`](../../../schemas/taxonomy/owasp.yaml), [`mitre-attack.yaml`](../../../schemas/taxonomy/mitre-attack.yaml), [`mitre-atlas.yaml`](../../../schemas/taxonomy/mitre-atlas.yaml), [`nist-ai-rmf.yaml`](../../../schemas/taxonomy/nist-ai-rmf.yaml), [`cwe.yaml`](../../../schemas/taxonomy/cwe.yaml) — 5 external-framework catalogs whose top-level `id` counts are the Decision 3 denominators
- F-A2 parser round-trip: [`scripts/tachi_parsers.py`](../../../scripts/tachi_parsers.py) — `parse_threats_findings` at line 621 with F-A2-extended `source_attribution` conditional-key emission
- Backward-compat harness: [`tests/scripts/test_backward_compatibility.py`](../../../tests/scripts/test_backward_compatibility.py) — SC-002 gate under `SOURCE_DATE_EPOCH=1700000000`
- Feature 141 precedent (conditional-section gating): [`docs/product/02_PRD/141-maestro-cross-layer-attack-chains-2026-04-12.md`](../../product/02_PRD/141-maestro-cross-layer-attack-chains-2026-04-12.md) — `has-attack-chains` boolean is the direct architectural precedent for F-B's `has-source-attribution` boolean
- Feature 128 precedent (Typst template + boolean gate): [`docs/product/02_PRD/128-executive-threat-architecture-infographic-2026-01-12.md`](../../product/02_PRD/128-executive-threat-architecture-infographic-2026-01-12.md) — Typst-template + `extract-report-data.py` boolean pattern

---

## Revision History

**2026-04-18 (Proposed — Feature 194, Day 1 Wave 1.0 decision-lock commit)**: Records the F-B Coverage Attestation Report Section decisions. Documents 7 numbered decisions covering the Typst-template + aggregator + `has-source-attribution` boolean pattern mirroring Feature 141 / Feature 128 precedent (Decision 1), the Q1-A 3-value Covered / Partial / Gap classification rule (Decision 2), the Q2-A catalog-length denominator authority restricted to 5 external frameworks (Decision 3), the FR-017 zero-crosswalk-JOIN scope boundary (Decision 4), the Q6-D Out-of-Scope deferral collapsing non-cited items into Gap in MVP (Decision 5), the SC-009 22-file zero-edit invariant preservation per ADR-023 / ADR-028 lineage (Decision 6), and the R9/MED-3 Partial disclosure rule requiring equal visual weight on all three counts in the per-framework headline (Decision 7). Authored at Day 1 Wave 1.0 as the decision-lock signal unblocking parallel Wave 2.0 authoring of the Typst template, the aggregator function, the fixtures, and the test suite. Status transitions to Accepted at Day 3 Wave 6.1 pre-merge; `<pending-post-merge-fill>` placeholder on the `Accepted-commit-SHA` field will be replaced at post-merge task with the squash-merge commit SHA per the Governance Protocol section above.

**2026-04-23 (Accepted — Feature 194, Wave 4.2 pre-merge transition T043)**: Transitioned ADR-029 from `Status: Proposed` to `Status: Accepted`. All 7 numbered decisions land as specified at Proposed time; no decision text is amended at Accepted. Implementation waves 1-4.1 verified green: Typst template `coverage-attestation.typ` landed, aggregator `aggregate_coverage_attestation()` + `compute_has_source_attribution()` landed in `scripts/extract-report-data.py`, `main.typ` integration landed (T012 + T013 + T014), SC-002 byte-identity harness green on all 6 baselines (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice, maestro-reference) under `SOURCE_DATE_EPOCH=1700000000`, and 22-file zero-edit invariant preserved (ADR-023 / ADR-028 sibling governance). **T012 guard-pattern selection note**: the default-value guards added to `main.typ` §2b use the `dictionary(report-data-module).at("name", default: ...)` idiom after binding `#import "report-data.typ" as report-data-module`, rather than the `if X != none { X } else { default }` idiom the ADR body did not explicitly prescribe — the `at(..., default: ...)` pattern was required to handle the absent-from-data-file case mandated by data-contract.md §Backward Compatibility, which the `!= none` idiom alone cannot cover because Typst's `#import ... : *` star-import does not bind absent names. No Decision text amendment needed; the guard-pattern selection is a Typst-specific implementation detail and does not affect the 7 numbered Decisions. Accepted-date 2026-04-23 is provisional pending PR merge; `<pending-post-merge-fill>` placeholder on `Accepted-commit-SHA` will be replaced by the squash-merge commit SHA at post-merge task T044 per Decision 7 dual-commit governance protocol and F-A1 / F-A2 (ADR-027 T039 / ADR-028 T036) precedent.
