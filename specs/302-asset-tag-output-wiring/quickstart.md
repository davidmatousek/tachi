# Quickstart: Verifying Asset-Tag Output Wiring (F-260b)

**Feature**: 302 | **Plan**: [plan.md](plan.md) | **Contract**: [contracts/affected-assets-contract.md](contracts/affected-assets-contract.md)

End-to-end verification recipe mapping each Success Criterion to a concrete check. Worked example: `examples/agentic-app/architecture-with-asset-tags.md` (carries `pii`, `phi`, `auth`, `safety` across 4 components) + unit fixtures for `secrets`, `financial`.

## Prerequisites

- On branch `302-asset-tag-output-wiring`; feature implemented.
- `SOURCE_DATE_EPOCH=1700000000` exported for any baseline regeneration.

## 1. Schema field + version bump (SC-001)

```bash
grep -A3 affected_assets schemas/finding.yaml   # → enum array with the 6 values + default []
grep schema_version schemas/finding.yaml        # → 1.9
```

## 2. Schema-stability byte-identity (SC-002)

```bash
SOURCE_DATE_EPOCH=1700000000 <regenerate no-tag baseline>
git diff -- examples/.../threats.md              # → ONLY the added affected_assets block (tables unchanged)
git diff -- examples/.../*.sarif                 # → ONLY added "affected_assets": [] entries
```

## 3. Per-tag propagation, all 6 tags (SC-003)

```bash
pytest tests/scripts/test_affected_assets_wiring.py -k propagation -q
# Asserts pii/phi/auth/safety via the worked example; secrets/financial via fixtures.
# Includes the no-op-modifier case: a `financial` tag on a finding already at I:H
# still lists `financial` in affected_assets (Q4 asset-exposure semantic).
```

## 4. Ceiling preserved (SC-004) + no scoring regression (NFR-2)

```bash
pytest tests/scripts/test_affected_assets_wiring.py -k ceiling -q   # no finding > 9.2; affected_assets populated regardless of clamp
# Score-equivalence: composite/severity unchanged vs the v4.31.0 worked example.
```

## 5. Empty-tag default (SC-005)

```bash
<run on a no-tag architecture>
# threats.md block shows `<id>: []` for every finding; both SARIFs show "affected_assets": [].
```

## 6. Cross-format consistency — the key gate (SC-006)

```bash
pytest tests/scripts/test_affected_assets_wiring.py -k cross_format -q
# Multi-finding (≥2 differently-tagged components + ≥1 untagged): asserts a per-finding
# equality table across the threats.md block, generate-threats-sarif.py, and
# generate-risk-scores-sarif.py — EVERY finding (incl. untagged []) byte-identical;
# the literal `affected_assets` key string is identical in both SARIF surfaces.
# NOTE (architect Pre-Mortem): production .sarif is LLM-authored. The equality table is the
# deterministic REFERENCE; SC-002 byte-identity against regenerated baselines is what pins the
# LIVE orchestrator/risk-scorer output to that reference. Production NFR-3 is test-checked, not structural.
```

## 7. Schema-doc accuracy (SC-007)

```bash
# asset-modifiers.md Output Contract section: enum + empty-default + per-format shape
# match emitted output for the worked example. Stale "9.5" in the T-2 example corrected to 9.2.
grep -n "9.5" .claude/skills/tachi-risk-scoring/references/asset-modifiers.md   # → no stale 9.5 ceiling
```

## 8. CI runs the suite (SC-008)

```bash
grep test_asset_sensitivity_tags .github/workflows/tachi-pytest.yml   # → matches in BOTH paths: filter AND pytest invocation
```

## 9. Release cadence (SC-009) + community credit (SC-010) — delivery-time

```bash
# PR title feat(302): ; CHANGELOG feat: entry naming @north-echo + PR #262.
# Post-merge: gh pr list --state open --search "release-please"  (within ~30s).
# Issue #302 close comment records the credit URL; Discussion #246 referenced.
```

## 10. Frozen constraints untouched (SC-011) + issues closed (SC-012)

```bash
git diff main -- schemas/risk-scoring.yaml scripts/tachi_parsers.py
# → NO change to VALID_ASSET_TAGS, modifier_ceiling: 9.2, or modifier-after-clamp ordering.
gh issue view 302 ; gh issue view 260   # → both CLOSED; #260 close comment links the F-260b PR + credits @north-echo
```

## Definition of Done (gates)

- All SC-001…SC-012 verifications pass.
- `test_asset_sensitivity_tags.py` (26 cases) + `test_affected_assets_wiring.py` green in CI.
- SC-006 cross-format equality + SC-002 byte-identity are the two hard correctness gates.
- SC-011 binary diff is clean (no frozen-constraint drift).
- **Live-pipeline check (R9 / architect Pre-Mortem #1)**: a real `tachi.threat-model` run on the tagged worked example emits `affected_assets` in `threats.md`, `threats.sarif`, AND `risk-scores.sarif` — not just the regeneration scripts. "Shipped, adopters see nothing" is the failure this gate prevents.
