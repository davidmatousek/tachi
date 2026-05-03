# Quickstart: Example Threat Models

## Overview

Feature 024 adds three standardized example threat models to the `examples/` directory. Each example pairs a Mermaid architecture diagram (`architecture.md`) with a complete threat model output (`threats.md`).

## Examples

| Example | Architecture | Threat Frameworks | Key Demo |
|---------|-------------|-------------------|----------|
| `web-app` | Frontend + API + Auth + DB | STRIDE + OWASP Web 2025 | Baseline output, empty AI sections |
| `agentic-app` | LLM + MCP + Agents + KB | STRIDE + AI + OWASP Agentic + MCP | AI-specific findings, correlated findings |
| `microservices` | Gateway + Services + MQ + DBs | STRIDE + OWASP Web 2025 | Cross-service threats at scale |

## How to Use

### 1. Browse Examples

Open any example's `architecture.md` to see the input and `threats.md` to see the output. GitHub renders Mermaid diagrams automatically.

### 2. Compare with Your Own Results

Run tachi against an example's `architecture.md`:

```bash
# Analyze the web-app example
tachi analyze examples/web-app/architecture.md

# Compare your output with the reference
diff examples/web-app/threats.md output/threats.md
```

### 3. Use as Templates

Copy an example directory and modify the architecture diagram to match your system:

```bash
cp -r examples/web-app my-project
# Edit my-project/architecture.md with your architecture
tachi analyze my-project/architecture.md
```

## Files Created

```
examples/
├── README.md                    # Overview + framework hierarchy
├── web-app/architecture.md      # Mermaid: 4 components
├── web-app/threats.md           # Schema v1.1, STRIDE-only
├── agentic-app/architecture.md  # Mermaid: 5+ components
├── agentic-app/threats.md       # Schema v1.1, STRIDE + AI
├── microservices/architecture.md # Mermaid: 7+ components
└── microservices/threats.md     # Schema v1.1, STRIDE-only
```

## Validation

Each example is validated against:
- Schema v1.1 (`schemas/output.yaml`) — all 8 sections present
- OWASP 3x3 risk matrix — risk levels internally consistent
- STRIDE-per-Element rules — coverage matrix `n/a` cells correct
- Mermaid rendering — diagrams render in GitHub
