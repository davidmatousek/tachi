# Architect P1 (Production Cutover) Checkpoint: Feature 373, T036 (second half)

**Reviewer**: architect · **Date**: 2026-10-10 (about 15:20–16:10Z) · **Reviewed at**: `8484a7b`, records-only over `729fa1b`. Re-checked at `9c15a3b` (N-1, test-only), which landed during the review. Branch `373-adopter-install-output-fidelity`, draft PR #375.

## STATUS: APPROVED_WITH_CONCERNS. GO for W4 (T037 ∥ T038).

- **The P1 gate passes, item by item** (§1). **No required changes.** Nothing blocks W4.
- **Is P1 conditional on N-1's CI cycle?** **No, not any more: the condition is met.**
  - **For W4** it never was. W4 is docs only, and N-1 is a test-only commit that cannot move product behavior or the oracle. P1 verified N-1 independently (§1.5).
  - **For `/aod.deliver`** it was conditional until N-1's cycle finished. It finished during this review: **10 of 10 checks are green at `9c15a3b`**. The `tachi pytest` legs finished at 15:47Z (ubuntu) and 16:07Z (macOS) in run 38064601442.
  - The only CI requirement left is deliver's usual one: green at whatever the final tip is. Committing this checkpoint's docs re-runs every workflow, because the PR-level path filter matches.
- **Concerns** (non-blocking):
  1. **More contract drift than L-1 named.** The opt-in report's bracket, the cleanup step's line, the checked-set storage, N8's missing contract pin and N11's missing contract text were all stale. All are amended here (§4). One N11 bullet is still due in `data-model.md` §2.2, which this checkpoint may not edit (§8).
  2. **Release urgency.** The released v4.48.0 names only image models that are now shut down. That has been true since 2026-10-02, so adopters on the current release get no infographic images today (§7.1).
- **Amended**: 4 contracts, 13 edits, each marked "(amended at P1, 2026-10-10)" (§4).
- **Follow-ups**: 7 to file at deliver, 0 driven by trip-wires (§5).

## 0. Rulings at a glance

| # | Item | Ruling |
|---|---|---|
| 1 | CI visibly green | **PASS.** 10 of 10 checks at `729fa1b`, and 10 of 10 at `9c15a3b` (N-1; macOS leg done 16:07Z) |
| 2 | K14 render set | **PASS.** 6/6 on `gemini-3-pro-image`, the fallback model at HTTP 200, and executive-architecture on one portrait page |
| 3 | K15 within two iterations | **PASS on iteration 1.** TW-5 not consumed, TW-6 not fired |
| 4 | `oracle-diff.md` 100% attributed, `agentic-app/sample-report` at 4/0/82 | **PASS.** Independently re-derived at `729fa1b` with P1's own differ |
| 5 | Code review | **APPROVED_WITH_CONCERNS.** 12 of 12 fixed. N-1 is fixed in `9c15a3b` and verified by P1 |
| 6 | N8 (T014) | **Landed as decided.** The contract pin T007 asked for was missing; amended |
| 7 | N11 (T009) | **Landed as decided, and intact** after RC-1, H-1/M-1 and L-1 (code history plus 5 dynamic probes) |
| 8 | RC-1, RC-2, RC-3 | **Closed as specified** |
| 9 | Contract amendments | 13 edits across 4 contracts: L-1 and L-8 as asked, plus drift corrections and records of the T036 fixes. One spec edit is named for the PM |
| 10 | Follow-ups | **File 7.** Not filed: the `target_is_dir` suggestion and the cosmetic Gemini artifacts |

## Evidence base

- **The main tree** was only read: git show/log/diff, grep, Read and `gh`. The only writes were the four contract files and this record. No pytest, extractor or `install.sh` ran there.
- **Scratch** is `…/scratchpad/p1/`.
  - `clone/tachi`: a clone at `8484a7b`, later moved to `9c15a3b`. It stayed clean after every run.
    - At `8484a7b`: the two K3 modules, manifest completeness and `test_gemini_request_contract.py` passed **142/142** on `/bin/bash` 3.2.57.
    - At `9c15a3b`: K3 plus manifest passed **76/76**.
  - `probe/probe.py` (output in `probe/run1/`): N11 ×5 and RC-1 ×3 against the tip's `install.sh`, with snapshot-proven zero writes.
  - `pipe/probe.sh` and `probe2.sh`: the SIGPIPE bound for the cleanup skip check (§4, constraint rows).
  - `oracle/check.py` and `check2.py`: P1's own leaf, line and stderr differ over T035's `pre/norm` (W0) and `final/norm` (`729fa1b`). It does not reuse T035's `analyze.py`.
  - N-1: the two M-1 tests at `9c15a3b`, run against `117b2a3`'s pre-fix installer, 10 runs.

---

## 1. The P1 gate list (agent-assignments §3)

### 1.1 CI is visibly green

**At `729fa1b`, every check succeeded:**

| Check | Run |
|---|---|
| `tachi pytest`, macOS leg (done 15:24Z) and ubuntu leg (done 15:05Z) | 38061641203 |
| `tachi install fidelity`: manifest-completeness, extraction-fidelity, report-posture | 38061641170 |
| `tachi mmdc preflight` | 38061641135 |
| `tachi catalog-drift` | 38061641148 |
| `tachi maestro coverage` | 38061641165 |
| `gitleaks (CI parity)` and the standalone gitleaks check | 38061641160 |

**History.**
- `91e4542` was 10/10 green.
- `f04254c` was red on `tachi pytest` only, on both legs. That was intended: it is RC-1's test-first push (`rc1-test-first.md`).
- `8484a7b` (records only) was pushed during this review.

**At `9c15a3b`** (N-1), the PR head: **10 of 10 green.**
- gitleaks ×2, catalog-drift, maestro coverage, mmdc preflight, and all three install-fidelity jobs.
- Both `tachi pytest` legs (run 38064601442): ubuntu done 15:47Z, macOS done 16:07Z.
- Ubuntu, with bash 5, mawk and a 64 KB pipe, is the leg where N-1's sizing matters most.

**Gated set** (`wave-04/results.json`, `91e4542`): 485 passed, 0 failed, 2 skipped, 0 regressions.
- That is wave 3's 482 plus the three RC tests.
- The 2 skips are pre-existing: a TTY skip and the #345 xfail.

**N4** (`n4-rerun-w3.md`): identical to W0 and W2 (408/14/4/8), with no status flip.
- The only changed signature is still `maestro-reference`'s `/Count 86` → `/Count 88`. It is attributed to K13.1 and intended (P0 §5).
- That signature is byte-identical to W2.

### 1.2 The K14 render set (`k15-renders.md`)

- **6/6 on `gemini-3-pro-image`:**
  - HTTP 200 on the first attempt, `finishReason: STOP`, camelCase keys;
  - 27.09–35.73 s at `imageSize: "2K"`;
  - 2752×1536 at 16:9.
- **The fallback, `gemini-3.1-flash-image`:** HTTP 200 on the first attempt (baseball-card, same `generationConfig`).
- **Executive-architecture on one portrait page.**
  - The image is 1792×2400 (3:4) on **page 14 of 88** of the compiled report, at 612×792 pt (US Letter, portrait).
  - `pdfimages` finds the image object once, so it is not split.
- **No blocked model**, so no P-9.2 or P-10.1 record is needed.
- **2K is kept**: the slowest render, 35.73 s, is under the about-45 s drop threshold.
- **The maintainer's visual check passed** (2026-10-10).
- **Why the K15 renders count for K14.** They double as K14's per-template renders under P-10.2 (a).
- **The fallback's data block was authored independently.** That is acceptable for K14, which tests the request contract and response parsing. The `allow_list` is byte-identical.

### 1.3 K15 within two iterations

- **Iteration 1 passed 6/6.** No layout label was rendered, and every finding ID shown is on that template's `allow_list`.
- **No carve or re-run.** TW-5 was not consumed and TW-6 did not fire. K15 ships as committed (`d0eae8e`, `f57bd37`, `d990f66`, `7f7cd47`, `982c074`). No prompt text changed, so T032 needs no re-run.

### 1.4 `oracle-diff.md`: 100% attributed, independently re-derived

**T035** reports:
- 552 JSON leaves, 544 `.typ` field changes and 18 stderr line classes, all attributed, with 0 unclassified;
- final versus post: 0/0/0 after the T036 fixes (§10, `729fa1b`).

**P1 re-derived it** with its own differ, over T035's W0 pre-snapshot and its `729fa1b` final snapshot:
- **JSON.** 850 changed leaves at full granularity; T035 counted subtrees such as `severity_mix` and ghost objects as one leaf. They fall in exactly T035's 8 classes, with **0 unclassified**:
  - posture: 144;
  - `allow_list`: 72;
  - preamble: 60;
  - funnel tiers;
  - reduction percentages;
  - S-9 scores: 26;
  - `delta_counts`: 20;
  - `top_findings[].delta_status`: 50.
- **The gate figure, exact.** `agentic-app/sample-report` is **4 NEW / 0 UPDATED / 82 UNCHANGED / 0 RESOLVED** in every file that carries it. `agentic-app` is 12 / 0 / 69 / 0.
- **R-b holds.** Executive-architecture JSON moved only in `allow_list` and posture. `metadata.project_name` is unchanged from pre to final on every file.
- **`.typ`.** The per-example line view reconciles to T035's 544 field changes. Each changed findings line can carry both `delta_status` and `recommendation`, so the line counts are lower than the field counts.

  | Example | Added posture lines | Changed lines |
  |---|---|---|
  | `agentic-app/sample-report` | 2 | 149: 85 findings, 62 remediation actions, 2 delta counts |
  | `maestro-reference` | 2 | 158 |
  | `agentic-app` | 2 | 83: 81 `delta_status`, 2 delta counts |
  | `predictive-ml-app` | 2 | 66 |
  | `mobile-banking` | 2 | 2 |
  | Every other example | 2 | 0 |
- **stderr.** +37 / −58 lines, in the same classes as T035 §5. RC-2's effect is exactly P0's prediction: 7 `could not find Scored Threat Table` lines per example, and no "(0)" comparison.

### 1.5 The code review (`.aod/results/code-reviewer-373.md`)

- **Verdict.** APPROVED_WITH_CONCERNS at `729fa1b`. All 12 findings are fixed, each with a test that fails before its fix.
- **N-1 is fixed in `9c15a3b`.**
  - It is test-only: one file, +41/−10. The padded names are about 180 characters longer.
  - **P1's own measurement:**
    - against `117b2a3`'s pre-fix installer, **both** M-1 tests were red in **10 of 10** runs (20 of 20 executions);
    - with the tip's installer restored, K3 plus manifest passed 76/76.
  - The commit's record says 20/20 red and 10/10 green. The ubuntu leg is green at `9c15a3b`.
- **Contract amendments.** Both amendments the review left for P1 (L-1, L-8) are made (§4), along with its optional syncs: the `ENVIRON` row and the `parse_score` "never raises" wording.
- **The `target_is_dir` suggestion:** not taken, and not tracked (§5).

---

## 2. N8 and N11: the formal check (deferred from P0 §7)

### 2.1 N8 (T014, with T007): landed as decided

**The decision** (T007, T014, "decided per L14") has three legs:
- keep the bare `^DATA CONTENT` fallback;
- pin it in a code comment **and in the contract's scaffold note**;
- A8 asserts exactly one line-start `FOOTER` after the marker.

**Each leg:**
- **Code.**
  - The primary marker is line-anchored (`extract-infographic-data.py:178`).
  - The fallback is kept, with its comment (`:181-186`).
  - `FOOTER` is searched for only after the marker line (`:211-212`).
  - Of the 11 commits that touched this file since W0, only `1660c10` (T007) has a `DATA CONTENT` or `FOOTER` hunk.
- **Test.** `test_exactly_one_line_start_footer_after_marker`, ×5 templates, gated in `extraction-fidelity`. It is green in CI and in P1's 142/142.
- **Contract: the gap.** The scaffold note described PD-6's anchoring but never said the fallback is kept. P0 §7's "the contract's scaffold note describes the PD-6 order" was true, but it was not the N8 pin. **Amended now** (§4, items 12 and 13).

### 2.2 N11 (T009): landed as decided, and intact after RC-1, H-1/M-1 and L-1

**The decision** (T008/T009, "decided per L14"):
- for each **directory** entry, refuse when `under "$SRC_P" "$dest"`;
- the always-refused remedy covers moving the clone;
- one test case.

**Code.**
- `install.sh:441-450`. The `elif` at `:447` avoids double-reporting when `dest == SRC_P`, and `:448` prints the line.
- `git log -L` shows that **only `c194946` (T009) ever touched these lines.**

**What the later commits changed in the same function family, and why N11 is unaffected:**

| Commit | What it changed | Effect on N11 |
|---|---|---|
| RC-1 `60f3714` | `resolve()`'s comment and first statement only (`:71-82`) | Its `[ -e ]` guard can make `phys_dest` fail on a whole-path ELOOP. N11 then skips silently, but §2.1 has already refused that link (the RC-1 probe below shows the refusal). No gap |
| H-1/M-1 `b03b834` | The classification loop's two `awk` lines. In the containment loop, a comment only | The containment loop uses no `awk`. `under` is an identity walk, so a `\` in the path is an ordinary character |
| L-1 `f106c9e` | The flag-eligible header, and the combined `die` | N11 lives in the always-refused block, whose header was already exact |

**Test.**
- `test_n11_clone_nested_inside_directory_entry_destination_refused` now proves zero writes with snapshots (L-9, `383140e`).
- It does not assert the bracket text. That stays optional (§4, item 6).

**Dynamic probes at the tip** (`probe/run1/`; each refused case exits 1 with zero writes, link targets included):

| Case | Result |
|---|---|
| Clone inside `.claude/skills/tachi-example/`, no flag | Refused: `[the tachi source clone lies inside this destination]` |
| The same, with `--follow-symlinks` | Refused (no flag remedy) |
| The same, on a project path containing `\`, with the flag | Refused |
| Clone inside a linked `.claude`'s target, no flag | **Both** blocks print, each with `Error: install stopped:` (L-1's combined case) |
| The same, with the flag | Refused by N11 alone |

**Records.**
- Contract: N11's rule and line were missing from `installer-cli.md`. **Amended** (§4, items 3 and 5).
- `data-model.md` §2.2 still lacks N11. That is carried forward (§8).

---

## 3. RC-1, RC-2 and RC-3: closed as specified

| RC | Commits | Evidence | Verdict |
|---|---|---|---|
| **RC-1** (MEDIUM, K3) | Test `f04254c`, fix `60f3714` | See below | **CLOSED** |
| **RC-2** (LOW, K11) | `7cf98f0` | See below | **CLOSED** |
| **RC-3** (LOW, K9) | `7b8a93f` | See below | **CLOSED** |

**RC-1.**
- The test-first push went red on **both** legs at `f04254c`: macOS `mkdir … ELOOP`, ubuntu `cp … ELOOP`.
- The fix makes `[ -e "$p" ] || return 1` the first statement (`:82`). The 32-hop ceiling is kept (`:84`) and the comment is corrected.
- The 21+21 case matches P0's specification: a plain entry first, `--follow-symlinks`, the broken/looping line for `.claude/skills`, and three snapshot sets.
- `bash -n` and shellcheck are clean, and the `x-release-please-version` markers are intact.
- **P1 re-ran P0's 17+17 reproduction at the tip:** refused with and without the flag, with zero writes. The 8+8 control installs (rc 0).

**RC-2.**
- Tier 1 parses `risk-scores.md` once. `risk_scores_row_count` is `None` when the table is absent or unreadable, and the row-count comparison runs only on a readable table.
- Its test pins exactly one `could not find…` line and no "(0)" line. The kitchen-sink 10-vs-11 warning still fires.
- In the oracle, the false "(0)" lines are gone, and 7 lines remain per example.
- L-3 (`e12318b`) extended the single parse to tier 2.

**RC-3.**
- The stop rule is `level <= max(matched_level, 2)`, and the docstring's claim is corrected.
- The pin test shows that a level-1 title gives `[]`. Nothing moved in the oracle, as predicted.

---

## 4. Contract amendments (all marked "(amended at P1, 2026-10-10)")

**`contracts/installer-cli.md`**

1. **RC-1 status.** "Until RC-1 lands, the code lags this text" is replaced by the landed record (`f04254c` red on both legs, then `60f3714`), plus P1's 17+17 re-run.
2. **The checked set, as implemented.** This replaces the stale "`|`-delimited origin string per component".
   - The code keeps TAB-delimited (component, need, origin) lines in `CHECKED_SET` and recovers origins with `awk`.
   - The size at P1 is about 300 lines and 235 unique components, about 30–36 KB.
3. **Destination containment: N11's reverse direction.** The snippet gains the `elif`, limited to directory entries, and a rule paragraph is added. It records why file entries are exempt, why the `elif` is there, the silent skip when `phys_dest` fails, the bracket text, and the P1 probes.
4. **Implementation constraints.**
   - The lead sentence now notes that the new rows were reproduced in T036.
   - **Row: pass shell values to `awk` through `ENVIRON`, never `awk -v`** (H-1).
   - **Row: no early-exit pipe reader on unbounded output under `pipefail`** (M-1). It also records that the failure **fails open** inside an `if`, and lists the two remaining early-exit readers, both on bounded input:
     - the origin string's `head -n 1`;
     - the cleanup skip check's `grep -Fxq` on `SKIP_CLEANUP_FILES`, at most 15 lines (about 0.5 KB) from the fixed five-name list.

     For that producer shape, P1 measured **0 failures in 3,000 runs up to 35 KB, and 300 in 300 from 104 KB**. The row says to re-check if `DEPRECATED_COMMANDS` grows.
5. **Messages.**
   - **L-1:** N11's trigger and its line `[the tachi source clone lies inside this destination]` are added to the always-refused block. In the code since `c194946`, the line had never been in the contract.
   - **L-1:** both header texts are confirmed against the code. `die` adds one `Error:`, and the flag-eligible header gained `install stopped:` in `f106c9e`.
   - **L-1:** the combined case prints the always-refused block, a blank line, then the flag-eligible block **with its own `Error:` prefix**. The exit code is 1.
   - **Drift outside L-1:**
     - A `cleanup-only` line shows `-> '<readlink text>'` when its link doesn't resolve.
     - **The opt-in block has no `[inside | outside project]` bracket.** No commit from `c194946` on has printed it. FR-K3.3 requires only naming each resolved destination, and the summary has no bracket either, so **the contract is amended to match the code, not the reverse** (code-economy rung 1).
     - The cleanup step's per-path `  Skipped cleanup (symlinked path, not deleted): <path>` line is now documented.
6. **Test harness.**
   - RC-1's case is recorded as landed.
   - "Cases added at T036": H-1 (backslash path, both legs), M-1 with **N-1's determinism requirement** (at least 20/20 red before the fix), L-1 and L-9.
   - Optional, not required: assert N11's bracket text, and add one combined-blocks case. Either could ride any later test-only commit.

**`contracts/manifest-completeness.md`**

7. **Workflow wiring (L-8).**
   - `brand/**` and `schemas/**` are added, with why: both are manifest directory entries, and leaving them out let a removal break every adopter install without firing the workflow.
   - The general rule: `&fidelity_paths` must match **every** manifest entry's source. At `8484a7b`, **37 of 37 entries match the 32 patterns** (P1 check).
   - This is the only contract that lists the fast workflow's `paths:`. The other three contracts have no such list.

**`contracts/extraction-data-contract.md`**

8. **`parse_score`:** it never raises, because `AttributeError` is now caught (L-5).
9. **`cover-page` fails closed** (L-6): its parameters default to `none`, and it panics when either is still `none`. So "REQUIRED, no default" holds at both layers.
10. **The S-9 comparand:** it fires when the difference is more than 0.1, compared exactly in `Decimal` (L-4).
11. **The row-count row:** tier 2 also parses `risk-scores.md` once (L-3). Tier 2 has no row-count comparison.

**`contracts/gemini-request-and-scaffold.md`**

12. **The scaffold note:** N8's kept bare `^DATA CONTENT` fallback, with its comment location and its landing commit (`1660c10`). This is the contract pin T007 asked for.
13. **The A8 row:** N8's assertion (exactly one line-start `FOOTER` after the marker).

**For the PM** (`spec.md` is PM-owned and was not edited):
- **Required:** NFR-7's first sub-bullet of the fast workflow's `paths:` ("the manifest, `.claude/skills/**`, … `scripts/install.sh` (for the end-to-end case)") should gain `brand/**` and `schemas/**`, or say "every manifest entry's source". The spec is now narrower than the workflow and the contract (L-8).
- **Optional:** N11's reverse direction is not in US-2 #7 or FR-K3. It traces to plan.md:502 and T008/T009, and the refusal text carries the remedy. No change is needed.
- **Nothing for the opt-in bracket:** FR-K3.3 already matches the code.

**No test reads the contracts at runtime.** The references are comments and docstrings only, so committing these amendments cannot affect CI.

---

## 5. Follow-up issues to file at `/aod.deliver`

File after `export AOD_REPO=davidmatousek/tachi`, in generic wording (NFR-6). The PM scopes each issue.

**File (7):**

| # | Title | One line | Source |
|---|---|---|---|
| 1 | install.sh: reject a `--version` value that starts with a dash | Add a parse-time `case "$VERSION_TAG" in -*) die …` guard and one negative K3 case (nothing checked out, nothing written) | SEC-K3-03 (P0 §6c) |
| 2 | Extractors: accept the `## Section N: Title` heading form | With that form, the parsers miss Section 6 and Section 2. The funnel then shows Threats Identified = 0, and the K11 join cannot read composite scores | P0 A-4 |
| 3 | Delta warnings: a free-text `baseline.source` on a stateless run is treated as a baseline | `has_baseline` is true for any non-null source (for example `"none (first run …)"`), so the "baseline run but no Status column" warning fires on a stateless run. Treat `none…` as no baseline, or have the producer write `null` | N7 (R-T3; tasks.md deliver list) |
| 4 | Project-name parser misses em-dash H1 forms | See below | New (W3) |
| 5 | maestro-stack infographic template: typography table specifies dark text on its dark background | See below | New (W3) |
| 6 | Infographic heat-map cell-level grid has no deterministic data source | See below | New (W3) |
| 7 | Infographic render: keep the Gemini API key off the process argument list | See below | New (P1, from the code review's NFR-5 advisory) |

**#4, the project-name parser.**
- `# Threat Model — {Name}` matches neither recognized form, and the `architecture.md` fallback's forms are narrow too. The result is "Unknown Project" in every infographic title (all six K15 renders) and in the metadata.
- `# {Name} — Threat Model` keeps a trailing ` —`.
- It is pre-existing: the output is byte-identical from pre to post.
- The production `threats.md` template writes a bare `# Threat Model Report`, so adopters depend entirely on the narrow fallback.
- The parser's tests (`test_project_name_parser.py`) are in the **ungated** N4 set. The fix should gate them.

**#5, maestro-stack contrast.**
- The Typography table (`#111827`, `#374151`, `#4B5563`, `#6B7280`) contradicts the same file's palette (text `#F8FAFC`, `#94A3B8`, `#64748B`) and its prompt's "white or light gray, minimum 4.5:1" (WCAG AA).
- The renders passed only because the prompt wins. It is a LOW template-copy fix.

**#6, the cell-level grid.**
- `schemas/infographic.yaml` requires `cell_level_grid`. The baseball-card prompt carries `{heat_map_cell_grid}`, which the agent text says must be "not inferred from aggregate counts".
- But `compute_heat_map` emits only component × severity counts, so the agent derives the per-category grid itself.
- The fix: add an extractor field with its golden, or relax the schema.

**#7, the Gemini key.**
- The reference prescribes header-only but leaves the `curl` form to the model. `-H "x-goog-api-key: $KEY"` puts the key in argv for a render of about 30 s (CWE-214).
- The fix: prescribe `-H @-` or `-H @file`, and pin it in A7. LOW.
- NFR-5 does not require this, so the PM may decline it.

**Not filed:**
- **The reviewer's `target_is_dir` suggestion:** a code-economy tidy-up of a test helper, with no tracking value. DEVOPS-K3 may drop the parameters on its next touch of `install_sh_helpers.py`.
- **The cosmetic Gemini artifacts:**
  - the garbled maestro-stack sub-headers ("ID Highest sendings");
  - TB-1's missing count badge;
  - the mixed C/High/H cell labels;
  - executive-architecture's layer-grouping simplification;
  - the fallback model's invented "Architecture risk-weight strip" heading and its red-outlined zero cell.

  These are **single-run model variance**. Each passes the K15 bar (no leaked label, no invented ID), and the garbled strings don't appear in the prompt. **No issue.** List them as known cosmetic variance in the PR body's render notes (T037). If any recurs across runs, it becomes a prompt-hardening item, for example quoting the exact sub-header strings.
- **A rider on #1 for the cleanup skip check:** not filed. At HEAD its input is at most about 0.5 KB, which is about 65× below the largest size P1 measured with no failure (35 KB) and about 200× below the smallest failing size (104 KB). The new constraint row documents the bound.
- **Follow-ups from tasks.md's deliver list** (TW-5 residual leakage, a blocked model, carved K-items): **none apply.**
  - T039 ruled NO CARVE.
  - TW-3 and TW-4 did not fire. #370 was folded in through T031.
  - TW-5 was not consumed and TW-6 did not fire.
  - TW-7 did not fire.
  - No model was blocked.

---

## 6. N-1 and P1's conditionality

| | |
|---|---|
| **W4 (T037 ∥ T038)** | **Not conditional.** It is docs only. N-1 cannot move product behavior or the oracle, and P1 verified it locally (§1.5) |
| **`/aod.deliver`** | **The condition is met.** `tachi pytest` is green on both legs at `9c15a3b` (run 38064601442: ubuntu done 15:47Z, macOS done 16:07Z), and all 10 PR checks are green. Deliver keeps its usual requirement: green at the final tip |
| **If a later test-only fix goes red** | Fix forward in the test module and re-run the cycle. It reopens P1 only if a non-test file changes |

---

## 7. Architecturally material before W4

1. **Release urgency.**
   - v4.48.0's render surface (`origin/main`) names only `gemini-3-pro-image-preview`, `gemini-3.1-flash-image-preview` (both shut down 2026-06-25) and `gemini-2.5-flash-image` (shut down 2026-10-02; spec `:28`, `:640`).
   - Since 2026-10-02, adopters on the current release get spec-only infographics: ADR-014's graceful degradation, with no image.
   - **Deliver F-373 promptly after W4.**
   - PD-7 has no K14 notice. **Recommendation to the PM (T038):** notice 1, "update the clone and re-run `install.sh`", should also say that the update moves infographic rendering to the current image models. Use generic wording.
2. **T038's notice set**, under PD-7's conditions.
   - **Notices 1–5 apply.** Notice 4 because K11 ships, notice 5 because K13-posture ships.
   - **Notice 6 drops:** no P-9.2 or P-10.1 fired, since no model was blocked and all renders were live.
   - **Notice 7 drops:** TW-7 did not fire.
   - The D-1 notice needs no change for RC-1, H-1, M-1 or L-1. They are pre-release fixes to K3, which has not shipped, and the refusal texts carry their remedies.
   - Notice 5 stays accurate with L-6. The `main.typ` guard fires first.
3. **The ADR-014 note** (T037; the architect writes it). Append a dated F-373 note; don't rewrite the 2026-03-23 text. It covers:
   - **The chain:** `gemini-3-pro-image`, then `gemini-3.1-flash-image`. The retired IDs leave the render surface, A6 guards against their return, and one `Retired models:` provenance line remains.
   - **The request shape:** `responseModalities ["TEXT","IMAGE"]` and `imageConfig.{aspectRatio, imageSize}`. 2K is kept (35.73 s maximum), and executive-architecture renders 3:4 portrait.
   - **The walk:** only on 404 `NOT_FOUND` or 403 `PERMISSION_DENIED`. A 400 is loud and non-blocking, and is not walked (PD-15). An exhausted chain logs at Error and names each model tried.
   - **Live verification:**
     - the W0 smoke, 8/8;
     - K14 and K15, 6/6 plus the fallback (2026-10-06);
     - the maintainer's check (2026-10-10).

     No live non-200 was seen, so the walk rows are pinned statically (A7).
   - **Key handling:** header-only (NFR-5).
   - **Watching for the next shutdown:** the reference's per-model `Verified:` lines make it visible.
   - **Supersession:** the note supersedes Decision §2's and the Mitigation section's preview model names.
4. **T037's PR body.**
   - The oracle classes are unchanged since `91e4542`: T036 moved 0/0/0.
   - `maestro-reference`'s PDF grows from 86 to 88 pages through K13.1, which goes in the #364 handoff.
   - The T036 fixes count as pre-release fixes.
   - The PR closes #373 and #370.
   - The title is already `fix(373): adopter install + output fidelity fixes`.
5. **The #364 handoff:** no change from T036.

## 8. Carry-forward (W4, P2, deliver)

- **W4:**
  - T037: the ADR-014 note per §7.3, the docs sweep, the CHANGELOG, the PR body per §7.4, and the #364 draft.
  - T038: notices 1–5, with notice 1 carrying the image-model clause (§7.1, §7.2).
- **Due from the architect at W4 or P2:** a `data-model.md` §2.2 bullet for N11's reverse direction, mirroring installer-cli "The reverse direction, N11". This checkpoint could not edit that file.
- **P2:**
  - read T037 and T038;
  - confirm the N11 bullet in §2.2;
  - confirm the PM's NFR-7 `paths:` edit;
  - confirm that `tachi pytest` is green on both legs at the final tip.
- **Deliver:**
  - CI is green at the final tip. N-1's own cycle already passed at `9c15a3b` (§6);
  - the branch is current, and `main` equals `origin/main` (KB 18);
  - the follow-ups in §5 are filed, after `export AOD_REPO=davidmatousek/tachi`;
  - the PR squash-merges as `fix(373)`, then the release-please patch PR opens;
  - the PD-7 pre-merge edit and the `gh release edit` backstop are applied;
  - the #364 comment is posted.
  - SC-7 stays outside this feature.

## 9. Final state

- **Main tree** (`git -C /Users/david/Projects/tachi status --short` at the end of this review; HEAD `9c15a3b`). The four contract files show as modified: `extraction-data-contract.md`, `gemini-request-and-scaffold.md`, `installer-cli.md` and `manifest-completeness.md`. This record is new. Nothing else changed.
- **Code and commits.** No product code or tests were edited, and nothing was committed; the orchestrator commits.
- **Scratch.** `p1/clone/tachi` is clean at `9c15a3b`, after the temporary installer swap was restored.
