# Examples

Example architecture inputs and their corresponding threat model outputs. These serve as reference implementations for users evaluating tachi and as test fixtures for validating agent behavior.

> **New here and interested in MAESTRO?** Start with [`maestro-reference/README.md`](maestro-reference/README.md) — a canonical healthcare-CDSS multi-agent walkthrough demonstrating MAESTRO layer coverage, cross-layer attack chains, and agentic pattern classification across all 7 layers. For format-specific parsing validation, see the "Format-Specific Test Fixtures" section below.

## Standardized Examples

Five polished examples demonstrate tachi's threat modeling capabilities across different architecture types. Each example pairs a Mermaid architecture diagram (`architecture.md`) with a complete schema v1.1+ threat model output (`threats.md`).

| Example | Architecture | Components | Key Demonstration |
|---------|-------------|------------|-------------------|
| [`web-app/`](web-app/) | Traditional multi-tier web application | 6 (CDN, API Gateway, Auth Service, Session Store, User Database) | Baseline STRIDE output with correctly empty AI sections |
| [`agentic-app/`](agentic-app/) | Agentic AI application with LLM and MCP | 7 (Guardrails, LLM Orchestrator, MCP Tool Server, Knowledge Base, Audit Logger) | STRIDE + AI findings, correlated findings, dual-dispatch |
| [`consumer-agent-app/`](consumer-agent-app/) | Consumer-facing AI companion (mental-health/wellness archetype) | 4 (End User, WellnessCompanionChatbot, Conversation Session Store, Interaction Audit Log) | Triggers F-4 `human-trust-exploitation` agent (OWASP ASI09:2026 communication axis) — single Process emitting to End User External Entity; engages all 4 FR-006 emission indicators (outgoing flow to human-named entity, consumer-facing prose match on `chatbot`/`companion`/`coach`, persistent persona/multi-turn dialogue, wellness coaching authority) |
| [`microservices/`](microservices/) | E-commerce microservices platform | 10 (API Gateway, Order/Payment/Notification Services, Message Queue, Databases) | Cross-service threat analysis at scale |
| [`maestro-reference/`](maestro-reference/) | Healthcare CDSS multi-agent reference scenario | 18 (Physician, Supervisor Orchestrator, Diagnostic Agent, Treatment Planner Agent, Risk Stratification Model, Outcomes Telemetry, Inter-Agent Communication Channel, +11 supporting components) | Canonical MAESTRO walkthrough — all 7 layers, cross-layer attack chains, agentic patterns, compliance posture cross-references |

### F-4 `consumer-agent-app` Baseline (Wave 5 regen, 2026-04-26)

The `consumer-agent-app/` baseline was added as a clean-slate Q5 lean baseline (architect Wave 3 Step 1 decision) to provide a deterministic, minimal trigger surface for the F-4 `human-trust-exploitation` agent (OWASP ASI09:2026 communication axis) — distinct from extending the existing `agentic-app/` baseline. The architecture (`consumer-agent-app/architecture.md`, 48 lines / 7287 bytes) defines a single mental-health/wellness companion Process emitting to a human-named End User External Entity, engaging all four FR-006 emission indicators (outgoing flow to human-named entity, consumer-facing prose match, persistent persona/multi-turn dialogue, wellness coaching authority).

**Wave 5 regen output** (under `consumer-agent-app/sample-report/`):
- 5 `TE-{N}` findings (TE-1 through TE-5, one per Pattern Category 1-5: undisclosed AI authorship / authority-claim emission / persuasive-tone manipulation / persona-boundary violations / synthetic-relationship exploitation)
- 19 total findings (1 Critical, 8 High, 7 Medium, 3 Low)
- 6 / 6 infographic JPEGs generated (baseball-card / system-architecture / executive-architecture / risk-funnel / maestro-stack / maestro-heatmap)
- 40-page security PDF with SHA-256 `7ac0b6392c9d197ada547660cace8b9f15eacd75b58f1cc2569c5f358269bce5` (byte-identical baseline preserved per ADR-021 `SOURCE_DATE_EPOCH=1700000000` invariant)

## Framework Relationship Hierarchy

STRIDE is the base threat modeling methodology. OWASP frameworks provide classification overlays that map findings to industry-recognized vulnerability categories.

```mermaid
graph TD
    STRIDE[STRIDE Methodology]

    subgraph OWASP Classification Frameworks
        Web[OWASP Top 10 Web 2025]
        Agentic[OWASP Agentic Top 10 2026]
        MCP[OWASP MCP Top 10 2025]
    end

    STRIDE -->|classifies web findings| Web
    STRIDE -->|extends with AI agents| Agentic
    STRIDE -->|extends with MCP agents| MCP
    Agentic -.->|cross-references| MCP
```

**How they relate:**
- **STRIDE** (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) is applied to every component via STRIDE-per-Element dispatch rules
- **OWASP Top 10 Web 2025** (A01–A10) classifies STRIDE findings against web vulnerability categories
- **OWASP Agentic Top 10 2026** (ASI01–ASI10) classifies AI agent-specific findings (agent autonomy, tool abuse)
- **OWASP MCP Top 10 2025** (MCP01–MCP10) classifies MCP/LLM-specific findings (prompt injection, data poisoning)

## Example-to-Framework Mapping

| Example | STRIDE | OWASP Web 2025 | OWASP Agentic 2026 | OWASP MCP 2025 | AI Sections |
|---------|--------|----------------|---------------------|----------------|-------------|
| `web-app` | All 6 categories | A01–A10 (8 mapped) | n/a | n/a | Empty (no AI components) |
| `agentic-app` | All 6 categories | A01–A10 (8 mapped) | ASI01–ASI10 (3 mapped) | MCP01–MCP10 (3 mapped) | Populated (AG + LLM + correlations) |
| `consumer-agent-app` | All 6 categories | A01–A10 (subset) | ASI09 (communication axis) | n/a | Populated (TE-1 through TE-5 communication-axis findings) |
| `microservices` | All 6 categories | A01–A10 (8 mapped) | n/a | n/a | Empty (no AI components) |

## Usage Instructions

### Browse Examples

Open any example's `architecture.md` to see the input diagram and `threats.md` to see the complete threat model output. GitHub renders Mermaid diagrams automatically.

### Sample Report

The [`agentic-app/sample-report/`](agentic-app/sample-report/) directory contains the complete output from running tachi against the agentic-app architecture. This shows every artifact the pipeline produces:

| File | Description |
|------|-------------|
| `threats.md` | Structured threat model with findings, coverage matrix, and risk summary |
| `threats.sarif` | SARIF 2.1.0 for GitHub Code Scanning integration |
| `threat-report.md` | Narrative report with executive summary and remediation roadmap |
| `attack-trees/` | 27 Mermaid attack trees for Critical and High findings |
| `threat-baseball-card.jpg` | Risk summary dashboard infographic |
| `threat-system-architecture.jpg` | Annotated architecture diagram with attack surface badges |

**Risk Summary Dashboard:**

![Threat Baseball Card](agentic-app/sample-report/threat-baseball-card.jpg)

**Annotated Architecture:**

![System Architecture](agentic-app/sample-report/threat-system-architecture.jpg)

### Compare with Your Own Results

Run tachi against an example's `architecture.md` and compare the output with the reference `threats.md`:

```bash
# Analyze the web-app example
tachi analyze examples/web-app/architecture.md

# Compare your output with the reference
diff examples/web-app/threats.md output/threats.md
```

### Use as Templates

Copy an example directory and replace the architecture diagram with your own system:

```bash
cp -r examples/web-app my-project
# Edit my-project/architecture.md with your architecture
tachi analyze my-project/architecture.md
```

## Format-Specific Test Fixtures

Three additional examples validate tachi's input format handling. These are retained as test fixtures and use the older schema v1.0 format:

| Example | Input Format | Purpose |
|---------|-------------|---------|
| [`ascii-web-api/`](ascii-web-api/) | ASCII box-drawing | Validates ASCII diagram parsing |
| [`free-text-microservice/`](free-text-microservice/) | Free-text prose | Validates natural language input |
| [`mermaid-agentic-app/`](mermaid-agentic-app/) | Mermaid flowchart | Validates Mermaid parsing with AI dispatch |
