# Contract: CA-Baseline Fingerprint Sidecar (Feature 329 / OQ-1)

**Feature**: 329 · **Date**: 2026-06-30 · Authority: ADR-037 D-9 (CA-page baseline regen lane), ADR-021 (`SOURCE_DATE_EPOCH` determinism). Supersedes nothing; complements `specs/185-cwe-catalog-expansion/contracts/baseline-regen.contract.md` (the recipe this feature scripts).

## Purpose

Define the **sidecar** artifact, the **fingerprint algorithm**, and the **regen-emission contract** that make the catalog-drift guard cheat-resistant. This file is the data-model for the feature (no relational model exists — the sidecar JSON *is* the schema).

## 1. Sidecar artifact

- **Path**: `examples/ca-baseline-fingerprints.json` (co-located with the 6 `examples/*/security-report.pdf.baseline` files it tracks). *(Architect may relocate; the guard and regen script reference a single constant.)*
- **Producer**: ONLY `scripts/regenerate-ca-baselines.sh` (via `python3 scripts/check-catalog-drift.py --emit`). **Never hand-edited** (OQ-1 cheat-resistance — Risk-1).
- **Consumer**: `scripts/check-catalog-drift.py --check` and `tests/scripts/test_catalog_drift_guard.py::test_live_tree_fingerprints_match_sidecar`.
- **Format**: JSON (stdlib `json`, `sort_keys=True`, `indent=2`, trailing newline) — deterministic, zero-dependency, easy fail-closed parse (FR-008).

### Schema

```json
{
  "_generated_by": "scripts/regenerate-ca-baselines.sh (do not hand-edit; advance only by re-running the regen)",
  "source_date_epoch": "1700000000",
  "frameworks": {
    "owasp":        { "raw_fingerprint": "<sha256-hex>", "in_scope_fingerprint": "<sha256-hex>", "raw_count": <int>, "in_scope_count": <int> },
    "mitre-attack": { "raw_fingerprint": "<sha256-hex>", "in_scope_fingerprint": "<sha256-hex>", "raw_count": <int>, "in_scope_count": <int> },
    "mitre-atlas":  { "...": "..." },
    "nist-ai-rmf":  { "...": "..." },
    "cwe":          { "...": "..." }
  }
}
```

- `frameworks` keys are **exactly** the live `ORDERED_FRAMEWORKS` members at emit time (dynamic — FR-004). The guard treats a live member **absent** from `frameworks` as drift (fail-closed, FR-008).
- `source_date_epoch` is informational provenance (the epoch the baselines were rendered under); the guard does not depend on it for the comparison (the guard renders nothing — NFR-001).

## 2. Fingerprint algorithm (FR-001)

For member `fw`, with `records = _load_framework_yaml_records(fw)` (raw, YAML order) and `in_scope = _load_framework_yaml_records(fw, in_scope_only=True)`:

```
# C-2 (Architect): mirror the loader's isinstance guard so a malformed non-dict
# top-level record fails CLOSED (deterministic marker → detected as drift) rather
# than raising AttributeError on .get(). raw mode is not isinstance-filtered upstream.
canonical(record) = [record.get("id"), bool(record.get("out_of_scope", False))] if isinstance(record, dict) \
                    else ["<non-dict>", repr(record)]
serialize(seq)    = json.dumps([canonical(r) for r in seq], ensure_ascii=False, separators=(",", ":"))
raw_fingerprint       = sha256(serialize(records).encode("utf-8")).hexdigest()
in_scope_fingerprint  = sha256(serialize(in_scope).encode("utf-8")).hexdigest()
raw_count             = len(records)
in_scope_count        = len(in_scope)
```

**Invariants**:
1. **Order preserved, never sorted** — YAML document order is what renders onto the CA page; sorting would mask a reorder that changes the rendered rows.
2. **Reuse, not re-implement** — `records`/`in_scope` come from the renderer's own loader (imported via `importlib` from the hyphenated `scripts/extract-report-data.py`), so the guard's coupling notion is the renderer's by construction. No bespoke YAML walk (FR-001, code-economy rung 2).
3. **`raw` ⊇ `in_scope` coverage** — `raw_fingerprint` catches add/remove of any record and any `out_of_scope` flip (HIGH-3); `in_scope_fingerprint` catches in-scope add/remove and ID rename/swap at constant count (HIGH-2). Both stored so the failure message (FR-006) can say which partition drifted.
4. **Counts are summary-only** — `raw_count`/`in_scope_count` exist for the human-readable message; the comparison keys on the fingerprints, never the bare counts (the count-neutral #333 case passes because both fingerprints are unchanged — FR-003).

## 3. Drift determination (`--check`)

```
live     = { fw: fingerprint(fw) for fw in ORDERED_FRAMEWORKS }   # dynamic
sidecar  = read_sidecar(path)                                     # FAIL CLOSED if missing/partial/unparseable
drift    = [ fw for fw in live
             if fw not in sidecar["frameworks"]
             or live[fw].raw_fingerprint      != sidecar[fw].raw_fingerprint
             or live[fw].in_scope_fingerprint != sidecar[fw].in_scope_fingerprint ]
exit 1 + message(drift)  if drift else exit 0
```

**Fail-closed (FR-008)**: a missing file, a JSON parse error, a missing `frameworks` key, or any live member absent from `frameworks` ⇒ **drift/failure**, never a pass. Deleting or truncating the sidecar cannot silence the guard (Risk-5).

**Failure message (FR-006)** — per drifted framework, on stderr:
```
catalog-drift: <fw> render-coupled fingerprint changed without a CA-baseline regen.
  in_scope: <N_expected> -> <N_live> records  (fingerprint <exp8>… -> <live8>…)
  raw:      <M_expected> -> <M_live> records  (fingerprint <exp8>… -> <live8>…)
Fix: regenerate the 6 CA baselines AND emit the sidecar:
  scripts/regenerate-ca-baselines.sh        # see specs/185-*/contracts/baseline-regen.contract.md (ADR-037 D-9)
```

## 4. Regen-emission contract (FR-002 / OQ-1)

`scripts/regenerate-ca-baselines.sh` is the **single canonical place** CA baselines are produced. Sequence (mirrors `baseline-regen.contract.md` exactly, then emits):

```
export SOURCE_DATE_EPOCH=1700000000
for name in web-app microservices ascii-web-api mermaid-agentic-app free-text-microservice maestro-reference; do
  python3 scripts/extract-report-data.py --target-dir examples/$name \
    --output templates/tachi/security-report/report-data.typ \
    --template-dir templates/tachi/security-report
  typst compile templates/tachi/security-report/main.typ \
    examples/$name/security-report.pdf.baseline --root .
done
git checkout -- templates/tachi/security-report/report-data.typ   # D-9 invariant 5 (no residue)
python3 scripts/check-catalog-drift.py --emit                     # FINAL STEP — writes the sidecar
```

**Why emission is the last step**: the sidecar becomes a genuine byproduct of regeneration — a developer cannot advance the expected fingerprints without re-rendering the baselines (Risk-1). A hand-maintained manifest was evaluated and **declined** (it forfeits this property); if ever adopted, the trade is recorded in the ADR-037 amendment.

**Determinism boundary**: this script (and the T001 pre-state) are the ONLY places rendering/`typst` runs. Neither the guard (`--check`) nor any CI-triggered job renders or hits the network (NFR-001 / ADR-021).

## 5. Acceptance (maps to spec SC + FR-007)

- `--emit` on a clean tree writes a sidecar whose fingerprints equal the live ones → `--check` exits 0 (SC-001 clean case).
- A grow / ID-swap / `out_of_scope`-flip without re-emit → `--check` exits 1 naming the framework (SC-001 / HIGH-2 / HIGH-3).
- A citation-string-only edit (no `(id, out_of_scope)` change) and a non-member (`nist-ai-600-1`) change → `--check` exits 0 (SC-004 / FR-003 / #333 class).
- Missing/partial/unparseable sidecar → `--check` exits 1 (FR-008).
- Synthetic test covers all six cases, each calling `_load_framework_yaml_records.cache_clear()` (Risk-3).
