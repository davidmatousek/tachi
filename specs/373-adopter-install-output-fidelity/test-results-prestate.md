# T001 — W0 Pre-State and Group B Oracle Pre-Snapshot

**Feature**: 373-adopter-install-output-fidelity
**Task**: T001 (W0, `/aod.build` wave 1)
**Agent**: `senior-backend-engineer` instance SBE-B
**W0 commit**: `0ce39d0` (`0ce39d033357f6315221bb70f2db8c1f1effe86e`, 2026-09-27 21:42:51 -0400)
**Executed**: all pytest and extractor runs below ran in a **scratch clone**, never the main tree (standing rule / #365). Only this document was written directly into the main tree.

**Timing**: work started 2026-09-28T01:46:00Z, ended 2026-09-28T02:22:00Z (wall clock, this session; see S5 for the per-phase breakdown).

---

## S0. Environment

Scratch clone: `git clone --no-hardlinks /Users/david/Projects/tachi "$SCR"`, where
`$SCR = /private/tmp/claude-501/-Users-david-Projects-tachi/5f109275-e25c-4be3-ac01-c337226261e5/scratchpad/w0-t001/tachi`.
Verified `git -C "$SCR" rev-parse --short HEAD` = `0ce39d0`, `git -C "$SCR" status --short` = empty, immediately after cloning and again after every run below.

| Tool | Version |
|---|---|
| python3 | 3.12.11 |
| pytest | 9.1.0 |
| pytest-timeout | 2.4.0 |
| PyYAML | 6.0.3 |
| typst | 0.14.2 (unknown hash) |
| mmdc (mermaid-cli) | 11.12.0 |
| OS | Darwin 25.6.0 arm64 (macOS, `Picard.local`) |

All commands below were run with `cwd = $SCR` unless stated otherwise.

---

## S1. Pre-state: literal pass/fail/skip/error totals

### (a) The four fast-workflow modules, run individually

Command (repeated per module):
```bash
python3 -m pytest tests/scripts/<module>.py -v
```

| Module | Result | Duration | stderr bytes |
|---|---|---|---|
| `test_tachi_parsers.py` | 7 passed | 0.03s | 0 |
| `test_extract_infographic_data.py` | 37 passed | 1.94s | 0 |
| `test_extract_report_data.py` | 25 passed | 10.69s | 0 |
| `test_extractor_contract_fixes.py` | 6 passed | 0.03s | 0 |

Subtotal: **75 passed, 0 failed, 0 skipped, 0 errors.** No reds.

### (b) `test_executive_architecture_payload.py` (N4)

```bash
python3 -m pytest tests/scripts/test_executive_architecture_payload.py -v
```

Result: **12 passed** in 0.52s. 0 stderr bytes. No reds.

### (c) `tachi-pytest.yml`'s current 16-module invocation (local macOS leg)

Run with the exact module list and flags from `.github/workflows/tachi-pytest.yml` (lines 191-208 at this commit):

```bash
python3 -m pytest \
  tests/scripts/test_init_sh_substitution.py \
  tests/scripts/test_init_sh_adversarial.py \
  tests/scripts/test_init_sh_constitution.py \
  tests/scripts/test_init_sh_self_delete.py \
  tests/scripts/test_template_substitute_unit.py \
  tests/scripts/test_init_input_unit.py \
  tests/scripts/test_substitute_shim_canary.py \
  tests/scripts/test_init_sh_defaults_env.py \
  tests/scripts/test_template_config_load_unit.py \
  tests/scripts/test_template_config_load_integration.py \
  tests/scripts/test_template_git_clone_timeout.py \
  tests/scripts/test_template_substitute_lint_no_eval.py \
  tests/scripts/test_init_precommit_matrix.py \
  tests/scripts/test_asset_sensitivity_tags.py \
  tests/scripts/test_affected_assets_wiring.py \
  tests/scripts/test_owasp_2026_contract.py \
  -v --timeout=1080
```

Result: **181 passed, 1 skipped, 1 xfailed** in 691.09s (0:11:31). 0 stderr bytes. Exit 0.

- The 1 skip: `test_init_precommit_matrix.py:164`, "Case 4 (TTY x no-flag default-Y) requires real TTY simulation via `pty.openpty()`... T017 covers this scenario via manual empirical verification." Pre-existing, documented skip.
- The 1 xfail: `test_init_sh_substitution.py::test_personalized_tree_bytes_match_baseline`, marked `strict=False`, with an inline note dating the staleness to before v4.44.0 (`6b3481e`), tracked under #345. Pre-existing, documented xfail.
- This run took 11m31s wall clock on this dev machine (workflow header comments anticipate ~9-12 min cold-cache on macOS runners; consistent).

Subtotal: **181 passed, 0 failed, 1 skipped, 0 errors, 1 xfailed** (183 collected). No reds.

### (d) The N4 ungated set: ~20 parser/extractor-consuming modules

**Derivation (reproducible).** Run from the scratch clone root:
```bash
grep -lE "tachi_parsers|extract[-_]infographic[-_]data|extract[-_]report[-_]data" tests/scripts/test_*.py | sort
```
This pattern covers all five forms named in the task (`tachi_parsers`, `extract-infographic-data`, `extract_infographic_data`, `extract-report-data`, `extract_report_data`) via one extended regex. It matched **31 files**. Removing the 4 modules already counted in (a), the 1 already counted in (b), and the 3 that overlap with (c)'s 16-module list (`test_asset_sensitivity_tags.py`, `test_affected_assets_wiring.py`, `test_owasp_2026_contract.py`) leaves **23 modules** — "roughly 20" per the task's own framing, and it includes every example module named in the task prompt (`test_source_attribution.py`, `test_finding_pattern_parser.py`, `test_project_name_parser.py`, `test_attack_chain_extraction.py`).

**Full N4 module list, each run individually** (`python3 -m pytest tests/scripts/<module>.py -v`):

| Module | Result | Duration |
|---|---|---|
| `test_attack_chain_extraction.py` | 27 passed | 2.40s |
| `test_attack_chains.py` | 26 passed | 0.05s |
| `test_backward_compatibility.py` | 6 failed, 6 passed, 2 skipped | 16.71s |
| `test_catalog_drift_guard.py` | 16 passed | 0.55s |
| `test_coverage_attestation.py` | 16 passed | 1.23s |
| `test_coverage_attestation_in_scope.py` | 3 failed, 16 passed | 0.58s |
| `test_coverage_attestation_pagination.py` | 5 passed | 2.42s |
| `test_coverage_attestation_tiers.py` | 7 passed | 0.02s |
| `test_coverage_percentage_computation.py` | 48 passed | 0.94s |
| `test_finding_pattern_parser.py` | 59 passed, 5 warnings | 0.05s |
| `test_human_trust_exploitation.py` | 1 failed, 24 passed, 8 errors | 0.09s |
| `test_maestro_coverage_invariant.py` | 9 passed, 2 skipped | 0.03s |
| `test_maestro_cross_surface_consistency.py` | 2 passed | 0.12s |
| `test_mmdc_preflight.py` | 8 passed | 0.05s |
| `test_pattern_classification_rules.py` | 15 passed | 0.04s |
| `test_pattern_extraction.py` | 33 passed | 0.05s |
| `test_pattern_synthesis.py` | 39 passed | 0.07s |
| `test_pdf_page_positioning.py` | 2 passed | 20.94s |
| `test_project_name_parser.py` | 16 passed | 0.14s |
| `test_pyyaml_deferred_import.py` | 1 failed, 10 passed | 0.09s |
| `test_smoke.py` | 1 passed | 0.01s |
| `test_source_attribution.py` | 9 passed | 0.03s |
| `test_tool_abuse_enrichment.py` | 3 failed, 14 passed | 0.08s |

Wall clock for the whole loop (23 separate pytest invocations, process-startup overhead included): 2026-09-28T01:58:23Z -> 01:59:13Z (50s).

Subtotal: **408 passed, 14 failed, 4 skipped, 8 errors** (434 collected across 23 modules).

### Grand total across (a)-(d)

**677 passed, 14 failed, 5 skipped, 8 errors, 1 xfailed = 705 collected test items** (75+12+183+434, minus zero overlap — no module is counted twice; (c)'s 3 overlapping modules were excluded from the (d) list before counting).

---

## S2. Every red: node id and one-line cause

All 22 reds are in the N4 set (d); (a), (b) and (c) are 100% green. None of these are attributable to Feature 373 — no F-373 code has landed yet at `0ce39d0`.

| # | Node id | Type | One-line cause |
|---|---|---|---|
| 1-6 | `test_backward_compatibility.py::test_unmodified_examples_byte_identical_pdfs[web-app\|microservices\|ascii-web-api\|mermaid-agentic-app\|free-text-microservice\|maestro-reference]` | FAILED (x6) | PDF byte mismatch vs the committed `.pdf.baseline` despite `SOURCE_DATE_EPOCH=1700000000`; first divergence is inside an embedded font subset tag (e.g. baseline `ZZMJWG+...SFNS-Regu...` vs generated `SPUEUJ+...SFNS-Regu...`). Font-subset-tag / Typst-toolchain drift on this machine vs whenever the baselines were captured; pre-existing, unrelated to F-373. |
| 7-9 | `test_coverage_attestation_in_scope.py::TestStream4CoveragePercentage::test_aggregator_matches_expected_fixture[findings_in_scope_only\|findings_oos_only\|findings_mixed]` | FAILED (x3) | Fixture expects `mitre-atlas.yaml_record_count == 30`; the catalog has 36 records (grew 30->36 per BLP-05 #186, 2026-06-07). Stale fixture constant; pre-existing, unrelated to F-373. |
| 10 | `test_human_trust_exploitation.py::test_no_agp_te_prose_synthesis` | FAILED | Asserts `examples/consumer-agent-app/test-output/2023-11-14T22-13-20-F4-wave5/threat-report.md` exists; that directory is an untracked local artifact from another feature's manual Wave-5 run and is not visible to (or reproducible in) a fresh scratch clone. |
| 11-18 | `test_human_trust_exploitation.py::test_wave5_te_count_is_five`, `test_wave5_source_attribution_present`, `test_wave5_primary_is_owasp_asi09`, `test_wave5_cwe_451_absent_from_source_attribution[CWE-451]`, `test_wave5_mitre_atlas_absent_from_source_attribution`, `test_wave5_external_regulatory_absent_from_source_attribution`, `test_wave5_source_attribution_resolves_against_catalog`, `test_wave5_no_trust_exploitation_agentic_pattern` | ERROR (x8) | Same missing untracked `.../F4-wave5/threats.md` directory as #10 (fixture/setup error, not an assertion failure). |
| 19 | `test_pyyaml_deferred_import.py::test_yaml_import_is_function_scoped[check-citation-urls.py]` | FAILED | `scripts/check-citation-urls.py:44` has a module-level `import yaml`, violating the KB-037 / F-241 stdlib-only-at-import invariant. Pre-existing, unrelated to F-373. |
| 20 | `test_tool_abuse_enrichment.py::test_tool_abuse_line_count_within_cap` | FAILED | `.claude/agents/tachi/tool-abuse.md` is 152 lines; cap is 150 (ADR-023 AI tier). Pre-existing 2-line overage, unrelated to F-373. |
| 21 | `test_tool_abuse_enrichment.py::test_categories_1_8_byte_identity_against_main` | FAILED | `subprocess.CalledProcessError`: `git show main:.claude/skills/tachi-tool-abuse/references/detection-patterns.md` exits 128. **Scratch-clone-recipe artifact, not a code defect**: a plain `git clone` of a local repo currently checked out on a feature branch creates a local branch only for that branch, plus remote-tracking refs (`remotes/origin/main`, etc.) for everything else — there is no local `main` ref to `git show` against. Confirmed by checking the main tree itself, where `git rev-parse --verify main` resolves fine. A real CI checkout of a PR branch would face the same absence unless it separately fetches/creates a local `main`; this is a pre-existing property of the test, not introduced by F-373. |
| 22 | `test_tool_abuse_enrichment.py::test_validate_source_attribution_on_regen` | FAILED | Asserts at least one `[NEW]`-tagged `AG-{N}` finding in the committed `examples/agentic-app/sample-report/threats.md`; none present at this commit. Expects a manual-regen state that is not currently checked in; pre-existing, unrelated to F-373. |

---

## S3. stderr capture and warning classes ((a)-(d))

Every one of the 29 pytest invocations in S1 (4 + 1 + 1 + 23) captured **0 bytes of stderr**. Nothing in this bundle's pre-existing test suite writes to the OS-level stderr stream.

One pytest **warnings summary** (a pytest-reporter feature, printed to stdout, not stderr) appeared, in exactly one module:
- `test_finding_pattern_parser.py`: **5x `PytestRemovedIn10Warning`** — "Class-scoped fixture defined as instance method is deprecated" (`_pytest/fixtures.py:1312`, pytest 9.1's forward-compat deprecation warning about a `TestParseThreatsFindings*` class using an instance-method fixture). Pre-existing, unrelated to F-373; no other module in (a)-(d) or (c) produced a warnings summary.

---

## S4. Group B oracle pre-snapshot (quickstart.md S3)

### Tracked example directories (12)

```bash
git ls-files 'examples/**/threats.md' | sed 's#/threats\.md$##' | sort
```
->
```
examples/agentic-app
examples/agentic-app/sample-report
examples/agentic-app/test-output/2026-03-25T12-53-57
examples/ascii-web-api
examples/consumer-agent-app/sample-report
examples/free-text-microservice
examples/maestro-reference
examples/mermaid-agentic-app
examples/microservices
examples/mobile-banking-app/sample-report
examples/predictive-ml-app/sample-report
examples/web-app
```
12 directories, matching the expected count. Slugs (strip `examples/`, replace `/` with `__`): `agentic-app`, `agentic-app__sample-report`, `agentic-app__test-output__2026-03-25T12-53-57`, `ascii-web-api`, `consumer-agent-app__sample-report`, `free-text-microservice`, `maestro-reference`, `mermaid-agentic-app`, `microservices`, `mobile-banking-app__sample-report`, `predictive-ml-app__sample-report`, `web-app`.

### Run list: 12 dirs x 7 (6 infographic templates + `report-data.typ`) = 84 runs

Per directory: `extract-infographic-data.py --target-dir D --template T --output OUT/<slug>/T.json` for T in {baseball-card, system-architecture, risk-funnel, maestro-stack, maestro-heatmap, executive-architecture}, plus `extract-report-data.py --target-dir D --template-dir templates/tachi/security-report --output OUT/<slug>/report-data.typ`. Each run's stderr captured beside its output (`OUT/<slug>/<T>.stderr`, `OUT/<slug>/report-data.stderr`).

**Exit codes: 84/84 exit 0.** The illustrative "executive-architecture exits 2 without scope data" case named in the task did **not** occur among these 12 tracked directories at `0ce39d0` — every committed example carries scope data (all 12 executive-architecture runs show `metadata.skip_image: false`, full payload, no early-exit).

### Normalization rules

1. **N1 (`generation_timestamp`)**: any dict key literally named `generation_timestamp` (present only in the executive-architecture template's `metadata` block; absent from the other 5 templates, which instead carry a content-derived `scan_date`) has its value replaced with the literal string `<normalized>`. Confirmed by the double-run diff (below) to be the **only** field that actually changes value between two runs of the same input.
2. **N2 (absolute paths through `/tachi/`)**: any string value (a JSON string, or anywhere in a `.typ`/`.stderr` file's text) containing an absolute path that runs through a `/tachi/` repo-root segment has that path token rewritten to `<REPO>/<tail>`, keeping only the portion after the last `/tachi/`. This single content-keyed rule (regex `` /[^"\s]*/tachi/ ``, applied with `re.sub`) covers two distinct fields with one mechanism:
   - `metadata.source_file` (JSON, executive-architecture only) and `#let baseline-source = "..."` (`.typ`) / `delta.baseline_source` (JSON, wherever `has_baseline: true`) — an absolute path rooted at whichever machine + clone ran the extractor (this session: `/private/tmp/.../scratchpad/w0-t001/tachi/...`);
   - the same `baseline_source`/`baseline-source` field is *also*, on inspection, a value **copied through verbatim from the committed fixture's own text** (a "compared against" line inside `examples/.../threats.md` itself, written on the original author's machine, e.g. `/Users/david/Projects/tachi/...`). It does not change run-to-run on one machine, but it is not portable across machines/sessions, so it still needs the rule for a pre-vs-post diff to be meaningful.
   - The regex requires the match to start at an actual `/` (never eating a preceding quote or prose word), so a harmless relative-path mention such as the `.typ` file's own boilerplate comment `// --- Image Paths (relative to templates/tachi/security-report/) ---` is correctly left untouched (verified: it does not start a `/.../tachi/` sequence with no intervening space, since the comment's words are space-separated).
3. **N3 (no other rule needed)**: content-derived fields that look like dates or run ids (`scan_date`, `assessment-date`, `baseline-date`, `run_id`, `baseline-run-id`) are parsed from the committed fixture's own frontmatter/prose (verified directly, e.g. `scan_date: "2026-04-27"` matches the literal `date: "2026-04-27"` line in `examples/agentic-app/sample-report/threats.md`) and are stable given unchanged input. The image-path fields in `report-data.typ` (`funnel-image-path` etc.) are already relative (`../../../examples/...`) and carry no machine-specific prefix. The double-run determinism check (below) is the authority that no further rule is needed; none was found empirically for this bundle's fixtures at `0ce39d0`.

### Determinism check

Ran `snapshot.sh` twice against the same scratch clone at `0ce39d0`, into two separate output directories, then diffed:

```
diff -rq "$OUT1/norm" "$OUT2/norm"    # exit 0, zero output -> byte-identical
```

`diff -rq` on the **raw** (pre-normalization) trees, by contrast, shows exactly **12 differing files** — the 12 `executive-architecture.json` raw outputs (one per example dir), and nothing else. This confirms both halves of the design: `generation_timestamp` is the only field that is genuinely volatile run-to-run, and it only appears in the executive-architecture payload; every other field (including `baseline_source`/`baseline-source`) is stable across repeated runs of the same input on the same machine. **No residual nondeterminism found.**

### stderr warning-class counts across the 84 runs

Total stderr captured: 18,753 bytes across 84 files. Aggregated by distinct line (`find raw -name '*.stderr' -exec cat {} \; | sort | uniq -c`) and attributed by directory (`grep -rl "<line>" raw | sort -u`):

**Warning-class lines** (prefixed `Warning:`), fully attributed:

| Class | Count | Source dir(s) |
|---|---|---|
| `could not find Recommended Actions table in threats.md` | 14 | `consumer-agent-app__sample-report` (7 runs) + `predictive-ml-app__sample-report` (7 runs) |
| `<ID> in '### <Band> Residual Severity' section but residual score <X> maps to <Band2>. Using score-derived band.` (7 distinct finding IDs: S-1, R-1, I-4, D-5, D-4, D-3, D-2) | 7 each (49 total) | `predictive-ml-app__sample-report` only, all 7 runs (one occurrence of each of the 7 lines per run) |
| `<N> findings in wrong severity sections (corrected using score-derived bands)` (summary of the row above) | 7 | `predictive-ml-app__sample-report` only, all 7 runs |
| `could not find severity distribution in risk-scores.md` | 2 | `consumer-agent-app__sample-report/risk-funnel` (1) + `maestro-reference/risk-funnel` (1) |
| `could not find Risk Summary table in threats.md` | 1 | `maestro-reference/risk-funnel` |

All five classes are pre-existing data-shape properties of these committed fixtures (severity-heading/score-band mismatches, missing optional tables) at `0ce39d0` — none are caused by, or expected to change because of, F-373's code. They are recorded here as the oracle's pre-state baseline per L8 (T035/N7 attribution).

**Informational (non-`Warning:`) lines**, not warning classes, included for completeness: per-run "Prompt scaffold extracted...", "Tier N selected, parsing artifacts...", "...generated (N findings, Tier T[, template=...])", "Coverage attestation: gate=...", "Attack trees: N ... extracted", "Attack chains: N ... extracted" — one line per run reporting that run's own finding/tier/count, not a cross-run class.

### Storage

- Raw: `$SCRATCH/oracle/pre/raw/<slug>/{<template>.json,<template>.stderr,report-data.typ,report-data.stderr}` (72 JSON + 12 `.typ` + 84 `.stderr` files).
- Normalized: `$SCRATCH/oracle/pre/norm/...` (same layout).
- Manifest: `$SCRATCH/oracle/pre/run-manifest.txt` (repo_dir, out_dir, head=`0ce39d0`, dir_count=12, started/finished timestamps), `$SCRATCH/oracle/pre/all-exits.txt` (84 lines), `$SCRATCH/oracle/pre/nonzero-exits.txt` (empty file — 0 nonzero exits).
- Determinism-check second run: `$SCRATCH/oracle/pre-determinism-check2/...` (same layout; kept for this session only, not required by any later task).
- Nothing under `$SCRATCH/oracle/` is committed. Only this document is.

---

## S5. Timing

| Phase | Start (UTC) | End (UTC) | Duration |
|---|---|---|---|
| Setup: scratch clone, tool versions | 01:46:00 | 01:46:41 | ~41s |
| S1(a) four fast-workflow modules | 01:46:41 | ~01:47:00 | ~13s combined |
| S1(d) grep derivation + 23 N4 modules | 01:58:23 | 01:59:13 | 50s |
| S1(c) 16-module CI-parity invocation | 01:47:21 | 01:58:52 | 691s (11m31s) — ran in background while S1(d) work was prepared |
| S4 oracle pre-snapshot, run 1 | 02:06:03 | 02:06:44 | 41s |
| S4 oracle pre-snapshot, run 2 (determinism) + diff | ~02:07 | ~02:08 | ~1 min |
| Investigation (reds, warning attribution, doc authoring) | ~02:08 | 02:22:00 | ~14 min |
| **Total wall clock** | **01:46:00** | **02:22:00** | **~36 min** |

---

## Appendix: `snapshot.sh` (full text)

Self-contained; takes `REPO_DIR OUT_DIR`. T035 can re-run this unmodified at the W0 SHA (or any later commit) to regenerate a comparable snapshot, as long as `REPO_DIR` is a tachi checkout (a scratch clone, never the main tree) with `scripts/`, `templates/` and `examples/` present, and `python3` on `PATH`.

```bash
#!/usr/bin/env bash
# =============================================================================
# snapshot.sh REPO_DIR OUT_DIR
#
# Self-contained Group B oracle snapshot for Feature 373 (T001, quickstart.md
# S3). Reproduces:
#   1. the raw extractor run (both extractors x 12 tracked example dirs x 6
#      infographic templates + 1 report-data run = 84 runs),
#   2. the stderr capture alongside each raw output,
#   3. the normalization pass (run-specific fields blanked / rewritten).
#
# Usage:
#   snapshot.sh REPO_DIR OUT_DIR
#     REPO_DIR - path to a tachi working tree (a scratch clone, never the main
#                tree) checked out at the commit to snapshot.
#     OUT_DIR  - directory to receive raw/, norm/, run-manifest.txt and
#                nonzero-exits.txt (created if absent; must not pre-exist
#                populated from an unrelated run).
#
# T035 (a later session) re-runs this unmodified at the W0 SHA to regenerate
# the pre-snapshot if the original scratchpad is gone. It requires only
# REPO_DIR to be a tachi checkout with scripts/, templates/ and examples/
# present, and python3 on PATH. No other state is assumed.
#
# Safety: this script only ever writes under REPO_DIR's own --output targets
# (which this script points at OUT_DIR, never at REPO_DIR/examples) and under
# OUT_DIR. It never writes into REPO_DIR/examples, so it never re-renders the
# tracked example PNGs (#365) even though it reads examples/**. REPO_DIR
# should still always be a scratch clone per the standing rule, never the
# main tree, so that any future change to this script cannot regress that.
# =============================================================================
set -euo pipefail

REPO_DIR="${1:?usage: snapshot.sh REPO_DIR OUT_DIR}"
OUT_DIR="${2:?usage: snapshot.sh REPO_DIR OUT_DIR}"

RAW="$OUT_DIR/raw"
NORM="$OUT_DIR/norm"
mkdir -p "$RAW" "$NORM"

TEMPLATES="baseball-card system-architecture risk-funnel maestro-stack maestro-heatmap executive-architecture"

cd "$REPO_DIR"

# Discover every TRACKED examples/**/threats.md directory (untracked
# test-output runs are out of scope; the scratch clone doesn't see them
# anyway). Sorted for a deterministic run order.
DIRS=$(git ls-files 'examples/**/threats.md' | sed 's#/threats\.md$##' | sort)
DIR_COUNT=$(printf '%s\n' "$DIRS" | grep -c .)

{
  echo "repo_dir=$REPO_DIR"
  echo "out_dir=$OUT_DIR"
  echo "head=$(git rev-parse --short HEAD)"
  echo "dir_count=$DIR_COUNT"
  date -u +"started=%Y-%m-%dT%H:%M:%SZ"
} > "$OUT_DIR/run-manifest.txt"

: > "$OUT_DIR/nonzero-exits.txt"
: > "$OUT_DIR/all-exits.txt"

while IFS= read -r D; do
  [ -z "$D" ] && continue
  # Slug disambiguates nested directories: strip the leading "examples/",
  # then replace every remaining "/" with "__".
  SLUG=$(printf '%s' "$D" | sed 's#^examples/##; s#/#__#g')
  mkdir -p "$RAW/$SLUG"

  for T in $TEMPLATES; do
    set +e
    python3 scripts/extract-infographic-data.py \
      --target-dir "$D" --template "$T" \
      --output "$RAW/$SLUG/$T.json" \
      2> "$RAW/$SLUG/$T.stderr"
    rc=$?
    set -e
    echo "$D $T exit=$rc" >> "$OUT_DIR/all-exits.txt"
    if [ "$rc" -ne 0 ]; then
      echo "$D $T exit=$rc" >> "$OUT_DIR/nonzero-exits.txt"
    fi
  done

  set +e
  python3 scripts/extract-report-data.py \
    --target-dir "$D" --template-dir templates/tachi/security-report \
    --output "$RAW/$SLUG/report-data.typ" \
    2> "$RAW/$SLUG/report-data.stderr"
  rc=$?
  set -e
  echo "$D report-data exit=$rc" >> "$OUT_DIR/all-exits.txt"
  if [ "$rc" -ne 0 ]; then
    echo "$D report-data exit=$rc" >> "$OUT_DIR/nonzero-exits.txt"
  fi
done <<EOF
$DIRS
EOF

date -u +"finished=%Y-%m-%dT%H:%M:%SZ" >> "$OUT_DIR/run-manifest.txt"

# ---- Normalization ----------------------------------------------------
# Rules (see prestate doc S4 "Normalization rules" for the human-readable
# list; this is the executable form of the same rules):
#   N1. Any dict key literally named "generation_timestamp" (present only in
#       the executive-architecture payload's metadata block) has its value
#       replaced with the literal string "<normalized>". It is a wall-clock
#       datetime.now() value at run time.
#   N2. Any string value, anywhere (JSON string, or a full line of a .typ or
#       .stderr file), that contains the literal path segment "/tachi/" has
#       everything up to and including the LAST such segment replaced with
#       "<REPO>/". This covers two distinct volatile-path shapes with one
#       rule: (a) metadata.source_file / #let baseline-source, which are
#       absolute paths rooted at whatever machine + clone ran the extractor
#       (e.g. a scratch clone under /private/tmp/...), and (b) baseline
#       comparison paths copied through from committed fixture content that
#       are rooted at the ORIGINAL author's machine (e.g.
#       /Users/david/Projects/tachi/...). Both name-shift across machines/
#       sessions while the tail after "tachi/" (e.g.
#       examples/agentic-app/threats.md) is the portable, comparable part.
#   N3. Nothing else is touched. Content-derived fields that happen to look
#       like dates (scan_date, assessment-date, baseline-date, run_id,
#       baseline-run-id) are parsed from the committed fixture's own
#       frontmatter/prose and are stable run to run given unchanged input,
#       so the double-run determinism check (S4) is the authority on
#       whether any further field needs a rule -- none was found empirically
#       for this bundle's fixtures at the W0 commit.
python3 - "$RAW" "$NORM" <<'PYEOF'
import json
import re
import sys
import pathlib

raw_root = pathlib.Path(sys.argv[1])
norm_root = pathlib.Path(sys.argv[2])

VOLATILE_KEYS = {"generation_timestamp"}

# Matches an absolute path token (starts at the '/', never eats a leading
# quote or preceding prose) that runs through a "/tachi/" repo-root segment.
# Greedy [^"\s]* finds the LAST "/tachi/" if a string somehow had two, which
# is the more conservative (shorter kept tail) choice.
PATH_RE = re.compile(r'/[^"\s]*/tachi/')


def strip_repo_prefix(s: str) -> str:
    """Rewrite every '<abs-path-to>/tachi/' token in s to '<REPO>/'.

    Covers both a scratch-clone-rooted absolute path (this run) and an
    original-author-machine-rooted absolute path (copied through from
    committed fixture content) with one content-keyed rule, and only
    replaces the path token itself -- text before it on the same line
    (e.g. `#let baseline-source = "`) and after it (the relative tail) is
    left untouched.
    """
    return PATH_RE.sub("<REPO>/", s)


def normalize_json(obj):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k in VOLATILE_KEYS:
                out[k] = "<normalized>"
            else:
                out[k] = normalize_json(v)
        return out
    if isinstance(obj, list):
        return [normalize_json(v) for v in obj]
    if isinstance(obj, str):
        return strip_repo_prefix(obj)
    return obj


def normalize_text(text: str) -> str:
    return strip_repo_prefix(text)


for json_path in sorted(raw_root.rglob("*.json")):
    rel = json_path.relative_to(raw_root)
    data = json.loads(json_path.read_text(encoding="utf-8"))
    normalized = normalize_json(data)
    out_path = norm_root / rel
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(normalized, indent=2) + "\n", encoding="utf-8")

for typ_path in sorted(raw_root.rglob("*.typ")):
    rel = typ_path.relative_to(raw_root)
    text = typ_path.read_text(encoding="utf-8")
    out_path = norm_root / rel
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(normalize_text(text), encoding="utf-8")

for stderr_path in sorted(raw_root.rglob("*.stderr")):
    rel = stderr_path.relative_to(raw_root)
    text = stderr_path.read_text(encoding="utf-8")
    out_path = norm_root / rel
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(normalize_text(text), encoding="utf-8")

print(f"normalized {sum(1 for _ in raw_root.rglob('*.json'))} json, "
      f"{sum(1 for _ in raw_root.rglob('*.typ'))} typ, "
      f"{sum(1 for _ in raw_root.rglob('*.stderr'))} stderr files")
PYEOF

echo "snapshot.sh: done. raw=$RAW norm=$NORM"
```

---

## Final git status check (main tree, standing rule 5)

```
$ git -C /Users/david/Projects/tachi status --short
?? specs/373-adopter-install-output-fidelity/test-results-prestate.md
?? specs/373-adopter-install-output-fidelity/test-results/
?? tests/scripts/fixtures/fidelity_373/
?? tests/scripts/install_sh_helpers.py
```

`test-results-prestate.md` is this document. The other three untracked paths are the parallel W0 tasks' own output — T002's `test-results/w0-smoke.md` and T003's fixture builders under `tests/scripts/fixtures/fidelity_373/` and `tests/scripts/install_sh_helpers.py` — not this task's. **No `examples/**` change** appears in the status, confirming the scratch-clone-only rule (standing rule 1) was respected throughout T001: no pytest, extractor or `install.sh` invocation ever ran against the main tree.
