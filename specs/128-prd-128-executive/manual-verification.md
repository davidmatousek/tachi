---
task: T023
feature: 128-prd-128-executive
wave: 4
date: 2026-04-09
verifier: main build agent (acting as orchestrator)
status: PASS
---

# T023 Manual End-to-End Verification

## Purpose

Verify that Wave 4 US-2 integration renders the Executive Threat Architecture page in the correct position in the generated PDF, and that the conditional block is correctly skipped when the image is absent.

## Method

Ran the extraction + compile pipeline twice against `examples/agentic-app/sample-report/`: once with a placeholder JPEG present (simulating T033 Gemini output) and once with the JPEG removed. Used `pdftotext -layout` to extract per-page text and asserted the presence, position, and total page count of key sections.

The placeholder JPEG was a copy of the existing `threat-system-architecture.jpg` standing in for the eventual Gemini-generated `threat-executive-architecture.jpg`. The placeholder was removed after verification. T033 will regenerate the real Gemini output in Phase 7.

## Commands Run

```bash
# Present branch
cp examples/agentic-app/sample-report/threat-system-architecture.jpg \
   examples/agentic-app/sample-report/threat-executive-architecture.jpg
python3 scripts/extract-report-data.py \
    --target-dir examples/agentic-app/sample-report \
    --output templates/tachi/security-report/report-data.typ \
    --template-dir templates/tachi/security-report/
typst compile templates/tachi/security-report/main.typ \
    /tmp/tachi-t023-verify/security-report.pdf --root .
pdftotext -layout /tmp/tachi-t023-verify/security-report.pdf \
    /tmp/tachi-t023-verify/security-report.txt

# Absent branch
rm examples/agentic-app/sample-report/threat-executive-architecture.jpg
python3 scripts/extract-report-data.py \
    --target-dir examples/agentic-app/sample-report \
    --output templates/tachi/security-report/report-data.typ \
    --template-dir templates/tachi/security-report/
typst compile templates/tachi/security-report/main.typ \
    /tmp/tachi-t023-verify/security-report-absent.pdf --root .
pdftotext -layout /tmp/tachi-t023-verify/security-report-absent.pdf \
    /tmp/tachi-t023-verify/security-report-absent.txt
```

Both compilations exited 0. Both PDFs were non-zero size.

## Results

### Present Branch (placeholder JPEG in target directory)

| Property | Value |
|----------|-------|
| Total pages | 34 |
| `has-executive-architecture` | `true` |
| Executive Summary first occurrence | page 10 |
| Executive Threat Architecture first occurrence | **page 11** |
| Attack Path Analysis first occurrence | page 12 |
| Attack Path pages | 12 through 19 (8 attack trees) |

The Executive Threat Architecture page sits **immediately after Executive Summary** (page 10 → 11) and **immediately before Attack Path Analysis** (page 11 → 12). This matches the US-2 requirement exactly.

### Absent Branch (no JPEG in target directory)

| Property | Value |
|----------|-------|
| Total pages | 33 |
| `has-executive-architecture` | `false` |
| Executive Summary first occurrence | page 10 |
| Executive Threat Architecture first occurrence | not present |
| Attack Path Analysis first occurrence | page 11 |

Page count drops by exactly one (34 → 33). The Executive Threat Architecture page is not inserted. Attack Path Analysis shifts forward from page 12 to page 11. This confirms the conditional block is correctly skipped when the flag is false.

### Backward Compatibility Signal

The absent-branch PDF is rendered from the exact same `main.typ` + `full-bleed.typ` as the pre-F-128 baseline, with `has-executive-architecture = false`. Structurally, the output should match the pre-F-128 rendering of agentic-app (modulo any other unrelated changes on the branch). Byte-identical equivalence for the 5 unmodified examples is verified formally by T024's `test_backward_compatibility.py` against the committed `.baseline` PDFs.

## TOC and Artifact Detection

| Signal | Expected | Observed | Result |
|--------|----------|----------|--------|
| `#let has-executive-architecture = true` emitted when image present | yes | yes | PASS |
| `#let has-executive-architecture = false` emitted when image absent | yes | yes | PASS |
| `#let executive-architecture-image-path = "..."` is relative | yes | yes (`../../../examples/agentic-app/sample-report/...`) | PASS |
| Page inserted at correct position | after Exec Summary, before Attack Path | page 11 between 10 and 12 | PASS |
| Page omitted when flag false | one fewer page than present branch | 33 vs 34 | PASS |
| Typst compile exits 0 in both branches | yes | yes | PASS |

## Issues Encountered and Resolved

**Issue**: Initial attempt used `/tmp/tachi-t023-verify/sample-report/` as the target directory to keep the real `examples/agentic-app/sample-report/` untouched. This failed at `typst compile --root .` because `infographic-page()` tries to load the image via `#image(image-path, ...)` and Typst refuses to read files outside the project root. The existing funnel/baseball/system-architecture images had the same failure mode when target-dir was outside the tachi repo.

**Resolution**: Switched to the in-tree `examples/agentic-app/sample-report/` target, added a placeholder JPEG, ran verification, and removed the placeholder after. The real Gemini-generated image will land in T033.

**Implication for test_backward_compatibility.py (T024)**: The 5 baseline examples are all under `examples/` (inside the repo root), so T024 will not hit the root restriction. No test change required.

## Cleanup

- Placeholder `examples/agentic-app/sample-report/threat-executive-architecture.jpg` deleted after verification
- Intermediate `templates/tachi/security-report/report-data.typ` deleted
- Temporary `/tmp/tachi-t023-verify/` retained for traceability until end of Wave 4

## Conclusion

T023 PASS. The US-2 PDF integration works end-to-end in both the present and absent branches. Page positioning matches the spec (between Executive Summary and Attack Path Analysis). Backward compatibility for the absent branch is structurally sound and will be formally verified by T024. No issues surfaced that require debugger escalation or architect re-review.
