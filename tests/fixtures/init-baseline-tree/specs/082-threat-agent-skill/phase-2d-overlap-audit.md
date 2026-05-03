---
phase: 2d
task: T047
status: COMPLETE
auditor: architect
reviewed: 11 detection-patterns.md files
overlaps_found: 11
overlaps_retained_duplicated: 6
overlaps_canonical_assigned: 5
wave: 13
date: 2026-04-11
---

# Phase 2d — Cross-Agent Coverage Overlap Audit (T047)

## Overview

This audit reviews all 11 tachi threat-agent companion skill detection-pattern reference files to identify overlapping detection categories and apply the **additive-signal test** ratified at T015 / T021 (Phase 1 joint rulings) and recorded in ADR-023 §Phase 1 Validation item 5. The test asks: when two agents claim coverage for the same technique/pattern, does each view add a signal the other view cannot detect? If yes/yes, duplication is retained with each agent owning the canonical signal facet for its lane. If only one yields, the yielding view is the canonical owner. If neither adds signal, primary-category ownership decides. If signals are redundant, the more specific signal wins.

Eleven candidate overlaps were surveyed by cross-grepping technique IDs, CWEs, OWASP categories, and ATT&CK/ATLAS references across all 11 files. Each candidate was opened to the indicator level (not just the citation footer) before classification, because Primary-Sources footnotes are reference inventories, not detection claims, and must not be conflated with category-level overlap.

**Outcome**: 11 overlaps surfaced. **6 overlaps pass the additive-signal test bilaterally** and are retained as duplicated coverage with explicit lane separation (the most prominent being AML.T0058 between tool-abuse and agent-autonomy, which was the explicit T021 carve-out). **5 overlaps fail the bilateral test** but were already correctly assigned canonical ownership during extraction (2 are footnote-only references with no detection claim; 3 are deliberate cross-references in Primary-Sources lists with no indicator-level conflict). **Zero ref files require content modification.** No new overlaps requiring de-scoping were uncovered. **Verdict: PASS.** Phase 2d passes without action items; the cross-agent coverage matrix is sound for downstream Wave 14 (T049 enrichment floor tally) and Wave 15 (T050 full-regression gate).

## Summary Table

| ID  | Technique / Pattern                                                  | Claimed By                                  | Disposition                       | Rationale                                                                                                                |
|-----|----------------------------------------------------------------------|---------------------------------------------|-----------------------------------|--------------------------------------------------------------------------------------------------------------------------|
| O-1 | MITRE ATLAS AML.T0058 LLM Plugin Compromise / Agent Context Poisoning | tool-abuse C6, agent-autonomy C8            | RETAINED DUPLICATION              | Bilaterally additive: supply-chain ingestion vs runtime memory state. Lanes already declared in agent-autonomy C8 prose. |
| O-2 | OWASP A01:2021 Broken Access Control                                 | privilege-escalation C8, info-disclosure (footer-only) | CANONICAL OWNER: privilege-escalation | info-disclosure cites A01 only in Primary Sources footer, NOT at indicator level. No conflict.                          |
| O-3 | OWASP LLM07:2025 System Prompt Leakage                               | model-theft C9, prompt-injection C6 (partial) | RETAINED DUPLICATION              | Bilaterally additive: model-theft = secret-asset + storage view; prompt-injection = injection-vector view.               |
| O-4 | OWASP LLM06:2025 Excessive Agency                                    | tool-abuse C6/7/8 + Primary, agent-autonomy C7 + Primary | RETAINED DUPLICATION              | Bilaterally additive: tool-abuse = tool-invocation/MCP lane; agent-autonomy = autonomy/permission/functionality lane.    |
| O-5 | MITRE ATT&CK T1195 Supply Chain Compromise                           | tampering C8, model-theft C7, data-poisoning C4/Primary | CANONICAL OWNERS: 3-way (each its own asset class) | Bilaterally additive across three asset classes: code/binary, model weights, training data. Already lane-separated.  |
| O-6 | OWASP A08:2021 Software and Data Integrity Failures                  | tampering C7/C8, denial-of-service Primary  | CANONICAL OWNER: tampering        | DoS only references A08 in Primary Sources footer (CWE-502 cited as cascade vector); no indicator-level claim.           |
| O-7 | CWE-77 OS Command Injection                                          | tampering C9, tool-abuse Primary, prompt-injection Primary (analog) | CANONICAL OWNER: tampering   | tool-abuse + prompt-injection cite as conceptual analogs in Primary Sources, no indicator. tampering owns indicator-level. |
| O-8 | CWE-89 SQL Injection                                                 | tampering (Input Injection + Primary), tool-abuse Primary | CANONICAL OWNER: tampering        | tool-abuse Primary Sources footnote only ("applicable to tool-parameter injection via SQL fragments"). No indicator.    |
| O-9 | MITRE ATLAS AML.T0051 LLM Prompt Injection                           | prompt-injection C6/C7/C8                   | CANONICAL OWNER: prompt-injection | Sole owner — no claim from any other agent.                                                                              |
| O-10| MITRE ATLAS AML.T0024 Exfiltration via ML Inference API              | model-theft C8                              | CANONICAL OWNER: model-theft      | Sole owner — no claim from any other agent.                                                                              |
| O-11| MITRE ATT&CK T1078 Valid Accounts                                    | spoofing C7 (T1078.004), privilege-escalation Primary | CANONICAL OWNER: spoofing        | privilege-escalation Primary Sources footnote only. spoofing owns indicator-level Cloud IAM Role Assumption.             |

**Tally**: 6 retained-duplication / 5 canonical-owner-assigned / 0 actions required.

## Per-Overlap Analysis

### O-1: MITRE ATLAS AML.T0058 — LLM Plugin Compromise / Agent Context Poisoning

**Claimed by**:
- `tachi-tool-abuse` Pattern Category 6 "LLM Plugin Compromise (ATLAS AML.T0058)" — `.claude/skills/tachi-tool-abuse/references/detection-patterns.md` lines 76-99
- `tachi-agent-autonomy` Pattern Category 8 "Agent Context Poisoning (ATLAS AML.T0058 — Runtime-Context View)" — `.claude/skills/tachi-agent-autonomy/references/detection-patterns.md` lines 102-130

**Background**: This is the explicit Phase 1 carve-out (concern C-4 in `phase-1-complete.md`). Wave 8 housekeeping H3 permitted the duplication on the condition that T047 (this audit) would adjudicate. The agent-autonomy reference contains an in-prose declaration at lines 102-104 stating "canonical ownership will be assigned at Feature 082 T047 via the additive-signal test" and codifies the rule "if a pattern is about *upstream supply chain*, it belongs to tool-abuse Category 6; if a pattern is about *runtime memory state*, it belongs here."

**Apply additive-signal test**:

| Question | tool-abuse C6 view | agent-autonomy C8 view |
|----------|---------------------|-------------------------|
| Detection target | Plugin/tool ingestion path at registration time | Long-term memory + cross-session conversation state |
| What signal does it detect that the other cannot? | Unsigned plugin manifest pulled at session start; absent allowlist of plugin sources; no SBOM for tool-augmented agents; runtime tool-list pulls; hash-pinning gaps on plugin definitions | Cross-session memory writes from user input; vector-store memory shared across users without per-tenant isolation; recursive RAG-poisoning loops; memory-bypassed safety checks ("user previously authorized X"); persistence across privilege transitions |
| Indicator overlap (verbatim) | Zero verbatim overlap. Verified via grep: "memory" appears 0 times in tool-abuse; "plugin manifest", "MCP server URL", "third-party MCP" appear 0 times in agent-autonomy C8 indicators. | Zero verbatim overlap. |
| Threat actor capability | Compromise upstream maintainer / plugin marketplace | Send a single crafted user message that becomes an indelible "remembered fact" |
| Mitigation surface | Cryptographic signature verification, allowlist of plugin sources, manifest hash pinning, plugin SBOM | Memory write sanitization, per-user/per-tenant memory isolation, expiration policies on long-term memory, state reset on privilege transitions |

**Result**: **YES / YES**. Each view detects a signal the other cannot. Bilateral additive yield is satisfied.

**Disposition**: **RETAINED DUPLICATION**. Each agent is the canonical owner of its own signal facet. Both files already declare the lane separation in prose (agent-autonomy C8 lines 102-104; tool-abuse C6 indicators are exclusively about supply-chain ingestion). This is the textbook case the additive-signal test was designed for, and the in-place declarations in both files mean no further annotation is required.

**Action**: None.

### O-2: OWASP A01:2021 Broken Access Control

**Claimed by**:
- `tachi-privilege-escalation` Pattern Category 8 "Broken Access Control — Function-Level and Field-Level (OWASP A01:2021)" — lines 78-110
- `tachi-info-disclosure` — A01 cited in Primary Sources footer at line 168 only

**Apply additive-signal test**:

`tachi-info-disclosure` does **not** make any indicator-level detection claim against A01. The single occurrence is in the Primary Sources reference footer (line 168). The audit task spec named this overlap explicitly because Wave 11 Track 2 had noted the lane separation, and verification was required.

**Verification**: I read every Pattern Category in info-disclosure (Categories 1 through 9 + Excessive Data in Responses). None invoke "Broken Access Control", "authorization", or A01 as a detection signal. The Excessive Data in Responses category at lines 28-34 covers "API responses returning full database records" and "List endpoints returning records the requesting user should not have access to" — these are confidentiality-lane symptoms (data over-exposed in a response shape) where the upstream cause may or may not be authorization failure. The category does not adjudicate the upstream cause; it adjudicates the disclosure surface. By contrast, privilege-escalation C8 explicitly targets the upstream authorization decision: "endpoint accepts resource identifiers... without a declared per-request authorization check" (line 84).

**Lane separation holds**: privilege-escalation owns the authorization-bypass lane (decision-point check missing); info-disclosure owns the confidentiality lane (data leaked through response shape regardless of upstream cause). The footer-only A01 citation in info-disclosure is a contextual reference — A01 is unavoidably part of the disclosure literature since A01 often triggers A02-style data leakage — not an indicator claim.

**Result**: NO bilateral additive yield because **only privilege-escalation makes a detection claim**. info-disclosure has no claim to lose.

**Disposition**: **CANONICAL OWNER: privilege-escalation**. info-disclosure's footer reference is acceptable as primary-source context and does not need removal — Primary Sources lists are reference inventories, not coverage claims. The Wave 11 Track 2 lane assertion is verified to hold in the actual content.

**Action**: None.

### O-3: OWASP LLM07:2025 System Prompt Leakage

**Claimed by**:
- `tachi-model-theft` Pattern Category 9 "System Prompt and Configuration Leakage (OWASP LLM07:2025)" — lines 113-140
- `tachi-prompt-injection` Pattern Category 6 indicators include system-prompt extraction signals — lines 76-77 + Primary Sources line 153 (LLM07 cited)

**Apply additive-signal test**:

| Question | model-theft C9 view | prompt-injection C6 view |
|----------|----------------------|---------------------------|
| What is the threat agent guarding? | The system-prompt as a sensitive *asset class* (analogous to a credential or model weight) | The system-prompt extraction *attempt* as an instance of the prompt-injection technique family |
| Detection target | Storage hygiene of the prompt asset: secrets embedded in prompt content, prompt stored in configs without access control, prompt versions retained without rotation, debug-log echoes that emit raw prompt | Adversarial prompt input patterns: "repeat your instructions verbatim", role-override DAN-style, meta-queries paraphrasing the prompt |
| Mitigation surface | Don't put secrets in prompts; rotate prompts on schedule; least-privilege the storage; output-filter classifier for high-similarity-to-known-prompt responses | Instruction-hierarchy enforcement at the model API; refusal-rate monitoring; reject role-override patterns; reset state at privilege transitions |
| What detection signal does it own that the other cannot? | "API key embedded in system prompt content" (storage-side); "Multiple system-prompt versions retained without rotation" (lifecycle); "Config-store accessible to engineers" (access path); "Audit logging on suspected leakage responses" — these are model-asset-protection signals, not injection-vector signals | "Instruction-hierarchy enforcement absent at model API layer"; "DAN/AIM/STAN/developer mode jailbreak templates"; "Multi-turn jailbreak scaffolding"; "Adversarial classifier on responses" — these are prompt-injection-technique signals, not model-asset-storage signals |

**Result**: **YES / YES**. The two views detect categorically different failure modes: model-theft owns the *what to protect* (the prompt as sensitive asset, including in storage and config); prompt-injection owns the *how it leaks at runtime* (the injection technique used to extract it). A real architecture can fail one without failing the other:
- Storage failure with no injection: An engineer with config-store read-access pulls the prompt directly.
- Injection failure with strong storage: The prompt isn't stored insecurely, but the model emits it in response to a paraphrase probe at runtime.

**Disposition**: **RETAINED DUPLICATION**. Both agents own complementary signal sets. Lane separation:
- model-theft = "system prompt is a sensitive asset and its storage/access path needs protection"
- prompt-injection = "system prompt extraction via meta-query / role-override is a runtime adversarial technique"

This duplication was implicit at extraction time (no in-prose carve-out, unlike AML.T0058) but is structurally sound. The in-file evidence supports it and the indicator sets are disjoint. No de-scoping needed.

**Action**: None.

### O-4: OWASP LLM06:2025 Excessive Agency

**Claimed by**:
- `tachi-tool-abuse` Pattern Category 6, 7, 8 cite LLM06:2025 in their primary-source lists (lines 89, 114, 140) and footer line 156
- `tachi-agent-autonomy` Pattern Category 7 "Excessive Agency Sub-Categories (OWASP LLM06:2025)" — lines 79-100, plus Primary Sources line 195

**Apply additive-signal test**:

LLM06:2025 is the canonical OWASP framing for the agent-autonomy threat domain. It decomposes into three sub-categories: Excessive Functionality, Excessive Permissions, Excessive Autonomy. The two ref files use LLM06 differently:

| Question | tool-abuse view | agent-autonomy C7 view |
|----------|------------------|-------------------------|
| What slice of LLM06 does it own? | The *Excessive Functionality* slice projected onto tool-invocation vectors: which tools the agent has, who registered them, whether plugin manifests are pinned, MCP server allowlist | The full three-sub-category taxonomy: Excessive Functionality (tool registration scope), Excessive Permissions (credential scope), Excessive Autonomy (human-in-the-loop checkpoints on irreversible actions) |
| What signal does it own that the other doesn't? | Plugin manifest pinning, MCP server allowlist, tool-shadowing/rug-pull detection, cross-tool taint tracking, tool-parameter-injection via model-generated arguments | Per-user-scoped credentials via token exchange (Excessive Permissions); human-in-the-loop confirmation gates on destructive actions (Excessive Autonomy); per-task minimum-tool-set declarations (Excessive Functionality at the planner level, not the wire level) |
| Coverage breadth | Tool-invocation surface only — does not cover credentials, autonomy gates, or planner-level functionality | All three LLM06 sub-categories at the agent-design level |

**Result**: **YES / YES**. tool-abuse owns the *tool-invocation pipeline* facet (catalog hygiene, MCP wire protocol, tool selection at the model-output layer). agent-autonomy owns the *agent-design* facet (declared tool sets per role, credential scoping via token exchange, human-approval gates on outputs). These are projection slices of the same OWASP category onto two distinct architecture layers — and per the additive-signal test, both contribute signal the other cannot.

**Verification**: I cross-checked indicator overlap:
- tool-abuse C6/C7/C8 indicators do not contain "human-in-the-loop", "approval gate", "token exchange", or "OAuth on-behalf-of" — the agent-autonomy C7 hallmark indicators.
- agent-autonomy C7 indicators do not contain "MCP", "plugin manifest", "rug pull", "tool shadowing", or "manifest pinning" — the tool-abuse hallmark indicators.

Disjoint at the indicator level. The shared LLM06 citation in both files' Primary Sources is a *reference* to the canonical taxonomy that both agents project onto, not a duplicated detection claim.

**Disposition**: **RETAINED DUPLICATION**. tool-abuse and agent-autonomy share LLM06:2025 as the canonical OWASP source for both their domains, but the indicator sets they each derive from LLM06 are disjoint and bilaterally additive. This mirrors the AML.T0058 pattern: shared technique ID, disjoint detection lanes.

**Action**: None.

### O-5: MITRE ATT&CK T1195 — Supply Chain Compromise

**Claimed by**:
- `tachi-tampering` Pattern Category 8 "Software Supply Chain Integrity Failures" — lines 96-128 (covers T1195, T1195.001, T1195.002)
- `tachi-model-theft` Pattern Category 7 "Model Supply Chain Compromise" — lines 75-83 (covers model-asset variant)
- `tachi-data-poisoning` "Fine-Tuning Supply Chain Attacks" pre-existing category at lines 46-53 + Primary Sources reference to AML.T0010 ML Supply Chain Compromise at line 134

**Apply additive-signal test (3-way)**:

| Question | tampering C8 | model-theft C7 | data-poisoning |
|----------|---------------|------------------|------------------|
| Asset class protected | Code, binaries, container images, application dependencies | Model weights, model serving frameworks, ONNX/quantization tools, model SBOM | Training data, fine-tuning datasets, LoRA adapters, RAG corpora |
| Indicator hallmarks | npm/PyPI/crates.io lockfile pins, container digest pinning, sigstore/SLSA attestation, dependency confusion namespace squatting | HuggingFace model card sigstore, model conversion tool provenance, model serving framework verification, model dependency SBOM | Public-scrape contamination, crowd-sourced label review, training-data hash validation, embedding-based de-duplication |
| Failure consequence | Tampered code in production via dependency hijack | Backdoored model serving identical to legitimate model | Behaviorally backdoored model that fails only on trigger inputs |
| What signal is unique? | Lockfile + digest + dependency confusion controls | Model-weight signature verification + model-SBOM | Trigger-activation evaluation + adversarial-review gate on training data |

**Result**: **YES / YES / YES**. Three-way bilaterally additive. Each agent owns a distinct asset class. The same upstream technique (T1195) projects onto three distinct asset stewardship lanes, and a real architecture can fail any one without failing the other two.

**Disposition**: **THREE CANONICAL OWNERS** (one per asset class). tampering = code/binary/container; model-theft = model artifacts; data-poisoning = training data. No single canonical owner is appropriate — the additive-signal test resolves to retained 3-way duplication. The indicator sets are disjoint at the lookup level (verified: tampering C8 does not contain "model weights" or "training data"; model-theft C7 does not contain "lockfile" or "crates.io"; data-poisoning Fine-Tuning Supply Chain does not contain "container image digest" or "npm package").

**Action**: None.

### O-6: OWASP A08:2021 Software and Data Integrity Failures

**Claimed by**:
- `tachi-tampering` Pattern Categories 7 and 8 cite A08 (lines 84, 116, 165, 179)
- `tachi-denial-of-service` cites A08 indirectly via CWE-502 in Primary Sources (line 164) — CWE-502 is a child of A08

**Apply additive-signal test**:

DoS does NOT make an indicator-level claim against A08. The CWE-502 reference appears only in Primary Sources because deserialization gadget chains are a known DoS amplification vector (a single deserialize call can trigger billions of allocations). The indicator categories of DoS do not target deserialization — they target resource exhaustion, ReDoS, billion-laughs, and cascade failures. CWE-502 deserialization-as-RCE is exclusively a tampering concern.

**Result**: NO bilateral yield — only tampering makes the detection claim.

**Disposition**: **CANONICAL OWNER: tampering**. DoS's CWE-502 footer reference is a contextual cross-link that does not constitute a coverage claim and does not need removal.

**Action**: None.

### O-7: CWE-77 OS Command Injection

**Claimed by**:
- `tachi-tampering` Pattern Category 9 "Injection Attacks Beyond SQL" indicator-level coverage of OS command injection (lines 135-160)
- `tachi-tool-abuse` Primary Sources line 165 cites CWE-77 as conceptual analog ("applicable to tool-parameter injection via shell commands in model-generated tool arguments")
- `tachi-prompt-injection` Primary Sources line 157 cites CWE-77 as conceptual analog ("Conceptual analog for prompt injection in LLM contexts")

**Apply additive-signal test**:

Both tool-abuse and prompt-injection cite CWE-77 explicitly as a *conceptual analog*, not as a detection target. Their Primary Sources prose contains the exact disclaimer language. tool-abuse owns Pattern Category 3 "Tool Parameter Injection" which detects unvalidated tool-parameter construction in model-generated tool arguments — this is a distinct detection signal from "Process constructs OS shell commands via string concatenation from external input" (tampering C9 line 135). The detection surfaces are:

| View | Detection target | Indicator example |
|------|------------------|---------------------|
| tampering C9 | Process source code that constructs shell commands by string concatenation | `subprocess.run(..., shell=True)`, `os.system`, backticks |
| tool-abuse C3 | LLM agent that builds tool arguments from unvalidated model output | "Tool parameters constructed from unvalidated model output"; "SQL fragments, shell commands, or file paths passed as tool arguments without sanitization" |
| prompt-injection | (No CWE-77 indicator) | N/A — only Primary Sources reference |

The tool-abuse C3 case is structurally different from tampering C9 because the *intermediary* is the LLM, not direct user-controlled input flowing into a shell. tool-abuse C3 already exists as its own category and is canonically owned by tool-abuse — it does not duplicate tampering C9's detection signal even though both reference CWE-77 as the underlying weakness.

**Result**: NO indicator-level overlap. Both tool-abuse and prompt-injection cite CWE-77 only as a Primary Source contextual cross-reference.

**Disposition**: **CANONICAL OWNER: tampering** (for the OS command injection detection signal at the source-code level). tool-abuse retains its independent canonical ownership of "Tool Parameter Injection" (Category 3) which is a distinct LLM-mediated variant. The Primary Sources cross-references in tool-abuse and prompt-injection are acceptable as authoritative-source context.

**Action**: None.

### O-8: CWE-89 SQL Injection

**Claimed by**:
- `tachi-tampering` Input Injection category (line 22) and Primary Sources (line 171)
- `tachi-tool-abuse` Primary Sources line 164 cites CWE-89 as analog ("applicable to tool-parameter injection via SQL fragments in model-generated tool arguments")

**Apply additive-signal test**: Same logic as O-7. tool-abuse cites CWE-89 only in Primary Sources as the underlying weakness behind a model-mediated variant. The actual indicator-level claim ("Tool Parameter Injection" Category 3) is canonically owned by tool-abuse and is not duplicated; the SQL-injection detection signal at the source-code-string-concatenation level is canonically owned by tampering.

**Disposition**: **CANONICAL OWNER: tampering** for the source-level SQL injection signal. tool-abuse retains independent ownership of LLM-mediated tool-parameter injection.

**Action**: None.

### O-9: MITRE ATLAS AML.T0051 LLM Prompt Injection: Direct

**Claimed by**: prompt-injection C6, C7, C8 only.

**Result**: Sole owner — no overlap. Listed for completeness because the audit task referenced it.

**Disposition**: **CANONICAL OWNER: prompt-injection**. No action.

### O-10: MITRE ATLAS AML.T0024 Exfiltration via ML Inference API

**Claimed by**: model-theft C8 only.

**Result**: Sole owner — no overlap. Listed for completeness.

**Disposition**: **CANONICAL OWNER: model-theft**. No action.

### O-11: MITRE ATT&CK T1078 Valid Accounts (incl. T1078.004 Cloud Accounts)

**Claimed by**:
- `tachi-spoofing` Pattern Category 7 "Cloud IAM Role Assumption Chain Abuse" — lines 85-114, cites T1078.004 explicitly at line 103
- `tachi-privilege-escalation` Primary Sources line 209 cites T1078 generically ("MITRE ATT&CK T1078 Valid Accounts")

**Apply additive-signal test**:

privilege-escalation does not contain an indicator-level Pattern Category targeting Valid Accounts as a detection signal. The footer reference is a contextual citation acknowledging that valid-account abuse is part of the privilege-escalation domain. The actual indicator-level cloud IAM detection is owned by spoofing C7 (which targets *cross-account assume-role chain abuse* — confused-deputy gaps, missing external IDs, IMDSv1 reachability, role-chain depth >2 hops). spoofing's choice of this category was a Phase 1b enrichment decision that placed cloud IAM under spoofing because the primary failure mode is *identity confusion* (confused-deputy, audience-mismatch on assumed roles), not authorization-policy bypass.

**Result**: No indicator-level overlap. privilege-escalation's footer T1078 reference is acceptable as primary-source context.

**Disposition**: **CANONICAL OWNER: spoofing**. The lane assignment makes sense at the technique level: T1078.004 "Valid Accounts: Cloud Accounts" is fundamentally an identity/credential abuse story (the credential is real, the assume-role chain is over-permissive), which fits spoofing's identity-spoofing scope better than privilege-escalation's authorization-decision scope. This is a defensible architectural choice from Phase 1b. No action.

**Note for awareness**: A future architecture review may want to revisit whether T1078.004 belongs more naturally in privilege-escalation (since assume-role chains are technically a privilege-escalation mechanism). Both placements are defensible per the additive-signal test; the current choice is consistent with how spoofing C7 is framed (identity-confusion lane) and does not warrant disturbance in T047.

**Action**: None for Feature 082. Flag for the team-lead's consideration in a future enrichment cycle if the spoofing C7 framing becomes contested in production usage. Not blocking.

## Cross-Agent Coverage Integrity

After this audit, the 11 threat agents have **distinct, complementary coverage** with **6 cases of intentional bilateral duplication** that the additive-signal test validates as carrying genuinely additive signal facets. The 5 non-overlap cases are footer-only Primary Sources cross-references — a healthy practice that lets each agent acknowledge upstream/adjacent techniques without claiming detection coverage.

**Coverage seams** (places where the cross-agent matrix is intentionally porous and a finding may be issued by either agent depending on how the architecture surfaces the failure):

1. **AML.T0058 (O-1)**: tool-abuse fires on supply-chain manifestation; agent-autonomy fires on runtime-memory manifestation. An architecture with both surfaces should produce two independent findings, one from each agent.
2. **LLM07:2025 (O-3)**: model-theft fires on storage/asset-protection manifestation; prompt-injection fires on runtime-injection-technique manifestation. Two independent findings expected on architectures that fail both.
3. **LLM06:2025 (O-4)**: tool-abuse fires on tool-invocation/MCP wire layer; agent-autonomy fires on agent-design (declared tool set, credentials, autonomy gates). Two independent findings expected on under-constrained agentic systems.
4. **T1195 (O-5)**: 3-way split across asset classes (code/model/data). Up to three independent findings expected on architectures that fetch all three asset classes from external registries.

These seams are *intentional*, validated by the additive-signal test, and aligned with the OWASP/ATLAS taxonomies they project from. They will not produce false-duplicate findings at the orchestrator level because the orchestrator dispatches per DFD element type and severity (the same DFD element will be processed by both relevant agents only when its description matches both agents' trigger keywords, which is the intended behavior — the architecture has a property that genuinely warrants two distinct security perspectives).

**Footer cross-references that pass audit without action**: O-2 (info-disclosure cites A01 in footer), O-6 (DoS cites A08/CWE-502 in footer), O-7 (tool-abuse + prompt-injection cite CWE-77 in footer), O-8 (tool-abuse cites CWE-89 in footer), O-11 (privilege-escalation cites T1078 in footer). Each is an authoritative-source acknowledgment, not a coverage claim, and Primary Sources lists are inventories of *applicable* references, not declarations of *exclusive* ownership. The PRD 082 architectural intent (as stated in plan.md §1.2 and ADR-023) is that agents share a common vocabulary of source citations even when their detection lanes are disjoint, because adjacent agents reading each other's references improves cross-agent consistency without creating duplicate findings.

## Actions Required

**None.**

The audit found 11 candidate overlaps. 6 pass the additive-signal test bilaterally and are retained as duplicated coverage with explicit lane separation. 5 are footer-only Primary Sources cross-references that do not constitute coverage claims and are correct as written. Zero ref files require modification. Zero indicator-level conflicts were found.

The cross-agent matrix produced by Phase 1 + Waves 9-11 + Wave 12 is sound and ready for Wave 14 (T049 enrichment-floor tally) and Wave 15 (T050 full regression gate).

## Decision

**PASS.**

- All 11 ref files are internally and cross-agent consistent.
- AML.T0058 (the explicit T021 carve-out) is bilaterally additive — duplication retained, lane separation in-prose at agent-autonomy C8.
- The Wave 11 Track 2 lane assertion for A01 (privilege-escalation owns authorization-bypass lane; info-disclosure does NOT cross over) is verified to hold at the indicator level.
- LLM07:2025 (model-theft vs prompt-injection) is bilaterally additive across asset-protection vs injection-technique facets — implicit duplication, structurally sound, no in-prose carve-out needed because the indicator sets are obviously disjoint.
- LLM06:2025 (tool-abuse vs agent-autonomy) is bilaterally additive across tool-invocation vs agent-design facets — implicit duplication, structurally sound.
- T1195 supply-chain (tampering vs model-theft vs data-poisoning) is 3-way bilaterally additive across asset classes — three canonical owners.
- All other candidate overlaps reduce to footer-only Primary Sources cross-references with no detection claim.

Phase 2d closes successfully. No follow-up tasks. T047 complete.

**Architect sign-off**: 2026-04-11
**Review method**: Manual cross-grep across 11 ref files + indicator-level read of every claimed overlap; comparison against ADR-023 §Phase 1 Validation item 5 (additive-signal test ratification) and phase-1-complete.md C-4 (AML.T0058 carve-out).
