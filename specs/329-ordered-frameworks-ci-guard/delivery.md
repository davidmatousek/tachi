# Delivery Retrospective — Feature 329: ORDERED_FRAMEWORKS Catalog-Drift CI Guard

**Closed**: 2026-06-30 · **PR**: #344 (squash-merged `38a8ceb`) · **Release**: v4.46.0 (release-please PR #341) · **Tasks**: 16/16
**Initiative**: BLP-06 Wave 2 — CI-hardening tail **lead** (P1) · **Branch**: `329-ordered-frameworks-ci-guard` (deleted at merge)

---

## What shipped

A CI guard that recomputes a deterministic **render-coupled fingerprint** — the ordered `[id, out_of_scope]` record list, in both raw and in-scope partitions — for every live `ORDERED_FRAMEWORKS` catalog member (owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe) by **reusing the renderer's own loader** (`_load_framework_yaml_records`) via `importlib`, and reddens CI when any member drifts from a committed sidecar without a CA-baseline regeneration. It renders nothing and hits no network (NFR-001) — closing the silent-red-on-`main` gap (the F-186→F-185 path; KB-15) that the unwired 6-PDF byte-identity suite left open, **without** the cost/flakiness of wiring full Typst rendering into CI.

### User stories (all 4 delivered + independently proven)
- **US1** — catch drift-without-regen → CI fails naming the framework, expected→actual fingerprints + counts, and the regen entry point (covers F-186 grow, HIGH-2 constant-count ID-swap, HIGH-3 `out_of_scope` flip).
- **US2** — don't false-red on count-neutral edits (the #333 citation-string class stays green).
- **US3** — guard the trunk: dual-trigger (`pull_request` + `push:[main]`) reddens direct-to-main drift (#338 lesson reused).
- **US4** — future-member coverage is automatic (derives its target set from the tuple at runtime; zero guard-code change).

### Key deliverables
- `scripts/check-catalog-drift.py` — fingerprint core + fail-closed sidecar I/O + `--check`/`--emit` CLI.
- `scripts/regenerate-ca-baselines.sh` — formalized CA-baseline regen; emits the sidecar as its FINAL step (cheat-resistance).
- `examples/ca-baseline-fingerprints.json` — the committed fingerprint sidecar (regen-emitted, never hand-edited).
- `tests/scripts/test_catalog_drift_guard.py` — 15 cases (live gate + grow/swap/flip catch + #333/non-member/clean ignore + dynamic future-member + fail-closed quartet).
- `.github/workflows/tachi-catalog-drift.yml` — dual-trigger, single `ubuntu-latest`, `contents: read`, single-source `&drift_paths` anchor.
- ADR-037 **D-14** (new decision; D-9 body byte-unchanged) + CHANGELOG + KB CI-backstop annotation.

---

## Delivery metrics

| Metric | Value |
|--------|-------|
| Estimate (plan) | 1.5 eng-days (floor 1.0 / ceiling 3.0) |
| Actual | Same-day — PRD → plan → build (W1–W3) → deliver (W4) all 2026-06-30, ~2 sessions |
| Variance | Favorable — landed near the floor; the OQ-3 green pre-state avoided the ceiling-day baseline-remediation tail |
| Tasks | 16/16 across 4 waves |
| Build-wave tests | W1 1/1 · W2 11/11 · W3 15/15 · 0 regressions (3/4 waves tested; W4 no code change) |

---

## Surprise log

The guard's first-ever **live CI fire on PR #344 passed green on the first attempt** — the A2 `pip install pyyaml` step closed the silent-no-op failure mode, and there was no path-filter typo or runner surprise. The OQ-3 pre-state byte-identity suite was already green (13 passed / 1 documented skip), so **no baseline remediation was needed** and the build never engaged the ceiling-day variance driver (the FR-2 regen lane). Clean, scope-disciplined execution end-to-end.

---

## Lessons learned

**(Pattern / Architecture)** A *render-coupling fingerprint guard* is a cheap, deterministic backstop for an expensive/flaky byte-identity check: reuse the renderer's **own** record loader (via `importlib`) so the guard's notion of "what the page depends on" is the renderer's by construction, and **emit the expected-value sidecar as the FINAL step of the regeneration script** so the expected fingerprints cannot be advanced without a genuine regen (cheat-resistance). This converts a manual define-time checklist (KB-15) into a CI-enforced invariant without rendering anything in CI. → KB Entry 19.

---

## Test evidence

### Build-Wave Test Results
| Wave | Tests | Passed | Failed | Status |
|------|-------|--------|--------|--------|
| wave-01 | 1 | 1 | 0 | pass |
| wave-02 | 11 | 11 | 0 | pass |
| wave-03 | 15 | 15 | 0 | pass |

**Build Summary**: PASSED — 27/27 test-executions passed across 3 tested waves (final module 15 distinct cases), 0 regressions. (W4 = acceptance + deliver, no code change → not test-executed.)

### Acceptance (T015 — quickstart negative probes, live tree)
- Probe-1 (record `id` rename) → `--check` **exit 1** naming `cwe`, fingerprint `88103f8e…→46b27d13…` (constant-count ID-swap, HIGH-2), regen entry-point printed; reverted clean.
- Probe-2 (url-only citation edit) → `--check` **exit 0** (the #333 count-neutral property); reverted clean.

### Gates & reviews
- **Security Scan**: PASSED — 4 files SAST, 0 findings; SCA skipped (0 manifests). Evidence in `.security/` + `security-scan.md`.
- **Economy Gate**: PASSED — no over-build (exemplary rung-2 loader reuse, stdlib-only, 0 new deps).
- **Design Gate**: Skipped — no UI files.
- **Architect final**: APPROVED (0 blocking, 0 new concerns).
- **Code review final**: APPROVED_WITH_CONCERNS (0 critical / 0 warning / 3 suggestion). Deferred **S-1**: a hand-corrupted non-dict sidecar *member* crashes `find_drift` instead of routing through `SidecarError` — fails closed (CI still reddens) and unreachable via the sanctioned `--emit` path; optional one-line hardening filed as a follow-up.
- **CI on PR #344**: all 5 checks green (guard check, gitleaks ×2, init.sh macos + ubuntu).

---

## How to see & test it

```bash
python3 scripts/check-catalog-drift.py            # exit 0 = clean; exit 1 = drift (+ stderr message)
scripts/regenerate-ca-baselines.sh                # regen the 6 CA baselines + emit the sidecar (local only; needs typst)
python3 -m pytest tests/scripts/test_catalog_drift_guard.py -q   # 15/15
```
The workflow `.github/workflows/tachi-catalog-drift.yml` runs the guard automatically on every PR and every push to `main`.

---

## Definition of Done (constitution VII) — CLOSED

1. ✅ **Pushed to Production** — `feat(329)` squash-merged to `main` (`38a8ceb`), post-green, via the deliver gate; v4.46.0 release PR open.
2. ✅ **Tested** — `test_catalog_drift_guard.py` 15/15 green in the dedicated dual-trigger workflow.
3. ✅ **User Validated** — quickstart negatives (drift caught / citation-only ignored); sidecar emitted by the regen script; guard green on the clean tree.
