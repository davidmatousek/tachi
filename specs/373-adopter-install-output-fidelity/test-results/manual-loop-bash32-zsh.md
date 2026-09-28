# Manual Install Loop -- Recorded Run Under macOS `/bin/bash` 3.2.57 and zsh 5.9

**Task**: T004/T005 (Phase 2 / W1, `/aod.build` wave 2) · **Feature**: 373-adopter-install-output-fidelity
**Date (UTC)**: 2026-09-28
**Contract**: `contracts/manifest-completeness.md` -- "Recorded once, not in CI: `test_manual_install_loop` and its zsh variant are also run under macOS `/bin/bash` 3.2.57 and zsh 5.9, and the results go in `test-results/`."
**Why recorded, not gated**: NFR-7 keeps `README.md` and the developer guide off `tachi-pytest.yml`'s trigger, so the strict-shell run is captured here once rather than re-verified every CI run.

## Shell versions (this machine)

```
$ /bin/bash --version | head -1
GNU bash, version 3.2.57(1)-release (arm64-apple-darwin25)

$ zsh --version
zsh 5.9 (arm64-apple-darwin25.0)
```

`/bin/bash` on macOS is Apple's frozen bash 3.2 (last GPLv2 release), invoked by its absolute path (never a PATH-resolved `bash`, which on this dev machine would resolve to a newer Homebrew build) -- matching the same principle as K3's installer-test harness (spec ruling S-7).

## pytest result (same shells, via the completeness module)

Run in a scratch clone (`git clone --no-hardlinks`) with the T004 manifest/doc fixes and the T005 module overlaid, never in the main tree (standing rule: no pytest in the main tree, #365).

```
$ LC_ALL=C python3 -m pytest tests/scripts/test_install_manifest_completeness.py -k manual_install_loop -v
collected 10 items / 8 deselected / 2 selected

tests/scripts/test_install_manifest_completeness.py::test_manual_install_loop PASSED [ 50%]
tests/scripts/test_install_manifest_completeness.py::test_manual_install_loop_zsh PASSED [100%]

2 passed, 8 deselected in 0.97s
```

`test_manual_install_loop` invokes `/bin/bash -c` directly (so it exercises 3.2.57 on this machine, and would exercise GNU bash 5.x on an ubuntu runner without any code change). `test_manual_install_loop_zsh` feeds the rewritten block on stdin to `zsh -f -i`, per the contract, and is skipped when `zsh` is absent (ubuntu runners may lack it) -- present here.

## Manual, non-pytest recorded run (concrete file counts)

To capture a standalone file count independent of pytest's internals, the README's manual-install-loop block was extracted, its `TACHI=` line rewritten to a throwaway, manifest-driven source copy (37 manifest entries; never the developer's real clone or the main tree), and run twice into a fresh empty project under each shell.

| Shell | Run 1 file count | Run 2 file count | Run 1 vs Run 2 | Nested `.claude/.claude`? |
|---|---|---|---|---|
| `/bin/bash` 3.2.57 | 165 | 165 | byte-identical file list | no |
| `zsh` 5.9 (`-f -i`, stdin) | 165 | 165 | byte-identical file list | no |

Cross-shell: bash 3.2.57's installed file list and zsh 5.9's installed file list are byte-identical (both 165 files, same relative paths).

`zsh -f -i` echoed its interactive `PS1`/`PS2` prompts while consuming the piped script (`pipe>`, `while>`, `case>`, ...) -- expected for `-i` against a non-tty stdin, and exactly what "models a paste into a stock interactive shell" (contract) describes. Exit status was 0 on every run, under both shells.

No comment-shaped line (`(^|[ \t])#`) appears in the block: the only `#` characters are inside `grep -v -e '^<!--' -e '^#' -e '^$'`, each immediately preceded by `^` (not whitespace or line-start), so the static no-comment assertion and this recorded run agree.

## Evidence this replaces (plan-review baseline)

The contract's own plan-review evidence recorded the *unfixed* (comment-bearing) block failing under `zsh -f -i` with `zsh: command not found: #`, installing 0 files, versus 158 files once the comment was removed, and 158 files (no nesting) on a second `/bin/bash` 3.2 run. This record supersedes that baseline for the now-fixed, comment-free block and the current (larger, F-373-updated) manifest: 165 files, both shells, both runs, no nesting.
