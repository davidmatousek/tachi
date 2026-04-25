# T019 — US2 Callout Count Verification (SC-212-3)

**Generated**: 2026-04-25
**Task**: T019 (Wave 3, US2)
**Target dataset**: `~/Projects/second-brain-mcp/docs/security/2026-04-23T23-02-25/`
**Template**: executive-architecture
**Env**: `SOURCE_DATE_EPOCH=1700000000`
**Python**: cpython-3.12.11 (uv-managed)

## SC-212-3 Determination: **FAIL**

Callout count = **5**. SC-212-3 requires `len(callouts) ∈ [6, 7, 8]`.

The L2 algorithm (post T016+T017 at HEAD `df4ced8`/`scripts/extract-infographic-data.py`) is functioning as specified by FR-212-9 (per-layer ceiling = 4), but on this specific dataset the ceiling combined with finding distribution caps the callout count at 5 — below the SC-212-3 lower bound of 6.

## Summary

| Field | Value |
|---|---|
| Callout count (post-F-212) | **5** |
| Pre-F-212 callout count baseline | 2 |
| Delta vs pre-F-212 | +3 |
| Total qualifying findings (Critical + High) | 9 |
| Qualifying layers (≥1 qualifying finding) | 2 of 3 (Supabase Platform = 0) |
| `metadata.skip_image` | `False` (correct: dataset has Critical/High findings) |
| SC-212-3 PASS/FAIL | **FAIL** (5 ∉ [6,7,8]) |

## Per-layer breakdown

| Layer | Position | Components | Qualifying findings (mapped) | Allocated callouts | `layer_overflow` |
|---|---|---|---|---|---|
| Supabase Platform | 0 | 9 | 0 | 0 | `None` |
| Application Layer | 1 | 4 | 8 | 4 (capped at `_PER_LAYER_CEILING=4`) | `"+ 4 more in this layer"` |
| External / Untrusted | 2 | 9 | 1 | 1 | `None` |
| **Total** | | | **9** | **5** | |

### Per-layer floor rule check (FR-212-9)

- 2 qualifying layers ≤ `_TOTAL_CAP=8` → per-layer floor of 1 applies for each qualifying layer.
- Supabase Platform has 0 qualifying findings → not subject to floor; correctly receives 0 callouts.
- Application Layer + External / Untrusted both have ≥1 callout → floor satisfied.
- **No layer exceeds `_PER_LAYER_CEILING=4`** → ceiling satisfied.
- All structural invariants from FR-212-9 hold; the `[6,7,8]` aspirational range is unreachable mechanically given this dataset shape.

### Why 5 is the algorithmic maximum here

In `_allocate_callouts_per_layer`:

```
qualifying_per_layer = {Application Layer: 8, External / Untrusted: 1}  # zeros filtered
n_qualifying = 2
target_total = min(9, 8) = 8
per-layer floor allocation = {App: 1, External: 1}  -> current_total = 2
LRM remainder phase: slots_left = 6
  iter: External Layer cap = min(4, 1) = 1, already at 1 → skipped
        Application Layer cap = min(4, 8) = 4, fills to 4
  total now = 5; no more slots can be allocated (every layer at its cap)
  defensive break (line 985-992) terminates loop
final allocation = {Application Layer: 4, External / Untrusted: 1}  -> sum = 5
```

The system-wide cap is 8 but the per-layer ceiling of 4 combined with only 2 qualifying layers (8 + 1 findings) produces a ceiling of `4 + 1 = 5`. **No bug in the implementation** — the dataset is contractually constrained by FR-212-9.

## Contract conflict

- **FR-212-8** (functional requirement): "MUST return 6–8 callouts ..."
- **FR-212-9** per-layer ceiling: "Per-layer ceiling: 4 callouts maximum per layer."
- **SC-212-3** (success criterion): "Count of callouts ... for the 9-qualifying-finding reference dataset is 6, 7, or 8."

These are jointly satisfiable only when `qualifying_layer_count >= ceil(6 / 4) = 2` AND when at least two layers each have `>= 2` qualifying findings (reaching `2 + 4 = 6`). On this dataset, 8 of 9 qualifying findings are in Application Layer; External Layer has only 1; Supabase Platform has 0. With the structural ceiling, 5 is the maximum.

## Resolution paths (recommended for Triad triage; do NOT modify code in this task per scope)

1. **Relax `_PER_LAYER_CEILING`** to 5 or 6 for this layer-count regime — would yield 6 callouts here. Spec FR-212-9 hard-codes 4 — would require a spec amendment.
2. **Relax SC-212-3 lower bound** to acknowledge dataset-shape variance — e.g. "callout count ≥ floor(min(8, total_qualifying))" or "≥ ceil(qualifying_layers + min(qualifying_findings - qualifying_layers, ...))". This documents that on a degenerate distribution the ceiling rule binds.
3. **Curate the reference dataset** to include findings in Supabase Platform (3+ findings would yield 4 + 2 + 1 = 7 callouts).
4. **Reinterpret SC-212-3**: read the spec language "system-wide" to mean "system-wide ranking pre-ceiling-trim, with overflow surfaced via `layer_overflow`". The pre-ceiling system-wide top-8 would yield 8 callouts. Under this reading, SC-212-3 measures system-wide selection, and the per-layer ceiling enforces visual density within the rendered image (overflow shown via the `+ N more` annotation, which already works — Application Layer's `"+ 4 more"` is correctly emitted).

Reading 4 is the most consistent with the spec's narrative intent (FR-212-9 overflow annotation explicitly handles "more findings than slots" → suggests slot-count is a render-density concern, not the SC-212-3 anchor). However, the spec is unambiguous in requiring `len(callouts) ∈ [6,7,8]` literally, so this is a spec/code reconciliation matter for PM + Architect.

## Full payload JSON

```json
{
  "callouts": [
    {
      "affected_component": "MCP Server (HTTP)",
      "composite_score": 7.8,
      "finding_id": "D-1",
      "layer_name": "Application Layer",
      "raw_description": "Attacker floods HTTP MCP endpoint exhausting Deno edge function capacity",
      "severity": "High"
    },
    {
      "affected_component": "MCP Tool Surface",
      "composite_score": 7.7,
      "finding_id": "D-9",
      "layer_name": "Application Layer",
      "raw_description": "Autonomous agent chains browse_thoughts + bulk_delete causing catastrophic data destruction",
      "severity": "High"
    },
    {
      "affected_component": "MCP Server (stdio)",
      "composite_score": 7.5,
      "finding_id": "AG-1",
      "layer_name": "Application Layer",
      "raw_description": "All 10 tools exposed to local agents without human-in-the-loop approval gates",
      "severity": "High"
    },
    {
      "affected_component": "MCP Server (stdio)",
      "composite_score": 7.5,
      "finding_id": "AGP-01",
      "layer_name": "Application Layer",
      "raw_description": "Two or more agentic components coordinate over inter-agent data flow",
      "severity": "High"
    },
    {
      "affected_component": "brain CLI",
      "composite_score": 8.4,
      "finding_id": "S-9",
      "layer_name": "External / Untrusted",
      "raw_description": "The brain CLI connects directly to PostgREST via HTTPS, bypassing both MCP servers, with no documented API key",
      "severity": "High"
    }
  ],
  "layers": [
    {
      "component_count": 9,
      "components": [
        "Dead-Letter Queue",
        "Embed Edge Function",
        "Hybrid Search RPC",
        "PostgREST API",
        "Supabase Vault",
        "developer_profile",
        "pg_cron Scheduler",
        "pgmq Queue",
        "thoughts"
      ],
      "layer_overflow": null,
      "name": "Supabase Platform",
      "position": 0,
      "source_kind": "trust_zone"
    },
    {
      "component_count": 4,
      "components": [
        "Ingest Edge Function",
        "MCP Server (HTTP)",
        "MCP Server (stdio)",
        "MCP Tool Surface"
      ],
      "layer_overflow": "+ 4 more in this layer",
      "name": "Application Layer",
      "position": 1,
      "source_kind": "trust_zone"
    },
    {
      "component_count": 9,
      "components": [
        "Browser Clients",
        "ChatGPT",
        "Claude Code",
        "Claude Desktop",
        "Cursor / Windsurf",
        "Gemini Client",
        "Slack Events API",
        "Slack Web API",
        "brain CLI"
      ],
      "layer_overflow": null,
      "name": "External / Untrusted",
      "position": 2,
      "source_kind": "trust_zone"
    }
  ],
  "metadata": {
    "fallback_used": false,
    "generation_timestamp": "2026-04-25T15:32:14Z",
    "qualifying_layer_count": 3,
    "skip_image": false,
    "source_file": "/Users/david/Projects/second-brain-mcp/docs/security/2026-04-23T23-02-25/threats.md",
    "template_name": "executive-architecture",
    "tier_source": "compensating-controls",
    "total_filtered_count": 9
  },
  "severity_distribution": {
    "critical_count": 0,
    "high_count": 9,
    "total_after_layer_dedup": 5,
    "total_qualifying": 9
  }
}
```

## Notes

- The new `layer_overflow` field (T017) is correctly populated on Application Layer (`"+ 4 more in this layer"`), correctly `None` on the other two.
- Determinism: the payload is byte-identical across two runs under `SOURCE_DATE_EPOCH=1700000000` (sample from `perf-mono-{0..4}.json` — content identical apart from `generation_timestamp` only when wall-clock differs; under the env override it does not).
- The Supabase Platform layer remains in `layers[]` with 9 components and 0 callouts despite no qualifying findings — correct per the spec; the rendering handles this via the "0 High/Critical findings in this layer" badge from FR-212-5.
- `metadata.qualifying_layer_count = 3` is a misnomer — it's actually `len(layers)` (structural layer count), not the count of layers with ≥1 qualifying finding (which would be 2). This is pre-existing behavior — not changed by F-212.
