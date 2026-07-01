# Data Model: Detect-Images Duplicate Cleanup (F-217)

**Date**: 2026-07-01 · **Spec**: [spec.md](spec.md) · No persistent stores — all entities are transient, derived per `detect_images` run from the assessment directory.

## Entities

### MislabeledImage
The only deletion candidate.

| Field | Type | Derivation | Validation |
|---|---|---|---|
| `path` | Path | candidate glob per stem | must exist, size > 0 (existing candidate rule preserved) |
| `stem` | str | one of the 6 known infographic stems | outside the stem set → never a candidate (no generic janitor) |
| `extension` | `.jpg` \| `.png` | filename | — |
| `content_format` | `png` \| `jpeg` \| `None` | magic-byte probe (`_file_format`) | `None` (unrecognized bytes) → never mislabeled, never deleted |
| `mislabeled` | bool | `content_format` is not None AND ext-for-format ≠ `extension` | direction-agnostic (FR-003) |

### CorrectedCounterpart
The survivor whose existence + byte-identity is deletion gate 2.

| Field | Type | Derivation | Validation |
|---|---|---|---|
| `path` | Path | same stem, extension = canonical ext for the mislabeled file's `content_format` | must exist, size > 0 |
| `byte_identical` | bool | `filecmp.cmp(mislabeled, counterpart, shallow=False)` | False → no deletion (AC-1d) |
| `pre_existed` | bool | recorded BEFORE recovery `copyfile` (recovery moment only) | recovery deletion requires `pre_existed == False` (AC-1g) |

### CleanupRecord
Operator-facing audit trail; stderr only, never stdout, never in emitted data.

| Field | Value |
|---|---|
| success record | one stderr line per deletion, naming deleted path + retained survivor |
| failure record | one stderr line per failed deletion, naming path + OS error; run continues, exit code unaffected (FR-005) |

## State Transitions (per candidate file, flag present)

```
candidate (exists, size>0, known stem)
  └─ probe content_format
      ├─ self-consistent ──────────────────────────────► PRESERVED (AC-1e/1h — predicate keys on mislabeled-ness)
      └─ mislabeled
          ├─ counterpart missing (recovery moment: write sibling first)
          │    └─ written sibling byte-identical?
          │         ├─ yes AND NOT pre_existed ──────────► DELETED + CleanupRecord (AC-1c)
          │         ├─ no (truncated/failed copy) ───────► PRESERVED, exit 0 (AC-1f)
          │         └─ yes BUT pre_existed ──────────────► PRESERVED (AC-1g cross-swap guard)
          └─ counterpart exists (pre-existing-pairs moment)
               └─ byte-identical?
                    ├─ yes ──────────────────────────────► DELETED + CleanupRecord (AC-1a)
                    └─ no ───────────────────────────────► PRESERVED (AC-1d — never guess)
```

Without the flag: every path above short-circuits to PRESERVED with zero cleanup output (AC-1b, FR-001).

## Invariants

- **INV-1**: `DELETED` is reachable only through `flag AND byte_identical` (SC-003 double gate) — both moments share one predicate implementation.
- **INV-2**: The emitted image path always references a self-consistent (correctly-labeled) file; cleanup never changes which file is emitted (path-invariance, AC-2a). **Structural proof**: the chosen file is by definition self-consistent (content format matches extension), so it can never satisfy the mislabeled deletion predicate — no iteration order can delete the emitted file (Architect review, LOW-1).
- **INV-3**: Extraction exit code and emitted output are identical whether cleanup succeeds, partially fails, or is skipped (FR-005 best-effort).
- **INV-4**: Zero-byte files are neither candidates nor counterparts (existing validation preserved).
