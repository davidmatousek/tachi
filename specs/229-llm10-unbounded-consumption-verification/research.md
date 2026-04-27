# Research Summary: F-5 LLM10 Unbounded Consumption Verification

**Feature**: 229 / F-5 — Heuristic A enrichment of `denial-of-service` + `model-theft` agents for OWASP LLM10:2025 coverage at two-agent scope
**Date**: 2026-04-27
**Phase**: 0 (preceding spec.md)
**Status**: Complete — PRD-time architect questions Q1/Q3/Q4/Q5 RESOLVED inline; Q2 architect-tractable at plan time
**PRD**: [docs/product/02_PRD/229-llm10-unbounded-consumption-verification-2026-04-27.md](../../docs/product/02_PRD/229-llm10-unbounded-consumption-verification-2026-04-27.md)

## Knowledge Base Findings

The institutional-knowledge index carries **one** prior entry on Heuristic A enrichment shape — F-3 (Feature 219, ASI07 tool-abuse enrichment, delivered 2026-04-26). F-3 was the **first execution** of the enrichment branch at single-agent scope. F-5 is the **second execution** and the **first at two-agent scope** — establishing the two-execution-deep validation gate that F-2 retrospective KB-037 codified for new-agent shape and that now extends to enrichment shape.

Prior BLP-01 KB entries cover the **new-agent** branch of Heuristic A:

- F-1 (Feature 201) `output-integrity` agent — established the lean-agent shape conformance for ADR-023 detection-variant agents.
- F-2 (Feature 206) `misinformation` agent — established the **second-execution-deep** validation of the new-agent shape; documented the regex-alternation minor-bump rule (ADR-030 Decision 8).
- F-4 (Feature 224) `human-trust-exploitation` agent — third new-agent execution + ASI09 sub-scope carve-up against existing `agent-autonomy` agent (ADR-033 Decision 2 Outcome B).

**Key F-3 lesson F-5 inherits**: pattern catalogs MUST cite only catalog-resolvable taxonomy IDs in references. F-5 verified at PRD time that LLM10, CWE-400, CWE-770, LLM03 are all catalog-resolvable. T1496 (Resource Hijacking) is **NOT** catalog-resolvable — it is named in `mitigation` narrative text only, not in `references` as a structured citation.

**Zero-MAESTRO-reference invariant (ADR-023 Decision 2)**: F-5 grep-verified at PRD time on all four target files — `denial-of-service.md`, `model-theft.md`, and both companion `detection-patterns.md` files carry **0** MAESTRO references. Additive edits MUST preserve this invariant.

## Codebase Analysis

### Existing target files (PRD-time + plan-time baselines, plan-time re-verified 2026-04-27)

| File | Lines | State | F-5 Edit Posture |
|------|-------|-------|------------------|
| `.claude/agents/tachi/denial-of-service.md` | 53 | 9 OWASP refs, `## Purpose` paragraph, Detection Workflow Step 5 | Additive — append `OWASP LLM10:2025` (10th entry), extend `## Purpose` 1–3 lines, extend Step 5 references |
| `.claude/agents/tachi/model-theft.md` | 95 | `owasp_references: [OWASP LLM10:2025, OWASP LLM03:2025]` (LLM10 ALREADY PRESENT), `## Purpose` paragraph | Additive — `owasp_references` audit confirms zero net change; extend `## Purpose` 1–3 lines |
| `.claude/skills/tachi-denial-of-service/references/detection-patterns.md` | 179 | Hybrid heading (8 thematic sections covering Cat 1–8 + named `## Pattern Category 9/10/11` + Primary Sources) | Additive — append Cat 12 + Cat 13 after Cat 11; extend Primary Sources |
| `.claude/skills/tachi-model-theft/references/detection-patterns.md` | 154 | 9 named `## Pattern Category` headings (1–9) + Overview + Targeted DFD + Trigger Keywords + Primary Sources | Additive — append Cat 10 + Cat 11 after Cat 9; extend Primary Sources |
| `.claude/skills/tachi-shared/references/finding-format-shared.md` | n/a | `denial-of-service` at line 12, `model-theft` at line 16 | **NO EDIT** — both already present |
| `schemas/finding.yaml` | n/a | `schema_version: "1.8"`; `id.pattern: ^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\d+$` (12 alternation values post-F-4) | **NO EDIT** — `D` and `LLM` already enumerated; no schema bump |

**Asymmetry F-5 highlights**:
- `denial-of-service.md` `owasp_references` requires a one-line append (LLM10 absent). `model-theft.md` `owasp_references` is **zero net change** (LLM10 already present per `[OWASP LLM10:2025, OWASP LLM03:2025]`). The audit confirms metadata completeness rather than extending it on `model-theft`.
- The two companions have **different heading structures**. `denial-of-service` companion uses a hybrid (8 thematic groupings for Cat 1–8 + 3 named `## Pattern Category` headings for Cat 9/10/11) and lacks a `## Trigger Keywords` section. `model-theft` companion uses uniform `## Pattern Category N:` headings throughout (Cat 1–9) and includes a `## Trigger Keywords` section at line 19. Byte-identity invariants apply to each companion's existing structure, not a shared template.

### F-5-specific structural advantages over F-1 / F-2 / F-4 (matching F-3)

| Dimension | F-1 / F-2 / F-4 (new-agent branch) | F-3 (enrichment, single-agent) | F-5 (enrichment, two-agent) |
|-----------|-----------------------------------|--------------------------------|------------------------------|
| New agent file | YES | NO | **NO** |
| New skill directory | YES | NO | **NO** |
| Schema version bump | YES (one regex-alternation value each) | NO (stays 1.7) | **NO** (stays 1.8) |
| New ID prefix | YES (OI, MI, TE) | NO (reuses AG) | **NO** (reuses D + LLM) |
| `finding-format-shared.md` consumers edit | YES | NO | **NO** (both agents already present) |
| Orchestrator dispatch edits | YES (functional) | NO (cosmetic Q2 only) | **NO** (cosmetic Q2 only — default-NO) |
| Pattern categories added | 5 each | 2 (one host) | **4** (2 per host × 2 hosts) |
| Host files edited | n/a (created) | 2 (1 agent + 1 companion) | **4** (2 agents + 2 companions) |

**F-5 is structurally larger than F-3 (~2× pattern-authoring surface) but smaller than F-2 (no new agent shape).** The two-agent edit surface is the distinguishing F-5 dimension; everything else inherits F-3's enrichment-branch shape.

### Naming conventions to follow (mirror F-3 ADR-032 + Cat 9–11 in DoS companion + Cat 1–9 in model-theft companion)

- ADR file naming: `ADR-NNN-feature-slug.md`. PRD-time + plan-time verified: ADR-033 highest committed; ADR-034 next available.
- Pattern Category headers (denial-of-service companion): `## Pattern Category N: <Name>` (matches existing Cat 9/10/11).
- Pattern Category headers (model-theft companion): `## Pattern Category N: <Name>` (matches existing Cat 1–9).
- Indicator bullets: `-` prefix, indicators ≥4 per category (Cat 12/13 ≥4 + 1 worked example + named mitigations; Cat 10/11 ≥4 + 1 worked example + named mitigations).
- Worked example: prose paragraph + threat description + agent reasoning trace.
- Mitigations: bulleted list of named LLM-specific mechanisms (per-tenant rate limit, prompt-size cap, max-context-window enforcement, output-token cap, cost-per-query alerting, denial-of-wallet anomaly detection, automated tenant suspension on budget breach).

## Architecture Constraints

### Active ADRs F-5 inherits from

- **ADR-021** SOURCE_DATE_EPOCH determinism — byte-identity baseline harness on the **6 non-LLM-serving baselines** (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`); `agentic-app` is the F-5 mutation target without a `.baseline` file by design.
- **ADR-023** Threat Agent Skill References Pattern:
  - **Decision 1**: lean-agent shape (≤120 lines STRIDE tier for `denial-of-service`; ≤150 lines AI tier for `model-theft`).
  - **Decision 2**: zero MAESTRO references on agent files and companion catalogs.
  - **Decision 3**: additive-only edit discipline on shared references — Cat 1–11 (DoS) and Cat 1–9 (model-theft) byte-identical pre/post edit.
- **ADR-027** Taxonomy Crosswalk Schema — F-5 cites OWASP LLM10, LLM03, CWE-400, CWE-770 from F-A1 catalogs.
- **ADR-028** Source Attribution Schema Extension — **F-5 does NOT extend `source_attribution` populator wiring**. PRD-time grep confirms neither host agent currently emits `source_attribution`; the `D-{N}` and `LLM-{N}` populator wiring is deferred to F-A3 per `schemas/finding.yaml` lines 230–238 and ADR-028 Decision 6. F-5 cites LLM10 in the prose-level `references:` array (existing finding-YAML field since v1.0). F-A3 inheritance is **one-way** (F-5 → F-A3); F-5 does not block on F-A3.
- **ADR-030** Decision 1 — three-signal-class taxonomy in LLM tier; F-5 cross-references this as the precedent for signal-class consolidation logic, applied here at two-agent scope (DoS + model-theft) within the LLM10 surface.
- **ADR-031** Decision 8 — regex-alternation minor-bump rule. F-5 cross-references **as the asymmetry**: F-1 / F-2 / F-4 invoked the rule; F-3 and F-5 do NOT — Heuristic A consolidation reuses the existing host's ID space.
- **ADR-032** ASI07 Tool-Abuse Enrichment — **direct precedent** for F-5. ADR-032 lines 84 and 182 explicitly forecast that F-5 will not need a schema bump because the host agents' `D-{N}` and `LLM-{N}` prefixes already exist. ADR-034 cross-references ADR-032 as the first enrichment-branch execution at single-agent scope; F-5 is the second execution at two-agent scope.
- **ADR-033** Human-Trust-Exploitation Agent — **structural sibling** for ADR-034. ADR-033 demonstrated that a single OWASP entry can be carved across multiple host agents at the documentation layer (ASI09 = `agent-autonomy` autonomy axis + `human-trust-exploitation` communication axis). F-5 demonstrates that an OWASP entry can be **enriched** across multiple host agents at the pattern-catalog layer (LLM10 = `denial-of-service` infrastructure-DoS sub-class + `model-theft` extraction-DoW sub-class). Both are valid Heuristic A applications.

### Public-ADR governance constraint

ADR-034 omits commercial framing per Option C governance contract (SDR-001). All BLP-01 strategy cross-references live in private companion docs only. The public ADR stands on technical merits.

### Catalog state at PRD time + plan time (verified 2026-04-27)

| Taxonomy | ID | Catalog Path | Status |
|----------|-----|--------------|--------|
| OWASP | LLM10 (Unbounded Consumption) | `schemas/taxonomy/owasp.yaml:373` | Present |
| OWASP | LLM03 (Supply Chain) | `schemas/taxonomy/owasp.yaml` | Present (existing model-theft `owasp_references` adjacency) |
| CWE | CWE-400 (Uncontrolled Resource Consumption) | `schemas/taxonomy/cwe.yaml:130` | Present |
| CWE | CWE-770 (Allocation of Resources Without Limits or Throttling) | `schemas/taxonomy/cwe.yaml:182` | Present |
| MITRE ATT&CK | T1496 (Resource Hijacking) | `schemas/taxonomy/mitre-attack.yaml` | **ABSENT** — text-only mention in mitigation narrative; NOT cited in `references` |

All 4 OWASP/CWE citations are catalog-resolvable. T1496 is named in `mitigation` narrative prose on Cat 10/11 findings as a cross-reference but does NOT appear as a structured `references` entry.

### Dispatch + consumer registration state (PRD-time + plan-time grep-verified 2026-04-27)

| Surface | Current state | F-5 edit |
|---------|---------------|----------|
| `dispatch-rules.md` line 73 | `model-theft (OWASP LLM10:2025)` already annotated | NO EDIT (already cites LLM10) |
| `dispatch-rules.md` LLM agents inventory line 109 / 157 | `prompt-injection, data-poisoning, model-theft, output-integrity, misinformation` includes model-theft | NO EDIT |
| `dispatch-rules.md` denial-of-service entry | NOT explicitly annotated with LLM10 today | **Q2 architect-tractable** — cosmetic-only annotation extending DoS line with `(..., LLM10)` permitted but not required (default-NO) |
| `orchestrator.md` lines 37 / 42 / 298 / 372 | both agents inventoried in agents list, sequential mode walk, and dispatch table | NO EDIT |
| `finding-format-shared.md` lines 12 / 16 | `denial-of-service` at 12, `model-theft` at 16 | NO EDIT — both already present |

### Q1 SPLIT resolution (PRD-time architect-resolved)

Context-window exhaustion has **two attack vectors** with disjoint owning categories:

- **Vector A (latency-DoS lens)** — attacker drives context-window to model max, legitimate users see degraded p99 latency; attacker intent is **availability disruption**. Same signal class as Cat 12 inference-flooding (per-request resource exhaustion via latency tail). Owner: `denial-of-service` Cat 13.
- **Vector B (cost-DoW lens)** — attacker drives context-window to maximum to inflate per-call cost; the "wallet" is the bill, not the system uptime; attacker intent is **economic damage**. Same signal class as Cat 10 cost-amplification (extraction-driven resource abuse). Owner: `model-theft` Cat 11.

The same architecture surfaces Cat 13 (latency) AND Cat 11 (cost), neither finding is duplicate, ADR-034 Decision 3 audit table assigns each to exactly one owning category. F-5 is the **first BLP-01 sub-pattern with cross-agent vector decomposition**.

### Q3 severity discrimination (PRD-time architect-resolved per OWASP 3×3)

| Pattern Category | Default Severity | Critical Floor Conditional |
|------------------|------------------|----------------------------|
| Cat 12 (inference-request flooding / token-budget exhaustion) | MEDIUM-HIGH | n/a |
| Cat 13 (context-window-exhaustion latency-DoS) | MEDIUM-HIGH | n/a |
| Cat 10 (cost amplification) | HIGH | n/a |
| Cat 11 (denial-of-wallet) | HIGH | **CRITICAL floor** ONLY when (a) multi-tenant freemium structure structurally evident AND (b) both per-tenant token budget AND cost alerting absent |

Severity-hint annotation column embedded in ADR-034 Decision 3 audit table.

## Industry Research

### OWASP LLM10:2025 — Unbounded Consumption

The OWASP LLM Top 10:2025 entry covers attack surfaces introduced when LLM-serving infrastructure lacks controls for:
- Inference-request rate limiting (per-tenant queries-per-second)
- Prompt-size enforcement (max-prompt-token cap at request ingestion)
- Token-budget enforcement (per-request, per-tenant, per-time-window)
- Context-window enforcement (max-context-window cap, per-conversation truncation)
- Output-token capping (per-query response-length cap)
- Recursive-prompt depth limiting (chain-of-thought self-amplification protection)
- Cost-velocity monitoring (per-tenant cost-per-time-window with anomaly alerting)
- Automated tenant suspension on budget breach (no manual approval delay)

Five sub-pattern surfaces emerge:
1. **Inference-request flooding** — unbounded QPS on inference endpoints.
2. **Token-budget exhaustion** — unbounded prompt-size driving compute saturation.
3. **Context-window exhaustion** — adversarial prompt expansion (split into Vector A latency-DoS + Vector B cost-DoW per Q1).
4. **Cost amplification via recursive or cost-asymmetric prompting** — small input drives disproportionately large output.
5. **Denial-of-wallet** — multi-tenant economic attack class where the bill is the attack target, not uptime.

### Best practices F-5 codifies

- **Per-tenant queries-per-second rate limit** at the API gateway as the primary inference-flooding control.
- **Prompt-size cap (max-prompt-token enforcement)** at request ingestion, before model invocation.
- **Per-tenant token budget** with hard-cap enforcement — the dominant denial-of-wallet control.
- **Max-context-window enforcement** at the API gateway with automatic 413-response on overflow.
- **Per-conversation truncation policy** with sliding-window limit on appended message history.
- **Cost-per-query p99 alerting** tied to per-tenant billing attribution.
- **Denial-of-wallet anomaly detection** via cost-velocity monitoring (per-tenant cost-per-time-window with anomaly alerting on percentile-velocity spikes).
- **Automated tenant suspension on budget breach** (no manual approval delay) — encodes the response loop required to stop runaway spend.
- **Output-token cap** tuned to realistic response-length p99.
- **Recursive-prompt depth limit** at the inference-runtime layer.

### MITRE ATT&CK T1496 (Resource Hijacking)

Adjacent technique covering attacker-positioned resource consumption — relevant where the architecture exhibits cost-amplification or denial-of-wallet exposure. Named in `mitigation` narrative on Cat 10 + Cat 11 findings as a cross-reference. **NOT** catalog-resolvable in `schemas/taxonomy/mitre-attack.yaml` (PRD-time + plan-time verified absent), so it does NOT appear as a structured `references` entry.

### CWE-400 (Uncontrolled Resource Consumption) / CWE-770 (Allocation of Resources Without Limits or Throttling)

Primary CWE references for the LLM-tier inference-resource-exhaustion sub-patterns. Both already in `denial-of-service.md` `owasp_references` metadata. F-5 cites them in `references` arrays on Cat 12/13 findings. CWE-400 is the broader root cause; CWE-770 is the more specific allocation-without-throttling case applicable to per-tenant token-budget gaps.

## Recommendations for Spec

1. **Preserve PRD's three-user-story structure** (US-229-1, US-229-2, US-229-3) with P0 priority on all three — Full LLM10 surface coverage, LLM-specific mitigation naming, and audit-confirmed additive transition with mapping table are co-equal MVP signals per PRD.
2. **Translate PRD's 14 success criteria** to spec SCs with grep-checkable predicates — line counts (`wc -l`), byte-identity proofs (structural diff returning empty), catalog-resolvability gates (taxonomy-yaml grep), schema-invariant gates (empty diff on `schemas/finding.yaml`), 6-baseline byte-identity (SOURCE_DATE_EPOCH harness).
3. **Codify the LLM-serving topology gate**: Cat 12/13 (`denial-of-service`) and Cat 10/11 (`model-theft`) emit findings only when the architecture additionally exhibits LLM-serving indicators (declared inference endpoint, LLM API gateway, per-tenant API key, token-counting middleware, cost-attribution layer, multi-tenant LLM-serving topology). On non-LLM-serving topologies, the new categories emit zero findings.
4. **Codify the byte-identity invariants** — Cat 1–11 in DoS companion + Cat 1–9 in model-theft companion + existing `## Purpose` prose in both agents byte-identical pre/post edit; 6 non-LLM-serving baselines byte-identical PDFs under `SOURCE_DATE_EPOCH=1700000000`.
5. **Codify the lean-shape envelope** — `denial-of-service.md` ≤120 lines (PRD-time baseline 53; expected 56–60); `model-theft.md` ≤150 lines (PRD-time baseline 95; expected 98–102).
6. **Codify the prose-level `references:` array contract** — every Cat 12/13 finding's `references` array includes `OWASP LLM10:2025` + `CWE-400` (and where applicable `CWE-770`); every Cat 10/11 finding's `references` array includes `OWASP LLM10:2025` (and where applicable `OWASP LLM03:2025`). T1496 is named in `mitigation` prose only, not in `references`. **F-5 does NOT extend `source_attribution` populator wiring on the host agents** — that scope belongs to F-A3.
7. **Codify the canonical sub-pattern → owning-agent mapping table in ADR-034 Decision 3** as the audit deliverable — 5 rows with severity-hint annotation column per Q3.
8. **Document the Heuristic A enrichment-pattern at two-agent scope** as the second execution and the first cross-agent application — establishes precedent for future Tier 2 ML/Mobile bundles where multi-agent enrichment may apply.
9. **Defer Q2 (cosmetic dispatch annotation) to Assumptions** with documented PM/architect leaning (default-NO, architect-tractable at plan time). Avoid re-adjudicating what the PRD already resolved (Q1 SPLIT, Q3 severity, Q4 4-categories, Q5 example target).
10. **Avoid implementation-detail leakage** — the spec describes WHAT (testable predicates: line counts, byte-identity, catalog-resolvability, references-array contents) not HOW (specific edit positions, exact prose, ADR sectioning). Plan stage owns HOW.

## References

- F-3 spec (immediate enrichment-branch precedent): `specs/219-asi07-tool-abuse-enrichment/spec.md` — model spec shape on this; F-5 is the two-agent extension.
- F-4 spec (immediate Tier 1 precedent): `specs/224-trust-exploitation-threat-agent/spec.md` — model PRD-time-resolved-Q1/Q3 handling on this.
- F-2 spec: `specs/206-misinformation-threat-agent/spec.md` — model 14-SC translation pattern.
- F-1 spec: `specs/201-output-integrity-threat-agent/spec.md` — first BLP-01 detection feature spec.
- ADR-030 Decision 1 (signal-class taxonomy in LLM tier): `docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md`
- ADR-032 (first enrichment-branch execution; lines 84 + 182 forecast F-5 no-bump): `docs/architecture/02_ADRs/ADR-032-asi07-tool-abuse-enrichment.md`
- ADR-033 (sub-scope carve-up structural sibling): `docs/architecture/02_ADRs/ADR-033-human-trust-exploitation-agent.md`
- Existing `denial-of-service` agent: `.claude/agents/tachi/denial-of-service.md` (53 lines, plan-time verified)
- Existing `denial-of-service` companion: `.claude/skills/tachi-denial-of-service/references/detection-patterns.md` (179 lines, ends at Cat 11)
- Existing `model-theft` agent: `.claude/agents/tachi/model-theft.md` (95 lines, `owasp_references` already includes LLM10)
- Existing `model-theft` companion: `.claude/skills/tachi-model-theft/references/detection-patterns.md` (154 lines, ends at Cat 9)
- Schema: `schemas/finding.yaml` (v1.8, `D` and `LLM` prefixes already enumerated, no bump in F-5)
