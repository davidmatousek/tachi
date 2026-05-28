# OWASP Five-Framework Coverage Matrix (50/50)

Canonical reference for tachi's OWASP coverage claim. Composed from
`schemas/taxonomy/owasp.yaml` + ADR-024 → ADR-037 + ADR-045 lineage.

## Headline

**OWASP five-framework total: 50/50 Covered** (LLM 2025 10/10 + Agentic 2026
10/10 + ML 2023 10/10 + Mobile 2024 10/10 + Web/API 2021/2023 10/10).

The schema (`schemas/taxonomy/owasp.yaml`) carries **6 framework buckets ×
10 items = 60 records**. The "five-framework" headline compresses Web Top
10:2021 (A01–A10) and API Security Top 10:2023 (API1–API10) into one
narrative slot per ADR-037 D-2.

## Matrix

| Framework | Bucket | Items | Status | OWASP Anchor | Detection ADRs |
|---|---|---|---|---|---|
| LLM 2025 | OWASP-LLM-2025 | LLM01–LLM10 | 10/10 | https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/ | ADR-030, ADR-031, ADR-034, ADR-045 |
| Agentic 2026 | OWASP-AGENTIC-2026 | ASI01–ASI10 | 10/10 | https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/ | ADR-032, ADR-033 + pre-BLP-01 |
| ML 2023 | OWASP-ML-2023 | ML01–ML10 | 10/10 | https://owasp.org/www-project-machine-learning-security-top-10/ | ADR-035 |
| Mobile 2024 | OWASP-MOBILE-2024 | M1–M10 | 10/10 | https://owasp.org/www-project-mobile-top-10/ | ADR-036 |
| Web 2021 | OWASP-2021 | A01–A10 | 10/10 | https://owasp.org/Top10/ | ADR-037 |
| API 2023 | OWASP-API-2023 | API1–API10 | 10/10 | https://owasp.org/API-Security/ | ADR-037 |

**Per-bucket total: 60/60.** **Headline framing: 5 slots × 10 items = 50/50** (Web + API combined).

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
