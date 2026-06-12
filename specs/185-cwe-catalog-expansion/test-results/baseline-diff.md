# T014 — Baseline Regeneration Page-Diff Evidence (Feature 185, US3 / W1-3)

**Date**: 2026-06-11 · **Branch**: `185-cwe-catalog-expansion` · **Executor**: senior-backend-engineer (W2 Track 1)
**Authority**: `contracts/baseline-regen.contract.md` (ADR-037 D-9, ADR-021 epoch pin) · **Typst**: 0.14.2 · **pdftotext**: poppler 26.01.0

## Verdict

**6/6 examples: CA-ONLY-DELTA-OK.** Every text-layer delta is confined to the Coverage Attestation framework-matrix pages (specifically the MITRE ATLAS page and the CWE Top 25 page). Both expected attributions present on every example: **cwe 53 → 93** (F-185) and **inherited mitre-atlas 30 → 36** (#186 absorb). Page counts unchanged on all 6 — the +40 CWE and +6 ATLAS badges reflow within the existing matrix pages, so no CA pagination growth occurred and no TOC/footer/per-finding page shifted. HALT rule (R6, non-CA delta) **not triggered**.

## Method

Per `contracts/baseline-regen.contract.md`, sequentially per example (shared `report-data.typ` forbids parallel regen), under `SOURCE_DATE_EPOCH=1700000000`:

```bash
export SOURCE_DATE_EPOCH=1700000000
/usr/bin/python3 scripts/extract-report-data.py \
  --target-dir examples/{name} \
  --output templates/tachi/security-report/report-data.typ \
  --template-dir templates/tachi/security-report
typst compile templates/tachi/security-report/main.typ /tmp/t014/{name}/new.pdf --root .
cp /tmp/t014/{name}/new.pdf examples/{name}/security-report.pdf.baseline
```

Two execution notes (both mirror the test body, `tests/scripts/test_backward_compatibility.py`, more exactly than the contract's literal lines):

1. **Interpreter**: bare `python3` (PATH-first) lacks PyYAML and crashes in `load_framework_yaml_record_counts()`; the byte-identity test runs `sys.executable` of the `/usr/bin/python3 -m pytest` invocation, so `/usr/bin/python3` is the faithful interpreter. (The first attempted run crashed before writing any output — no mutation resulted.)
2. **Compile target**: typst 0.14.2 cannot infer output format for a `.baseline` path (`error: could not infer output format`). The test compiles to a `security-report.pdf` temp path and byte-compares; the regen therefore compiled to `/tmp/t014/{name}/new.pdf` and copied onto the baseline — byte-equivalent to the contract's intent, identical to the test's procedure.

**Diff procedure**: old baseline saved to `/tmp/t014/{name}/old.pdf` before overwrite; per-page text extracted with `pdftotext -f N -l N` for every page of old and new; pages aligned (identical prefix + identical suffix verified pairwise); every differing page classified (CA page = emitted by `coverage-attestation-page`: framework-matrix pages carrying the `Coverage Attestation — {framework}` heading/running-header, or `Per-Finding Source Attribution` pages; TOC and all other pages = non-CA). Any non-CA delta ⇒ HALT.

## Per-example results

| Example | Pages old→new | Differing pages | ATLAS delta (page) | CWE delta (page) | Non-CA deltas | Verdict |
|---|---|---|---|---|---|---|
| web-app | 24 → 24 | p20, p22 | 30→36 badges, +6 (p20) | 53→93 badges, +40 (p22) | none | CA-ONLY-OK |
| microservices | 26 → 26 | p22, p24 | 30→36, +6 (p22) | 53→93, +40 (p24) | none | CA-ONLY-OK |
| ascii-web-api | 20 → 20 | p17, p19 | 30→36, +6 (p17) | 53→93, +40 (p19) | none | CA-ONLY-OK |
| mermaid-agentic-app | 37 → 37 | p33, p35 | 30→36, +6 (p33) | 53→93, +40 (p35) | none | CA-ONLY-OK |
| free-text-microservice | 24 → 24 | p20, p22 | 30→36, +6 (p20) | 53→93, +40 (p22) | none | CA-ONLY-OK |
| maestro-reference | 86 → 86 | p67, p69 | 30→36, +6 (p67) | 53→93, +40 (p69) | none | CA-ONLY-OK |

In every example, all pages outside the two listed matrix pages are text-layer identical, including the TOC (no entry renumbered — page counts did not shift), the Per-Finding Source Attribution pages, and — for maestro-reference — the 17 trailing pages (p70–p86: per-finding attribution + Control Coverage + Remediation Roadmap, which render after the CA block).

## Attestation summary-line deltas (decisive lines, old → new)

The percentage stayed `0.00%` everywhere, exactly as the contract anticipated (covered count is 0 on these frameworks) — the visible delta is denominators and Gap rows:

| Example | MITRE ATLAS summary line | CWE Top 25 summary line |
|---|---|---|
| web-app | `Covered: 0 / 30 = 0.00% · Partial: 0 · Gap: 30` → `0 / 36 … Gap: 36` | `Covered: 0 / 53 = 0.00% · Partial: 13 · Gap: 40` → `0 / 93 … Partial: 13 · Gap: 80` |
| microservices | `0 / 30 … Gap: 30` → `0 / 36 … Gap: 36` | `0 / 53 … Partial: 13 · Gap: 40` → `0 / 93 … Partial: 13 · Gap: 80` |
| ascii-web-api | `0 / 30 … Gap: 30` → `0 / 36 … Gap: 36` | `0 / 53 … Partial: 9 · Gap: 44` → `0 / 93 … Partial: 9 · Gap: 84` |
| mermaid-agentic-app | `0 / 30 … Gap: 30` → `0 / 36 … Gap: 36` | `0 / 53 … Partial: 14 · Gap: 39` → `0 / 93 … Partial: 14 · Gap: 79` |
| free-text-microservice | `0 / 30 … Gap: 30` → `0 / 36 … Gap: 36` | `0 / 53 … Partial: 11 · Gap: 42` → `0 / 93 … Partial: 11 · Gap: 82` |
| maestro-reference | `0 / 30 … Gap: 30` → `0 / 36 … Gap: 36` | `0 / 53 … Partial: 8 · Gap: 45` → `0 / 93 … Partial: 8 · Gap: 85` |

Invariant check: Partial + Gap = 93 on every new CWE page (13+80, 9+84, 14+79, 11+82, 8+85) and Partial counts are unchanged from old — all 40 new records land in Gap, as expected (no existing finding attributes to them). ATLAS Gap = 36 with Partial 0 everywhere.

## Inherited #186 ATLAS absorb — badge identity

The +6 ATLAS Gap badges added on every example are exactly the six #186 additions: `AML.T0001, AML.T0005, AML.T0025, AML.T0037, AML.T0043, AML.T0048` (verified in the web-app p20 hunk; identical set on all examples since the matrix renders the full catalog).

## Representative diff hunk (web-app p22, CWE matrix)

```
-Covered: 0 / 53 = 0.00% · Partial: 13 · Gap: 40
+Covered: 0 / 93 = 0.00% · Partial: 13 · Gap: 80
...
-Gap (40)                      +Gap (80)
+✗ CWE-1035  +✗ CWE-1039  +✗ CWE-1104  +✗ CWE-122  +✗ CWE-125
+✗ CWE-16    +✗ CWE-20    +✗ CWE-256   +✗ CWE-259  +✗ CWE-260
+… (40 new ✗ badges total; 13 ◐ Partial badges reflow position within the page grid, unchanged in identity)
```

(The 13 Partial badge identities are unchanged; their pdftotext line positions shift because the badge grid reflows — confined to the same CA page.)

## Byte-size record

| Example | old bytes | new bytes |
|---|---|---|
| web-app | 1,320,661 | 1,322,909 |
| microservices | 1,373,076 | 1,375,313 |
| ascii-web-api | 1,279,340 | 1,281,938 |
| mermaid-agentic-app | 2,174,553 | 2,176,776 |
| free-text-microservice | 1,316,018 | 1,318,260 |
| maestro-reference | 7,032,004 | 7,034,341 |

Pre-state cross-check: T001 recorded the test-regenerated maestro-reference at 7,032,279 bytes when only the ATLAS drift existed (cwe.yaml still 53); the new baseline at 7,034,341 carries ATLAS + CWE deltas — consistent.

## Residue (contract invariant 5)

`templates/tachi/security-report/report-data.typ` is **gitignored** (`.gitignore:204`) and has never been tracked — the contract's literal `git checkout -- …` is inoperative (no committed state exists; "no transient output committed" is structurally guaranteed). Equivalent no-residue action taken: the transient file was deleted after the final regen. `git status --porcelain` shows only the 6 baseline modifications (plus parallel Track-2/T016 files not owned by this task). The byte-identity suite regenerates `report-data.typ` per-test, so deletion cannot affect T015.
