# Cursor Adapter

This adapter packages tachi's 14 threat modeling agents as Cursor rule files (`.mdc`). Each agent becomes a rule with YAML frontmatter that Cursor's AI agent can discover and activate during conversation.

**Important behavioral difference from Claude Code**: Cursor uses **passive context injection**, not active agent dispatch. There is no Agent tool that programmatically invokes sub-agents. Instead, the orchestrator rule is always loaded into context (`alwaysApply: true`), and threat agent rules are loaded on-demand by Cursor's agent based on their `description` fields matching the conversation context. This means Cursor decides which rules to activate rather than the orchestrator explicitly dispatching them.

---

## Prerequisites

- [Cursor](https://cursor.sh/) IDE installed
- Cursor rules feature enabled (Settings > Features > Rules)
- A project directory where you want to run threat analysis

---

## Installation

From your project root, copy the rule files into your Cursor rules directory:

```bash
cp -r adapters/cursor/rules/ .cursor/rules/tachi/
```

This creates `.cursor/rules/tachi/` containing all 14 threat modeling rule files.

---

## What's Included

### Orchestrator

| File | Mode | Description |
|------|------|-------------|
| `orchestrator.mdc` | `alwaysApply: true` | Central coordinator for OWASP four-step threat modeling. Parses architecture input, coordinates STRIDE and AI threat analysis, produces threats.md, SARIF output, narrative report, and visual infographic specification. |

### STRIDE Agents (6)

| File | Mode | Threat Category |
|------|------|----------------|
| `spoofing.mdc` | Agent Requested | Identity impersonation -- authentication bypass, credential theft, session hijacking |
| `tampering.mdc` | Agent Requested | Unauthorized data modification -- input injection, data flow manipulation, supply chain attacks |
| `repudiation.mdc` | Agent Requested | Accountability failures -- missing audit trails, log tampering, timestamp manipulation |
| `info-disclosure.mdc` | Agent Requested | Confidentiality violations -- error message exposure, data at rest/in transit leakage |
| `denial-of-service.mdc` | Agent Requested | Availability degradation -- resource exhaustion, algorithmic complexity, cascading failures |
| `privilege-escalation.mdc` | Agent Requested | Unauthorized privilege gain -- broken access control, role escalation, multi-tenancy violations |

### AI/LLM Agents (5)

| File | Mode | Threat Category |
|------|------|----------------|
| `prompt-injection.mdc` | Agent Requested | Direct and indirect prompt injection, jailbreaking, system prompt extraction |
| `data-poisoning.mdc` | Agent Requested | Training data manipulation, RAG index corruption, knowledge base poisoning |
| `model-theft.mdc` | Agent Requested | Model weight exfiltration, API-based extraction, artifact exposure |
| `agent-autonomy.mdc` | Agent Requested | Excessive agent autonomy, goal misalignment, cascading multi-agent failures |
| `tool-abuse.mdc` | Agent Requested | Unauthorized tool invocation, capability escalation, parameter injection, tool poisoning |

### Report Agents (2)

| File | Mode | Description |
|------|------|-------------|
| `threat-report.mdc` | Agent Requested | Generates narrative threat report with executive summary, Mermaid attack trees, and prioritized remediation roadmap |
| `threat-infographic.mdc` | Agent Requested | Generates visual risk specification with six sections and optional presentation-ready infographic image via Gemini API |

---

## How It Works

Cursor rules use a passive context injection model that differs from Claude Code's active agent dispatch:

- **Orchestrator** (`orchestrator.mdc`) is set to `alwaysApply: true`, so it is always loaded into the AI agent's context. It provides the threat modeling methodology, output format, and coordination instructions.

- **Threat agent rules** (STRIDE, AI, and report agents) are all set to `alwaysApply: false` (Agent Requested mode). Cursor's AI agent activates them based on their `description` field matching the current conversation context.

- **Context-driven activation**: When you describe a system architecture or ask about specific threat categories, Cursor reads the `description` frontmatter of each rule and loads the relevant threat agents into context automatically.

- **Explicit activation**: For a complete threat model covering all 11 threat categories, explicitly reference all tachi threat agents in your prompt so Cursor loads every rule. Without explicit reference, Cursor may only activate a subset based on what it determines is relevant.

---

## Invocation Workflow

### Quick Start -- Full Threat Model

1. Open your project in Cursor with the rules installed.

2. Start a new Composer session (or chat) and provide your architecture description:
   ```
   Run a complete tachi threat model on this system:

   [Paste your architecture description, DFD, or system overview here]

   Analyze using all tachi threat agents: spoofing, tampering, repudiation,
   info-disclosure, denial-of-service, privilege-escalation, prompt-injection,
   data-poisoning, model-theft, agent-autonomy, and tool-abuse.
   ```

3. The orchestrator rule (always in context) guides the analysis structure. Cursor activates the referenced threat agent rules and applies each agent's methodology against your architecture.

4. After analysis, request the report and infographic:
   ```
   Generate the tachi threat report and threat infographic from the findings.
   ```

### Targeted Analysis

For focused analysis on specific threat categories, reference only the agents you need:

```
Analyze this API gateway for spoofing and privilege-escalation threats
using tachi threat agents.

[Architecture description]
```

Cursor will load the orchestrator (always active) plus the spoofing and privilege-escalation rules based on your explicit reference and their description match.

---

## Verification

1. Confirm the files are installed:

```bash
ls .cursor/rules/tachi/
```

You should see 14 `.mdc` files (plus `.gitkeep`).

2. Verify rule loading. Open Cursor settings and navigate to the Rules section. The tachi rules should appear in the list with their descriptions visible.

3. Test activation. Start a new chat and ask:
   ```
   What tachi threat modeling rules are available?
   ```
   The orchestrator context should be present (always applied), and Cursor should be able to describe the available threat agents from their rule descriptions.

---

## Uninstallation

Remove the installed rules:

```bash
rm -rf .cursor/rules/tachi/
```

---

## VERSION File

The `VERSION` file in this adapter directory contains the source commit SHA and per-agent SHA-256 checksums. Use it to verify which version of the agents you have installed and to confirm file integrity after copying. If the source version does not match your tachi checkout, regenerate the adapter with `scripts/generate-adapter-version.sh`.
