---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-05-30
    status: APPROVED
    notes: "0 BLOCKING / 0 HIGH / 0 MEDIUM / 3 LOW. All 5 spec user stories represented as independently-testable phases; all 12 FRs trace to tasks (NFR-2 score-equivalence in T022; NFR-3 cross-format in T013/T016). Zero scope creep — FR-006 frozen constraints + risk-scoring.yaml 1.2 bump + extra examples + custom vocabularies + PDF/infographic all held OUT (T021 binary gate). Feature-branch/deliver split correct: CHANGELOG feat(302) + @north-echo attribution on-branch (T019); credit tail (FR-011c Discussion ack + Co-Authored-By) + issue closes (FR-012 #246→#262→#260→#302) + release-please verify (FR-010/SC-009) at /aod.deliver. @north-echo framed as PROTOTYPE AUTHOR of PR #262 (never 'surfaced by'), recognition-not-assignment. LOW: L-1 effort note is team-lead-domain; L-2 Design B fallback correctly routed as PM+Architect PRD amendment (PM declined — no Design B task leaked); L-3 US1/US2 phase-order inversion well-documented. Full review .aod/results/product-manager.md."
  architect_signoff:
    agent: architect
    date: 2026-05-30
    status: APPROVED
    notes: "0 BLOCKING / 0 HIGH / 0 MEDIUM / 2 LOW (advisory). Task breakdown faithfully implements architect-approved Design A — AD-1 fidelity 5/5: deterministic populator as value authority (T005) writing the threats.md block; BOTH production LLM authoring-contract edits present and distinct (T011 sarif-specification.md orchestrator→threats.sarif, T012 risk-scorer.md→risk-scores.sarif); pipeline-sequencing step (T006); shared parse_affected_assets extractor (T008) separate from emitter edits (T009/T010); ADR-046 tasked (T003). Dependency chain matches the plan critical path; US-2-before-US-1 honored. All four correctness gates present + wired: SC-006 cross-format (T013), SC-002 byte-identity (T016), SC-011 frozen binary diff (T021), R9 live-pipeline (T018). Frozen-constraint discipline intact (tachi_parsers.py READ-ONLY); NFR-3 test-checked framing consistent — no structural overclaim. LOW folded: LOW-1 T011/T012 authoring-text-vs-runtime note added; LOW-2 shared-test-file serialize-on-write note added + [P] dropped from T017. Full review .aod/results/architect.md."
  techlead_signoff:
    agent: team-lead
    date: 2026-05-30
    status: APPROVED_WITH_CONCERNS
    notes: "0 BLOCKING / 0 HIGH / 2 MEDIUM / 3 LOW — both MEDIUM folded. Constraint Analysis + Systems Thinking lenses. EFFORT RE-VALIDATED FROM THE CORRECTED PREMISE (PM M-1 hand-off): prior PRD-stage ~1-2 day rating WITHDRAWN (the '1-2 line at an existing site' premise was void — §3.5 is LLM prose, not an executable join; parse_component_asset_map has no production caller). Corrected surface (T001-T022: net-new populator + pipeline-sequencing step + 3 LLM authoring-contract edits + ADR-046 + regeneration scripts + tests + baselines + CI + docs + credit) = ~3-4 working days REALISTIC. CALENDAR PASS (independently verified, zero weekend defects): build window 2026-06-01 Mon → 2026-06-11 Thu ceiling = ~9 working days; ~3-4 day effort → ~5 working-days residual slack. Comfortably within ceiling — Design B fallback NOT triggered. Capacity CLEAR (1 draft PR #303, 1 branch, F-1 #296 gate closed). Critical path + granularity + test staffing sound. M-1 (stale '6-working-day slack' framing) FOLDED → corrected to residual ~5 days. M-2 (same-file [P] on T007/T013/T017) FOLDED → [P] dropped from T017 + serialize-on-write note. Cleared for /aod.build. Full review .aod/results/team-lead.md."
---

# Tasks: Asset-Tag Output Wiring (F-260b)

**Input**: Design documents from `specs/302-asset-tag-output-wiring/`
**Prerequisites**: plan.md (dual-approved), spec.md (PM-approved), research.md, data-model.md, contracts/, quickstart.md

**Tests**: INCLUDED — the spec mandates them (FR-9 regression protection; SC-1…SC-7; the existing 26-case suite; SC-6 cross-format equality; SC-2 byte-identity).

**Organization**: By user story (spec US-1…US-5). Phases are ordered by the AD-1 dependency chain — the `threats.md` value foundation (US-2) lands before the SARIF surfaces (US-1) that copy from it. `[Story]` labels map to **spec** US numbers (US1 = SARIF, US2 = threats.md) regardless of phase order.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: spec user story (US1…US5); Setup/Foundational/Polish carry no story label

---

## Phase 1: Setup

**Purpose**: Capture the pre-change reference state needed for the SC-002 byte-identity gate.

- [X] T001 Capture pre-change baseline snapshot of the no-tag example outputs (`threats.md`, `threats.sarif`, `risk-scores.sarif`) under `SOURCE_DATE_EPOCH=1700000000` and confirm `examples/agentic-app/architecture-with-asset-tags.md` carries the expected `pii`/`phi`/`auth`/`safety` tags across 4 components (records the SC-002 "before" for the additive-only diff).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The schema field, the governance ADR, and the `threats.md` block contract — every user story depends on these.

**CRITICAL**: No user-story work begins until this phase is complete.

- [X] T002 [P] Add optional always-present `affected_assets` enum-array field (default `[]`, 6-value enum) to `schemas/finding.yaml`; bump `schema_version` 1.8 → 1.9; add the inline comment per the file convention citing ADR-026/028/037 + PR #262 + always-present-default note + cross-ref to frozen `risk-scoring.yaml` (FR-001).
- [X] T003 [P] Author thin `docs/architecture/02_ADRs/ADR-046-asset-tag-output-wiring.md` recording the LLM-vs-Python tier-boundary decision, production-tier election, the deterministic-value rationale (FR-2 literal), test-checked (not structural) production NFR-3, and the deferred structural ideal (Q2 / plan AD-1).
- [X] T004 [P] Define the always-present per-finding `affected_assets` block contract (new structure — `threats.md` has no detail block; tables stay byte-stable) in `.claude/skills/tachi-shared/references/finding-format-shared.md` and `templates/tachi/output-schemas/threats.md` (FR-003 surface; the contract the populator + extractor + SARIF authors implement).

**Checkpoint**: Schema field + block contract fixed → populator and SARIF work can begin.

---

## Phase 3: User Story 2 — Asset tags populated per finding in threats.md (Priority: P1, value foundation)

**Goal**: The deterministic populator writes the `affected_assets` block into `threats.md`; a downstream consumer reading `threats.md` sees per-finding asset tags. This is the FR-2 value authority US-1 will copy from.

**Independent Test**: Run the pipeline on the tagged worked example → `threats.md` carries an `affected_assets` field on every finding (populated where the component is tagged, `[]` otherwise).

- [X] T005 [US2] Implement the deterministic populator (value authority) in `scripts/` (e.g. `scripts/populate-affected-assets.py`): join `parse_component_asset_map(architecture)` to each finding by target component (same case-insensitive/fuzzy cascade as risk-scorer §3.5), `affected_assets = component_asset_map.get(component, [])` (sorted, verbatim), and write the `affected_assets` block into `threats.md`. Pure function, no LLM, no scoring change (FR-002). Depends on T002, T004.
- [X] T006 [US2] Wire the populator into the production pipeline as a sequencing step that runs **after** the orchestrator emits `threats.md` and **before** SARIF authoring, in `.claude/commands/tachi.threat-model.md` and `.claude/commands/tachi.risk-score.md` (AD-1 M-2). Depends on T005.
- [X] T007 [P] [US2] Unit tests for the populator in `tests/scripts/test_affected_assets_wiring.py`: all 6 tags propagate (SC-003), empty-default `[]` present (SC-005), fuzzy component match, no-op-modifier-with-present-tag still lists the tag (Q4 semantic), sorted/deduped output, `UNCHANGED`/`RESOLVED` findings still carry the field. Depends on T005.

**Checkpoint**: `threats.md` carries deterministic `affected_assets` — US-2 independently testable.

---

## Phase 4: User Story 1 — Asset tags propagate into SARIF (Priority: P1, depends on US-2)

**Goal**: Both SARIF surfaces carry `result.properties.affected_assets` (snake_case) sourced from the single `threats.md` block — GitHub Code Scanning + SAST aggregators see asset-aware findings.

**Independent Test**: SARIF for the tagged example shows `properties.affected_assets` per result (`["phi","pii"]` sorted for tagged components, `[]` for untagged), byte-identical between the two emitters.

- [X] T008 [US1] Add the shared `parse_affected_assets(threats_content) -> dict[finding_id, list[str]]` extractor to `scripts/sarif_common.py` (single source for the regeneration/verification tier; mirrors the `parse_component_metadata` desync-fix precedent). Depends on T004.
- [X] T009 [P] [US1] Add `result.properties.affected_assets` (literal **snake_case** key, flat array — Q3) to `scripts/generate-threats-sarif.py`, sourced from the extractor; do NOT inherit the surrounding key-casing drift (FR-004 verification tier). Depends on T008.
- [X] T010 [P] [US1] Add `result.properties.affected_assets` (snake_case, flat array) to `scripts/generate-risk-scores-sarif.py`, sourced from the extractor (FR-004 verification tier). Depends on T008.
- [X] T011 [US1] Update the production LLM authoring contract in `.claude/skills/tachi-orchestration/references/sarif-specification.md`: orchestrator emits `threats.sarif` `result.properties.affected_assets` (snake_case) copied verbatim from the `threats.md` block (FR-004 production). Depends on T004.
- [X] T012 [US1] Update the production LLM authoring contract in `.claude/agents/tachi/risk-scorer.md` SARIF section: risk-scorer emits `risk-scores.sarif` `result.properties.affected_assets` (snake_case) copied verbatim from the `threats.md` block; **§3.5 scoring + 9.2 ceiling UNCHANGED** (frozen). Depends on T004.
- [X] T013 [US1] Cross-format consistency test (SC-006) in `tests/scripts/test_affected_assets_wiring.py`: multi-finding worked example (≥2 differently-tagged components + ≥1 untagged) asserting a per-finding equality table across the `threats.md` block, `generate-threats-sarif.py`, and `generate-risk-scores-sarif.py` — every finding (incl. untagged `[]`) byte-identical value + identical `affected_assets` key string. Depends on T009, T010.

**Checkpoint**: Both SARIF surfaces carry `affected_assets`; cross-format equality enforced.

---

## Phase 5: User Story 4 — "Asset-aware" is provable, not aspirational (Priority: P2)

**Goal**: The schema-doc surface accurately documents the contract, baselines regenerate additive-only, and a live pipeline run proves end-to-end propagation.

**Independent Test**: Schema doc matches emitted output; baseline diff is additive-only; a real `tachi.threat-model` run on the worked example shows tags in all three surfaces.

- [X] T014 [P] [US4] Extend `.claude/skills/tachi-risk-scoring/references/asset-modifiers.md` with an "Output Contract" section (enum, empty-default, per-format representation) **and correct the stale "9.5" in the T-2 worked example to the frozen `9.2`** (FR-007, Q7). Must NOT touch `schemas/risk-scoring.yaml`. Depends on T004.
- [X] T015 [P] [US4] Add a pointer to the `affected_assets` contract in `schemas/README.md` (FR-007).
- [X] T016 [US4] Regenerate the no-tag example baselines under `SOURCE_DATE_EPOCH=1700000000`; verify `git diff` shows ONLY the additive `affected_assets` block/property, all existing table rows byte-identical (SC-002, AD-2). Depends on T005, T006, T011, T012.
- [X] T017 [US4] Schema-doc accuracy test (SC-007) + ceiling-preservation test (SC-004: a tagged finding clamps at 9.2, `affected_assets` populated regardless) in `tests/scripts/test_affected_assets_wiring.py` (serializes on the shared test file with T007/T013 — not `[P]`). Depends on T014.
- [X] T018 [US4] Live-pipeline verification (R9 / architect Pre-Mortem #1): run the real `tachi.threat-model` on `examples/agentic-app/architecture-with-asset-tags.md` and confirm `affected_assets` appears in `threats.md`, `threats.sarif`, AND `risk-scores.sarif` — not just the regeneration scripts. `[MANUAL-ONLY] live LLM-pipeline run requires a human/agent invocation, not a unit test`. Depends on T006, T011, T012. **RESULT**: run1 surfaced a live-authoring sequencing defect (orchestrator self-authored the block, mis-assigned S-7 → 1/69 cross-format mismatch); fixed in-scope (T023, Option B); run2 live re-verification PASS — threats.sarif 3-way-equal to the deterministic block (0 mismatches, 20 tagged findings correct). risk-scores.sarif flow verified already correctly sequenced. See `.aod/results/tester-t018.md`.

- [X] T023 [US4] **Remediation (discovered by T018's R9 gate)**: fix the threat-model production sequencing so the deterministic `affected_assets` populator runs BEFORE `threats.sarif` is authored (Option B — in-scope wiring fix; makes the approved AD-1 "populator authors the block → SARIF copies it verbatim" flow actually work). Adds orchestrator Phase 3.7 (populator at the Phase 3→4 boundary, both Phase 3.6 exit paths routed through it, self-authoring forbidden); makes `tachi.threat-model.md` Step 2 imperative + ordered; verifies `tachi.risk-score.md` already correctly sequenced. Markdown/authoring-contract only — frozen files (`risk-scoring.yaml`, `tachi_parsers.py`, `populate-affected-assets.py`) untouched; no scoring change. See `.aod/results/sbe-t018-fix.md`.

**Checkpoint**: Contract documented + baselines clean + live propagation proven.

---

## Phase 6: User Story 3 — @north-echo wired and credited (Priority: P2)

**Goal**: The CHANGELOG attribution lands on the feature branch; the public acknowledgment chain completes at delivery.

**Independent Test**: CHANGELOG names @north-echo as PR #262's prototype author (never "surfaced by") and references Discussion #246.

- [X] T019 [US3] Add the `CHANGELOG.md` `feat(302):` entry — `feat(302): wire asset-sensitivity tags through finding IR + threats.md + SARIF (F-260b)` — with the @north-echo attribution line (prototype author of PR #262, NEVER "surfaced by"; credit is recognition, not a work assignment — declined follow-on) referencing Discussion #246 (FR-010 + FR-011a/d). Reuse the trailer `Co-Authored-By: Christopher Lusk <122107484+north-echo@users.noreply.github.com>` on the feature commit.

> **Delivery-time (`/aod.deliver`, not feature-branch tasks)**: FR-011c Discussion #246 acknowledgment comment + offered `Co-Authored-By`; FR-012 close Issue #302 (cite PR + release + credit URL) and parent #260 (link F-260b PR + credit @north-echo) — completing the #246 → #262 → #260 → #302 chain.

---

## Phase 7: User Story 5 — Release cadence restored (Priority: P3, delivery-time)

**Goal**: The feature ships `feat:`-eligible and triggers a release, restoring the cadence F-1 (#296) broke.

**Independent Test**: `feat(302):` squash-merge → release-please PR opens within ~30s.

> **Delivery-time (`/aod.deliver`)**: ensure the PR title is `feat(302): …`; after squash-merge verify a release-please PR opens within ~30s (`gh pr list --state open --search "release-please"`); if absent, push a `feat(302):` release-marker (FR-010 / SC-009, per `feedback_aod_deliver_release_gate.md`). The CHANGELOG `feat:` entry is delivered in T019. No feature-branch code task.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: CI protection, frozen-constraint gate, full validation.

- [X] T020 [P] CI wiring (FR-008): add `tests/scripts/test_asset_sensitivity_tags.py` (existing 26-case suite — 23 defs + 1 parametrize → 26) AND `tests/scripts/test_affected_assets_wiring.py` to BOTH the `paths:` filter and the `pytest` invocation in `.github/workflows/tachi-pytest.yml` (lock-step — Entry 3 / F-256 lesson). Also added the source surfaces (`populate-affected-assets.py`, `sarif_common.py`, `schemas/finding.yaml`) to `paths:` so the suite triggers on F-260b code changes; YAML validated, lock-step audited (both files in paths + invocation).
- [ ] T021 Frozen-constraint gate (SC-011): verify `git diff main -- schemas/risk-scoring.yaml scripts/tachi_parsers.py` shows NO change to `VALID_ASSET_TAGS`, `modifier_ceiling: 9.2`, the modifier-after-clamp ordering, or `risk-scoring.yaml` `schema_version` (stays 1.1).
- [ ] T022 Run full `quickstart.md` validation (SC-001…SC-012); confirm the 26-case suite + `test_affected_assets_wiring.py` are green in CI; NFR-2 score-equivalence vs the v4.31.0 worked example holds.

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (P1)**: no deps — start immediately (the SC-002 "before" snapshot).
- **Foundational (P2)**: T002/T003/T004 independent (different files) — parallel. Blocks Phases 3–8.
- **US-2 (Phase 3)**: after Foundational. The value foundation.
- **US-1 (Phase 4)**: after Foundational; T008 needs T004; SARIF emitters (T009/T010) need T008; SC-006 (T013) needs T009/T010. **Logically downstream of US-2** (SARIF copies the `threats.md` block), though the script-tier wiring can proceed once T004 fixes the contract.
- **US-4 (Phase 5)**: T016 baseline regen needs the populator + production authoring (T005/T006/T011/T012); T018 live run needs T006/T011/T012.
- **US-3 (Phase 6)** + **US-5 (Phase 7)**: CHANGELOG (T019) any time after wiring; rest is `/aod.deliver`.
- **Polish (Phase 8)**: after the tests/files they reference exist (T020 needs T007/T013/T017; T021/T022 after all wiring).

### Critical Path
T002/T004 → T005 (populator) → T006 (pipeline wiring) → T011/T012 (production SARIF authoring) → T016 (baseline regen) + T018 (live verify) → T022 (full validation). T013 (SC-006 cross-format) is the correctness gate; T021 (SC-011) is the frozen-constraint gate.

### Parallel Opportunities
- **Foundational**: T002 (schema) ∥ T003 (ADR) ∥ T004 (block contract).
- **US-1 emitters**: T009 (threats-sarif) ∥ T010 (risk-scores-sarif) after T008.
- **US-4 docs**: T014 (asset-modifiers) ∥ T015 (schemas/README). T017 may run alongside T014/T015 (different files) but **serializes on the shared `test_affected_assets_wiring.py`** against T007/T013 — hence not `[P]`.
- **CI**: T020 can proceed once the test files exist.

---

## Parallel Example: Foundational Phase

```bash
Task: "Add affected_assets field + 1.9 bump to schemas/finding.yaml"        # T002
Task: "Author thin ADR-046 in docs/architecture/02_ADRs/"                    # T003
Task: "Define affected_assets block contract in finding-format-shared.md + threats.md template"  # T004
```

## Implementation Strategy

### MVP (US-2 then US-1)
1. Setup + Foundational (schema + ADR + block contract).
2. **US-2** — deterministic populator + pipeline wiring → `threats.md` carries tags (downstream-consumer value). **STOP & VALIDATE** (T007).
3. **US-1** — extractor + both SARIF surfaces + production authoring → code-scanning value. **STOP & VALIDATE** (T013 cross-format).
4. **US-4** — docs + baseline regen + live verify (the "provable" gate).
5. CHANGELOG (US-3 T019) + CI (T020) + frozen gate (T021) + full validation (T022).
6. Credit chain + release verify complete at `/aod.deliver` (US-3 tail + US-5).

### Effort note (R8 / team-lead — re-validated)
Per plan R8, the production surface (deterministic populator + pipeline-sequencing step + 3 LLM authoring-contract edits + ADR-046 + regeneration scripts + tests + baselines + CI + docs + credit) is **~3–4 working days** — larger than the PRD's ~1–2 day NFR-7 framing (the "1-2 line at an existing site" premise was void: §3.5 is LLM prose, not an executable join). **Team-lead re-validated from the corrected premise**: the build window 2026-06-01 (Mon) → 2026-06-11 (Thu) ceiling = ~9 working days; the corrected ~3–4 day effort leaves **~5 working-days residual slack** — comfortably within the ceiling. Design B fallback NOT triggered.

---

## Notes
- [P] = different files, no incomplete-task dependency.
- `[Story]` maps to **spec** US numbers (US1 = SARIF, US2 = threats.md); phase order follows the dependency chain.
- Frozen constraints (6-tag enum, 9.2 ceiling, modifier-after-clamp ordering, `risk-scoring.yaml`) are READ-ONLY — SC-011 gate (T021).
- Commit after each task or logical group; the draft PR (#303) shows progress.
- Production NFR-3 is baseline/test-checked (SC-006 + SC-002), not structural — the live-pipeline gate (T018) is what proves adopters see `affected_assets`.
- **Shared test file**: T007, T013, T017 all extend `tests/scripts/test_affected_assets_wiring.py` (append-only, different phases). The build agent MUST treat it as **serialize-on-write** — do not run these concurrently despite differing logical deps (team-lead M-2 / architect LOW-2).
- **Authoring-text vs runtime (T011/T012)**: T011/T012 edit the LLM authoring-contract *text* (they need only T004's block contract to know what to copy). Their *runtime* correctness — that the block exists for the LLM to copy — is verified downstream by T016 (baseline) + T018 (live run). So nothing ships unverified (architect LOW-1).
