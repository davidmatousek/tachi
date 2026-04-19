# Mermaid-Agentic-App Baseline Pre-Check — T012 Output

**Task reference**: T012 (Wave 1.1 static DFD inspection — architect M2 absorption)
**Target file**: `examples/mermaid-agentic-app/input.md` (note: this example uses `input.md` rather than `architecture.md` — naming-convention artifact only)
**Run date**: 2026-04-18

## Search

Grep for the 10 canonical output-integrity trigger keywords from
`detection-patterns.md` (authored in T013) against
`examples/mermaid-agentic-app/input.md`:

- `LLM output`
- `rendered HTML`
- `model output to browser`
- `model output to SQL`
- `LLM-generated query`
- `template engine`
- `outbound HTTP from agent`
- `LLM-synthesized URL`
- `command construction`
- `file path from model`

## Result

**ZERO MATCHES** across all 10 trigger keywords.

## Interpretation

The `mermaid-agentic-app` example describes a multi-agent orchestration
topology (per Feature 091 MAESTRO infographic test baseline) but does NOT
contain a component-level description of an LLM-output-to-downstream-sink
flow that would trigger the `output-integrity` agent under the FR-011
both-keyword-AND-sink-indicator rule. The example remains within the
5-baseline backward-compatibility set (`web-app`, `microservices`,
`ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) tested
under `SOURCE_DATE_EPOCH=1700000000` per ADR-021.

**Byte-identity preserved — no baseline break expected.** Wave 4
regeneration of `examples/agentic-app/` is the only expected baseline-
differentiating regen. TL-H1 re-baseline escalation is NOT required.

## Escalation Decision

**No escalation required**. Wave 4 T031 decision-gate review will confirm
this pre-check result still holds post-orchestrator-registration.
