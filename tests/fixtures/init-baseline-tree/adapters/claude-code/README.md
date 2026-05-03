# Claude Code Adapter

This adapter maps tachi's 14 threat modeling agents into Claude Code's native `.claude/agents/` format. Each agent is a standalone markdown file with YAML frontmatter that Claude Code recognizes and can dispatch via the Agent tool.

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed and functional
- A project with `.claude/` directory initialized (`claude init`)

## Installation

From your project root, copy the agent files into your Claude Code agents directory:

```bash
cp -r adapters/claude-code/agents/ .claude/agents/tachi/
```

This creates `.claude/agents/tachi/` containing all 14 threat modeling agents.

## What's Included

### Orchestrator

| File | Description |
|------|-------------|
| `orchestrator.md` | Central coordinator for OWASP four-step threat modeling. Parses architecture input, dispatches threat agents, detects cross-agent correlations, and produces the coverage matrix, risk summary, SARIF output, narrative report, and visual infographic spec. |

### STRIDE Agents (6)

| File | Threat Category |
|------|----------------|
| `spoofing.md` | Identity impersonation -- authentication bypass, credential theft, session hijacking |
| `tampering.md` | Unauthorized data modification -- input injection, data flow manipulation, supply chain attacks |
| `repudiation.md` | Accountability failures -- missing audit trails, log tampering, timestamp manipulation |
| `info-disclosure.md` | Confidentiality violations -- error message exposure, data at rest/in transit leakage |
| `denial-of-service.md` | Availability degradation -- resource exhaustion, algorithmic complexity, cascading failures |
| `privilege-escalation.md` | Unauthorized privilege gain -- broken access control, role escalation, multi-tenancy violations |

### AI/LLM Agents (5)

| File | Threat Category |
|------|----------------|
| `prompt-injection.md` | Direct and indirect prompt injection, jailbreaking, system prompt extraction |
| `data-poisoning.md` | Training data manipulation, RAG index corruption, knowledge base poisoning |
| `model-theft.md` | Model weight exfiltration, API-based extraction, artifact exposure |
| `agent-autonomy.md` | Excessive agent autonomy, goal misalignment, cascading multi-agent failures |
| `tool-abuse.md` | Unauthorized tool invocation, capability escalation, parameter injection, tool poisoning |

### Report Agents (2)

| File | Description |
|------|-------------|
| `threat-report.md` | Generates narrative threat report with executive summary, Mermaid attack trees, and prioritized remediation roadmap |
| `threat-infographic.md` | Generates visual risk specification with six sections and optional presentation-ready infographic image via Gemini API |

## Verification

1. Confirm the files are installed:

```bash
ls .claude/agents/tachi/
```

You should see 14 `.md` files (plus `.gitkeep`).

2. Invoke the orchestrator. Claude Code's Agent tool can dispatch `tachi-orchestrator`, which coordinates the full threat modeling workflow. Start a Claude Code session and reference the orchestrator agent to begin analysis.

3. Check the agent list. All 14 agents should be visible to Claude Code when it scans `.claude/agents/tachi/`.

## How It Works

The adapter provides a self-contained threat modeling team that operates through Claude Code's Agent tool:

- **Orchestrator** (`orchestrator.md`) coordinates the entire threat modeling process. It receives architecture input (DFD, system description), dispatches the appropriate threat agents, correlates findings across agents, and produces consolidated output.

- **STRIDE agents** (spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation) each analyze one traditional threat category from the STRIDE framework. They operate against data flow diagram elements and produce structured findings.

- **AI agents** (prompt-injection, data-poisoning, model-theft, agent-autonomy, tool-abuse) analyze threats specific to AI/LLM-integrated systems. They cover the OWASP LLM Top 10 and agentic threat patterns.

- **Report agents** (threat-report, threat-infographic) transform structured threat model output into human-readable deliverables -- a narrative report with attack trees and a visual risk infographic specification.

Claude Code dispatches agents in parallel via the Agent tool, allowing multiple STRIDE and AI agents to analyze the target system concurrently before the orchestrator merges and deduplicates their findings.

## Uninstallation

Remove the installed agents:

```bash
rm -rf .claude/agents/tachi/
```

## VERSION File

The `VERSION` file in this adapter directory contains the source commit SHA and per-agent SHA-256 checksums. Use it to verify which version of the agents you have installed and to confirm file integrity after copying.
