# OI Extraction & Comparison Contract (SC-003, corrected)

**Feature**: #295 | **Supersedes for execution**: `specs/292-output-integrity-cross-sink-refinement/contracts/cross-link-no-emission-contract.md` §3/§6 (dual-defective — FR-008 defect Issue documents both; the archived file is NOT edited)
**Consumers**: T017 execution (build), SC-003 verification record, future OI-catalog maintainers

## 1. Corrected extraction filter (authoritative)

```bash
jq '[.runs[0].results[] | select(.partialFingerprints["findingId/v1"] // "" | startswith("OI-"))]' <input.sarif>
```

- The OI discriminator is `partialFingerprints["findingId/v1"]` — **never** `ruleId` (real ruleIds are `tachi/*`-family; the archived §3 filter matches zero results and false-passes on empty-vs-empty).
- Secondary cross-check only: `properties.tags` containing `output-integrity`; `threats.md` `| OI-` rows (top-level file, §4+§7 scope, 8 rows — the `sample-report/` copy has 12 due to the F-260b Affected Assets block).

## 2. False-pass guard (MUST precede any diff)

1. Anchor-side extraction MUST be non-empty and yield exactly `{OI-1, OI-2, OI-3, OI-4}` (cardinality 4, pre-verified 2026-07-03 against `git show 0629fa2~1:examples/agentic-app/sample-report/threats.sarif`).
2. Fresh-side extraction MUST be non-empty (expected cardinality 4).
3. Any empty extraction, or anchor cardinality ≠ 4 ⇒ **gate ERROR** (broken filter / wrong artifact / failed run) — halt; never interpret as "zero emissions = PASS".

## 3. Comparison sides

- **Anchor**: `git show 0629fa2~1:examples/agentic-app/sample-report/threats.sarif` (LLM-authored production artifact).
- **Fresh (primary, D-A)**: single-agent `tachi-output-integrity` YAML findings → assembler (`specs/295-f292-verification-runs/tools/`) → `fresh-oi.sarif`. Assembler reuses `scripts/sarif_common.py::build_sarif_envelope` (+ `generate-threats-sarif.py::build_result` where mapping is clean) via importlib (`test_affected_assets_wiring.py:520-536` precedent). Raw YAML committed verbatim beside the SARIF.
- **Fresh (fallback)**: scoped-full run (Phase 5 skipped) native `threats.sarif`.
- The corrected filter applies **uniformly to both sides** regardless of path.

## 4. D-1 hard gate (emission-level identity)

| Gate field | Comparison | Verdict rule |
|---|---|---|
| OI finding count | integer equality (expect 4 = 4) | ≠ ⇒ FAIL |
| findingId set | set equality | ≠ ⇒ FAIL |
| Per-finding sink/flow identity | **identifier-level** table: primary = `locations[].logicalLocations[].name` (structural component identifier, present on both sides — Architect plan-review verification 2026-07-03); secondary = quoted flow names from `message.text` lead; both sides' verbatim text committed | any identity mismatch ⇒ FAIL |

Everything else (severity, CWE list, message prose, `affected_assets`, MAESTRO annotations, envelope bytes) is **drift bucket** — see §5. Message *prose* is drift by design: two LLM sessions phrase the same emission differently; identification ≠ wording.

## 5. Attribution (fail-closed)

Every non-gate byte/field delta MUST map to a named class or the gate FAILS:

| Class | Named source |
|---|---|
| Asset tags (`affected_assets`, tag columns) | F-260b (v4.31.0) |
| MAESTRO annotations (`maestro-layer` etc.) | F-098 / #311 |
| Crosswalk/citation growth (owasp/cwe refs) | #184–#186 |
| Assembler-tier envelope (formatting, run metadata, ordering) | D-A standing class (primary path only) |
| *(anything else)* | **unattributable ⇒ FAIL** ⇒ FR-007 defect Issue with evidence |

Bounded walk: `git log -p 0629fa2..HEAD -- <surface files>` per class; record commit SHAs in the attribution table.

## 6. Outcomes

- **PASS** ⇒ SC-003 record + T017 checkbox + FR-008 contract-defect filing (always).
- **FAIL** ⇒ defect Issue w/ evidence (FR-007) + honest record; #295 still closes on the record.
- **ERROR ×2 (tooling)** ⇒ M-1 escape hatch: tooling defect Issue + staged-partial record close (FR-021).
