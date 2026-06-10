---
title: "50/50 OWASP coverage in tachi — what it means and how to verify it"
author: David Matousek
date: 2026-06-01
summary: tachi (Threat Modeling and Vulnerability Detection Harness for Claude Code) ships at full coverage across the OWASP LLM 2025, Agentic 2026, ML 2023, Mobile 2024, and Web/API (2021 + 2023) Top 10s. This article walks through what "50/50" means under the hood, how the per-framework counts compose to a five-slot narrative, and how to reproduce the coverage claim byte-deterministically on your own machine.
related:
  - https://github.com/pratik-saptarshi/tachi-rust
  - https://github.com/pratik-saptarshi/tachi-rust/blob/main/docs/standards/OWASP_COVERAGE.md
---

# 50/50 OWASP coverage in tachi — what it means and how to verify it

## §a — Why 50/50, and what 10/10 means per framework

OWASP-coverage claims age badly. A scanner says "we cover the OWASP Top 10," and the reader is left guessing: which Top 10 — Web 2021, API 2023, LLM 2025, Agentic 2026, ML 2023, Mobile 2024? All catalogued items, or a representative subset? Are findings traceable back to OWASP item IDs, or does "coverage" mean a marketing line in a datasheet? When a maintainer or security engineer evaluates a scanning column, those distinctions matter — they're the difference between an audit-defensible claim and one that evaporates under review.

tachi takes the explicit position. The schema in `schemas/taxonomy/owasp.yaml` carries **6 framework buckets × 10 items each = 60 records**: LLM 2025 (LLM01–LLM10), Agentic 2026 (ASI01–ASI10), ML 2023 (ML01–ML10), Mobile 2024 (M1–M10), Web 2021 (A01–A10), and API 2023 (API1–API10). Each record links a catalogued threat to one or more tachi detection agents and to the architectural decision record (ADR) that documents the closure.

The headline compresses this 60-record schema into a five-slot narrative: **OWASP five-framework total: 50/50 covered**, where Web 2021 (A01–A10) and API 2023 (API1–API10) collapse into a combined Web/API slot. That compression is intentional — Web Top 10 and API Security Top 10 share the STRIDE detection pipeline plus cross-framework `source_attribution` populator wiring, so they live on the same engine even though they're distinct OWASP frameworks. ADR-037 D-2 documents the decision; the schema keeps both buckets separate, the narrative compresses to one slot per the bridge pattern, and the canonical anchor (`docs/standards/OWASP_COVERAGE.md`) carries the footnote so the math always reconciles.

What does **10/10 mean per slot**? It means every catalogued item in that OWASP framework — every numbered threat in the original OWASP document — has at least one tachi detection agent that detects it, plus an ADR documenting the closure decision and a populator that emits the OWASP item ID in the SARIF and finding outputs. It does **not** mean zero false positives. It does **not** mean tachi replaces SAST or SCA. It does **not** mean every false-negative case is covered. It means catalogued-threat coverage with a reproducible verification anchor.

The per-bucket canonical URLs (kept separate for citation accuracy):

- LLM 2025 — <https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/>
- Agentic 2026 — <https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/>
- ML 2023 — <https://owasp.org/www-project-machine-learning-security-top-10/>
- Mobile 2024 — <https://owasp.org/www-project-mobile-top-10/>
- Web 2021 — <https://owasp.org/Top10/>
- API 2023 — <https://owasp.org/API-Security/>

That's the headline. The next section shows you how to verify it on your machine without taking my word for any of it.

## §b — Verification walkthrough (byte-deterministic Coverage Attestation)

The verification anchor is the per-framework **Coverage Attestation** page that the `/tachi.security-report` command emits as part of the PDF security report. Under `SOURCE_DATE_EPOCH=1700000000`, the Coverage Attestation page bytes are reproducible: run the command, diff against the committed baseline PDF, and the diff is empty. If you can reproduce the baseline byte-for-byte, you've verified that the coverage matrix the report displays matches the matrix the schema declares.

**Slot-bridging trade-off**. tachi ships several worked example architectures under `examples/`. A single architecture cannot exercise all five framework slots — a pure web app doesn't trigger LLM agents, an LLM agentic app doesn't trigger mobile detection. To exercise all 5 slots, you have two paths: (a) run four single-slot examples one per slot, or (b) run two-to-four examples where at least one is a slot-bridging architecture. `examples/agentic-app/` bridges Agentic + LLM. `examples/web-app/` bridges Web + API. Picking those two plus one ML and one Mobile example gives full 5-slot coverage in four runs. Picking only `web-app` + `agentic-app` covers four slots with two runs and is a good ergonomic starting point. The verification walkthrough below uses both.

**Baseline layout note**. Baselines live in two on-disk layouts depending on when the example was added:

- **Nested** (`agentic-app`, `consumer-agent-app`, `mobile-banking-app`, `predictive-ml-app`): the baseline PDF is at `examples/{name}/sample-report/security-report.pdf.baseline`.
- **Top-level** (`web-app`): the baseline PDF is at `examples/{name}/security-report.pdf.baseline`.

The recipe below uses the correct path per layout — copy-paste both blocks and the recipe works against either example.

**Recipe — nested-layout example (agentic-app, bridges Agentic + LLM)**:

```bash
SOURCE_DATE_EPOCH=1700000000 /tachi.security-report examples/agentic-app/
diff examples/agentic-app/sample-report/security-report.pdf{,.baseline}
# Expected: empty diff. The Coverage Attestation page bytes match the committed baseline.
```

**Recipe — top-level-layout example (web-app, bridges Web + API)**:

```bash
SOURCE_DATE_EPOCH=1700000000 /tachi.security-report examples/web-app/
diff examples/web-app/security-report.pdf{,.baseline}
# Expected: empty diff. The Coverage Attestation page bytes match the committed baseline.
```

**Recipe — ML slot (predictive-ml-app, nested layout)**:

```bash
SOURCE_DATE_EPOCH=1700000000 /tachi.security-report examples/predictive-ml-app/
diff examples/predictive-ml-app/sample-report/security-report.pdf{,.baseline}
# Expected: empty diff. The Coverage Attestation page emits the per-finding OWASP ML 2023 item IDs aggregated across STRIDE + ML enrichment agents.
```

**Recipe — Mobile slot (mobile-banking-app, nested layout)**:

```bash
SOURCE_DATE_EPOCH=1700000000 /tachi.security-report examples/mobile-banking-app/
diff examples/mobile-banking-app/sample-report/security-report.pdf{,.baseline}
# Expected: empty diff. The Coverage Attestation page emits the per-finding OWASP Mobile 2024 item IDs aggregated across STRIDE + Mobile enrichment agents.
```

The four runs together cover all five framework slots: LLM + Agentic via `agentic-app`; Web + API via `web-app`; ML via `predictive-ml-app`; Mobile via `mobile-banking-app`. If you want a single-architecture proxy for all five slots simultaneously, `examples/maestro-reference/` is the closest — a multi-slot bridging architecture that exercises STRIDE + LLM + Agentic detection at once across a richer surface — though it doesn't add ML or Mobile coverage on its own.

**What the byte-determinism guarantees and what it doesn't**. The Coverage Attestation page is governed by ADR-021 (byte-determinism contract) + ADR-029 (Coverage Attestation report-section contract) + ADR-037 D-11 (Web/API combined-slot byte-determinism). Those three ADRs together commit the project to a single, reproducible Coverage Attestation page per architecture. The narrative `threats.md` output is **not** byte-deterministic — it depends on the LLM's reasoning trajectory, which varies run-to-run. The Coverage Attestation page, on the other hand, is structural: it aggregates `source_attribution` items across emitted findings using deterministic schema lookups, so the same architecture under the same `SOURCE_DATE_EPOCH` always produces the same Coverage Attestation bytes. That's the anchor — narrative output can vary, but the coverage anchor doesn't.

**If the diff isn't empty**. Three likely causes, in order of frequency: (1) `SOURCE_DATE_EPOCH` not set — re-run with `SOURCE_DATE_EPOCH=1700000000` explicit; (2) Typst or `mmdc` version drift — the report toolchain pins are documented in the prerequisites section of the tachi README; (3) the baseline is stale because tachi shipped a new finding or schema record since the example baseline was last regenerated — the maintainer regenerates baselines as part of release, but if you're running on a checkout between releases the diff will reflect intentional delta. If you reproduce a non-empty diff on a release tag with the documented toolchain, that's a reproducible bug worth filing — see §f.

The recipe is documented in `docs/standards/OWASP_COVERAGE.md` (canonical anchor) and is the same recipe used in the F-1 pre-publication narrative-defensibility check (`specs/296-*/notes/narrative-defensibility-check.md`). You can run the recipe yourself before trusting any tachi coverage claim — that's the point.

## §c — Coverage matrix

The canonical matrix lives at `docs/standards/OWASP_COVERAGE.md` in the tachi repo. Reproduced here for reference:

| Framework | Bucket | Items | Status | OWASP Anchor | Detection ADRs |
|---|---|---|---|---|---|
| LLM 2025 | OWASP-LLM-2025 | LLM01–LLM10 | 10/10 | [LLM 2025](https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/) | ADR-030, ADR-031, ADR-034, ADR-045 |
| Agentic 2026 | OWASP-AGENTIC-2026 | ASI01–ASI10 | 10/10 | [Agentic 2026](https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/) | ADR-032, ADR-033 + pre-BLP-01 |
| ML 2023 | OWASP-ML-2023 | ML01–ML10 | 10/10 | [ML 2023](https://owasp.org/www-project-machine-learning-security-top-10/) | ADR-035 |
| Mobile 2024 | OWASP-MOBILE-2024 | M1–M10 | 10/10 | [Mobile 2024](https://owasp.org/www-project-mobile-top-10/) | ADR-036 |
| Web 2021 | OWASP-2021 | A01–A10 | 10/10 | [Web 2021](https://owasp.org/Top10/) | ADR-037 |
| API 2023 | OWASP-API-2023 | API1–API10 | 10/10 | [API 2023](https://owasp.org/API-Security/) | ADR-037 |

**Per-bucket total**: 60/60.
**Headline framing**: 5 slots × 10 items = 50/50 (Web + API combined per ADR-037 D-2).

The Detection ADRs column points to the architectural decision records that document each framework's closure. They're the audit trail: every claim in this matrix traces to an ADR you can read, a schema record you can grep, and a Coverage Attestation page you can reproduce. The `source_attribution` schema extension (ADR-028) is the wiring that makes the matrix machine-readable — every emitted finding can carry an optional `source_attribution` field naming the OWASP item ID, the MITRE ATT&CK technique, the MITRE ATLAS pattern, the NIST AI RMF category, and the CWE identifier. The Coverage Attestation page (ADR-029) aggregates those `source_attribution` fields across the run and emits a per-framework summary, so the matrix you see in the PDF is generated from the same schema records that this article cites.

## §d — What 10/10 means per framework

### LLM 2025 — `prompt-injection`, `data-poisoning`, `model-theft`, `output-integrity`, `misinformation` (ADR-030, ADR-031, ADR-034, ADR-045)

LLM 2025 is closed by five LLM-specific detection agents that map one-to-many onto the OWASP LLM Top 10:2025 catalogue. The `prompt-injection` agent covers LLM01 (Prompt Injection) and the indirect-injection class — adversarial inputs embedded in retrieved documents, tool outputs, or upstream agent responses that hijack the LLM's instruction-following. `data-poisoning` covers LLM04 (Data and Model Poisoning) across training-set, RAG-vector-store, and embedding-index ingress paths — including the case where an attacker who can write to a knowledge base shapes downstream LLM behavior across many sessions. `model-theft` covers LLM10 (Unbounded Consumption — denial-of-wallet and extraction attacks per ADR-034) — including the cost-amplification case where an attacker drives token consumption to exhaust budget and the membership-inference case where queries reconstruct the training set. `output-integrity` covers LLM05 (Improper Output Handling) — including the three pattern-catalog gaps that ADR-045 closed in v4.36.0 (vector-filter / search-DSL injection where LLM-generated query DSLs reach a search backend without sanitization; package-manager / CI-workflow execution sinks where LLM-generated dependency manifests or CI YAML reach an executor; cross-agent handoff sinks where one agent's output is consumed as another agent's instruction without bounds checking). `misinformation` covers LLM09 (Misinformation) — factual-integrity violations reaching humans or decision cascades, per ADR-031, with a particular focus on advisory contexts (clinical, legal, financial) where unverified LLM output is consumed as if grounded. The remaining LLM items distribute across these five agents through the schema crosswalk; the per-finding `source_attribution` field carries the LLM item ID so SARIF consumers can filter by OWASP catalogue.

### Agentic 2026 — `agent-autonomy`, `tool-abuse`, `human-trust-exploitation` (ADR-032, ADR-033 + pre-BLP-01)

Agentic 2026 (ASI01–ASI10) is closed by three Agentic-specific agents. `agent-autonomy` covers the autonomy axis: insufficient oversight, runaway agents, action-without-approval patterns — the canonical example is an agent that sends 500 emails or commits 50 PRs without a human-in-the-loop checkpoint. `tool-abuse` covers MCP plugin abuse, tool-call argument tampering, inter-agent communication abuse, and capability escalation through chained tool calls (ADR-032 documents the ASI07 enrichment) — including the case where a malicious MCP server exfiltrates source code on invocation and the case where chained tool calls grant capabilities that the agent shouldn't have on its own. `human-trust-exploitation` (ADR-033) covers the communication axis — synthetic-relationship exploitation, undisclosed AI authorship, authority-claim emission, and persuasive-tone manipulation toward human consumers. Wellness chatbots claiming medical authority while concealing AI authorship are the canonical case; ASI09 (Identity Spoofing and Impersonation) and the broader trust-exploitation surface live here. The pre-BLP-01 agents (the original Agentic coverage bundle that predates the BLP-01 initiative's full-framework closure) cover the remaining items including agent identity (ASI01), memory poisoning (ASI03), goal manipulation (ASI05), and the multi-agent coordination patterns where one rogue agent contaminates a workflow's joint state.

### ML 2023 — `tampering` + `data-poisoning` + `model-theft` enrichment (ADR-035)

ML 2023 (ML01–ML10) is closed by enriching the existing `tampering`, `data-poisoning`, and `model-theft` agents for predictive ML signal-handling patterns. ADR-035 documents the closure. The enrichment adds ML-specific trigger patterns — adversarial input attacks where carefully crafted inputs cause misclassification at inference time, training-pipeline tampering where malicious examples shape the model's decision boundary during fit, model-inversion attacks where black-box queries reconstruct sensitive training records, and membership-inference attacks where an adversary determines whether a specific record was in the training set — without spawning new agents. The detection logic for predictive-ML inversion overlaps significantly with `model-theft`'s extraction patterns, which is why the closure reuses agents rather than introducing parallel ones; the per-trigger-pattern enrichment is documented in the agent's reference file. The per-finding `source_attribution` carries the ML item ID; the Coverage Attestation page emits the per-framework summary.

### Mobile 2024 — `spoofing` + `tampering` + `info-disclosure` + `privilege-escalation` + `repudiation` enrichment (ADR-036)

Mobile 2024 (M1–M10) is closed by enriching five STRIDE agents (`spoofing`, `tampering`, `info-disclosure`, `privilege-escalation`, `repudiation`) for mobile-specific patterns. ADR-036 documents the closure with a per-item mapping: M2 (Inadequate Supply Chain Security) and M3 (Insecure Authentication/Authorization) map to `spoofing` + `privilege-escalation` because the mobile supply-chain risks bridge identity and authorization; M4 (Insufficient Input/Output Validation) maps to `tampering` with mobile-specific deep-link and intent-filter trigger patterns; M6 (Inadequate Privacy Controls) and M9 (Insecure Data Storage) map to `info-disclosure` covering cleartext-storage, keystore-bypass, and shared-preference leakage cases; M8 (Security Misconfiguration) and M10 (Insufficient Cryptography) span multiple STRIDE buckets because the mobile misconfiguration surface (permissions, exported-component overscope, debuggable builds shipped to production) cross-cuts multiple STRIDE categories. The `mobile-banking-app` example exercises this enrichment end-to-end — run the verification recipe in §b against it and the Coverage Attestation page will display the per-item Mobile 2024 coverage. As with ML 2023, the enrichment adds trigger patterns without spawning new agents.

### Web 2021 + API 2023 — STRIDE agents + cross-framework `source_attribution` populator (ADR-037)

The Web/API combined slot is closed by the six STRIDE agents (`spoofing`, `tampering`, `repudiation`, `info-disclosure`, `denial-of-service`, `privilege-escalation`) with a cross-framework `source_attribution` populator that emits OWASP Web 2021 (A01–A10) and OWASP API 2023 (API1–API10) item IDs on findings. ADR-037 documents the closure including D-2 (the combined-slot narrative compression so the headline reads 50/50 instead of 60/60) and D-11 (the Web/API Coverage Attestation byte-determinism contract that anchors the verification recipe in §b). Per-item examples: A01:2021 Broken Access Control maps to `privilege-escalation`; A03:2021 Injection maps to `tampering`; A07:2021 Identification and Authentication Failures maps to `spoofing`; API3:2023 Broken Object Property Level Authorization maps to `privilege-escalation` with API-specific trigger patterns around mass-assignment and excessive-property-exposure; API4:2023 Unrestricted Resource Consumption maps to `denial-of-service`; API10:2023 Unsafe Consumption of APIs maps to `tampering` plus `info-disclosure` because the unsafe-consumption surface bridges trust-boundary violations and data leakage. The `web-app` example exercises the Web slot; the same architecture's API-style endpoints exercise the API slot through the same six STRIDE agents — that's why one architecture bridges two framework slots.

The full per-item crosswalk lives in `schemas/taxonomy/owasp.yaml` — one record per item, one or more detection agents per record, with audit trail back to the ADR. Grep for the OWASP item ID and you'll find the agent assignment. Grep for the agent name and you'll find every OWASP item that agent covers across all five frameworks. The schema is the single source of truth; everything else is derived from it.

## §e — Try it yourself

The repo is at <https://github.com/pratik-saptarshi/tachi-rust>. The canonical anchor for the 50/50 claim is <https://github.com/pratik-saptarshi/tachi-rust/blob/main/docs/standards/OWASP_COVERAGE.md>. The developer walkthrough with worked examples is at <https://github.com/pratik-saptarshi/tachi-rust/blob/main/docs/guides/DEVELOPER_GUIDE_TACHI.md>. Install with `~/Projects/tachi/scripts/install.sh` from your project root; run `/tachi.threat-model` to generate a complete threat model; run `/tachi.security-report` to produce the PDF with the Coverage Attestation page that anchors the matrix. Apache 2.0 licensed; no telemetry, no remote inference — the harness runs on your machine and your architecture description stays on your machine.

## §f — Contributing

If you've used tachi on a real architecture, [GitHub Discussions](https://github.com/pratik-saptarshi/tachi-rust/discussions) is the right surface for ideas, questions, and "here's how I'm using it" reports — the [In the Wild](https://github.com/pratik-saptarshi/tachi-rust/discussions/categories/in-the-wild) category exists for exactly that. If you've hit a reproducible bug or a gap in the OWASP coverage that you can demonstrate against a baseline, [GitHub Issues](https://github.com/pratik-saptarshi/tachi-rust/issues) is the place — the project follows a comment-first-give-choice contribution path: open an issue or discussion with the gap, the maintainer responds with an option list (you draft the PR / maintainer drafts it with attribution / you provide the test case and the maintainer ships it), and the merge attribution stays with the contributor. F-260 (`@north-echo`, PR #262, v4.31.0) and F-292 (`@armorer-labs`, PR #293, v4.36.0) are recent examples of community contributions that closed real gaps in the catalogue — the same path is open to you.
