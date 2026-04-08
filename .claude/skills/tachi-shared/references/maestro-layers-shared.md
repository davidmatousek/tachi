---
type: shared-reference
name: maestro-layers-shared
version: 1.0.0
source_schema: schemas/finding.yaml
consumers:
  - orchestrator
  - risk-scorer
  - control-analyzer
  - threat-report
---

# MAESTRO Layers — Shared Reference

Canonical CSA MAESTRO seven-layer taxonomy definitions for agentic AI architectures. This is the single source of truth for layer identifiers, descriptions, keyword mappings, and the classification algorithm used during Phase 1 (Scope). All consuming agents should Read this file rather than maintaining inline definitions.

**Source**: Cloud Security Alliance — MAESTRO (Multi-Agent Environment Security Toolkit for Reasoning and Orchestration), February 2025.

---

## Classification Algorithm

MAESTRO layer classification runs during Phase 1 after DFD classification. It assigns exactly one layer to each component using keyword matching.

### Rules

1. **Input**: Component name, description, and DFD type (all three fields).
2. **Matching**: Case-insensitive substring match. A keyword match anywhere within any of the three input fields triggers a layer assignment.
3. **Evaluation order**: Layers are evaluated in order L1 through L7. The first matching layer wins.
4. **Single assignment**: Each component receives exactly one layer — no multi-layer assignments.
5. **Default**: Components matching no layer keywords are assigned `"Unclassified"` without error.
6. **Multi-word keywords**: Keywords containing spaces match as a complete phrase (adjacent, in order).

### Ordering Rationale

The L1-L7 evaluation order is load-bearing — changing the order changes classification results. The ordering follows a specificity gradient:

- **L1 (Foundation Model)** is evaluated first because foundation model keywords are the most specific and least ambiguous.
- **L7 (User Interface)** is evaluated last because UI keywords (e.g., "API endpoint") are the most general and could match components at other layers.
- **L4 (Deployment Infrastructure)** and **L5 (Security)** are evaluated in the middle because their keywords have moderate specificity.

**WARNING**: Changing keyword order changes classification. Test against all example architectures after any modification to the keyword table.

---

## Seven-Layer Taxonomy

| Layer ID | Layer Name | Description | Example Components |
|----------|-----------|-------------|-------------------|
| L1 | Foundation Model | Pre-trained or fine-tuned large language models and their inference engines | GPT-4o, Claude, Gemini, fine-tuned model, inference endpoint |
| L2 | Data Operations | Data pipelines, vector stores, embedding indexes, and training/retrieval data management | Vector DB, RAG pipeline, training dataset, embedding index, knowledge base |
| L3 | Agent Framework | Orchestration layers, planning engines, tool dispatch, and agent execution frameworks | Agent orchestrator, tool server, MCP server, workflow engine, planner |
| L4 | Deployment Infrastructure | Runtime environments, networking, and infrastructure services | API gateway, load balancer, Kubernetes cluster, container runtime, CDN |
| L5 | Security | Authentication, authorization, content filtering, and security monitoring | WAF, auth service, secrets manager, guardrail, rate limiter, IAM |
| L6 | Agent Ecosystem | Multi-agent coordination, delegation, and inter-agent communication | Multi-agent supervisor, agent mesh, delegation broker, swarm coordinator |
| L7 | User Interface | User-facing surfaces and API endpoints for human interaction | Chat UI, admin dashboard, REST API, GraphQL endpoint, web portal |

---

## Keyword-to-Layer Mapping

Keywords are matched case-insensitively against component name, description, and DFD type. Evaluated in L1-L7 order; first match wins.

### L1 — Foundation Model

| Keyword |
|---------|
| LLM |
| language model |
| GPT |
| Claude |
| Gemini |
| base model |
| fine-tuned model |
| model weights |
| foundation model |
| inference engine |

### L2 — Data Operations

| Keyword |
|---------|
| vector |
| RAG |
| embedding |
| training data |
| data pipeline |
| knowledge base |
| vector DB |
| vector store |
| fine-tuning |
| dataset |
| corpus |
| index |
| database |
| cache |

### L3 — Agent Framework

| Keyword |
|---------|
| orchestrator |
| planner |
| executor |
| tool dispatch |
| agent framework |
| tool server |
| MCP server |
| function calling |
| chain |
| workflow engine |

### L4 — Deployment Infrastructure

| Keyword |
|---------|
| container |
| runtime |
| API gateway |
| load balancer |
| reverse proxy |
| CDN |
| DNS |
| ingress |
| kubernetes |
| docker |
| serverless |
| network |
| queue |
| registry |

### L5 — Security

| Keyword |
|---------|
| auth |
| WAF |
| firewall |
| secrets manager |
| audit log |
| guardrail |
| content filter |
| rate limit |
| encryption |
| RBAC |
| IAM |
| access control |
| security |

### L6 — Agent Ecosystem

| Keyword |
|---------|
| multi-agent |
| agent-to-agent |
| swarm |
| delegation |
| coordination |
| supervisor |
| sub-agent |
| agent registry |
| agent mesh |

### L7 — User Interface

| Keyword |
|---------|
| chat UI |
| dashboard |
| admin console |
| web interface |
| frontend |
| user portal |
| API endpoint |
| REST API |
| GraphQL |
| client |
| user |

---

## Output Format

### Component Inventory (Phase 1)

When classification completes, the component inventory includes a MAESTRO Layer column:

| Component | DFD Type | MAESTRO Layer | Description |
|-----------|----------|---------------|-------------|
| LLM Service | Process | L1 — Foundation Model | GPT-4o inference endpoint |
| Vector DB | Data Store | L2 — Data Operations | RAG vector store for document retrieval |
| Agent Orchestrator | Process | L3 — Agent Framework | Central planning and tool dispatch |

### Finding Inheritance (Phase 3)

Each finding inherits `maestro_layer` from its target component's Phase 1 classification:
- Look up the finding's `component` in the Phase 1 component inventory.
- Copy the component's `maestro_layer` value to the finding.
- If the component is not found in the inventory, default to `"Unclassified"`.
