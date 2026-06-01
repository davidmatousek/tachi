---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-05-30
    status: APPROVED_WITH_CONCERNS
    notes: "0 BLOCKING / 0 HIGH / 1 MEDIUM / 2 LOW (rev-1). Both PM-focus axes PASS: scope discipline (6-tag enum + 9.2 ceiling + modifier-after-clamp ordering held OUT, SC-011 intact, no creep/contraction) + no-silent-scope-change (the FR-relaxing Design B fallback is explicitly routed to PM+Architect as a PRD amendment, NOT silently adopted). PM DECISIONS: Design A stands; Design B NOT elected; no PRD amendment authorized; Q4 (all-tags asset-exposure) + Q5 (CHANGELOG + Discussion #246 + offered Co-Authored-By, LinkedIn deferred) preserved verbatim; all 5 personas served; FR-10/11/12 (feat(302) cadence / @north-echo prototype-author credit / #246→#262→#260→#302 close chain) carry through intact. M-1 (non-blocking team-lead hand-off): the '1-2 line at an existing site' effort premise is VOID — §3.5 is LLM prose, not an executable join — team-lead MUST re-validate effort at /aod.tasks from the corrected premise. L-1/L-2 are architect-domain. NOTE: the architect's parallel rev-1 H-1 correction (production NFR-3 is baseline/test-checked not structural; production SARIF is LLM-authored) was folded into rev-2 and alters NO PM scope decision — US-4 'provable, not aspirational' is still met via baseline tests + worked example. Full review .aod/results/product-manager.md."
  architect_signoff:
    agent: architect
    date: 2026-05-30
    status: APPROVED
    notes: "APPROVED (rev-2) — all 6 rev-1 findings resolved, 0 open, 0 regressions. Rev-1 was CHANGES_REQUESTED (1 HIGH / 3 MEDIUM / 2 LOW). H-1 RESOLVED: AD-1 now states production .sarif is LLM-authored (orchestrator → threats.sarif, risk-scorer → risk-scores.sarif, no Bash) and the generate-*-sarif.py scripts have ZERO production callers (F-219-vintage = regeneration/verification tier); NFR-3 production consistency corrected to baseline/test-checked (maestro_layer precedent), structural only in the script tier; production authoring sites added as in-scope Components — the populator pipeline-sequencing step + LLM-copy instructions in BOTH sarif-specification.md AND risk-scorer.md; correction propagated to data-model.md §Cross-Format + contract §4 + quickstart live-pipeline gate. M-1: appended block reframed as a NEW structure (threats.md has no detail block — all tables). M-2: production tier ELECTED + sequencing resolved at plan time (AD-1 M-2). M-3: Design A buys deterministic VALUE (FR-2 literal), NOT structural NFR-3 — both designs test-checked cross-format in production. L-1: Q2 expanded + thin ADR-046 COMMITTED (production-tier criterion met). L-2: data-flow diagram shows the two production LLM SARIF-authoring acts + Python scripts as the parallel verification tier. No regressions: Q1 appended-block surface, Q3/FR-4 snake_case key pin, SC-011 frozen-constraint discipline, 1.8→1.9 minor bump, AD-2 baseline strategy, Design B as PRD-amendment fallback all intact. Pre-Mortem failure modes (R9 'shipped, adopters see nothing') addressed via live-pipeline DoD gate. R8/R9 production surface ~3-4 days (within the 06-11 ceiling's 6-day slack) → team-lead re-scope at /aod.tasks. Full review .aod/results/architect.md."
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: Asset-Tag Output Wiring (F-260b)

**Branch**: `302-asset-tag-output-wiring` | **Date**: 2026-05-30 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/302-asset-tag-output-wiring/spec.md`
**PRD**: [302-asset-tag-output-wiring-2026-05-30.md](../../docs/product/02_PRD/302-asset-tag-output-wiring-2026-05-30.md)
**Revision**: rev-2 (architect H-1/M-1/M-2/M-3/L-1/L-2 folded — production-tier elected; NFR-3 corrected to test-checked; ADR-046 committed)

## Summary

Wire @north-echo's community-merged asset-sensitivity tags (PR #262, v4.31.0) end-to-end through the output stack so tags an adopter sets in their architecture description propagate into machine-readable output. Add an optional, always-present `affected_assets[]` field to `finding.yaml` (schema 1.8 → 1.9), produce its value **deterministically** from `parse_component_asset_map()` joined to each finding by component, serialize it in `threats.md`, and carry it into **both** SARIF surfaces' `result.properties`. Protect the existing 26-case test suite by wiring it into CI, add regression tests, and credit @north-echo. Frozen constraints (6-tag enum, 9.2 ceiling, modifier-after-clamp ordering) are out of scope.

**The plan's central job** is to resolve the architect-owned Q1/Q2/Q3/Q6/Q7 and reconcile a **two-layer gap between the PRD's mental model and the code** (both verified against the source, architect-confirmed):

1. The PRD's FR-2 assumes a "deterministic threats.md serializer" joining `parse_component_asset_map()` to findings. **It does not exist** — `threats.md` is authored by the orchestrator LLM agent, and `parse_component_asset_map()` has **no production caller** (referenced only by the LLM risk-scorer's prose `risk-scorer.md:281`, a doc, and its 26 tests).
2. **The production `.sarif` files are LLM-authored too** — the orchestrator writes `threats.sarif`; the risk-scorer (tools: Read/Glob/Grep/Write, **no Bash**, `model: sonnet`) writes `risk-scores.sarif`. The Python `generate-*-sarif.py` scripts are **F-219-vintage utilities with zero production callers**; they are the regeneration/baseline/verification tier, **not** the artifact an adopter receives.

**Consequence**: NFR-3 cross-format consistency in **production** is **baseline/test-checked** — the same guarantee class as `maestro_layer`/`agentic_pattern` — **NOT** structural-by-construction. This plan elects the **production tier** (US-1/US-4 require adopters to see `affected_assets` in live output) and names every production authoring site. See [Architecture Decision AD-1](#architecture-decision-ad-1-the-determinism-mechanism) — the load-bearing decision.

## Technical Context

**Language/Version**: Python 3.11 (stdlib-only per PAT-014); Markdown + YAML (schemas, references, templates); LLM agent prose (orchestrator, risk-scorer)
**Primary Dependencies**: `scripts/tachi_parsers.py` (`parse_component_asset_map`, `VALID_ASSET_TAGS`), `scripts/sarif_common.py` (shared helpers the regeneration scripts import), pytest
**Storage**: Files only — `schemas/finding.yaml`, `threats.md`, SARIF JSON; no database
**Testing**: pytest (`tests/scripts/test_asset_sensitivity_tags.py` — existing 26 cases; new F-260b regression tests); byte-identity baseline regen under `SOURCE_DATE_EPOCH=1700000000`
**Target Platform**: Local CLI (Claude Code LLM pipeline) + GitHub Actions CI (`tachi-pytest.yml`)
**Project Type**: Single project (instrumentation harness — LLM agents + Python scripts + schemas + references)
**Performance Goals**: N/A. Determinism of the value is the hard requirement.
**Constraints**: Byte-deterministic baselines (ADR-021); cross-format consistency (NFR-3, **baseline/test-checked in production** — see AD-1); frozen constraints untouched (SC-011); the PRD's ~1–2 day NFR-7 envelope is **superseded** by the corrected surface (see Complexity Tracking / R8 — team-lead re-scopes)
**Scale/Scope**: 1 schema field + 1 deterministic populator (value authority) + 1 threats.md surface + 3 production LLM authoring-contract updates + 2 SARIF regeneration scripts + 1 shared extractor + thin ADR-046 + CI wiring + 6 regression tests + docs + community credit

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Status |
|---|---|---|
| VIII — Product-Spec Alignment | spec.md has PM sign-off APPROVED | ✅ PASS |
| Additive-schema discipline (ADR-026) | New field is additive + has default + shape unchanged → minor bump | ✅ PASS (1.8 → 1.9) |
| Byte-deterministic baselines (ADR-021) | Baselines regenerate under `SOURCE_DATE_EPOCH`; only the additive block differs | ✅ PASS (AD-2) |
| Frozen-constraint discipline (NFR-5) | No enum/ceiling/ordering change | ✅ PASS (SC-011 binary diff gate) |
| IX — Community attribution | External contributor credited accurately | ✅ PASS (FR-11; @north-echo prototype-author framing) |
| ADR governance (Q2) | Production-tier populator modifies live agent SARIF-authoring contracts | ✅ PASS via **thin ADR-046** (architect criterion: production-tier → require a thin ADR; field alone would be no-ADR per ADR-026/028/037) |

## Architecture Decision AD-1: The Determinism Mechanism

**This is the load-bearing decision.** FR-2 (deterministic value), FR-3 (in `threats.md`), FR-4 (SARIF carries it), and NFR-3 (cross-format consistency) all converge here.

### The architecture, accurately (verified against code, architect-confirmed)

tachi has **two tiers the PRD treated as one**:

- **Production / LLM-authoring tier** — `tachi.threat-model` invokes the **orchestrator agent**, which writes `threats.md` (findings as **pipe-table rows** in §3 STRIDE / §4 AI — there are **no per-finding detail blocks**) **and** `threats.sarif`. `tachi.risk-score` invokes the **risk-scorer agent** (no Bash), which writes `risk-scores.md` and `risk-scores.sarif`. This is the artifact adopters receive.
- **Regeneration / Python tier** — `generate-threats-sarif.py`, `generate-risk-scores-sarif.py`, `sarif_common.py`, `parse_component_asset_map()`. These parse *committed* `.md` and exist for baselines/tests. **Nothing in the live pipeline invokes them** (the F-219 `delivery.md:146` aspiration to route production SARIF through them was never wired).

Today nothing connects `parse_component_asset_map()` (Python tier) to any production output (LLM tier). Every FR in this feature crosses that boundary.

### Decision: **Design A — deterministic value authority + production LLM-copy authoring + regeneration-tier verification**

Elected **tier: production** (US-1/US-4 demand live output carry `affected_assets`; a regeneration-only wiring would ship a feature adopters never see — failing US-1/US-4).

1. **Value authority (FR-2, deterministic)** — a deterministic, non-LLM populator computes `affected_assets = component_asset_map.get(component, [])` (Q4: all tags on the component; sorted/deduped free from the parser) and **writes the `affected_assets` block into `threats.md`**. The value is a pure 6-enum lookup — it has no business being LLM-judged. This is FR-2's literal "deterministic, not LLM-authored" value, satisfied for the canonical `threats.md` surface.
2. **Surface (Q1)** — an **always-present, machine-readable `affected_assets` block appended to `threats.md`**, keyed by finding ID (`[]` when none). This is a **new structure** (M-1: `threats.md` has no existing detail block — it is 100% tables; the PRD-stage "detail-block field" lean rested on an inaccurate mental model). Appending leaves every existing STRIDE/AI table row **byte-identical** (SC-002 "added lines only") and avoids a brittle change to the position-based table parser.
3. **Production SARIF authoring (FR-4)** — because production `.sarif` is LLM-authored, the LLM authoring contracts MUST be updated to **copy the single `threats.md` block value verbatim**: `sarif-specification.md` (orchestrator → `threats.sarif`) and `risk-scorer.md` SARIF section (risk-scorer → `risk-scores.sarif`), each emitting `result.properties.affected_assets` (literal **snake_case** key, flat array — Q3). The populator must write the `threats.md` block **before** SARIF authoring sources it (sequencing — see M-2 below).
4. **Verification tier** — `parse_affected_assets(threats_content)` in `sarif_common.py` + the `generate-*-sarif.py` scripts + baselines are the deterministic **reference** that pins the production LLM output: SC-006 multi-finding equality + SC-002 byte-identity enforce that production matches the deterministic ground truth.

### What this guarantees (corrected — H-1)

| Requirement | Guarantee |
|---|---|
| FR-2 (deterministic value, not LLM-authored) | ✅ **literal** for the `threats.md` block (populator-written). The SARIF copy is mechanical (no LLM judgment over the value). |
| FR-3 (in `threats.md`) | ✅ appended block. |
| FR-4 (both SARIF surfaces carry it) | ✅ via updated LLM authoring contracts (production) + the regeneration scripts (reference). |
| NFR-3 (cross-format consistency) | ⚠️ **baseline/test-checked in production** (SC-006 + SC-002) — the `maestro_layer` precedent's guarantee. **Structural** only in the regeneration/script tier. *(This corrects rev-1's overclaim that the shared extractor delivers structural NFR-3 in production — it does not, because production SARIF is LLM-authored.)* |

### M-2 — production sequencing (resolved at plan time, not deferred)

The populator must write the `threats.md` block **before** the SARIF surfaces source it. The orchestrator currently bundles `threats.md` + `threats.sarif` in one agent pass, so the build MUST sequence one of:
- **(preferred)** orchestrator emits `threats.md` tables → deterministic populator appends the block (Bash step in the `tachi.threat-model` flow, which the *command* — not the no-Bash agent — can run) → SARIF authoring (orchestrator/risk-scorer) copies the block. Keeps FR-2 literal (populator owns the value).
- **(fallback, only if sequencing proves infeasible within the ceiling)** orchestrator transcribes both the block and the SARIF property from the tags it reads, with the populator/scripts as the verification reference — this weakens FR-2 to test-enforced and is **Design B** (PRD amendment, PM+Architect election).

This sequencing is the one genuinely new pipeline-wiring item; it is **in scope** and team-lead-costed (R8), not a silent build deferral.

### Alternative — **Design B (LLM-transcribed value)**: REJECTED as primary

The orchestrator/risk-scorer transcribe `affected_assets` into all three surfaces (like `maestro_layer`); the populator/scripts only verify. **Smaller** (no pipeline-sequencing step). **But** the *value* is LLM-judged, relaxing **FR-2 ("not LLM-authored")**. Both designs are equally test-checked for cross-format consistency in production (NFR-3) — so **the only thing Design A buys over Design B is a deterministic value (FR-2 literal)** (M-3 — corrected from rev-1, which wrongly claimed Design A also buys structural NFR-3). That is still worth it — a `dict.get` over a 6-value enum should not be LLM-judged — but it is the honest reason. Design B requires a **PRD amendment (PM scope)**; PM has **declined** it (no amendment authorized). Documented as the Triad-electable fallback if R8 re-scoping finds Design A incompatible with the 2026-06-11 ceiling.

### Deferred ideal (out of scope, one-line)

A genuinely **structural** production NFR-3 would route production SARIF through the Python scripts (orchestrator/risk-scorer write only `.md`; a deterministic Bash step generates `.sarif` — the F-219 `delivery.md:146` aspiration). That is a pipeline re-architecture (remove SARIF authoring from two agents, regenerate all SARIF baselines) far exceeding this feature; noted as the future ideal, not F-260b scope.

## Architecture Decision AD-2: Byte-Identity Baseline Strategy

Appending an always-present `affected_assets` block means existing baselines gain **only added lines** — STRIDE/AI table rows stay byte-identical. Regenerate the no-tag baseline once under `SOURCE_DATE_EPOCH=1700000000` as a feature deliverable (ADR-037 controlled-regeneration precedent); SC-002 asserts the only diff is the additive block (line-level, strict — Pre-Mortem #4). Strictly cleaner than a column approach.

## Open-Question Resolutions

| Q | Resolution | Owner |
|---|---|---|
| **Q1** serialization surface | Always-present appended per-finding `affected_assets` block (by finding ID), `[]` default; a **new structure** (no detail block exists); existing tables byte-stable (AD-1 §2) | Architect ✓ (this plan) |
| **Q2** new ADR? | **Thin ADR-046 committed.** The field alone needs no ADR (ADR-026 rule + ADR-028/037 precedents); but production-tier election modifies the **live agent SARIF-authoring contracts**, which the architect's criterion makes ADR-worthy. ADR-046 records: the LLM/Python tier boundary, production-tier election, test-checked (not structural) production NFR-3, the deterministic-value rationale, and the deferred structural ideal | Architect ✓ (criterion met) |
| **Q3** SARIF property shape | Flat array of tag strings (matches `threats.md`; trivializes the copy) | Architect ✓ |
| **Q4** populator semantics | All tags on the target component (asset exposure) — `map.get(component, [])` verbatim | PM ✓ (pre-resolved) |
| **Q5** credit surface | CHANGELOG + Discussion #246 comment + offered `Co-Authored-By`; LinkedIn deferred to BLP-04 F-3+ | PM ✓ (pre-resolved) |
| **Q6** example coverage | Single existing `examples/agentic-app/architecture-with-asset-tags.md` (4 tags) + unit fixtures for `secrets`/`financial` | Team-Lead ✓ |
| **Q7** schema-doc location | Extend `asset-modifiers.md` (Output Contract section) + `schemas/README.md` pointer + `finding.yaml` field comment; correct the stale "9.5" in the T-2 example; never touch byte-frozen `risk-scoring.yaml` | Architect ✓ |

## Components

- **`finding.yaml` schema field** — optional `affected_assets` enum-array, default `[]`, `schema_version` 1.9 (always-present-with-default, `agentic_pattern`/`maestro_layer` precedent).
- **Deterministic populator (value authority, NEW)** — Python; joins `parse_component_asset_map(architecture)` → findings by component; writes the `affected_assets` block into `threats.md`. Pure function; no LLM; no scoring change.
- **Pipeline sequencing step (NEW)** — runs the populator after the orchestrator emits `threats.md` tables and before SARIF authoring (AD-1 M-2); a Bash step in the `tachi.threat-model`/`tachi.risk-score` command flow.
- **`threats.md` `affected_assets` block** (`templates/tachi/output-schemas/threats.md` + `finding-format-shared.md`) — new appended structure; tables byte-stable.
- **Production LLM SARIF-authoring contracts** — `sarif-specification.md` (orchestrator → `threats.sarif`) **and** `risk-scorer.md` SARIF section (risk-scorer → `risk-scores.sarif`): emit `result.properties.affected_assets` (snake_case, flat array) copied verbatim from the `threats.md` block.
- **Shared extractor + regeneration scripts (verification tier)** — `parse_affected_assets()` in `sarif_common.py`; `generate-threats-sarif.py` + `generate-risk-scores-sarif.py` emit the property for baselines/tests.
- **ADR-046 (thin, NEW)** — documents the determinism-mechanism / tier-boundary decision.
- **Schema docs** — `asset-modifiers.md` Output Contract section (+ stale-9.5 fix) + `schemas/README.md` pointer.
- **CI** (`.github/workflows/tachi-pytest.yml`) — 26-case suite + new tests into `paths:` + invocation (lock-step).
- **Community credit** — `CHANGELOG.md` + Discussion #246 + Issue #302/#260 close.

## Data Flow

```
architecture description (.md, inline [asset:pii,phi] tags)
   │
   ├──────────────── PRODUCTION (LLM-authoring tier) ────────────────────────────────┐
   │  orchestrator agent ─► threats.md  (findings as table rows — tables FROZEN here) │
   │        │                                                                          │
   │        ▼   (Bash step in command flow — AD-1 M-2)                                 │
   │  DETERMINISTIC POPULATOR (Python): parse_component_asset_map(arch) ⋈ findings     │
   │        │   affected_assets = map.get(component, [])  (sorted)  ← FR-2 value       │
   │        ▼                                                                          │
   │  threats.md + appended always-present affected_assets block (by finding ID)       │
   │        │                                                                          │
   │        ├─► orchestrator authors threats.sarif  ─ copies block value (snake_case)  │
   │        └─► risk-scorer authors risk-scores.sarif ─ copies block value (snake_case)│
   │                         └──── adopter-facing output (US-1/US-2) ──────────────────┘
   │
   └──────────────── VERIFICATION (Python regeneration tier — NOT live) ──────────────┐
      parse_affected_assets(threats_content) [sarif_common.py]                          │
        │                                                                               │
        ├─► generate-threats-sarif.py        ─┐                                         │
        └─► generate-risk-scores-sarif.py    ─┴─► baselines + SC-006 equality / SC-002  │
                                                  pin production output to ground truth  │
      ────────────────────────────────────────────────────────────────────────────────┘
```

Production cross-format consistency (NFR-3) = the single `threats.md` block value copied into both SARIFs + **baseline/test enforcement** (SC-006/SC-002), the `maestro_layer` guarantee. The risk-scorer §3.5 CVSS-modifier pass and the 9.2 ceiling are **unchanged** — the populator records provenance only; it never re-scores.

## Tech Stack

Python 3.11 stdlib-only (PAT-014); pytest; Markdown/YAML; LLM agents (orchestrator, risk-scorer); GitHub Actions; `SOURCE_DATE_EPOCH` deterministic baselines (ADR-021). No new third-party dependencies.

## Project Structure

### Documentation (this feature)

```
specs/302-asset-tag-output-wiring/
├── plan.md  spec.md  research.md  data-model.md  quickstart.md
├── contracts/affected-assets-contract.md
└── tasks.md             # /aod.tasks output
```

### Source Code (repository root — files touched)

```
schemas/
├── finding.yaml                  # + affected_assets field; schema_version 1.9
└── README.md                     # + pointer to the affected_assets contract

scripts/
├── tachi_parsers.py              # READ-ONLY (VALID_ASSET_TAGS/parse_component_asset_map frozen — SC-011)
├── <populator>                   # NEW deterministic value authority (writes threats.md block; AD-1 §1)
├── sarif_common.py               # + parse_affected_assets() shared extractor (verification tier)
├── generate-threats-sarif.py     # + result.properties.affected_assets (regeneration/verification tier)
└── generate-risk-scores-sarif.py # + result.properties.affected_assets (regeneration/verification tier)

templates/tachi/output-schemas/
└── threats.md                    # + appended affected_assets block (tables byte-stable)

.claude/skills/
├── tachi-shared/references/finding-format-shared.md          # + affected_assets block serialization
├── tachi-risk-scoring/references/asset-modifiers.md          # + Output Contract section; fix stale 9.5
└── tachi-orchestration/references/sarif-specification.md      # + LLM-copy instruction: threats.sarif affected_assets (PRODUCTION authoring)

.claude/agents/tachi/
├── orchestrator.md               # threats.md tables UNCHANGED; emits before populator runs (sequencing)
└── risk-scorer.md                # §3.5 scoring UNCHANGED (frozen); + SARIF section LLM-copy instruction: risk-scores.sarif affected_assets (PRODUCTION authoring)

.claude/commands/                  # tachi.threat-model / tachi.risk-score: + populator sequencing step (AD-1 M-2)

docs/architecture/02_ADRs/
└── ADR-046-asset-tag-output-wiring.md   # NEW thin ADR (tier-boundary decision)

.github/workflows/tachi-pytest.yml # + test_asset_sensitivity_tags.py + new tests (paths + invocation)

tests/scripts/
├── test_asset_sensitivity_tags.py     # existing 26 cases (now CI-protected)
└── test_affected_assets_wiring.py     # NEW — SC-001..SC-007 regression (populator + extractor + cross-format)

examples/agentic-app/<baselines>   # regenerated once under SOURCE_DATE_EPOCH (additive block only)
CHANGELOG.md                       # feat(302): entry + @north-echo attribution
```

**Structure Decision**: Single-project instrumentation harness spanning the LLM/Python tier boundary. New artifacts: the deterministic populator, the pipeline sequencing step, and thin ADR-046; everything else extends existing files following `agentic_pattern`/`maestro_layer` + `sarif_common` precedents.

## Phase 0: Research

Complete — [research.md](research.md) + the AD-1 code investigation (this plan, architect-verified). Zero NEEDS CLARIFICATION remain. Decisions (Decision / Rationale / Alternatives):
- **Production-tier Design A** (deterministic value authority + LLM-copy authoring + regeneration verification). *Rationale*: only path delivering FR-2 literal value AND adopter-facing output (US-1/US-4). *Alternatives*: Design B (LLM value, FR-2 relaxed → PRD amendment, PM-declined); structural-via-script-rearchitecture (out of scope, NFR-7); regeneration-only (adopters see nothing → fails US-1/US-4).
- **Appended block, new structure, not a column**. *Rationale*: byte-stable tables + SC-002 "added lines"; no column-parser change. *Alternatives*: column (modifies every row) — rejected.
- **snake_case `affected_assets` key pinned in both SARIF surfaces**. *Rationale*: matches schema/threats.md; refuses the documented key-casing drift. *Alternatives*: inherit surrounding kebab/camel — rejected.
- **NFR-3 production = test-checked (not structural)**. *Rationale*: production SARIF is LLM-authored; honest framing = `maestro_layer` precedent.

## Phase 1: Design & Contracts

Artifacts: [data-model.md](data-model.md), [contracts/affected-assets-contract.md](contracts/affected-assets-contract.md), [quickstart.md](quickstart.md) (all updated to the corrected production/verification tier framing). Post-design Constitution re-check: PASS (Q2 resolved via committed ADR-046, not deferred).

## Complexity Tracking

| Item | Why needed | Finding |
|---|---|---|
| **Deterministic populator + pipeline sequencing step** (AD-1) | FR-2 deterministic value MUST be written into `threats.md` by a non-LLM component before SARIF authoring sources it; no caller of `parse_component_asset_map` exists today | **The PRD/team-lead "1-2 line at an existing site" premise is FALSE** — §3.5 is LLM prose, not an executable join. This is net-new infra + a new pipeline-sequencing step. Simpler alt = Design B (LLM value) → relaxes FR-2, PM-declined. |
| **Three production LLM authoring-contract updates** | Production `.sarif` is LLM-authored; the Python scripts are not live | `sarif-specification.md` + `risk-scorer.md` SARIF section must emit the copied property; the rev-1 component list (treating scripts as emitters) omitted these — now added. |
| **Thin ADR-046** | Production-tier modifies live agent SARIF-authoring contracts | Architect criterion: production-tier → require thin ADR (≈046). Field alone would be no-ADR. |

## Risks (delta from PRD §Risks)

Inherits PRD R1–R7. **New/elevated**:
- **R8 (NEW, HIGH-likelihood) — production surface materially exceeds the PRD's ~1–2 day NFR-7 envelope**: deterministic populator + new pipeline-sequencing step + 3 LLM authoring-contract edits + ADR-046 + regeneration-script wiring + tests + baselines + CI + docs + credit. Realistic effort ~3–4 working days. *Impact: MEDIUM (effort/scope, not correctness/value).* **Mitigation**: still within the 06-11 ceiling's 6 working-days slack (team-lead PRD-stage CALENDAR PASS); **team-lead MUST re-scope at `/aod.tasks` from the corrected premise** (PM M-1 hand-off); NFR-7 "re-scope, don't expand silently" honored; Design B is the PM+Architect fallback if the ceiling is threatened.
- **R9 (NEW) — "shipped, adopters see nothing"** (architect Pre-Mortem #1): if only the regeneration scripts are wired and the production authoring sites are missed, baselines pass green but the live `tachi.threat-model` emits no `affected_assets`. **Mitigation**: the production authoring sites are now first-class Components; quickstart §3/§5 must verify against a **live agent run**, not only `pytest`.
- **R2 (held, structural mitigation in the verification tier)** — two-emitter drift caught by the single `parse_affected_assets` extractor + SC-006 multi-finding equality; in production, both SARIFs copy the one `threats.md` block value.
- **R3 (held)** — frozen-logic scope creep: SC-011 binary diff on `risk-scoring.yaml` + `tachi_parsers.py`; populator is READ-ONLY against `parse_component_asset_map`.
