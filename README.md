# tachi

**Rust-native threat modeling, AI security analysis, and release-audit harness
with native and fallback adapters.**

*AI-Reasoning Scanner - STRIDE + AI + MAESTRO + OWASP coverage.*

![tachi - Rust-native threat modeling, AI security analysis, and release-audit
harness with native and fallback adapters. AI-Reasoning Scanner (STRIDE + AI +
MAESTRO + OWASP) with five-framework coverage, a 3-step install, and a 5-step
security-report workflow.](brand/posters/2026-05-29-owasp-coverage-poster.jpg)

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![GitHub release](https://img.shields.io/github/v/release/pratik-saptarshi/tachi-rust)](https://github.com/pratik-saptarshi/tachi-rust/releases)
[![Built with AOD Kit](https://img.shields.io/badge/built%20with-AOD%20Kit-blueviolet.svg)](https://github.com/davidmatousek/agentic-oriented-development-kit)

**Get started**: [Core capabilities](#core-capabilities) |
[Platform compatibility](docs/platform-compatibility.md) |
[How an auditor uses tachi](#how-an-auditor-uses-tachi) |
[Use cases](#use-cases) | [Quick start](#quick-start) |
[Developer guide](docs/guides/DEVELOPER_GUIDE_TACHI.md)

---

## What tachi is

tachi is a Rust-native security analysis harness that helps teams inspect
architecture, threat models, AI agent behavior, and release-readiness evidence
from one workflow. The canonical threat logic lives in `agents/`; platform
adapters only repackage that same core contract for the target harness. It
produces human-readable reports and machine-readable artifacts such as SARIF,
attack trees, risk scores, and control coverage summaries.

The active repository is Rust/Tauri-native. The old Python/FastAPI surface is
retired; remaining Python references are archival or compatibility fixtures
only. **Archived legacy guidance** for the retired FastAPI pack is preserved in
historical docs for reference only and is not part of active setup flows.

Publication and release-readiness guidance lives in:

- [`docs/bill-of-materials.html.md`](docs/bill-of-materials.html.md) for the
  publishable surface inventory.
- [`docs/platform-compatibility.md`](docs/platform-compatibility.md) for the
  harness matrix, install surfaces, and fallback behavior.
- [`docs/publish-readiness-checklist.html.md`](docs/publish-readiness-checklist.html.md)
  for the pre-push security, privacy, docs, and CI gate.

## Compatibility at a Glance

| Support level | Harnesses | Install surface |
|---|---|---|
| Native adapter | Claude Code, Cursor, Copilot, GitHub Actions | Dedicated adapter pack or workflow file |
| Thin shim | Codex, OpenCode, Termux, Voltagent, Antigravity | `adapters/generic/prompts/` plus harness-specific launch docs |
| Generic fallback | Pi-style harnesses and unsupported clients | `adapters/generic/prompts/` |

See [`docs/platform-compatibility.md`](docs/platform-compatibility.md) for the
full matrix and setup recipes.

## Standalone MCP Server

Use `tachi-mcp` when you want the canonical command contract over stdio
instead of a harness-specific adapter.

Build and run it with:

```bash
cargo build -p tachi-mcp --features stdio
cargo run -p tachi-mcp --features stdio -- --stdio
```

The MCP transport keeps the same analysis command names and canonical artifact
paths:

| Tool | Canonical artifact |
|---|---|
| `tachi.coverage-audit` | `target/mcp/coverage-audit.txt` |
| `tachi.infographic-data` | `target/mcp/infographic-data.json` |
| `tachi.report-data` | `target/mcp/report-data.typ` |
| `tachi.risk-scores-sarif` | `target/mcp/risk-scores-sarif.sarif` |
| `tachi.threats-sarif` | `target/mcp/threats-sarif.sarif` |

Validate the transport and schema contract with:

```bash
cargo test -p tachi-mcp --test contract_snapshot --test schema_snapshot --test tools_registration --test session_policy --test stdio
```

---

## Core capabilities

| Capability | What it does | Why an auditor cares |
|---|---|---|
| Architecture discovery | `/tachi.architecture` turns source, config, infrastructure, and docs into a consistent architecture draft. | Establishes the audit boundary, data flow, trust boundaries, and scope assumptions. |
| Threat modeling | `/tachi.threat-model` analyzes Mermaid, prose, ASCII, PlantUML, or C4 input and emits structured findings. | Produces a repeatable threat register instead of ad hoc notes. |
| AI and agentic coverage | Models prompt injection, tool abuse, autonomy gaps, RAG risks, model theft, and related agent behaviors. | Extends review beyond standard web/API threat modeling. |
| Standards mapping | Findings map to OWASP, MITRE ATT&CK, ATLAS, NIST AI RMF, CWE, and MAESTRO where applicable. | Makes the evidence easier to present to security, compliance, and engineering. |
| Quantitative scoring | `/tachi.risk-score` adds severity, exploitability, reachability, owner, SLA, and review-date fields. | Helps prioritize remediation and verify the highest-risk items first. |
| Compensating-control analysis | `/tachi.compensating-controls` compares findings against existing controls in the codebase. | Distinguishes inherited design risk from already-mitigated risk. |
| SARIF output | `threats.sarif`, `risk-scores.sarif`, and `compensating-controls.sarif` are ready for code-scanning tools. | Lets auditors publish findings into the same pipeline used for code-security alerts. |
| Visual and PDF reporting | `/tachi.infographic` and `/tachi.security-report` create stakeholder-ready artifacts. | Turns technical output into evidence suitable for reviews, sign-off, and executive summaries. |
| Baseline tracking | Repeated runs compare current findings to a prior baseline. | Supports remediation verification and regression detection over time. |

## Why this repo exists

tachi complements SAST, SCA, and secrets scanning with architecture-aware
security analysis. It is useful when the risk is not a syntax bug, but a broken
flow, missing boundary, unsafe automation path, or incomplete control story.

This repository is built with the [Agentic Oriented Development Kit
(AOD Kit)](https://github.com/davidmatousek/agentic-oriented-development-kit),
which provides the governance and release discipline around the security
harness.

---

## How an auditor uses tachi

An auditor can use tachi as a repeatable evidence pipeline for application,
platform, or AI-agent security reviews.

1. Define the scope, target repository, and audit objective.
1. Generate or review the architecture with `/tachi.architecture` so the
   boundary, inputs, data stores, and external dependencies are explicit.
1. Run `/tachi.threat-model` to produce `threats.md`, SARIF, attack trees, and
   baseline deltas.
1. Run `/tachi.risk-score` to prioritize the findings with owners and SLAs.
1. Run `/tachi.compensating-controls` to separate existing mitigations from
   missing controls.
1. Export the results into `tachi.infographic` and `tachi.security-report` for
   stakeholder review.
1. Compare a later run against the baseline to verify remediation progress.

Good audit inputs are specific. Include authentication paths, authorization
boundaries, privileged workflows, queues, data stores, third-party APIs, model
providers, tool servers, agent permissions, logging, monitoring, and deployment
controls. Vague architecture input produces generic findings; specific
architecture input produces actionable findings.

## Use cases

- AI-agent security review for MCP servers, tool-calling agents, RAG systems,
  and autonomous workflows.
- Application threat modeling for web apps, APIs, mobile backends,
  microservices, batch jobs, and event-driven systems.
- Audit evidence generation for internal audit, customer review, and vendor due
  diligence.
- Release readiness review before major launches or security-sensitive
  releases.
- Control validation that compares identified threats against existing
  compensating controls.
- Security backlog creation from findings, owners, SLAs, and remediation notes.

## What you get

- Structured findings with IDs, severity, and remediation guidance.
- SARIF for code scanning and security dashboards.
- Attack trees and narrative reporting for reviewers.
- Risk scores and ownership metadata for follow-up.
- Visual summaries and PDF assessment artifacts for non-engineering audiences.

---

## Community

- **Questions, ideas, and feature requests** -> [GitHub Discussions](https://github.com/pratik-saptarshi/tachi-rust/discussions)
- **Reproducible bugs** -> [GitHub Issues](https://github.com/pratik-saptarshi/tachi-rust/issues)
- **Security vulnerabilities** -> [private advisory](https://github.com/pratik-saptarshi/tachi-rust/security/advisories/new) (do not post publicly)
- **Full security policy** -> [SECURITY.md](SECURITY.md) (supported versions, response SLA, scope)
- **Pre-commit secret-scanning** -> [docs/standards/PRECOMMIT_HOOKS.md](docs/standards/PRECOMMIT_HOOKS.md) (gitleaks default-secure hook; existing adopters opt in via `pre-commit install`)
- **Publishing gate** -> [docs/publish-readiness-checklist.html.md](docs/publish-readiness-checklist.html.md) and [docs/bill-of-materials.html.md](docs/bill-of-materials.html.md)

If you are new here, start with the [Welcome thread](https://github.com/pratik-saptarshi/tachi-rust/discussions) for how the board is organized.

---

## Prerequisites

tachi requires two external CLIs for full functionality. Both are required:
`typst` compiles the PDF security report, and `@mermaid-js/mermaid-cli`
(`mmdc`) renders attack-path diagrams. See [ADR-022](docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md)
for the rationale.

Harness selection does not change those report prerequisites. It only changes
which adapter pack you install and how you invoke the first analysis.

**macOS**

```bash
brew install typst
npm install -g @mermaid-js/mermaid-cli
```

**Linux** (Debian/Ubuntu)

```bash
apt install typst   # or: cargo install typst-cli / dnf install typst on Fedora
npm install -g @mermaid-js/mermaid-cli
```

**WSL**

```bash
apt install typst
npm install -g @mermaid-js/mermaid-cli
```

`/tachi.security-report` aborts at preflight with a clear install command if
either CLI is missing when attack trees are present.

---

## Quick start

### 1. Clone tachi

```bash
git clone https://github.com/pratik-saptarshi/tachi-rust.git ~/Projects/tachi
```

### 2. Install into your project

From your project root:

```bash
~/Projects/tachi/scripts/install.sh
```

To install a specific version:

```bash
~/Projects/tachi/scripts/install.sh --version v4.37.0 # x-release-please-version
```

If tachi is cloned to a non-default location:

```bash
~/Projects/tachi/scripts/install.sh --source /path/to/tachi
```

If you need a harness-native adapter instead of the core installer, use the
pack that matches your target harness:

| Harness | Adapter surface | First-run entrypoint |
|---|---|---|
| Claude Code | `adapters/claude-code/agents/` | `/tachi.threat-model` |
| Cursor | `adapters/cursor/rules/` | Ask Cursor to run a complete tachi threat model |
| Copilot | `adapters/copilot/agents/` and `adapters/copilot/instructions/` | `@tachi-orchestrator` |
| GitHub Actions | `adapters/github-actions/tachi.threat-model.yml` | Pull request or manual dispatch |
| Codex, OpenCode, Termux, Voltagent, Antigravity, Pi-style harnesses | `adapters/generic/prompts/` | Run the numbered prompts in order |

<details>
<summary>Manual install</summary>

```bash
# Agents (threat analysis engine)
cp -r ~/Projects/tachi/.claude/agents/tachi/ .claude/agents/tachi/

# Commands (6 slash commands)
mkdir -p .claude/commands
for cmd in tachi.threat-model tachi.risk-score tachi.compensating-controls tachi.infographic tachi.security-report tachi.architecture; do
  cp ~/Projects/tachi/.claude/commands/$cmd.md .claude/commands/
done

# Schemas, templates, references, and brand assets
cp -r ~/Projects/tachi/schemas/ schemas/
cp -r ~/Projects/tachi/templates/ templates/
mkdir -p adapters/claude-code/agents
cp -r ~/Projects/tachi/adapters/claude-code/agents/references/ adapters/claude-code/agents/references/
cp -r ~/Projects/tachi/brand/ brand/

# Compatibility guide
mkdir -p docs
cp ~/Projects/tachi/docs/platform-compatibility.md docs/

# Developer guide
mkdir -p docs/guides
cp ~/Projects/tachi/docs/guides/DEVELOPER_GUIDE_TACHI.md docs/guides/
```

</details>

See [`INSTALL_MANIFEST.md`](INSTALL_MANIFEST.md) for the full list of
distributable files.

### 3. Reload Your Harness

After copying the files, restart or reload your harness so it picks up the new
agents, rules, commands, or workflow files.

If you want infographic images (`.jpg`), set `GEMINI_API_KEY` from
[Google AI Studio](https://aistudio.google.com/apikey). This is optional; all
text-based outputs work without it.

### 4. Create your architecture file

Create `docs/security/architecture.md` describing your system. The recommended
path is to let tachi draft it from the current project:

```text
/tachi.architecture
```

By default this writes `docs/security/architecture.md`, captures components,
data flows, trust boundaries, and external entities, and detects LLM, agent,
MCP, RAG, tool, and model-provider components so the AI threat agents activate.

You can also write the file yourself or ask Claude Code directly:

```text
Investigate this repository's architecture -- source code, config files,
infrastructure definitions, READMEs -- and create docs/security/architecture.md
as a Mermaid flowchart with all major components, data flows, protocols, and
trust boundaries.
```

tachi auto-detects the format. Mermaid, free-text, ASCII, PlantUML, and C4 are
all supported.

### 5. Run your first threat model

```text
/tachi.threat-model
```

That is it. One command. tachi validates the setup, reads your architecture,
dispatches 14 threat agents, and writes everything to a timestamped folder
under `docs/security/`.

If you are using another harness:

- Cursor: ask it to run a complete tachi threat model using the installed
  rules.
- Copilot: mention `@tachi-orchestrator` in chat.
- Generic fallback: run `00-orchestrator.md`, then the numbered prompts in
  order, then `12-threat-report.md` and `13-threat-infographic.md`.

### 6. Review your results

| File | Source | What it contains |
|---|---|---|
| `threats.md` | `/tachi.threat-model` | Primary threat model, findings, coverage matrix, MAESTRO layers, risk summary |
| `threats.sarif` | `/tachi.threat-model` | SARIF 2.1.0 for GitHub Code Scanning and CI/CD integration |
| `threat-report.md` | `/tachi.threat-model` | Narrative report with executive summary and remediation roadmap |
| `attack-trees/` | `/tachi.threat-model` | One Mermaid attack tree per Critical/High finding |
| `risk-scores.md` | `/tachi.risk-score` | Quantitative risk scores with CVSS, exploitability, scalability, reachability |
| `risk-scores.sarif` | `/tachi.risk-score` | SARIF 2.1.0 with composite scores as `security-severity` per finding |
| `compensating-controls.md` | `/tachi.compensating-controls` | Detected codebase controls, residual risk, missing control recommendations |
| `compensating-controls.sarif` | `/tachi.compensating-controls` | SARIF 2.1.0 with residual risk as `security-severity` per finding |
| `threat-baseball-card.jpg` | `/tachi.infographic` | Baseball card risk dashboard (requires `GEMINI_API_KEY`) |
| `threat-system-architecture.jpg` | `/tachi.infographic` | Annotated architecture diagram with finding legend |
| `threat-risk-funnel.jpg` | `/tachi.infographic` | Risk distribution funnel by severity |
| `threat-maestro-stack.jpg` | `/tachi.infographic` | MAESTRO layer stack visualization (agentic systems only) |
| `threat-maestro-heatmap.jpg` | `/tachi.infographic` | MAESTRO layer x severity heat map (agentic systems only) |
| `security-report.pdf` | `/tachi.security-report` | Professional PDF booklet with all artifacts assembled |

Start with `threats.md` Section 7, Recommended Actions. Then run
`/tachi.risk-score` for quantitative prioritization,
`/tachi.compensating-controls` to detect existing defenses,
`/tachi.infographic` for visual risk diagrams, and
`/tachi.security-report` to assemble everything into a PDF booklet. Work
through Critical findings first, then High.

> Full walkthrough: the [Developer Guide](docs/guides/DEVELOPER_GUIDE_TACHI.md)
> covers the complete 5-step risk lifecycle with worked examples, advanced
> options, and CI/CD integration.

---

## Command options

### /tachi.threat-model

Runs the 5-phase threat modeling pipeline: scope, determine threats, determine
countermeasures, assess, and report. Produces `threats.md`, `threats.sarif`,
`threat-report.md`, `attack-trees/`, and `attack-chains.md` when cross-layer
chains are detected. Findings include MAESTRO layer classification for
agentic AI components. The command automatically detects a prior baseline for
delta tracking.

```bash
# Default - uses docs/security/architecture.md
/tachi.threat-model

# Specify architecture file
/tachi.threat-model path/to/my-architecture.md

# Custom output directory
/tachi.threat-model docs/security/architecture.md --output-dir reports/security/

# Version-tagged output for a release
/tachi.threat-model docs/security/architecture.md --version v1.0.0

# Explicit baseline for delta comparison
/tachi.threat-model docs/security/architecture.md --baseline docs/security/2026-03-01/threats.md
```

### /tachi.risk-score

Enriches threat-model output with quantitative risk scores and governance
fields. Produces `risk-scores.md` and `risk-scores.sarif`.

```bash
# Score threats in the default location
/tachi.risk-score

# Score threats in a specific directory
/tachi.risk-score docs/security/2026-03-27/

# Custom output directory
/tachi.risk-score docs/security/2026-03-27/ --output-dir reports/risk/
```

### /tachi.compensating-controls

Scans a target codebase against scored threats to detect existing security
controls, calculate residual risk, and recommend missing controls. Requires
`/tachi.risk-score` output as input. Produces `compensating-controls.md` and
`compensating-controls.sarif`.

```bash
# Scan current project against risk scores in the default location
/tachi.compensating-controls

# Scan against risk scores in a specific directory
/tachi.compensating-controls docs/security/2026-03-27/

# Scan a different codebase
/tachi.compensating-controls docs/security/2026-03-27/ --target ~/Projects/my-app/

# Custom output directory
/tachi.compensating-controls docs/security/2026-03-27/ --output-dir reports/controls/
```

### /tachi.infographic

Generates visual threat infographic specifications and presentation-ready
images. Auto-detects the richest data source in the output directory (prefers
`compensating-controls.md` > `risk-scores.md` > `threats.md`). Produces spec
markdown and `.jpg` images.

Templates: `baseball-card`, `system-architecture`, `risk-funnel`,
`maestro-stack`, `maestro-heatmap`, `all`

```bash
# Generate all templates (auto-includes MAESTRO if data present)
/tachi.infographic

# Generate from a specific directory
/tachi.infographic docs/security/2026-03-27/

# Generate a specific template
/tachi.infographic docs/security/2026-03-27/ --template baseball-card
/tachi.infographic docs/security/2026-03-27/ --template risk-funnel

# Generate both MAESTRO templates
/tachi.infographic docs/security/2026-03-27/ --template maestro
```

### /tachi.security-report

Assembles all pipeline artifacts into a professional multi-page PDF security
assessment booklet. Auto-detects available artifacts and conditionally includes
pages. Requires `typst` for PDF compilation and `mmdc` for attack-path diagram
rendering when diagrams are present.

Page types may include: cover, disclaimer, table of contents, risk
methodology, assessment scope, executive summary, attack-path analysis,
attack-chain diagrams, MAESTRO findings, infographic pages, findings detail,
control coverage, and remediation roadmap.

```bash
# Generate PDF from the default location
/tachi.security-report

# Generate from a specific directory
/tachi.security-report docs/security/2026-03-27/

# Custom output path
/tachi.security-report docs/security/2026-03-27/ --output reports/assessment.pdf
```

---

## How it works

tachi uses a multi-agent orchestration pattern. The orchestrator parses your
architecture, identifies components and data flows, and dispatches the right
combination of 14 threat agents per component.

| Component type | STRIDE agents | AI agents |
|---|---|---|
| External entity (users, APIs) | S, R | - |
| Process (servers, agents) | S, T, R, I, D, E | LLM + AG if AI keywords are detected |
| Data store (databases, caches) | T, I, D | - |
| Data flow (API calls, messages) | T, I, D | - |

AI agents activate when component names or descriptions contain keywords such
as LLM, agent, orchestrator, MCP, tool server, embedding, RAG, and related
terms.

After all agents report, the orchestrator deduplicates findings, runs
cross-agent correlation, computes risk ratings, and generates the output suite.

### MAESTRO layer classification

For agentic AI systems, tachi maps each finding to the [CSA MAESTRO](https://cloudsecurityalliance.org/)
seven-layer taxonomy:

| Layer | Name | Scope |
|---|---|---|
| L1 | Foundation model | Pre-trained LLMs, inference engines |
| L2 | Data operations | Vector stores, RAG pipelines, embeddings |
| L3 | Agent framework | Orchestrators, tool servers, MCP |
| L4 | Deployment infrastructure | API gateways, containers, networking |
| L5 | Evaluation and observability | Audit logging, monitoring, anomaly detection, forensics |
| L6 | Security and compliance | Auth, guardrails, rate limiting, encryption, IAM |
| L7 | Agent ecosystem | Multi-agent coordination, delegation, chat UIs, API endpoints |

MAESTRO layers appear in `threats.md`, propagate through downstream commands,
and power the `maestro-stack` and `maestro-heatmap` infographic templates.

### Agentic pattern synthesis

For multi-agent architectures, tachi's Pattern Synthesis Engine classifies
findings into six canonical cross-cutting agentic patterns:

| Pattern | Canonical definition |
|---|---|
| `agent_collusion` | Multiple compromised agents coordinate to achieve malicious objectives |
| `emergent_behavior` | Unpredictable behaviors arising from multi-agent interactions |
| `temporal_attack` | Persistent-state exploits such as sleeper agents or gradual corruption |
| `trust_exploitation` | Inter-agent identity spoofing, reputation manipulation, trust-chain attacks |
| `communication_vulnerability` | Inter-agent message interception, protocol manipulation, routing attacks |
| `resource_competition` | Resource monopolization, priority manipulation, coordination disruption |


Each finding receives a new `agentic_pattern` enum field (schema 1.4) during Phase 3.6 — gated by the multi-agent predicate (≥2 agentic/LLM components, inter-agent data flow, or explicit multi-agent keywords in the architecture description). Pattern assignments appear in `threats.md` Section 7 (Pattern column), Section 4b (Findings by Agentic Pattern), `threat-report.md` Section 7 (Agentic Pattern Analysis narrative), and SARIF `maestro-pattern:<name>` tags mirroring the existing `maestro-layer:<L#>` convention. The deterministic classification rule table and the multi-agent gate predicate live in [`maestro-agentic-patterns-shared.md`](.claude/skills/tachi-shared/references/maestro-agentic-patterns-shared.md).

Previously-uncovered patterns (Agent Collusion, Temporal Attacks, Emergent Behavior) that are not captured by any individual detection agent surface via net-new findings with the `AGP-NN` id prefix, generated deterministically when the architecture satisfies a rule's topology preconditions but no existing finding carries the pattern label.

### Baseline Delta Tracking

When you run `/tachi.threat-model` on a system that already has a previous run, tachi automatically detects the baseline and computes a delta: new findings, resolved findings, unchanged findings, and updated findings. This lets you track risk posture changes over time without manual diffing.

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

### AI-Specific (8 categories)

| Category | Threat | Example |
|----------|--------|---------|
| **Prompt Injection** (LLM) | Adversarial inputs hijacking LLM behavior | Hidden instructions in a document causing the LLM to leak its system prompt |
| **Data Poisoning** (LLM) | Corrupted training/RAG data | Attacker modifying knowledge base documents to spread misinformation |
| **Model Theft** (LLM) | Model extraction or unbounded consumption | Competitor reverse-engineering your fine-tuned model via API queries; cost-amplification denial-of-wallet |
| **Output Integrity** (LLM) | Improper handling of LLM output flowing into execution sinks | LLM-generated SQL passed to a database client without parameterization; markdown XSS in a rendered chat reply |
| **Misinformation** (LLM) | Factually incorrect or fabricated LLM output reaching humans/decisions | Clinical advisory LLM hallucinating drug dosages without RAG grounding |
| **Agent Autonomy** (AG) | Insufficient oversight | AI agent sending 500 emails without human approval |
| **Tool Abuse** (AG) | Tool misuse or manipulation | Malicious MCP plugin exfiltrating source code when invoked; insecure inter-agent communication |
| **Human-Agent Trust Exploitation** (AG) | Communication-axis trust manipulation toward human users | Wellness chatbot subtly claiming medical authority while concealing AI authorship |

---

## OWASP Coverage

tachi ships at full coverage across five OWASP frameworks (50/50 items covered). Every finding can carry an optional [`source_attribution`](docs/architecture/02_ADRs/ADR-028-source-attribution-schema-extension.md) field citing OWASP / MITRE ATT&CK / MITRE ATLAS / NIST AI RMF / CWE items, and the `tachi.security-report` PDF emits a per-architecture **Coverage Attestation** page aggregating coverage across cited frameworks.

| Framework | Items Covered | Detection Surface |
|-----------|---------------|-------------------|
| OWASP Top 10 for LLM Applications 2025 | 10/10 | LLM agents (`prompt-injection`, `data-poisoning`, `model-theft`, `output-integrity`, `misinformation`) |
| OWASP Agentic Top 10 2026 | 10/10 | Agentic agents (`agent-autonomy`, `tool-abuse`, `human-trust-exploitation`) |
| OWASP ML Top 10 2023 | 10/10 | `tampering` + `data-poisoning` + `model-theft` enrichment for predictive ML |
| OWASP Mobile Top 10 2024 | 10/10 | `spoofing` + `tampering` + `info-disclosure` + `privilege-escalation` + `repudiation` enrichment for mobile |
| OWASP Top 10:2021 + API Security Top 10:2023 | 10/10 | STRIDE detection agents with cross-framework `source_attribution` populator wiring |

See [`schemas/taxonomy/`](schemas/taxonomy/README.md) for the cross-framework crosswalk catalog (38 ATT&CK + 7 ATLAS + 41 CWE references currently cited, plus NIST AI RMF mappings).

---

## Examples

The [`examples/`](examples/) directory contains complete threat models across different input formats and architectures:

| Example | Input Format | Architecture | Threat Categories |
|---------|-------------|-------------|-------------------|
| [Agentic App](examples/agentic-app/) | Mermaid | LLM orchestrator + MCP tools | STRIDE + AI + MAESTRO |
| [Mermaid Agentic App](examples/mermaid-agentic-app/) | Mermaid | Multi-agent system | STRIDE + AI |
| [Web App](examples/web-app/) | Mermaid | Traditional web application | STRIDE |
| [Microservices](examples/microservices/) | Mermaid | Cross-service architecture | STRIDE |
| [ASCII Web API](examples/ascii-web-api/) | ASCII | REST API with database | STRIDE |
| [Free-text Microservice](examples/free-text-microservice/) | Free-text | Event-driven microservice | STRIDE |

The agentic-app example includes a [complete sample report](examples/agentic-app/sample-report/) showing every artifact the pipeline produces -- structured findings, SARIF, narrative report, attack trees, cross-layer attack chains, risk scores, compensating controls, and infographics:

![Threat Baseball Card](examples/agentic-app/sample-report/threat-baseball-card.jpg)

![System Architecture](examples/agentic-app/sample-report/threat-system-architecture.jpg)

![Risk Funnel](examples/agentic-app/sample-report/threat-risk-funnel.jpg)

---

## Integration Reference

| Resource | Location | Purpose |
|----------|----------|---------|
| Interface Contract | [`docs/INTERFACE-CONTRACT.md`](docs/INTERFACE-CONTRACT.md) | Input formats, invocation protocol, output structure |
| Output Templates | [`templates/tachi/`](templates/tachi/) | Canonical output structures and Typst PDF templates |
| Schemas | [`schemas/`](schemas/) | Machine-readable contracts ([finding.yaml](schemas/finding.yaml), [input.yaml](schemas/input.yaml), [output.yaml](schemas/output.yaml), [risk-scoring.yaml](schemas/risk-scoring.yaml), [aisvs.yaml](schemas/aisvs.yaml)) |
| Taxonomy Crosswalk | [`schemas/taxonomy/`](schemas/taxonomy/README.md) | Machine-readable catalog of OWASP/MITRE/NIST/CWE IDs + cross-framework crosswalk, including the AISVS taxonomy catalog at [taxonomy/aisvs.yaml](schemas/taxonomy/aisvs.yaml) (Feature 180 F-A1) |
| Source Attribution | [`docs/architecture/02_ADRs/ADR-028-source-attribution-schema-extension.md`](docs/architecture/02_ADRs/ADR-028-source-attribution-schema-extension.md) | Optional `source_attribution` finding field (schema 1.5) citing F-A1 framework IDs — contract only (Feature 189 F-A2) |
| Threat Agents | [`.claude/agents/tachi/`](.claude/agents/tachi/) | 14 detection agents (6 STRIDE + 5 LLM + 3 Agentic) + 7 utility agents (orchestrator, attack-tree-delta, threat-report, threat-infographic, risk-scorer, control-analyzer, report-assembler) |
| Commands | [`.claude/commands/`](.claude/commands/) | 6 slash commands: tachi.threat-model, tachi.risk-score, tachi.compensating-controls, tachi.infographic, tachi.security-report, tachi.architecture |
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

## Releases

Releases are automated via [release-please](https://github.com/googleapis/release-please). When conventional commits (`feat:`, `fix:`, `docs:`, etc.) are merged to `main`, release-please updates the release state on push and creates the next semantic tag and GitHub Release directly (no separate release PR branch churn).

To install a specific version: `install.sh --version v4.37.0` <!-- x-release-please-version -->

---

## Running Tests

tachi-rust uses Rust-native tests plus the Rust-backed coverage audit as the current validation path:

```bash
cargo test
make coverage-audit
make llvm-cov
cargo clippy --all-targets -- -D warnings
```

This runs the Rust test suite, the Rust-backed coverage audit, the LLVM coverage report with toolchain-local LLVM binaries, and Clippy warning gates. Publishing work should keep Rust coverage at or above the project floor documented in [`docs/standards/PUBLISHING_SECURITY.md`](docs/standards/PUBLISHING_SECURITY.md); as of 2026-06-24, `make llvm-cov` reports 85.33% line coverage, which clears the current 85% migration floor.

The legacy compatibility target remains available for archival migration use, but it is intentionally not listed as part of the Rust-native validation path above.

---

## Contributing

We welcome contributions. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

Apache 2.0 License. See [LICENSE](LICENSE) for details.
