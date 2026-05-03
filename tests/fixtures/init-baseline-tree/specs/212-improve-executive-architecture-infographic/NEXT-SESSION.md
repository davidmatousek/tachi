# Session Continuation: Feature 212 — Improve Executive-Architecture Infographic

**Generated**: 2026-04-25 (post Wave 3)
**Branch**: `212-improve-executive-architecture-infographic` (synced to origin; draft PR #213 OPEN)
**Last Commit**: `0046213` docs(212): T010 SC-212-1 review — absolute structural 4/4 PASS, comparative deferred

## Completed This Session

Wave 3 (US1 visual validation + US2 implementation) complete with caveats.

| Wave | Tasks | Key commits | Outcome |
|------|-------|-------------|---------|
| 3 — Lane 3A (US1 visual) | T009, T010, T011 | `48d904e`, `bb9cf12`, `0046213` | T009 iteration-1 image regenerated (626 KB JPEG; 5 callouts; layer_overflow rendered correctly); T010 absolute structural review 4/4 PASS, side-by-side comparison deferred (OpenClaw asset missing); T011 PDF byte-identity zero diff (SHA-256 match) |
| 3 — Lane 3B (US2 impl) | T016, T017, T018, T019, T020 | `c575894`, `f311a30`, `ab8018c` | LRM allocator landed (27/27 tests green; 0 regressions); spec triage Path 4 + re-baselined SC-212-8 gate; defensive perf-hygiene caching fix retained |

**Cumulative**: Waves 0-3 complete. **22 / 37 tasks (59%)**.

### Wave 3 Caveats Requiring P1 PM Sign-off

Two architect-acknowledged caveats are queued for PM sign-off at the **P1 checkpoint** (post Wave 5):

1. **Spec amendment package** (FR-212-8, SC-212-3, Edge Cases) — T019 surfaced a structural conflict between FR-212-8 (≥6 callouts when total qualifying ≥6), FR-212-9 (per-layer ceiling = 4), and SC-212-3 (literal `len(callouts) ∈ [6,7,8]`) on the second-brain-mcp dataset (8+1+0 distribution → algorithmic max = 5 callouts). Architect triage in `specs/212-*/artifacts/architect-spec-triage-t019.md` recommended **Path 4** (reinterpret SC-212-3 as displayed-plus-overflow union; the `layer_overflow` annotation already encodes this design intent). Three additive amendments (A/B/C) drafted; PM sign-off deferred to P1. **No code changes required.** F-128 byte-identity gate (T011) unaffected.

2. **T010 comparative side-by-side review** — Absolute structural review (orchestrator-as-PM-proxy, 2026-04-25) records 4/4 PASS on all four SC-212-1 criteria via direct image inspection of `iteration-1/threat-executive-architecture.jpg`. Comparative side-by-side review against `openclaw-agent-threat-model-infographic.jpg` is BLOCKED on asset availability (asset is not bundled with tachi and not present on the local Mac filesystem). Deferred to human reviewer with OpenClaw access at the P1 checkpoint. **Risk R1 budget retains 2 iterations** if comparative review surfaces structural gaps.

### Wave 3 Methodology Findings

- **SC-212-8 runtime gate methodology**: T020 surfaced that `/usr/bin/time -p` has 10 ms quantization granularity, masking sub-10ms regressions and producing categorical-bucket flips that look like ±33% deltas. Controlled A/B (Wave 1 baseline code re-run today reads 55 ms warm-runs vs post-F-212's 45 ms warm-runs) confirms no actual regression. `runtime-baseline.txt` re-baselined in commit `ab8018c`. For sub-10ms regression detection (Wave 4 onwards), `time.monotonic()` or hyperfine recommended.
- **Defensive caching**: `_qualifying_per_layer(findings, layers)` was being called twice per payload build (once in `_select_critical_high_callouts`, once in `_build_executive_architecture_payload` for `layer_overflow` annotation). Cached + threaded through in `c575894` / `ab8018c` — saves ~16 μs per build (below current measurement floor, but eliminates duplicate work).

### Architect-Recommended Wave-4 Fast-Follow (Concern C2)

Architect triage flagged that the `_F212_L2_FIXTURES` matrix in `tests/scripts/test_extract_infographic_data.py` lacks a fixture that mirrors the second-brain-mcp distribution (8+1+0). **Recommended addition** (Amendment D):

```python
_F212_L2_FIXTURES = [
    ("absent", 0, 0),
    ("single-layer", 2, 1),
    ("two-layer", 5, 2),
    ("three-layer", 9, 3),
    ("all-layers-qualifying", 11, 5),
    ("dominant-layer-skew", 9, 2),  # 8+1+0 — matches second-brain-mcp shape
]
```

The new fixture would assert: `len(callouts) == 5`, Application Layer = 4 callouts (at ceiling), External Layer = 1 callout, Application Layer.layer_overflow = `"+ 4 more in this layer"`. **Suggest adding as a Wave 4 fast-follow task** (or fold into T029 verification).

## Current State

- **Phase**: implement (mid-build at Wave 3 → 4 boundary)
- **Uncommitted**: Clean — all committed and pushed to origin/draft PR #213
- **Tasks**: 22 / 37 complete (59%)
- **Test status (Wave 3 close)**: 366 passed in `tests/scripts/`, 12 failed (all in `test_executive_architecture_payload.py` — these are the Wave 2 / US3 red-bar tests waiting on Wave 4 implementation), 1 skipped. **Zero regressions.**
- **F-128 contracts**: Preserved (T011 PDF byte-identity zero diff verified at HEAD)

## Next Actions (Wave 4 — US3 Implementation)

Wave 4 lands US3 (Level 3 — payload schema extension with `flow_edges[]` and `clusters[]`) and the prompt co-landing in `executive-architecture.md`. 12 US3 red-bar tests in `test_executive_architecture_payload.py` must turn green.

### Lane 4A — US3 Backend (sequential within, parallel with 4B)

| Task | Agent | Description |
|------|-------|-------------|
| T023 | senior-backend-engineer | Add `_TRUST_LEVEL_ORDER` constant reuse / re-declaration in `scripts/extract-infographic-data.py`. Module-scoped for use by `_build_clusters`. No duplication — reuse the existing declaration if accessible (line 715 area). |
| T024 [P] | senior-backend-engineer | New helper `_build_flow_edges(parsed_scope) -> list[dict]`: read `parsed_scope["data_flows"]`; emit one record per entry with fields `source`, `destination` (NOT `target`), `data`, `protocol`; sort `(source.casefold(), destination.casefold())`; truncate to first 50 + log warning if length >50. |
| T025 [P] | senior-backend-engineer | New helper `_build_clusters(parsed_scope) -> list[dict]`: read `parsed_scope["trust_boundaries"]`; emit one record per entry with `name` (from `zone`), `members` (from `components`, sorted case-insensitive), `trust_level` (from `trust-level` via hyphen→underscore rename); sort `(_TRUST_LEVEL_ORDER.get(trust_level, 99), name.casefold())` mirroring `_compute_trust_zones:784`. |
| T026 | senior-backend-engineer | Extend `_build_executive_architecture_payload()` return dict to include `flow_edges` and `clusters` top-level keys. Both MUST always be present (empty list when absent — never `null`). Preserve all existing keys. |

### Lane 4B — US3 Prompt Co-landing (sequential within, parallel with 4A)

| Task | Agent | Description |
|------|-------|-------------|
| T027 | senior-backend-engineer | Update VERBATIM-locked Gemini prompt block in `.claude/skills/tachi-infographics/references/executive-architecture.md` to reference `flow_edges` and `clusters` by name. Instruct directional arrows from `flow_edges[*]` and dashed sub-group boundaries from `clusters[*]`. Remove any prior infer-from-component-names instructions. |
| T028 | senior-backend-engineer | Document new payload schema in same file's §Payload schema — enumerate `flow_edges[]` fields (`source`, `destination`, `data`, `protocol`) and `clusters[]` fields (`name`, `members`, `trust_level`) with sort + empty-semantics notes. Cross-reference data-model.md. |

### Lane 4C — US3 Verify (after 4A AND 4B complete)

| Task | Agent | Description |
|------|-------|-------------|
| T029 | tester | Run `pytest tests/scripts/test_executive_architecture_payload.py -v` — all 12 drift-guard tests MUST go green (currently red-bar from Wave 2). Also run `pytest tests/scripts/test_extract_infographic_data.py -v` — all 27 must still pass (no regression). |
| T030 | senior-backend-engineer (regen) + ux-ui-designer (review) | Regenerate reference image with US1+US2+US3 all landed; save to `specs/212-*/artifacts/final/`; manual review that arrows match `flow_edges[]` and dashed boundaries match `clusters[]`. Record in `sc-212-1-final-review.md`. |

### Wave 4 Gate (PASS conditions)

- T029: all 12 drift-guard tests green; US2 tests still green (no regression).
- T026 verified: payload carries both `flow_edges` and `clusters` top-level keys, always present.
- Field-name lock: `destination` (not `target`); `trust_level` (not `trust-level`); `members` (not `components`).
- Prompt co-landing: `test_prompt_co_landing` from Wave 2 T022 passes.
- T030 visual: arrows + dashed boundaries match payload contents.

### Wave 4 Recommended Fast-Follow (from Architect Concern C2)

Add a new test case `test_per_layer_floor_invariant[dominant-layer-skew]` to the `_F212_L2_FIXTURES` matrix mirroring the second-brain-mcp shape (8+1+0). Lock today's behavior into the test matrix so future regressions are caught.

## Context Files (read first when resuming)

Mandatory reads:
- `specs/212-improve-executive-architecture-infographic/spec.md` — feature spec (PM APPROVED; pending P1 amendments)
- `specs/212-improve-executive-architecture-infographic/plan.md` — implementation plan
- `specs/212-improve-executive-architecture-infographic/tasks.md` — tasks (22 done; pick up at T023)
- `specs/212-improve-executive-architecture-infographic/agent-assignments.md` — wave plan
- `specs/212-improve-executive-architecture-infographic/contracts/payload-schema.md` — producer/consumer contract (US3 critical)
- `specs/212-improve-executive-architecture-infographic/data-model.md` — full payload schema (flow_edges + clusters fields)

Wave-3-specific artifacts (already in repo, relevant for Wave 4):
- `specs/212-improve-executive-architecture-infographic/artifacts/architect-spec-triage-t019.md` — P1 PM-sign-off package
- `specs/212-improve-executive-architecture-infographic/artifacts/sc-212-1-review.md` — T010 partial review (Wave 4 final review at T030)
- `specs/212-improve-executive-architecture-infographic/artifacts/us2-output-spec.md` — US2 payload reference for US3 development
- `specs/212-improve-executive-architecture-infographic/artifacts/runtime-post-us2.txt` — runtime methodology context (re-baselined)
- `specs/212-improve-executive-architecture-infographic/test-results/wave-03/results.json` — Wave 3 test gate baseline for Wave 4 regression comparison
- `tests/scripts/test_executive_architecture_payload.py` — 12 red-bar tests Wave 4 must turn green
- `scripts/tachi_parsers.py:904+` — `parse_scope_data()` producer (T024 reads `data_flows[]`; T025 reads `trust_boundaries[]`)

## Resume Command

```bash
claude "Resume Feature 212 implementation (branch: 212-improve-executive-architecture-infographic, draft PR #213). Waves 0-3 complete (22/37 tasks; 59%). Two P1 PM sign-off items queued: (1) spec amendments A/B/C from architect-spec-triage-t019.md; (2) T010 OpenClaw side-by-side comparative review. Run /aod.build to continue with Wave 4 — US3 implementation (T023-T030: flow_edges + clusters payload schema extension + prompt co-landing + 12 drift-guard tests turning green)."
```

## Environmental notes

- Python: `/Users/david/.local/share/uv/python/cpython-3.12.11-macos-aarch64-none/bin/python3` (3.12.11)
- pytest: `/Users/david/Library/Python/3.9/bin/pytest` (8.4.2)
- typst: `/opt/homebrew/bin/typst`
- GEMINI_API_KEY: set in shell (39 chars) — needed for T030 image regen
- Reference dataset: `~/Projects/second-brain-mcp/docs/security/2026-04-23T23-02-25/`
- OpenClaw reference asset for T030 + deferred T010 review: `openclaw-agent-threat-model-infographic.jpg` — NOT bundled with tachi; local reviewer needs access for the comparative side-by-side
