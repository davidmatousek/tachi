# Economy Gate — F-333 Citation-URL Remediation

**Status**: Passed — no over-build found
**Scope**: 2 changed code files (`git diff main...HEAD`, advisory): `scripts/check-citation-urls.py`, `tests/schemas/test_citation_linkrot_parity.py`
**Method**: Inline judgment (Step 8b — trivially small diff: +25/−0 LOC in the script + 61 test lines; over-engineering already assessed by the T016 binding code-review gate).
**Timestamp**: 2026-06-29

## Verdict

No over-build. The change sits at the correct laziness-ladder rungs:

- **Rung 1 (spec requires)**: FR-002 mandates the ATLAS host-scoped re-classify; FR-008 mandates the synthetic-404 test. Nothing speculative.
- **Rung 2 (reuse existing)**: the override reuses the existing `_verdict_for_status` function, the `_classification` helper, and the `Verdict` enum — no new helper, class, or abstraction invented. The architect confirmed no `classify_one()` refactor was needed.
- **Rung 3 (stdlib)**: host extraction uses `urllib.parse.urlsplit` (already imported), not a hand-rolled parser or a new dependency.
- **Minimal form**: a bounded module-level dict (`_HOST_STATUS_OVERRIDES`) + a 3-line guard. One host entry — the Rule of Three is respected, not pre-generalized into a config system.
- The NIST/OWASP fixes are pure in-place string-value replacements (no tooling, no auto-rewriter — explicitly out of scope).

## Safety carve-outs intact (not shortened for brevity)

- **Determinism boundary (ADR-021)**: the new logic is offline-unit-tested over synthetic statuses; no network on any PR/push path.
- **NFR-005 signal quality**: global `_HARD_ROT_STATUSES` / `_NEEDS_REVIEW_STATUSES` frozensets untouched; the override is host- and status-scoped (a genuine 410/451 on the same host still flags).
- **Input handling**: `urlsplit(url).hostname or ""` guards a `None` host.

Zero new runtime dependencies (NFR-002). No `AOD-SIMPLIFICATION` marker needed — nothing was intentionally deferred below spec.
