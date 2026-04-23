---
name: tachi-misinformation
description: "Companion skill for the misinformation threat agent. Provides the LLM09:2025 pattern catalog consumed by agents/tachi/misinformation.md."
---

# tachi-misinformation

Companion skill for the `misinformation` threat agent (agents/tachi/misinformation.md).

## Purpose

Hosts the misinformation pattern catalog (references/detection-patterns.md) that the agent loads on dispatch. Detection focuses on OWASP LLM09:2025 Misinformation — the factual-integrity signal class covering:
- Ungrounded factual emission
- Citation fabrication
- Overreliance / missing HITL on decision-critical output
- Retrieval-grounding gaps
- Confidence-calibration absence

Per ADR-031 (Heuristic A three-way split): distinct from `prompt-injection` (input-side) and `output-integrity` (execution-sink sanitization per ADR-030 Decision 1).

## Consumers

- `agents/tachi/misinformation.md` — loads `references/detection-patterns.md` on dispatch via the single MANDATORY Read directive (ADR-023 lean-agent pattern).

## References

- `references/detection-patterns.md` — 5-category pattern catalog (Q1 PRD decision)

## Related ADRs

- ADR-023 — lean-agent pattern
- ADR-030 — F-1 precedent; Decision 1 scope bounds; Decision 8 regex-extension rule
- ADR-031 — THIS skill's decision record
