# Architect P0 Checkpoint Review: Install Script and Version Tagging

**Reviewer**: architect
**Date**: 2026-04-06
**Scope**: Waves 1-2 (Phase 1 Foundation + Phase 2 US1 MVP)
**Files**: `scripts/install.sh`, `INSTALL_MANIFEST.md`
**Verdict**: APPROVED

---

## Plan Sign-off Concerns Resolution

Four concerns were raised during plan sign-off (APPROVED_WITH_CONCERNS). Status of each:

### Concern 1: common.sh should NOT be sourced in install.sh

**Status**: RESOLVED

The install script does not source `common.sh`. Zero references to `common.sh` exist in the file. This is correct because `install.sh` may run from a target project that does not have tachi's internal scripts. The script is fully self-contained with its own `die()`, `usage()`, color constants, and source auto-detection. Compare with `sync-upstream.sh` (lines 28-29) which does source `common.sh` -- that script runs from within the tachi repo, so sourcing is appropriate there. The install script correctly avoids this dependency.

### Concern 2: Manifest path granularity (resolved during implementation)

**Status**: RESOLVED

Not directly applicable to install.sh code. The manifest section in `INSTALL_MANIFEST.md` uses appropriate granularity: directories with trailing `/` for bulk copy (e.g., `.claude/agents/tachi/`, `schemas/`, `templates/tachi/`) and individual file paths for selective items (e.g., `.claude/commands/threat-model.md`, `docs/guides/DEVELOPER_GUIDE_TACHI.md`). The script correctly differentiates via `case "$entry" in */)` pattern matching.

### Concern 3: T009 should use git -C for source version

**Status**: RESOLVED

Line 167: `git -C "$SOURCE_DIR" describe --tags --always 2>/dev/null || echo "untagged"`. Uses `git -C` to operate on the source repository, not the current working directory. This is essential because the user runs the script from their target project root, which may have its own (or no) git repository. The `-C` flag ensures version detection always targets the tachi source repo.

### Concern 4: Copy loop must prepend SOURCE_DIR to paths

**Status**: RESOLVED

Line 134: `src_path="${SOURCE_DIR}/${entry}"`. Every manifest entry is prepended with `SOURCE_DIR` before any filesystem operation. Target paths use `${TARGET_DIR}/${entry}`. Separation is clean and correct.

---

## Architecture Assessment

### Script Structure

The script follows a clean linear flow: constants, helpers, variables, auto-detection, argument parsing, validation, manifest parsing, copy loop, summary. Each section is clearly delineated with comment headers and task ID references (T004-T010). Structure matches the established convention in `generate-adapter-version.sh` and `sync-upstream.sh`.

### Bash 3.2+ Compatibility

**PASS**. No Bash 4+ constructs detected:
- No `[[ ]]` double brackets (uses `[ ]` POSIX test throughout)
- No associative arrays (`declare -A`)
- No `mapfile` / `readarray`
- No `|&` pipe-with-stderr
- No `${var,,}` / `${var^^}` case manipulation
- `while/case` argument parsing matches `sync-upstream.sh` convention
- Arithmetic uses `$((expr))` which is Bash 3.2 compatible
- Process substitution `< <(parse_manifest ...)` on line 161 is supported in Bash 3.2

### Error Handling

**PASS**. Comprehensive:
- `set -euo pipefail` at top -- strict mode
- `die()` for fatal errors with red-colored stderr output
- Validates source directory existence (line 86)
- Validates manifest file existence (line 89)
- Validates git availability before allowing `--version` (lines 96-98)
- Non-fatal warnings for missing manifest entries (lines 144, 156) -- continues processing remaining entries
- Non-zero exit code when any copies fail (line 177)
- Unknown arguments caught and reported (line 79)
- Missing argument values caught (lines 66, 68)

### Copy Logic Correctness

**PASS**. The directory copy pattern `cp -r "${src_path}." "${TARGET_DIR}/${entry}"` uses the POSIX dot-suffix trick to copy directory contents into the target without creating a nested subdirectory. Verified this works correctly on macOS and Linux. File copy uses plain `cp` with `mkdir -p` for parent directory creation.

### Manifest Design

**PASS**. The machine-parseable section uses HTML comment markers (`<!-- BEGIN MANIFEST -->` / `<!-- END MANIFEST -->`), which are invisible in rendered markdown. One path per line with directory/file distinction via trailing slash. The maintenance checklist (line 98) includes updating the machine-parseable section -- addressing the plan concern about keeping both sections in sync.

### Idempotency

**PASS**. `cp -r` overwrites by default. `mkdir -p` is a no-op for existing directories. No delete operations. Running the script N times produces identical results per FR-010 and SC-004.

---

## Findings Summary

| # | Severity | Finding | Status |
|---|----------|---------|--------|
| 1 | INFO | common.sh correctly not sourced | RESOLVED |
| 2 | INFO | git -C correctly used for source version | RESOLVED |
| 3 | INFO | SOURCE_DIR correctly prepended to paths | RESOLVED |
| 4 | INFO | Manifest checklist updated | RESOLVED |
| 5 | INFO | No Bash 4+ constructs detected | PASS |
| 6 | INFO | Error handling comprehensive | PASS |
| 7 | INFO | Copy pattern correct for both dirs and files | PASS |
| 8 | INFO | Idempotent behavior verified | PASS |

Zero blocking issues. Zero non-blocking concerns. All four plan sign-off concerns addressed correctly.

---

## FR Coverage (Waves 1-2)

| FR | Description | Status |
|----|-------------|--------|
| FR-001 | Copy all manifest files | Implemented (T007+T008) |
| FR-002 | Create intermediate directories | Implemented (mkdir -p) |
| FR-003 | Report version and count | Implemented (T009) |
| FR-004 | Accept --source parameter | Implemented (T005) |
| FR-005 | Auto-detect source from script location | Implemented (T004) |
| FR-010 | Idempotent | Verified by design (cp overwrites) |
| FR-011 | Never delete files | Verified (no rm/delete operations) |
| FR-012 | --help flag | Implemented (T003+T005) |
| FR-013 | Machine-parseable manifest section | Implemented (T001) |
| FR-014 | Parse machine section, not tables | Implemented (T007) |
| FR-020 | Bash 3.2+ compatible | Verified (no 4+ constructs) |

Remaining FRs (006-009, 015-019) are scoped to Waves 3-5 (version checkout, docs, tagging).

---

## Verdict

**APPROVED**. The MVP implementation is architecturally sound, correctly addresses all four plan sign-off concerns, maintains Bash 3.2+ compatibility, handles errors comprehensively, and follows established tachi script conventions. Ready to proceed to Wave 3 (version checkout support).
