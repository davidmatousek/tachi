# Copilot Adapter

This adapter maps tachi's 14 threat modeling agents into GitHub Copilot's custom agents format. Each agent is a `.agent.md` file with YAML frontmatter that Copilot recognizes and can dispatch. Two agents that exceed Copilot's 30K character limit are split into compact agent files paired with `.instructions.md` context files.

## Prerequisites

- GitHub Copilot with custom agents support enabled
- VS Code or compatible IDE with Copilot extension
- A project repository with `.github/` directory

## Installation

From your project root, copy the agent and instructions files into your Copilot directories:

```bash
# Copy agent files
mkdir -p .github/agents/tachi
cp adapters/copilot/agents/*.agent.md .github/agents/tachi/

# Copy instructions files (supplementary context for oversized agents)
mkdir -p .github/instructions
cp adapters/copilot/instructions/*.instructions.md .github/instructions/
```

This creates `.github/agents/tachi/` containing 14 threat modeling agents and `.github/instructions/` containing 2 supplementary context files.

## What's Included

### Agent Files (14)

#### Orchestrator

| File | Description |
|------|-------------|
| `orchestrator.agent.md` | Central coordinator for OWASP four-step threat modeling. Parses architecture input, dispatches threat agents, detects cross-agent correlations, and produces the coverage matrix, risk summary, SARIF output, narrative report, and visual infographic spec. |

#### STRIDE Agents (6)

| File | Threat Category |
|------|----------------|
| `spoofing.agent.md` | Identity impersonation -- authentication bypass, credential theft, session hijacking |
| `tampering.agent.md` | Unauthorized data modification -- input injection, data flow manipulation, supply chain attacks |
| `repudiation.agent.md` | Accountability failures -- missing audit trails, log tampering, timestamp manipulation |
| `info-disclosure.agent.md` | Confidentiality violations -- error message exposure, data at rest/in transit leakage |
| `denial-of-service.agent.md` | Availability degradation -- resource exhaustion, algorithmic complexity, cascading failures |
| `privilege-escalation.agent.md` | Unauthorized privilege gain -- broken access control, role escalation, multi-tenancy violations |

#### AI/LLM Agents (5)

| File | Threat Category |
|------|----------------|
| `prompt-injection.agent.md` | Direct and indirect prompt injection, jailbreaking, system prompt extraction |
| `data-poisoning.agent.md` | Training data manipulation, RAG index corruption, knowledge base poisoning |
| `model-theft.agent.md` | Model weight exfiltration, API-based extraction, artifact exposure |
| `agent-autonomy.agent.md` | Excessive agent autonomy, goal misalignment, cascading multi-agent failures |
| `tool-abuse.agent.md` | Unauthorized tool invocation, capability escalation, parameter injection, tool poisoning |

#### Report Agents (2)

| File | Description |
|------|-------------|
| `threat-report.agent.md` | Generates narrative threat report with executive summary, Mermaid attack trees, and prioritized remediation roadmap |
| `threat-infographic.agent.md` | Generates visual risk specification with six sections and optional presentation-ready infographic image via Gemini API |

### Instructions Files (2)

| File | Paired Agent | Purpose |
|------|-------------|---------|
| `tachi-orchestrator-context.instructions.md` | `orchestrator.agent.md` | Full orchestration logic, dispatch rules, output assembly, and cross-correlation analysis (~115K chars from source) |
| `tachi-threat-report-context.instructions.md` | `threat-report.agent.md` | Report generation templates, attack tree construction, and remediation roadmap formatting (~24K chars from source) |

## Size Constraint Handling

Copilot custom agents have a 30,000 character limit per `.agent.md` file. Two source agents exceed this limit:

- **orchestrator** (~120K source) -- Split into a compact `orchestrator.agent.md` (15,570 chars) containing metadata, dispatch configuration, and summary instructions, paired with `tachi-orchestrator-context.instructions.md` (115,490 chars) containing the full orchestration logic.
- **threat-report** (~43K source) -- Split into a compact `threat-report.agent.md` (20,231 chars) containing metadata, schema references, and core instructions, paired with `tachi-threat-report-context.instructions.md` (23,833 chars) containing detailed report generation context.

All other agents are under 30K characters in their entirety (range: 5,596 -- 26,488 chars).

## How It Works

The adapter provides a self-contained threat modeling team that operates through Copilot's custom agent system:

- **Orchestrator** (`orchestrator.agent.md`) is the only `user-invocable: true` agent. It coordinates the entire threat modeling process: receives architecture input (DFD, system description), dispatches the appropriate threat agents via its `agents` field, correlates findings across agents, and produces consolidated output.

- **STRIDE agents** (spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation) each analyze one traditional threat category from the STRIDE framework. They operate against data flow diagram elements and produce structured findings.

- **AI agents** (prompt-injection, data-poisoning, model-theft, agent-autonomy, tool-abuse) analyze threats specific to AI/LLM-integrated systems. They cover the OWASP LLM Top 10 and agentic threat patterns.

- **Report agents** (threat-report, threat-infographic) transform structured threat model output into human-readable deliverables -- a narrative report with attack trees and a visual risk infographic specification.

The orchestrator dispatches agents via its `agents` frontmatter field, allowing Copilot to coordinate multiple STRIDE and AI agents analyzing the target system before merging and deduplicating their findings.

## Invocation

In your IDE with Copilot enabled, invoke the tachi orchestrator by referencing the agent:

```
@tachi-orchestrator Analyze the threat model for this application
```

The orchestrator will parse your architecture input and coordinate the full STRIDE + AI threat analysis workflow, dispatching sub-agents as needed.

## Verification

1. Confirm the files are installed:

```bash
ls .github/agents/tachi/
ls .github/instructions/
```

You should see 14 `.agent.md` files in the agents directory and 2 `.instructions.md` files in the instructions directory.

2. Verify agent recognition. Open your IDE with Copilot and check that `tachi-orchestrator` appears as an available agent when using the `@` mention syntax.

3. Test invocation. Reference `@tachi-orchestrator` in a Copilot chat to confirm it responds with the threat modeling workflow.

## Uninstallation

Remove the installed agents and instructions:

```bash
rm -rf .github/agents/tachi/
rm .github/instructions/tachi-orchestrator-context.instructions.md
rm .github/instructions/tachi-threat-report-context.instructions.md
```

## VERSION File

The `VERSION` file in this adapter directory contains the source commit SHA and per-agent SHA-256 checksums computed from the source agent files. Use it to verify which version of the agents you have installed and to confirm file integrity after copying.
