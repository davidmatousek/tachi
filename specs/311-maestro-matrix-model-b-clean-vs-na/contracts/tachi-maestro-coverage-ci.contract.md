# Contract: `tachi-maestro-coverage.yml` extension (F-250 lock-step)

**Feature**: 311 · **Surface**: `.github/workflows/tachi-maestro-coverage.yml` + its pytest invocation · **Spec**: FR-011 · **Precedent**: F-315 dedicated job + F-250 lock-step rule

Model B adds the cross-surface consistency assertion (see `cross-surface-consistency.contract.md`) to the **existing** dedicated MAESTRO job — it does NOT create a new workflow. The job shape (ubuntu-latest, `setup-python@v5` 3.11, `pip install pytest pytest-timeout`) is unchanged.

## Lock-step requirement (F-250 — non-negotiable)

Any addition to the MAESTRO test set or author/parse surface MUST update **BOTH** the workflow `on.pull_request.paths` list AND the pytest invocation **in the same commit**, or the gate goes false-green.

## Required `paths:` additions for Model B (regression-necessary)

The consistency assertion reads committed example render IR / threats.md, so changes to any author/parse surface are regression-relevant:

```
# already present (F-315): tests/scripts/test_maestro_coverage_invariant.py,
#   examples/**/threats.md, scripts/tachi_parsers.py,
#   scripts/populate-maestro-coverage.py, .github/workflows/tachi-maestro-coverage.yml
# Model B adds (regression-necessary or defense-in-depth):
scripts/extract-report-data.py                              # emits PDF coverage_state
scripts/extract-infographic-data.py                         # emits infographic coverage_state
templates/tachi/security-report/maestro-findings.typ        # PDF n/a render branch
templates/tachi/infographics/infographic-maestro-stack.md   # infographic n/a band state
.claude/agents/tachi/orchestrator.md                        # authors the Section-6 token
tests/scripts/test_extract_infographic_data.py              # coverage_state + backfill-survival
tests/scripts/test_extract_report_data.py                   # coverage_state + ordinal-0
tests/scripts/fixtures/golden/maestro-stack.json            # regenerated golden
```

(The exact regression-necessary vs defense-in-depth split is finalized in tasks.md, mirroring the F-315 Decision-A two-tier model.)

## Invocation

```
python3 -m pytest tests/scripts/test_maestro_coverage_invariant.py -v
```

If the consistency assertion is authored in a separate test module (e.g. `test_maestro_cross_surface_consistency.py`), the invocation MUST list it too, and `paths:` MUST include it (lock-step).

## Acceptance

- **Given** the current example set, **When** the job runs, **Then** it passes green (all-7-rows present AND all three surfaces agree on `microservices`).
- **Given** a forced cross-surface divergence, **When** the job runs, **Then** it fails naming the layer ID.
- **Given** a change to `extract-infographic-data.py`, **When** a PR touches it, **Then** the job fires (path present); the `tachi-pytest.yml` bash-matrix trigger surface is unchanged (no cross-firing — F-315 NFR-4).
