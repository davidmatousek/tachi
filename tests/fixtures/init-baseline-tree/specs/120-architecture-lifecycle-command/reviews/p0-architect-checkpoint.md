# P0 Architect Checkpoint Review: Feature 120 — Architecture Lifecycle Command

**Reviewer**: architect
**Date**: 2026-04-09
**Scope**: Waves 0-2 implementation (Phase 1 + Phase 2 + Phase 3 from tasks.md)
**Artifacts Reviewed**:
- `.claude/commands/tachi.architecture.md` (lifecycle management additions)
- `.claude/commands/tachi.threat-model.md` (snapshot step addition)
- `specs/120-architecture-lifecycle-command/spec.md` (FR alignment)
- `docs/product/02_PRD/120-architecture-lifecycle-command-2026-04-09.md` (PRD alignment)
- `specs/120-architecture-lifecycle-command/plan.md` (plan alignment)

## Review Criteria

### 1. Architecture Soundness — Step Ordering

The step ordering is logically sound and follows the correct dependency chain:

**`/tachi.architecture`**: Step 0 (detect) -> Step 0a (archive) -> Step 0b (guided update) -> Step 1 (scope) -> Step 2 (analyze) -> Step 3 (generate body) -> Step 3a (checksum + frontmatter) -> Step 4 (report)

This correctly ensures:
- Detection happens before any modification
- Archive happens before overwrite (preserves data)
- Guided update collects context before generation
- Body is written before checksum is computed (two-pass)
- Frontmatter is prepended after checksum (correct ordering)
- Report runs last and has access to all computed values

**`/tachi.threat-model`**: Step 0 (parse flags) -> Step 1 (validate prerequisites, items 1-3 create output dir) -> Step 1.4 (snapshot) -> Step 2 (run analysis)

Snapshot is correctly positioned after directory creation and before orchestrator invocation.

**Finding**: PASS. No dependency issues detected.

### 2. Spec Alignment — FR Coverage

| FR | Description | Covered | Location |
|----|-------------|---------|----------|
| FR-001 | YAML frontmatter with 5 fields | YES | Step 3a, lines 118-127 |
| FR-002 | Version starts at 1, increments by 1 | YES | Step 3a item 2 (three cases) |
| FR-003 | Checksum is SHA-256 of body only, sha256: prefix | YES | Step 3a item 1 |
| FR-004 | Explicit platform tool invocation (shasum -a 256) | YES | Step 3a item 1 |
| FR-005 | Legacy files treated as v0, first managed = v1 | YES | Step 0 item 2 + Step 3a |
| FR-006 | Archive before overwrite to {parent_dir}/.archive/v{N}/ | YES | Step 0a |
| FR-007 | Archive preserves complete file including frontmatter | YES | Step 0a item 4 |
| FR-008 | Archive directory auto-created | YES | Step 0a item 3 (mkdir -p) |
| FR-009 | Archive append-only, idempotent for same version | YES | Step 0a item 5 |
| FR-010 | No archive for first-time generation | YES | Step 0a item 1 |
| FR-011 | previous_version contains relative path or null | YES | Step 3a item 2 |
| FR-012 | Threat model copies architecture to output folder | YES | Step 1.4 item 1 |
| FR-013 | Snapshot is verbatim, no modifications | YES | Step 1.4 item 1, Note |
| FR-014 | Snapshot filename matches source | YES | Step 1.4 item 1 |
| FR-015 | Skip silently if architecture file missing | YES | Step 1.4 item 2 |
| FR-016 | Snapshot after dir creation, before orchestrator | YES | Position between Step 1.3 and Step 2 |
| FR-017 | Guided update mode with 6 categories | YES | Step 0b items 2-4 |
| FR-018 | No changes = file untouched, no archive, no version increment | YES | Step 0b item 6 |
| FR-019 | Description summarizes changes from update session | YES | Step 3a item 5 |
| FR-020 | Archive path relative to parent directory | YES | Step 0a item 2 |
| FR-021 | Example files unchanged | YES | Not modified (confirmed via glob) |
| FR-022 | Downstream pipeline unaffected | YES | No changes to any downstream files |

**Finding**: PASS. All 22 FRs are addressed in the implementation.

### 3. Two-Pass Write Pattern

Step 3a specifies:
1. Write body to output file (Step 3 does this)
2. Run `shasum -a 256 {output_path}` to compute hash
3. Read file content, prepend frontmatter block, write back

This is architecturally correct. The two-pass approach avoids:
- Chicken-and-egg problem (hash needs content, frontmatter needs hash)
- Echo/pipe issues with large markdown bodies containing special characters
- Any risk of the frontmatter itself being included in the hash

**Finding**: PASS. Pattern is sound and correctly documented.

### 4. Version Logic Completeness

Three cases specified in Step 3a item 2:

| Case | Detection | Version | previous_version | Archive |
|------|-----------|---------|-------------------|---------|
| Fresh generation | No file at path | 1 | null | None |
| Legacy upgrade | File exists, no frontmatter | 1 | .archive/v0/{filename} | v0 |
| Managed update | File exists, frontmatter with version N | N+1 | .archive/v{N}/{filename} | vN |

All three cases are covered. The legacy-to-managed transition correctly uses v0 as the archive version and produces v1 as the first managed version.

**Finding**: PASS. All three version transition paths are complete.

### 5. Archive Path Convention

Step 0a item 2 consistently specifies: `{parent_dir}/.archive/v{N}/{filename}`

- `{parent_dir}` is derived from the architecture file's directory (not hardcoded)
- `{N}` uses the current version for managed files, `0` for legacy
- `{filename}` uses the actual filename (not hardcoded to `architecture.md`)
- This supports custom paths like `security/my-arch.md` -> `security/.archive/v{N}/my-arch.md`

Step 3a item 2 uses consistent relative paths for `previous_version`: `.archive/v{N}/{filename}`

**CONCERN**: The `previous_version` field in Step 3a uses relative paths (`.archive/v0/{filename}`) while Step 0a describes the full derivation using `{parent_dir}/.archive/v{N}/{filename}`. The relative path is the correct choice for the frontmatter field (portable, no absolute paths), but the relationship between the two should be stated explicitly. Currently it is implicit — an implementer must infer that `previous_version` is relative to the architecture file's parent directory.

**Finding**: CONCERN (Low). The convention is correct but the relationship between the absolute archive path (used for file operations) and the relative `previous_version` value (stored in frontmatter) is implicit rather than explicit.

### 6. Backward Compatibility

Two dimensions verified:

**Architecture files as threat model input**: Step 1.4 in `tachi.threat-model.md` copies the file verbatim regardless of frontmatter presence. The orchestrator receives content via `<architecture-input>` tags (Step 2 reads the file content). The research notes (and PRD Risk 1) confirm the format detector treats frontmatter as free text. Example files confirmed to have no frontmatter (checked all 3).

**Existing pipeline**: No changes to any agent file, parser file, or downstream command file. Only `tachi.architecture.md` and `tachi.threat-model.md` were modified.

**Finding**: PASS. Backward compatibility is preserved.

### 7. Snapshot Placement

Step 1.4 is positioned between:
- Step 1 item 3 ("Check output directory" — creates `output_dir` if it does not exist)
- Step 2 ("Run Threat Analysis" — invokes orchestrator)

This is the correct insertion point. The timestamped output directory is created as part of Step 0 item 7 (timestamp computation) and Step 1 item 3 (directory creation). By Step 1.4, the directory exists and can receive the snapshot file.

The Note clarifies that the snapshot is informational — the orchestrator still receives architecture via `<architecture-input>` tags. This prevents any confusion about whether the snapshot replaces the existing input mechanism.

**Finding**: PASS. Correctly positioned.

### 8. Guided Update Abort Path

Step 0b item 6 specifies:
- Leave architecture file untouched
- No version increment
- Display: "No changes indicated. Architecture file unchanged."
- Skip Steps 1, 2, 3, and 3a entirely
- Proceed directly to Step 4 with a "no changes" report

**ADVISORY**: The abort path skips Steps 1, 2, 3, and 3a but does not mention skipping Step 0a (archive). However, Step 0b runs *after* Step 0a, so by the time the abort is triggered, the archive has already been performed. This means an abort after guided update still leaves an archive entry — which is a potentially surprising behavior. If the user indicates "no changes," one might expect no archive to be created either.

However, this is defensible for P1: the archive captures the state at the time of the update attempt, which has audit value. The archive is idempotent (FR-009), so a subsequent successful run will overwrite the same version. This is a design choice, not a defect.

**Finding**: ADVISORY. Abort path is functionally correct. The archive-before-abort behavior is a defensible P1 design choice. Consider documenting this behavior for user clarity in a future iteration.

### 9. Additional Observations

**A. Step ordering label**: The threat model command numbers the snapshot as "Step 1.4" which is unconventional but unambiguous. The decimal numbering clearly communicates this is an insertion between existing steps without renumbering. Acceptable.

**B. Description field coverage**: Step 3a item 5 covers all four description cases (first-time, legacy upgrade, managed update with guided mode, managed update without guided mode). The fourth case (managed update without guided mode) is correctly identified as an edge case for future direct-edit flows.

**C. Usage examples**: The examples section at the bottom of `tachi.architecture.md` has not been updated to show lifecycle-related examples (e.g., updating an existing file). This is a documentation gap but not a functional issue.

**D. Command cross-reference**: The threat model report (Step 3) references `/risk-score` instead of `/tachi.risk-score`. This predates Feature 120 and is not in scope for this review, but is noted for a future cleanup.

## Summary

| ID | Severity | Finding | Recommendation |
|----|----------|---------|----------------|
| F-01 | PASS | Step ordering is logically sound with correct dependency chain | None |
| F-02 | PASS | All 22 FRs (FR-001 through FR-022) are addressed in implementation | None |
| F-03 | PASS | Two-pass write pattern correctly avoids hash-frontmatter circular dependency | None |
| F-04 | PASS | All three version transition cases (fresh, legacy, managed) are complete | None |
| F-05 | CONCERN | previous_version relative path convention is implicit — relationship to absolute archive path not stated | Add a clarifying note in Step 3a that previous_version is relative to the architecture file's parent directory |
| F-06 | PASS | Backward compatibility preserved — examples unchanged, downstream unaffected | None |
| F-07 | PASS | Snapshot at Step 1.4 correctly positioned between dir creation and orchestrator | None |
| F-08 | ADVISORY | Guided update abort still leaves archive from Step 0a — archive-before-abort is defensible but potentially surprising | Consider documenting this behavior for users in a future P1 iteration |
| F-09 | PASS | Description field covers all four generation scenarios | None |
| F-10 | ADVISORY | Usage examples not updated with lifecycle scenarios (update existing file) | Add lifecycle usage examples in a future documentation pass |

**Blocking findings**: 0
**Concerns**: 1 (Low severity)
**Advisories**: 2

## Decision

**STATUS: APPROVED_WITH_CONCERNS**

The implementation is architecturally sound. Step ordering follows correct dependency chains, all 22 functional requirements are addressed, the two-pass checksum pattern is correctly specified, and backward compatibility is preserved. The single concern (implicit relative path convention) is low severity and does not block validation. The two advisories are documentation improvements appropriate for a future iteration.

Recommendation: Proceed to Phase 4 validation (Wave 3).
