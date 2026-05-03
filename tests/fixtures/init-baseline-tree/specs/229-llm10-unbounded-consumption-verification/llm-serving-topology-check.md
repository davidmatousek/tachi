# T022 LLM-Serving Topology Dry-Run

**Feature**: 229 / F-5
**Date**: 2026-04-27
**Author**: architect (Wave 1.1 plan-day check)

## Purpose

Pre-Wave 2 dry-run grep on 7 example architectures to verify LLM-serving topology gate (FR-015) coverage assumptions before example regeneration. Aligns with plan.md System Design item 4 + tasks.md T022.

## Methodology

Grep each architecture file with specific LLM-serving topology indicators distinct from generic "model" / "agent" / "inference" terminology:

```
inference (endpoint|api|gateway)
per-tenant token
max-context-window
token-counting middleware
cost-attribution layer
/v1/(completions|chat|generate)
llm.api.gateway
per-tenant api key
context window
prompt token
```

## Results

| Baseline | Architecture file | Specific LLM-serving indicators | Expected per plan |
|---|---|---|---|
| `web-app` | `architecture.md` | 0 | 0 ✓ |
| `microservices` | `architecture.md` | 0 | 0 ✓ |
| `ascii-web-api` | `input.md` (no `architecture.md`) | (not checked — uses `input.md` format) | 0 expected |
| `mermaid-agentic-app` | `input.md` (no `architecture.md`) | (not checked — uses `input.md` format) | 0 expected |
| `free-text-microservice` | `input.md` (no `architecture.md`) | (not checked — uses `input.md` format) | 0 expected |
| `maestro-reference` | `architecture.md` | 4 (Model Inference API Gateway, language model inference endpoint, etc.) | 0 expected ⚠ FLAGGED |
| `agentic-app` | `architecture.md` | 0 | ≥1 expected ⚠ FLAGGED |

## Findings

### Finding 1 — `maestro-reference` exhibits LLM-serving terminology (FLAGGED for Wave 3 architect review)

`maestro-reference` architecture.md contains terms like "Model Inference API Gateway" (line 50), "language model inference endpoint" (line 155), and "API gateway container fronting the foundation-model and risk-model inference endpoints" (line 160). These match the LLM-serving indicators on a literal grep basis.

**However**, maestro-reference is an OWASP MAESTRO reference architecture for healthcare clinical-LLM scenarios — it depicts an LLM-serving topology BUT does NOT exhibit the multi-tenant denial-of-wallet / cost-amplification / per-tenant token-budget structural features that F-5 Cat 12/13 + Cat 10/11 detect. The architecture lacks declared per-tenant API keys, declared per-tenant token budgets, declared cost-attribution per-tenant, and declared multi-tenant freemium structure.

**Disposition**: The actual topology gate enforcement is via the agent's pattern matching logic on holistic architecture context, not a crude grep. The pipeline determinism check (T054 `pytest tests/scripts/test_backward_compatibility.py -v` on the 6 baselines under `SOURCE_DATE_EPOCH=1700000000`) is the authoritative test. If `maestro-reference` byte-identity breaks at T054, escalate per PRD R1 escalation path with architect + team-lead approval.

**Pre-emptive flag**: Wave 3 T054 architect-monitored. If byte-identity holds, the topology gate works as designed (the agent reads holistic context, not literal phrase matches). If byte-identity breaks, redirect Day 2 buffer capacity to indicator refinement on Cat 12/13 + Cat 10/11.

### Finding 2 — `agentic-app` does not exhibit specific LLM-serving topology indicators by literal grep (FLAGGED for Wave 2 confirmation)

`agentic-app` architecture.md does not contain literal phrases like "inference endpoint", "per-tenant token", "max-context-window", or "/v1/completions". The broader grep on LLM/agent/inference/model returns 16 matches (LLM-related terminology is present in agent descriptions), but the specific indicator phrases F-5 patterns target are not present.

**Disposition**: per Q5 RESOLVED at PRD time, `examples/agentic-app/` was confirmed as the multi-component LLM topology established by F-3 mutation. The actual emission test (Wave 2 T045 `/tachi.threat-model examples/agentic-app/`) is the authoritative test of LLM-serving topology gate trigger. If T045 reveals zero new D-{N} or LLM-{N} findings citing LLM10:2025, escalate per PRD R1 with architect re-evaluation of LLM-serving topology gate logic + potential architecture extension to add explicit indicator phrases.

**Pre-emptive flag**: Wave 2 T043 + T045 architect-monitored. If T045 emits ≥1 Cat 12/13 + ≥1 Cat 10/11 findings, the topology gate fires correctly via holistic agent context reading (not literal phrase matching). If T045 emits zero, redirect Day 2 buffer capacity to architecture extension on `agentic-app` adding explicit LLM-serving indicators.

## Verdict

Pre-flagged 2 concerns (maestro-reference + agentic-app); proceed with Wave 2 example regeneration. The actual topology gate enforcement is via agent pattern matching on holistic architecture context, NOT crude grep — the pipeline determinism + emission tests at T045 + T054 are the authoritative gates. Both flags are advisory, not BLOCKING for Wave 2 progression.

## Cross-References

- Plan System Design item 4 (LLM-serving topology dry-run)
- Tasks T022 (this dry-run); T043 (Q5 confirmation); T045 (Wave 2 example regen); T054 (Wave 3 6-baseline byte-identity)
- PRD R1 escalation path (regen friction absorption ≤8 hours)
