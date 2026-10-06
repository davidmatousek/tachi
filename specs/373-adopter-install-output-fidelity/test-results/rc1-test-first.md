# RC-1 test-first record (W3, P0 required change)

**Feature**: 373-adopter-install-output-fidelity
**Change**: RC-1 (MEDIUM, K3) — the residual of SEC-K3-01 (`p0-architect-review.md` Sec. 6(b), Sec. 9)
**Agent**: DEVOPS-K3 (Lane A, owner of `scripts/install.sh`), W3
**Base**: `add7912` on branch `373-w3-rc1` (worktree `.../scratchpad/wt/rc1`)

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

1. `f5a2b1f` — `test(373): RC-1 regression — 21+21-link linked-ancestor chain refused with zero writes (P0 RC-1)`
   — adds `test_rc1_regression_21_plus_21_hop_linked_ancestor_chain_refused_with_follow_symlinks`
   to `tests/scripts/test_install_sh_symlink_preflight.py`. `scripts/install.sh` untouched.
2. `c5edbc4` — `fix(373): RC-1 — whole-path existence guard first in install.sh resolve() (P0 RC-1, SEC-K3-01 residual)`
   — makes `[ -e "$p" ] || return 1` the first statement of `resolve()`; fixes the
   comment above it; 32-hop ceiling unchanged.
3. (this file) — `docs(373): RC-1 test-first record (P0 RC-1)`

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
That evidence is the CI run on commit `f5a2b1f` (test-only, pre-fix) — to be
filled in by the orchestrator once CI reports.

---

## Green runs (macOS, after the fix at `c5edbc4`)

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
  (`c5edbc4`) the fix. Zero new findings.
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
