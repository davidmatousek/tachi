# Narrative-Defensibility Pre-Check (FR-008 / SC-009)

**Date**: 2026-05-28 (Day 1 PM)
**Author**: maintainer
**Feature**: F-1 (Issue #296) — 50/50 OWASP Coverage Distribution Launch (BLP-04 Wave 1)
**Branch**: `296-50-50-owasp-coverage-distribution-launch`

## Purpose

Pre-publication evidence that every claim made in F-1 distribution artifacts
(README hero block, OWASP_COVERAGE.md canonical anchor, Cybersec article,
LinkedIn post, GitHub profile refresh, Discussion #179 closing comment)
maps back to a verified source-of-truth. Per FR-008, this note's first
commit timestamp MUST predate (a) the LinkedIn post publication, (b) the
Cybersec article PR merge timestamp (SC-009).

## Sources verified

### (a) `docs/standards/OWASP_COVERAGE.md` (canonical anchor — Wave 0 output)

- [x] **Exists**: `docs/standards/OWASP_COVERAGE.md` created 2026-05-28 (T005 output).
- [x] **Line cap**: 66 lines ≤ 80 (T007 verification; Architect H2 Option B lean).
- [x] **Indexed**: row added to `docs/standards/README.md` in alphabetical position between `NAMING_GUIDELINES.md` and `PRECOMMIT_HOOKS.md` (T006 output).

### (b) `schemas/taxonomy/owasp.yaml` — 6 buckets × 10 items = 60 records

- [x] **Verified**: `grep -c "^- id:" schemas/taxonomy/owasp.yaml` = **60** (T004 output, 2026-05-28).
- [x] **Per-bucket breakdown** (composed from schema + ADR lineage):
  - OWASP-LLM-2025: 10 items (LLM01–LLM10)
  - OWASP-AGENTIC-2026: 10 items (ASI01–ASI10)
  - OWASP-ML-2023: 10 items (ML01–ML10)
  - OWASP-MOBILE-2024: 10 items (M1–M10)
  - OWASP-2021 (Web): 10 items (A01–A10)
  - OWASP-API-2023: 10 items (API1–API10)
- [x] **Five-slot narrative**: 60 records compressed to 50/50 headline by combining Web 2021 + API 2023 into one narrative slot per ADR-037 D-2.

### (c) Byte-deterministic `Coverage Attestation` reproduction (≥1 example)

**Verifiable** via the canonical recipe documented in `docs/standards/OWASP_COVERAGE.md` §Reproducibility. Two baseline layouts present in the repo:

- **Nested layout** (e.g., `examples/agentic-app/sample-report/security-report.pdf.baseline`): verified present.
- **Top-level layout** (e.g., `examples/web-app/security-report.pdf.baseline`): verified present.

**Recipe** (one-shot — also documented in OWASP_COVERAGE.md and Cybersec article §b):

```bash
# Nested-layout example (agentic-app)
SOURCE_DATE_EPOCH=1700000000 /tachi.security-report examples/agentic-app/
diff examples/agentic-app/sample-report/security-report.pdf{,.baseline}
# Expected: empty diff on Coverage Attestation page bytes.

# Top-level-layout example (web-app)
SOURCE_DATE_EPOCH=1700000000 /tachi.security-report examples/web-app/
diff examples/web-app/security-report.pdf{,.baseline}
```

**Anchor ADRs**: ADR-021 (byte-determinism contract) + ADR-029 (Coverage Attestation section contract) + ADR-037 D-11 (Web/API combined-slot byte-determinism).

**Pre-publication re-run requirement**: this recipe MUST be executed against ≥1 example and yield an empty diff before the Cybersec article PR merges (T015 → T016) and before the LinkedIn post publishes (T017 → T018). If any diff is non-empty at pre-publication time, HALT and scope-reduce the claim to the verified subset.

### (d) OWASP framework canonical URLs — all 200 OK (verified 2026-05-28)

| Framework | URL | HTTP Status |
|---|---|---|
| LLM 2025 | https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/ | **200 OK** |
| Agentic 2026 | https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/ | **200 OK** |
| ML 2023 | https://owasp.org/www-project-machine-learning-security-top-10/ | **200 OK** |
| Mobile 2024 | https://owasp.org/www-project-mobile-top-10/ | **200 OK** |
| Web 2021 | https://owasp.org/Top10/ | **200 OK** |
| API 2023 | https://owasp.org/API-Security/ | **200 OK** |

**Verification command**:
```bash
for url in <each-url>; do
  curl -s -o /dev/null -w "%{http_code}" -L --max-time 10 "$url"
done
```

**Pre-publication re-check requirement**: URLs MUST be re-verified within 24 hours of each external surface publication. If any URL returns non-200, HALT and scope-reduce the headline to the verified subset.

## ADR lineage verified

- **ADR-024 → ADR-037**: per-framework closure ADRs (read at research time; cross-referenced in OWASP_COVERAGE.md Matrix column "Detection ADRs").
- **ADR-029**: Coverage Attestation report section contract (byte-determinism anchor).
- **ADR-037 D-2**: Web/API combined-slot narrative compression decision.
- **ADR-037 D-11**: Web/API combined-slot byte-determinism contract.
- **ADR-045**: F-292 cross-sink refinement; line 133 attributes @armorer-labs gap-analysis comment.

## Halt-condition (FR-008)

If any of the below conditions becomes true at publication time, HALT, scope-reduce the claim to the verified subset, and do NOT publish unverified surfaces:

- Any framework's bucket count ≠ 10.
- Any OWASP framework canonical URL returns non-200.
- Any cited ADR anchor is broken or has been retracted.
- `Coverage Attestation` PDF diff is non-empty against committed baseline under `SOURCE_DATE_EPOCH=1700000000`.

## Timestamp guarantee (SC-009)

This file's first commit timestamp MUST predate the LinkedIn post URL
recording timestamp AND the Cybersec article PR merge timestamp.
Verification at F-1 close: `git log --follow --format="%aI" -- specs/296-*/notes/narrative-defensibility-check.md` first line < LinkedIn URL file mtime AND < Cybersec article PR merge timestamp.
