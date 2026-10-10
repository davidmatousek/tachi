# RC-1 test-first record (W3, P0 required change)

**Feature**: 373-adopter-install-output-fidelity
**Change**: RC-1 (MEDIUM, K3) — the residual of SEC-K3-01 (`p0-architect-review.md` Sec. 6(b), Sec. 9)
**Agent**: DEVOPS-K3 (Lane A, owner of `scripts/install.sh`), W3
**Base**: `add7912` on branch `373-w3-rc1` (worktree `.../scratchpad/wt/rc1`)
**Integrated onto**: `373-adopter-install-output-fidelity` (PR #375) — see "Integration note" below for the worktree→branch SHA mapping and CI evidence (T034, W3 integration).

Per the architect's P0 review, `resolve()`'s 32-hop ceiling bounds only one
link's own chain, while the real OS ELOOP limit counts every link met in
resolving a single path, linked ancestors included. Two chains each under
32 hops can still sum past the platform limit when one is nested inside the
other's resolved destination — reproduced at P0 with two 17-hop chains
(`.claude`, and inside its target, `.claude/skills`), which let the
pre-flight through and then crashed `mkdir -p` mid-copy, after an earlier
manifest entry had already been written (non-atomic partial install).

---

## Commits (in order)

Worktree SHAs (original lane commits, branch `373-w3-rc1`), superseded on
integration by the branch SHAs on the right:

1. `f5a2b1f` → **`f04254c`** — `test(373): RC-1 regression — 21+21-link linked-ancestor chain refused with zero writes (P0 RC-1)`
   — adds `test_rc1_regression_21_plus_21_hop_linked_ancestor_chain_refused_with_follow_symlinks`
   to `tests/scripts/test_install_sh_symlink_preflight.py`. `scripts/install.sh` untouched.
   Pushed alone first (push 1) for deliberate test-first CI evidence — see
   "Integration note" below.
2. `c5edbc4` → **`60f3714`** — `fix(373): RC-1 — whole-path existence guard first in install.sh resolve() (P0 RC-1, SEC-K3-01 residual)`
   — makes `[ -e "$p" ] || return 1` the first statement of `resolve()`; fixes the
   comment above it; 32-hop ceiling unchanged. One textual difference from the
   worktree commit: the integration dropped the contract's
   `(amended at P0, 2026-09-28)` doc-tracking marker from the `resolve()`
   comment (a doc-tracking marker only, not code — see "Integration note").
3. (this file) → **`91e4542`** — `docs(373): RC-1 test-first record (P0 RC-1)`
   — this file, updated in place with the integrated SHAs and CI evidence.

Push 2 (tip, `91e4542`) carries RC-3 (`7b8a93f`) and RC-2 (`7cf98f0`) ahead of
the RC-1 fix/record above — unrelated P0 fixes integrated in the same W3
wave; see `specs/373-adopter-install-output-fidelity/test-results/wave-04/results.json`
for the full T034 gated-set + CI verification covering all three.

21+21 (not P0's reproduction figure of 17+17) was chosen so the combined
42-hop lookup deterministically exceeds BOTH Darwin's 32-hop `MAXSYMLINKS`
AND Linux's 40-hop `SYMLOOP_MAX` on both CI legs — 17+17 (34) clears
Darwin's 32 but not Linux's 40, so it would silently pass on an Ubuntu
runner. Each 21-hop chain alone stays under the shared 32-hop ceiling, so
only the new whole-path guard (not the pre-existing per-chain hop count)
can refuse it.

---

## Red run (macOS, against `add7912`, before the fix)

```
cd .../wt/rc1 && LC_ALL=C python3 -m pytest tests/scripts/test_install_sh_symlink_preflight.py \
  -k test_rc1_regression_21_plus_21_hop_linked_ancestor_chain_refused_with_follow_symlinks -v
```

**Result: 1 failed** (not a harness error — a real mid-copy crash):

```
result.returncode == 1   # this assertion PASSED — the script did exit 1
assert "Nothing was written" in out
AssertionError: assert 'Nothing was written' in
'\nFollowing symlinked destination(s) (--follow-symlinks):
  .claude -> .../outside-a
  .claude/skills -> .../outside-b
  Skipped cleanup (symlinked path, not deleted): .claude/commands/threat-model.md
  ...
mkdir: .../project/.claude/skills: Too many levels of symbolic links\n'
```

The pre-flight's own `resolve()` classified **both** `.claude` and
`.claude/skills` as merely `outside` the project (each independently
resolves in 21 hops, under the 32-hop ceiling — an absolute link target
decouples hop-counting from the `.claude` prefix after the first hop), so
`--follow-symlinks` let the copy loop proceed. The REAL `mkdir -p`, given
the full unresolved logical path, then had to walk `.claude`'s chain and
continue into `skills`'s own chain in one OS-level lookup (42 hops) and hit
ELOOP on Darwin. This is the exact failure mode P0 found, not a different
or earlier error.

**Independent confirmation of the non-atomic partial write** (manual
reproduction script in the scratchpad, same fixture, outside pytest so the
project directory could be inspected after the crash):
```
returncode: 1
mkdir: .../project/.claude/skills: Too many levels of symbolic links
--- plain entry written? ---
True
--- .claude/skills/tachi-example written? ---
False
```
`scripts/example_script.py` (listed first in the manifest) was written to
disk before the crash; `.claude/skills/tachi-example` (which never gets
copied) was not. This confirms the red run fails for the right reason: a
genuine non-atomic partial install, matching SEC-K3-01/RC-1 exactly.

The Linux-leg red run (same test, same `add7912` base, Ubuntu CI) is
expected to fail the same way for the same reason, since Linux's own
`SYMLOOP_MAX` (commonly 40) is also exceeded by the combined 42-hop lookup.
That evidence is the CI run on commit `f04254c` (test-only, pre-fix) —
confirmed below under "Integration note".

---

## Integration note (T034, W3 integration)

The orchestrator integrated the worktree lane in two pushes to produce
test-first CI evidence for this exact RC-1 regression, rather than a single
combined push:

- **Push 1 — `f04254c`** (test only, installer still unfixed): adds the RC-1
  regression test with `scripts/install.sh` untouched. Expected: `tachi
  pytest` red on **both** CI legs (the real OS-level symlink ceiling this
  test pins is platform-independent — see red-run analysis above), every
  other workflow green.
- **Push 2 — `91e4542`** (tip): adds RC-3 (`7b8a93f`), RC-2 (`7cf98f0`), the
  RC-1 fix (`60f3714`), and this record (`91e4542`). Expected: all CI green.

One textual diff from the worktree commits: integration dropped the
contract's `(amended at P0, 2026-09-28)` doc-tracking marker from the
`resolve()` comment in `scripts/install.sh` (a marker used to track which
P0-review amendment introduced a comment block, not executable code).
Verified directly — `git diff c5edbc4 60f3714 -- scripts/install.sh`
shows exactly one changed line: the trailing `   (amended at P0,
2026-09-28)` text is removed from the first comment line above `resolve()`.
Nothing else in the file differs — the statement `[ -e "$p" ] || return 1`
and the rest of the comment are byte-identical between the two commits.

### CI evidence — Push 1 (`f04254c`), confirmed RED on both `tachi pytest` legs

| Leg | Run / Job | Conclusion | Result line |
|-----|-----------|------------|--------------|
| macos-latest | [run 37486585591 / job 112348071119](https://github.com/davidmatousek/tachi/actions/runs/37486585591/job/112348071119) | **failure** | `1 failed, 239 passed, 1 skipped, 1 xfailed in 1869.15s (0:31:09)` |
| ubuntu-latest | [run 37486585591 / job 112348071478](https://github.com/davidmatousek/tachi/actions/runs/37486585591/job/112348071478) | **failure** | `1 failed, 235 passed, 5 skipped, 1 xfailed in 401.37s (0:06:41)` |

Both legs fail on the **same single test**,
`test_install_sh_symlink_preflight.py::test_rc1_regression_21_plus_21_hop_linked_ancestor_chain_refused_with_follow_symlinks`,
for the same reason — the pre-flight lets `--follow-symlinks` proceed, and
the real copy then hits the platform's symlink ceiling mid-install:

```
# macos-latest
E   AssertionError: assert 'Nothing was written' in '\nFollowing symlinked destination(s) (--follow-symlinks):
  .claude -> .../outside-a
  .claude/skills -> .../outside-b
  ...
mkdir: .../project/.claude/skills: Too many levels of symbolic links\n'

# ubuntu-latest
E   assert 'Nothing was written' in "\nFollowing symlinked destination(s) (--follow-symlinks):
  .claude -> .../outside-a
  .claude/skills -> .../outside-b
  ...
cp: cannot stat '.../project/.claude/skills/tachi-example/': Too many levels of symbolic links\n"
```

Every other workflow on `f04254c` stayed green: `gitleaks`, `gitleaks
full-repo scan`, `manifest-completeness`, `extraction-fidelity`,
`report-posture`, `Verify all 7 MAESTRO layers present in example tables`,
`Verify preflight gate fires when mmdc is absent`, `Verify ORDERED_FRAMEWORKS
fingerprints match the committed sidecar`.

### CI evidence — Push 2 (`91e4542`), confirmed ALL GREEN (10/10 checks)

| Check | Run / Job | Conclusion |
|-------|-----------|------------|
| pytest init.sh suite — macos-latest | [run 37487273141 / job 112350467359](https://github.com/davidmatousek/tachi/actions/runs/37487273141/job/112350467359) | success |
| pytest init.sh suite — ubuntu-latest | [run 37487273141 / job 112350467832](https://github.com/davidmatousek/tachi/actions/runs/37487273141/job/112350467832) | success |
| manifest-completeness | run 37487273132 / job 112350483839 | success |
| extraction-fidelity | run 37487273132 / job 112350483211 | success |
| report-posture | run 37487273132 / job 112350483874 | success |
| Verify all 7 MAESTRO layers present | run 37487273218 / job 112350467287 | success |
| Verify preflight gate fires when mmdc is absent | run 37487273172 / job 112350467107 | success |
| Verify ORDERED_FRAMEWORKS fingerprints match sidecar | run 37487273212 / job 112350467357 | success |
| gitleaks full-repo scan | run 37487273174 / job 112350467508 | success |
| gitleaks | [run 112350618202](https://github.com/davidmatousek/tachi/runs/112350618202) | success |

Full T034 gated-set totals (local scratch-clone run at `91e4542`, all three
wave-4 pytest invocations) and classification against the wave-03 baseline
are recorded in
`specs/373-adopter-install-output-fidelity/test-results/wave-04/results.json`
(485 passed / 0 failed / 2 skip-equivalent — wave-03's 482 plus exactly the
3 new RC tests, zero regressions).

---

## Green runs (macOS, after the fix at `60f3714`)

New test alone:
```
LC_ALL=C python3 -m pytest tests/scripts/test_install_sh_symlink_preflight.py \
  -k test_rc1_regression_21_plus_21_hop_linked_ancestor_chain_refused_with_follow_symlinks -v
# 1 passed
```

Both K3 modules, full run:
```
LC_ALL=C python3 -m pytest tests/scripts/test_install_sh_symlink_preflight.py \
  tests/scripts/test_install_sh_ref_restore.py -v
# 59 passed in 7.87s
```
(58/58 at P0's patch baseline + 1 new RC-1 regression test = 59/59.) The
32/33-hop boundary tests (`test_symlink_chain_hop_boundary[32-hops-resolves]`,
`[33-hops-unresolvable]`) and the existing SEC-K3-01 regression
(`test_sec_k3_01_regression_33_hop_claude_chain_refused_with_follow_symlinks`)
all stayed green — unaffected by the new guard, as expected (tmp paths are
physical; on Darwin the new `[ -e ]` guard and the old per-chain loop agree
at the 32/33 boundary, on Linux the old loop ceiling alone still catches 33
since the real OS limit there is higher).

---

## Static checks

- `bash -n scripts/install.sh` — clean, no output, exit 0.
- `shellcheck scripts/install.sh` (0.11.0) — clean, no findings, exit 0,
  both **before** (`add7912` baseline, copied aside) and **after**
  (`c5edbc4`, the worktree fix commit — integrated unchanged as `60f3714`
  apart from the doc-marker drop noted under "Integration note") the fix.
  Zero new findings. Not independently re-run against `60f3714`; the
  statement-level diff is identical per `git show 60f3714 -- scripts/install.sh`.
- `git diff add7912 -- scripts/install.sh` — touches only `resolve()`'s
  leading comment block and its first statement (`[ -e "$p" ] || return 1`).
  No other line in `scripts/install.sh` changed. The three
  `x-release-please-version` markers (`:13,28,57` before the diff; unchanged
  line numbers after, since the edit is below them) are untouched —
  confirmed both by `grep -n` and by the diff containing zero matches for
  that string, and by `test_release_please_markers_preserved_in_install_sh`
  staying green.

## Files

- `scripts/install.sh` (`resolve()`, fixed)
- `tests/scripts/test_install_sh_symlink_preflight.py` (new regression test)
- No changes to `tests/scripts/install_sh_helpers.py` — the existing
  `build_source_tree(entries=...)` override and `build_symlink_chain` (which
  already generalizes to any root, not just the project root) were
  sufficient to build the nested 21+21 fixture; no new helper was needed.
