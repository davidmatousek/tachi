# OWASP Five-Framework Coverage Matrix (50/50)

Canonical reference for tachi's OWASP coverage claim. Composed from
`schemas/taxonomy/owasp.yaml` + ADR-024 → ADR-037 + ADR-045 lineage.

## Headline

**OWASP five-framework total: 50/50 Covered** (LLM 2026 10/10 + Agentic 2026
10/10 + ML 2023 10/10 + Mobile 2024 10/10 + Web/API 2021/2023 10/10).

The schema (`schemas/taxonomy/owasp.yaml`) carries **6 framework buckets ×
10 items = 60 records**. The "five-framework" headline compresses Web Top
10:2021 (A01–A10) and API Security Top 10:2023 (API1–API10) into one
narrative slot per ADR-037 D-2.

## Matrix

| Framework | Bucket | Items | Status | OWASP Anchor | Detection ADRs |
|---|---|---|---|---|---|
| LLM 2026 | OWASP-LLM-2026 | LLM01–LLM10 | 10/10 | https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/ | ADR-030, ADR-031, ADR-034, ADR-045 |
| Agentic 2026 | OWASP-AGENTIC-2026 | ASI01–ASI10 | 10/10 | https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/ | ADR-032, ADR-033 + pre-BLP-01 |
| ML 2023 | OWASP-ML-2023 | ML01–ML10 | 10/10 | https://owasp.org/www-project-machine-learning-security-top-10/ | ADR-035 |
| Mobile 2024 | OWASP-MOBILE-2024 | M1–M10 | 10/10 | https://owasp.org/www-project-mobile-top-10/ | ADR-036 |
| Web 2021 | OWASP-2021 | A01–A10 | 10/10 | https://owasp.org/Top10/ | ADR-037 |
| API 2023 | OWASP-API-2023 | API1–API10 | 10/10 | https://owasp.org/API-Security/ | ADR-037 |

**Per-bucket total: 60/60.** **Headline framing: 5 slots × 10 items = 50/50** (Web + API combined).

## LLM 2026 Category Verdicts

Re-derived 2026-08-10 (F-362 T019) against the 2026 category definitions —
no verdict is carried forward from the 2025 edition. Verdict model:
`Covered(evidence: agent + pattern category)` |
`Partial(gap: <absorbed sub-class>, issue #NNN)` (`data-model.md` §6, F-362).
Four categories (LLM01, LLM04, LLM05, LLM10) absorb 2026-only sub-classes;
their full evidence is recorded in the F-362 gap analysis
(`specs/362-remap-owasp-llm-top10-2026/gap-analysis.md`) and is summarized
below.

**Editorial note on the Matrix row's Detection ADRs**: ADR-030, ADR-031,
ADR-034, and ADR-045 are immutable historical records — each was accepted
while asserting a 2025-edition OWASP LLM code, and F-362 does not edit them.
Their lineage re-keys under the 2026 permutation (each 2025 category kept
its name and moved to a new number): **ADR-030/045 → LLM10:2026**
(`output-integrity` net-new-agent closure + same-agent enrichment; both
cite the Improper Output Handling category, numbered differently pre- and
post-remap); **ADR-031 → LLM07:2026** (`misinformation` net-new-agent
closure; cites the Misinformation category, numbered differently
pre- and post-remap); **ADR-034 → LLM06:2026** (`denial-of-service` +
`model-theft` dual-agent closure; cites the Unbounded Consumption category,
numbered differently pre- and post-remap). Read each ADR's cited code
through this lineage, not literally.

| 2026 ID | Category (2026 name) | Verdict | Evidence (agent + pattern category) |
|---|---|---|---|
| LLM01 | Prompt Injection | **Covered** | `tachi-prompt-injection` Pattern Categories 1–8 (Direct/Indirect Injection, Jailbreaking, System Prompt Extraction, Cross-Plugin Injection, Evolved Direct-Injection/Jailbreak Variants, **Indirect Injection via Poisoned External Sources** incl. cross-modal image/audio/video payloads, Evasion via Encoding/Obfuscation incl. multimodal smuggling) — cross-modal-injection absorption; gap-analysis Record 1 |
| LLM02 | Sensitive Information Disclosure | **Covered** | `tachi-info-disclosure` Pattern Categories 1–10 (error-message exposure, excessive data in responses, data at rest/in-transit exposure, side-channel leakage, debug/diagnostic exposure, SSRF to cloud metadata, information-repository data staging) on LLM-serving processes and prompt-context stores |
| LLM03 | Excessive Agency | **Covered** | `tachi-tool-abuse` Pattern Category 7 (per-request instruction-hijack invocation of an authorized-but-wrong-scope tool) + `tachi-agent-autonomy` Pattern Category 7 (Excessive Functionality / Excessive Permissions / Excessive Autonomy sub-categories) and Pattern Category 8 (agent context / memory poisoning — the memory and persistent-state subsection) |
| LLM04 | Supply Chain | **Covered** | `tachi-model-theft` Pattern Category 7 (Model Supply Chain Compromise) + `tachi-data-poisoning` "Fine-Tuning Supply Chain Attacks" / Pattern Category 7 (third-party-hub provenance sub-indicator) — model-artifact-authenticity absorption; full evidence in gap-analysis Record 2 |
| LLM05 | Data and Model Poisoning | **Covered** | `tachi-data-poisoning` Pattern Category 7 (Backdoor Triggers in Training and Fine-Tuning Data) + Training Data Manipulation + Fine-Tuning Supply Chain Attacks + Pattern Category 8 (Transfer Learning Supply Chain) + Pattern Category 9 (Feedback-Loop Model Skewing) — fine-tuning-subversion absorption; full evidence in gap-analysis Record 3 |
| LLM06 | Unbounded Consumption | **Covered** | `tachi-denial-of-service` Pattern Category 12 (LLM Inference-Request Flooding and Token Exhaustion) + Pattern Category 13 (Context-Window Exhaustion, Vector A / latency-driven) + `tachi-model-theft` Pattern Category 6 (Unbounded Inference Consumption) + Pattern Category 10 (Cost Amplification) + Pattern Category 11 (Denial-of-Wallet, Vector B / cost-driven) — ADR-034 dual-agent closure |
| LLM07 | Misinformation | **Covered** | `tachi-misinformation` Pattern Categories 1–5 (Ungrounded Factual Emission, Citation Fabrication, Overreliance / Missing HITL, Retrieval-Grounding Gap, Confidence-Calibration Absence) — ADR-031 closure |
| LLM08 | **Hidden Context Exposure** (System Prompt Leakage, 2025 name) | **Covered** | `tachi-prompt-injection` "System Prompt Extraction" pattern + Pattern Category 6 (meta-query system-prompt extraction — leakage mechanism) + Pattern Category 7 (untrusted-vs-trusted content boundary-marker absence — the 2026-broadened trust-failure mechanism) + `tachi-model-theft` Pattern Category 9 (System Prompt and Configuration Leakage) |
| LLM09 | Vector and Embedding Weaknesses | **Covered** | `tachi-data-poisoning` Pattern Category 6 (RAG and Vector Store Poisoning at Retrieval Time — runtime retrieval-index contamination, distinct from training-time poisoning) |
| LLM10 | Improper Output Handling | **Covered** | `tachi-output-integrity` Pattern Category 2 (Server-Side Execution Sinks) + AI-Coding-Assistant sub-example (Package-Manager / CI-Workflow Injection) — insecure-generated-code-at-scale absorption; full evidence in gap-analysis Record 4. **Scope boundary**: architecture-level detection only (LLM-emitted code, install commands, or CI workflow steps reaching an unguarded executor) — semantic-quality analysis of AI-authored source content itself is explicitly out of scope, per the existing "Application-source-code SAST replacement" anti-claim below |

**10/10 Covered.** The headline is unmoved by the four 2026 scope
absorptions (cross-modal injection, model-artifact authenticity,
fine-tuning subversion, insecure generated code at scale) — each lands on
an existing detection surface rather than opening a gap; see the gap
analysis for the full per-absorption evidence trail.

### Residual notes (documentary — not coverage gaps)

- **R-1** (LLM01, robustness): the cross-modal evidence lives in Pattern
  Categories 7–8, which the `tachi-prompt-injection` persona's own
  Detection-Workflow enumeration undercounts (names 5 of the catalog's 8
  categories). The content is still reachable at runtime via the persona's
  mandatory full-catalog Read directive. Tracked for follow-up filing at
  T026 (FU-1).
- **R-2** (LLM10, scope-fenced): the *semantic quality of AI-generated
  source code itself* is not detected by tachi and is not claimed — see the
  LLM10 row's scope boundary above and the Anti-claims section below.
- **R-3** (LLM08, documentary): the 2026-broadened "hidden context" object
  types (e.g. RAG-retrieved-but-unshown content, tool/function schemas) are
  reached by the catalog's own "internal instructions" / "configuration"
  language and by the general untrusted-content boundary pattern (Pattern
  Category 7), rather than by an indicator that names RAG-context or
  tool-schema leakage specifically. The system-prompt-and-configuration
  core of LLM08 (the 2025 System Prompt Leakage scope) is directly and
  explicitly detected.

## Reproducibility (byte-deterministic)

The per-framework `Coverage Attestation` page in committed baselines is
byte-deterministic under `SOURCE_DATE_EPOCH=1700000000` (ADR-021 +
ADR-029 + ADR-037 D-11). **Baseline layouts differ across examples**:

- **Nested layout** (4 baselines: `agentic-app`, `consumer-agent-app`,
  `mobile-banking-app`, `predictive-ml-app`):
  `examples/{name}/sample-report/security-report.pdf.baseline`
- **Top-level layout** (e.g., `web-app`):
  `examples/{name}/security-report.pdf.baseline`

The recipe below uses the nested-layout `agentic-app` baseline; swap the
path to match the example's actual layout when reproducing on others.

```bash
# Nested-layout example (agentic-app)
SOURCE_DATE_EPOCH=1700000000 /tachi.security-report examples/agentic-app/
diff examples/agentic-app/sample-report/security-report.pdf{,.baseline}
# Compare specifically the Coverage Attestation page bytes.

# Top-level-layout example (web-app)
SOURCE_DATE_EPOCH=1700000000 /tachi.security-report examples/web-app/
diff examples/web-app/security-report.pdf{,.baseline}
```

## Anti-claims (NOT covered by 50/50)

- Zero-false-positive guarantee.
- Coverage of OWASP frameworks NOT enumerated above (e.g., OWASP IoT, OWASP Serverless).
- Application-source-code SAST replacement.
- CVE detection (SCA) replacement.

## See also

- [Threat Categories](../../README.md#threat-categories) — the 14 specialized agents.
- [`schemas/taxonomy/owasp.yaml`](../../schemas/taxonomy/owasp.yaml) — machine-readable source-of-truth.
- ADR-024 → ADR-037 + ADR-045 — per-framework closure decisions.
