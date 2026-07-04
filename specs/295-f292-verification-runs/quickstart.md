# Quickstart: F-295 Verification Runs Execution Runbook

**Plan**: [plan.md](plan.md) | Contracts: [oi-extraction](contracts/oi-extraction-contract.md), [regen-byte-identity](contracts/regen-byte-identity-contract.md)
Serial order is mandatory (FR-021): Stage 0 → 1 → 2 → 3. Attempt cap 2 per live run, then M-1 escape hatch.

## Stage 0 — Pre-state (FR-019; BLOCKS all commits)

```bash
# Literal totals per D-E suite (record verbatim in test-results/pre-state.md)
python3 -m pytest tests/scripts/test_backward_compatibility.py -v --timeout=1080   # incl. slow PDF suite (local-only)
python3 -m pytest tests/scripts/test_maestro_coverage_invariant.py tests/scripts/test_maestro_cross_surface_consistency.py -v
python3 -m pytest tests/scripts/test_catalog_drift_guard.py -v
python3 -m pytest tests/scripts/test_affected_assets_wiring.py -v
# Corpus-coupling sweep (glob/count-pin assertions over examples/**)
grep -rn "examples/\*\*\|glob.*examples\|BASELINE_EXAMPLES\|len(.*examples" tests/ --include="*.py" | grep -v test-output
```
Commit `specs/295-f292-verification-runs/test-results/pre-state.md` (totals + sweep + inherited-red dispositions) BEFORE anything else.

## Stage 1 — T017 / US-1 (SC-003)

```bash
# 1. Anchor extraction + guard (expect exactly OI-1..OI-4)
git show 0629fa2~1:examples/agentic-app/sample-report/threats.sarif \
  | jq '[.runs[0].results[] | select(.partialFingerprints["findingId/v1"] // "" | startswith("OI-"))]' \
  > specs/295-f292-verification-runs/test-results/anchor-oi-subset.json
jq 'length' specs/295-f292-verification-runs/test-results/anchor-oi-subset.json   # MUST print 4; else gate ERROR
```
2. **Fresh run (primary)**: dispatch `tachi-output-integrity` (Agent tool) with orchestrator-shaped context — target components + full `examples/agentic-app/architecture.md` + OI scope. Save raw YAML verbatim to `test-results/t017-fresh-findings.yaml`. *(Fallback attempt 2: scoped-full run `report: false`; use its native threats.sarif.)*
3. **Assemble + extract**: `python3 specs/295-f292-verification-runs/tools/assemble_oi_sarif.py test-results/t017-fresh-findings.yaml > test-results/fresh-oi.sarif`, then same jq → `fresh-oi-subset.json`; guard non-empty.
4. **D-1 gate + attribution** per [contract §4–§5](contracts/oi-extraction-contract.md); build the sink/flow identity table; run the bounded `git log -p 0629fa2..HEAD -- <surfaces>` walk for any drift.
5. **Record + file**: `sc-003-verification-record.md`; FR-008 contract dual-defect Issue (always); FR-007 defect Issue only on FAIL; check T017 box on #295.

## Stage 2 — T026 / US-2 (SC-015)

```bash
# 3a. URI enabler FIRST (P0 commit, independent of run outcome)
#   - generate-threats-sarif.py: derive artifactLocation.uri from input path (build_result, :481)
#   - covering assertion in tests/scripts/test_affected_assets_wiring.py
#   - add scripts/generate-threats-sarif.py to tachi-pytest.yml &hardening_paths (lock-step)
#   - L-a proof: script-output-before vs script-output-after on agentic-app threats.md (byte-identical)
python3 scripts/generate-threats-sarif.py examples/agentic-app/sample-report/threats.md /tmp/agentic-before.sarif  # pre-change
# ...apply URI change...
python3 scripts/generate-threats-sarif.py examples/agentic-app/sample-report/threats.md /tmp/agentic-after.sarif
cmp /tmp/agentic-before.sarif /tmp/agentic-after.sarif   # MUST be identical (uri input is the same file)
```
1. **Run** (session): `/tachi.threat-model examples/multi-tenant-rag-app/architecture.md --output-dir examples/multi-tenant-rag-app/test-output/` with `SOURCE_DATE_EPOCH=1700000000` exported (convention). Phase 5 ON. Overflow fallback: staged per-skill (`/tachi.risk-score` …).
2. **Cat 6 gate**: committed-run `threats.md` MUST show ≥1 `OI-*` Cat 6 finding (CWE-943, Pinecone `tenant_id` omission shape). Zero ⇒ defect Issue; STOP (no baseline commit; US-3 defers).
3. **Baseline commit**: copy `threats.md threat-report.md risk-scores.md risk-scores.sarif` from the timestamped run dir to `examples/multi-tenant-rag-app/`; then:
```bash
python3 scripts/generate-threats-sarif.py examples/multi-tenant-rag-app/threats.md examples/multi-tenant-rag-app/threats.sarif
python3 scripts/generate-threats-sarif.py examples/multi-tenant-rag-app/threats.md /tmp/regen-check.sarif
cmp examples/multi-tenant-rag-app/threats.sarif /tmp/regen-check.sarif      # FR-011 byte-identity
grep -c "^| L[1-7] " examples/multi-tenant-rag-app/threats.md               # MAESTRO all-7 shape (FR-012)
jq -r '.runs[0].results[0].locations[0].physicalLocation.artifactLocation.uri' examples/multi-tenant-rag-app/threats.sarif  # MUST be examples/multi-tenant-rag-app/threats.md
```
4. Verify README row (FR-013), commit exactly 5 artifacts + T026 record; file risk-scores parameterization enhancement Issue.

## Stage 3 — US-3 / P1 (only if Stage 2 regen check passed — FR-018)

1. `tests/scripts/test_sarif_regen_identity.py` per [contract §1](contracts/regen-byte-identity-contract.md) (fail-closed).
2. `.github/workflows/tachi-sarif-regen.yml` with the exact 6-path anchor ([contract §3](contracts/regen-byte-identity-contract.md)) — paths + invocation, one commit.
3. Local: `python3 -m pytest tests/scripts/test_sarif_regen_identity.py -v` green; PR body carries the FR-017 coverage-boundary statement.

## Escape hatches & honesty rules

- 2 tooling-failed attempts on any live run ⇒ file tooling defect, close story on staged-partial record (M-1/FR-021).
- Gate failures are the runs *working*: file the defect with evidence, record honestly, #295 still closes (KB Entry 17).
- Never hand-edit committed artifacts; never touch detection-tier files or the archived 292 contract (FR-020).
