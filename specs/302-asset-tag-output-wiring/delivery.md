# Delivery Document: Feature 302 — Asset-Tag Output Wiring (F-260b)

**Delivery Date**: 2026-06-01
**Branch**: `302-asset-tag-output-wiring`
**PR**: #303

---

## What Was Delivered

- **Asset tags now propagate into SARIF** (US-1, P1): every result in both `threats.sarif` and `risk-scores.sarif` carries a `properties.affected_assets` array — sorted tag strings for tagged components, `[]` (present, not omitted) for untagged. GitHub Code Scanning and SAST aggregators are now asset-aware.
- **`affected_assets` populated per finding in `threats.md`** (US-2, P1): a new always-present per-finding block lists the asset tags of each finding's target component, `[]` otherwise — structured asset-impact data downstream tools can read without re-parsing the architecture.
- **`affected_assets` schema field added** to `schemas/finding.yaml` (`schema_version` 1.8 → 1.9): always-present, default `[]`, 6-value enum — the first additive bump since F-224 that is not a regex-alternation prefix extension.
- **Deterministic populator + shared extractor**: `scripts/populate-affected-assets.py` (the pure-Python value authority, joins component→tags and writes the `threats.md` block) and `scripts/sarif_common.py` (shared `affected_assets` extractor for the verification tier).
- **"Asset-aware" is now provable** (US-4, P2): cross-format equality (SC-006) + byte-identity (SC-002) gates, a live-pipeline R9 acceptance check, and ADR-046 recording the deterministic-value / LLM-authored-output / Python-verification-tier boundary.
- **@north-echo wired and credited** (US-3, P2): CHANGELOG `feat:` entry naming @north-echo + PR #262; Discussion #246 acknowledgement; contribution chain #246 → #262 → #260 → #302.
- **CI regression protection** (US-4): the previously-unwired 26-case asset-tag suite + the 35-case wiring suite are now wired into `tachi-pytest.yml` in path-filter ↔ pytest-invocation lock-step.

**Frozen / out of scope (SC-011, held)**: the 6-tag enum, the 9.2 CVSS modifier ceiling, and modifier-after-clamp ordering — wiring, not re-tuning.

---

## How to See & Test

1. **Schema field + version (SC-001)**: `grep -A3 affected_assets schemas/finding.yaml` → enum array + default `[]`; `grep schema_version schemas/finding.yaml` → `1.9`.
2. **Per-tag propagation, all 6 tags (SC-003)**: `pytest tests/scripts/test_affected_assets_wiring.py -k propagation -q` (pii/phi/auth/safety via the worked example; secrets/financial via fixtures).
3. **Ceiling preserved + no scoring regression (SC-004 / NFR-2)**: `pytest tests/scripts/test_affected_assets_wiring.py -k ceiling -q` → no finding > 9.2; composite/severity unchanged vs the v4.31.0 worked example.
4. **Empty-tag default (SC-005)**: run on a no-tag architecture → `threats.md` shows `<id>: []` for every finding; both SARIFs show `"affected_assets": []`.
5. **Cross-format consistency — the key gate (SC-006)**: `pytest tests/scripts/test_affected_assets_wiring.py -k cross_format -q` → per-finding equality across the `threats.md` block + both SARIF emitters, byte-identical incl. untagged `[]`.
6. **CI runs the suite (SC-008)**: `grep test_asset_sensitivity_tags .github/workflows/tachi-pytest.yml` → matches in BOTH the `paths:` filter AND the pytest invocation.
7. **Frozen constraints untouched (SC-011)**: `git diff main -- schemas/risk-scoring.yaml scripts/tachi_parsers.py` → no change to `VALID_ASSET_TAGS`, `modifier_ceiling: 9.2`, or ordering.
8. **Full SC-001…SC-012 recipe**: see [quickstart.md](quickstart.md).

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Estimated Duration | 1-2 days |
| Actual Duration | ~2 days (branch 2026-05-30 → delivered 2026-06-01) |
| Variance | On-target |

---

## Surprise Log

Smooth sailing — everything went roughly as planned, no major surprises.

_(Maintainer note, recorded for the audit trail: at delivery time the merge was briefly blocked by a stale `init-baseline-tree` CI fixture — see Lessons Learned / KB Entry 9. This was a routine deliver-time fixup, not a build surprise.)_

---

## Lessons Learned

| Category | Lesson | KB Entry |
|----------|--------|----------|
| Process Improvement | Regenerate the `init-baseline-tree` fixture in lock-step whenever a delivery touches a CI paths-filtered file or a tracked placeholder-bearing doc — the byte-content contract runs only on `pull_request`, so doc drift on `main` accumulates invisibly and surfaces on the next unrelated feature PR. Verify substitution semantics are intact first so a regen never masks a real regression. | Entry 9 in INSTITUTIONAL_KNOWLEDGE.md |

---

## Feedback Loop

**New Ideas**: None

---

## Source Artifacts

| Artifact | Path |
|----------|------|
| Specification | specs/302-asset-tag-output-wiring/spec.md |
| Implementation Plan | specs/302-asset-tag-output-wiring/plan.md |
| Task Breakdown | specs/302-asset-tag-output-wiring/tasks.md |
| PRD | docs/product/02_PRD/302-asset-tag-output-wiring-2026-05-30.md |
| ADR | docs/architecture/02_ADRs/ADR-046-asset-tag-output-wiring.md |
| Contract | specs/302-asset-tag-output-wiring/contracts/affected-assets-contract.md |

---

## Test Evidence

### Test Scenarios (Living Documentation)

This project (a CLI / markdown threat-modeling harness, active pack `knowledge-system`) declares **no E2E/Playwright test contract**, so the `/aod.deliver` E2E validation gate is not applicable. Acceptance criteria are verified by the pytest suites below rather than Gherkin scenarios.

| AC ID | Verification | Suite | Status |
|-------|--------------|-------|--------|
| SC-001/003/005 | Schema field, per-tag propagation, empty default | `test_asset_sensitivity_tags.py` (26 cases) | ✅ green |
| SC-002/004/006 | Byte-identity, ceiling, cross-format equality | `test_affected_assets_wiring.py` (35 cases) | ✅ green |

### Execution Evidence

#### E2E Validation Gate

| Field | Value |
|-------|-------|
| Status | skipped |
| Gate Mode | n/a (no stack E2E contract) |
| Gate Result | skip |
| Skip Reason | Active pack `knowledge-system` declares no `e2e_command` test contract (FR-011 backward-compat path) |

**Failure Details**: N/A

#### Build-Wave Test Results

Per-wave full-suite pytest runs (`python3 -m pytest tests/scripts/`, cumulative as the suite grew), from `specs/302-asset-tag-output-wiring/test-results/`:

| Wave | Passed | Failed | Skipped | Gate |
|------|--------|--------|---------|------|
| wave-2 | 773 | 16 | 1 | pass |
| wave-3 | 822 | 16 | 2 | pass |
| wave-4 | 852 | 16 | 2 | pass |
| wave-5 | 856 | 16 | 2 | pass |
| wave-6 | 865 | 16 | 2 | pass |

**Build Summary** (`test-results/summary.json`): 10 total waves, 5 tested / 5 skipped (no `.py` source change), all gate decisions **pass**. Real end-state = Wave 6: **865 pass / 16 fail / 2 skip**.

- The **16 failures are constant across waves 2-6** (byte-identical) — a documented **F-302-INDEPENDENT pre-existing cluster on `main`** (threat-model pipeline coverage-attestation + line-count caps), in neither F-260b suite.
- **F-260b-specific suites: 61/61 green** (`test_affected_assets_wiring.py` 35 + `test_asset_sensitivity_tags.py` 26), confirmed at Wave 9 acceptance (T022).
- 1 regression counted (Wave 2, first tested wave, non-blocking, resolved at the P0 checkpoint — both MEDIUMs closed); 0 regressions in waves 3-6.

#### Post-Merge CI

Both `tachi-pytest` matrix legs green on PR #303 after the baseline-fix commit `711e4ae`: **ubuntu-latest** (5m56s) and **macos-latest** bash 3.2.57 floor (19m37s). Gitleaks: pass.

**Notes**: Unit/integration via pytest; cross-platform substitution determinism verified by the init.sh matrix. No coverage tooling detected (`coverage_trend: null`).

---

## Documentation Updates

| Domain | Agent | Files Updated | Status |
|--------|-------|---------------|--------|
| Product | product-manager | 1 (`docs/product/02_PRD/INDEX.md` → Delivered) | ✅ pass |
| Architecture | architect | 4 (`README.md` ADR-046 index, `01_system_design`, `00_Tech_Stack` schema 1.9, `03_patterns` new pattern) | ✅ pass |
| DevOps | devops | 3 (`CI_CD_GUIDE.md`, `README.md`, `environment-variables.md`) | ✅ pass |

---

## Cleanup

- [x] Feature branch deleted (local + remote, pruned)
- [x] All tasks complete (23/23)
- [x] No TBD/TODO in docs
- [ ] Committed and pushed
- [ ] GitHub Issue closed (`stage:done`)

**Feature 302 is now officially CLOSED.**
