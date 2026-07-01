# Contracts: Detect-Images Duplicate Cleanup (F-217)

This feature has no REST/GraphQL surface. The contracts are the CLI, the Python call signature, and the stderr record format.

## 1. CLI Contract — `scripts/extract-report-data.py`

```
--cleanup-mislabeled-images    (optional, boolean, default: absent/off)
```

| Aspect | Contract |
|---|---|
| Type | `store_true` boolean; long-form kebab flag, no short alias (matches existing parser conventions) |
| Default | absent → cleanup fully disabled; behavior, files, stdout, stderr, and exit code byte-identical to pre-feature (FR-001) |
| With flag | deletion permitted only under the double gate (flag AND byte-identical correctly-labeled counterpart); direction-agnostic; both moments covered (FR-002/003/004) |
| Exit code | unchanged semantics; per-file deletion failure NEVER changes exit code or emitted output (FR-005) |
| Help text | one sentence fragment documenting opt-in deletion of mislabeled duplicates with byte-identity guard |
| Composability | orthogonal to `--target-dir/--output/--template-dir/--title`; no flag interactions |

## 2. Python Contract — `detect_images`

```python
def detect_images(target_dir, template_dir, cleanup=False):  # cleanup: keyword, defaulted
    """Returns the same mapping as today; cleanup only removes files never selected for emission."""
```

| Guarantee | Detail |
|---|---|
| Signature compat | `cleanup` is a defaulted parameter; existing two-positional-arg calls (`tests/scripts/test_extractor_contract_fixes.py:200`, production call site) remain valid and behaviorally unchanged (FR-006) |
| Return value | unchanged shape and values; with cleanup the returned/emitted paths are identical to a no-cleanup run over the same directory (INV-2 path-invariance) |
| Threading | `main()` passes `cleanup=args.cleanup_mislabeled_images` at the single production call site |

## 3. stderr Record Contract

| Event | Record |
|---|---|
| Deletion | exactly one line per deleted file, containing the word "delet", the removed path, and the retained survivor path |
| Deletion failure | exactly one line per failure with the path and OS error; extraction continues (best-effort) |
| No-op (flag, nothing eligible) | zero cleanup lines (AC-1e) |
| Without flag | zero cleanup lines; existing mismatch-recovery note unchanged |

Notes: records go to stderr only (stdout and `report-data.typ` untouched). Tests assert presence/absence and count of records, not exact prose — wording may be tuned without breaking the contract.

## 4. Test Harness Contract — `run_extract`

```python
def run_extract(target_dir, template_dir=None, extra_args=None):  # extra_args: list[str] appended to argv
```

Existing call sites unaffected (optional-with-default). Cleanup tests pass `extra_args=["--cleanup-mislabeled-images"]` to exercise the CLI path end-to-end.
