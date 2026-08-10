# Gap Analysis: 2026 Scope Absorptions vs. Existing Detection (F-362)

**Task**: T018 [US3] · **Date**: 2026-08-10 · **Analyst**: security-analyst (MANUAL-ONLY, analyst judgment)
**Spec authority**: [spec.md](spec.md) §Movement Map, FR-003, FR-004, US-3 AC-1 · **Schema**: [data-model.md](data-model.md) §7
**Scope rule (FR-003)**: assess what **exists**. New detections are out of scope — every gap is recorded here for follow-up filing, never designed in-loop.

## Partial-downgrade signal

> **NO Partial downgrade. All four absorbed sub-classes are covered by existing detections.**
> LLM01:2026, LLM04:2026, LLM05:2026 and LLM10:2026 each retain a **Covered** verdict on 2026 definitions.
> Consequence for T019/T021: the coverage headline is **not** moved by the absorptions, and no restatement surface (`README.md` ×5, `.claude/rules/scope.md`, developer guide, system-design README) changes on account of this analysis. The B-close risk gate for a downgrade cascade is **clear**.
>
> Two **non-blocking** follow-up issues are proposed below (§Follow-ups) — one detection-robustness (persona↔catalog enumeration parity), one documentation (LLM10 scope-boundary note). Neither is a coverage gap; neither blocks T019, T020 or T021. Both are recorded for **T026(c)** filing, not filed here.

## Evidence-base commit context

| Item | Value |
|---|---|
| Branch | `362-remap-owasp-llm-top10-2026` |
| HEAD at analysis | `b59f0f3` (`docs(362): NEXT-SESSION handoff — waves A4-A6 done (Phase 2 complete), resume at Wave B1`) |
| Evidence surfaces read | `.claude/agents/tachi/{prompt-injection,data-poisoning,model-theft,output-integrity,agent-autonomy}.md`; `.claude/skills/tachi-{prompt-injection,data-poisoning,model-theft,output-integrity,agent-autonomy,tool-abuse}/references/detection-patterns.md` |
| Mid-edit caveat | Sibling lanes are concurrently re-keying OWASP **code labels** (2025→2026) in these same files; pattern **content** is unchanged. All evidence below is therefore cited by **pattern name / catalog section**, never by line number, and all categories are named by 2026 code + name. Observed label state was ignored as an analysis input. |

## Method and evidence bar

The same anti-drift bar the crosswalk disposition work (T007) applied: **if the coverage cannot be articulated in one sentence tying a named pattern to the absorbed sub-class, it is not covered.** Each record below states that sentence explicitly. Where an absorbed sub-class has a facet that no existing pattern reaches, the facet is named in the record's **Residual** row rather than absorbed into the verdict — an honest Partial is acceptable, a suppressed one is not (SC-005).

Host-agent assignment follows [data-model.md](data-model.md) §2, including the P1 ruling (2026-08-09) that `tachi-tampering` carries no LLM attestation and must **not** be cited for LLM04:2026.

## Summary

| # | Absorbed sub-class | 2026 category | Covered / Gap | Verdict impact |
|---|---|---|---|---|
| 1 | Cross-modal (image/audio) injection | **LLM01:2026** Prompt Injection | **Covered** (robustness caveat R-1) | none |
| 2 | Model-artifact authenticity | **LLM04:2026** Supply Chain | **Covered** | none |
| 3 | Fine-tuning subversion | **LLM05:2026** Data and Model Poisoning | **Covered** | none |
| 4 | Insecure generated code at scale | **LLM10:2026** Improper Output Handling | **Covered** at architecture level (scoped residual R-2) | none |

---

## Record 1 — Cross-modal (image/audio) injection → LLM01:2026 Prompt Injection

**Host agent**: `tachi-prompt-injection` (persona `.claude/agents/tachi/prompt-injection.md`; catalog `.claude/skills/tachi-prompt-injection/references/detection-patterns.md`)

**Existing-detection evidence**:

1. **Pattern Category 7 — "Indirect Injection via Poisoned External Sources"** carries the indicator *"Multimodal inputs (images with embedded OCR text, audio with spoken instructions, video with caption injection) bypassing text-only content filters"*, alongside the hidden-text/low-salience vectors for each ingestion channel.
2. **Pattern Category 8 — "Evasion via Encoding and Obfuscation (Base64, Unicode, Multimodal)"** is titled for the modality axis and carries the indicator *"Multimodal smuggling: image-based OCR payloads (text rendered as pixels), audio transcription payloads (spoken instructions), video-caption injection"*, with a matching mitigation — *"Apply OCR-based text extraction to image inputs and transcription-based text extraction to audio inputs, then feed extracted text through the same content filter as native text"* — and a refusal-rate-parity-across-modalities control.

**One-sentence coverage justification**: The prompt-injection catalog already names image-OCR and audio-transcription payloads as first-class injection channels in two distinct pattern categories, detects the exact architectural tell (a text-only input filter sitting in front of a model that ingests non-text modalities), and prescribes modality-specific extraction-then-filter mitigations — which is precisely the sub-class LLM01:2026 absorbs.

**Residual / caveat (R-1, robustness — not a coverage gap)**: The cross-modal evidence lives **only** in Pattern Categories 7 and 8, and the `tachi-prompt-injection` persona never names those categories: its Purpose enumerates five patterns and its Detection Workflow step 1 instructs the agent to load *"the five pattern categories (Direct Prompt Injection, Indirect Prompt Injection, Jailbreaking, System Prompt Extraction, Cross-Plugin Injection)"* while the catalog carries **eight**. The content is still reachable at runtime — the `**MANDATORY**: Read` directive loads the whole catalog and workflow step 3 says "walk through the pattern categories" generically — so this is an anchoring risk, not an absence. Secondary note: the catalog's trigger-keyword list carries no modality terms (`image`, `vision`, `audio`, `speech`, `multimodal`), so activation on a cross-modal architecture depends on the LLM Process itself matching `model` / `LLM` / `inference` / `prompt`. Both points are folded into proposed issue **FU-1**.

**Verdict impact**: **none.** LLM01:2026 holds **Covered**.

---

## Record 2 — Model-artifact authenticity → LLM04:2026 Supply Chain

**Host agents**: `tachi-model-theft` + `tachi-data-poisoning` (supply-chain tier per data-model §2). `tachi-tampering` is explicitly **not** cited (P1 ruling 2026-08-09).

**Existing-detection evidence** (LLM-tier patterns cited first so the verdict does not rest on predictive-ML-only surfaces):

1. **`model-theft` Pattern Category 7 — "Model Supply Chain Compromise"** (LLM-tier): *"Base models or pretrained checkpoints downloaded from public registries without cryptographic signature verification"*; *"CI/CD pipelines for model deployment that lack artifact integrity checks between build and deploy stages"*; absence of an SBOM for model inference dependencies.
2. **`data-poisoning` "Fine-Tuning Supply Chain Attacks"** (LLM-tier, pre-existing category): *"Models loaded from public registries (Hugging Face, model zoos) without signature verification"*; *"No model integrity verification (hash comparison) between download and deployment"*; LoRA/PEFT modules from untrusted contributors.
3. **`data-poisoning` Pattern Category 7 — "Backdoor Triggers in Training and Fine-Tuning Data"**: *"Model weights, LoRA adapters, or PEFT modules pulled from third-party hub (HuggingFace, Civitai, ModelScope) without checksum, sigstore, or signature verification"*.
4. **`model-theft` Pattern Category 14 — "Predictive-ML Artifact Supply Chain (Model Registry, Weight Tampering)"** (predictive-ML tier, strongest explicit statement of the sub-class): *"Model-signing or attestation policy is missing — there is no Sigstore-style cryptographic attestation, no KMS-backed signature, and no SLSA provenance attached to promoted model artifacts"*; *"Integrity verification at model-load time is absent — the inference service loads weight files from artifact storage without verifying signature, hash, or attestation before initializing the model"*; mutable weight storage; permissive promotion IAM.
5. **`data-poisoning` Pattern Category 10 — "Predictive-ML Supply Chain Completeness"** covers the disjoint corpus-side facet (dataset checksum manifest, feature-store write-audit, registry promotion gate) per the ADR-035 D-4 two-facet carve.

**One-sentence coverage justification**: Model-artifact authenticity — is this weight file the artifact its publisher signed, and is that checked before it is loaded? — is detected by four existing pattern categories across two agents that test for signature/attestation/hash verification at download, at registry promotion, and at model-load time, on both LLM-serving and predictive-ML topologies.

**Residual / caveat**: none material. Coverage is deeper than the absorption requires: the artifact-side (`model-theft` Cat 14) and corpus-side (`data-poisoning` Cat 10) facets are deliberately disjoint by architectural tell, so a single architecture surfaces both without duplication.

**Verdict impact**: **none.** LLM04:2026 holds **Covered**. Corroborating signal from T007: crosswalk ledger row 13 records that *"2026's +model-artifact-authenticity delta directly strengthens this mapping"* for the CWE-494 (Download of Code Without Integrity Check) edge now keyed to LLM04:2026.

---

## Record 3 — Fine-tuning subversion → LLM05:2026 Data and Model Poisoning

**Host agent**: `tachi-data-poisoning` (persona Purpose already states that *"contaminated fine-tuning datasets embed persistent backdoors that activate on specific trigger inputs"*).

**Existing-detection evidence**:

1. **Pattern Category 7 — "Backdoor Triggers in Training and Fine-Tuning Data"** is the direct hit: indicators include *"DFD element fine-tunes or continues pretraining on data sourced from public internet scrape or user-contributable corpora without adversarial-review gate"*, RLHF/preference data without a human-review bottleneck, *"No declared evaluation for trigger-activation behaviors (trigger discovery, backdoor scanning tools like ABS, Neural Cleanse, STRIP)"*, and *"Fine-tuning checkpoints are not compared against a clean base model for behavioral divergence on held-out inputs"* — the last of which is also the detector for **alignment/guardrail erosion** introduced through otherwise-benign fine-tuning. Its worked example is a coding assistant whose fine-tune corpus carries trigger-phrase backdoors that survive standard evaluation.
2. **"Training Data Manipulation"** and **"Fine-Tuning Supply Chain Attacks"** (pre-existing categories): fine-tuning pipelines pulling from mutable shared storage without snapshot isolation; no checksum validation between collection and use; shared fine-tuning infrastructure where multiple teams can overwrite model artifacts.
3. **Pattern Category 8 — "Transfer Learning Supply Chain (Predictive ML)"**: the fine-tuning-load surface — no `revision=` SHA pinning, no SHA-256 digest comparison, no Sigstore attestation check at load time, LoRA/PEFT merged without attestation, missing model-card provenance gate.
4. **Pattern Category 9 — "Feedback-Loop Model Skewing"** covers the retraining-loopback variant (production inference data re-entering the fine-tune/retrain path without drift detection or labeler-trust scoring).
5. Persona-level worked example **"Fine-Tuning Data Manipulation via Shared Storage"** demonstrates the emitted-finding shape for this sub-class.

**One-sentence coverage justification**: Fine-tuning subversion in all three of its forms — poisoned fine-tune corpus, tampered adapter/checkpoint at load, and behavioural divergence from the clean base after tuning — is detected by four existing `data-poisoning` pattern categories whose indicators name the fine-tuning step explicitly and whose mitigations prescribe backdoor scanning, clean-base divergence comparison, and signed-adapter policy.

**Residual / caveat**: none material.

**Verdict impact**: **none.** LLM05:2026 holds **Covered**.

---

## Record 4 — Insecure generated code at scale → LLM10:2026 Improper Output Handling

**Host agent**: `tachi-output-integrity` (ADR-030/045 lineage).

**Existing-detection evidence**:

1. **Pattern Category 2 — "Server-Side Execution Sinks (SQLi / OS Command / Code Injection)"** carries the core indicator *"Code evaluators (`eval`, `exec`, `Function()`, `vm.runInContext`, `subprocess` with `shell=True`) invoked on model output"* plus shell-command construction from model output.
2. **Pattern Category 2's dedicated sub-example — "Package-Manager / CI-Workflow Injection (AI Coding Assistant)"** is the on-point surface: an LLM Process emits an install script or GitHub Actions workflow that a CI runner or developer machine executes without validation. It ships extended trigger keywords (`npm install`, `pip install`, `apt install`, `brew install`, `gh workflow`, `actions/`, `uses:`, `package-lock`, `requirements.txt`), a 2026 incident record establishing the **scale** dimension (SANDWORM_MODE self-propagating npm worm — 170+ packages / 404 malicious versions in a day; the LiteLLM PyPI compromise; Agentic Workflow Injection), and three named mitigations (registry/scope allowlist, microVM/gVisor sandbox isolation, Sigstore-backed signature verification).
3. The both-keyword-AND-sink-indicator activation rule keeps this precise rather than speculative: a prose mention of `npm install` outside an execution-sink context does not fire the agent.

**One-sentence coverage justification**: `output-integrity` Pattern Category 2 and its AI-coding-assistant sub-example detect LLM-emitted code, install commands and CI workflow steps flowing into an executor without registry allowlisting, sandbox isolation or signature verification — the architecture-level form of insecure generated code reaching production at scale, including the hallucinated-dependency (slopsquatting) vector.

**Residual (R-2, scoped out by an existing published anti-claim — not a new gap)**: One facet of the phrase "insecure generated code at scale" is **not** detected by tachi and by design cannot be: the *semantic quality of the generated source itself* (an AI-authored handler containing SQL injection, a hardcoded credential, or weak crypto) committed into the adopter's repository at volume. No pattern category in any tachi catalog performs source-content analysis (confirmed by sweep across all tachi skill reference catalogs: zero SAST and zero static-analysis patterns; the single "secret scanning" occurrence is a mitigation recommendation in `info-disclosure`, not a detection pattern), and this is already fenced by two published anti-claims — `docs/standards/OWASP_COVERAGE.md` §Anti-claims ("Application-source-code SAST replacement") and `.claude/rules/scope.md` ("NOT a SAST/SCA replacement"). The nearest architectural neighbour is `agent-autonomy` Pattern Category 7's *Excessive Autonomy* indicator, which names *"No declared human-in-the-loop gate for irreversible actions (send, delete, publish, transfer, **merge**, **deploy**)"* — but that fires on the autonomy axis and attributes to **LLM03:2026 Excessive Agency**, not LLM10:2026, so it is recorded here as an adjacency, **not** claimed as LLM10 evidence. Because the residual sits entirely inside an already-published anti-claim, it does not make the LLM10:2026 verdict Partial; it makes the LLM10 row's scope boundary worth stating explicitly (proposed issue **FU-2**).

**Verdict impact**: **none.** LLM10:2026 holds **Covered** (architecture-level detection; content-level analysis remains a documented anti-claim). Corroborating signal from T007: crosswalk ledger row 52 records that *"2026's +insecure-generated-code-at-scale delta directly strengthens this mapping"* for the MITRE ATLAS AML.T0060 (Publish Hallucinated Entities) edge now keyed to LLM10:2026.

---

## Follow-ups — RECORDED for T026(c) filing, NOT filed here

Per the FR-003 handling rule and the task's pre-authorized absorption, the proposed issues are written inline below. Neither is a coverage gap; neither blocks T019/T020/T021.

### FU-1 (detection robustness, priority: medium)

**Title**: `Persona↔catalog pattern-category enumeration parity for tachi threat agents`

**Body**: Several tachi agent personas enumerate a stale pattern-category count in their Detection Workflow, understating the catalog they are mandated to load: `prompt-injection` names five categories in both Purpose and workflow step 1 while its catalog carries eight (Cats 6–8 include the only cross-modal image/audio injection coverage in the repo); `output-integrity` names five in Purpose, workflow step 1 and its Skill References row — and the catalog's own Overview also says five — while the catalog carries six (Cat 6 Vector/Search-DSL Injection); `model-theft` workflow step 2 enumerates nine while the catalog carries fourteen; `data-poisoning` workflow step 2 enumerates seven while the catalog carries ten (its Purpose does name 8–10). The pattern content is reachable — the `**MANDATORY**: Read` directive loads the full catalog and the workflow says "walk through the pattern categories" — so this is an anchoring/drift risk rather than missing detection, surfaced by the F-362 T018 gap analysis when the LLM01:2026 cross-modal evidence was found to live exclusively in two categories the persona never names. Proposed fix: make the persona enumerations catalog-derived or count-free, and consider adding modality trigger keywords (`image`, `vision`, `audio`, `speech`, `multimodal`) to the prompt-injection catalog. Related: F-362 `specs/362-remap-owasp-llm-top10-2026/gap-analysis.md` Record 1 (R-1).

### FU-2 (documentation, priority: low)

**Title**: `State the LLM10:2026 generated-code scope boundary explicitly in OWASP_COVERAGE.md`

**Body**: The 2026 edition's LLM10 Improper Output Handling spans "insecure generated code at scale". Tachi covers the architecture-level facet (LLM-emitted code, install commands and CI workflow steps reaching an executor without allowlisting, sandboxing or signature verification — `output-integrity` Pattern Category 2 and its AI-coding-assistant sub-example) but not the source-content facet (vulnerabilities inside AI-authored application code), which is already fenced by the existing "Application-source-code SAST replacement" anti-claim in `docs/standards/OWASP_COVERAGE.md` and the "NOT a SAST/SCA replacement" statement in `.claude/rules/scope.md`. Proposed change is documentation-only: make the boundary explicit at the LLM10 row / anti-claims section so adopters reading the 2026 category name do not infer generated-code static analysis. No detection work and no coverage-count change is implied. Related: F-362 `specs/362-remap-owasp-llm-top10-2026/gap-analysis.md` Record 4 (R-2).

## Downstream consequences

| Consumer | Consequence |
|---|---|
| **T019** (coverage re-derivation + `OWASP_COVERAGE.md`) | All four absorption-affected rows carry **Covered** with the evidence citations above. No Partial row, so no `issue #NNN` annotation is required in the verdict model (data-model §6). LLM10's row may optionally carry the FU-2 boundary note once filed. |
| **T020** (D5 consistency test) | Unaffected — the test asserts edition-token parity, not verdict content. |
| **T021** (restatement sweep) | **No coverage-count change.** README ×5 (including the `:7` poster alt-text / poster-image disposition), `.claude/rules/scope.md:24`, developer guide, and `docs/architecture/01_system_design/README.md:130` are **no-ops with respect to this analysis** — the PM W3 regenerate-or-annotate branch for a downgrade is not triggered, and no triad-visible governance edit to `.claude/rules/scope.md` arises from FR-003. |
| **T026(c)** | File FU-1 and FU-2 as written above. |
| **SC-005** | Satisfied: every verdict carries 2026-definition detection evidence; the two residuals (R-1 robustness, R-2 anti-claim-fenced facet) are published here rather than suppressed. |
