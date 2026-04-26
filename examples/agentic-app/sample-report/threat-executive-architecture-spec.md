---
schema_version: "1.0"
template: "executive-architecture"
date: "2026-04-26"
source_file: "compensating-controls.md"
data_source_type: "compensating-controls"
finding_count: 81
image_generated: true
has_baseline: true
delta_note: "NEW finding AG-8 (Inter-Agent Communication Channel, OWASP ASI07:2026, raw Critical — residual High after controls)"
---

## 1. Metadata

| Field | Value |
|-------|-------|
| template_name | executive-architecture |
| tier_source | compensating-controls |
| source_file | /Users/david/Projects/tachi/examples/agentic-app/test-output/2026-04-26T03-39-12-F3-wave3/threats.md |
| generation_timestamp | 2026-04-26T04:47:13Z |
| qualifying_layer_count | 3 |
| total_filtered_count | 8 |
| skip_image | false |
| fallback_used | false |

**Delta Context**: This executive-architecture view shows the system across 3 trust zone layers (User Zone, External Services, Application Zone). 8 qualifying High-severity findings are distributed across 5 callouts after layer-dedup. AG-8 (NEW — Inter-Agent Communication Channel, OWASP ASI07:2026) is visible as a callout in the Application Zone layer, anchored to the Inter-Agent Communication Channel node. No Critical residual findings — all High.

---

## 2. Architecture Layers

Ordered top-to-bottom (position 0 = most exposed / untrusted):

### Layer 0 — User Zone (untrusted, position 0)

- **Components**: User
- **Component count**: 1
- **Source kind**: trust_zone
- **Overflow**: none

### Layer 1 — External Services (semi-trusted, position 1)

- **Components**: External API
- **Component count**: 1
- **Source kind**: trust_zone
- **Overflow**: none

### Layer 2 — Application Zone (trusted, position 2)

- **Components**: Audit Logger, Clinical Advisory Sub-Agent, Guardrails Service, Inter-Agent Communication Channel, Knowledge Base, LLM Agent Orchestrator, Long-Running Learning Loop, MCP Tool Server, Specialist Agent
- **Component count**: 9
- **Source kind**: trust_zone
- **Overflow**: + 3 more in this layer (Knowledge Base, Long-Running Learning Loop, Audit Logger not displayed as primary nodes)

---

## 3. Threat Callouts

5 callouts selected from 8 qualifying High-severity findings (post-layer dedup, weighted Largest Remainder Method):

| # | Layer | Finding ID | Severity | Composite Score | Affected Component | Raw Description |
|---|-------|-----------|----------|-----------------|-------------------|-----------------|
| 1 | User Zone | S-1 | High | 8.2 | User | An attacker impersonates a legitimate user by replaying stolen session tokens or forging identity credentials |
| 2 | Application Zone | AG-1 | High | 7.8 | LLM Agent Orchestrator | Prompt injection causes the Orchestrator to autonomously execute unauthorized high-impact actions |
| 3 | Application Zone | E-2 | High | 7.8 | LLM Agent Orchestrator | The Orchestrator has privileged access to KB, MCP Tool Server, and delegation authority — self-authorization via prompt injection |
| 4 | Application Zone | E-1 | High | 7.7 | Guardrails Service | Prompt injection that bypasses the Guardrails Service elevates attacker privilege to trusted caller |
| 5 | Application Zone | I-2 | High | 7.2 | LLM Agent Orchestrator | The Orchestrator's context window contains sensitive data exposed via inference side-channels |

**Note on AG-8**: Finding AG-8 (Inter-Agent Communication Channel, raw Critical, residual High, score not ranked in top-5 post-control) is the sole new finding this wave. It targets the A2A communication fabric. Because it is new and architecturally significant, designers should consider adding a 6th callout for AG-8 anchored to the Inter-Agent Communication Channel node in the Application Zone, marked [NEW].

**Gemini rewrite directive** (applied at image render time, not in spec):
- S-1: "An attacker could steal login credentials and impersonate real users without detection."
- AG-1: "A malicious prompt could hijack the AI system to take harmful unauthorized actions."
- E-2: "The central AI coordinator could grant itself forbidden permissions if tricked by a bad prompt."
- E-1: "An attacker who bypasses the safety filters gains the same trust level as a legitimate internal caller."
- I-2: "Sensitive patient data in the AI's working memory could leak to an outside observer."

---

## 4. Severity Distribution

| Metric | Value |
|--------|-------|
| Critical count (residual) | 0 |
| High count (residual) | 8 |
| Total qualifying (Critical + High) | 8 |
| Total after layer dedup | 5 |

(Medium and Low findings are not displayed in this template per executive-architecture specification.)

---

## 5. Visual Layout Directives

| Directive | Value |
|-----------|-------|
| Orientation | Portrait (8.5:11 page aspect ratio) |
| Layer ordering | Untrusted at TOP (User Zone → External Services → Application Zone top-to-bottom) |
| Layer fill pastels | Layer 0 (#F0F4FF cool blue), Layer 1 (#FFF4F0 warm peach), Layer 2 (#F0FFF4 cool green) |
| Component nodes | Rounded-rectangle per component, layer-coded fill, severity-colored border |
| Callout borders | High severity = orange #EA580C, dashed 2pt, warning triangle icon |
| Leader lines | 1pt solid neutral stroke anchoring each callout box to its component node |
| Empty-layer treatment | Compact badge (pill, max 15% page height) for layers with 0 Critical/High findings |
| Typography | Title bold 28-32pt; layer labels semi-bold 18-22pt; node labels 12-14pt; callout text 12-14pt sans-serif (IBM Plex Sans / DM Sans / Manrope) |
| Inter-layer arrows | Top-to-bottom directional arrows with explicit arrowheads between adjacent layers |
| Callout non-overlap | Callout boxes in page margins or inter-layer whitespace; no overlap with nodes or other callouts |

**Node border colors**:
- User: orange #EA580C (S-1 High)
- External API: gray #6B7280 (no qualifying findings)
- LLM Agent Orchestrator: orange #EA580C (AG-1, E-2, I-2 — High)
- Guardrails Service: orange #EA580C (E-1 — High)
- Inter-Agent Communication Channel: orange #EA580C (AG-8 [NEW] — High residual; consider [NEW] badge)
- All other Application Zone components: gray #6B7280

**Delta emphasis for AG-8 [NEW]**: If a 6th callout is added for AG-8, it should anchor to Inter-Agent Communication Channel with a callout reading approximately: "No encryption or authentication between AI agents — a compromised process could intercept and hijack agent commands." (25 words, plain English, per FR-212-3).

### Flow Edges (for inter-component arrows in diagram)

Key flows (from flow_edges payload, subset for portrait orientation):

- User → Guardrails Service (Prompt / Query, HTTPS)
- Guardrails Service → LLM Agent Orchestrator (Validated Prompt, Internal)
- LLM Agent Orchestrator → Inter-Agent Communication Channel (Delegation Message, Internal)
- Inter-Agent Communication Channel → Specialist Agent (Delegated Task, Internal)
- Specialist Agent → Inter-Agent Communication Channel (Specialist Result, Internal)
- Inter-Agent Communication Channel → LLM Agent Orchestrator (Aggregated Result, Internal)
- LLM Agent Orchestrator → MCP Tool Server (Tool Call Request, JSON-RPC)
- MCP Tool Server → External API (API Request, HTTPS)
- External API → MCP Tool Server (API Response, HTTPS)
- LLM Agent Orchestrator → Clinical Advisory Sub-Agent (Clinical Query / Context, JSON-RPC)
- Clinical Advisory Sub-Agent → LLM Agent Orchestrator (Clinical Summary + Recommendations, JSON-RPC)

### Clusters (trust zone dashed sub-group boundaries)

| Cluster Name | Trust Level | Members |
|-------------|------------|---------|
| Application Zone | trusted | Audit Logger, Clinical Advisory Sub-Agent, Guardrails Service, Inter-Agent Communication Channel, Knowledge Base, LLM Agent Orchestrator, Long-Running Learning Loop, MCP Tool Server, Specialist Agent |
| External Services | semi-trusted | External API |
| User Zone | untrusted | User |

---

## 6. Gemini Prompt Construction Notes

The Gemini prompt for this template uses the **verbatim-locked block** from `.claude/skills/tachi-infographics/references/executive-architecture.md` (FR-212-6). Only the `<<...>>` slots are substituted at runtime:

**Slot values**:

- `<<project_name>>`: `Agentic AI Application`

- `<<layer_block>>`:
```
Layer 0 — User Zone (untrusted, position 0):
  Component nodes: User [border: orange — High finding S-1]

Layer 1 — External Services (semi-trusted, position 1):
  Component nodes: External API [border: gray — no qualifying findings]

Layer 2 — Application Zone (trusted, position 2):
  Component nodes: LLM Agent Orchestrator [border: orange — High AG-1/E-2/I-2], Guardrails Service [border: orange — High E-1], Inter-Agent Communication Channel [border: orange — High AG-8 NEW], MCP Tool Server [border: gray], Clinical Advisory Sub-Agent [border: gray], Specialist Agent [border: gray]
  Overflow badge: "+ 3 more in this layer" (Knowledge Base, Long-Running Learning Loop, Audit Logger)
```

- `<<callout_block>>`:
```
Callout 1 — User Zone, anchored to: User
  Finding: S-1 | Severity: High
  Plain-English (≤25 words): An attacker could steal login credentials and impersonate real users without detection.

Callout 2 — Application Zone, anchored to: LLM Agent Orchestrator
  Finding: AG-1 | Severity: High
  Plain-English (≤25 words): A malicious prompt could hijack the AI system to take harmful unauthorized actions.

Callout 3 — Application Zone, anchored to: LLM Agent Orchestrator
  Finding: E-2 | Severity: High
  Plain-English (≤25 words): The central AI coordinator could grant itself forbidden permissions if tricked by a bad prompt.

Callout 4 — Application Zone, anchored to: Guardrails Service
  Finding: E-1 | Severity: High
  Plain-English (≤25 words): An attacker who bypasses the safety filters gains the same trust level as a legitimate internal caller.

Callout 5 — Application Zone, anchored to: LLM Agent Orchestrator
  Finding: I-2 | Severity: High
  Plain-English (≤25 words): Sensitive patient data in the AI working memory could leak to an outside observer.
```

- `<<empty_layer_block>>`:
```
External Services layer: 0 High/Critical findings in this layer
```

- `<<single_zone_caption>>`: (not emitted — 3 layers present, no single-zone edge case)

- `<<flow_edges_block>>`:
```
Audit Logger → Long-Running Learning Loop [data: Training Signal Stream via Internal]
Clinical Advisory Sub-Agent → Audit Logger [data: Clinical Decision Log Entry via Internal]
Clinical Advisory Sub-Agent → Knowledge Base [data: Context Retrieval (Vector Search) via Internal]
Clinical Advisory Sub-Agent → LLM Agent Orchestrator [data: Clinical Summary + Recommendations via JSON-RPC]
External API → MCP Tool Server [data: API Response via HTTPS]
Guardrails Service → Audit Logger [data: Filtering Event Log via Internal]
Guardrails Service → LLM Agent Orchestrator [data: Validated Prompt via Internal]
Guardrails Service → User [data: Rejected Prompt + Reason via HTTPS]
Inter-Agent Communication Channel → LLM Agent Orchestrator [data: Aggregated Result via Internal]
Inter-Agent Communication Channel → Specialist Agent [data: Delegated Task via Internal]
Knowledge Base → Clinical Advisory Sub-Agent [data: Retrieved Documents via Internal]
Knowledge Base → LLM Agent Orchestrator [data: Retrieved Documents via Internal]
LLM Agent Orchestrator → Audit Logger [data: Decision Log Entry via Internal]
LLM Agent Orchestrator → Clinical Advisory Sub-Agent [data: Clinical Query / Context via JSON-RPC]
LLM Agent Orchestrator → Inter-Agent Communication Channel [data: Delegation Message via Internal]
LLM Agent Orchestrator → Knowledge Base [data: Context Retrieval (Vector Search) via Internal]
LLM Agent Orchestrator → MCP Tool Server [data: Tool Call Request via JSON-RPC]
LLM Agent Orchestrator → User [data: Response via HTTPS]
Long-Running Learning Loop → Clinical Advisory Sub-Agent [data: Periodic Model Update via Internal]
Long-Running Learning Loop → LLM Agent Orchestrator [data: Periodic Model Update via Internal]
Long-Running Learning Loop → Specialist Agent [data: Periodic Model Update via Internal]
MCP Tool Server → Audit Logger [data: Tool Execution Log via Internal]
MCP Tool Server → External API [data: API Request via HTTPS]
MCP Tool Server → LLM Agent Orchestrator [data: Tool Result via JSON-RPC]
MCP Tool Server → Specialist Agent [data: Tool Result via JSON-RPC]
Specialist Agent → Audit Logger [data: Decision Log Entry via Internal]
Specialist Agent → Inter-Agent Communication Channel [data: Specialist Result via Internal]
Specialist Agent → MCP Tool Server [data: Tool Call Request via JSON-RPC]
User → Guardrails Service [data: Prompt / Query via HTTPS]
```

- `<<clusters_block>>`:
```
Application Zone (trusted): Audit Logger, Clinical Advisory Sub-Agent, Guardrails Service, Inter-Agent Communication Channel, Knowledge Base, LLM Agent Orchestrator, Long-Running Learning Loop, MCP Tool Server, Specialist Agent
External Services (semi-trusted): External API
User Zone (untrusted): User
```

**Image generation**: Invoke Gemini API using the verbatim-locked prompt block with slots substituted as above. Target aspect ratio: portrait (8.5:11). On success, save as `threat-executive-architecture.jpg` or `.png` per returned MIME type.
