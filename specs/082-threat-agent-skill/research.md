# Research Summary: Threat Agent Skill References (PRD 082)

**Feature**: 082 — Threat Agent Skill References
**Date**: 2026-04-11
**Author**: product-manager + parallel research agents
**PRD**: [docs/product/02_PRD/082-threat-agent-skill-references-2026-04-11.md](../../docs/product/02_PRD/082-threat-agent-skill-references-2026-04-11.md)

This research grounds the spec in concrete codebase measurements, architecture precedent, and primary-source availability for enrichment. Three parallel research streams ran: codebase inventory, architecture context, and web research on enrichment sources.

---

## 1. Codebase Current State (verified)

### 1.1 Threat agent files — line counts and structure

All 11 threat agents have `model: sonnet` set in frontmatter. Zero have `**MANDATORY**: Read` directives or skill references today.

| Agent | Category | Lines | Frontmatter `model:` | Skill Refs? | Inline OWASP 3×3 at |
|-------|----------|-------|---------------------|-------------|----------------------|
| [spoofing.md](.claude/agents/tachi/spoofing.md) | STRIDE | 113 | sonnet | ❌ | lines 92-98 |
| [tampering.md](.claude/agents/tachi/tampering.md) | STRIDE | 126 | sonnet | ❌ | lines 101-109 |
| [repudiation.md](.claude/agents/tachi/repudiation.md) | STRIDE | 124 | sonnet | ❌ | lines 100-108 |
| [info-disclosure.md](.claude/agents/tachi/info-disclosure.md) | STRIDE | 128 | sonnet | ❌ | lines 103-111 |
| [denial-of-service.md](.claude/agents/tachi/denial-of-service.md) | STRIDE | 141 | sonnet | ❌ | lines 117-125 |
| [privilege-escalation.md](.claude/agents/tachi/privilege-escalation.md) | STRIDE | 136 | sonnet | ❌ | lines 109-117 |
| [prompt-injection.md](.claude/agents/tachi/prompt-injection.md) | AI | 167 | sonnet | ❌ | lines 151-159 |
| [data-poisoning.md](.claude/agents/tachi/data-poisoning.md) | AI | 171 | sonnet | ❌ | lines 153-161 |
| [model-theft.md](.claude/agents/tachi/model-theft.md) | AI | 188 | sonnet | ❌ | lines 170-178 |
| [tool-abuse.md](.claude/agents/tachi/tool-abuse.md) | AI | 185 | sonnet | ❌ | lines 167-175 |
| [agent-autonomy.md](.claude/agents/tachi/agent-autonomy.md) | AI | 201 | sonnet | ❌ | lines 181-189 |
| **Total** | — | **1,680** | — | **0/11** | — |

**Representative STRIDE structure** (from spoofing.md, verified by Explore agent):
- Frontmatter (lines 1-9)
- Metadata YAML block (lines 11-26: category, threat_class, dfd_targets, owasp_references, output_schema)
- Purpose (lines 28-32)
- Detection Scope / Pattern Indicators (lines 34-71)
- Finding Template + OWASP 3×3 matrix (lines 73-98)
- References list (lines 100-113)

### 1.2 Control-analyzer reference pattern (model)

[control-analyzer.md](.claude/agents/tachi/control-analyzer.md) — **427 lines** (PRD cited 423; minor correction)

| Section | Line Range |
|---------|-----------|
| Frontmatter (`model: sonnet`) | 1-10 |
| Preamble / role | 12-22 |
| **`## Skill References` table** | 24-42 |
| Input Boundary | 46-78 |
| Baseline-Aware Analysis | 82-117 |
| Pipeline Overview (6 phases) | 120-138 |
| Phase 1-6 workflow sections | 141-342 |
| **`**MANDATORY**: Read` directive — Phase 3** | line 263 → control-categories.md |
| **`**MANDATORY**: Read` directive — Phase 4** | line 305 → evidence-criteria.md |
| **`**MANDATORY**: Read` directive — Phase 5** | line 325 → residual-risk.md |

**Pattern semantics** (confirmed by codebase read): control-analyzer has **3 distinct `MANDATORY: Read` directives at phase boundaries** (phases 3, 4, 5). Each phase gates its own skill read. This is the **methodology / phase-gated variant** of the lean pattern.

### 1.3 `tachi-control-analysis` skill directory

`.claude/skills/tachi-control-analysis/references/` — **3 reference files, 537 lines total**:
- control-categories.md
- evidence-criteria.md
- residual-risk.md

### 1.4 Existing `tachi-shared` reference state (critical audit data)

`.claude/skills/tachi-shared/references/` — 4 files, 646 lines:

| File | Lines | Frontmatter `consumers:` | **ACTUAL consumers (verified)** |
|------|-------|------------------------|---------------------------------|
| severity-bands-shared.md | 110 | 6 infra agents | 6 infra agents ✅ (matches reality) |
| **stride-categories-shared.md** | 146 | **orchestrator + 11 threat agents** | **orchestrator only (aspirational — 11 threat agents listed but none Read it)** |
| **finding-format-shared.md** | 177 | **11 threat agents + orchestrator + risk-scorer** | **orchestrator + risk-scorer only (same aspirational gap)** |
| maestro-layers-shared.md | 213 | 4 infra agents | 4 infra agents ✅ |

**Architect's concern validated**: two shared reference files already list threat agents as consumers in their frontmatter but zero threat agents actually Read them today. PRD 082's refactor is the work that finally makes the frontmatter match reality.

**Content orientation of finding-format-shared.md**: Explore agent confirmed it is written as a **consumption spec** (orchestrator / risk-scorer validating already-constructed findings) rather than a **production spec** (threat agents constructing findings). When 11 threat agents start Reading this file as their finding template, they will need additive producer-oriented content — see spec decision below.

### 1.5 Existing `tachi-*` skill directory inventory

| Skill Directory | Ref Files | Total Lines | Primary Consumer |
|-----------------|-----------|-------------|------------------|
| `tachi-control-analysis` | 3 | 537 | control-analyzer |
| `tachi-infographics` | 5 | 877 | threat-infographic |
| `tachi-orchestration` | 9 | 2,241 | orchestrator |
| `tachi-report-assembly` | 3 | 664 | report-assembler |
| `tachi-risk-scoring` | 6 | 916 | risk-scorer |
| `tachi-shared` | 4 | 646 | All agents (cross-cutting) |
| `tachi-threat-reporting` | 3 | 517 | threat-report |
| **TOTAL** | **33** | **6,398** | 7 skill directories |

### 1.6 Cross-agent duplicated content (consolidation candidates)

- **OWASP 3×3 risk matrix**: 11 identical copies, ~10 lines each = **~110 lines duplicated**
- **Risk level computation narrative**: 11 near-identical copies, ~4-6 lines each = **~55 lines duplicated**
- **Finding schema field guidance** (STRIDE agents): 6 near-identical copies, ~5-15 lines each = **~60 lines duplicated**
- **Estimated total consolidation target**: ~225-250 lines (~14-16% of 1,680 total agent volume)

### 1.7 Example architectures (regression surface)

6 canonical examples verified:
- [examples/web-app/threats.md](examples/web-app/threats.md) — 265 lines
- [examples/microservices/threats.md](examples/microservices/threats.md) — 324 lines
- [examples/ascii-web-api/threats.md](examples/ascii-web-api/threats.md) — 219 lines
- [examples/mermaid-agentic-app/threats.md](examples/mermaid-agentic-app/threats.md) — 198 lines
- [examples/free-text-microservice/threats.md](examples/free-text-microservice/threats.md) — 229 lines
- [examples/agentic-app/threats.md](examples/agentic-app/threats.md) — 294 lines

Plus 2 test/sample artifacts under `agentic-app/sample-report/` and `agentic-app/test-output/` — ignore these for regression.

### 1.8 ADR locations (confirmed)

- **ADR-021** (byte-determinism): [docs/architecture/02_ADRs/ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md](docs/architecture/02_ADRs/ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md)
- **ADR-022** (mmdc fail-loud, first CLI prereq ADR): [docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md](docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md)
- **ADR-020** (MAESTRO keyword classification): referenced; exists in same directory.
- **ADR-023**: does not exist yet — **PRD 082 creates it** (see spec FR).

---

## 2. Architecture Context

### 2.1 Lean + skill references pattern precedent

Feature 078 established tier-specific line caps:
- **Leaf agents ≤200 lines** (threat agents land in this tier)
- **Report agents ≤300 lines**
- **Methodology agents ≤500 lines**

PRD 082's tier targets (STRIDE ≤120, AI ≤150, hard ceiling 180) are **tighter than the leaf-agent cap** and ratified by architect review (Section 3, lines 75-108 of `.aod/results/architect.md`).

### 2.2 Prototype-first gate (Feature 078 T014 precedent)

`specs/078-agent-context-optimization/tasks.md` T014-T016 established the gate pattern:
- **T014**: Run full pipeline; compare outputs against baseline. Accepted criteria: finding count per category ±2, severity ±1, SARIF count ±2, correlation group count ±1.
- **T015**: Verify line count via `wc -l`.
- **T016**: Verify every extracted line exists in skill reference files (zero orphaned content).
- **Result on Feature 078**: "Finding counts PASS (±1 per category). Severity ±1 FAIL due to intentional improvement" — **clamping bug was found AND an intentional behavioral improvement was accepted**. Gate was real, not theater.
- **KB entry**: PAT-018 from Feature 078 delivery notes: "Prototype-first gates work — added ~2 hours but prevented an estimated 4-6 hours of rework at scale."

### 2.3 Determinism constraint (ADR-021)

Threat agent skill references must contain **static, deterministic patterns** (keyword tables, dispatch rules). No LLM-generated content. Any shared reference edit that flows through to report pipeline will diff the 5 byte-deterministic PDFs at the byte level even if content is equivalent — **R6 in PRD is the mitigation**, re-baseline is expected.

### 2.4 Finding schema (v1.3) — unaffected

`schemas/finding.yaml` v1.3 has no threat-agent-specific fields. The refactor touches **agent internals**, not the agent→orchestrator output contract. Schema stays at 1.3.

### 2.5 Constitution principles that apply

- **Principle VIII (Observability)**: if a skill reference file is missing/malformed, agent must produce clear error (no silent fallback) — consistent with ADR-022 fail-loud posture
- **Principle III (Backward Compat)**: finding output format stays identical; orchestrator dispatch rules unchanged
- **Principle X (Product-Spec Alignment)**: triple sign-off required on all artifacts

### 2.6 Shared reference content orientation (architect flag)

Architect concern: `finding-format-shared.md` is written as a **consumer enforcement spec** (orchestrator validating findings) rather than a **producer construction spec** (threat agents building findings). When 11 threat agents start Reading this file as their finding template, they need **additive producer-oriented content**. The spec must decide:
- **Option A**: Add a `## For Threat Agents (Producers)` section to the existing file (additive, preferred).
- **Option B**: Split the file into `finding-format-consumer.md` + `finding-format-producer.md` (invasive, rejected by default — breaks stable consumer contract).

**Spec decision**: Option A — append producer-oriented section during Phase 2c shared-reference consolidation wave.

---

## 3. Primary Source Availability for Enrichment

### 3.1 Source matrix (verified by web-researcher)

| Source | License | Coverage | Fit for PRD 082 |
|---|---|---|---|
| **OWASP Top 10 (2021)** | CC BY 3.0 | 10 web risks; maps to all 6 STRIDE | Strong baseline |
| **OWASP AI Exchange** | **CC0 1.0** (zero attribution) | Full AI threat taxonomy | Excellent — best for AI agents |
| **OWASP LLM Top 10 (v2025)** | CC BY-SA 4.0 | LLM01-LLM10; direct maps to 5 AI agents | Excellent — canonical LLM reference |
| **NIST AI 600-1** (Jul 2024) | US Federal public domain | 12 GAI risk categories (governance, not detection) | Moderate — use for framing, not detection signatures |
| **MITRE ATT&CK** (v15/v16) | Free w/ attribution | 14 enterprise tactics | Strong — industrial-grade STRIDE taxonomy |
| **MITRE ATLAS** (v5.1, Nov 2025) | Free w/ MITRE attribution | 16 tactics, 84 techniques; **14 new agent-specific techniques added Oct 2025** (AML.T0058-T0062) | Excellent — authoritative AI adversarial source |
| **CWE Top 25 (2024)** | Royalty-free | 25 weaknesses by rank; strong STRIDE cross-walk | Strong |

### 3.2 Per-agent enrichment candidates (≥2 per agent target; ≥22 aggregate)

**STRIDE agents — candidate new categories**:
- **spoofing**: (1) OAuth/OIDC token replay + audience-confusion (OWASP A07, CWE-287/306); (2) cloud-IAM role assumption chain abuse (ATT&CK T1078.004 Valid Accounts: Cloud Accounts)
- **tampering**: (1) deserialization gadget chains (CWE-502, OWASP A08); (2) software supply-chain integrity failures (ATT&CK T1195, SLSA levels)
- **repudiation**: (1) logging/monitoring gaps (OWASP A09, unlogged privileged actions); (2) ATT&CK T1070 Indicator Removal (log deletion, timestomping)
- **info-disclosure**: (1) SSRF to cloud metadata endpoints (CWE-918, OWASP A10, IMDSv1 vs v2); (2) sensitive info via error messages (CWE-200, CWE Top 25 rank 17)
- **denial-of-service**: (1) uncontrolled resource consumption (CWE-400, new in 2024 Top 25; algorithmic complexity/ReDoS); (2) ATT&CK T1498/T1499 network and endpoint DoS
- **privilege-escalation**: (1) improper privilege management (CWE-269) + missing authorization on critical functions (CWE-862, CWE-306); (2) ATT&CK T1548 Abuse Elevation Control Mechanism

**AI agents — canonical pattern categories**:
- **prompt-injection** (OWASP LLM01, ATLAS AML.T0051): direct injection/jailbreaks, indirect injection (poisoned RAG/webpage/PDF), evasion encoding (Base64/unicode/multimodal)
- **data-poisoning** (OWASP LLM04, ATLAS AML.T0020): training-data poisoning (backdoor triggers, label flipping), RAG/vector-DB poisoning (OWASP LLM08), supply-chain model poisoning (LLM03 — HuggingFace typosquatting)
- **model-theft** (OWASP LLM02 + LLM10, ATLAS Exfiltration AML.TA0013): extraction via inference API, parameter/weight exfiltration, system-prompt leakage (OWASP LLM07)
- **tool-abuse** (OWASP LLM06 Excessive Agency, **ATLAS AML.T0061 AI Agent Tools**, **AML.T0062 Exfiltration via AI Agent Tool Invocation**): over-granted permission scope, tool-invocation injection, cross-tool data exfiltration
- **agent-autonomy** (OWASP LLM06, **ATLAS AML.T0058 Agent Context Poisoning**, **AML.T0059 Activation Triggers**): excessive autonomy w/o human-in-the-loop, context poisoning (multi-turn memory corruption), goal drift / unbounded consumption (LLM10)

### 3.3 Feasibility verdict

**Enrichment floor (≥22 new categories with primary source citations) is comfortably achievable.** OWASP LLM Top 10 + OWASP AI Exchange + MITRE ATLAS collectively provide 3+ citable categories per AI agent (15+ new). OWASP Top 10 + CWE Top 25 + MITRE ATT&CK provide 3+ per STRIDE agent (18+ new). **Total ceiling ~33+ new categories**, well above the 22 target. Zero licensing friction.

---

## 4. Recommendations for Spec

### 4.1 Must include in spec

1. **Sibling variant framing** (architect concern #1): Explicitly declare that detection agents are structurally different from methodology agents. Load-point semantics: **single `**MANDATORY**: Read` directive at invocation start**, not phase-gated. Section name **`## Detection Workflow`** (not `## Phase Workflow`).
2. **Tier-specific line targets** enforced: STRIDE ≤120 (stretch ≤90), AI ≤150 (stretch ≤130), hard ceiling 180.
3. **ADR-023 task**: Create `docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md` documenting the detection-variant with four decisions: (a) single-point load, (b) MAESTRO stays orchestrator-side, (c) shared refs additive-only, (d) producer-vs-consumer orientation for shared refs.
4. **Phase 1a/1b sub-phasing**: Refactor-only regression → enrichment addition → combined Phase 1 gate. Sub-phase revertable independently.
5. **Phase 2c serialization**: Shared reference consolidation is a single-writer wave (not parallelized with per-agent extraction).
6. **R6 in scope**: Re-baseline 5 byte-deterministic PDFs as expected Phase 3 outcome (NOT an incident).
7. **Per-agent commit discipline**: Each agent extraction is a separate commit so per-agent revert is possible in Phase 2.
8. **Aggregate enrichment floor**: `≥22 new categories aggregate` (NOT `≥2 per agent`). Per-agent enrichment is de-scopable.
9. **Q7 open question**: Where do AI agent example findings live post-refactor? Default: **in-agent for Phase 1 prototype**, revisit if file size exceeds tier target.
10. **Shared-reference audit task**: Before consolidating finding-format-shared.md, audit consumer-vs-producer orientation. Append `## For Threat Agents (Producers)` section (additive Option A).

### 4.2 Avoid

- **Adding MAESTRO references to any threat agent** — MAESTRO inheritance runs orchestrator-side (Phase 3 Table Assembly). Threat agents are MAESTRO-agnostic today; PRD must preserve that.
- **Modifying existing shared reference content** — edits must be additive-only (append new sections, never rewrite existing). Escalation path: if existing content must change, create a new file alongside.
- **Assuming the 6 example architectures exercise enriched patterns** — enrichment validation is **source-citation-based**, not example-triggered. M4 (finding count delta ≥0) is correct; do not overclaim "examples will gain findings from enriched patterns" (most won't).
- **Expanding scope to new threat categories** — no new STRIDE letters, no new AI category beyond the 11 agents.

### 4.3 Spec should NOT re-litigate

These are already resolved in the PRD or its review docs:
- Skill directory naming: `tachi-<agent-name>/` with no tier prefix (PRD Q3, architect concern 5, team-lead Minor 3)
- Q4 MAESTRO: closed — threat agents are MAESTRO-agnostic
- Q5 diff format: qualitative pre/post per Feature 078 precedent
- Model field: already set to `sonnet` on all 11 agents (verified) — no change needed

---

## 5. Open Risks to Call Out in Spec

- **Enrichment scope creep** (highest-risk bundling): refactor + enrichment bundled. Mitigation: Phase 1a/1b sub-phasing, per-agent de-scopability, aggregate floor instead of per-agent floor.
- **Shared-ref blast radius** (R3 in PRD): pre-commit to additive-only editing as a policy, not as a hope.
- **Content orientation gap** in finding-format-shared.md: architect flagged; spec must add a consumer-vs-producer audit task.
- **Single-writer serial constraint** on Phase 2c: team-lead flagged; spec must declare this constraint explicitly.

---

## 6. References

- **PRD**: [docs/product/02_PRD/082-threat-agent-skill-references-2026-04-11.md](../../docs/product/02_PRD/082-threat-agent-skill-references-2026-04-11.md)
- **Architect review**: [.aod/results/architect.md](../../.aod/results/architect.md) (11 concerns, 3 medium, 8 low)
- **Team-lead review**: [.aod/results/team-lead.md](../../.aod/results/team-lead.md) (8 non-blocking concerns, realistic 32h estimate)
- **Feature 078 precedent**: `specs/078-agent-context-optimization/tasks.md` T014-T016 (prototype gate + validation)
- **Feature 136 precedent**: re-baselined 5 PDFs after `maestro-layers-shared.md` edit (ADR-021 determinism model)
- **Control-analyzer pattern**: [.claude/agents/tachi/control-analyzer.md](../../.claude/agents/tachi/control-analyzer.md) (methodology / phase-gated variant)
