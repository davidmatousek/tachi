# Contract: `scripts/install.sh` CLI, pre-flight and restore (K3, D-1, FR-K3.1–K3.7)

**Revision 1 (2026-09-27).** This revision folds in:
- the architect's plan review: M1 (destination containment), M8 (bash 3.2 implementation constraints) and L6 (classification refinements);
- the PM's plan review: RC-P4 (wording).

Changed sections are marked **(rev. 1)**. The decisions are recorded under PD-10 in `research.md`.

## Synopsis

```
install.sh [--source <path>] [--version <tag>] [--follow-symlinks] [--help]
```

`--follow-symlinks` is long form only, takes no value, and has **no short alias** (`-L` would suggest `cp -L`, which is a source-side meaning). It is parsed in the existing `while/case` loop. Both help surfaces (the header comment at `:8-19` and `usage()`) document it with this scope text **(rev. 1, RC-P4 (a))**:

> `--follow-symlinks`  Install through symlinked destinations (for example a linked `.claude/skills`). Without it, install.sh stops before writing anything when a destination is a symlink. With it, install.sh follows links at or above each installed path, names every resolved destination, and only copies: it never deletes through a link. Even with it, install.sh refuses broken, looping or wrong-type links (a file where a folder is needed, or the reverse), links nested inside an installed folder, and destinations inside the tachi source clone.

The README's K3 section (W2 Lane A) reuses this scope sentence, so the nested-link disclosure reaches the README surface (P-9.3; PM §9 item 8).

The existing `x-release-please-version` markers (`:13,19,43`) are kept. The new flag line carries no version, so it needs no marker.

## Order of operations

1. Parse the arguments and validate them (existing).
2. **Resolve the physical roots.** Run `unset CDPATH` once near the top, then `TARGET_P=$(cd -P "$TARGET_DIR" && pwd -P)` and `SRC_P=$(cd -P "$SOURCE_DIR" && pwd -P)`.
3. **Project-root containment** (S-2; identity-based per ruling AR-1). This replaces the logical `:95` equality guard, at the same site, before the version block: `if under "$TARGET_P" "$SRC_P"; then die …; fi`. `under` is defined under "Destination containment" below. No checkout has happened, so there is nothing to restore.
4. **The version block** (existing): the dirty-tree refusal, `ORIGINAL_REF`, the trap (fixed, see "The ref restore"), the local tag check, and the checkout.
5. **The pre-flight** (new). It reads the manifest from the checked-out source (`parse_manifest`), builds the checked set, classifies each link, checks each destination's containment (data-model §2), prints the report, and then either `die`s (refusal) or continues. **It writes nothing.**
6. **Cleanup** (existing, `:128-152`). With the flag, any deprecated path that has a link as the file or an ancestor is skipped and recorded as skipped. Without the flag, such a path has already caused a refusal in step 5.
7. **Copy** (existing, `:181-212`).
8. **Summary** (existing, plus the new lines below), then exit.

## Pre-flight algorithm (bash 3.2; NFR-3 primitives only) **(rev. 1)**

```bash
# resolve PATH -> prints the physical path; returns 1 if unresolvable (dangling, or > 40 hops)
resolve() {
  local p=$1 hops=0 t d
  while [ -L "$p" ]; do
    hops=$((hops + 1)); [ "$hops" -le 40 ] || return 1
    t=$(readlink "$p") || return 1
    case $t in /*) p=$t ;; *) p=$(dirname "$p")/$t ;; esac
  done
  [ -e "$p" ] || return 1
  if [ -d "$p" ]; then (cd -P "$p" && pwd -P)
  else d=$(cd -P "$(dirname "$p")" && pwd -P) || return 1; printf '%s/%s\n' "$d" "$(basename "$p")"
  fi
}

# phys_dest PATH -> prints where PATH physically is, or would be once created:
# resolve() of its deepest existing component, plus the components that do not exist yet.
# Returns 1 when the walk meets a dangling link (already refused as unresolvable).
phys_dest() {
  local q=$1 rest="" d
  while [ ! -e "$q" ]; do
    [ -L "$q" ] && return 1
    rest="/$(basename "$q")$rest"
    q=$(dirname "$q")
  done
  d=$(resolve "$q") || return 1
  printf '%s%s\n' "$d" "$rest"
}
```

Both helpers were verified at plan review in the scratchpad, on `/bin/bash` 3.2.57 and on bash 5.3.9. `resolve` handled relative, absolute and chained links, a link reached through an ancestor link, a 2-cycle, a self-loop, an ancestor self-loop (ELOOP, so unresolvable), 40 hops (resolves) and 41 hops (unresolvable). `phys_dest` handled seven cases:
- a link to an **ancestor** of the clone (`templates → ..`): source-tree;
- a link straight into the clone: source-tree;
- a new file under a linked ancestor;
- a dangling ancestor: fails;
- an existing linked file entry: its target;
- a plain new path;
- an existing file-entry link into the clone: source-tree.

**The checked set.** For each manifest entry `E` (with the trailing `/` stripped as `e`):
- **ancestors**: each strict prefix of `e`, checked at `$TARGET_P/<prefix>` (origin `ancestor`, `need = dir`);
- **the entry**: `$TARGET_P/$e` (origin `entry`; `need = dir` for a directory entry, `file` for a file entry);
- **the subtree**, for directory entries only: `(cd "$SRC_P/$e" && find . -mindepth 1)`, each `./rel` checked at `$TARGET_P/$e/rel` (origin `subtree`);
- **cleanup**: each of the five `DEPRECATED_COMMANDS` files (origin `cleanup-file`, `need = file`) and their ancestors (origin `cleanup-ancestor`).

A component keeps **every** origin it has, stored as a `|`-delimited origin string per component. There are no associative arrays in bash 3.2. The checked set is about 220 paths at HEAD: 33 entries (37 after K1/K2), 173 subtree paths, about 11 ancestors and 5 cleanup files. No manifest entry is a prefix of another; the completeness test's hygiene check keeps it that way.

**Link classification** (`[ -L "$path" ]`, never gated on `[ -e ]`). Precedence follows data-model §2.1:
1. `cleanup-only`, when the origins are exactly `cleanup-file`;
2. `unresolvable`: `resolve` fails, or the target type does not match `need`;
3. `nested`: `subtree` is among the origins;
4. `inside` or `outside`, against `TARGET_P`.

**Destination containment (rev. 1, M1).** This replaces the old per-link `source-tree` class. It applies to every manifest entry, and to every cleanup file that is not itself a link. A cleanup file that is itself a link is `cleanup-only`, and it is never deleted through, whatever its target.

**Containment compares file identity, never path strings (rev. 2, ruling AR-1).** `pwd -P` keeps whatever case the user typed or the link text used, and it does not canonicalize macOS firmlinks. So a string-prefix test (`case "$X/" in "$SRC_P"/*)`) is bypassed by a case-variant path on APFS (for example `~/projects/tachi` for a clone at `~/Projects/tachi`) or by a firmlink. `under` compares by identity with `[ -ef ]` (same device and inode), which was verified on 17 of 17 cases on bash 3.2.57 and 5.3.9:

```bash
# under PATH ROOT -> 0 if PATH (physical; its tail may not exist yet) is ROOT or lies under it.
# Compares identity ([ -ef ]: same device and inode), so case variants and firmlinks cannot bypass it.
under() {
  local x=$1 root=$2
  while [ ! -e "$x" ]; do x=${x%/*}; [ -n "$x" ] || x=/; done
  while :; do
    [ "$x" -ef "$root" ] && return 0
    [ "$x" = / ] && return 1
    x=${x%/*}; [ -n "$x" ] || x=/
  done
}

if dest=$(phys_dest "$TARGET_P/$e"); then
  if under "$dest" "$SRC_P"; then record_refusal source-tree "$e" "$dest"; fi
fi
```

The string operations inside `under` are safe because `phys_dest`'s existing prefix comes from `pwd -P`, so it holds no symlinks, and its string parents equal its physical parents.

The check runs with or without the flag. It catches links into the clone, links to an ancestor of the clone, a clone vendored at a destination path with no link at all, and case-variant or firmlink aliases of the clone.

**Report lines** are collected in newline-delimited strings and printed through `LC_ALL=C sort` for determinism.

### Implementation constraints (additions to NFR-3) **(rev. 1, M8)**

Each was reproduced at plan review on `/bin/bash` 3.2.57 and on bash 5.3.9.

| Constraint | Why |
|---|---|
| Call `resolve` and `phys_dest` **only in a conditional**: `if r=$(resolve "$p"); then …; else …; fi` | A bare `r=$(resolve …)` under `set -e` aborts the installer with rc 1 and no message |
| Never write `local r=$(resolve …)` | `local` returns 0 and **masks** the failure. A dangling link then looks resolved (empty path), classifies as `outside`, and would be *followed* with the flag, which breaks D-1's "always refuse dangling" |
| Declare helper variables `local` (`p`, `t`, `d`, `hops`, `q`, `rest`) | Keeps them out of the script's globals |
| No expansion of a possibly-empty array under `set -u`. Use newline-delimited strings, or guard with `${a[@]+"${a[@]}"}` | bash 3.2 treats `"${a[@]}"` of an empty array as an unbound variable, which is fatal. A no-link install (the common case) would crash at its summary on macOS only |
| Enumerate with `while …; done < <(…)`, never `… \| while …` | A pipe runs the loop in a subshell, and the origin strings and report lines are lost (both bash versions) |
| `unset CDPATH` once | Otherwise `cd` with a relative `--source` path can search `CDPATH` and print to stdout, which corrupts `$(cd … && pwd -P)` |
| `find . -mindepth 1` is acceptable | Not POSIX, but present in both BSD and GNU `find`. Order differs between them, so reports are sorted |

## Messages **(rev. 1)**

These are installer-authored texts. Tests assert these phrases, never `cp` or `readlink` wording.

**Always-refused block**, printed if any path is `unresolvable`, `nested` or `source-tree`:
```
Error: install stopped: destination(s) tachi cannot install through. Nothing was written.
  <component> -> <resolved>   [nested link inside <entry>: the copy cannot pass through it]
  <component> -> '<readlink text>'   [broken, looping or wrong-type link]
  <component> -> <resolved>   [link to a file where a folder is needed]
  <component> -> <resolved>   [link to a folder where a file is needed]
  <path> -> <physical destination>   [inside the tachi source clone <SRC_P>]
--follow-symlinks cannot help with these. Replace or remove each link listed above (or move the tachi clone out of the listed destination), then re-run.
```
A nested line shows `-> <resolved>` when the nested link resolves, and `-> '<readlink text>'` otherwise (RC-P4, optional items adopted).

**Flag-eligible block**, printed without the flag if any link is `inside` or `outside` (and alongside the always-refused block when both apply) **(RC-P4 (b))**:
```
Error: install stopped: symlinked destination(s) found. Nothing was written.
  <component> -> <resolved>   [inside project | outside project]
Re-run with --follow-symlinks to install through these links (it only copies and never deletes through a link), or replace each link with a real directory or file.
```

**`cleanup-only` without the flag.** The deprecated file is listed in the flag-eligible block with the bracket `[deprecated tachi command: with --follow-symlinks it is skipped, never deleted]`.

**Project-root containment** (RC-P4 optional: print the clone path):
```
Error: the target project is the tachi source clone or lies inside it. Nothing was written.
  project:     <TARGET_P>
  tachi clone: <SRC_P>
Run install.sh from your own project directory, outside the tachi clone.
```

**Opt-in, printed before copying:**
```
Following symlinked destination(s) (--follow-symlinks):
  <component> -> <resolved>   [inside project | outside project]
```

**Summary additions:**
```
Installed through symlink(s):
  <component> -> <resolved>
Skipped cleanup (symlinked path, not deleted):
  <path>
```

**Restore warning** (stderr):
```
Warning: could not restore the tachi source repo to its original ref '<ref>'.
  Restore it with: git -C '<SOURCE_DIR>' checkout '<ref>'
```

## Exit codes

| Outcome | Exit |
|---|---|
| Completed install | 0 |
| Refusal (containment, the always-refused class, or flag-eligible without the flag) | 1 (through `die`) |
| Any other failure (existing `die` paths, `COPY_FAIL`) | 1 |
| A failed ref restore | **Does not change the exit code.** It warns only |

## The ref restore (FR-K3.5, PD-11)

```bash
cleanup() {
  rc=$?
  if [ -n "${ORIGINAL_REF:-}" ]; then
    if ! git -C "$SOURCE_DIR" checkout "$ORIGINAL_REF" --quiet; then
      printf '%s\n' "Warning: could not restore the tachi source repo to its original ref '$ORIGINAL_REF'." \
                    "  Restore it with: git -C '$SOURCE_DIR' checkout '$ORIGINAL_REF'" >&2
    fi
  fi
  exit "$rc"
}
trap cleanup EXIT
```

- `ORIGINAL_REF` is the branch name, or `git rev-parse HEAD` when the clone started detached (existing `:106-109`).
- The misleading comment at `:111` is corrected to say that the restore always runs, as a harmless no-op when no checkout happened.
- **Verified at plan review** on both shells. The snippet preserves the exit status on every path tested (normal 0, `die`, a `set -e` failure, `exit 3`, pipefail, a failed command substitution), and it prints the warning exactly when the restore fails.

## Test harness contract (FR-K3.6; `tests/scripts/install_sh_helpers.py`) **(rev. 1)**

- Invoke `/bin/bash` explicitly, a fixed path rather than the repo's `BASH`-overridable `BASH_BIN` idiom, with `LC_ALL=C`. Strip ANSI color codes before asserting, and ignore the mmdc courtesy warning.
- **The source** is a copy of the working-tree `scripts/install.sh` plus a synthetic manifest and source tree in `tmp_path`, so the tests have no commit-first dependency and make no network call.
- **`--version` cases** build a throwaway repo:
  - `git init`, commit, `git tag`, with `GIT_CONFIG_GLOBAL=/dev/null` and `GIT_CONFIG_NOSYSTEM=1`;
  - commits pass `-c user.name=… -c user.email=…`;
  - the tagged and HEAD commits differ only in manifest and source content, and `install.sh` is **identical** in both, because the running script must never change under bash;
  - never run against the live checkout.
- **The forced restore failure** uses a `/bin/sh` `git` shim first on `PATH`. The shim `exec`s the real git's absolute path, captured beforehand, and fails only `checkout <ORIGINAL_REF>`, selected by an environment variable.
- **"Zero files written"** is asserted by before-and-after snapshots (path, type, `readlink`, size, mtime) of the target tree and of each link's resolved directory.
- **Non-vacuous link cases**:
  - "reached through a link" runs with `cwd` at the link and `env["PWD"]` set to the logical path;
  - "above the root" builds its own ancestor link, because pytest's `tmp_path` is already physical on macOS.
- **Cases added in rev. 1:**
  - a destination that lands in the clone through a link to the clone's **parent** (refused with and without the flag);
  - a clone vendored at a destination path with no link (refused);
  - an ancestor link to a **file** (wrong type; refused even with the flag);
  - a **dangling deprecated-command file link** (refused without the flag; with the flag the install proceeds and the cleanup is listed as skipped);
  - a **no-link install on `/bin/bash` 3.2** that must exit 0 with an unchanged summary (the empty-list regression guard for M8).
- **Cases added in rev. 2 (ruling AR-1):**
  - a link whose text spells the clone in a **different case** (refused with and without the flag);
  - a project reached through a **case-variant path inside the clone** (refused by project-root containment).

  Both run on the macOS leg. They skip on a case-sensitive volume, probed by upper-casing an existing path, which is the ubuntu leg.
- **The shell is pinned to `/bin/bash`** (N12). The harness does not honor an exported `BASH`, because that would let the strict leg drift off bash 3.2 (S-7).
- **Test-first**: the cleanup safety negatives (refused without the flag; skipped with it; the shared file survives) are written before the implementation.

## Release-note text for D-1 (SC-6 notice 2; the PM finalizes the wording in W4)

> **Installing into symlinked folders now requires consent.** If any folder or file tachi installs into is a symlink, for example `.claude/`, `.claude/skills`, `docs/`, `scripts/`, `templates/`, `schemas/`, `brand/` or `adapters/`, `install.sh` stops and names each link. Nothing is written. Re-run with `--follow-symlinks` to install through it, or replace the link with a real directory or file. Even with the flag, tachi never deletes through a link, and it always refuses dangling or looping links, links nested inside an installed folder, and destinations inside the tachi source clone. Replace or remove those links.
