# `predictive-ml-app/` — F-6 (Feature 232) ML Top 10 Coverage Bundle Mutation Target

This directory holds the F-6 mutation target — a fictional fraud-detection predictive-ML application architecture (`architecture.md`) and its regenerated security-report baseline (`sample-report/security-report.pdf.baseline` after Wave 4.0 regeneration completes).

## Purpose

The architecture exhibits all five predictive-ML topology indicators required by FR-014 of the Feature 232 specification:

1. Training pipeline ingesting from a public dataset repository (Public Dataset Repository → Model Training Pipeline)
2. Fine-tuning step on pretrained weights from a public registry (HuggingFace Hub → Fine-Tuning Service, no checksum verification)
3. MLOps model registry promoting versioned artifacts (MLflow Model Registry → Prediction API)
4. Prediction-API endpoint serving a classifier with no input-validation barrier (FraudDetectionML Prediction API receiving raw user-controlled transaction features)
5. Active-learning feedback loop reading production predictions back into training (Active-Learning Feedback Loop → Internal Merchant Transaction History through Production-Label Labeling Worker)

The architecture deliberately omits adversarial-defense controls, dataset-checksum manifests, signed-artifact policies, model-card review gates, output-perturbation noise, query-rate throttling, DP-SGD on training, label-flip detection on the active-learning loop, and integrity verification at model-load time so that the F-6 detection pipeline emits the full seven-Pattern-Category surface (tampering Cat 10 + data-poisoning Cat 8/9/10 + model-theft Cat 12/13/14) on a clean-slate baseline.

## Mutation Target Status

**Excluded from `tests/scripts/test_backward_compatibility.py` byte-identity loop** per FR-014 (mirrors `examples/agentic-app/` F-3 + F-5 mutation-target precedent and `examples/consumer-agent-app/` F-4 mutation-target precedent). The baseline regenerated here intentionally changes when F-6 enrichment ships and again on any subsequent ML-Pattern-Category enrichment feature; therefore byte-identity stability against this baseline is not a backward-compatibility invariant.

The six non-predictive-ML baselines that DO participate in the byte-identity loop are: `web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`. Those six baselines exhibit no predictive-ML topology indicators and therefore receive zero new ML-Pattern-Category findings from F-6 — preserving the SC-018 byte-identity invariant under `SOURCE_DATE_EPOCH=1700000000` per ADR-021.

## Regeneration

Regenerate the baseline end-to-end via the standard pipeline (run from the repository root):

```bash
cd examples/predictive-ml-app && \
  SOURCE_DATE_EPOCH=1700000000 /tachi.threat-model && \
  SOURCE_DATE_EPOCH=1700000000 /tachi.risk-score && \
  SOURCE_DATE_EPOCH=1700000000 /tachi.compensating-controls && \
  SOURCE_DATE_EPOCH=1700000000 /tachi.infographic all && \
  SOURCE_DATE_EPOCH=1700000000 /tachi.security-report
```

The expected emission (per SC-019) is at least six new ML findings: at least one new `T-{N}` from tampering Cat 10, at least one new `D-{N}` from data-poisoning Cat 8, 9, or 10, and at least one new `LLM-{N}` from model-theft Cat 12, 13, or 14 — aggregating to at least six findings across the six closed ML Top 10 items (ML01, ML03, ML04, ML06, ML07, ML08). ML06's two-facet split per ADR-035 D-4 may produce two findings (one corpus-side data-poisoning Cat 10 and one artifact-side model-theft Cat 14) on this architecture because both supply-chain signals are present.

## Lineage

| Feature | Mutation Target | Purpose |
|---|---|---|
| F-3 (Feature 219) | `examples/agentic-app/` | OWASP ASI07:2026 tool-abuse enrichment (Cat 9 + Cat 10) |
| F-4 (Feature 224) | `examples/consumer-agent-app/` | OWASP ASI09:2026 human-trust-exploitation surface |
| F-5 (Feature 229) | `examples/agentic-app/` | OWASP LLM10:2025 unbounded-consumption enrichment (Cat 12-13 DoS + Cat 10-11 model-theft) |
| **F-6 (Feature 232)** | **`examples/predictive-ml-app/`** | **OWASP ML Top 10:2023 coverage bundle (7 categories across 3 host agents)** |
