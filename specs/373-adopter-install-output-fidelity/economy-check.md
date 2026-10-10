# Economy Gate — Feature 373

**Step**: `/aod.build` Step 8, Economy Gate (advisory, judgment-based, diff-scoped)
**Date**: 2026-10-10
**Diff**: `63438d7...276dd28` (branch `373-adopter-install-output-fidelity`, draft PR #375)
**Scope**: 17 changed code files, after the pinned Step-8 exclusions (docs, `.aod/`, `specs/`, config including `.github/workflows/*.yml`, and lockfiles):
- 4 scripts: `scripts/install.sh`, `scripts/tachi_parsers.py`, `scripts/extract-infographic-data.py`, `scripts/extract-report-data.py`;
- 2 Typst templates: `templates/tachi/security-report/{cover,main}.typ`;
- 11 test files: `tests/scripts/install_sh_helpers.py` plus 10 `test_*.py` modules.

**Method**: a code-reviewer dispatch, applying the laziness ladder and the carve-out-survival check in `.claude/rules/code-economy.md`.
- It reuses the T036 economy observations (`.aod/results/code-reviewer-373.md`; the `target_is_dir` suggestion).
- It adds a fresh pass: a reference and unused-parameter scan of every changed Python file, a caller analysis of new parameters, and a scratch-only probe of the 3-tier funnel.

**Verdict**: Findings: 2 advisory

## Findings

| File | The lower rung that applied | Suggested reduction |
|---|---|---|
| `tests/scripts/install_sh_helpers.py` | **Rung 1 / rung 7** (the spec does not require it; nothing speculative). `add_symlink` (`:257`, `:275`) and `add_nested_symlink` (`:285`, `:297`) accept a `target_is_dir` parameter and `del` it at once ("documents intent only"). Three call sites pass `target_is_dir=False` to no effect (`test_install_sh_symlink_preflight.py:271`, `:285`, `:1003`). Separately, a 44-line `__all__` (`:35-78`) has no consumer: no test uses `import *`, it is the only `__all__` under `tests/`, and 16 of its 41 names are used only inside the module. | Drop the parameter, both `del` lines and the three keyword arguments. Delete `__all__`; the module docstring and the `_` prefixes already mark the API. About −55 lines, with no behavior change. This carries forward T036's SUGGESTION, which P1 also left unfiled. |
| `scripts/extract-infographic-data.py` (the K11 funnel) | **(a) Rung 1** (no caller requires it). `compute_risk_funnel`'s `rs_content` parameter (`:1411`) feeds only `_funnel_3tier_mode`'s re-parse fallback (`:1671-1672`). That fallback is unreachable: `main()` (`:2311-2313`) is the sole caller, and at tier 2 it always passes the parsed list, since `parse_risk_scores_findings` never returns `None`. No test calls either function directly. The fallback exists for "any other caller", and there is none. **(b) Rung 6** (can it be one line?). In 3-tier mode V3 is V2 by construction (data-model §4.1). So the `_funnel_width(W2·V3/V2, …)` branch (`:1696-1702`) always returns its own else value, W2 − STEP = 80, and the (1→2) reduction (`:1728`) is always `0.0`. The data-model's reduction table states that literally: "3-tier mode: `0.0` (V3 = V2)". A scratch probe over 2,005 inputs gave widths (90, 80, 70) and 0.0 in every case. | (a) Have `_funnel_3tier_mode` take the parsed `rs_findings` only, and drop `rs_content` and its docstring paragraphs from both signatures. (b) In 3-tier mode, emit `w3 = w2 - STEP` and `0.0 if volumes_available else None`, with a one-line comment citing §4.1. About −15 lines. Behavior-neutral: identical JSON, so no golden moves. |

Neither finding touches shipped behavior. Both are good candidates for the `/aod.document` code-simplification pass, not for an in-loop fix at final-gate time.

## Carve-out check (code-economy §1): no carve-out shortened

- **Input validation: strengthened.**
  - `install.sh` resolves physical roots with failure-checked `cd -P` and adds identity-based project-root containment (`[ -ef ]`). It classifies every destination link, keeps the 32-hop ceiling, and splits prefixes by parameter expansion only (SEC-K3-02). The default is deny: without the flag, it refuses.
  - `parse_score` now rejects NaN and Infinity, which `float()` used to let fall through to "Low", and never raises.
  - Placeholder IDs are dropped explicitly.
- **Error handling: strengthened.**
  - The `--version` restore trap is loud on failure (it was `2>/dev/null || true`) and preserves the exit code.
  - M-1's silent exit 141 is gone. The new installer-cli constraint row bounds the two remaining early-exit readers (`install.sh:386`, `:514`), and their writers are bounded by the fixed 5-entry `DEPRECATED_COMMANDS`.
  - Stale report data panics in both `main.typ` and `cover-page` (L-6) instead of rendering a default "LOW RISK".
  - Every K11/K12/K13.1 degradation prints an aggregated stderr warning.
  - Two reviewed cases are not carve-out losses. Removing the legacy "misclassified" warning was ratified at P0 (§1.4); the score-derived band stays authoritative. The 3-tier mode's `AOD-SIMPLIFICATION` marker records an accepted ceiling, and a degenerate input yields null volumes (unavailable), never wrong numbers.
- **Security: holds.**
  - No secrets anywhere in the diff.
  - The Gemini key is header-only per NFR-5.
  - `--follow-symlinks` is opt-in, and even with it the installer never deletes through a link.
- **Accessibility: not affected.** The cover badge keeps its prior colors; only the label's source moved, from Typst to `report-data.typ`.
- **One runnable check: holds.** Every K-item has gated tests. Each of the 12 T036 fixes has a test that is red before its fix, and the M-1 pair is red deterministically after `9c15a3b`.

## Passed (no over-build)

- **`install.sh`.** The resolver, `phys_dest` and `under` exist because NFR-3 rules out `readlink -f` and `realpath`. `under` uses the native `-ef` operator. The copy loop is unmodified: `cp` and `mkdir -p` already write through a link, which is the native rung.
- **`tachi_parsers.py`.** Stdlib `Decimal`, and a data-model-specified alias table and classifiers. `classify_control_status` replaces two copies of the old row idiom.
- **`extract-report-data.py`.** The composites join appears in both extractors: two instances, below the Rule of Three, and AR-3 keeps them local. `_merge_delta_status` stays a two-line delegate because an existing test calls it.
- **`compute_allow_list`.** Applies the ladder explicitly (AR-3: local, not a shared helper).
- **Typst.** Net-negative on the cover: the in-template rubric (−22 lines) gives way to data-driven parameters.
- **Tests.**
  - Per-module importlib loaders follow the repo's 11-module convention; conftest has no loader fixture.
  - The two zero-call helpers in `test_install_manifest_completeness.py` are module fixtures.
  - Test-module sizes follow the contract-enumerated cases: the installer harness list, A1–A11, and the sibling-parity set.
- **Pre-dispositioned, not re-litigated.** The N8 bare-marker fallback (kept by L14). The exec-arch builder's optional posture parameters (M-2: an existing test calls it positionally).

Full review record: `.aod/results/code-reviewer-373-final.md` (local, gitignored; the substance is reproduced above).
