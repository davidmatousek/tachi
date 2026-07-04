# T001 — Precondition Sanity Check

**Date**: 2026-07-03
**Branch**: `295-f292-verification-runs`
**Purpose**: Verify pre-verified facts (plan.md / research.md D-A..D-E) still hold at execution time, before any US1/US2/US3 work begins. Per quickstart.md Stage 1.1.

---

## 1. Anchor Extraction (corrected filter)

**Command**:
```bash
git show 0629fa2~1:examples/agentic-app/sample-report/threats.sarif \
  | jq '[.runs[0].results[] | select(.partialFingerprints["findingId/v1"] // "" | startswith("OI-"))] | map(.partialFingerprints["findingId/v1"])'
```

**Verbatim output**:
```json
[
  "OI-1",
  "OI-2",
  "OI-3",
  "OI-4"
]
```

**Cardinality check** (`... | length`): `4`

**Result**: MATCH — exactly `["OI-1","OI-2","OI-3","OI-4"]`, cardinality 4 as required. Gate PASS (contracts/oi-extraction-contract.md §2 false-pass guard satisfied).

### Anchor commit resolution

**Command**: `git rev-parse 0629fa2~1`

**Verbatim output**:
```
3f107e3f1e5ffa37efa40793629136b34f2b4cea
```

**Result**: MATCH — expected `3f107e3...`, resolved to `3f107e3f1e5ffa37efa40793629136b34f2b4cea`.

---

## 2. Tooling Availability

**Command**: `jq --version; python3 -m pytest --version; python3 --version`

**Verbatim output**:
```
jq-1.7.1-apple
pytest 9.1.0
Python 3.12.11
```

**Result**: PASS — `jq` present (1.7.1-apple); `pytest` 9.1.0 satisfies `>=8` requirement; Python 3.12.11.

---

## 3. Branch Currency with Origin

**Command**: `git fetch origin && git status -sb`

**Verbatim output**:
```
From https://github.com/davidmatousek/tachi
 * [new tag]         v4.46.0    -> v4.46.0
## 295-f292-verification-runs...origin/295-f292-verification-runs
 M docs/product/_backlog/BACKLOG.md
```

**Result**: PASS — branch `295-f292-verification-runs` tracks `origin/295-f292-verification-runs` with no ahead/behind divergence (no `[ahead N]` / `[behind N]` markers). One pre-existing uncommitted working-tree change noted: `docs/product/_backlog/BACKLOG.md` (auto-regenerated timestamp from an unrelated `/aod.status` invocation — not a T001 concern, not touched by this task, out of scope per tasks.md "Do NOT modify any other file"). No divergence from HEAD relevant to the F-248/F-256 clone-HEAD harness (`tests/scripts/` paths untouched).

---

## Overall T001 Verdict

**STATUS: PASS** — all four preconditions hold. Proceeding to T002 (pre-state suite).
