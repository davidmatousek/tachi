# Research Summary: Feature 145 — Canonical MAESTRO Worked Example

**Feature**: 145 | **Date**: 2026-04-16 | **PRD**: [145-maestro-canonical-worked-example-2026-04-16.md](../../docs/product/02_PRD/145-maestro-canonical-worked-example-2026-04-16.md)

---

## Examples Directory Conventions

### Directory Structure (Wave 0 Option X vs Option Y)

| Example | Input file | Pipeline outputs | `sample-report/`? |
|---------|-----------|------------------|-------------------|
| `web-app/` | `architecture.md` | `threats.md` + `security-report.pdf.baseline` (minimal) | No |
| `microservices/` | `architecture.md` | `threats.md` + `security-report.pdf.baseline` (minimal) | No |
| `ascii-web-api/` | `input.md` | `threats.md` + `security-report.pdf.baseline` (minimal) | No |
| `mermaid-agentic-app/` | `input.md` | `threats.md` + `threat-report.md` + `attack-trees/` + baseline | No |
| `free-text-microservice/` | `input.md` | `threats.md` + `security-report.pdf.baseline` (minimal) | No |
| `agentic-app/` | `architecture.md` | Top-level `threats.md` + baseline; **full artifact set** (11 .md files + 4 JPGs + SARIF + 27 attack trees + PDF) under `sample-report/` subdirectory | **Yes (only example)** |

**Key finding**: 5 of 6 examples use **flat structure**. Only `agentic-app` uses `sample-report/` subdirectory, and only for its richer artifact set. There is no uniform convention for the richer set — `agentic-app`'s subdirectory layout is a historical artifact, not a repository-wide convention.

**Decision (to confirm in plan.md Wave 0)**: **Option Y (flat)** — matches the 5-of-6 convention; establishes canonical structure for future rich-artifact examples. The PRD (FR-1) recommends Option Y; team-lead review L4 confirmed; 5-of-6 flat precedent supports.

### examples/README.md Structure

Location: `examples/README.md` (106 lines). Contains:
- **Standardized Examples table** (3 rows: web-app, agentic-app, microservices) — columns: Example | Architecture | Components | Key Demonstration
- **Framework Relationship Hierarchy** (Mermaid + mapping)
- **Usage Instructions** (Browse, Sample Report, Compare, Templates)
- **Format-Specific Test Fixtures** table (3 rows: ascii-web-api, free-text-microservice, mermaid-agentic-app)

**Action**: Add new row to Standardized Examples table for `maestro-reference` with Key Demonstration text like "Canonical MAESTRO walkthrough — all 7 layers, cross-layer chains, agentic patterns". Add prominent first-read callout near the top. No existing rows deleted.

### Regression Fixture List

Location: `tests/scripts/test_backward_compatibility.py:40-45`:

```python
BASELINE_EXAMPLES = [
    "web-app",
    "microservices",
    "ascii-web-api",
    "mermaid-agentic-app",
    "free-text-microservice",
]
```

`agentic-app` explicitly excluded (line 28-33: "regeneration target, not expected to match pre-existing baseline"). The suite runs under `SOURCE_DATE_EPOCH="1700000000"` per ADR-021.

**Action**: Add `"maestro-reference"` to `BASELINE_EXAMPLES` (6th baseline; Regime A per PRD FR-7). **Gated on mmdc CI availability** (see External Dependencies below).

### Mermaid Convention

From `examples/mermaid-agentic-app/input.md` (52 lines) and `examples/agentic-app/architecture.md` (81 lines, 10 components):

- `flowchart TD` (top-down)
- Subgraphs for trust/security zones (User Zone / Application Zone / External Services)
- Processes: `Name[Label]`; data stores: `Name[(Label)]`
- Edge labels: `A -->|"Description (Protocol)"| B`
- Component Summary table below the diagram: Component | DFD Element Type | Notes/AI Dispatch Trigger

**For Feature 145**: Adopt same format. With 14+ components across 7 MAESTRO layers, consider nested subgraphs grouping components by layer (User Zone / Ecosystem L7 / Agent Framework L3 / Foundation L1 / Data L2 / Infrastructure L4 / Observability L5 / Security L6) to make the MAESTRO stack visually explicit.

---

## MAESTRO Detection Patterns (FR-4 Pre-Execution Checklist)

### Layer Classification Keywords

`.claude/skills/tachi-shared/references/maestro-layers-shared.md` — case-insensitive substring match, first match wins, evaluated in L1→L7 order:

| Layer | Canonical Name | Trigger keywords (sample) |
|-------|----------------|---------------------------|
| L1 | Foundation Models | LLM, language model, GPT, Claude, Gemini, foundation model, base model, fine-tuned model, model weights, inference engine |
| L2 | Data Operations | vector, RAG, embedding, training data, data pipeline, knowledge base, vector DB, fine-tuning, corpus, index, database, cache |
| L3 | Agent Frameworks | orchestrator, planner, executor, tool dispatch, agent framework, tool server, MCP server, function calling, chain, workflow engine |
| L4 | Deployment and Infrastructure | container, runtime, API gateway, load balancer, reverse proxy, CDN, DNS, ingress, kubernetes, docker, serverless, network, queue, registry |
| L5 | Evaluation and Observability | audit log, monitoring, SIEM, anomaly detection, telemetry, log, metrics, tracing, forensics, alerting, observability |
| L6 | Security and Compliance | auth, WAF, firewall, secrets manager, guardrail, content filter, rate limit, encryption, RBAC, IAM, access control, security |
| L7 | Agent Ecosystem | multi-agent, agent-to-agent, swarm, delegation, coordination, supervisor, sub-agent, agent registry, agent mesh, chat UI, dashboard, admin console, web interface, frontend, user portal, API endpoint, REST API, GraphQL, client, user |

**L5-before-L6 ordering is load-bearing**: "audit log" must hit L5 before L6 to prevent detective controls from being misclassified as preventive.

### Multi-Agent Gate Predicate (`maestro-agentic-patterns-shared.md` §4)

TRUE if ANY of:
- **(a)** ≥2 components classified as `agentic` or `llm` dispatch category (sufficient alone)
- **(b)** ≥1 data flow where both source AND target are `agentic`/`llm`
- **(c)** Architecture description contains (case-insensitive) any of: `multi-agent`, `swarm`, `supervisor`, `delegation`, `agent mesh`

### Dispatch Category Triggers

`.claude/skills/tachi-orchestration/references/dispatch-rules.md`:
- **LLM**: `LLM`, `model`, `GPT`, `Claude` → dispatches prompt-injection, data-poisoning, model-theft
- **AG (Agentic)**: `agent`, `autonomous`, `orchestrator`, `MCP server`, `tool server`, `plugin` → dispatches agent-autonomy, tool-abuse
- **Dual-dispatch**: Components whose name/description matches both → all 5 AI agents + 6 STRIDE

### Agentic Pattern Rules (R-01 through R-06, priority order)

| Rule | Pattern | Priority | Preconditions | Generates net-new? |
|------|---------|----------|---------------|--------------------|
| R-01 | Agent Collusion | 10 | `agentic`/`llm` + `inter_agent_data_flow` + description contains `coordinate` / `joint` / `collude` / `cross-agent` / `inter-agent` / `shared channel` / `shared memory` | **Yes** |
| R-02 | Temporal Attack | 20 | `persistent_state` topology (fine-tuning pipeline, persistent agent memory, long-running learning loop) + temporal keywords (`sleeper`, `gradual`, `drift`, `dormant`, `re-training`) | **Yes** |
| R-03 | Emergent Behavior | 30 | `agentic`/`llm` + `multi_agent` + description contains `cascade` / `unpredictable` / `interaction` / `emergent` | **Yes** |
| R-04 | Trust Exploitation | 40 | `spoofing` or `agentic` + `multi_agent` | No (annotation only) |
| R-05 | Communication Vulnerability | 50 | `agentic` or `info-disclosure` + component matches `inter_agent_channel` regex + `inter_agent_channel` topology | No |
| R-06 | Resource Competition | 60 | `denial-of-service` or `agentic` + `multi_agent` + description contains `resource` / `monopol` / `competition` / `quota` / `starve` / `contention` / `lock` | No |

### Pre-Execution Architecture Checklist (FR-4)

Before first pipeline invocation, verify by static review of architecture.md:

1. **Multi-agent gate predicate TRUE** — ≥2 `agentic`/`llm` components AND (inter-agent data flow OR multi-agent keywords present)
2. **R-01 satisfied** — Explicit inter-agent data flow between two agentic components in Mermaid
3. **R-02 satisfied** — At least one persistent-state component (fine-tuning pipeline, agent memory store, long-running learning loop) with temporal keywords in description
4. **R-03 satisfied** — Multi-agent topology AND emergent-behavior keywords (`cascade`, `unpredictable`, `emergent`, `interaction`) in at least one agentic component's description

All 4 green → architecture is pre-qualified to surface ≥3 agentic patterns (Collusion + Temporal + Emergent) without a reactive iteration loop.

---

## CSA Canonical MAESTRO Walkthrough (Reference Target)

**Canonical example**: Multi-agent financial trading system (Snyk Labs is the authoritative Tier-1 walkthrough — CSA blog introduces MAESTRO conceptually; Practical DevSecOps gives layer purposes only).

**Layer-by-layer population**:

| Layer | Trading-system components |
|-------|---------------------------|
| L1 Foundation Models | Market prediction models (adversarial-example vulnerable) |
| L2 Data Operations | Historical market data in vector DBs, RAG retrieval |
| L3 Agent Frameworks | Workflow orchestration, inter-agent comms, decision logic |
| L4 Deployment Infrastructure | Container runtime, service comm channels |
| L5 Evaluation & Observability | Audit trails, behavioral monitoring |
| L6 Security & Compliance | Compliance rule enforcement, access controls |
| L7 Agent Ecosystem | Inter-agent trust relationships, comm protocols |

**Cross-layer attack narrative**: "Execution Hijack" — adversarial examples corrupt L1 → poisoned data corrupts L2 → prompt injection hijacks L3 → container escape manipulates L4 → log injection conceals L5 → policy manipulation blinds L6 → agent impersonation compromises L7. Framed as a phased campaign (Phase 1: Foundation, Months 1-3).

**Artifact shape**: (1) seven-layer architectural diagram, (2) layer-populated component table, (3) single cross-layer attack narrative with sequenced kill-chain, (4) per-layer threat-category mapping. tachi's Feature 141 (cross-layer chains) + Feature 142 (agentic patterns) output maps directly onto this shape.

**Non-financial requirement**: Feature 145 FR-2 explicitly mandates a non-financial domain to avoid appearing derivative.

---

## Candidate Domain Analysis

### Option A — Healthcare Clinical Decision Support (PRD Recommended)

**Composed reference architecture** (from arxiv 2504.03699, arxiv 2506.13800, AWS Bedrock AgentCore):

| MAESTRO Layer | CDSS components |
|---------------|-----------------|
| L1 Foundation Models | Clinical LLM (diagnostic reasoning), risk stratification model, medical imaging classifier |
| L2 Data Operations | FHIR resource store (Conditions/MedicationRequest/Observations), clinical guideline RAG corpus, medical literature vector DB, patient cohort synthetic database |
| L3 Agent Frameworks | Diagnostic Agent, Treatment Planner Agent, Risk Stratification Agent, Supervisor/Coordinator Orchestrator, Validation Agent, Clinical Tool Server (MCP → FHIR) |
| L4 Deployment and Infrastructure | Model inference gateway, container runtime, EHR ingestion queue, API gateway |
| L5 Evaluation and Observability | Clinical audit log, outcomes tracking dashboard, physician override registry, inter-agent call tracing |
| L6 Security and Compliance | HIPAA RBAC, encryption service (AES-256/TLS 1.3), consent manager, compliance audit, de-identification guardrail |
| L7 Agent Ecosystem | Physician portal (clinician UI), patient summary generator, inter-agent communication channel, agent registry, supervisor→specialist delegation protocol |

**Strengths**: ≥2 components per layer natural; all 3 agentic-pattern preconditions (R-01 inter-agent flow via supervisor↔specialists; R-02 persistent state via outcomes tracking / physician override registry; R-03 emergent behavior in cascading diagnostic recommendations); cross-layer chain is natural (e.g., L2 guideline corpus poisoning → L3 Treatment Planner hijack → L5 audit log tampering → L6 policy bypass → L7 false clinical recommendation to physician); dramatic attack narrative; regulatory surface (HIPAA) makes L6 sharp.

**Risks**: Content-review burden (must be plausible but clearly fictional); architect review M2 flagged this — DoD requires security-analyst review of README disclaimer if Option A chosen.

### Option B — Autonomous Research Assistant

Literature scanner, claim extractor, citation validator, synthesis agent, research director. L2 academic corpus. L5 citation provenance. L6 license/source authorization.

**Strengths**: Lower content-review overhead; L2 data poisoning very canonical.
**Weaknesses**: L6 compliance less sharp; niche feel.

### Option C — Supply-Chain Optimization

Demand forecaster, inventory balancer, logistics router, risk assessor, supply-chain orchestrator. L2 ERP + supplier vectors. L5 decision audit. L6 vendor compliance.

**Strengths**: Clear business domain; multi-agent natural.
**Weaknesses**: Thematic overlap with existing `microservices` example; less dramatic attacks.

**Recommendation (to confirm in plan.md Wave 0)**: **Option A (Healthcare)** — richest layer coverage, strongest R-01/R-02/R-03 precondition coverage, most dramatic cross-layer chain, mapping to the canonical CSA shape is cleanest. Architect concern M2 addressed via security-analyst DoD gate on README disclaimer. Fallback ranking A → B → C per PRD.

---

## Feature 120 Architecture Frontmatter (FR-8 Path B)

Feature 120 introduces architecture version tracking via YAML frontmatter:

```yaml
---
version: "1.0"
date: "2026-04-YY"
description: "Canonical MAESTRO reference architecture — multi-agent healthcare clinical decision support system"
checksum: "sha256:..."
previous_version: null
---
```

**Path B (PRD FR-8)**: Hand-author architecture body during Wave 1 + iterate in Wave 3 **without committing frontmatter**. Once pipeline outputs meet FR-4 gates, invoke `/tachi.architecture` in "create" mode — it computes SHA-256 over body via `shasum -a 256`, injects frontmatter, commits v1.0. No intermediate frontmatter commits.

No `.archive/v0/` entry on initial commit (the legacy-file archival logic fires only when updating an existing frontmatter-less architecture via `/tachi.architecture`, not when creating a new one).

---

## External Dependencies (mmdc CI Availability)

**Hard prerequisite (ADR-022 / Feature 130)**: `@mermaid-js/mermaid-cli` (mmdc) is required when attack trees are present. Feature 145 will produce 14+ components with multi-agent topology → Critical/High findings guaranteed → attack trees guaranteed → mmdc invoked.

**CI check required**:
- Local dev: `npm install -g @mermaid-js/mermaid-cli`
- CI workflow running `tests/scripts/test_backward_compatibility.py` — separate from `.github/workflows/tachi-mmdc-preflight.yml` (which asserts **absence**). Must verify mmdc is provisioned in the backward-compat CI workflow before FR-7 integration lands.

**Fallback**: If CI does not have mmdc, FR-7 (regression fixture integration) is deferred to a follow-up PR per Risk 145.3 contingency — the canonical example still ships as adopter-facing artifact; baseline added to `BASELINE_EXAMPLES` once CI is updated.

---

## Recommendations for spec.md

1. **Carry forward all 8 PRD functional requirements** (FR-1 through FR-8). They are written at user-story level, testable, and map to PRD sections exactly.
2. **Carry forward all 6 PRD user stories** (US-1 through US-6) with priorities preserved.
3. **Lock operational decisions** that PRD defers to `/aod.plan` Wave 0 as `[NEEDS CLARIFICATION]` entries on spec.md, limited to the 3 highest-impact:
   - Domain: A / B / C (PRD recommends A)
   - Directory structure: X / Y (PRD recommends Y)
   - mmdc CI availability (conditional on FR-7)
4. **Scope boundaries**: This is content-authoring only. No code changes, no schema changes, no agent changes. Reinforce this in Assumptions section.
5. **Key entities section**: The feature's primary entities are the **example directory**, the **architecture.md**, the **README.md**, and the **pipeline output artifacts** — not new data models.
6. **Edge cases**: architecture iteration exceeding cap; domain change mid-implementation; mmdc CI gap; subtle byte-diff on baseline regeneration.
7. **Success criteria**: Use PRD Success Criteria as the canonical list; express them technology-agnostic.

---

## Pre-Resolved Operational Decisions Preserved from PRD

These were pre-resolved at PRD level and carry into spec/plan without re-litigation:

- **Architecture iteration fallback ranking** (team-lead M3): (a) keyword-tune → (b) extend architecture → (c) relax FR-3 to 6/7 layers
- **Pre-execution architecture checklist** (architect M4): 4 conditions static-reviewed before first pipeline invocation
- **Wave 0 timebox** (team-lead L1): ≤2h, EOD Day 1 hard stop, escalate to user on no-consensus
- **README parallelism** (team-lead M2/L2): Sections 1/2/5/6/7 drafted in parallel with architecture iteration; Sections 3/4 gated on pipeline output freeze
- **Feature 120 workflow path** (architect M5): Path B — checksum injected after architecture is frozen
- **Structural DoD discipline** (team-lead L4): No mixed structure — pipeline output lands in chosen Option X/Y location

---

## Appendix: FR-005 Pre-Execution Architecture Review Checklist Verification (Wave 1 T011-T014)

**Date**: 2026-04-16
**Artifact under review**: `examples/maestro-reference/architecture.md` (body frozen, no frontmatter yet — Path B per FR-012)
**Reference tables**: `.claude/skills/tachi-shared/references/maestro-layers-shared.md` + `.claude/skills/tachi-shared/references/maestro-agentic-patterns-shared.md`

### Condition 1 — Multi-agent gate predicate TRUE (T011)

The Phase 3.6 multi-agent gate predicate evaluates true when at least one of three OR conditions (a, b, c) holds. All three conditions hold for this architecture.

- **Condition (a) — ≥2 agentic/llm components**: Supervisor Orchestrator (LLM+AG dual-dispatch), Diagnostic Agent (LLM+AG dual-dispatch), Treatment Planner Agent (LLM+AG dual-dispatch). Count = 3. **TRUE**.
- **Condition (b) — inter-agent data flow (both endpoints agentic/llm)**: Supervisor ↔ Inter-Agent Communication Channel ↔ Diagnostic Agent + Supervisor ↔ Inter-Agent Communication Channel ↔ Treatment Planner Agent. Both endpoints of each leg are agentic/llm. **TRUE**.
- **Condition (c) — multi-agent keyword match on architecture description**: architecture.md header comment contains `multi-agent`, `supervisor`, `delegation` (all three listed in the authoritative keyword list). **TRUE**.

**Result**: Predicate TRUE via all three independent conditions. ✅

### Condition 2 — R-01 Agent Collusion precondition (T012)

R-01 requires: `category_in [agentic, llm]` AND `architecture_has: topology: [inter_agent_data_flow]` AND `description_contains` at least one of the collusion-indicative tokens.

- **category_in**: ≥3 findings expected on agentic/llm components (Supervisor, Diagnostic, Treatment Planner).
- **inter_agent_data_flow**: satisfied (see Condition 1 condition (b) above). ✅
- **description_contains** (finding-level): Supervisor Orchestrator description carries `coordinate`, `delegation`, `cross-agent`, `inter-agent`; edge labels on Supervisor ↔ Channel and Channel ↔ Agent data flows carry `cross-agent coordinate`, `inter-agent coordinate`, `joint reasoning`. Finding descriptions emitted by detection agents targeting these components are expected to inherit this phrasing. ✅

Note on architect APPROVED_WITH_CONCERNS concern (T012 `delegation`): `delegation` is not in the canonical R-01 `description_contains` list in `maestro-agentic-patterns-shared.md` Section 3 — the inclusion here is additive and harmless (R-01 uses OR disjunction on its description_contains list; the presence of `coordinate` / `cross-agent` / `inter-agent` / `joint` / `shared channel` already satisfies the disjunction). The `delegation` token also independently satisfies the multi-agent gate predicate condition (c).

**Result**: Precondition met. ✅

### Condition 3 — R-02 Temporal Attack precondition (T013)

R-02 requires: `architecture_has: topology: [persistent_state]`. The `persistent_state` topology indicator is satisfied when at least one component matches any of three `persistent_state`-related component_type tokens: `fine_tuning_pipeline`, `persistent_agent_memory`, or `long_running_learning_loop`.

- **Outcomes Telemetry and Physician Override Audit Store** description carries `learning loop`, `feedback loop`, `continual learning`, `re-training`, `drift` keywords.
- Per `maestro-agentic-patterns-shared.md` Section 4 Component Type Token List, `long_running_learning_loop` matches on "learning loop", "feedback loop", "continual learning". All three present in this component's description.
- Therefore `long_running_learning_loop` token matches → `persistent_state` topology evaluates TRUE. ✅

Note on architect APPROVED_WITH_CONCERNS concern (T013): the canonical R-02 rule requires only the `persistent_state` topology — no `description_contains` on the finding itself. The architecture-level description keywords drive topology evaluation (and satisfy R-02), not finding-level description constraints. The `description_contains` entries here describe the architecture component's description rather than the finding description; this is a conservative posture and does not alter the rule evaluation.

**Result**: Precondition met. R-02 `generates_finding_when_no_match: true` — net-new AGP finding expected if no existing finding carries `temporal_attack`. ✅

### Condition 4 — R-03 Emergent Behavior precondition (T014)

R-03 requires: `category_in [agentic, llm]` AND `architecture_has: topology: [multi_agent]` AND `description_contains` at least one of [`cascade`, `unpredictable`, `interaction`, `emergent`].

- **category_in**: ≥3 findings expected on agentic/llm components (Supervisor, Diagnostic, Treatment Planner).
- **multi_agent topology**: satisfied (see Condition 1 condition (a) — ≥2 agentic/llm components). ✅
- **description_contains**: Supervisor Orchestrator description carries `cascade`, `emergent`, `interaction` (verbatim: "cascading delegation across specialist agents with emergent coordination patterns" + "cross-agent interaction"). Architecture header comment also carries `cascading delegation`, `emergent coordination patterns`. ✅

Note on architect APPROVED_WITH_CONCERNS concern (T014 `feedback loop`): `feedback loop` is not in the canonical R-03 `description_contains` list — it appears in Outcomes Telemetry's description for R-02 `long_running_learning_loop` token matching (Section 4), not R-03 classification. R-03 matches on `cascade` / `emergent` / `interaction` via Supervisor Orchestrator's description. No ambiguity.

**Result**: Precondition met. ✅

### Summary

| Condition | Task | Status | Evidence |
|-----------|------|--------|----------|
| 1. Multi-agent gate predicate TRUE | T011 | ✅ TRUE | 3 agentic/llm + inter-agent flows + keyword match (all three OR conditions TRUE) |
| 2. R-01 Agent Collusion precondition | T012 | ✅ Met | inter_agent_data_flow + collusion tokens present |
| 3. R-02 Temporal Attack precondition | T013 | ✅ Met | long_running_learning_loop via Outcomes Telemetry keywords |
| 4. R-03 Emergent Behavior precondition | T014 | ✅ Met | multi_agent topology + cascade/emergent/interaction tokens |

**Wave 1 Gate status**: All 4 FR-005 conditions green by static review. Architecture body is frozen-ready for Wave 2 pipeline invocation. No frontmatter committed (Path B per FR-012; frontmatter injection deferred to Wave 6).

**Keyword-hygiene items C1/C2/C3 (architect review) status**:
- **C1** (L4/L5 collision on "registry"): Component renamed from "Outcomes Tracking & Physician Override Registry" to "Outcomes Telemetry and Physician Override Audit Store". Name no longer contains `registry` (L4 keyword). Name contains `telemetry` (L5 keyword). First-match-wins lands component at L5. ✅
- **C2** (L3 classification on bare "Agent"): Diagnostic Agent description contains L3 phrase keywords `executor` and `tool dispatch` (also `coordinates`). Landing at L3 confirmed. ✅
- **C3** (L1 classification on bare "Model"): Risk Stratification Model description contains L1 phrases `fine-tuned model`, `foundation model`, `language model`, `inference engine`. Landing at L1 confirmed. ✅

All Wave 1 acceptance criteria met.

---

## Appendix B: Wave C (Wave 2) Output Quality Gate Verification (T020-T023)

**Verified**: 2026-04-17 post-pipeline
**Artifacts inspected**: `examples/maestro-reference/threats.md`, `examples/maestro-reference/threat-report.md`, `examples/maestro-reference/attack-chains.md`

### T020 — FR-007 MAESTRO Layer Coverage (≥6 of 7, 7/7 preferred)

**Result**: ✅ **PASS — 7 of 7 layers surfaced**

Evidence: `examples/maestro-reference/threats.md` Section 6 "Risk by MAESTRO Layer" table shows:

| MAESTRO Layer | Finding Count | Highest Severity |
|---------------|---------------|------------------|
| L1 — Foundation Model | 18 | Critical |
| L2 — Data Operations | 9 | Critical |
| L3 — Agent Framework | 30 | Critical |
| L4 — Deployment Infrastructure | 11 | High |
| L5 — Evaluation and Observability | 6 | Critical |
| L6 — Security and Compliance | 12 | High |
| L7 — Agent Ecosystem | 22 | Critical |

All 7 MAESTRO layers have ≥1 finding. FR-004 (7/7) also satisfied — no need for FR-004 relaxation to 6/7.

### T021 — FR-008(b) Cross-Layer Chain Surfacing (≥1 chain spanning ≥3 layers)

**Result**: ✅ **PASS — 3 chains surfaced; max span 5 layers**

Evidence: `examples/maestro-reference/attack-chains.md` Section 1 Chain Summary:

| Chain ID | Title | Layers | Max Severity | Finding Count |
|----------|-------|--------|--------------|---------------|
| CHAIN-001 | RAG Corpus Poisoning to False Clinical Recommendation via Agent Hijack | L2 → L3 → L5 → L6 → L7 | Critical | 5 |
| CHAIN-002 | Prompt Injection to Orchestrator Privilege Escalation via Foundation Model | L7 → L1 → L3 → L6 | Critical | 4 |
| CHAIN-003 | Outcomes Telemetry Tampering to Model Drift via Learning Loop | L5 → L1 → L3 → L7 | Critical | 4 |

CHAIN-001 spans 5 MAESTRO layers — exceeds the FR-008(b) ≥3 requirement. Chain member findings trace architectural component lineage (RAG Corpus → Diagnostic Agent → Clinical Audit Log → HIPAA RBAC → Physician Clinical Portal) per the chain shape designed in Wave 1 Cross-Layer Attack Chain Shape section.

Cross-reference: `examples/maestro-reference/threat-report.md` Section 6 "Cross-Layer Attack Chains" contains narrative for all 3 chains with chain-breaking control target identification (T-15 for CHAIN-001, LLM-1 for CHAIN-002, T-16 for CHAIN-003).

### T022 — FR-008(c) Agentic Pattern Surfacing (≥3 of 6 canonical patterns populated)

**Result**: ✅ **PASS — 6 of 6 patterns populated in threats.md; 5 of 6 narrated in threat-report.md**

Evidence: `examples/maestro-reference/threats.md` Section 4b "Findings by Agentic Pattern":

| Pattern | Count | Findings |
|---------|-------|----------|
| trust_exploitation | 5 | S-5, S-6, S-7, S-8, E-3 |
| agent_collusion | 4 | AG-1, AG-2, AGP-01, AGP-03 |
| communication_vulnerability | 3 | T-3, I-3, AG-8 |
| temporal_attack | 2 | T-16, AGP-02 |
| resource_competition | 2 | D-3, D-4 |
| emergent_behavior | 1 | AGP-03 |

All 6 canonical CSA MAESTRO agentic patterns populated. 3 net-new AGP findings generated by Phase 3.6 synthesis: AGP-01 (agent_collusion on Inter-Agent Communication Channel, Critical), AGP-02 (temporal_attack on Outcomes Telemetry), AGP-03 (emergent_behavior + agent_collusion on Supervisor Orchestrator — `multiple` classification).

`examples/maestro-reference/threat-report.md` Section 7 "Agentic Pattern Analysis" narrates 5 of 6 patterns (Agent Collusion, Emergent Behavior, Temporal Attacks, Trust Exploitation, Resource Competition). Communication Vulnerability pattern is covered via per-finding narratives in Section 3.4 (T-3, I-3, AG-8) but not called out with a dedicated subsection header. Still ≥3 of 6 per FR-008(c) — **gate satisfied**. Minor observation flagged for potential T035 PM review: consider adding explicit Communication Vulnerability subsection in future iterations.

### T023 — FR-008(a) MAESTRO Findings Section Populated (per-layer content)

**Result**: ✅ **PASS — per-layer content populated across threat-report.md**

Evidence: MAESTRO layer content is distributed rather than isolated to a single section in threat-report.md (this matches tachi's existing threat-report format for all examples):

- `threat-report.md` Section 2 "Architecture Overview" enumerates all 7 MAESTRO layers with component placement (lines 71-82)
- `threat-report.md` Section 3 "Threat Analysis" (per-category) tags every finding with its MAESTRO layer (42 distinct layer citations across findings, all 7 layers represented)
- `threats.md` Section 6 "Risk by MAESTRO Layer" provides the quantitative per-layer breakdown (see T020 above)
- `threats.md` Section 7 "Recommended Actions" includes the new Pattern column (Feature 142) alongside existing Category/Component/Risk Level

Feature 091's dedicated MAESTRO Findings section is rendered in the PDF via the `templates/tachi/security-report/maestro-findings.typ` Typst page — this is a PDF-side rendering and will be validated in T019 security-report output.

FR-008(a) "MAESTRO Findings section populated" is satisfied by the layer-tagged content density in the markdown artifacts (threats.md + threat-report.md combined) per the existing tachi schema where per-layer metadata is a finding-level attribute rather than a dedicated markdown section structure.

### Wave C Gate Summary

| Gate | Task | Status | Evidence |
|------|------|--------|----------|
| FR-007 MAESTRO layer coverage ≥6/7 | T020 | ✅ PASS (7/7) | threats.md Section 6 |
| FR-008(b) cross-layer chain ≥3 layers | T021 | ✅ PASS (5 layers max) | attack-chains.md Section 1, threat-report.md Section 6 |
| FR-008(c) agentic patterns ≥3/6 | T022 | ✅ PASS (6/6 in threats.md; 5/6 narrated) | threats.md Section 4b, threat-report.md Section 7 |
| FR-008(a) MAESTRO findings populated | T023 | ✅ PASS (per-layer content distributed) | threat-report.md Sections 2+3, threats.md Section 6 |

**All 4 Wave C gates PASS on first pipeline run. Wave D (conditional iteration) is SKIPPED.** Proceeding directly to Wave C remaining tasks (T018/T019) and Wave E (T033-T034 + T035/T036 review).
