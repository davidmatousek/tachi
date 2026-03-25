# tachi

**Automated threat modeling sidecar for your projects.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](CHANGELOG.md)
[![Built with AOD Kit](https://img.shields.io/badge/built%20with-AOD%20Kit-blueviolet.svg)](https://github.com/davidmatousek/agentic-oriented-development-kit)

---

## What is tachi?

tachi is a threat modeling sidecar that you add to any project. It dispatches 14 specialized AI agents against your architecture description and produces a complete threat model in one command.

- **11 threat categories**: 6 STRIDE + 3 LLM-specific + 2 Agentic
- **5 input formats**: Mermaid, free-text, ASCII, PlantUML, C4
- **8 output artifacts**: structured findings, SARIF, narrative report, attack trees, infographics
- **Works with any stack**: tachi analyzes architecture, not code

tachi is built with the [Agentic Oriented Development Kit (AOD Kit)](https://github.com/davidmatousek/agentic-oriented-development-kit), a governance framework for AI agent-assisted development.

---

## Quick Start

### 1. Clone tachi (one-time)

```bash
git clone https://github.com/davidmatousek/tachi.git ~/Projects/tachi
```

### 2. Add tachi to your project

From your project root:

```bash
# Copy agents + infographic templates
cp -r ~/Projects/tachi/adapters/claude-code/agents/ .claude/agents/tachi/

# Copy the /threat-model command
mkdir -p .claude/commands
cp ~/Projects/tachi/adapters/claude-code/commands/threat-model.md .claude/commands/
```

### 3. Create your architecture file

Create `docs/security/architecture.md` describing your system. You can write it yourself or ask Claude Code:

```
Investigate this repository's architecture -- source code, config files, infrastructure
definitions, READMEs -- and create docs/security/architecture.md as a Mermaid flowchart
with all major components, data flows, protocols, and trust boundaries.
```

tachi auto-detects the format. Mermaid, free-text, ASCII, PlantUML, and C4 are all supported.

### 4. Run your first threat model

```
/threat-model
```

That's it. One command. tachi validates the setup, reads your architecture, dispatches 14 threat agents, and writes everything to a timestamped folder under `docs/security/`.

### 5. Review your results

| File | What It Contains |
|------|-----------------|
| `threats.md` | Primary threat model -- findings, coverage matrix, risk summary, mitigations |
| `threats.sarif` | SARIF 2.1.0 for GitHub Code Scanning and CI/CD integration |
| `threat-report.md` | Narrative report with executive summary and remediation roadmap |
| `attack-trees/` | One Mermaid attack tree per Critical/High finding |
| `threat-baseball-card-spec.md` | Baseball Card risk dashboard specification |
| `threat-baseball-card.jpg` | Baseball Card infographic (requires `GEMINI_API_KEY`) |
| `threat-system-architecture-spec.md` | Annotated architecture diagram specification |
| `threat-system-architecture.jpg` | Architecture infographic with finding legend (requires `GEMINI_API_KEY`) |

Start with `threats.md` Section 7 -- Recommended Actions. Work through Critical findings first, then High.

---

## Command Options

```bash
# Default -- uses docs/security/architecture.md
/threat-model

# Specify architecture file
/threat-model path/to/my-architecture.md

# Custom output directory
/threat-model docs/security/architecture.md --output-dir reports/security/

# Version-tagged output for a release
/threat-model docs/security/architecture.md --version v1.0.0

# Only generate one infographic template
/threat-model docs/security/architecture.md --infographic-template baseball-card
```

---

## How It Works

tachi uses a multi-agent orchestration pattern. The orchestrator parses your architecture, identifies components and data flows, then dispatches the right combination of threat agents per component:

| Component Type | STRIDE Agents | AI Agents |
|---------------|---------------|-----------|
| External Entity (users, APIs) | S, R | -- |
| Process (servers, agents) | S, T, R, I, D, E | LLM + AG if AI keywords detected |
| Data Store (databases, caches) | T, I, D | -- |
| Data Flow (API calls, messages) | T, I, D | -- |

AI agents activate when component names or descriptions contain keywords like "LLM", "agent", "orchestrator", "MCP", "tool server", "embedding", "RAG", etc.

After all agents report, the orchestrator deduplicates findings, runs cross-agent correlation, computes risk ratings, and generates the output suite.

---

## Threat Categories

### STRIDE (6 categories)

| Category | Threat | Example |
|----------|--------|---------|
| **S**poofing | Identity impersonation | Stolen API key used to make authenticated requests |
| **T**ampering | Unauthorized data modification | SQL injection modifying database records |
| **R**epudiation | Missing accountability | User denies triggering an expensive operation, no logs exist |
| **I**nformation Disclosure | Data exposure | Error messages leaking internal architecture details |
| **D**enial of Service | Availability attacks | Request flooding exhausting connection pools |
| **E**levation of Privilege | Unauthorized access | Regular user accessing admin endpoints |

### AI-Specific (5 categories)

| Category | Threat | Example |
|----------|--------|---------|
| **Prompt Injection** (LLM) | Adversarial inputs hijacking LLM behavior | Hidden instructions in a document causing the LLM to leak its system prompt |
| **Data Poisoning** (LLM) | Corrupted training/RAG data | Attacker modifying knowledge base documents to spread misinformation |
| **Model Theft** (LLM) | Model extraction | Competitor reverse-engineering your fine-tuned model via API queries |
| **Agent Autonomy** (AG) | Insufficient oversight | AI agent sending 500 emails without human approval |
| **Tool Abuse** (AG) | Tool misuse or manipulation | Malicious plugin exfiltrating source code when invoked |

---

## Examples

The [`examples/`](examples/) directory contains complete threat models you can reference:

| Example | Architecture | Threat Categories |
|---------|-------------|-------------------|
| [Web App](examples/web-app/) | Traditional web application | STRIDE |
| [Agentic App](examples/agentic-app/) | LLM orchestrator + MCP tools | STRIDE + AI |
| [Microservices](examples/microservices/) | Cross-service architecture | STRIDE |

---

## Integration Reference

| Resource | Location | Purpose |
|----------|----------|---------|
| Interface Contract | [`docs/INTERFACE-CONTRACT.md`](docs/INTERFACE-CONTRACT.md) | Input formats, invocation protocol, output structure |
| Output Template | [`templates/threats.md`](templates/threats.md) | Canonical output structure with all 7 sections |
| Schemas | [`schemas/`](schemas/) | Machine-readable contracts ([finding.yaml](schemas/finding.yaml), [input.yaml](schemas/input.yaml), [output.yaml](schemas/output.yaml)) |
| Threat Agents | [`agents/stride/`](agents/stride/) + [`agents/ai/`](agents/ai/) | Agent prompt definitions |
| Developer Guide | [`docs/guides/DEVELOPER_GUIDE_TACHI.md`](docs/guides/DEVELOPER_GUIDE_TACHI.md) | Full walkthrough with worked examples |

---

## Known Issues

### Finding count variance between runs

Successive threat model runs on the same architecture may produce slightly different finding counts (typically +/- 10%). This is expected behavior with LLM-based analysis.

**What's consistent**: Core findings across all STRIDE and AI categories. The same high-severity threats will appear in every run.

**What varies**: Borderline findings in the long tail -- a Medium-severity finding like "missing correlation ID on external API calls" may appear in one run but not the next, depending on how the agent reasons through the architecture.

**Why this happens**: Each of the 14 threat agents makes independent LLM calls. LLM output is non-deterministic by nature, so agents may surface slightly different findings on each invocation.

**If you need higher consistency**:
- Run twice and diff the results to catch edge cases
- Use a previous run's `threats.md` as a baseline for comparison
- Treat the threat model as a living document that improves with each run

---

## Built with AOD Kit

tachi is built with the [Agentic Oriented Development Kit (AOD Kit)](https://github.com/davidmatousek/agentic-oriented-development-kit), a governance framework for AI agent-assisted development. AOD Kit provides the SDLC Triad methodology (PM + Architect + Team Lead sign-offs), quality gates, and structured workflows that govern how tachi itself is developed and maintained.

---

## Contributing

We welcome contributions. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT License. See [LICENSE](LICENSE) for details.
