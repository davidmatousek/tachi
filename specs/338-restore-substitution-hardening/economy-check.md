# Economy Gate — Feature 338

**Timestamp**: 2026-06-30 UTC
**Verdict**: PASSED — no over-build found
**Scope**: 1 changed code file in the restore commit (`scripts/init.sh`; the 2 `.aod/scripts/bash/*.sh` are diff-scoped code but excluded from the SAST/economy code-file set under the pinned `.aod/` exclusion). Advisory, diff-scoped (`git diff main...HEAD`).

## Assessment against the laziness ladder (`.claude/rules/code-economy.md`)

This feature is a **restoration**, which sits at the most economical rungs of the ladder:

- **Rung 1 (spec requires it)**: the restore is a shipped-regression fix mandated by spec.md FR-001..005/FR-009 — not speculative.
- **Rung 2 (reuse existing code)**: the 3 script bodies are restored via `git checkout 5b64f68 -- <file>` and are **byte-identical** to known-good v4.44.0 (T007 confirmed empty diff). Zero net-new logic, zero new abstraction.
- **Rung 5 (no new dependency)**: no dependencies added (plan Technical Context: "Primary Dependencies: none added").
- The `defaults.env` changes are **surgical 1-line key edits** (add `TECH_STACK`, remove `ORCHESTRATION_TARGET`), the minimum to satisfy the restored whitelist loader's exact-set check (FR-009 / OQ-3) — not a whole-file rewrite.

## Carve-out survival (Section 1)

No safety carve-out was shortened by a simplification. The opposite: the restore **re-establishes** input validation (F-248 parameter-expansion + value-class checks), config-load hardening (F-256 `aod_template_load_kv_file` whitelist parser replacing `source`), and the clone-timeout watchdog (`AOD_FETCH_TIMEOUT`). Error handling (exit 8 on disallowed/missing key) is restored, not removed.

## Conclusion

No over-build. The change is the minimal restore of tested known-good code that satisfies the spec and strengthens (does not trade away) every safety carve-out. **PASSED.**
