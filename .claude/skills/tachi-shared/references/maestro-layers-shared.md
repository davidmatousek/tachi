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

**Source**: Cloud Security Alliance — MAESTRO (Multi-Agent Environment, Security, Threat, Risk, and Outcome), February 2025.

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

The L1-L7 evaluation order follows a specificity gradient from most specific to most general, with observability placed before security to ensure detective controls are classified correctly.

- **L1 (Foundation Models)** is evaluated first because foundation model keywords (LLM, GPT, Claude, Gemini, inference engine) are the most specific and least ambiguous — they rarely match components at other layers.
- **L2 (Data Operations)** follows because data pipeline keywords (vector, RAG, embedding, dataset) are domain-specific to data handling infrastructure.
- **L3 (Agent Frameworks)** is next because agent orchestration keywords (orchestrator, planner, tool dispatch, MCP server) are specific to agentic orchestration layers.
- **L4 (Deployment Infrastructure)** is evaluated in the middle because infrastructure keywords (container, load balancer, API gateway) are common but clearly scoped to runtime deployment.
- **L5 (Evaluation and Observability)** is evaluated before L6 Security so that detective control keywords (audit log, monitoring, SIEM, anomaly detection, telemetry) classify to the observability layer rather than being misrouted to security. This ordering resolves the semantic ambiguity where "audit log" could match either layer — first-match-wins with L5-before-L6 gives the correct observability classification.
- **L6 (Security and Compliance)** is evaluated after L5 because security keywords (auth, WAF, firewall, guardrail, RBAC, IAM) are specific to preventive controls and access enforcement. Components matching both L5 and L6 keywords classify to L5 first (e.g., "security audit log" → L5 via `audit log` match).
- **L7 (Agent Ecosystem)** is evaluated last because it is the broadest catch-all — covering multi-agent coordination (multi-agent, swarm, delegation), agent-to-agent protocols, and human-agent interaction (chat UI, dashboard, API endpoint, web portal). Keywords here are the most general and could potentially match components at other layers, so L7 evaluates last to avoid capturing specific components that belong elsewhere.

**WARNING**: Changing keyword order changes classification. The L5-before-L6 ordering is load-bearing for canonical MAESTRO observability/security separation. Test against all six example architectures after any modification to the keyword table.

---

## Seven-Layer Taxonomy

| Layer ID | Layer Name | Description | Example Components |
|----------|-----------|-------------|-------------------|
| L1 | Foundation Model | Pre-trained or fine-tuned large language models and their inference engines | GPT-4o, Claude, Gemini, fine-tuned model, inference endpoint |
| L2 | Data Operations | Data pipelines, vector stores, embedding indexes, and training/retrieval data management | Vector DB, RAG pipeline, training dataset, embedding index, knowledge base |
| L3 | Agent Framework | Orchestration layers, planning engines, tool dispatch, and agent execution frameworks | Agent orchestrator, tool server, MCP server, workflow engine, planner |
| L4 | Deployment Infrastructure | Runtime environments, networking, and infrastructure services | API gateway, load balancer, Kubernetes cluster, container runtime, CDN |
| L5 | Evaluation and Observability | Detective controls, logging, monitoring, anomaly detection, forensics, and telemetry collection | Audit logger, SIEM, observability stack, metrics collector, alerting system, forensic log store |
| L6 | Security and Compliance | Authentication, authorization, content filtering, preventive controls, and compliance enforcement | WAF, auth service, secrets manager, guardrail, rate limiter, IAM, RBAC, encryption service |
| L7 | Agent Ecosystem | Multi-agent coordination, delegation, agent-to-agent communication, and human-agent interaction surfaces | Multi-agent supervisor, agent mesh, delegation broker, swarm coordinator, chat UI, admin dashboard, REST API |

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

### L5 — Evaluation and Observability

| Keyword |
|---------|
| audit log |
| monitoring |
| SIEM |
| anomaly detection |
| telemetry |
| log |
| metrics |
| tracing |
| forensics |
| alerting |
| observability |

### L6 — Security and Compliance

| Keyword |
|---------|
| auth |
| WAF |
| firewall |
| secrets manager |
| guardrail |
| content filter |
| rate limit |
| encryption |
| RBAC |
| IAM |
| access control |
| security |

### L7 — Agent Ecosystem

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
