# K3 test-first record (T008, Lane A', W1)

**Feature**: 373-adopter-install-output-fidelity
**Task**: T008 — K3 test harness, safety negatives first (FR-K3.6, L16)
**Agent**: SBE-T (senior-backend-engineer, test-lane instance, Lane A')
**Wall clock**: approx. 2026-09-27 22:20–22:51 EDT (~31 min)
**Installer under test**: `scripts/install.sh` at commit `8916554` (branch `373-w1-laneAp`), **unmodified** — T009 (DEVOPS-K3) has not yet run.

This file is the recorded evidence FR-K3.6/L16 requires in place of a red
commit: two pytest runs against today's installer, before any implementation
change. `scripts/install.sh` itself was never touched by this task.

---

## Phase 1 — cleanup safety negatives, written and run FIRST

Per the task's TEST-FIRST requirement, only the four cleanup safety-negative
cases (US-2 #8, plus the rev. 1 dangling-deprecated-command-link variant)
were written and run before anything else in the suite existed:

- `test_ancestor_link_over_deprecated_commands_refused_without_flag`
- `test_ancestor_link_over_deprecated_commands_skipped_with_flag`
- `test_dangling_deprecated_command_link_refused_without_flag`
- `test_dangling_deprecated_command_link_skipped_with_flag`

Command:
```
cd "$WT" && LC_ALL=C python3 -m pytest tests/scripts/test_install_sh_symlink_preflight.py -v
```

**Result: 4 failed, 0 passed** — all four red, for the expected reasons:

1. `..._refused_without_flag` (the shared-folder ancestor-link case) —
   **today's installer actively deletes the shared file through the linked
   ancestor**, instead of refusing:
   ```
   AssertionError:   Removed deprecated: .claude/commands/threat-model.md
       Cleaned up 1 deprecated command file(s)
   ```
   This is the live vulnerability K3 exists to fix, reproduced concretely:
   today's `[ -f "$target_path" ]` / `rm -f` cleanup loop follows a symlinked
   `.claude/commands` straight through to a file outside the project and
   deletes it, with no refusal, no flag, no report.
2. `..._skipped_with_flag` — today's argument parser has no
   `--follow-symlinks` at all: `Error: Unknown option: --follow-symlinks`.
3. `test_dangling_deprecated_command_link_refused_without_flag` — today's
   `-f` test on a dangling symlink is simply false, so the install
   proceeds and exits 0 with no refusal and no mention of the link at all
   (a silent bypass, not a crash).
4. `..._skipped_with_flag` — same "Unknown option" cause as #2.

Full raw output was captured for this phase and matches the summary above
(4 failed in 0.11s).

---

## Phase 2 — full suite against today's installer

After Phase 1 was recorded, the rest of the suite was written (every US-2
scenario #1–#12, the rev. 1 and rev. 2/AR-1 additions, N11, and the
`--version` ref-restore module), then the **whole suite** was run again
against the same unmodified installer:

```
cd "$WT" && LC_ALL=C python3 -m pytest tests/scripts/test_install_sh_symlink_preflight.py tests/scripts/test_install_sh_ref_restore.py -v
```

**Result: 56 collected, 45 failed, 11 passed** (3.2s). Zero collection
errors, zero non-assertion exceptions — every failure is a clean, understood
`AssertionError` against a specific missing behavior.

`test_install_sh_symlink_preflight.py`: 47 items. `test_install_sh_ref_restore.py`: 9 items.

### The 11 that already pass today (pre-existing correct behavior, or harness self-checks — not K3)

| Test | Why it's already green |
|---|---|
| `test_project_reached_through_ancestor_link_not_refused` | A no-link install through an ancestor link was never a problem; today's installer doesn't inspect links at all, so it simply proceeds |
| `test_unchanged_install_no_symlinks_copies_same_files` | Baseline regression guard: plain copy behavior is unchanged |
| `test_follow_symlinks_short_alias_rejected` | Today's `*)` catch-all already rejects any unrecognized option, including `-L` |
| `test_follow_symlinks_with_value_rejected` | Same catch-all rejects `--follow-symlinks=true` |
| `test_release_please_markers_preserved_in_install_sh` | Pure regression pin: the 3 existing markers are untouched |
| `test_harness_keeps_install_sh_identical_at_tag_and_head` | Harness self-check (not installer behavior) |
| `test_ref_restored_after_successful_version_install_on_branch` | Today's restore-on-success already works |
| `test_ref_restored_after_successful_version_install_detached_head` | Same, detached-HEAD variant |
| `test_ref_restored_after_copy_failure` | Today's restore-on-COPY_FAIL already works |
| `test_ref_restored_after_invalid_version_tag` | Today's restore-on-refusal already works, for a refusal reason that predates K3 |
| `test_successful_restore_prints_no_warning` | Positive control: no warning fires when nothing forces a failure |

### The 45 that are red (K3 pre-flight, `--follow-symlinks`, containment, or the FR-K3.5 warning do not exist yet)

```
test_ancestor_link_over_deprecated_commands_refused_without_flag
test_ancestor_link_over_deprecated_commands_skipped_with_flag
test_dangling_deprecated_command_link_refused_without_flag
test_dangling_deprecated_command_link_skipped_with_flag
test_directory_entry_symlink_refused_without_flag
test_directory_entry_symlink_installs_with_flag
test_ancestor_of_file_entry_refused_without_flag
test_ancestor_of_file_entry_installs_with_flag
test_file_entry_symlink_refused_without_flag
test_file_entry_symlink_installs_with_flag
test_nested_symlinked_file_always_refused[no-flag]
test_nested_symlinked_file_always_refused[with-flag]
test_nested_symlinked_directory_always_refused[no-flag]
test_nested_symlinked_directory_always_refused[with-flag]
test_dangling_entry_link_always_refused[no-flag]
test_dangling_entry_link_always_refused[with-flag]
test_looping_entry_link_always_refused[no-flag]
test_looping_entry_link_always_refused[with-flag]
test_wrong_type_link_dir_needed_always_refused[no-flag]
test_wrong_type_link_dir_needed_always_refused[with-flag]
test_wrong_type_link_file_needed_always_refused[no-flag]
test_wrong_type_link_file_needed_always_refused[with-flag]
test_symlink_chain_hop_boundary[40-hops-resolves]
test_symlink_chain_hop_boundary[41-hops-unresolvable]
test_link_straight_into_clone_always_refused[no-flag]
test_link_straight_into_clone_always_refused[with-flag]
test_link_to_clone_parent_always_refused[no-flag]
test_link_to_clone_parent_always_refused[with-flag]
test_vendored_clone_at_entry_destination_refused_without_flag
test_vendored_clone_at_entry_destination_refused_with_flag
test_n11_clone_nested_inside_directory_entry_destination_refused
test_project_root_is_source_clone_refused
test_project_root_inside_source_clone_refused
test_case_variant_link_into_clone_refused_without_flag
test_case_variant_link_into_clone_refused_with_flag
test_project_root_case_variant_of_clone_refused
test_project_inside_clone_via_case_variant_path_refused
test_in_project_link_classified_inside_despite_ancestor_link
test_follow_symlinks_long_form_accepted
test_multiple_refusals_sorted_deterministically
test_help_flag_documents_follow_symlinks_scope
test_header_comment_documents_follow_symlinks_scope
test_ref_restored_after_symlink_refusal_with_version           (test_install_sh_ref_restore.py)
test_forced_restore_failure_warns_and_preserves_success_exit_code  (test_install_sh_ref_restore.py)
test_forced_restore_failure_warns_and_preserves_refusal_exit_code  (test_install_sh_ref_restore.py)
```
(all in `test_install_sh_symlink_preflight.py` unless noted)

They fall into four causes, all expected and all resolved by T009:
1. **No pre-flight at all** — no symlink classification, no containment,
   so every "refused" assertion fails because today's script just
   proceeds (exit 0).
2. **No `--follow-symlinks` flag** — any `with-flag` case dies immediately
   with `Unknown option`.
3. **Old message text** — `test_project_root_is_source_clone_refused` and
   the case-variant project-root cases already get refused (exit 1) via
   today's narrower self-install guard, but with the OLD message
   ("Cannot install tachi into its own source directory...") instead of
   the new "Nothing was written" contract wording.
4. **The FR-K3.5 warning is swallowed** — today's restore line is
   `git ... checkout "$ORIGINAL_REF" --quiet 2>/dev/null || true`, which
   silences BOTH the failure's exit status and its stderr unconditionally.
   Verified directly (outside pytest, against the real forced-failure
   shim) that the shim's induced failure genuinely fires and is genuinely
   swallowed by exactly that redirect — this is not a harness gap.

### A concrete near-miss worth flagging to T009's implementer

`test_project_root_case_variant_of_clone_refused` (rev. 2, AR-1), run with
`$PWD` carrying the case-variant spelling forward (as a real interactive
shell would after `cd`-ing there — see the docstring for why this is
required for the case to be non-vacuous), does **not** fail via the old
message text. It fails like this:
```
cp: .../TACHI-SRC/.claude/skills/tachi-example/. and
    .../tachi-src/.claude/skills/tachi-example/. are identical (not copied).
```
Today's exact-string self-install guard is silently **bypassed** by the
case-variant alias (the comparison strings differ in case, so they don't
match), and the script proceeds into the copy loop, which then tries to
`cp -r` the clone's own subtree onto itself. BSD `cp` happens to refuse a
same-file self-copy here; this is not guaranteed to be true of every `cp`
on every path shape, and is exactly the class of bypass AR-1's identity-based
`under()`/`[ -ef ]` check (physical-destination containment, never a string
prefix) exists to close.

---

## Handoff notes: contract ambiguities decided while writing these tests

1. **Which deprecated paths appear in the "skipped" summary list when their
   shared ancestor is linked.** `data-model.md` §2.3 and the "Order of
   operations" step 6 read (to me) as: once a cleanup path's ancestor is
   classified linked, ALL FIVE `DEPRECATED_COMMANDS` entries under it are
   structurally skipped-and-reported, regardless of whether each one has
   real backing content in the shared folder (the pre-flight classifies by
   path, not by post-hoc `[ -f ]` existence). I did **not** assert this for
   all five, only for the one file (`threat-model.md`) my fixture actually
   populates with real "shared" content — asserting all five felt too
   strong to hard-code against T009 without contract text pinning it
   explicitly. `test_ancestor_link_over_deprecated_commands_skipped_with_flag`
   asserts only: the summary says "skipped" somewhere, and the one real
   shared file survives untouched.
2. **N11's exact message wording.** `contracts/installer-cli.md`'s
   `Messages` section gives the `source-tree` bracket line for the
   dest-under-clone direction (`[inside the tachi source clone <SRC_P>]`)
   but not for N11's reverse direction (clone-under-a-directory-entry's-
   destination). T009's own task text ("the always-refused remedy already
   covers moving the clone") reads as intentional reuse of the same
   always-refused block/class, so `test_n11_clone_nested_inside_directory_entry_destination_refused`
   asserts only the header/exit-code/no-flag-remedy shape the contract
   does pin, not a specific bracket phrase.
3. **The "reached through a link" / case-variant harness cases must
   override `$PWD` to be non-vacuous, and this extends beyond what the
   contract states explicitly.** Empirically verified while writing this
   suite: when `run_install_sh` starts bash with no inherited `$PWD` (the
   harness's default), bash derives `$PWD` at startup via a real
   `getcwd()`, which — on a case-insensitive, case-preserving volume —
   silently re-normalizes a case-variant cwd back to its on-disk stored
   case before `install.sh`'s own `TARGET_DIR="$(pwd)"` ever runs. A test
   built that way would pass even under a naive string comparison,
   proving nothing about AR-1's identity-based check. The contract only
   states this explicitly for the "reached through a link"/"above the
   root" cases (Test harness contract, US-2 #9); I applied the same
   `pwd_override` requirement to the two case-variant **project-root**
   cases (US-2 #7 rev. 2) after finding this by direct experiment (see the
   near-miss above) — the case-variant **link-text** cases (`readlink`
   output is authoritative regardless of `$PWD`) did not need it.
4. **"Fails" in FR-K3.6's ref-restore list** is implemented as a
   `COPY_FAIL` case (a tagged-commit manifest entry with no backing file,
   via `build_version_tagged_source_repo`'s new `remove_from_tagged`
   parameter), and **"refusal"** as a K3 symlink refusal combined with
   `--version` (currently red, since it depends on T009). A second refusal
   test using today's pre-existing invalid-tag refusal is included
   alongside it so the ref-restore mechanic itself has a green baseline
   independent of K3 landing.
5. `install_sh_helpers.py` gained the harness runner (`run_install_sh`,
   `InstallResult`, ANSI/mmdc-warning cleaning, tree snapshots, the
   `--version` throwaway-repo builder, and the forced-checkout-failure
   `git` shim) on top of T003's sandbox builders. `build_source_tree`'s
   existing `extra_files` parameter (already present from T003) turned out
   to be exactly what the nested-link tests (US-2 #5) needed, since the
   pre-flight's `subtree` origins are enumerated from the **source's**
   `find . -mindepth 1`, not whatever a test happens to place in the
   project — a nested link only exercises that code path if its name
   actually exists in the source subtree.

## Files

- `tests/scripts/test_install_sh_symlink_preflight.py` (new, 47 items)
- `tests/scripts/test_install_sh_ref_restore.py` (new, 9 items)
- `tests/scripts/install_sh_helpers.py` (extended: harness runner added on
  top of T003's sandbox builders; `scripts/install.sh` itself untouched)

`scripts/install.sh` was not modified by this task. T009 (DEVOPS-K3)
implements against this suite next; T010 lands both in one lock-step commit.
