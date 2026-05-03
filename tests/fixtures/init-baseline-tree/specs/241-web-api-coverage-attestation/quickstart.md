# Quickstart: F-241 Web/API Coverage Attestation + Populator Wiring

**Feature**: 241 — F-8 + F-A3 Web/API Coverage Attestation + Populator Wiring [Tier 3]
**Created**: 2026-05-01
**Phase**: Plan / Phase 1 design artifact
**Purpose**: Verification walkthrough for reviewers and operators executing this feature

This document gives a step-by-step verification path for F-241's outputs. Run these commands in order on the `241-web-api-coverage-attestation` branch after the build is complete.

---

## Prerequisites

- `git checkout 241-web-api-coverage-attestation`
- Repository at the expected post-build state (Wave 6.3 complete)
- `pytest` available (already in dev deps per Feature 128 precedent)
- `gh` CLI authenticated for release-please verification

---

## Step 1: Verify Stream 1 — F-A3 populator wiring (14 of 14 detection-tier agents)

```bash
grep -l "source_attribution" .claude/agents/tachi/*.md | wc -l
# Expected: 14
```

```bash
grep -l "source_attribution" .claude/agents/tachi/*.md
# Expected output: 14 paths matching the 11 newly-wired hosts + 3 pre-existing F-1/F-2/F-4 net-new agents
# - .claude/agents/tachi/agent-autonomy.md
# - .claude/agents/tachi/data-poisoning.md
# - .claude/agents/tachi/denial-of-service.md
# - .claude/agents/tachi/human-trust-exploitation.md
# - .claude/agents/tachi/info-disclosure.md
# - .claude/agents/tachi/misinformation.md
# - .claude/agents/tachi/model-theft.md
# - .claude/agents/tachi/output-integrity.md
# - .claude/agents/tachi/privilege-escalation.md
# - .claude/agents/tachi/prompt-injection.md
# - .claude/agents/tachi/repudiation.md
# - .claude/agents/tachi/spoofing.md
# - .claude/agents/tachi/tampering.md
# - .claude/agents/tachi/tool-abuse.md
```

```bash
pytest tests/scripts/test_f_a3_populator_wiring.py -v
# Expected: All assertions pass; verifies 14/14 detection-tier coverage + line-count cap (≤200 lines per agent) + canonical pattern compliance.
```

## Step 2: Verify Stream 2 — Six Partial Web/API item closures

```bash
pytest tests/scripts/test_coverage_attestation_audit.py -v
# Expected: All assertions pass; verifies that:
# - Every "Covered" row in schemas/taxonomy/owasp.yaml has at least 1 agent + 1 detection-pattern category citation per BLP-01 §8 Quality Bar.
# - Each of A05, A06, API6, API8, API9, API10 has either a closure path or a Deferral ADR rationale + follow-on Issue.
```

```bash
# Verify Q-Plan-1 + Q-Plan-2 placement (manual spot-check)
grep -i "API6" .claude/skills/tachi-tool-abuse/references/detection-patterns.md
# Expected: At least one match indicating API6 closure path lands on tool-abuse host

grep -i "API9" .claude/skills/tachi-info-disclosure/references/detection-patterns.md
# Expected: At least one match indicating API9 closure path lands on info-disclosure host

grep -c "API9" .claude/skills/tachi-repudiation/references/detection-patterns.md
# Expected: 0 (Q-Plan-2 RESOLVED API9 to info-disclosure, not repudiation; companion stays byte-identical)
```

## Step 3: Verify Stream 3 — Taxonomy YAML expansion + record-shape extension

```bash
# Confirm record counts post-expansion
python -c "import yaml; print('owasp:', len(yaml.safe_load(open('schemas/taxonomy/owasp.yaml'))))"
# Expected: 60 (no new rows; F-241 audit-only)

python -c "import yaml; print('atlas:', len(yaml.safe_load(open('schemas/taxonomy/mitre-atlas.yaml'))))"
# Expected: ~30 (12 → ~30 expansion)

python -c "import yaml; print('attack:', len(yaml.safe_load(open('schemas/taxonomy/mitre-attack.yaml'))))"
# Expected: ~600 (38 → ~600 expansion with tactical-grouping Out-of-Scope)
```

```bash
# Confirm record-shape +2 fields are present on all records
python -c "
import yaml
for path in ['schemas/taxonomy/owasp.yaml', 'schemas/taxonomy/mitre-attack.yaml', 'schemas/taxonomy/mitre-atlas.yaml']:
    records = yaml.safe_load(open(path))
    has_oos_field = sum(1 for r in records if 'out_of_scope' in r)
    has_rationale_field = sum(1 for r in records if 'out_of_scope_rationale' in r)
    print(f'{path}: out_of_scope on {has_oos_field}/{len(records)}, rationale on {has_rationale_field}/{len(records)}')
"
# Expected: out_of_scope present on 100% of records; out_of_scope_rationale present on records with out_of_scope=true (or all if defaults are explicitly written)
```

```bash
# Confirm tactical-grouping Out-of-Scope rationale on TA0005/7/8/9/10/11/40 ATT&CK records
python -c "
import yaml
records = yaml.safe_load(open('schemas/taxonomy/mitre-attack.yaml'))
oos_count = sum(1 for r in records if r.get('out_of_scope', False))
print(f'ATT&CK Out-of-Scope items: {oos_count}/{len(records)}')
"
# Expected: oos_count is the count of all ATT&CK techniques inside TA0005/7/8/9/10/11/40 (typically ~250-350 of ~600 records)
```

## Step 4: Verify Stream 4 — Aggregator extension + 8-baseline regen

```bash
# Confirm pyyaml deferred-import invariant (KB-037 alignment)
pytest tests/scripts/test_pyyaml_deferred_import.py -v
# Expected: PASS — asserts `import yaml` remains inside function bodies in extract-report-data.py
```

```bash
# Confirm aggregator coverage-percentage computation
pytest tests/scripts/test_coverage_percentage_computation.py -v
# Expected: PASS — synthetic-fixture cross-check + real-baseline cross-check (8 baselines × 5 frameworks = 40 cross-check pairs); 0 percentage point delta
```

```bash
# Regenerate all 8 example baselines under fixed-epoch
SOURCE_DATE_EPOCH=1700000000 make regenerate
# Expected: 8 baselines regenerate without errors; 6 pre-existing baselines have non-CA pages byte-identical; 2 net-new baselines authored from scratch
```

```bash
# Confirm baseline byte-identity on non-CA pages (manual diff)
git diff --stat examples/web-app/security-report.pdf.baseline
# Expected: Only Coverage Attestation pages differ; non-CA pages byte-identical
```

```bash
# Visually inspect Coverage Attestation rendering on at least one baseline
open examples/web-app/security-report.pdf.baseline
# Expected:
# - Coverage Attestation section is non-empty
# - Per-finding attribution table has ≥1 row with OWASP / CWE / etc. citations
# - 5 framework pages each show:
#   * yaml-record-count: <total>
#   * in-scope-record-count: <total minus out-of-scope>
#   * covered-count, partial-count, gap-count
#   * coverage-percentage: e.g., "23.33%" (NOT "0.00%" or "N/A")
```

## Step 5: Verify Cross-Cutting — ADR-037 + §6 Coverage Matrix demotion

```bash
# Confirm ADR-037 exists and is Accepted
ls docs/architecture/02_ADRs/ADR-037-*.md
# Expected: exactly 1 file matching ADR-037-web-api-coverage-attestation-and-populator-wiring.md

grep -i "^status:" docs/architecture/02_ADRs/ADR-037-*.md
# Expected: status: Accepted (post-Day-27 dual-commit)
```

```bash
# Confirm §6 Coverage Matrix demotion annotation
grep -i "historical.*superseded.*pipeline-generated attestation" _internal/strategy/BLP-01-threat-coverage.md
# Expected: At least one match
```

```bash
# Confirm zero finding.yaml shape change
grep -E "^schema_version:" schemas/finding.yaml
# Expected: schema_version: "1.8" (unchanged from pre-F-241 state)
```

```bash
# Confirm zero new runtime dependencies
git diff main..HEAD -- pyproject.toml requirements*.txt package.json
# Expected: Empty diff (no new deps)
```

## Step 6: Verify Test Suite Health

```bash
pytest tests/scripts/ -v
# Expected: All test scripts pass green, including:
# - test_f_a3_populator_wiring.py (NEW)
# - test_coverage_attestation_audit.py (NEW)
# - test_coverage_percentage_computation.py (NEW)
# - test_pyyaml_deferred_import.py (NEW)
# - test_backward_compatibility.py (MODIFIED — 11-host enrichment branch update)
# - All pre-existing test scripts (regression check)
```

## Step 7: Verify F-7 28-File Detection-Tier Zero-Edit Invariant

```bash
# Confirm files outside F-241 scope remain byte-identical
git diff main..HEAD --name-only -- .claude/agents/tachi/ | grep -v -E "(spoofing|tampering|info-disclosure|privilege-escalation|repudiation|denial-of-service|tool-abuse|data-poisoning|model-theft|prompt-injection|agent-autonomy)"
# Expected: Empty (only the 11 F-A3 target hosts modified)
```

```bash
# Confirm companion catalogs outside Stream 2 scope remain byte-identical
git diff main..HEAD --name-only -- .claude/skills/ | grep -v -E "tachi-(privilege-escalation|info-disclosure|tampering|tool-abuse)/references/detection-patterns.md"
# Expected: Empty (only the 4 Stream 2 target catalogs modified)
```

## Step 8: Verify Release-Please R12 Compliance (post-merge only)

After PR #242 squash-merges with `feat(241):` Conventional Commits title:

```bash
gh pr list --state open --search "release-please" --limit 3
# Expected: A release-please PR opens within ~30s post-merge
# If empty, manually push an empty marker commit:
#   git commit --allow-empty -m "feat(241): Web/API Coverage Attestation + Populator Wiring — release marker"
#   git push origin main
```

---

## Success Criteria Mapping

The verification steps map to spec.md success criteria:

| Step | Verifies SC |
|------|------------|
| 1 | SC-001 (14/14 wiring), SC-003 (line-count cap), SC-017 (test scripts green) |
| 2 | SC-005 (Partial item closure), SC-006 (citation evidence), SC-017 |
| 3 | SC-008 (taxonomy inventories), SC-014 (record-shape +2 fields backward-compat) |
| 4 | SC-007 (8/8 baselines render), SC-009 (0 ppt delta), SC-013 (no new deps), SC-015 (byte-identity), SC-017 |
| 5 | SC-010 (matrix demotion), SC-011 (ADR-037 Accepted), SC-014 (finding.yaml unchanged), SC-013 |
| 6 | SC-012 (test suite health), SC-017 |
| 7 | SC-003 (line-count cap), FR-021 (28-file zero-edit invariant) |
| 8 | SC-016 (release-please R12) |

All 18 SCs (SC-001..SC-018) reachable via this quickstart sequence.

---

## Failure Modes & Recovery

| Symptom | Likely Cause | Recovery |
|---------|-------------|----------|
| `grep ... \| wc -l` returns < 14 | One or more F-A3 target host files missing wiring | Re-author missing host's populator block; re-run Step 1 |
| `test_coverage_percentage_computation.py` fails with non-zero ppt delta | Aggregator denominator filter not applied OR fixture mismatch | Inspect `_build_per_framework_aggregate()` for Out-of-Scope filter; verify fixture matches expected math |
| Baseline regen fails with `pyyaml` import error at module load | Stdlib-only module-load invariant violated | Move `import yaml` inside function body in `extract-report-data.py`; re-run `test_pyyaml_deferred_import.py` |
| Non-CA pages of pre-existing baselines differ post-regen | `SOURCE_DATE_EPOCH` not set OR upstream tooling change introduced churn | Set `SOURCE_DATE_EPOCH=1700000000` explicitly; investigate any non-CA-page churn as regression |
| ADR-037 review pending past Day 27 | Architect disagreement on Q-PM-1 single-vs-split resolution | Re-engage Architect; document split-ADR alternative as ADR-037-companion if joint disagreement persists |
| 1–2 Partial items deferred (Risk 3 from PRD) | API6 or API9 not closeable under existing-pattern + new-Indicator allowance | Add Deferral D-numbered decision to ADR-037; create follow-on GitHub Issue; annotate §6 Coverage Matrix accordingly |

---

## References

- spec.md — feature specification (PM APPROVED_WITH_CONCERNS)
- plan.md — implementation plan (this directory)
- data-model.md — entity shapes (this directory)
- contracts/finding-contract.md — populator + aggregator contracts (this directory)
- ADR-037 — public per-feature ADR (NEW; documents 10 decisions)
- BLP-01 strategic plan §6 — coverage matrix annotated historical post-F-241
