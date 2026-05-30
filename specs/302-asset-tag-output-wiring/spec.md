---
prd_reference: docs/product/02_PRD/302-asset-tag-output-wiring-2026-05-30.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-05-30
    status: APPROVED
    notes: "0 BLOCKING / 0 HIGH / 0 MEDIUM / 3 LOW. Faithful, complete, scope-disciplined translation of PRD #302. Community-credit accuracy PASS — @north-echo framed as PROTOTYPE AUTHOR of PR #262, 'surfaced by' present only as a prohibition, full #246→#262→#260→#302 chain captured (FR-011/FR-012/US-3). Scope discipline PASS — 6-tag enum + 9.2 ceiling + modifier-after-clamp ordering held OUT (FR-006/SC-011); US-5 release-cadence is additive continuity not scope creep. Zero [NEEDS CLARIFICATION] (grep-verified); architect-owned Q1/Q2/Q3/Q6/Q7 deferred to plan.md with stated defaults; PM-resolved Q4 (all tags = asset exposure) + Q5 (CHANGELOG + Discussion #246 + offered Co-Authored-By, LinkedIn deferred to BLP-04 F-3+) preserved verbatim. 12 FRs + NFR coverage + 12 SCs + 5 personas represented. All 3 LOW folded post-review: L-2 FR-008 26-case provenance parenthetical restored; L-3 FR-007 AC-2 added flagging the stale-9.5 asset-modifiers.md cleanup (risk-scoring.yaml untouched per SC-011); L-1 FR-011 declined-follow-on recognition-not-assignment nuance added. Full review .aod/results/product-manager.md."
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: Asset-Tag Output Wiring (F-260b)

**Feature Branch**: `302-asset-tag-output-wiring`
**Created**: 2026-05-30
**Status**: Draft
**Input**: User description: "PRD: 302 - asset-tag-output-wiring"
**PRD**: [docs/product/02_PRD/302-asset-tag-output-wiring-2026-05-30.md](../../docs/product/02_PRD/302-asset-tag-output-wiring-2026-05-30.md)
**Research**: [research.md](research.md)

## Overview

In v4.31.0, the community merged @north-echo's PR #262: optional inline `[asset:tag1,tag2]` tags on architecture components that act as CVSS impact-bit floors during risk scoring. The prototype is **half-integrated** — the parser extracts the tags and the risk-scorer consumes them to elevate scores, but **nothing emits which assets a finding touches**. An adopter who sets asset tags sees a slightly different number but cannot see the tags anywhere in the output, and downstream consumers (GitHub Code Scanning, SAST aggregators) get no structured asset signal.

This feature wires the asset-sensitivity tags **end-to-end through the output stack**: a `finding.yaml` schema field, deterministic population from the existing parser, `threats.md` serialization, and SARIF emission in both emitters — plus CI protection for the existing-but-unwired test suite and a community-credit moment for @north-echo. It is **wiring, not re-tuning**: the tag enum (6 values), the 9.2 modifier ceiling, and the modifier-after-clamp ordering are FROZEN and out of scope.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Asset tags propagate into SARIF (Priority: P1)

As a tachi adopter who set asset-sensitivity tags in my architecture description, I want the tags to propagate into SARIF output, so that GitHub Code Scanning and my SAST aggregator show tag-weighted, asset-aware findings.

**Why this priority**: This is the headline adopter-facing value and the most externally visible proof that "asset-aware risk scoring" is real. SARIF is the integration surface adopters consume in CI.

**Independent Test**: Run a threat-model (or risk-score) on an architecture description containing `[asset:...]` tags and inspect the SARIF; each affected result carries an `affected_assets` property listing the applicable tag strings. Delivers value on its own — adopters' code-scanning dashboards become asset-aware.

**Acceptance Scenarios**:

1. **Given** an architecture description with a `[asset:pii,phi]` component, **When** SARIF is generated, **Then** the corresponding result's `properties.affected_assets` is `["phi","pii"]` (sorted).
2. **Given** a finding on an untagged component, **When** SARIF is generated, **Then** its `properties.affected_assets` is `[]` (present, not omitted).
3. **Given** the same architecture, **When** both `generate-threats-sarif.py` and `generate-risk-scores-sarif.py` run, **Then** every finding's `affected_assets` value and the literal property key string are byte-identical between the two emitters.

---

### User Story 2 - Asset tags populated per finding in threats.md (Priority: P1)

As a downstream tool or analyst reading `threats.md`, I want `affected_assets` populated per finding, so that I can read structured asset-impact data without re-parsing the architecture description.

**Why this priority**: `threats.md` is the single source the SARIF emitters copy from; without it US-1 cannot hold the cross-format consistency invariant. Together US-1 + US-2 are the core of the feature.

**Independent Test**: Run a threat-model on a tagged architecture; `threats.md` shows an `affected_assets` field on every finding (populated where the target component carries tags, `[]` otherwise). Delivers value on its own to structured-data consumers.

**Acceptance Scenarios**:

1. **Given** an architecture with tagged components, **When** `threats.md` is produced, **Then** each finding whose target component carries tags shows an `affected_assets` field listing those tag strings (sorted), and each finding on an untagged component shows `affected_assets: []`.
2. **Given** the same finding, **When** its `threats.md` value and its SARIF value are compared, **Then** they are byte-equivalent (same tags, same order, same key string).

---

### User Story 3 - @north-echo's contribution is wired and credited (Priority: P2)

As @north-echo, author of the merged PR #262 asset-tag prototype, I want my contribution wired through the full output stack and credited, so that the feature is actually useful to downstream adopters and my contribution chain is preserved publicly.

**Why this priority**: The first non-trivial community contribution to tachi deserves to be coherent end-to-end and credited accurately. This protects the trust signal that invites future contributions.

**Independent Test**: After US-1 + US-2 pass, a community-credit artifact (CHANGELOG attribution + a public acknowledgment with an offered `Co-Authored-By` trailer, referencing Discussion #246) exists and frames @north-echo as the prototype author; the acknowledgment URL is recorded in Issue #302.

**Acceptance Scenarios**:

1. **Given** the feature is end-to-end functional, **When** the credit artifact is authored, **Then** it names @north-echo as the author of PR #262 (wording "prototype authored/contributed by", never "surfaced by"), offers a `Co-Authored-By` trailer, and references Discussion #246.
2. **Given** the credit artifact is published, **When** Issue #302 is closed, **Then** the close comment records the acknowledgment URL and the contribution chain (Discussion #246 → PR #262 → #260 → #302).

---

### User Story 4 - "Asset-aware" is provable, not aspirational (Priority: P2)

As the tachi maintainer preparing any public reference to "asset-aware risk scoring", I want the feature coherent end-to-end before that reference exists, so that the capability is provable, not aspirational.

**Why this priority**: BLP-04 is an adoption initiative; later waves benefit from a complete, demonstrable asset-tag story. A half-integrated feature reads as "merged and forgotten."

**Independent Test**: An adopter-facing reproducibility check holds — any tagged architecture produces `threats.md` + SARIF with tags visibly present, the worked example (`examples/agentic-app/architecture-with-asset-tags.md`) demonstrates propagation, and the schema-doc surface accurately documents the emitted shape.

**Acceptance Scenarios**:

1. **Given** the worked example architecture, **When** the full pipeline runs, **Then** the emitted output visibly carries the asset tags and matches the schema-doc description.
2. **Given** the schema-doc surface, **When** an adopter reads it, **Then** the enum, empty-default semantics, and per-format representation match the actual emitted output.

---

### User Story 5 - Release cadence is restored (Priority: P3)

As an adopter tracking tachi releases who saw F-1 (#296) close `docs:`-only with no release PR, I want F-260b to ship `feat:`-eligible and trigger a release, so that the cadence (every shipped capability yields a release) is restored within ~1 week of the F-1 break.

**Why this priority**: Process continuity, not a code capability — but the explicit named reason F-260b is the `feat:` follow-up to F-1's deliberate `docs:`-only close.

**Independent Test**: The squash-merge uses a `feat(302):` PR title; a release-please PR opens within ~30s post-merge; the CHANGELOG entry is `feat:`-prefixed.

**Acceptance Scenarios**:

1. **Given** the feature PR is squash-merged with a `feat(302):` title, **When** the merge lands on `main`, **Then** a release-please PR opens within ~30s; if it does not, a `feat(302):` release-marker commit is pushed.

---

### Edge Cases

- **No tags anywhere**: every finding's `affected_assets` is present as `[]` in IR, `threats.md`, and both SARIF emitters — never omitted (preserves byte-deterministic baselines).
- **No-op modifier with present tag**: a tag that forces an impact bit already at its max (e.g. `financial` → `I:H` on a finding already at `I:H`) still appears in `affected_assets` — the field records *asset exposure*, not *modifier deltas*.
- **Ceiling clamp**: a finding whose modified `cvss_base` would exceed 9.2 caps at 9.2; `affected_assets` is populated regardless of whether the ceiling clamped.
- **Component with multiple tags**: `affected_assets` lists all of them, sorted and deduplicated (verbatim from the parser's already-sorted output).
- **Fuzzy component match**: the populator joins on the same case-insensitive/fuzzy component cascade the risk-scorer §3.5 modifier pass already uses; an unmatched finding gets `[]`.
- **Unknown tag in input**: tags outside the frozen 6-value enum are ignored by the existing parser (with a stderr warning) and never appear in `affected_assets`.
- **`UNCHANGED`/`RESOLVED` findings**: inherit baseline behavior; `affected_assets` is still present per FR-005.

## Requirements *(mandatory)*

### Functional Requirements

> Each AC begins with **Given** and follows Given/When/Then. `[MANUAL-ONLY]` marks ACs that cannot be automated.

- **FR-001 (schema field)**: `schemas/finding.yaml` MUST gain an optional, **always-present-with-default** `affected_assets` field — an array of strings constrained to the frozen 6-value enum (`pii | phi | auth | secrets | financial | safety`), default `[]` — modeled on the `agentic_pattern`/`maestro_layer` always-present-default precedent (NOT the `source_attribution` omit-when-empty precedent). `schema_version` MUST bump `1.8 → 1.9` (minor, per the ADR-026 rule). The inline schema comment MUST follow the file's existing convention and cite ADR-026 (minor-bump rule) + ADR-028 (additive-field precedent) + ADR-037 (populator precedent) + PR #262, with an always-present-default note and a cross-reference that the modifier logic lives frozen in `risk-scoring.yaml`.
  - **AC-1**: **Given** `finding.yaml` at `schema_version: 1.8`, **When** F-260b lands, **Then** `affected_assets` is defined as an optional enum-array field with default `[]` and `schema_version` reads `1.9`.
  - **AC-2**: **Given** the field definition, **When** its inline comment is read, **Then** it cites ADR-026/028/037 + PR #262 and the always-present-default semantics.

- **FR-002 (deterministic population)**: The `affected_assets` value MUST be produced **deterministically** by joining `parse_component_asset_map()` output to each finding by target component (same case-insensitive/fuzzy cascade as the risk-scorer §3.5 pass), as a verbatim lookup `affected_assets = component_asset_map.get(component, [])`. The value MUST be sorted (matching the parser's already-sorted output). The **LLM risk-scorer agent MUST NOT author this field**. The CVSS impact-bit floor pass, the modifier-after-clamp ordering, and the 9.2 ceiling MUST remain unchanged.
  - **AC-1**: **Given** a finding on a tagged component, **When** `affected_assets` is populated, **Then** the value equals that component's sorted tag list from `parse_component_asset_map()` verbatim.
  - **AC-2**: **Given** any architecture, **When** F-260b runs, **Then** no finding's `cvss_base`, composite score, or severity band changes relative to the PR #262 behavior.

- **FR-003 (threats.md serialization)**: Per-finding `threats.md` output MUST emit an `affected_assets` field (array of tag enum strings). The serialization surface MUST be documented in [finding-format-shared.md](../../.claude/skills/tachi-shared/references/finding-format-shared.md) and reflected in the [threats.md template](../../templates/tachi/output-schemas/threats.md). *(Surface shape resolved in plan.md — see Plan-Time Decisions Q1.)*
  - **AC-1**: **Given** a tagged architecture, **When** `threats.md` is produced, **Then** every finding carries an `affected_assets` field, populated where the target component is tagged.

- **FR-004 (SARIF emission — both emitters)**: **Both** `scripts/generate-threats-sarif.py` and `scripts/generate-risk-scores-sarif.py` MUST add an `affected_assets` entry to each result's `properties` bag. The literal key MUST be `affected_assets` (snake_case, byte-identical to the schema and `threats.md` field) in both emitters — the pre-existing key-casing drift MUST NOT be replicated. Both emitters MUST source the value from the single emitted `threats.md` (a copy via one shared extractor, e.g. `parse_affected_assets()` in `sarif_common.py`), NOT independently re-derive it. [sarif-specification.md](../../.claude/skills/tachi-orchestration/references/sarif-specification.md) MUST document the property.
  - **AC-1**: **Given** a finding, **When** both emitters run, **Then** each result carries `properties.affected_assets` with the literal snake_case key.
  - **AC-2**: **Given** the same finding, **When** the two emitters' output is compared, **Then** the `affected_assets` value and key are byte-identical.

- **FR-005 (backward-compatible empty default)**: When an architecture (or a finding's target component) carries no tags, `affected_assets` MUST be present as an empty array `[]`, NOT omitted, in every format (IR, `threats.md`, SARIF).
  - **AC-1**: **Given** an untagged architecture, **When** output is generated, **Then** every finding shows `affected_assets: []` / `"affected_assets": []` in `threats.md` and both SARIF emitters.

- **FR-006 (frozen-constraint preservation)**: F-260b MUST NOT add tag-enum entries, change the 9.2 ceiling, or change the modifier-after-clamp ordering. `VALID_ASSET_TAGS` and the `asset_modifiers` table remain frozen. Any diff touching these MUST be reverted.
  - **AC-1**: **Given** the merged feature, **When** `git diff main -- schemas/risk-scoring.yaml scripts/tachi_parsers.py` is run, **Then** it shows no change to `VALID_ASSET_TAGS`, the `9.2` ceiling, or the modifier-after-clamp section.

- **FR-007 (schema documentation)**: A schema-doc surface MUST accurately describe the emitted `affected_assets` contract — its enum, empty-default semantics, and IR/`threats.md`/SARIF representation. The contract documentation MUST NOT be added to `schemas/risk-scoring.yaml` (kept byte-frozen for SC-011). *(Location resolved in plan.md — see Q7; default = extend [asset-modifiers.md](../../.claude/skills/tachi-risk-scoring/references/asset-modifiers.md) + a `schemas/README.md` pointer + the FR-001 field comment.)*
  - **AC-1**: **Given** the schema-doc surface, **When** compared to emitted output, **Then** the enum, empty-default semantics, and per-format representation match.
  - **AC-2**: **Given** the doc-extension touches `asset-modifiers.md`, **When** edited, **Then** the stale "9.5" in its T-2 worked example is corrected to the frozen `9.2` — and `schemas/risk-scoring.yaml` is NOT touched (kept byte-frozen for SC-011).

- **FR-008 (CI wiring)**: `.github/workflows/tachi-pytest.yml` MUST add `tests/scripts/test_asset_sensitivity_tags.py` (the existing 26-case suite — 23 test functions, 26 collected via parametrize) plus any new F-260b tests to **both** its `paths:` filter and its pytest invocation (lock-step).
  - **AC-1**: **Given** the updated workflow, **When** `grep test_asset_sensitivity_tags .github/workflows/tachi-pytest.yml` runs, **Then** it matches in both the paths filter and the pytest command.
  - **AC-2**: **Given** a PR touching the relevant paths, **When** CI runs, **Then** the asset-tag suite executes.

- **FR-009 (regression protection)**: The regression tests behind SC-001…SC-007 MUST be implemented and pass: schema-stability byte-identity, per-tag propagation (all 6 tags), ceiling enforcement, empty-default, worked-example dry-run, and cross-format consistency.
  - **AC-1**: **Given** the test suite, **When** it runs, **Then** all SC-001…SC-007 regression tests pass.

- **FR-010 (release-cadence restoration)**: The feature MUST ship via a `feat(302):` PR title; `CHANGELOG.md` MUST gain a `feat:`-prefixed entry. The maintainer MUST verify a release-please PR opens post-merge (~30s SLO); if not, push a `feat(302):` release-marker.
  - **AC-1**: **Given** the squash-merge with a `feat(302):` title, **When** it lands on `main`, **Then** a release-please PR opens within ~30s (else a `feat(302):` marker is pushed). `[MANUAL-ONLY] post-merge release-please verification is a delivery-time check`

- **FR-011 (community credit)**: A community-credit artifact MUST credit @north-echo for PR #262 following the F-292/@armorer-labs *mechanism* precedent: (a) a `CHANGELOG.md` attribution line, (b) an offered `Co-Authored-By:` trailer, (c) a public acknowledgment (Discussion #246 comment), (d) a Discussion #246 reference. Wording MUST reflect that @north-echo authored merged PR #262 — never "surfaced by". @north-echo declined follow-on work, so the credit is **recognition, not a work assignment** — no contribution ask. The acknowledgment URL MUST be recorded in the Issue #302 close comment.
  - **AC-1**: **Given** the credit artifact, **When** reviewed, **Then** it names @north-echo as PR #262's author (never "surfaced by"), offers `Co-Authored-By`, and references Discussion #246. `[MANUAL-ONLY] attribution wording + tone require human review`

- **FR-012 (issue close)**: Issue #302 MUST be closed with a comment citing the feature PR, the release tag, and the community-credit URL. Parent Issue #260 MUST be closed; its close comment MUST link the F-260b PR and credit @north-echo, completing the Discussion #246 → PR #262 → #260 → #302 chain.
  - **AC-1**: **Given** delivery, **When** Issues #302 and #260 are viewed, **Then** both show `state=CLOSED` and #302's close comment cites PR + release + credit URLs. `[MANUAL-ONLY] issue-close is a delivery-time action`

### Key Entities

- **`affected_assets` field**: an optional, always-present array of asset-sensitivity tag strings on each finding; default `[]`; lives in `finding.yaml` IR, `threats.md`, and both SARIF emitters' `result.properties`. Records *which assets a finding touches*.
- **Asset tag enum (FROZEN)**: the 6-value vocabulary `pii | phi | auth | secrets | financial | safety`. No additions in scope.
- **`component_asset_map`**: the existing parser output (`parse_component_asset_map()`) mapping component display names → sorted, deduped, lowercase tag lists. The single deterministic source for population.
- **Finding**: the unit of output; gains `affected_assets` without any change to its scoring fields.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001 (schema field + version bump)**: `schemas/finding.yaml` contains the optional `affected_assets` enum-array field and `schema_version` is `1.9`. *Verify*: `grep -A3 affected_assets schemas/finding.yaml` shows the 6-value enum; `grep schema_version schemas/finding.yaml` shows `1.9`.
- **SC-002 (schema-stability byte-identity)**: no-tag example baselines regenerate byte-identically except the additive `affected_assets: []`. *Verify*: regenerate under `SOURCE_DATE_EPOCH=1700000000`; `git diff` shows only added `affected_assets` lines.
- **SC-003 (per-tag propagation)**: all 6 enum tags propagate to IR, `threats.md`, and SARIF — `pii`, `phi`, `auth`, `safety` via the worked example; `secrets`, `financial` via unit fixtures; including a no-op-modifier-with-present-tag case that still lists the tag.
- **SC-004 (ceiling enforcement preserved)**: a tagged finding whose modified `cvss_base` would exceed 9.2 caps at 9.2; `affected_assets` is populated regardless of clamp.
- **SC-005 (empty-tag default)**: a no-tag architecture produces `affected_assets: []` (present) in all formats on every finding.
- **SC-006 (cross-format consistency)**: an automated **multi-finding** test (≥2 differently-tagged components + ≥1 untagged) asserts a per-finding equality table across `threats.md`, `generate-threats-sarif.py`, and `generate-risk-scores-sarif.py` — every finding (including untagged `[]`) has byte-identical `affected_assets` value and key.
- **SC-007 (schema-doc accuracy)**: the schema-doc surface's enum + empty-default semantics + per-format representation match the actual emitted output.
- **SC-008 (CI runs asset-tag tests)**: `tachi-pytest.yml` runs `test_asset_sensitivity_tags.py` + new F-260b tests. *Verify*: `grep` matches in both paths filter and pytest command; a CI run shows the suite executing.
- **SC-009 (release cadence restored)**: a `feat(302):` squash-merge triggers a release-please PR within ~30s; CHANGELOG entry uses `feat:`.
- **SC-010 (community credit recorded)**: @north-echo credited (CHANGELOG names @north-echo + PR #262); acknowledgment URL in Issue #302 close comment; Discussion #246 referenced.
- **SC-011 (frozen constraints untouched)**: `git diff main -- schemas/risk-scoring.yaml scripts/tachi_parsers.py` shows no change to the enum, ceiling, or modifier ordering (only additive populator/emitter changes elsewhere).
- **SC-012 (issues closed)**: Issue #302 closed with deliverable + credit URLs; parent Issue #260 closed.

## Assumptions

- `threats.md` is authored by the orchestrator LLM agent (verified); the deterministic-value requirement (FR-002) is satisfied by a deterministic lookup whose value the agent copies verbatim (the `agentic_pattern`/`maestro_layer` working pattern) and/or a deterministic post-step — the exact serialization mechanism is a plan-time decision (Q1), not a scope question.
- The `examples/agentic-app/architecture-with-asset-tags.md` worked example (4 of 6 tags across 4 components) plus unit fixtures for `secrets`/`financial` are sufficient propagation coverage; broader example coverage is a follow-on (Q6).
- No new ADR is required; the ADR-026 minor-bump rule + ADR-028/037 precedents govern (Q2). plan.md adds one sentence classifying population as a deterministic serializer-tier join, not a new synthesis phase.
- Adding an optional field with `[]` default is backward-compatible (additive minor bump); consumers ignoring unknown fields are unaffected.

## Plan-Time Decisions (deferred to `/aod.plan`, architect-owned)

These are mechanism choices with stated defaults — not spec ambiguities. They do not block sign-off.

| Ref | Question | Default (lean) |
|---|---|---|
| Q1 | `threats.md` serialization surface | Always-present per-finding **detail-block** field (Design A); gated block (Design B) rejected — violates FR-005 |
| Q2 | New ADR for the schema field? | **No** — ADR-026 rule + ADR-028/037 precedents suffice; one classifying sentence in plan.md |
| Q3 | SARIF property shape | **Flat array** of tag strings (matches `threats.md`, trivializes NFR-3) |
| Q4 | Populator semantics *(PM-resolved)* | **All tags on the target component** (asset exposure, not modifier deltas); architect owns sort/dedup only |
| Q5 | Community-credit surface *(PM-resolved)* | CHANGELOG + Discussion #246 comment + offered `Co-Authored-By`; LinkedIn deferred to BLP-04 F-3+ |
| Q6 | Example coverage | **Single** existing example; expansion is follow-on |
| Q7 | Schema-doc location | Extend `asset-modifiers.md` (+ `schemas/README.md` pointer + field comment); not in `risk-scoring.yaml` |

## Dependencies

**Satisfied**: PR #262 merged (@north-echo, v4.31.0); F-1 (#296) CLOSED 2026-05-30 (BLP-04 sequencing gate); ADR-026 / ADR-028 / ADR-037 exist.

**Frozen constraints (non-negotiable, inherited from PR #262)**: 6-value tag enum; 9.2 modifier ceiling; modifier-after-clamp ordering; inline-only tag location (no sidecar `assets.yaml`).

## Out of Scope

- New tag-enum entries (enum frozen at 6).
- Modifier-ceiling, ordering, or CVSS modifier-logic changes (wiring, not re-tuning).
- Asset-tag variants for additional example architectures beyond the existing agentic-app example (follow-on, Q6).
- Custom/extensible tag vocabularies (rejected in the #260 discussion).
- Heavy long-form distribution writing (deferred to BLP-04 F-3+).
- `affected_assets` in the PDF report / infographics (separate report-assembly feature).
- `risk-scoring.yaml` `schema_version` 1.1 → 1.2 bump (no cumulative shape change this feature).
