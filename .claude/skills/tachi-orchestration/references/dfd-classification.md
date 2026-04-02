---
source_agent: orchestrator
extracted_from: .claude/agents/tachi/orchestrator.md
version: 1.0.0
---

# DFD Classification Reference

Classify each component extracted from the architecture input as one of the four Data Flow Diagram (DFD) element types. The DFD classification determines which STRIDE categories apply to each component (via the STRIDE-per-Element normalization in dispatch rules) and drives the coverage gate requirements.

---

## DFD Element Types

### External Entity

Users, external systems, third-party services, or anything that exists outside the system boundary. External entities interact with the system but are not controlled by it.

**Classification signals**:
- Labeled as user, client, customer, external service, third-party provider, browser, mobile app
- Positioned outside trust boundaries or system boundaries in diagrams
- Described as sending requests to or receiving responses from the system

**Examples**: "User", "External API", "Third-party Auth Provider", "Mobile Client", "Browser"

### Process

Services, applications, servers, agents, orchestrators, or any component that actively processes, transforms, or routes data. Processes are the most broadly threatened element type (subject to all 6 STRIDE categories).

**Classification signals**:
- Labeled as service, server, gateway, handler, controller, agent, orchestrator, engine, worker, processor
- Described as receiving input, performing operations, and producing output
- Acts as an intermediary between other components

**Examples**: "API Gateway", "Auth Service", "LLM Agent Orchestrator", "MCP Tool Server", "Payment Processor"

### Data Store

Databases, file systems, caches, knowledge bases, message queues, or any component that persists or buffers data.

**Classification signals**:
- Labeled as database, DB, cache, store, queue, repository, knowledge base, file system, bucket, log
- Described as storing, persisting, buffering, or retaining data
- In Mermaid diagrams, often uses the `[( )]` cylinder notation

**Examples**: "User DB", "Knowledge Base", "Redis Cache", "Message Queue", "S3 Bucket"

### Data Flow

Connections, API calls, messages, or data transfers between components. Data flows represent the movement of data through the system and are typically represented as arrows or relationships in diagrams.

**Classification signals**:
- Represented as arrows, edges, or relationship lines in diagrams
- Described as API calls, requests, responses, messages, or data transfers between named components
- Has a source component and a destination component

**Examples**: "HTTPS Request from Client to Gateway", "SQL Query from Service to DB", "gRPC call between microservices"

---

## Ambiguous Classification Rule

When a component cannot be confidently classified into one of the four DFD element types, apply the following default:

- **Default to Process** (broadest STRIDE coverage -- all 6 categories apply).
- Flag the classification for human review by adding a note in the component's Description field: `"[Classification uncertain -- defaulted to Process for maximum threat coverage]"`.

This ensures no component receives insufficient threat analysis due to misclassification. Process is the safest default because it triggers analysis for all 6 STRIDE categories, whereas other types have narrower coverage sets.

---

## Format-Specific Extraction Guidance

### ASCII

Extract components from box-drawing structures (`+--+...+--+`) and bracket labels (`[Label]`). Extract data flows from arrow connectors (`-->`, `<--`, `<-->`). Each box or bracketed label is a component. Each arrow between components is a data flow.

### Free-text

Extract components by identifying nouns and noun phrases that refer to system elements (services, databases, users, APIs, agents). Extract data flows from verbs and phrases describing interactions between components (sends, queries, forwards, connects to, calls). Parse sentence structure to identify source-destination relationships.

### Mermaid

Extract components from node definitions (`A[Label]`, `B((Label))`, `C{Label}`, `D[(Label)]`). The label text inside the delimiters is the component name. Extract data flows from edge definitions (`-->`, `--->`, `-.->`) connecting nodes. `subgraph` blocks define trust boundaries, not components -- the components are the nodes within them.

### PlantUML

Extract components from declarations: `actor` for external entities, `[Component]` for processes, `database` for data stores, and other stereotype-annotated elements. Extract data flows from relationship arrows (`->`, `-->`, `.>`). Boundary blocks (`boundary`, `rectangle`) define trust boundaries, not components.

### C4

Extract components from C4 function calls: `Person(...)` for external entities, `System(...)` / `Container(...)` / `Component(...)` for processes, `ContainerDb(...)` / `ComponentDb(...)` for data stores. The second argument in each function call is the display label. Extract data flows from `Rel(...)` declarations. `System_Boundary(...)` and `Enterprise_Boundary(...)` define trust boundaries, not components.

---

## DFD Type to STRIDE Coverage Summary

The DFD classification directly determines which STRIDE categories apply to each component:

| DFD Type | Applicable STRIDE Categories |
|----------|------------------------------|
| External Entity | S, R |
| Process | S, T, R, I, D, E |
| Data Store | T, I, D |
| Data Flow | T, I, D |

This mapping is the basis of the STRIDE-per-Element normalization defined in the dispatch rules reference. Process components receive the broadest analysis (all 6 categories), which is why uncertain classifications default to Process.
