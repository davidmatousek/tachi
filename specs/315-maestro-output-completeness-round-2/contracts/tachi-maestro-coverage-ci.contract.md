# Contract: tachi-maestro-coverage CI job (Story 2 / US-3 / #313)

**Type**: GitHub Actions workflow contract. New file: `.github/workflows/tachi-maestro-coverage.yml`. Modeled on the `.github/workflows/tachi-mmdc-preflight.yml` **file precedent** (dedicated single-concern job). (ADR-022 governs the mmdc/Typst toolchain prerequisite, not the CI-job shape.)

## Job shape

- **Runner**: `ubuntu-latest` (single OS — the invariant is a markdown-glob assertion, OS-independent).
- **Setup**: `actions/setup-python@v5` (Python 3.11); `pip install pytest pytest-timeout`.
- **Invocation**: `python -m pytest tests/scripts/test_maestro_coverage_invariant.py -v`.
- **Check name**: a distinct name (e.g. `tachi maestro coverage`) so a <7-row regression is self-explaining in the PR checks UI.

## Trigger contract (lock-step with the invocation — F-250 rule)

The test reads **committed** `examples/**/threats.md`, so `paths:` is two-tiered:

```
# regression-necessary (a change here can alter a committed example matrix)
- tests/scripts/test_maestro_coverage_invariant.py
- examples/**/threats.md
- scripts/tachi_parsers.py                       # MAESTRO_LAYERS
- scripts/populate-maestro-coverage.py           # the tool that rewrites example tables
- .github/workflows/tachi-maestro-coverage.yml

# defense-in-depth (optional) — author/parse the PRODUCTION matrix, do not change committed examples
- scripts/extract-report-data.py
- .claude/agents/tachi/orchestrator.md
- templates/tachi/security-report/maestro-findings.typ
```

Any future addition to the MAESTRO test set or example-author surface updates BOTH `paths:` and the pytest invocation in the same commit (F-250 lock-step). tasks.md finalizes whether to keep the defense-in-depth tier.

## Behavioral guarantees

1. **Fails on regression**: if any in-scope `examples/**/threats.md` MAESTRO table has fewer than 7 canonical layers, the job exits non-zero and the test output **names the missing layer ID(s)**.
2. **Green on current set**: passes against the current examples (all matrices complete at 7 rows).
3. **No cross-firing (NFR-4)**: a change to an unrelated (non-MAESTRO) file does NOT trigger this job, and **does not modify `tachi-pytest.yml`'s `paths:` or invocation** — the existing job's scope is untouched.
4. **Skips table-less files**: examples without a MAESTRO table are skipped (not failed).

## Verification

- Force a <7-row table in a temporary example/fixture → job fails naming the layer.
- Touch an unrelated file → job does not run; `tachi-pytest.yml` unchanged.
- Remove the `intentionally NOT wired into CI` note from the test docstring (FR-007).

## Non-goals

- Does NOT fold into `tachi-pytest.yml` (Decision A).
- Does NOT change the byte-gated baselines or the backward-compat job.
