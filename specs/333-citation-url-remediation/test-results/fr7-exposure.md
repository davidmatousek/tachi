# FR-007 Rendering-Exposure Verification (T014)

**Date**: 2026-06-29
**Task**: T014 — FR-007 rendering-exposure grep (plan D5)
**Result**: PASS — ZERO hits across all 13 baseline artifacts

## Baseline Artifacts Searched

All `security-report.pdf.baseline` files located under `examples/`:

1. `examples/agentic-app/sample-report/security-report.pdf.baseline`
2. `examples/agentic-app/test-output/2026-04-19T03-20-30/security-report.pdf.baseline`
3. `examples/agentic-app/test-output/2026-04-23T19-30-00-F2-wave4/security-report.pdf.baseline`
4. `examples/ascii-web-api/security-report.pdf.baseline`
5. `examples/consumer-agent-app/sample-report/security-report.pdf.baseline`
6. `examples/consumer-agent-app/test-output/2023-11-14T22-13-20-F4-wave5/security-report.pdf.baseline`
7. `examples/free-text-microservice/security-report.pdf.baseline`
8. `examples/maestro-reference/security-report.pdf.baseline`
9. `examples/mermaid-agentic-app/security-report.pdf.baseline`
10. `examples/microservices/security-report.pdf.baseline`
11. `examples/mobile-banking-app/sample-report/security-report.pdf.baseline`
12. `examples/predictive-ml-app/sample-report/security-report.pdf.baseline`
13. `examples/web-app/security-report.pdf.baseline`

No additional coverage or personalized-attack-tree baseline docs were found under `examples/` or `tests/` beyond the PDF baselines above (tests/fixtures/init-baseline-tree and tests/fixtures/regenerate-baseline.sh are shell scripts, not artifact baselines).

## Grep Patterns and Hit Counts

| Pattern | Expected Hits | Actual Hits |
|---------|---------------|-------------|
| `atlas.mitre.org/techniques` | 0 | **0** |
| `doi.org/10.6028/NIST.AI.100-1` | 0 | **0** |
| `artificial-intelligence-risk-management-framework-ai-rmf-10` | 0 | **0** |
| `genai.owasp.org` | 0 | **0** |

**Total hit count: 0**

## Conclusion

FR-007 rendering-exposure requirement is satisfied. The report aggregator reads record IDs/counts only (extract-report-data.py:1140-1193) and never embeds citation URL strings in the PDF text layer. No ADR-037 D-9 baseline-regen lane is required. The mitre-atlas and nist-ai-rmf ORDERED_FRAMEWORKS members (the #185 trap predicate) produce zero citation string exposure in all byte-identity-baselined render artifacts.
