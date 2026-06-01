# Contract: `affected_assets` Cross-Format Output

**Feature**: 302 (F-260b) | **Plan**: [../plan.md](../plan.md) | **Data model**: [../data-model.md](../data-model.md)

This is the authoritative contract for the `affected_assets` field across all three output surfaces. The cross-format byte-equivalence here is the single most important correctness invariant (NFR-3).

---

## 1. Schema contract — `schemas/finding.yaml`

```yaml
# Asset Sensitivity (v1.9 — Feature 260b / PR #262)
# Additive, always-present-with-default field (minor bump per ADR-026; additive-field
# precedent ADR-028; populator precedent ADR-037). Default [] is ALWAYS emitted
# (agentic_pattern/maestro_layer precedent — NOT source_attribution's omit-when-empty).
# Modifier logic (CVSS impact-bit floors, 9.2 ceiling) lives FROZEN in risk-scoring.yaml.
affected_assets:        # array<enum>, default []
  - pii | phi | auth | secrets | financial | safety
```

- `schema_version` MUST read `1.9`.
- Enum domain FROZEN at 6 values. Array MUST be sorted ascending, deduped.
- MUST validate: an empty array is valid and is the default.

## 2. threats.md contract — appended `affected_assets` block

- The existing STRIDE (§3) and AI (§4) finding **tables are unchanged** (byte-stable).
- A new always-present block serializes `affected_assets` per finding ID. Every finding in §3/§4 MUST appear in the block; findings with no tags appear with `[]`.
- The block MUST be deterministically authored by the populator (AD-1), NOT by the orchestrator LLM.
- Exact block syntax (fenced YAML vs. list) is finalized at build; it MUST be parseable by `parse_affected_assets()` and MUST key by the finding ID used in §3/§4 (e.g. `S-1`, `AG-2`, `LLM-3`).

Reference shape (illustrative):

```yaml
# affected_assets (Feature 260b) — sorted enum tags per finding; [] when none
S-1: [phi, pii]
T-2: []
LLM-1: [secrets]
```

## 3. SARIF contract — `result.properties.affected_assets` (both SARIF surfaces)

Applies to both `threats.sarif` and `risk-scores.sarif`. **Production** `.sarif` is LLM-authored — `threats.sarif` by the orchestrator (per `sarif-specification.md`), `risk-scores.sarif` by the risk-scorer (per `risk-scorer.md` SARIF section) — each **copying the single `threats.md` block value verbatim**. The `generate-*-sarif.py` scripts are the **regeneration/verification tier** (baselines/tests), not the live emitters. Per affected `result` object:

```json
"properties": {
  "affected_assets": ["phi", "pii"]
}
```

- Literal property key MUST be `affected_assets` (snake_case) — byte-identical in **both** emitters. MUST NOT adopt the surrounding kebab/camel key-casing drift.
- Value MUST be a flat array of enum strings (Q3), sorted, sourced verbatim from the shared `parse_affected_assets(threats_content)` extractor (NOT re-derived from `component_asset_map`).
- Untagged findings MUST emit `"affected_assets": []` (present, not omitted).
- Placed in `result.properties` (OASIS-sanctioned property bag; GitHub Code Scanning ignores unknown properties gracefully). MUST NOT collide with the reserved `tags` key.

## 4. Invariants (production NFR-3 = baseline/test-checked, enforced by SC-006 + SC-002)

For **every** finding `f` (including untagged):

```
threats_block(f.id)                          ← deterministic value authority (populator)
  == threats_sarif(f).properties.affected_assets        (LLM copy, production)
  == risk_scores_sarif(f).properties.affected_assets    (LLM copy, production)
  == finding.yaml(f).affected_assets schema shape
```

— same elements, same sort order, same `affected_assets` key string. Divergence is a defect. The `threats.md` block is the deterministic source; the production SARIF surfaces copy it. Because production `.sarif` is LLM-authored, this equality is **test-enforced** (SC-006 multi-finding equality table + SC-002 byte-identity against regenerated baselines) — NOT structural-by-construction. The `parse_affected_assets()` extractor + regeneration scripts provide the deterministic reference the tests compare against.

## 5. Frozen (MUST NOT change) — SC-011 binary diff gate

- `VALID_ASSET_TAGS` (6-tag tuple) in `scripts/tachi_parsers.py`
- `modifier_ceiling: 9.2` and the `asset_modifiers` table in `schemas/risk-scoring.yaml`
- The modifier-after-clamp ordering (risk-scorer §3.5)
- `risk-scoring.yaml` `schema_version` (stays `1.1`)
