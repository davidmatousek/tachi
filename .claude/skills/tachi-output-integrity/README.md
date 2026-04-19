# tachi-output-integrity

Companion skill for the `tachi-output-integrity` threat agent. Externalizes the detection pattern catalog and severity-relevant references consumed at detection start.

**Consumers**:

- `tachi-output-integrity` — the AI-tier threat agent emitting `OI-{N}` findings

## Purpose

Holds the canonical detection vocabulary for OWASP LLM05:2025 Improper Output Handling threats. Keeping the pattern catalog in this companion skill (rather than inline in the agent file) lets `tachi-output-integrity.md` stay within the ADR-023 lean-agent 150-line soft target, and lets the pattern taxonomy evolve independently of the agent's orchestration workflow.

## Layout

- `references/detection-patterns.md` — frontmatter + `## Overview` + `## Detection Scope` (trigger keywords + applicable DFD element types) + `## Detection Patterns` (5 numbered categories covering Client-Side Execution Sinks, Server-Side Execution Sinks, SSRF, Template/Expression Injection, and Path Traversal). Each category carries indicators, a worked example, primary/related citations, and trigger keywords.

## Related

- Agent: `.claude/agents/tachi/output-integrity.md`
- ADR: `docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md`
- Schema: `schemas/finding.yaml` (v1.6 — `OI` prefix added to `id.pattern` regex alternation)
- F-A1 catalog (read-only source for `source_attribution`): `schemas/taxonomy/owasp.yaml` + `schemas/taxonomy/cwe.yaml`
- F-A2 contract (source attribution): `docs/architecture/02_ADRs/ADR-028-source-attribution-schema-extension.md`
