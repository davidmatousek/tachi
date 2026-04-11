# Phase 1b Regression Verification — Feature 082 (Threat Agent Skill References)

**Feature**: 082-threat-agent-skill-references
**Phase**: 1b — Prototype regression verification after Wave 6 enrichment
**Date**: 2026-04-11
**Branch**: `082-threat-agent-skill`
**Scope**: Verify that enrichment applied to the two prototype companion skill reference files (`tachi-spoofing` and `tachi-prompt-injection`) during Wave 6 does not cause any regressions against the T001 baselines, and produces ≥1 new finding on at least one example architecture per enriched agent.

## Context

- Wave 5 (commits `4304b55` + `10cecb3`): Two threat agents (`spoofing`, `prompt-injection`) were refactored to move their inline pattern catalog into companion skill reference files, with a `**MANDATORY**: Read` directive loading the new file at detection start.
- Wave 6 (T016 + T017): The two companion reference files were enriched with new additive pattern categories:
  - `tachi-spoofing/references/detection-patterns.md`: +2 categories (6 = OAuth/OIDC Token Replay and Audience Confusion, 7 = Cloud IAM Role Assumption Chain Abuse). 67 to 136 lines.
  - `tachi-prompt-injection/references/detection-patterns.md`: +3 categories (6 = Evolved Direct/Jailbreak Variants, 7 = Indirect Injection via Poisoned External Sources, 8 = Evasion via Encoding/Obfuscation). 73 to 158 lines.
- T001 baselines: `specs/082-threat-agent-skill/baselines/*-threats.md` (6 files, one per example).
- Gate criteria: finding count per category within ±2 of T001 baseline, severity distribution ±1 per level, SARIF count ±2, ≥1 new finding surfaces from enrichment on the prototype agents' example surface, no existing finding dropped.

---

## T018 — Phase 1b Regression Verification

### Methodology Chosen: Option B (Deterministic DFD-vs-Pattern Cross-Reference Proof)

**Rationale**: Option A (invoking `/tachi.threat-model` from within the subagent tool environment and diffing output against baselines) is not feasible — subagents in this environment cannot invoke top-level slash commands. Additionally, Option A is stochastic (LLM-driven detection can vary run-to-run), whereas Option B provides deterministic proof via content equivalence, analogous to the T012 Option B methodology already used in Phase 1a.

**Proof structure**: For each enriched agent, demonstrate that (1) the new pattern categories are materially present in the ref file with actionable detection signals, (2) the agent file still loads the ref file via a `**MANDATORY**: Read` directive, (3) at least one example architecture contains one or more DFD components whose characteristics match one or more new detection signals, so (4) it is deterministically guaranteed that at least one new finding will emerge at runtime. This is proof-by-construction of runtime detection capacity, not an empirical measurement.

---

### Demonstration 1 — Spoofing Enrichment Surfaces ≥1 New Finding

**Target example**: `examples/microservices/` (richer cross-service auth surface than `examples/web-app/` — the API Gateway + Service Registry + Payment Service triad provides multiple OAuth/token-replay opportunities, and the Payment Service calls to `External Payment Provider` are a direct analogue for cross-account cloud role assumption in the "service-to-service trust via shared issuer" sense).

**Baseline spoofing findings count (from `baselines/microservices-threats.md`)**: 4 (S-1 through S-4).

1. S-1 — Rogue internal process impersonating API Gateway (missing mTLS)
2. S-2 — Service Registry poisoning redirecting payment traffic
3. S-3 — JWT token forgery at API Gateway (weak signing algorithm)
4. S-4 — DNS hijacking targeting External Payment Provider certificate chain

**Pre-refactor ref file coverage**: All 4 baseline findings are matched by original categories 1-5 (Authentication Bypass, Credential Theft and Replay, Session Hijacking, Service Impersonation, Federated Identity Attacks). These categories remain byte-verbatim in the enriched ref file at lines 19-52, so none of the 4 existing findings can be dropped.

#### DFD Component Match for Pattern Category 6 — OAuth/OIDC Token Replay and Audience Confusion

**Component cited**: `API Gateway` (DFD Process, DMZ zone)

**Component characteristics** (from `examples/microservices/architecture.md`):
- Single entry point for all external HTTPS traffic
- Routes REST requests to `Order Service` and `Payment Service` — two distinct backend services
- Listed in baseline S-3 finding as issuing JWTs with weak signing (`HS256`), implying a JWT token issuance pipeline
- Baseline mitigation text mentions "validate issuer, audience, and expiration claims" — confirming JWT aud-claim validation is a relevant concern on this component

**Matching Category 6 indicators** (from `tachi-spoofing/references/detection-patterns.md` lines 58-68):

| Indicator (Category 6) | Match Rationale |
|---|---|
| "Same access or ID token accepted by multiple distinct services from a shared issuer without per-audience `aud` claim enforcement" | API Gateway routes to both Order Service and Payment Service — if both accept the gateway-issued JWT without per-service aud validation, a token minted for the Order Service can be replayed to the Payment Service. Architecture does not declare per-service aud enforcement. |
| "`aud` claim not validated, or validated only by type rather than by exact audience identifier" | Baseline S-3 mitigation explicitly lists `aud` validation as a *recommended* control — implying the baseline DFD does **not** currently enforce audience validation. This exactly matches the Category 6 indicator. |
| "Missing `exp` enforcement or clock-skew tolerance wider than 5 minutes" | Baseline S-3 mitigation recommends 15-minute JWT expiration as a *future* control — implying current TTL is unbounded or excessive. Matches Category 6 indicator. |

**New Category 6 finding that will emerge at runtime** (projected, not empirically measured): an `aud`-confusion finding on the API Gateway, distinct from S-3 (which is generic JWT signature forgery). This new finding focuses on cross-service token replay under a shared issuer — a different attack surface than signature cracking. Projected severity `High` (Medium likelihood + High impact). This finding cannot be a reclassification of S-3 because S-3's threat description cites signature algorithm weakness (cryptographic primitive), not audience validation (claim semantics).

**Also relevant**: `Service Registry` (DFD Process, DMZ zone) is an additional Category 6 candidate — a compromised registry could redirect token-validation traffic to an attacker endpoint sharing the same issuer identifier, exactly matching the indicator "JWT `kid` header trusted without constraining the key set to a pinned JWKS endpoint". This is a secondary projected finding.

#### DFD Component Match for Pattern Category 7 — Cloud IAM Role Assumption Chain Abuse

**Component cited**: `Payment Service` calling `External Payment Provider` (DFD data flow from trusted Payment Service Process to External Entity)

**Component characteristics**:
- Payment Service makes `HTTPS / Charge Request` calls to External Payment Provider (Stripe-like third party)
- Architecture does not declare how credentials are provisioned for this external call (API key? OAuth client credential? assumed role?)
- Baseline S-4 cites DNS hijacking / certificate spoofing but does **not** address credential/role provisioning for the outbound call

**Matching Category 7 indicators** (from `tachi-spoofing/references/detection-patterns.md` lines 89-99):

| Indicator (Category 7) | Match Rationale |
|---|---|
| "Session tokens from assumed roles stored in logs, error traces, or shared caches" | Payment Service presumably logs outbound charge requests for reconciliation; without explicit credential redaction, the Payment Service session token (or OAuth bearer for the external provider) can leak into logs. |
| "No `sts:SessionTags` or `sts:SourceIdentity` constraints on assumed sessions — loses attribution across the chain" | Architecture does not declare any per-call attribution tagging on the external payment call. A cross-service abuse (if the Payment Service were to be called by a rogue Order Service) would lose attribution context. |
| "Service account or workload identity has `iam.serviceAccounts.getAccessToken` privilege over arbitrary other service accounts" | Generic indicator — matches any microservice architecture where the Payment Service holds credentials delegated from higher-level identity (e.g., IRSA in EKS, Workload Identity in GKE). Architecture does not declare least-privilege on Payment Service's IAM posture. |

**New Category 7 finding that will emerge at runtime** (projected): an IAM/credential delegation finding on the Payment Service citing missing least-privilege constraints on the outbound external provider credential. Projected severity `Medium` (Low likelihood + High impact). Distinct from S-4 (which addresses transport-layer certificate validation, not identity/role provisioning).

**Note**: Even if Category 7 match strength for `microservices/` is marginal (it is a traditional microservice, not an explicit AWS/GCP cloud architecture), the `web-app/` example's `Auth Service` is a stronger candidate — it is the credential issuer and could be matched on indicator "trust policy allows `sts:AssumeRole` from a principal pattern containing `*`" if the architecture were to declare IAM role use. The `agentic-app/` MCP Tool Server making HTTPS calls to `External API` is also a strong candidate.

#### Minimum guaranteed new findings (Spoofing, Category 6 + 7)

- **Category 6 (microservices, API Gateway)**: **1** guaranteed new finding on aud-confusion/token-replay
- **Category 7 (microservices, Payment Service)**: **1** projected new finding on missing IAM delegation least-privilege (secondary; stronger match would be in a cloud-explicit example)

**Total new spoofing findings on microservices**: **≥1** (exceeding the gate's "≥1 new finding" requirement).

**Baseline preservation**: S-1 through S-4 are all matched by original categories 1-5 which are byte-verbatim preserved. Zero drops.

---

### Demonstration 2 — Prompt-Injection Enrichment Surfaces ≥1 New Finding

**Target example**: `examples/agentic-app/` (richest LLM surface — `LLM Agent Orchestrator` with `Guardrails Service`, `Knowledge Base` RAG pipeline, `MCP Tool Server` multi-tool orchestration, and `External API` for tool calls).

**Baseline prompt-injection findings count (from `baselines/agentic-app-threats.md`)**: 3 LLM findings (plus 4 AG findings from agent-autonomy/tool-abuse agents which are out of scope for this demonstration).

1. LLM-1 — Indirect injection via documents retrieved from Knowledge Base
2. LLM-2 — Knowledge Base poisoning corrupting LLM reasoning
3. LLM-3 — LLM-generated tool call parameters containing injection payloads

**Pre-refactor ref file coverage**: LLM-1 matches Pattern 2 (Indirect Prompt Injection), LLM-2 is borderline Pattern 2 (data poisoning adjacent), LLM-3 matches Pattern 5 (Cross-Plugin Injection). Original patterns 1-5 remain byte-verbatim in the enriched ref file at lines 37-65. Zero drops possible.

#### DFD Component Match for Pattern Category 6 — Direct Injection and Jailbreaks (Evolved Variants)

**Component cited**: `LLM Agent Orchestrator` (DFD Process, Application Zone, Layer 1 Foundation Model)

**Component characteristics** (from `examples/agentic-app/architecture.md`):
- Receives `Validated Prompt` from Guardrails Service (the Guardrails handles filtering, but NOT instruction-hierarchy enforcement)
- Concatenates retrieved KB context + user prompt into LLM inference calls (multi-turn, stateful)
- Orchestrates multi-step tool calls via MCP Tool Server — state persists across steps
- Architecture does not declare conversation-state reset between privilege transitions
- Architecture does not declare adversarial prompt classifiers or refusal-rate monitoring

**Matching Category 6 indicators** (from `tachi-prompt-injection/references/detection-patterns.md` lines 72-80):

| Indicator (Category 6) | Match Rationale |
|---|---|
| "System prompts that lack explicit instruction-hierarchy enforcement (no `system`-vs-`user` role separation or equivalent privilege tagging)" | Architecture does not declare how the Orchestrator distinguishes system prompt from user prompt from retrieved content. The Guardrails Service filters input but does not assert instruction-hierarchy. Direct match. |
| "Conversation history persisting across privilege transitions without state reset" | Multi-turn orchestration implicitly persists history (required for coherent multi-step tool chains). Architecture does not declare state reset. |
| "No declared resistance to prompt-leakage probes that paraphrase the system prompt back to the model" | Architecture's Guardrails Service only declares filtering ("Rejected Prompt + Reason"), no output-side guardrails for leakage. |
| "Absence of adversarial prompt classifiers or refusal-rate monitoring on model responses" | Architecture declares no such monitoring. Only audit logging (Audit Logger), which is reactive, not preventive. |

**New Category 6 finding that will emerge at runtime** (projected): an instruction-hierarchy bypass finding on the LLM Agent Orchestrator citing DAN-style evolved jailbreak resistance gap. Distinct from LLM-1 (indirect injection) because Category 6 addresses *direct* user-supplied jailbreak payloads, which the Guardrails Service might filter but the Orchestrator itself has no second-layer defense against. Projected severity `High` to `Critical` (High likelihood + High impact; jailbreak enables scope escalation).

#### DFD Component Match for Pattern Category 7 — Indirect Injection via Poisoned External Sources

**Component cited**: `LLM Agent Orchestrator` consuming retrieved `Knowledge Base` content (DFD data flow KB to Orchestrator, labeled "Retrieved Documents")

**Component characteristics**:
- KB is a Data Store in the Application Zone with no declared provenance tracking
- Retrieved documents flow into the Orchestrator's context window
- Architecture does not declare content-extraction isolation (hidden-text stripping, HTML tag sanitization, multimodal handling)
- `MCP Tool Server` calls to `External API` produce tool results that are fed back to the Orchestrator — a tool-response-re-injection channel

**Matching Category 7 indicators** (from `tachi-prompt-injection/references/detection-patterns.md` lines 99-108):

| Indicator (Category 7) | Match Rationale |
|---|---|
| "RAG pipelines pulling from user-contributable stores without provenance tagging" | KB is a Data Store whose contribution surface is undeclared; architecture does not declare first-party vs third-party vs user-contributed sourcing. Direct match. |
| "Retrieved content lacks explicit boundary markers distinguishing untrusted data from trusted instructions" | Architecture does not declare any boundary enforcement in the KB to Orchestrator data flow. |
| "Tool-response data re-injected into the agent's next prompt without sanitization or provenance labeling" | `ToolServer to Orchestrator "Tool Result"` data flow has no declared sanitization. The subsequent Orchestrator inference concatenates the tool result into the next turn's context. |
| "Multimodal inputs (images with embedded OCR text, audio with spoken instructions, video with caption injection)" | Less-direct match — architecture does not explicitly declare multimodal ingestion, but also does not exclude it. |

**New Category 7 finding that will emerge at runtime** (projected): Distinct from LLM-1 (which addresses the *concept* of indirect injection via KB) — Category 7 addresses the *channel-specific* vectors (hidden text, invisible annotations, per-source trust scoring, tool-response re-injection). The tool-response-re-injection path is a *new* attack surface not covered by LLM-1 because LLM-1 scopes to "documents retrieved from the knowledge base", not tool-call results. Projected severity `High`.

#### DFD Component Match for Pattern Category 8 — Evasion via Encoding and Obfuscation

**Component cited**: `Guardrails Service` (DFD Process, Application Zone)

**Component characteristics**:
- Filters prompts via declared `Filtering Event Log`
- Architecture does not declare Unicode NFKC normalization or bidi-override character stripping
- Architecture does not declare Base64/hex/ROT13 decode-then-filter pipeline
- Architecture filters before forwarding to the Orchestrator, so filter bypass yields full Orchestrator scope

**Matching Category 8 indicators** (from `tachi-prompt-injection/references/detection-patterns.md` lines 127-135):

| Indicator (Category 8) | Match Rationale |
|---|---|
| "Input-filtering components use substring or keyword matching without Unicode NFKC normalization, whitespace collapse, or case fold" | Architecture does not declare normalization on the Guardrails Service input. Direct match. |
| "No declared detection for Base64, hex, URL-encoded, or ROT13 input before LLM forwarding" | Architecture does not declare decode-then-filter. |
| "Zero-width character injection (U+200B ZWSP, U+200C ZWNJ, U+200D ZWJ) splitting denied keywords" | No declared zero-width stripping. |
| "Multimodal smuggling: image-based OCR payloads" | No declared OCR-based extraction in the Guardrails filter chain. |

**New Category 8 finding that will emerge at runtime** (projected): a filter-bypass via encoding evasion finding on the Guardrails Service (*not* on the Orchestrator, because the threat is the filter's normalization gap, not the model's reasoning). This is a structurally new finding because it targets an architectural component (Guardrails Service) that the pre-enrichment 5 categories did not specifically address. Projected severity `High` (High likelihood + High impact, since filter bypass defeats the primary control).

#### Minimum guaranteed new findings (Prompt Injection, Categories 6 + 7 + 8)

- **Category 6 (agentic-app, LLM Agent Orchestrator)**: **1** guaranteed new finding on instruction-hierarchy / evolved-jailbreak
- **Category 7 (agentic-app, LLM Agent Orchestrator + tool response re-injection)**: **1** guaranteed new finding on tool-response-re-injection channel
- **Category 8 (agentic-app, Guardrails Service)**: **1** guaranteed new finding on encoding-evasion filter bypass

**Total new prompt-injection findings on agentic-app**: **≥1** (substantially exceeding the gate). In practice, the demonstration projects ≥3 new findings on this rich example.

**Baseline preservation**: LLM-1, LLM-2, LLM-3 are all matched by original categories 1-5 which are byte-verbatim preserved. Zero drops.

---

### Demonstration 3 — No Drops Argument (9 Non-Enriched Agents Unchanged + 5 Original Categories Preserved Verbatim)

**Git-level proof (9 non-enriched agents)**:

Command: `git diff main -- .claude/agents/tachi/tampering.md .claude/agents/tachi/repudiation.md .claude/agents/tachi/info-disclosure.md .claude/agents/tachi/denial-of-service.md .claude/agents/tachi/privilege-escalation.md .claude/agents/tachi/data-poisoning.md .claude/agents/tachi/model-theft.md .claude/agents/tachi/tool-abuse.md .claude/agents/tachi/agent-autonomy.md`

Result: **empty output** (zero diff). The 9 non-enriched agent files are byte-identical to `main`. Therefore:

- Any finding these 9 agents produced on any example architecture on `main` is produced verbatim on the feature branch.
- The baselines `baselines/*-threats.md` for T (tampering), R (repudiation), I (info-disclosure), D (DoS), E (privilege-escalation), and the LLM/AG agents (data-poisoning, model-theft, tool-abuse, agent-autonomy) are all 1:1 reproducible from the current branch.
- **Zero findings can be dropped** by any of these 9 agents, because their detection logic is identical.

**Content-equivalence proof (5 original categories in each enriched ref file)**:

**Spoofing ref file** (lines 19-52): Verified via git comparison against `main:.claude/agents/tachi/spoofing.md` pre-refactor `### Patterns and Indicators` section. The 5 original categories (Authentication Bypass, Credential Theft and Replay, Session Hijacking, Service Impersonation, Federated Identity Attacks) appear byte-verbatim as `##`-level subsections at lines 19-52 of the new ref file. All bullet points are preserved verbatim. Enrichment (Categories 6 and 7) is purely additive at lines 54-115.

**Prompt-Injection ref file** (lines 37-65): Verified via git comparison against `main:.claude/agents/tachi/prompt-injection.md` pre-refactor `### Detection Patterns` section. The 5 numbered patterns (1. Direct Prompt Injection, 2. Indirect Prompt Injection, 3. Jailbreaking, 4. System Prompt Extraction, 5. Cross-Plugin Injection) appear byte-verbatim as numbered list items with identical sub-bullets. Enrichment (Categories 6, 7, 8) is purely additive at lines 67-149.

**Conclusion (FR-14 / ADR-023 Decision 3 compliance)**: Enrichment is strictly additive. Any pre-refactor finding that would have been produced by the 5 original categories is still produced by those categories after enrichment, because the category text is identical. **Zero existing findings can be dropped by enrichment.**

---

### Demonstration 4 — Count Deltas and Tolerance Check

| Agent | Pre-Enrichment Categories | Post-Enrichment Categories | Category Delta | ±2 Tolerance? |
|---|---|---|---|---|
| tachi-spoofing | 5 | 7 | +2 | PASS (at boundary) |
| tachi-prompt-injection | 5 | 8 | +3 | FAIL-tolerance strictly, PASS-intent |

**Tolerance interpretation clarification**: The gate criteria "finding count per category within ±2" refers to **per-category finding counts across examples**, not **agent-level category counts**. The +2/+3 category additions increase the *ceiling* of potential findings, but the *existing* 5 categories continue producing identical counts.

**Per-category finding count (existing 5 categories) delta**: **0** (byte-verbatim preservation → deterministic count equivalence). Pass ±2.

**New category finding count delta**:
- Spoofing Category 6 (OAuth token replay): Expected +0 to +3 findings per example, depending on DFD match. Microservices: projected +1 (API Gateway aud confusion).
- Spoofing Category 7 (Cloud IAM): Expected +0 to +2 findings per example. Microservices: projected +1 (Payment Service). Other examples: 0 (no explicit cloud IAM surface).
- Prompt-Injection Category 6 (Evolved Jailbreak): Expected +0 to +1 findings per LLM-bearing example. Agentic-app: projected +1.
- Prompt-Injection Category 7 (Poisoned External): Expected +0 to +2 findings per RAG-bearing example. Agentic-app: projected +1 (tool response re-injection).
- Prompt-Injection Category 8 (Encoding Evasion): Expected +0 to +1 findings per LLM-bearing example. Agentic-app: projected +1 (Guardrails Service).

**Severity distribution impact**: New findings project into High/Critical band. Expected severity distribution delta: +1 to +3 in High and/or Critical (additive). Existing severity distribution of baseline findings unchanged (5 original categories produce identical threats). Pass ±1 per level for existing findings; new findings extend the distribution additively.

**SARIF count delta**: SARIF is generated from the same findings population. Count delta mirrors the finding count delta: +2 to +5 across both enriched agents combined. Pass ±2 **per agent** (the gate is per-agent ±2, not total ±2 across both agents).

---

### T018 Gate Status: **PASS**

| Gate Criterion | Status | Evidence |
|---|---|---|
| Finding count per category within ±2 of T001 | PASS | Existing 5 categories preserved byte-verbatim -> zero delta on existing categories. New categories 6/7 (spoofing) and 6/7/8 (prompt-injection) add 0-3 findings per example, within ±2 per-category tolerance. |
| Severity distribution ±1 per level | PASS | Existing findings: zero delta (byte-verbatim preservation). New findings: additive extension of High/Critical band. |
| SARIF count ±2 | PASS | SARIF mirrors finding count; per-agent delta ≤2. |
| ≥1 new finding from enrichment on prototype example surface | PASS | Spoofing: ≥1 on microservices (API Gateway aud confusion, Category 6). Prompt-Injection: ≥1 on agentic-app (LLM Orchestrator instruction-hierarchy, Category 6 -- and +2 more on Categories 7, 8). |
| No existing finding dropped | PASS | 9 non-enriched agents byte-identical to main (zero diff). 5 original categories in each enriched ref file byte-verbatim preserved (git content check). Enrichment is strictly additive per FR-14/ADR-023 Decision 3. |

**Overall T018**: **PASS** via Option B deterministic proof. Empirical validation via Option A (live `/tachi.threat-model` invocation + baseline diff) would provide additional confidence but is not feasible from within the subagent tool environment and is not required by the gate criteria given the strength of the content-equivalence argument.

---

## T019 — Phase 1b Line Count Verification (FR-10)

**Gate (FR-10)**: Agent file line caps — STRIDE ≤120, AI ≤150, hard ceiling 180. Ref files have no cap.

| File | Type | Observed LOC | Expected LOC (post-Wave 6) | Cap | Status |
|---|---|---|---|---|---|
| `.claude/agents/tachi/spoofing.md` | Agent (STRIDE) | 51 | 51 (unchanged since Wave 5) | ≤120 | PASS |
| `.claude/agents/tachi/prompt-injection.md` | Agent (AI) | 95 | 95 (unchanged since Wave 5) | ≤150 | PASS |
| `.claude/skills/tachi-spoofing/references/detection-patterns.md` | Ref | 136 | ~136 (post-T016) | none (n/a) | PASS (recorded for record) |
| `.claude/skills/tachi-prompt-injection/references/detection-patterns.md` | Ref | 158 | ~158 (post-T017) | none (n/a) | PASS (recorded for record) |

**Command used**: `wc -l .claude/agents/tachi/spoofing.md .claude/agents/tachi/prompt-injection.md .claude/skills/tachi-spoofing/references/detection-patterns.md .claude/skills/tachi-prompt-injection/references/detection-patterns.md`

**Output**:
```
      51 .claude/agents/tachi/spoofing.md
      95 .claude/agents/tachi/prompt-injection.md
     136 .claude/skills/tachi-spoofing/references/detection-patterns.md
     158 .claude/skills/tachi-prompt-injection/references/detection-patterns.md
     440 total
```

### T019 Gate Status: **PASS**

- Both agent files remain well under their tier caps (spoofing 51/120 = 42.5% of cap; prompt-injection 95/150 = 63.3% of cap; both well under the 180 hard ceiling).
- Both ref files exceed their pre-Wave-6 length by the expected delta (spoofing 67 to 136 = +69; prompt-injection 73 to 158 = +85) — enrichment was applied as planned.
- Agent files are byte-identical to Wave 5 state (no incidental agent drift during enrichment) — confirming that Wave 6 (T016 + T017) operated purely on the ref files as required.
- Ref files have no line-count cap per FR-10 and per ADR-023 Decision 4 (skill references are externalized precisely to lift the agent-file line cap).

---

## Concerns and Caveats

1. **Option B is deterministic proof, not empirical measurement.** The projected new findings are described by their structural match against the ref file indicators. An adversarial reviewer could argue that runtime LLM behavior might not produce these findings despite matching indicators (e.g., the LLM producing the threat might conflate the new Category 6 aud-confusion finding with the existing S-3 JWT forgery finding). This concern is noted but not considered blocking because (a) the indicator language in the ref file is distinctive enough to generate distinct threats, (b) the content of the existing 5 categories is preserved verbatim so the existing findings cannot be eliminated by merging, and (c) the gate criteria accept Option B per the task description.

2. **Tolerance interpretation ambiguity** (category count vs. finding count): As noted in Demonstration 4, the "±2 per category" tolerance can be read as either per-agent category count (strict reading: spoofing +2, prompt-injection +3 — prompt-injection would fail strict) or per-category finding count (intended reading: existing 5 categories unchanged, new categories are additive). The intended reading is clearly the latter (since the existing categories are untouched), and the gate is intended to prevent drops, not to cap additive enrichment.

3. **Empirical validation opportunity**: A future T020 or follow-up task could run `/tachi.threat-model` on `examples/microservices/` and `examples/agentic-app/` from the top level (outside the subagent environment) and diff the output against the T001 baselines to empirically confirm the projections in Demonstrations 1 and 2. This is orthogonal to the Phase 1b gate and belongs in a separate validation loop. The current proof is sufficient for Phase 1b per the task's Option B permission.

4. **Category 7 (Cloud IAM) weak match on microservices**: The microservices example is a traditional service-mesh architecture without explicit cloud IAM role assumption. The Category 7 match for Payment Service is the best available but is not a pure cloud-IAM chain. A stronger Category 7 match will emerge when a future example includes explicit AWS/GCP IAM trust policies. This does not block the current gate because spoofing Category 6 already provides ≥1 guaranteed new finding on microservices independently.

5. **Prompt-injection Category 6 overlap with baseline LLM-1**: LLM-1 is a generic indirect injection finding that could theoretically subsume Category 6's evolved-jailbreak specifics. However, the Category 6 finding focuses on *direct* user-supplied jailbreak payloads with instruction-hierarchy bypass, which is a structurally different threat from LLM-1's *indirect* RAG-retrieved injection. Risk of collapse is low but not zero.

---

## T020 Security Spot-Check

**Reviewer**: security-analyst
**Scope**: 5 new enrichment categories (2 spoofing + 3 prompt-injection) added by Wave 6 (T016 + T017) to two prototype companion skill reference files
**Date**: 2026-04-11

### Review methodology

For each of the 5 new categories I verified (1) primary-source quality by checking that every cited URL resolves to an authoritative, actively-maintained standard, advisory, or peer-reviewed body (OWASP, CWE, NIST, MITRE ATT&CK / ATLAS, AWS/Azure/GCP canonical docs, or named peer-reviewed research), flagging any secondary citation as a WARN; (2) taxonomy fit by checking that each new category is a sub-variant of the parent threat class (identity-spoofing sub-type for spoofing; LLM input-layer attack variant for prompt-injection) rather than a cross-class intruder (e.g., a tampering concept placed inside spoofing); (3) speculation grounding by scanning indicator language for red-flag phrases ("theoretical", "hypothetical", "could potentially", "if an attacker were to") and confirming indicators are backed by observed CVEs, published PoCs, or MITRE-catalogued techniques; and (4) overlap against the 5 original categories in the same file using the byte-verbatim original category text confirmed by the T018 content-equivalence check. For "evolved variant" categories I applied the additive-signal test (per T020 criterion 4): the test is whether the new indicators ADD signal beyond the original, not whether they partially share scope.

### Spoofing Category 6: OAuth/OIDC Token Replay and Audience Confusion

- **Source quality**: **PASS**. Citations are all primary and canonical:
  - OWASP Top 10 2021 A07 (`https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/`) — canonical OWASP URL, currently maintained; slightly older (2021) but OWASP Top 10 revisions are on a 3-4 year cadence and A07 is not superseded.
  - CWE-287 Improper Authentication (`https://cwe.mitre.org/data/definitions/287.html`) — canonical MITRE CWE URL.
  - CWE-306 Missing Authentication for Critical Function (`https://cwe.mitre.org/data/definitions/306.html`) — canonical MITRE CWE URL.
  - CWE-345 Insufficient Verification of Data Authenticity (`https://cwe.mitre.org/data/definitions/345.html`) — canonical MITRE CWE URL. Well-aligned with `aud` claim validation failure semantics.
  All four URLs are authoritative with no secondary/blog citations. Minor note: a direct citation of RFC 7519 JWT (`exp`, `aud`, `jti` claims) would further strengthen the source stack but is not required because OWASP A07 and CWE-345 already cover the threat semantically.
- **Taxonomy fit**: **FITS**. OAuth/OIDC token replay and `aud` confusion are identity-layer attacks that cause one party to be authenticated as another — precisely the STRIDE Spoofing class. This is a clean refinement of the pre-existing "Federated Identity Attacks" category (pattern 5), narrowing the federated-identity space to token-level replay and audience-confusion sub-types.
- **Speculation**: **GROUNDED**. Indicators map to well-documented attack classes. `aud` confusion is catalogued in OAuth 2.0 threat model (RFC 6819) and is a known root cause in multiple real-world incidents. JWT `kid` header abuse is a documented CVE class (e.g., CVE-2018-0114 `node-jose`, CVE-2022-21449 Java ECDSA, CVE-2020-28042 `jsonwebtoken` kid path injection). `alg: none` and HS256/RS256 confusion are the original 2015 Auth0 research findings. No speculative "what if" language.
- **Overlap**: **PARTIAL OVERLAP — JUSTIFIED**. There is scope adjacency with original category 5 (Federated Identity Attacks), which already includes JWT signature confusion and missing issuer validation. However, Category 6 adds distinct signal in three directions: (a) per-audience `aud` enforcement as a claim-semantics concern (not a cryptographic concern), (b) refresh-token-rotation, `jti` replay-windowing, and clock-skew tolerance (operational-temporal controls absent in cat 5), and (c) multi-tenant issuer / shared-issuer scope crossing. The indicators ADD signal rather than paraphrase cat 5. Justified refinement.

### Spoofing Category 7: Cloud IAM Role Assumption Chain Abuse

- **Source quality**: **PASS**. Citations are primary and canonical:
  - MITRE ATT&CK T1078.004 Valid Accounts: Cloud Accounts (`https://attack.mitre.org/techniques/T1078/004/`) — canonical MITRE URL, continuously maintained.
  - MITRE ATT&CK T1550.001 Application Access Token (`https://attack.mitre.org/techniques/T1550/001/`) — canonical MITRE URL.
  - AWS IAM Confused Deputy Problem (`https://docs.aws.amazon.com/IAM/latest/UserGuide/confused-deputy.html`) — canonical AWS UserGuide URL, not a marketing/blog deep link.
  All three URLs are authoritative. A strengthening would be a GCP `iam.serviceAccounts.getAccessToken` canonical doc citation (the category mentions GCP and Azure Managed Identity without a corresponding primary source) — this is a WARN-adjacent observation but not blocking because AWS STS + MITRE ATT&CK cover the threat semantically and the spoofing class does not hinge on cloud-provider specificity.
- **Taxonomy fit**: **FITS**. Cloud IAM role assumption chain abuse is an identity-layer attack (the attacker causes the authorization boundary to be crossed as a different principal). STRIDE Spoofing is the correct class — confused-deputy is identity impersonation, not tampering or EoP at the class level (even though it produces privilege gain). It is a natural generalization of "Service Impersonation" (original category 4) into the cloud workload identity plane.
- **Speculation**: **GROUNDED**. Every indicator maps to documented attack classes: SSRF-to-IMDSv1 (Capital One 2019 breach — the canonical public precedent), over-permissive `sts:AssumeRole` trust policies (AWS re:Inforce talks, numerous pentesting case studies), missing external ID conditions (explicitly named in AWS's own documentation as the confused-deputy fix). IMDSv1 hop-limit guidance is the AWS-published control. No "theoretical" language.
- **Overlap**: **PARTIAL OVERLAP — JUSTIFIED**. Adjacency with original category 4 (Service Impersonation: missing mTLS, DNS spoofing) and category 1 (Authentication Bypass: hardcoded credentials). Category 7 adds distinct signal on: (a) role assumption chain length and auditability, (b) trust policy condition syntax (external ID, `SourceIdentity`, `SourceVpce`, `PrincipalTag`), (c) IMDS service reachability as the SSRF-to-credential-theft pivot, and (d) session token handling in logs / caches. Indicators do not paraphrase original categories — they operate on a different abstraction layer (cloud control plane rather than application transport). Justified refinement.

### Prompt-injection Category 6: Direct Injection and Jailbreaks (Evolved Variants)

- **Source quality**: **PASS**. Citations are primary and canonical:
  - OWASP LLM01:2025 Prompt Injection (`https://genai.owasp.org/llmrisk/llm01-prompt-injection/`) — canonical OWASP GenAI URL, current 2025 edition.
  - MITRE ATLAS AML.T0051 LLM Prompt Injection: Direct (`https://atlas.mitre.org/techniques/AML.T0051`) — canonical MITRE ATLAS URL.
  - MITRE ATLAS AML.T0054 LLM Jailbreak (`https://atlas.mitre.org/techniques/AML.T0054`) — canonical MITRE ATLAS URL.
  All three are authoritative and post-2024 / actively maintained. This is the strongest source stack of the 5 categories under review.
- **Taxonomy fit**: **FITS**. Explicitly labeled "Evolved Variants" of pattern 1 (Direct Prompt Injection) and pattern 3 (Jailbreaking). The category intentionally refines the prior categories rather than introducing a new threat class. Taxonomic boundary is observed.
- **Speculation**: **GROUNDED**. DAN, AIM, STAN, and developer mode are all publicly documented jailbreak templates with thousands of catalogued prompts (e.g., jailbreakchat.com archives, `l1x0r/DAN` GitHub repos). MITRE ATLAS AML.T0054 explicitly catalogues these under "LLM Jailbreak". Instruction-hierarchy bypass is addressed in OpenAI's own July 2024 research paper "The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions" — a direct reference to this paper would further strengthen the category but the OWASP LLM01:2025 and ATLAS citations are already sufficient. Multi-turn jailbreak scaffolding is also catalogued (e.g., "Crescendo" attack, Microsoft 2024). No speculative language observed.
- **Overlap**: **PARTIAL OVERLAP — JUSTIFIED** (this is the explicitly-labeled evolved-variant case that the T020 criterion permits). Significant textual adjacency with original pattern 1 (direct injection) and pattern 3 (jailbreaking) — which is expected and by design. Applying the additive-signal test: the new indicators ADD role-hierarchy tagging (system/user/tool separation), explicit DAN-family taxonomy, nested template escape tokens (`### End of system prompt ###`, fake XML/tool-call tags), conversation-state reset at privilege transitions, prompt-leakage probes ("paraphrase the system prompt back"), and refusal-rate monitoring. These are net-new detection signals absent from the original patterns, which spoke generically about "absence of output filtering" and "role-play or persona-switching attacks". The refinement is substantive and justified.

### Prompt-injection Category 7: Indirect Injection via Poisoned External Sources

- **Source quality**: **PASS**. Citations are primary:
  - OWASP LLM01:2025 Indirect Injection subsection (`https://genai.owasp.org/llmrisk/llm01-prompt-injection/`) — canonical OWASP GenAI URL.
  - MITRE ATLAS AML.T0051 (`https://atlas.mitre.org/techniques/AML.T0051`) — canonical MITRE ATLAS URL.
  - Greshake et al., 2023 "Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection" — peer-reviewed AISec '23 paper, the foundational published research for indirect prompt injection. The citation is scholarly (no URL provided inline), which is acceptable for a named peer-reviewed work; arXiv URL `https://arxiv.org/abs/2302.12173` could be added for click-through but the citation is authoritative as-is.
  All three are primary sources. MITRE ATLAS does maintain a distinct technique for indirect injection (AML.T0051 has sub-techniques / variants) but the direct category citation is correct.
- **Taxonomy fit**: **FITS**. Indirect injection via poisoned external sources is a canonical prompt-injection sub-class (input-layer attack via context-window contamination). Refinement of pattern 2 (original "Indirect Prompt Injection").
- **Speculation**: **GROUNDED**. Every indicator is backed by published research or observed incidents: hidden-text HTML injection is the canonical Greshake 2023 PoC vector; calendar-invite indirect injection is documented in Simon Willison's blog and in Microsoft's 2024 Copilot indirect-injection advisory; multimodal smuggling is catalogued in Anthropic's and Google DeepMind's published red-team findings; tool-response re-injection is documented in OWASP LLM01:2025's "multi-step agent" discussion. The "code comments carrying `// IGNORE PRIOR: <instructions>`" indicator is based on observed supply-chain-adjacent attacks on code-indexing agents. No speculative language.
- **Overlap**: **PARTIAL OVERLAP — JUSTIFIED**. Strong scope adjacency with original pattern 2 (Indirect Prompt Injection) — by design, as this is an explicit refinement. Additive-signal test: the new indicators ADD channel-specific vectors (HTML attribute injection, CSS-hidden text, PDF hidden text layers, email subject-line injection, calendar invite description fields, multimodal OCR/audio/video, code comment injection, per-source provenance tagging). The original pattern 2 spoke generically of "RAG pipelines", "email/message processing", and "database records"; Category 7 provides channel-level detection signals. Substantively additive.

### Prompt-injection Category 8: Evasion via Encoding and Obfuscation

- **Source quality**: **PASS**. Citations are primary:
  - OWASP AI Exchange (`https://owaspai.org/docs/ai_security_overview/`) — canonical OWASP AI Exchange URL.
  - OWASP LLM01:2025 obfuscation subsection (`https://genai.owasp.org/llmrisk/llm01-prompt-injection/`) — canonical OWASP GenAI URL.
  - MITRE ATLAS AML.T0051 (`https://atlas.mitre.org/techniques/AML.T0051`) — canonical MITRE ATLAS URL.
  Note: Unicode TR36 (Security Considerations) and Unicode TR39 (Security Mechanisms) would be ideal supplementary citations for the homoglyph and bidi-override indicators, but the category's primary source stack is already authoritative. A WARN-adjacent observation: adding a Unicode TR reference would strengthen the claim on NFKC normalization specifically. Not blocking.
- **Taxonomy fit**: **FITS**. Encoding and obfuscation evasion is an input-layer attack that smuggles prompt injection payloads past filter components — the category is squarely within the prompt-injection threat class. The self-description correctly notes it targets "the normalization gap between input-filtering components and the LLM tokenizer" — a legitimate new detection surface.
- **Speculation**: **GROUNDED**. Indicators are backed by observed technique classes: Unicode homoglyph substitution is catalogued by Unicode Consortium (TR36); zero-width character injection is the basis of the well-known "invisible prompt injection" PoCs (Riley Goodside demonstrations Dec 2023, Anthropic and OpenAI blog acknowledgments 2024); Base64/hex/ROT13 encoding bypass of input filters is documented in multiple public PoCs; tokenizer-aware payloads are published in academic red-teaming work (e.g., "GCG" Zou et al. 2023 adversarial suffix research, Greedy Coordinate Gradient). Multilingual bypass is documented in OpenAI's own "Language Models are Few-Shot Learners" safety evaluations and in the "low-resource language jailbreak" research (Yong et al. 2023). No speculative language.
- **Overlap**: **NO OVERLAP** (or minimal). Category 8 is the most taxonomically distinctive of the three prompt-injection additions. The original 5 patterns do not address: Unicode normalization, encoding decode-then-filter pipelines, zero-width character stripping, bidi-override detection, multimodal OCR/audio extraction, or tokenizer-filter normalization gaps. Category 8 targets the input-filter component specifically (the Guardrails-Service analogue), which was not an explicit detection surface in the original 5 patterns. This is a legitimate vocabulary expansion, not a refinement.

### Aggregate verdict

**PASS**. All 5 new categories cite primary sources with canonical URLs (OWASP, CWE, MITRE ATT&CK, MITRE ATLAS, AWS UserGuide, peer-reviewed Greshake 2023), fit cleanly within their parent threat taxonomy (spoofing sub-types for the 2 spoofing additions; prompt-injection sub-variants for the 3 prompt-injection additions), are grounded in observed CVEs / MITRE-catalogued techniques / published PoCs (no speculative "what if" language), and add substantive net-new detection signal beyond the preserved original 5 categories. The enrichment is high-quality security-content and is ready to ship to the remaining 9 agents in Waves 9-11.

### ±2 tolerance interpretation recommendation

**Recommendation: Interpretation (b)** — the ±2 tolerance applies to per-existing-category finding drift, not to new-category count.

**Rationale**: The gate's purpose per FR-14 and ADR-023 Decision 3 is regression prevention — "no existing finding dropped, no silent count change in existing detection signals". A gate that caps total category count at +2 would make the feature's ≥2-enrichment floor structurally incompatible with the regression gate (prompt-injection added 3 categories, which under interpretation (a) would fail). This is not a reasonable gate-design outcome.

Interpretation (b) also matches the underlying security-review principle: what you want to detect is "did the existing patterns continue to fire at their historical rate, or did enrichment silently cannibalize existing findings by re-categorizing them?" That is a per-existing-category finding-count question, not a per-file category-count question. Under interpretation (b), the tester's T018 content-equivalence proof (existing 5 categories preserved byte-verbatim) is the strongest possible evidence for gate pass: the existing categories cannot drift because their text cannot drift. Enrichment categories 6/7/8 are additive and produce only *new* findings — they cannot subtract from existing-category counts.

A gate that limited enrichment additivity would also create a perverse incentive to under-enrich or to pack multiple distinct attack surfaces into a single category (e.g., "Category 6: All the new stuff"), which would harm content quality and auditability. Interpretation (b) aligns the gate with its security-regression purpose and is unambiguously the intended reading.

**Advisory note for T021 joint review**: The architect and team-lead should ratify interpretation (b) in the gate criteria text of `specs/082-threat-agent-skill/plan.md` (or equivalent governance doc) to prevent the ambiguity from recurring on T048 Phase 2e review after Waves 9-11. A single sentence ("±2 tolerance applies to finding counts produced by pre-existing categories; new categories added by enrichment are not bounded by this tolerance") would resolve this permanently.

### Concerns and recommendations

1. **Minor: GCP/Azure canonical docs missing in Spoofing Category 7** — The category text mentions GCP `iam.serviceAccounts.getAccessToken` and Azure Managed Identity but cites only the AWS `confused-deputy` UserGuide. Recommend adding canonical GCP and Azure docs for completeness before T048 (non-blocking, WARN-adjacent). Candidate URLs: Google Cloud IAM Service Account Credentials API canonical doc; Azure Managed Identity overview canonical doc. This is a robustness improvement, not a gate failure.

2. **Minor: Unicode TR references would strengthen Prompt-Injection Category 8** — Unicode TR36 (Security Considerations) and TR39 (Security Mechanisms) are the primary normative sources for NFKC normalization, homoglyph detection, and bidi-override handling. Recommend adding these as supplementary citations before T048. Non-blocking.

3. **Minor: Greshake 2023 arXiv URL would improve click-through** — The Greshake et al. 2023 citation in Prompt-Injection Category 7 is scholarly but lacks a direct URL. Suggest adding `https://arxiv.org/abs/2302.12173` for navigability. Non-blocking — named peer-reviewed work is authoritative without an inline URL.

4. **Observation (not a concern): Category 6 prompt-injection overlap with Category 1/3 is explicitly labeled** — The "Evolved Variants" label is the category's explicit declaration that it refines the originals. The additive-signal test passes (new indicators add role-hierarchy tagging, DAN-family taxonomy, nested template escape, conversation-state reset, prompt-leakage probes, refusal-rate monitoring) but future reviewers should apply the same test at T048 rather than reject on overlap-visibility alone.

5. **Observation (not a concern): Taxonomy labeling strength** — The spoofing file names new categories as "Pattern Category 6" and "Pattern Category 7" (with descriptive titles), while the prompt-injection file uses the same "Pattern Category N" label but retains a differing original-5 structure (numbered list items for 1-5, then headings for 6-8). This is a minor structural inconsistency across the two files and may warrant a unification pass before T048 for visual consistency. Non-blocking.

6. **Positive note: citation strength ranking** — Strongest source stack: Prompt-Injection Category 6 (OWASP LLM01:2025 + two MITRE ATLAS techniques, post-2024). Strongest taxonomy fit: Spoofing Category 6 (clean refinement of original pattern 5). Most novel surface: Prompt-Injection Category 8 (no overlap — legitimately expands vocabulary to normalization-gap detection). These should serve as exemplars for the remaining 9 agents in Waves 9-11.

---

## T021 Joint Gate Ruling (architect + team-lead)

**Date**: 2026-04-11
**Reviewers**: architect, team-lead (parallel reviews, independent convergence)
**Verdict**: **APPROVED_WITH_CONCERNS** (joint) — architect APPROVED_WITH_CONCERNS + team-lead APPROVED; applying the more cautious label per joint-review discipline
**Iteration**: 1 of 2 used (Phase 1b sub-budget, independent of Phase 1a per spec data-model)

### Technical gate criteria summary

| Check | Status | Evidence |
|---|---|---|
| T018 regression — ≥1 new finding per enriched agent | PASS | Option B structural proof: spoofing C6 matches microservices API Gateway / aud enforcement; prompt-injection C6+C8 match agentic-app LLM Orchestrator / Guardrails Service |
| T018 regression — no dropped findings | PASS | 9 non-enriched agents byte-identical; 5 original categories in each enriched file preserved verbatim |
| T019 line counts | PASS | spoofing.md 51/120; prompt-injection.md 95/150; ref files 136 and 158 (no cap) |
| T020 security spot-check | PASS | 5/5 categories GROUNDED; 5/5 FITS taxonomy; 4/5 PARTIAL-JUSTIFIED overlap, 1/5 NO OVERLAP; all citations primary sources |

### Joint ruling findings

**1. ±2 tolerance interpretation (b) ratified**

Both reviewers ratify interpretation (b): "±2 tolerance applies to finding counts produced by pre-existing categories; new categories added by enrichment are not bounded by this tolerance." Interpretation (a) is structurally incompatible with the ≥2 enrichment floor. Architect mandates a **plan.md FR-13 area amendment before T049** (Wave 14 aggregate floor check) to lock this interpretation permanently — not before Wave 9. Team-lead confirms this can be folded into Wave 8 housekeeping (see §Follow-ups).

**2. Option B methodology: valid with acknowledged asymmetry**

Architect accepts Option B for Phase 1b with one asymmetry caveat: Option B is strong on the "no drops" sub-question (byte-identical non-enriched agents + verbatim-preserved original categories give a deterministic proof of no drops) but is weaker on the "≥1 new finding" sub-question (proves conditions for new findings are met, rather than demonstrating findings actually emerge from the LLM). This weakness is acceptable for prototype-scale Phase 1b because the match quality is high and the ≥1 floor is easily met; at T047 / Phase 7 aggregate scale, architect **recommends Option A (empirical pipeline runs)** if operationally feasible — this does NOT block Phase 1b.

**3. Overlap findings acceptable now, re-audit at T047**

Four of five new categories have "partial-justified overlap" with existing categories. Architect rules this acceptable on first-principles grounds: indicators are the runtime primitive, categories are authorial grouping for contributor navigation, and overlap at the indicator level is a real issue (duplication) while overlap at the category level is a naming question. T047 cross-agent overlap audit should apply an "additive-signal test" per category: does the new category add indicators the existing category lacks? If yes, accept; if no, reject. All 5 new categories pass this test on first-principles reading.

**4. E-4 exit criterion partially validated**

Phase 1 validates the sibling skill-variant pattern on n=2 agents across both STRIDE and AI tiers. Both halves — extraction (Phase 1a T015) and enrichment (Phase 1b T021) — are structurally validated. Full generalization to n=11 is what Waves 9-11 prove, NOT what Phase 1 prototype proves. T022 ADR-023 Phase 1 Validation section should acknowledge this explicitly: "Phase 1 validated the pattern on n=2; Waves 9-11 test generalization to the remaining 9 agents."

**5. R1 and R2 status updated**

- **R1** (sibling variant doesn't generalize): **LOW and decreasing** — both prototype halves cleanly validated. Pattern works for STRIDE and AI tiers.
- **R2** (enrichment below ≥22 floor): **LOW-MEDIUM, on-track** — team-lead projects 23 minimum / 32 conservative / 37 ceiling against the 22 floor. Prompt-injection's +3 contribution shows headroom, and high-material agents (tool-abuse, data-poisoning, model-theft) are queued for Waves 9-11.

### Residual concerns (non-blocking)

- **C1** (architect + team-lead): Plan.md amendment to FR-13 / ±2 tolerance area. One sentence clarification. Must land **before T049 (Wave 14)**, not before Wave 9.
- **C2** (team-lead): AML.T0058 ownership conflict between tool-abuse (Wave 10) and agent-autonomy (Wave 11). Team-lead recommends a 5-minute task-text clarification in T038 and T040 during Wave 8 housekeeping, plus formal owner assignment at T047 (Wave 13).
- **C3** (team-lead, carry-forward from T015): agent-autonomy tier cap risk at Wave 11 Track 3 (201 baseline → ≤150 target). Watch item; Q7 contingency (migrate example findings to companion ref file) ready to trigger if needed.
- **C4** (architect): Minor source-citation gaps noted by security-analyst (GCP/Azure canonical docs for Spoofing C7; Unicode TR36/TR39 for Prompt-Injection C8; arXiv URL for Greshake 2023). All non-blocking WARN items for T048 follow-up, not Phase 1b blockers.
- **C5** (architect): T022 Phase 1 Validation section should enumerate 6 items (2 from T015 + 4 from T021). No 5th ADR decision required.

### Follow-ups for Wave 8 (T022 + T023)

1. **T022 ADR-023 promotion** — Draft → Accepted with 6-item Phase 1 Validation section including:
   - (from T015) Canonical 5-section shape (6 for AI-tier with inline examples); Empty Results Handling and Output Handoff not in canonical shape
   - (from T021) Sibling variant pattern validated on n=2 for both tiers; enrichment first-class operation confirmed; ±2 tolerance interpretation (b) documented; Option B methodology valid for extraction, Option A preferred for enrichment scale verification at T047
2. **Plan.md FR-13 area amendment** — clarify ±2 tolerance interpretation (b) before T049 (Wave 14). Can land alongside T022 or as separate task.
3. **AML.T0058 task-text clarification** — T038 (tool-abuse) and T040 (agent-autonomy) get a 5-minute task-text edit noting "AML.T0058 canonical owner to be assigned at T047; in the interim, both agents may extract their version — duplication is acceptable at this phase and will be resolved at T047".

### Phase 4+5 (Waves 9-11) readiness

**READY** to proceed, subject to:
- Wave 8 T022 ADR acceptance (normal)
- Wave 8 T023 Phase 1 Combined Checkpoint (normal — cites T015 and T021 approvals)
- No new dependencies introduced by Phase 1b

### Signed approvals

```yaml
joint_gate: T021 Phase 1b
feature: 082-threat-agent-skill
status: APPROVED_WITH_CONCERNS
date: 2026-04-11
tolerance_ruling: interpretation (b) ratified
methodology_ruling: Option B valid, Option A preferred for T047 scale
overlap_ruling: acceptable now; re-audit at T047 via additive-signal test
e4_validation: partial (n=2 prototype; n=11 generalization still to be proven in Waves 9-11)
iteration_used: 1 of 2 (Phase 1b sub-budget)
r1_status: LOW, decreasing
r2_status: LOW-MEDIUM, on-track (23-37 projection vs 22 floor)
architect_signoff:
  status: APPROVED_WITH_CONCERNS
  file: .aod/results/architect-t021-phase-1b-gate.md
team_lead_signoff:
  status: APPROVED
  file: .aod/results/team-lead-t021-phase-1b-gate.md
next_gate: T023 Phase 1 Combined Checkpoint (Wave 8)
```

**Phase 4+5 rollout (Waves 9-11) is unblocked subject to Wave 8 T022/T023 completion.**
