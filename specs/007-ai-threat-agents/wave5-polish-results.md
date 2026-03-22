# Wave 5: Polish & Cross-Cutting Results

**Date**: 2026-03-22
**Tasks**: T046-T048

## T046: MITRE ATLAS Cross-References — PASS (already present)

All 5 agents already have MITRE ATLAS references:

| Agent | MITRE ATLAS Reference | Specific Technique ID |
|---|---|---|
| prompt-injection | LLM Prompt Injection | Tactic TA0043, Technique AML.T0051 |
| data-poisoning | Poisoning AI Training Data | Tactic TA0040, Technique AML.T0020 |
| model-theft | ML Model Access | Tactic TA0044, Technique AML.T0044 |
| agent-autonomy | Abuse of AI Agent Capabilities | Descriptive (no ATLAS ID yet) |
| tool-abuse | Abuse of AI Capabilities | Descriptive (no ATLAS ID yet) |

**Note**: Agent-autonomy and tool-abuse use descriptive ATLAS references because MITRE ATLAS does not yet have specific technique IDs for agentic threat categories. This is expected and acceptable.

## T047: CWE Identifiers — PASS (2 additions)

### Already Present
- prompt-injection: CWE-77 (Improper Neutralization of Special Elements) ✓
- data-poisoning: CWE-1395 (Dependency on Vulnerable Third-Party Component) ✓
- model-theft: CWE-209 (Error Message Containing Sensitive Information), CWE-522 (Insufficiently Protected Credentials) ✓
- tool-abuse: CWE-89 in example finding (SQL Injection via parameter injection) ✓

### Added
- **model-theft**: Added CWE-200 (Exposure of Sensitive Information to an Unauthorized Actor) — parent category covering model weight exfiltration, API-based extraction, and metadata leakage
- **data-poisoning**: Added CWE-345 (Insufficient Verification of Data Authenticity) — directly maps to training data manipulation and RAG index poisoning

### Task Spec Deviation
- Task specified CWE-1321 (Prototype Pollution) for data-poisoning. CWE-1321 is a JavaScript-specific vulnerability (prototype pollution) and does not apply to ML data poisoning attacks. Substituted CWE-345 (Insufficient Verification of Data Authenticity) which directly maps to the agent's detection patterns (training data manipulation, RAG index poisoning, knowledge base corruption).

## T048: README Accuracy — PASS

`agents/ai/README.md` accurately documents:
- **AG table**: agent-autonomy.md + tool-abuse.md → Agentic Threats
- **LLM table**: prompt-injection.md + data-poisoning.md + model-theft.md → LLM Threats
- **Reference Standards**: OWASP Agentic Top 10 2026 (draft), MCP Top 10 v0.1 Beta, OWASP LLM Top 10 v2025
- **Rationale**: 5 agents for detection precision, 2 tables for reporting clarity
- **Workflow**: Correctly describes orchestrator collection and grouping

## Summary

| Task | Status | Action |
|---|---|---|
| T046 | PASS | All 5 agents have MITRE ATLAS references (verified, no changes needed) |
| T047 | PASS | Added CWE-200 to model-theft, CWE-345 to data-poisoning |
| T048 | PASS | README 5-agent-to-2-table mapping verified accurate |

**Wave 5 Result: 3/3 PASS — Polish complete**
