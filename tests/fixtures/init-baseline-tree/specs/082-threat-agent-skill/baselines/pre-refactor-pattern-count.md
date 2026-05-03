# Feature 082 — Pre-Refactor Detection Pattern Category Count

**Capture date**: 2026-04-11
**Branch**: `082-threat-agent-skill`
**Method**: Manual audit of inline pattern categories in each of the 11 threat agent files

A "category" is a labeled group of patterns (bolded heading under `### Patterns and Indicators` for STRIDE agents, or a top-level numbered item under `### Detection Patterns` for AI agents), **not** an individual line item. Sub-vectors nested under a parent category (e.g., `tool-abuse.md` category 5 "Tool Poisoning" has three sub-bullets 5a/5b/5c) are counted as **one** category because they share a common parent heading and enrichment would extend the parent category, not the nested sub-vectors.

Section header conventions differ by tier:
- **STRIDE agents** use `## Detection Scope` → `### Targeted DFD Element Types` → `### Patterns and Indicators` with bolded category headers
- **AI agents** use `## Detection Scope` → `### Trigger Keywords` → `### Applicable DFD Element Types` → `### Detection Patterns` with numbered list items

---

## STRIDE Agents

| Agent | Category Count | Category Names (abbreviated) |
|-------|----------------|-------------------------------|
| `spoofing.md` | 5 | Authentication Bypass; Credential Theft and Replay; Session Hijacking; Service Impersonation; Federated Identity Attacks |
| `tampering.md` | 6 | Input Injection; Data Flow Manipulation; Persistent Data Corruption; Code and Configuration Tampering; API Parameter Manipulation; Cross-Site Request Forgery |
| `repudiation.md` | 6 | Missing Audit Trails; Insufficient Log Detail; Log Tampering Vulnerability; Deniable Actions; Timestamp Manipulation; Log Injection and Evasion |
| `info-disclosure.md` | 6 | Error Message Exposure; Excessive Data in Responses; Data at Rest Exposure; Data in Transit Exposure; Side-Channel Information Leakage; Debug and Diagnostic Exposure |
| `denial-of-service.md` | 8 | Resource Exhaustion; Algorithmic Complexity Attacks; Database and Storage Saturation; Connection and Pool Exhaustion; Dependency and Cascade Failures; Application-Layer Attacks; Infrastructure-Layer Attacks; Flooding and Abuse |
| `privilege-escalation.md` | 7 | Broken Access Control; Insecure Direct Object References (IDOR); Role and Permission Escalation; Path Traversal and Scope Bypass; Multi-Tenancy Boundary Violations; Lateral Movement; Privilege Persistence |
| **STRIDE subtotal** | **38** | — |

## AI Agents

| Agent | Category Count | Category Names (abbreviated) |
|-------|----------------|-------------------------------|
| `prompt-injection.md` | 5 | Direct Prompt Injection; Indirect Prompt Injection; Jailbreaking; System Prompt Extraction; Cross-Plugin Injection |
| `data-poisoning.md` | 5 | Training Data Manipulation; RAG Index Poisoning; Knowledge Base Corruption; Fine-Tuning Supply Chain Attacks; Context Window Contamination |
| `model-theft.md` | 7 | Direct Weight Exfiltration; API-Based Model Extraction; Model Artifact Exposure; Side-Channel Model Reconstruction; Fine-Tuned Model Theft; Unbounded Inference Consumption; Model Supply Chain Compromise |
| `tool-abuse.md` | 5 | Unauthorized Tool Invocation; Capability Escalation via Tool Composition; Tool Parameter Injection; Tool Chain Manipulation; Tool Poisoning (parent category with 3 sub-vectors: 5a Direct Poisoning, 5b Tool Shadowing, 5c Rug Pull / Tool Redefinition) |
| `agent-autonomy.md` | 6 | Excessive Autonomy; Goal Misalignment; Unconstrained Action Scope; Missing Human-in-the-Loop; Cascading Failures in Multi-Agent Systems; Autonomous Resource Consumption |
| **AI subtotal** | **28** | — |

---

## Aggregate

| Tier | Agents | Total Categories |
|------|--------|------------------|
| STRIDE | 6 | 38 |
| AI | 5 | 28 |
| **Total** | **11** | **66** |

**Audit notes**:
- All 6 STRIDE agents share an identical section structure: `## Detection Scope` → `### Targeted DFD Element Types` → `### Patterns and Indicators` with bolded category headers. No STRIDE agent deviates from this convention.
- All 5 AI agents share a different but equally consistent structure: `## Detection Scope` → `### Trigger Keywords` → `### Applicable DFD Element Types` → `### Detection Patterns` with numbered list items. No AI agent uses the STRIDE bolded-header convention and no AI agent deviates from the numbered list convention.
- `tool-abuse.md` category 5 "Tool Poisoning" contains three sub-vectors labeled 5a/5b/5c — counted as **one** category here because enrichment would logically extend the parent (e.g., adding a new 5d sub-vector). If a downstream counter chooses to treat the sub-vectors as independent categories, `tool-abuse.md` would count as 7 and the aggregate would be 68. This note documents the ambiguity so the enrichment floor can be measured consistently.
- No agent file had an absent or divergent detection-pattern section. Every file follows its tier convention — the 66 aggregate is stable across all reasonable counting conventions (with the tool-abuse tool-poisoning case noted above).
- Nothing unexpected: section structure is remarkably uniform within each tier, which is exactly the property that makes the sibling-variant extraction viable (FR-10, plan.md §1.1).

This aggregate establishes the pre-refactor pattern-category baseline. Feature 082 enrichment floor is ≥22 NEW aggregate categories (SC-006), so post-refactor total must be ≥ (baseline + 22) = **≥88 aggregate categories** across all 11 companion skill reference directories.
</content>
</invoke>