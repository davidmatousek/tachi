# Wave 1.1 — Multi-Agent Topology Dry-Run (T014)

**Feature**: 219 / F-3
**Date**: 2026-04-25
**Author**: Wave 1.1 pre-edit dry-run

## Purpose

Pre-Wave 3 grep on all 6 baseline architectures to verify the multi-agent / multi-MCP topology gate (FR-011) ensures byte-identity preservation on the 5 non-multi-agent baselines, and to confirm `agentic-app` exhibits the multi-agent topology required for Q3 PM default extension.

## Method

Grep each baseline's primary architecture file (`architecture.md` or `input.md`) for multi-agent / multi-MCP indicators:
- "Inter-agent Communication Channel" / "inter-agent" / "A2A" — multi-agent topology marker (Feature 142 component type)
- "MCP-to-MCP" / multi-hop MCP relay — multi-MCP topology marker

## Results

| Baseline | Architecture file | Inter-agent matches | Multi-MCP matches | Topology classification | Expected Cat-9/10 emission |
|----------|-------------------|---------------------|-------------------|-------------------------|----------------------------|
| `web-app` | architecture.md | 0 | 0 | Non-multi-agent (web app DFD) | ZERO |
| `microservices` | architecture.md | 0 | 0 | Non-multi-agent (microservices DFD) | ZERO |
| `ascii-web-api` | input.md | 0 | 0 | Non-multi-agent (single-API DFD) | ZERO |
| `mermaid-agentic-app` | input.md | 0 | 1 MCP Tool Server (single-MCP) | Stylistic-multi-agent (single-orchestrator + single-MCP) | ZERO |
| `free-text-microservice` | input.md | 0 | 0 | Non-multi-agent | ZERO |
| `agentic-app` | architecture.md | 4 (Inter-Agent Communication Channel) | 1 MCP Tool Server (single-MCP) | **Multi-agent topology established** (Feature 142) | **≥1 Cat-9 finding expected** (Cat-10 conditional on multi-MCP — single-MCP architecture; Cat-10 = ZERO) |

## Verdict

**GREEN — Q3 PM default confirmed**:

1. **5 non-multi-agent baselines verified zero-emission by topology gate** — `web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice` all lack the multi-agent/multi-MCP topology required by Categories 9-10. Topology gate (FR-011) guarantees zero new findings → SC-010 byte-identity preserved by construction.
2. **`agentic-app` exhibits multi-agent topology** — `Inter-Agent Communication Channel` Process component is registered (Feature 142 establishes this baseline post-merge); ≥1 Category-9 A2A finding expected on regen. **Single MCP Tool Server only** — Category-10 multi-hop MCP trust chain NOT present in current `agentic-app` baseline; Cat-10 = ZERO unless architect at T032 chooses to extend `agentic-app/architecture.md` with explicit multi-MCP relay (Agent → MCP-A → MCP-B).
3. **Q3 fallback decision deferred to T032** — if Wave 3 architect determines `agentic-app` needs explicit multi-MCP relay extension to surface Category-10 findings, options are: (a) add MCP relay to `agentic-app/architecture.md` as part of regeneration; (b) Q3 fallback to `maestro-reference` extension or new minimal multi-agent fixture (~0.5d Buffer Day 1 consumption).

## Risk surfaces

- **Cat-10 emission gap if `agentic-app` ships single-MCP only**: SC-009 + SC-011 require ≥1 new Category-9/10 `AG-{N}` finding. Cat-9 from inter-agent channel suffices to satisfy SC-009 (≥1 finding from Categories 9 OR 10). If architect wants both Cat-9 AND Cat-10 demonstrated, a multi-MCP relay extension to `agentic-app/architecture.md` is needed at T034. This is an architect plan-day refinement, not a blocker.
- **`mermaid-agentic-app` single-MCP byte-identity**: stylistic-agentic-multi-agent baseline must emit zero Cat-9 (no inter-agent channel) and zero Cat-10 (single-MCP). Topology gate enforces both. T040 Wave 3 backward-compat test verifies SC-010.

## Recommendation

Proceed to Wave 2 (Pattern Categories 9 + 10 authoring). T032 architect confirms regen target at Wave 3 — extend `agentic-app/architecture.md` with explicit multi-MCP relay if Cat-10 demonstration is desired, OR satisfy SC-009 via Cat-9 emission alone.
