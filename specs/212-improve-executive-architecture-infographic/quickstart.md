# Quickstart — Feature 212 Local Regeneration & Validation

**Feature**: 212 — Improve Executive-Architecture Infographic
**Audience**: developer implementing F-212 or reviewing the rendered output

## Prerequisites

- Python 3.11+ with tachi repo dependencies installed
- `SOURCE_DATE_EPOCH=1700000000` export for determinism checks (ADR-021)
- Local access to `~/Projects/second-brain-mcp/docs/security/2026-04-23T23-02-25/` (primary reference dataset) OR use in-repo fallback at `tests/scripts/fixtures/exec_arch/agentic_app/`
- Gemini API credentials configured (existing — see `docs/devops/` for setup)
- `openclaw-agent-threat-model-infographic.jpg` reference asset accessible (human-review target — not bundled with tachi)

## Level 1 — Regenerate reference image with new prompt

```bash
# From tachi repo root
export SOURCE_DATE_EPOCH=1700000000

# Extract the payload
python scripts/extract-infographic-data.py \
  --threats ~/Projects/second-brain-mcp/docs/security/2026-04-23T23-02-25/threats.md \
  --template executive-architecture \
  --out /tmp/f212/threat-executive-architecture-spec.md

# Trigger Gemini image generation via the tachi-infographic agent
# (agent reads the spec .md and invokes Gemini with the VERBATIM-locked prompt)
# See .claude/agents/tachi/threat-infographic.md for exact invocation

# Compare regenerated JPG to openclaw reference visually
open /tmp/f212/threat-executive-architecture.jpg
open openclaw-agent-threat-model-infographic.jpg
```

**Validation checklist (SC-212-1 — 4 structural criteria)**:
- [ ] Components render as rounded-rectangle nodes (not floating text)
- [ ] Directional arrows with explicit arrowheads connect layers
- [ ] Callouts have leader lines pointing to specific nodes
- [ ] ≥5 callouts visible on the page

If Phase 1 cannot reach 3/4 after 2 iterations → invoke Risk R1 contingency (re-prioritize L3 ahead of L1).

## Level 2 — Verify callout density and floor rule

```bash
# Run the Level-2 fixture matrix
pytest tests/scripts/test_extract_infographic_data.py -k per_layer_floor -v

# Run determinism check
pytest tests/scripts/test_extract_infographic_data.py -k deterministic -v

# Manual inspection of reference dataset output
python scripts/extract-infographic-data.py \
  --threats ~/Projects/second-brain-mcp/docs/security/2026-04-23T23-02-25/threats.md \
  --template executive-architecture \
  --out /tmp/f212/ && \
  python -c "
import json, sys
with open('/tmp/f212/threat-executive-architecture-spec.md') as f:
    # Extract JSON payload block from .md file
    # (exact parsing depends on spec-md format; adapt as needed)
    pass
"
```

**Validation checklist (SC-212-3, SC-212-4)**:
- [ ] `callouts[]` length is 6, 7, or 8 on the 9-qualifying-finding reference dataset
- [ ] Every qualifying layer is represented with ≥1 callout (per-layer floor rule)
- [ ] No single layer has > 4 callouts (per-layer ceiling)
- [ ] Layers exceeding 4 have `layer_overflow: "+ N more in this layer"` annotation

## Level 3 — Verify payload schema extension

```bash
# Run the L3 drift-guard fixture matrix
pytest tests/scripts/test_executive_architecture_payload.py -v

# Verify the prompt co-landing (reads skill reference file and asserts flow_edges/clusters present)
pytest tests/scripts/test_executive_architecture_payload.py -k prompt_co_landing -v

# Determinism across two runs on identical input
python scripts/extract-infographic-data.py \
  --threats tests/scripts/fixtures/exec_arch/agentic_app/threats.md \
  --template executive-architecture \
  --out /tmp/f212a/
python scripts/extract-infographic-data.py \
  --threats tests/scripts/fixtures/exec_arch/agentic_app/threats.md \
  --template executive-architecture \
  --out /tmp/f212b/
diff /tmp/f212a/threat-executive-architecture-spec.md /tmp/f212b/threat-executive-architecture-spec.md
# Should produce no output (byte-identical)
```

**Validation checklist (SC-212-5, SC-212-6)**:
- [ ] Payload contains `flow_edges` key (always)
- [ ] Payload contains `clusters` key (always)
- [ ] On populated input: `flow_edges[0]` has `destination` key (not `target`)
- [ ] On populated input: `clusters[0]` has `members` key (populated from `components`)
- [ ] On absent-section input: both arrays are `[]` (not `null`, not missing)
- [ ] Two consecutive runs produce byte-identical payload JSON

## Integration — PDF byte-identity on zero-finding input (SC-212-7)

```bash
# Generate pre-F-212 baseline PDF on a zero-finding fixture
git checkout main
export SOURCE_DATE_EPOCH=1700000000
# Run full pipeline with zero-finding threats.md → save as baseline.pdf

# Switch back to feature branch
git checkout 212-improve-executive-architecture-infographic
# Run full pipeline with same zero-finding threats.md → save as feature.pdf

# Compare
cmp baseline.pdf feature.pdf
# Should produce no output (byte-identical)
```

If PDFs differ on zero-finding input → F-128 skip-behavior contract broken. Bug-fix required; do not merge.

## Full end-to-end regeneration (Phase 4 delivery gate)

```bash
# From scratch with all three levels landed
export SOURCE_DATE_EPOCH=1700000000

# Regenerate reference image
python scripts/extract-infographic-data.py \
  --threats ~/Projects/second-brain-mcp/docs/security/2026-04-23T23-02-25/threats.md \
  --template executive-architecture \
  --out /tmp/f212-final/

# Trigger image generation via tachi-infographic agent
# (see agent docs)

# Pixel-height measurement for empty-layer waste (SC-212-2)
# (manual; use image measurement tool on /tmp/f212-final/threat-executive-architecture.jpg)

# Run full test suite
pytest tests/scripts/test_extract_infographic_data.py -v
pytest tests/scripts/test_executive_architecture_payload.py -v
```

**Final delivery checklist (all SCs)**:
- [ ] SC-212-1 (structural parity 4/4)
- [ ] SC-212-2 (empty-layer waste ≤15%)
- [ ] SC-212-3 (6–8 callouts on reference dataset)
- [ ] SC-212-4 (per-layer floor-rule tests pass)
- [ ] SC-212-5 (payload schema tests pass)
- [ ] SC-212-6 (determinism byte-identical)
- [ ] SC-212-7 (PDF byte-identity on zero-finding)
- [ ] SC-212-8 (runtime ≤10% regression)

## Troubleshooting

- **Gemini returns text-only image (failure mode)**: Prompt does not begin with "schematic diagram with shapes and arrows" directive. Verify verbatim-locked prompt text in `executive-architecture.md`.
- **Callout count is 2 instead of 6–8**: L2 change not applied; still running per-layer-dedup. Check `_select_critical_high_callouts()` version.
- **Payload missing `flow_edges` / `clusters`**: L3 change not applied or `parse_scope_data` returned empty. Check input `threats.md` has `### Data Flows` and `### Trust Boundaries` sections.
- **Determinism test fails**: Likely unsorted iteration over a dict/set. Verify sort pattern matches `_compute_trust_zones` (case-folded + trust-level order).
- **`flow_edges[0]` has `target` key instead of `destination`**: L3 field-name lock broken. Fix at `_build_flow_edges()` return — must emit `destination` to match producer.
- **PDF byte-identity fails on zero-finding**: F-128 skip-behavior contract broken. Check the `has-executive-architecture` gate still evaluates to `false` when zero qualifying findings.
