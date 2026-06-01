---
prd:
  number: 302
  topic: asset-tag-output-wiring
  created: 2026-05-30
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-05-30, status: APPROVED_WITH_CONCERNS, notes: "0 BLOCKING / 1 HIGH / 4 MEDIUM / 3 LOW. Sign-off focus = community-credit accuracy + scope discipline, both PASS. H-1 (ADR-026 mis-titled Complex-Shape Addition Clarifier, recurred 5x) RESOLVED INLINE — re-cited to ADR-026 (Agentic Pattern Classification Mechanism, minor-bump rule) + ADR-028 (additive-field precedent) + ADR-037 (populator precedent) across Proposed Solution, FR-1, Q2, Dependencies, Governance Notes. M-1 (attribution wording — must read prototype authored by @north-echo, NEVER surfaced by; @armorer-labs form would under-credit a PR author) RESOLVED INLINE in FR-11. M-2 (#260 close comment must link F-260b PR + credit @north-echo, completing Discussion #246 to PR #262 to #260 to #302 chain) RESOLVED INLINE in FR-12. M-3 (Q4/Q5 are PM-owned) RESOLVED INLINE — section retitled Architect/PM-Owned, Q4 + Q5 marked PM-RESOLVED. M-4 (durable cadence carve-out cite) RESOLVED INLINE in FR-10 pointing at Issue #296 close comment. PM DECISIONS recorded: Q4 = all tags on target component (asset exposure, not modifier deltas; source-of-truth aligned); Q5 = CHANGELOG + Discussion #246 acknowledgment + offered Co-Authored-By, LinkedIn deferred to BLP-04 F-3+ (code-voice discipline). @north-echo correctly framed as PROTOTYPE AUTHOR throughout (US-3/FR-11/NFR-4/R5); declined-follow-on noted; credit is recognition not assignment. All 5 personas from Issue #302 covered; US-5 release-cadence story is additive not scope creep. Frozen constraints held out cleanly (SC-11 binary diff gate). LOWs (26-case parenthetical, SC-3 wording, new-file wording) folded. Full review .aod/results/product-manager.md."}
  architect_signoff: {agent: architect, date: 2026-05-30, status: APPROVED_WITH_CONCERNS, notes: "0 BLOCKING / 3 HIGH / 4 MEDIUM / 3 LOW. All factual claims verified accurate against current code (finding.yaml 1.8, risk-scoring.yaml 1.1 ceiling 9.2 + 6-tag enum, two SARIF emitters, parser at tachi_parsers.py:1472, risk-scorer is LLM model:sonnet, suite not in CI). All 3 HIGH RESOLVED INLINE: H-1/H-2 (F-189 source_attribution is the WRONG empty-default precedent — it omits-when-empty, opposite of FR-5 always-present []; re-anchored FR-1 + Q1 to the agentic_pattern / maestro_layer always-present-with-default precedent; F-189 reframed as a contrast in Dependencies; Q1 lean rewritten to always-present detail-block field Design A, gated Design B rejected). H-3 (populator placed in LLM risk-scorer threatens NFR-3 byte-equivalence) — FR-2 rewritten to deterministic serializer/script-tier population from parse_component_asset_map joined by component; LLM risk-scorer explicitly NOT the populator; NFR-3 now structurally guaranteed not test-dependent. M-1 (both emitters must source affected_assets from single emitted threats.md value via shared extractor, not re-derive) RESOLVED INLINE FR-4 + NFR-3. M-2 (pin literal snake_case affected_assets key in both emitters — codebase has pre-existing key-casing drift) RESOLVED INLINE FR-4 + SC-6. M-3 (output-contract docs must live outside risk-scoring.yaml to keep SC-11 diff clean) RESOLVED INLINE FR-7 + Q7. M-4 (finding.yaml field comment convention) RESOLVED INLINE FR-1. L-3 (all-6-tags + no-op-modifier-with-present-tag test) RESOLVED INLINE SC-3. Schema bump 1.8 to 1.9 (minor, ADR-026 rule, all 3 conditions hold) CONFIRMED correct; no new ADR (L-1; plan.md to add one sentence classifying populator as deterministic serializer-tier join not a synthesis phase). Frozen constraints (9.2 ceiling, 6-tag enum, modifier-after-clamp) held. Pre-Mortem (4 failure modes) + Systems Thinking lenses applied. All 5 plan.md APPROVE conditions now pre-satisfied in PRD text. Full review .aod/results/architect.md."}
  techlead_signoff: {agent: team-lead, date: 2026-05-30, status: APPROVED_WITH_CONCERNS, notes: "0 BLOCKING / 0 HIGH / 2 MEDIUM / 3 LOW. Constraint Analysis + Systems Thinking lenses. CALENDAR PASS — independent cal 5/6 2026 verification of all 8 timeline dates; zero weekend-placement defects (#292 lesson actively designed out): Day 0 Sat 2026-05-30 = /aod.define live now (allowed); Sun 05-31 correctly marked weekend no-work; all five build/work days 06-01 Mon through 06-05 Fri fall weekday; hard ceiling 06-11 Thu. EFFORT ~1-2 days REALISTIC (not optimistic) — verified both SARIF emitters import a shared sarif_common module (mitigates two-path drift), risk-scorer §3.5:288 already does the component to component_asset_map fuzzy-match so populator is a 1-2 line provenance capture at an existing site, F-189 additive-optional precedent proven, CI edit is 2-line lock-step; longest single task = FR-4 two-emitter SARIF + SC-6 cross-format gate (correctly placed Day 3 AM). CAPACITY CLEAR — 0 open PRs project-wide, 0 active remote feature branches, F-1 #296 verified CLOSED 2026-05-30 16:02 UTC (gate satisfied); senior-backend-engineer + tester assignment appropriate. 26-case claim VERIFIED accurate via pytest --collect-only (23 def + 1 parametrize expanding to 4 = 26). M-2 (no explicit multi-finding cross-emitter dedup/sort assertion — R2 partial-divergence mode) RESOLVED INLINE — SC-6 verify upgraded to a multi-finding per-finding equality table across threats.md + both emitters incl untagged [] findings. M-1 (slack miscount) RESOLVED INLINE — corrected to 6 working days from target. L-1 (#260 close at FR-12 correct), L-2 (26-case provenance logged), L-3 (Day 3 PM deliver slips to Buffer-1 if SC-6 finds divergence — orchestrator awareness). Buffers sufficient-to-generous. Cleared for /aod.plan. Full review .aod/results/team-lead.md."}
source:
  idea_id: 302
  story_id: null
---

# F-2 (F-260b) — Asset-Tag Output Wiring (BLP-04 Wave 2): Product Requirements Document

**Status**: Approved (HIGH/MEDIUM concerns folded inline; residual LOW/plan-time items → `/aod.plan`)
**Created**: 2026-05-30
**Spec**: TBD (will land at `specs/302-asset-tag-output-wiring/spec.md` after `/aod.plan`)
**Author**: product-manager
**Reviewers**: architect, team-lead
**Phase**: BLP-04 Adoption Push, Wave 2 (Community-Credit Follow-Up)
**Priority**: P1
**Parent Initiative**: BLP-04 Adoption Push (4-feature initiative; F-1 #296 CLOSED 2026-05-30)
**Source**: Seed Issue [#302](https://github.com/davidmatousek/tachi/issues/302) (captured 2026-05-30; pre-vetted in the BLP-04 blueprint Wave-2 planning)
**Lineage**: Follow-on to Issue [#260](https://github.com/davidmatousek/tachi/issues/260) / PR [#262](https://github.com/davidmatousek/tachi/pull/262) (@north-echo, merged v4.31.0 2026-05-06); references Discussion [#246](https://github.com/davidmatousek/tachi/discussions/246)
**ICE**: 22 (Impact 8, Confidence 7, Effort 7)

---

## 📋 Executive Summary

### The One-Liner

Wire @north-echo's community-merged asset-sensitivity tags (PR #262, v4.31.0) **end-to-end through the output stack** — `finding.yaml` schema field, risk-scorer populator, `threats.md` serialization, and SARIF emission — so that tags an adopter sets in their architecture description **actually propagate into machine-readable output** instead of remaining latent CVSS-only modifiers, and credit the contributor publicly per the established community-attribution precedent.

### Problem Statement

In v4.31.0 (2026-05-06), the community accepted @north-echo's PR #262: optional inline `[asset:tag1,tag2]` tags on architecture-description components that act as **CVSS impact-bit floors** during risk-scoring (e.g., a `pii` tag forces `C:H`). The prototype is real and tested — but it is **half-integrated**:

- The Mermaid parser extracts tags into a `component_asset_map` ([scripts/tachi_parsers.py:1472](../../../scripts/tachi_parsers.py#L1472)) ✓
- The risk-scorer **consumes** the map to elevate CVSS impact bits (Section 3.5, ceiling 9.2) ✓
- But **nothing emits which assets a finding touches**. The risk-scorer modifies the score and discards the tag provenance. There is **no `affected_assets[]` field** in [`schemas/finding.yaml`](../../../schemas/finding.yaml) (still v1.8), **no `affected_assets:` block** in `threats.md`, and **no `affected_assets` property** in either SARIF emitter ([generate-threats-sarif.py:444](../../../scripts/generate-threats-sarif.py#L444), generate-risk-scores-sarif.py).

The consequence: **an adopter who sets asset tags sees a slightly different number, but cannot see the tags anywhere in the output.** Downstream consumers (GitHub Code Scanning, SAST aggregators, the risk-scorer's own machine-readable surface) get no structured asset signal — exactly the signal those tools want consumed rather than re-derived, per tachi's source-of-truth positioning.

Two compounding costs:

1. **Credibility liability.** Half-integrated community work reads as "merged and forgotten." The first non-trivial community contribution to tachi deserves to be *coherent end-to-end* before "asset-aware risk scoring" is described anywhere public. Right now the claim would be aspirational, not provable.
2. **Discovery barrier.** "Asset-aware" is a differentiated positioning angle (it closes the asset-value gap in the 4-dimension composite). It cannot be marketed until the output proves it — and BLP-04 is an adoption initiative whose later waves (F-3 signal capture, F-4 MAESTRO announcement) benefit from a complete, demonstrable asset-tag story.

F-1 (#296, the 50/50 OWASP coverage distribution launch) **CLOSED 2026-05-30** and shipped `docs:`-only, deliberately breaking the release cadence. F-260b is the `feat:`-eligible follow-up that **restores the release cadence** (per the F-1 NFR-5 mitigation: F-2 ships `feat:` within ~1 week of F-1 close).

### Proposed Solution

A single feature branch wiring the **four missing output surfaces**, plus the schema field they depend on, plus CI protection for the existing-but-unwired test suite, plus a community-credit moment:

1. **Schema field** ([`schemas/finding.yaml`](../../../schemas/finding.yaml)): add an **optional, always-present-with-default** `affected_assets[]` field (array of the 6 frozen tag-enum strings; default `[]`), modeled on the `agentic_pattern` / `maestro_layer` always-present-with-default precedent — **NOT** the F-189 `source_attribution` conditional-absent pattern (whose omit-when-empty semantics are incompatible with FR-5). Bump `schema_version` 1.8 → 1.9 per the minor-bump rule in **ADR-026 (Agentic Pattern Classification Mechanism)**, extended for additive-optional finding fields in **ADR-028 (Source Attribution Schema Extension, F-189)** and **ADR-037 (populator wiring, F-241)**.

2. **Deterministic populator** ([`parse_component_asset_map()`](../../../scripts/tachi_parsers.py#L1472) → serializer/script tier): the `affected_assets[]` value is produced **deterministically** by joining `parse_component_asset_map()` output to each finding by target component, **in the serializer/script layer** — **NOT** authored by the LLM risk-scorer agent (an LLM cannot guarantee the byte-determinism NFR-3 requires; this mirrors how `maestro_layer`/`agentic_pattern` reach output via deterministic joins, not LLM authorship). This is the "populator" — the bridge between the (already-built) parser and the (new) output fields. The risk-scorer's §3.5 CVSS modifier pass and the 9.2 ceiling are **unchanged and frozen**; it gains no output-authoring role.

3. **`threats.md` serialization** ([finding-format-shared.md](../../../.claude/skills/tachi-shared/references/finding-format-shared.md), [threats.md template](../../../templates/tachi/output-schemas/threats.md)): emit a per-finding `affected_assets:` field so the human-readable and structured surface both carry the tags.

4. **SARIF emission** ([generate-threats-sarif.py](../../../scripts/generate-threats-sarif.py), generate-risk-scores-sarif.py, [sarif-specification.md](../../../.claude/skills/tachi-orchestration/references/sarif-specification.md)): both emitters add an `affected_assets` entry (literal snake_case key) to each result's `properties` bag (result-level SARIF extension), **sourced from the single emitted `threats.md` value** (a verbatim copy, not an independent re-derivation) so GitHub Code Scanning and downstream aggregators see tag-weighted findings and the two emitters cannot drift.

5. **Schema documentation**: a schema-doc surface (new section or doc extension, location per Q7) accurately describing the emitted `affected_assets[]` shape across IR / `threats.md` / SARIF, so the contract is discoverable.

6. **CI wiring** ([.github/workflows/tachi-pytest.yml](../../../.github/workflows/tachi-pytest.yml)): add the existing 26-case `tests/scripts/test_asset_sensitivity_tags.py` suite to the path filter + pytest invocation. Today the suite exists and passes locally but is **not run in CI** — a regression hole.

7. **Community credit**: an attribution moment for @north-echo following the F-292 / @armorer-labs precedent (CHANGELOG attribution + offered `Co-Authored-By` trailer + a public acknowledgment), with Discussion #246 referenced. URL recorded in Issue #302.

**Backward-compatibility spine**: when an architecture description has **no** tags, `affected_assets:` is an **empty array (present, not omitted)** in every format — `affected_assets: []` in `threats.md`, `"affected_assets": []` in SARIF. This preserves schema stability and byte-deterministic baselines (ADR-021, `SOURCE_DATE_EPOCH`).

### Scope

**In Scope (this feature)**:
- `schemas/finding.yaml` optional `affected_assets[]` field + `schema_version` 1.8 → 1.9 bump
- Risk-scorer populator wiring (records applied/present tags on findings) — agent §3.5 + asset-modifiers reference, no modifier-logic change
- `threats.md` per-finding `affected_assets:` serialization — `finding-format-shared.md` + template
- SARIF `affected_assets` property emission in **both** `generate-threats-sarif.py` and `generate-risk-scores-sarif.py` + `sarif-specification.md` reference update
- Schema-doc surface (new section or doc extension, location per Q7) describing the `affected_assets[]` contract across the three output formats
- CI: add `test_asset_sensitivity_tags.py` to `tachi-pytest.yml` (paths filter + pytest invocation)
- Regression Protection Plan tests (schema-stability, tag-propagation, ceiling, empty-default, cross-format consistency, schema-doc accuracy)
- `CHANGELOG.md` `feat(302):` entry (restores release cadence after F-1 docs-only close)
- Community-credit announcement for @north-echo; Discussion #246 referenced; URL recorded in Issue #302
- Issue #302 closed with deliverable + credit URLs

**Out of Scope (deferred / belongs elsewhere)**:
- **New tag-enum entries.** The enum is FROZEN at 6 (`pii | phi | auth | secrets | financial | safety`) per PR #262. Adding a tag is a separate change requiring its own ADR + community process.
- **Modifier-ceiling or ordering changes.** Ceiling FROZEN at 9.2; modifier-after-clamp ordering FROZEN. F-260b is wiring, not re-tuning. Any change here is a hard scope violation.
- **CVSS modifier-logic changes.** The Section 3.5 impact-bit floor logic is unchanged.
- **Asset-tag variants for additional examples** beyond the existing `examples/agentic-app/architecture-with-asset-tags.md` — example expansion is a follow-on (see Q6).
- **Custom/extensible tag vocabularies** (sidecar `assets.yaml`, user-defined tags) — rejected in the #260 discussion; out of scope.
- **Heavy long-form distribution** (a standalone ~3000-word article like F-1). F-260b's community-credit is a focused acknowledgment, not a distribution campaign; broader asset-tag distribution belongs to BLP-04 F-3+ (see Q5).

**Deferred (may be follow-on)**:
- `schema_version` 1.2 bump for `risk-scoring.yaml` (the `asset_modifiers` sibling table is already at 1.1; a future cumulative shape change triggers 1.2 — not this feature).
- Asset-tag coverage in non-agentic example architectures (web-app, microservices).
- Surfacing `affected_assets[]` in the PDF security report / infographics (downstream report consumers; separate report-assembly feature).

---

## 🎯 User Stories

**US-1 (Tag-setting adopter, SARIF propagation anchor)**:
> **When** I'm a tachi adopter who set asset-sensitivity tags in my architecture description, **I want** the tags to propagate into SARIF output, **so that** GitHub Code Scanning and my SAST aggregator show tag-weighted, asset-aware findings.

**Acceptance**: Running `tachi.threat-model` (or `tachi.risk-score`) on an architecture description containing `[asset:...]` tags produces SARIF where each affected result carries an `affected_assets` property listing the applicable tag strings. A finding on a `[asset:pii,phi]` component shows `"affected_assets": ["phi", "pii"]` (sorted) in its `result.properties`. A finding on an untagged component shows `"affected_assets": []`.

**US-2 (Risk-scorer / structured-data consumer, threats.md anchor)**:
> **When** I'm a downstream tool or analyst reading `threats.md`, **I want** `affected_assets[]` populated per finding, **so that** I can read structured asset-impact data without re-parsing the architecture description.

**Acceptance**: `threats.md` per-finding output includes an `affected_assets:` field (array of tag enum strings). For an architecture with tags, the field is populated on findings whose target component carries tags; for an architecture without tags, the field is present as an empty array on every finding. The `threats.md` value is byte-equivalent to the SARIF `affected_assets` for the same finding (US-1 cross-format consistency).

**US-3 (@north-echo, contributor-recognition anchor)**:
> **When** I'm @north-echo, author of the merged PR #262 asset-tag prototype, **I want** my contribution wired through the full output stack and credited, **so that** the feature is actually useful to downstream adopters and my contribution chain is preserved publicly.

**Acceptance**: The asset-tag feature is end-to-end functional (US-1 + US-2 pass). A community-credit artifact (CHANGELOG attribution + a public acknowledgment per the F-292 / @armorer-labs precedent, with an offered `Co-Authored-By` trailer) credits @north-echo for PR #262 and references Discussion #246. The acknowledgment URL is recorded in Issue #302. Framing is accurate: @north-echo authored the *prototype*; F-260b is the *maintainer-side wiring* of that prototype.

**US-4 (Maintainer, end-to-end coherence anchor)**:
> **When** I'm the tachi maintainer preparing any public reference to "asset-aware risk scoring", **I want** the asset-tag feature coherent end-to-end before that reference exists, **so that** the capability is provable, not aspirational.

**Acceptance**: An adopter-facing reproducibility test holds — *any* architecture description with tags produces SARIF + `threats.md` output where the tags are visibly present, and the maintainer can point to a worked example (`examples/agentic-app/architecture-with-asset-tags.md`) whose output demonstrates propagation. The schema-doc surface accurately documents the emitted shape. No "asset-aware" claim outruns the wiring.

**US-5 (Release-cadence continuity anchor)**:
> **When** I'm an adopter tracking tachi releases who saw F-1 close `docs:`-only with no release PR, **I want** F-260b to ship `feat:`-eligible and trigger a release, **so that** the cadence (every shipped capability yields a release) is restored within ~1 week of the F-1 break.

**Acceptance**: F-260b's squash-merge uses a `feat(302):` PR title; release-please opens a release PR within ~30s post-merge (verified per project memory `feedback_aod_deliver_release_gate.md`). The CHANGELOG entry is `feat:`-prefixed.

---

## ✅ Functional Requirements

**FR-1 (finding.yaml schema field)**: [`schemas/finding.yaml`](../../../schemas/finding.yaml) MUST gain an **optional, always-present-with-default** `affected_assets` field: an array of strings constrained to the frozen 6-value tag enum (`pii | phi | auth | secrets | financial | safety`), default `[]`. The field MUST be additive and backward-compatible. `schema_version` MUST bump 1.8 → 1.9 per the minor-bump rule established in **ADR-026 (Agentic Pattern Classification Mechanism)** and extended for additive-optional finding fields in **ADR-028 (Source Attribution Schema Extension)**. The empty-default serialization MUST follow the **`agentic_pattern` / `maestro_layer` always-present-with-default precedent** (sentinel default always emitted), **NOT** the F-189 `source_attribution` conditional-absent precedent (omit-when-empty), which is incompatible with FR-5. The field's inline schema comment MUST follow the file's existing convention: `# Asset Sensitivity (v1.9 — Feature 260b / PR #262)` + ADR-026 minor-bump citation + always-present-default note + a cross-reference that the modifier logic lives frozen in `risk-scoring.yaml`.

**FR-2 (deterministic populator — serializer/script tier)**: The `affected_assets[]` value MUST be produced **deterministically** from [`parse_component_asset_map()`](../../../scripts/tachi_parsers.py#L1472) joined to each finding by target component (the same case-insensitive/fuzzy cascade the risk-scorer §3.5 modifier pass already uses). Population MUST happen in the **deterministic serializer/script layer** — the `threats.md` serializer joins by component; both SARIF emitters then read the emitted `threats.md` value. The **LLM risk-scorer agent MUST NOT author this field** (an LLM cannot guarantee the byte-determinism NFR-3 requires; cf. ADR-026 routing `agentic_pattern` through a deterministic rule table rather than LLM judgment). Output MUST be sorted, matching `parse_component_asset_map`'s sorted output. The CVSS impact-bit floor pass, the modifier-after-clamp ordering, and the 9.2 ceiling MUST remain **unchanged** — FR-2 adds deterministic provenance recording, not scoring behavior.

**FR-3 (threats.md serialization)**: Per-finding `threats.md` output MUST emit an `affected_assets:` field (array of tag enum strings). The serialization surface (per-finding YAML block vs inline) is resolved in `/aod.plan` (Q1); the chosen surface MUST be documented in [finding-format-shared.md](../../../.claude/skills/tachi-shared/references/finding-format-shared.md) and reflected in the [threats.md template](../../../templates/tachi/output-schemas/threats.md).

**FR-4 (SARIF emission)**: **Both** [`scripts/generate-threats-sarif.py`](../../../scripts/generate-threats-sarif.py) and `scripts/generate-risk-scores-sarif.py` MUST add an `affected_assets` entry to each result's `properties` bag (a SARIF result-level property: array of tag enum strings). The literal property key MUST be **`affected_assets`** (snake_case, byte-identical to the `threats.md` field and schema field name) in **both** emitters — do NOT replicate the pre-existing key-casing drift between the two scripts. Both emitters MUST **source the value from the single emitted `threats.md`** (a copy via a shared extractor, e.g. `parse_affected_assets(threats_content)`), NOT independently re-derive it from `component_asset_map`. The [sarif-specification.md](../../../.claude/skills/tachi-orchestration/references/sarif-specification.md) reference MUST document the property. The two emitters MUST produce identical `affected_assets` values for the same finding (NFR-3 cross-format consistency).

**FR-5 (backward-compatible empty default)**: When an architecture description carries no tags (or a finding's target component carries none), `affected_assets` MUST be present as an **empty array** (`[]`), NOT omitted, in every output format (IR, `threats.md`, SARIF). This preserves schema stability and the byte-deterministic baseline contract.

**FR-6 (frozen-constraint preservation)**: F-260b MUST NOT add tag-enum entries, MUST NOT change the 9.2 modifier ceiling, and MUST NOT change the modifier-after-clamp ordering. The `VALID_ASSET_TAGS` tuple and the `asset_modifiers` table remain frozen per PR #262. Any diff touching these is out of scope and MUST be reverted.

**FR-7 (schema documentation)**: A schema-doc surface (a new section or extension of an existing doc — location per Q7, default = extend [asset-modifiers.md](../../../.claude/skills/tachi-risk-scoring/references/asset-modifiers.md) + a [`schemas/README.md`](../../../schemas/README.md) pointer + the `finding.yaml` field comment per FR-1) MUST accurately describe the emitted `affected_assets[]` contract — its enum, its empty-default semantics, and its representation in IR / `threats.md` / SARIF. The output-contract documentation MUST NOT be added to `schemas/risk-scoring.yaml` (which stays byte-frozen for SC-11).

**FR-8 (CI wiring)**: [`.github/workflows/tachi-pytest.yml`](../../../.github/workflows/tachi-pytest.yml) MUST add `tests/scripts/test_asset_sensitivity_tags.py` (the existing 26-case suite — 23 test functions, 26 collected cases via parametrize) to both its `paths:` filter and its pytest invocation, plus any **new** F-260b tests (FR-9 / Success Criteria). The asset-tag parser + populator + emitter tests MUST run on PRs touching the relevant paths.

**FR-9 (regression protection)**: The Regression Protection Plan tests (see Success Criteria SC-1 … SC-7) MUST be implemented and pass: schema-stability byte-identity for no-tag baselines, per-tag propagation positive tests, ceiling-enforcement test (extended from PR #262), empty-default test, risk-scorer dry-run on `examples/agentic-app/architecture-with-asset-tags.md`, and cross-format (SARIF ↔ `threats.md`) consistency.

**FR-10 (release-cadence restoration)**: The feature MUST ship via a `feat(302):` PR title; `CHANGELOG.md` MUST gain a `feat:`-prefixed entry: `feat(302): wire asset-sensitivity tags through finding IR + threats.md + SARIF (F-260b)`. The maintainer MUST verify a release-please PR opens post-merge (≈30s SLO); if it does not, push a `feat(302):` release-marker per `feedback_aod_deliver_release_gate.md`. (The cadence carve-out — F-1 shipped `docs:`-only, F-2 restores `feat:` cadence — is recorded durably in the Issue #296 closing comment per the F-1 close-out.)

**FR-11 (community credit)**: A community-credit artifact MUST credit @north-echo for PR #262 following the F-292 / @armorer-labs precedent **for the *mechanism* only** (CHANGELOG attribution + offered `Co-Authored-By` + Discussion acknowledgment): (a) a `CHANGELOG.md` attribution line, (b) an offered `Co-Authored-By: ` trailer (per Constitution IX), (c) a public acknowledgment (Discussion comment and/or LinkedIn — surface resolved in Q5), and (d) a reference to Discussion #246. The attribution **wording** MUST reflect that @north-echo *authored merged PR #262* — "prototype authored/contributed by @north-echo (PR #262)", **NEVER** "surfaced by" (the @armorer-labs discussion-commenter form would under-credit a PR author). The acknowledgment URL MUST be recorded in the Issue #302 close comment.

**FR-12 (Issue close)**: Issue #302 MUST be closed with a comment citing: the feature PR, the release-please/release tag, and the community-credit URL. Parent Issue #260 MUST be transitioned to closed (it was held open pending this follow-on per the PR #262 squash-merge note "full close after the follow-on lands"); the **#260 close comment MUST link the F-260b feature PR and credit @north-echo**, completing the public contribution chain (Discussion #246 → PR #262 → #260 → #302).

---

## 🚧 Non-Functional Requirements

**NFR-1 (schema stability / byte-deterministic baselines)**: Adding `affected_assets[]` MUST NOT break the byte-deterministic baseline contract (ADR-021). Existing no-tag example baselines MUST regenerate byte-identically except for the additive `affected_assets: []` field, verified under `SOURCE_DATE_EPOCH=1700000000`. The field addition is additive and optional; no consumer that ignores it breaks.

**NFR-2 (no scoring regression)**: F-260b MUST NOT alter any finding's CVSS base, composite score, or severity band relative to the PR #262 behavior. The populator records tags; it does not re-score. Verified by the extended ceiling-enforcement test and a score-equivalence check against the v4.31.0 worked example.

**NFR-3 (cross-format consistency)**: For any single finding, the `affected_assets` value MUST be byte-equivalent across IR, `threats.md`, and both SARIF emitters (same tags, same sort order, same `affected_assets` key string). This is the single most important correctness invariant — divergence between formats is a defect. It MUST be guaranteed **structurally** (a single deterministic source — `parse_component_asset_map` → `threats.md` → copied into both SARIF property bags via one shared extractor per FR-2/FR-4), not merely test-checked.

**NFR-4 (community provenance preservation)**: @north-echo's authorship of PR #262 MUST be preserved and accurately framed (prototype author, not "requester"). The credit follows the documented external-contributor pattern (`feedback_external_contributor_collisions.md`): comment-first, give-choice, preserve authorship. Per project memory, @north-echo declined follow-on items in the post-merge thank-you thread — F-260b is maintainer-driven wiring; @north-echo is credited, not assigned.

**NFR-5 (frozen-constraint discipline)**: The 6-value enum, 9.2 ceiling, modifier-after-clamp ordering, and inline-only tag location are FROZEN per PR #262 and project memory `project_f260_asset_tags.md`. Any reviewer or implementer tempted to "improve" these MUST treat the temptation as out-of-scope. Changing a frozen constraint requires its own discovery → ADR → community cycle.

**NFR-6 (writing-voice vs code-voice separation)**: Per the BLP-04 §3 Sequencing Discipline established in F-1, F-260b is **code-voice** work. The community-credit artifact (FR-11) is a focused acknowledgment, not a distribution campaign — heavy long-form writing (article-scale) is deferred to BLP-04 F-3+ to avoid diluting the code-voice focus (Q5).

**NFR-7 (effort discipline / small surface)**: The wiring is mechanical once the schema field and serialization surface are decided. The estimate is ~1–2 focused working days. If implementation balloons (e.g., a reviewer reopens a frozen constraint, or the serialization surface requires template-engine changes), that is a signal to re-scope, not to expand silently.

---

## 🎯 Success Criteria

**SC-1 (schema field + version bump)**: `schemas/finding.yaml` contains the optional `affected_assets` enum-array field; `schema_version` is `1.9`.
- **Verify**: `grep -A3 affected_assets schemas/finding.yaml` shows the field with the 6-value enum; `grep schema_version schemas/finding.yaml` shows `1.9`.

**SC-2 (schema-stability byte-identity)**: No-tag example baselines regenerate byte-identically except the additive `affected_assets: []`.
- **Verify**: Regenerate a no-tag baseline under `SOURCE_DATE_EPOCH=1700000000`; `git diff` shows only added `affected_assets: []` lines (threats.md) / `"affected_assets": []` (SARIF), no other changes.

**SC-3 (per-tag propagation)**: Each of the 6 enum tags propagates correctly to IR, `threats.md`, and SARIF.
- **Verify**: Propagation tests MUST cover **all 6 enum tags** — 4 (`pii`, `phi`, `auth`, `safety`) via `examples/agentic-app/architecture-with-asset-tags.md`, and `secrets` + `financial` via unit fixtures. A **no-op-modifier-with-present-tag** case (e.g. `financial` on a finding already at `I:H`) MUST assert `affected_assets` still lists the tag even though the CVSS bit was unchanged (the Q4 semantic). Findings on tagged components show the expected sorted `affected_assets`.

**SC-4 (ceiling enforcement preserved)**: A finding with tags whose modified `cvss_base` would exceed 9.2 caps at 9.2.
- **Verify**: The PR #262 ceiling test (extended) passes; no finding exceeds 9.2; `affected_assets` is populated regardless of whether the ceiling clamped.

**SC-5 (empty-tag default)**: An architecture description with no tags produces `affected_assets: []` (present, not omitted) in all formats.
- **Verify**: Run on a no-tag example; `threats.md` and SARIF both show empty `affected_assets` on every finding.

**SC-6 (cross-format consistency)**: SARIF `affected_assets` and `threats.md` `affected_assets:` are byte-equivalent for **every** finding; both SARIF emitters agree; the property key string is byte-identical (`affected_assets`, snake_case) in both emitters.
- **Verify**: An automated **multi-finding** test runs the full worked example (≥2 differently-tagged components + ≥1 untagged) end-to-end and asserts a *per-finding* equality table across `threats.md`, `generate-threats-sarif.py`, and `generate-risk-scores-sarif.py` — **every** finding, including untagged `[]` ones — has byte-identical `affected_assets` (catches R2's partial-divergence mode, not just a single-finding spot check).

**SC-7 (schema-doc accuracy)**: The new schema-doc surface accurately describes the emitted shape.
- **Verify**: The schema-doc enum + empty-default semantics + per-format representation match the actual emitted output for the worked example.

**SC-8 (CI runs asset-tag tests)**: `tachi-pytest.yml` runs `test_asset_sensitivity_tags.py` + new F-260b tests.
- **Verify**: `grep test_asset_sensitivity_tags .github/workflows/tachi-pytest.yml` matches in both the paths filter and the pytest command; a CI run on the feature PR shows the suite executing.

**SC-9 (release cadence restored)**: A `feat(302):` squash-merge triggers a release-please PR.
- **Verify**: `gh pr list --state open --search "release-please"` shows a release PR within ~30s of merge; CHANGELOG entry uses `feat:`.

**SC-10 (community credit recorded)**: @north-echo credited; acknowledgment URL in Issue #302; Discussion #246 referenced.
- **Verify**: Issue #302 close comment contains the credit URL; CHANGELOG attribution line names @north-echo + PR #262; Discussion #246 cited.

**SC-11 (frozen constraints untouched)**: No diff to the tag enum, ceiling, or modifier ordering.
- **Verify**: `git diff main -- schemas/risk-scoring.yaml scripts/tachi_parsers.py` shows no change to `VALID_ASSET_TAGS`, `modifier_ceiling: 9.2`, or the modifier-after-clamp section (only additive populator/emitter changes elsewhere).

**SC-12 (Issues closed)**: Issue #302 closed with deliverable + credit URLs; parent Issue #260 closed.
- **Verify**: `gh issue view 302` and `gh issue view 260` both show `state=CLOSED`; #302 close comment cites PR + release + credit URLs.

---

## ❓ Open Questions (Architect/PM-Owned, Resolve in `/aod.plan`)

> **PM pre-resolved at sign-off**: Q4 (populator semantics) and Q5 (credit surface) are PM-owned and resolved in the PM review — see the inline decisions below. The architect owns only the *mechanical/determinism* aspects of Q4. Q1, Q2, Q3, Q6, Q7 remain architect-owned and deferrable.

**Q1 (threats.md serialization surface)**: How should `affected_assets:` appear per finding — an **always-present per-finding detail-block field**, a **new finding-table column**, or a **frontmatter aggregate**?
- **Lean**: **Always-present per-finding field in the finding *detail block*** (value `[]` when empty, `["phi","pii"]` when tagged), modeled on the `agentic_pattern` / `maestro_layer` always-present-with-default pattern — **NOT** a gated/conditional block (F-189 `source_attribution` omits-when-empty, which structurally cannot satisfy FR-5's "present on every finding"). Emitting in the per-finding **detail block** (not the summary STRIDE/AI table row) keeps table rows byte-stable AND satisfies FR-5. The one-time additive `affected_assets: []` baseline drift is exactly what R1/SC-2 plan for.
- **Decision criterion**: Architect's call on detail-block field shape. Default = always-present detail-block field (Design A). A gated block (Design B) is rejected — it violates FR-5/SC-5 and complicates NFR-3.

**Q2 (schema bump + ADR)**: `finding.yaml` 1.8 → 1.9 is governed by the ADR-026 minor-bump rule. Does the field addition warrant its **own ADR**, or is PR #262 + the existing ADR lineage + this PRD sufficient? (Issue #302 states "No new ADR — architectural decisions live in PR #262 + frozen constraints.")
- **Lean**: **No new ADR.** The substantive architecture decisions (enum, ceiling, ordering, inline location) were made in PR #262's review and are frozen; F-260b is mechanical wiring of an already-decided shape. **ADR-028** (Source Attribution Schema Extension, F-189) added an optional finding field under ADR-026's minor-bump rule *without* a per-field ADR; **ADR-037** (Web/API Coverage Attestation + Populator Wiring, F-241) wired populators with byte-identity baseline discipline likewise. F-260b is the same pattern (additive optional field + deterministic populator) and inherits those precedents. Cite ADR-026 (minor-bump rule) + ADR-028 (additive-field precedent) + ADR-037 (populator precedent) in the schema comment block; reference PR #262. **plan.md should add one sentence** classifying `affected_assets` population as a *deterministic serializer-tier join, not a new synthesis phase* (per Architect L-1) so a future reader does not misclassify it against the ADR-026 governance table.
- **Decision criterion**: Architect confirms the no-ADR call (concurred in review; binds to the Issue #302 governance note). A thin ADR is the fallback only if the architect later judges the IR-field addition record-worthy — default is no new ADR.

**Q3 (SARIF property shape)**: Should `properties.affected_assets` be a **flat array of tag strings** (`["phi","pii"]`) or a **structured object** (e.g., `{component, tags}`)?
- **Lean**: **Flat array of tag strings**, matching the `threats.md` shape exactly (NFR-3 cross-format consistency is trivial when both are the same flat array). The component is already identifiable from the SARIF location; nesting it inside the property is redundant.
- **Decision criterion**: Architect's call; default = flat array.

**Q4 (populator semantics: all tags vs effective tags) — PM-RESOLVED**: Should `affected_assets[]` record **all** tags on the target component, or **only** tags that actually elevated a CVSS impact bit? Example: a `financial` tag (forces `I:H`) on a finding already at `I:H` is a *no-op modifier* — but the asset is still present.
- **PM decision (resolved at sign-off)**: **All tags on the target component.** The field describes *asset exposure*, not *modifier deltas* — a PII store is PII-affected even when the category default already forced `C:H`. This is the source-of-truth-aligned answer (downstream consumers want to know *what a finding touches*) and the simpler, deterministic rule. **Mechanically** `affected_assets = component_asset_map.get(component, [])` verbatim — a pure deterministic lookup, no effective-modifier computation, decoupled from the §3.5 floor logic.
- **Architect owns**: sort order + dedup mechanics only (the semantic is PM-settled).

**Q5 (community-credit surface + timing) — PM-RESOLVED**: @north-echo credit — **Discussion comment + CHANGELOG only** (in-channel, code-voice), or also a **LinkedIn acknowledgment** (writing-voice)? And before, at, or after merge?
- **PM decision (resolved at sign-off)**: **CHANGELOG attribution + a Discussion #246 acknowledgment comment at/after merge + offered `Co-Authored-By` trailer; LinkedIn deferred to BLP-04 F-3+.** Per NFR-6, F-260b is code-voice; a heavy LinkedIn writing moment risks the F-1 voice-separation discipline. A focused Discussion acknowledgment is sufficient recognition and keeps the asset-tag distribution moment available for a later wave. @north-echo declined follow-on work (memory), so the credit is recognition, not a contribution ask.

**Q6 (example coverage)**: Add asset-tag variants to additional examples (web-app, microservices), or keep the single `examples/agentic-app/architecture-with-asset-tags.md`?
- **Lean**: **Keep the single example** for this feature. It already exercises 4 of the 6 tags across 4 components and is sufficient for the propagation tests. Broader example coverage is a clean follow-on and does not gate the wiring.
- **Decision criterion**: Team-Lead's call on test sufficiency. Default = single example; expansion is follow-on.

**Q7 (schema-doc location)**: Where does the `affected_assets[]` contract doc live — extend [`schemas/README.md`](../../../schemas/README.md), extend the [asset-modifiers reference](../../../.claude/skills/tachi-risk-scoring/references/asset-modifiers.md), or a new standalone doc?
- **Lean**: **Extend the existing `asset-modifiers.md` reference with an "Output Contract" section + a short `schemas/README.md` pointer.** Keeps the asset-tag knowledge co-located (parsing → modifier → output) rather than fragmenting it; avoids a new file with low surface area. No new standalone `docs/standards/` file unless the Architect prefers one for adopter discoverability.
- **Decision criterion**: Architect's call on co-location vs. discoverability. Default = extend asset-modifiers.md + schemas/README pointer + the `finding.yaml` field comment (FR-1). The contract doc MUST NOT live in `schemas/risk-scoring.yaml` — that file stays byte-frozen for SC-11.

---

## ⚠️ Risks & Mitigations

**R1 (baseline byte-drift)**: Adding `affected_assets: []` to existing findings changes the byte content of every example baseline, breaking the SC-003 byte-identity guarantee if not handled.
- **Likelihood**: HIGH (it touches every finding's serialization)
- **Impact**: MEDIUM (baseline tests fail loudly; not a silent regression)
- **Mitigation**: FR-5 mandates empty-array-present default; baselines are regenerated once under `SOURCE_DATE_EPOCH=1700000000` as part of the feature; SC-2 verifies the only diff is the additive field. This is the F-241 precedent (additive field → controlled baseline regeneration).

**R2 (two SARIF emitters drift)**: `generate-threats-sarif.py` and `generate-risk-scores-sarif.py` are separate scripts; wiring one and forgetting the other (or implementing them inconsistently) ships divergent output.
- **Likelihood**: MEDIUM (two code paths, easy to miss one)
- **Impact**: MEDIUM (cross-format inconsistency erodes the structured-data contract)
- **Mitigation**: FR-4 names both emitters explicitly; SC-6 + NFR-3 require an automated cross-emitter consistency test; prefer a shared property-construction helper if the two scripts already share one.

**R3 (scope creep into frozen logic)**: An implementer or reviewer "improves" the ceiling, enum, or ordering while in the neighborhood.
- **Likelihood**: MEDIUM (the modifier logic is right there; the temptation is real)
- **Impact**: HIGH (re-tuning a frozen, community-reviewed constraint without process erodes the contribution and the trust signal)
- **Mitigation**: FR-6 + NFR-5 declare the constraints FROZEN and out-of-scope; SC-11 is a binary diff check on `risk-scoring.yaml` + `tachi_parsers.py`; project memory `project_f260_asset_tags.md` documents the freeze rationale.

**R4 (schema-bump ripple)**: `finding.yaml` 1.8 → 1.9 may surface consumers that hard-validate the schema version or field set.
- **Likelihood**: LOW (the field is optional/additive; consumers ignoring unknown fields are unaffected)
- **Impact**: LOW (additive, backward-compatible by FR-1)
- **Mitigation**: Optional field + empty default; grep for `schema_version` consumers during `/aod.plan`; the F-189 + F-260-prototype precedents confirm additive fields are safe.

**R5 (community-credit misframing)**: The acknowledgment frames @north-echo inaccurately (e.g., "requester" instead of "prototype author") or assumes follow-on commitment they declined.
- **Likelihood**: LOW (precedent + memory are explicit)
- **Impact**: MEDIUM (eroded trust with a model first contributor)
- **Mitigation**: NFR-4 + `feedback_external_contributor_collisions.md` + `project_f260_asset_tags.md` (declined follow-on noted). Frame as "prototype author, maintainer wired the output stack"; offer `Co-Authored-By`; do not assign work.

**R6 (CI surfaces latent failures)**: Wiring `test_asset_sensitivity_tags.py` into CI for the first time could surface environment-specific failures the local runs masked.
- **Likelihood**: LOW (suite is stdlib-only, 26 cases passing locally)
- **Impact**: LOW (caught pre-merge on the feature PR itself)
- **Mitigation**: FR-8 adds the suite on the feature branch so CI exercises it before merge; the suite is PAT-014 stdlib-only (no external deps to drift).

**R7 (release-cadence skip repeats)**: A non-`feat:` PR title slips through and release-please skips the release (the F-212 incident).
- **Likelihood**: LOW (documented incident + two-step enforcement)
- **Impact**: MEDIUM (the cadence restoration is the explicit point of F-260b per F-1 NFR-5)
- **Mitigation**: FR-10 mandates `feat(302):` title; `/aod.deliver` pre-merge title check + post-merge release-please verification per `feedback_aod_deliver_release_gate.md` + git-workflow.md.

---

## 📅 Estimated Timeline

**Schedule policy**: Weekday-anchored cadence. F-260b is **code-voice** and **small-surface** (mechanical wiring once the schema field + serialization surface are decided). Working-day effort: ~1–2 focused days. Wall-clock target: 3 working days from `/aod.plan`; hard ceiling 2026-06-11 (Thu) per BLP-04 Wave-2 target. Today (2026-05-30) is a **Saturday** — the `/aod.define` step runs now; build work anchors to the following work week.

| Day | Date | Activity | Owner |
|---|---|---|---|
| Day 0 | 2026-05-30 (Sat) | `/aod.define` — this PRD; parallel Triad reviews. F-1 (#296) confirmed CLOSED 16:02 UTC → sequencing gate satisfied. | product-manager + architect + team-lead |
| — | 2026-05-31 (Sun) | Weekend | — |
| Day 1 | 2026-06-01 (Mon) | `/aod.plan` — spec.md + plan.md + tasks.md resolving Q1–Q7 (serialization surface, ADR call, SARIF shape, populator semantics, credit surface, example coverage, schema-doc location) | product-manager + architect + team-lead |
| Day 2 AM | 2026-06-02 (Tue) | `/aod.build` Wave 1 — `finding.yaml` field + 1.9 bump (FR-1); deterministic populator in serializer tier (FR-2); `threats.md` serializer (FR-3) | senior-backend-engineer |
| Day 2 PM | 2026-06-02 (Tue) | `/aod.build` Wave 2 — SARIF emission in both emitters (FR-4); schema doc (FR-7); CI wiring (FR-8) | senior-backend-engineer |
| Day 3 AM | 2026-06-03 (Wed) | `/aod.build` Wave 3 — Regression Protection tests (FR-9 / SC-1…SC-8); baseline regeneration under `SOURCE_DATE_EPOCH`; Security Scan (Step 7) | senior-backend-engineer + tester |
| Day 3 PM | 2026-06-03 (Wed) | `/aod.deliver` — PR ready → squash-merge `feat(302):`; release-please verify (FR-10); community-credit (FR-11); close Issue #302 + parent #260 (FR-12) | product-manager + maintainer |
| **Buffer-1** | 2026-06-04 (Thu) | Slip buffer — serialization-surface rework or cross-format-consistency test iteration | — |
| **Buffer-2** | 2026-06-05 (Fri) | Slip buffer — unforeseen schema-ripple or CI failure | — |
| **Hard ceiling** | 2026-06-11 (Thu) | BLP-04 Wave-2 target ship; escalate to user if unclosed | — |

**Total wall-clock**: 3 working days target (~1–2 focused days of effort). Hard ceiling 2026-06-11 (Thu) — 6 working days of slack from the 06-03 target (4 beyond the two named buffers).

**Critical path**:
1. Day 1 `/aod.plan` Q1 (serialization surface) + Q3 (SARIF shape) + Q4 (populator semantics) decisions unblock all wiring.
2. Day 2 wiring is parallel-safe across the four surfaces once the shape is fixed (schema field is the one true dependency — it lands first).
3. Day 3 cross-format-consistency test (SC-6) is the correctness gate; baseline regeneration (SC-2) is the byte-stability gate.

**F-3 kickoff gate**: BLP-04 F-3 (adoption signal capture) follows F-260b close; no F-3 work before #302 closes (mirrors the F-1 → F-2 sequencing discipline, though F-2 → F-3 is less voice-sensitive since both can be code-adjacent).

---

## 🔗 Dependencies

**Hard dependencies (satisfied)**:
- **PR #262 merged (@north-echo, v4.31.0, 2026-05-06)** — provides the parser, modifier table, modifier pass, worked example, and 26-case test suite that F-260b wires through to output. **MERGED ✓** (memory: `project_f260_asset_tags.md`).
- **F-1 (#296) CLOSED 2026-05-30** — the BLP-04 §3 sequencing gate; F-2 starts only after F-1 close. **CLOSED ✓** (16:02 UTC, verified).
- **ADR-026 (Agentic Pattern Classification Mechanism)** — its minor-bump rule governs the `finding.yaml` 1.8 → 1.9 bump; its `agentic_pattern` field is the always-present-with-default precedent for the empty-default semantic (FR-1/FR-5). **EXISTS ✓**.
- **ADR-028 (Source Attribution Schema Extension, F-189)** — precedent for adding an optional additive finding field under ADR-026's minor-bump rule without a per-field ADR (Q2). **SHIPPED ✓** (PRD #189). *Note: its `source_attribution` field is a **contrast** for empty-handling — it omits-when-empty, which F-260b deliberately does NOT do (FR-5 mandates always-present `[]`).*
- **ADR-037 (Web/API Coverage Attestation + Populator Wiring, F-241)** — the canonical populator-wiring + additive-field + byte-identity-baseline precedent (FR-2, NFR-1, SC-2). **SHIPPED ✓** (PRD #241).

**Soft dependencies (informational)**:
- **Discussion #246** (@north-echo's original "prioritization beyond severity buckets" request) — referenced in the community-credit (FR-11) and CHANGELOG; thematically pairs with F-260b.
- **BLP-04 strategy doc** — authored at F-1 close-out (per F-1 Q5); F-260b is its Wave 2; no blocking dependency.
- **F-3 (adoption signal capture)** — NOT YET STARTED; follows F-260b close; inherits the asset-aware story F-260b completes.

**Frozen constraints (inherited from PR #262 — non-negotiable, see NFR-5)**:
- Tag enum FROZEN at 6: `pii | phi | auth | secrets | financial | safety`
- Modifier ceiling FROZEN at 9.2 (NOT 9.5)
- Modifier-after-clamp ordering FROZEN
- Inline-only tag location (`Component["Name<br/>[asset:tag1,tag2]"]`); no sidecar `assets.yaml`

---

## 📌 Governance Notes

- **Type**: Feature (parallel Triad review: PM + Architect + Team-Lead).
- **ADR**: No new ADR by default (Q2, Architect-concurred) — architectural decisions live in PR #262 + frozen constraints; the ADR-026 minor-bump rule governs the schema bump, with ADR-028 (additive-field) + ADR-037 (populator) as the inherited precedents.
- **Sign-off focus** (per Issue #302): PM on community-credit accuracy + scope discipline; Architect on schema stability + cross-format consistency + frozen-constraint preservation; Team-Lead on test coverage + small-surface effort realism.
- **Release**: `feat(302):` — restores release cadence after F-1's deliberate `docs:`-only break (F-1 NFR-5 mitigation).

---

*Generated via `/aod.define` (BLP-04 Wave 2). Next: `/aod.plan PRD: 302 - asset-tag-output-wiring`.*
