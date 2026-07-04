# Data Model: F-292 Post-Merge Verification Runs (#295)

**Plan**: [plan.md](plan.md) | **Date**: 2026-07-03
No database or API entities — all entities are git-committed files and Issue records. Validation rules are the fail-closed gates.

## Entities

### 1. Pre-292 Anchor (immutable, read-only)
| Field | Value / Rule |
|---|---|
| Commit | `0629fa2~1` = `3f107e3` (immediate parent of F-292 squash; pushed main history) |
| Authoritative artifact | `examples/agentic-app/sample-report/threats.sarif` via `git show` |
| Cross-check artifact | `examples/agentic-app/threats.md` at same ref (§4+§7 tables only; 8 `\| OI-` rows) |
| Validation | OI extraction MUST yield exactly `{OI-1, OI-2, OI-3, OI-4}` (pre-verified 2026-07-03); anything else ⇒ gate ERROR |

### 2. OI Emission Record (the D-1 gate unit)
| Field | Source (anchor side) | Source (fresh side) | Gate role |
|---|---|---|---|
| `findingId` | `partialFingerprints["findingId/v1"]` | YAML block `id` → same SARIF field via assembler | **Hard gate** (set equality + count) |
| `sink/flow identity` | `locations[].logicalLocations[].name` (structural, primary) + `message.text` quoted flow names (secondary) | YAML block component/flow fields (schema v1.9) → same SARIF fields via assembler | **Hard gate** (identifier-level table comparison) |
| `message prose` | `message.text` full | YAML description/title | Drift bucket (LLM phrasing varies) |
| `properties.*` (severity, impact, likelihood, maestro-layer, owasp_id, tags, baselineState) | SARIF result properties | assembler-mapped | Drift bucket (attribution required) |
| Envelope/format bytes | LLM-authored SARIF | assembler-emitted SARIF | Drift bucket, standing class "assembler-tier envelope" |

**State transitions**: extracted → guarded (non-empty, cardinality) → gated (PASS/FAIL) → attributed (each non-gate delta → named class or FAIL) → recorded.

### 3. SC-003 Verification Record (`specs/295-f292-verification-runs/sc-003-verification-record.md`)
Required sections: commands (verbatim), anchor SHAs, corrected filter text, both OI subsets (committed as `anchor-oi-subset.json` / `fresh-oi-subset.json` + raw YAML findings), sink/flow identity table, diff output, attribution table, gate verdict, filings list. Invalid without ALL sections (fail-closed record).

### 4. Committed Evidence Baseline (`examples/multi-tenant-rag-app/`, root layout)
| Artifact | Authoring tier | Claims |
|---|---|---|
| `threats.md` | LLM (run byproduct, never hand-edited) | ≥1 Cat 6 `OI-*` finding (CWE-943); MAESTRO table all-7 rows; Affected Assets block present |
| `threat-report.md`, `risk-scores.md` | LLM | presence + run provenance |
| `risk-scores.sarif` | LLM | presence only — **NO regen claim** |
| `threats.sarif` | script (URI-corrected generator) | byte-identical regen from committed `threats.md` (FR-011); `uri` = `examples/multi-tenant-rag-app/threats.md` |
Exactness rule: the committed set is exactly these 5 files (attack-trees/chains/run-dir excluded).

### 5. Pre-state Record (`specs/295-f292-verification-runs/test-results/pre-state.md`)
Literal pass/skip/fail totals per D-E suite + corpus-coupling sweep results + inherited-red dispositions. MUST predate any artifact/enabler commit (git-history-checkable).

### 6. Purpose-built Regen Check (US-3, P1)
`tests/scripts/test_sarif_regen_identity.py` + `.github/workflows/tachi-sarif-regen.yml`. Contract: [contracts/regen-byte-identity-contract.md](contracts/regen-byte-identity-contract.md). Structural gate: exists only if FR-011 passed (FR-018).

### 7. Filed Issues (pre-decided dispositions)
| Trigger | Issue type | Always/conditional |
|---|---|---|
| Contract §3 dual defect (filter + invocation) | defect vs archived contract (OQ-4 disposition decided there) | ALWAYS (FR-008) |
| `generate-risk-scores-sarif.py` parameterization gap | enhancement | ALWAYS (FR-011) |
| D-1 gate FAIL / zero Cat 6 / regen mismatch | defect w/ evidence | conditional (FR-007, US-2 scenario 7) |
| 2× tooling failure | tooling defect + staged-partial close | conditional (M-1/FR-021) |
