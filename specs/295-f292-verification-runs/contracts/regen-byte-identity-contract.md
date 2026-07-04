# SARIF-Regen Byte-Identity Contract (US-3, P1)

**Feature**: #295 | **Enforces**: SC-015 clause b (narrowed) for `examples/multi-tenant-rag-app/` | **Structural gate**: exists only if FR-011 passed at commit time (FR-018 — T026 gate failure defers this whole contract to the follow-up defect Issue, not a US-3 failure)

## 1. Assertion

`tests/scripts/test_sarif_regen_identity.py` MUST:

1. importlib-load `scripts/generate-threats-sarif.py` (hyphenated filename — `test_affected_assets_wiring.py:520-536` pattern).
2. Regenerate SARIF from the committed `examples/multi-tenant-rag-app/threats.md` (via `main()`-equivalent path or CLI subprocess — implementer's choice, but the input MUST be the committed file, unmodified).
3. Assert `read_bytes()` equality against the committed `examples/multi-tenant-rag-app/threats.sarif`.
4. **Fail closed**: missing input file, missing committed SARIF, zero findings parsed, or generator exception ⇒ test FAILURE (never skip, never vacuous pass).
5. No `SOURCE_DATE_EPOCH` dependency — the generator is timestamp-free (determinism is structural; ADR-021's mechanism is Typst-only). The test MUST NOT claim otherwise in comments/docstrings.

## 2. Scope boundary (MUST be stated in the delivery PR body — FR-017)

- **Covers**: SARIF-regen byte-identity for the `multi-tenant-rag-app` baseline only.
- **Deliberately does NOT cover**: PDF byte-identity; `BASELINE_EXAMPLES` membership (PDF suite + F-142 all-`agentic_pattern: none` gate — multi-agent example carve-out, mermaid-agentic-app precedent); `risk-scores.sarif` regen (generator has no CLI, hardcoded paths, ≥80-finding gate — enhancement Issue filed under FR-011).

## 3. CI wiring (D-B — the check MUST actually execute in CI)

New dedicated workflow `.github/workflows/tachi-sarif-regen.yml`, `tachi-catalog-drift.yml` pattern:

- Single `ubuntu-latest` runner (OS-independent assertion — single-runner is load-bearing, not a cost saving); `permissions: contents: read`; `pip install 'pytest>=8' 'pytest-timeout>=2'` (+`pyyaml` only if the assembler-free test needs it); direct pytest invocation of the module.
- Triggers: `pull_request` + `push: branches: [main]` via ONE shared paths anchor (post-#338 FR-006 pattern).
- **Paths anchor (lock-step, one commit — ADR-039 D-6 / KB Entry 3)**, exactly:
  1. `tests/scripts/test_sarif_regen_identity.py`
  2. `scripts/generate-threats-sarif.py`
  3. `scripts/sarif_common.py`
  4. `examples/multi-tenant-rag-app/threats.md`
  5. `examples/multi-tenant-rag-app/threats.sarif`
  6. `.github/workflows/tachi-sarif-regen.yml`

## 4. Relation to FR-014 covering assertion (P0, separate — D-C)

The URI-derivation assertion lives in `tests/scripts/test_affected_assets_wiring.py` (existing 15-module gate) and lands with the enabler regardless of US-3's fate; `scripts/generate-threats-sarif.py` joins `tachi-pytest.yml`'s `&hardening_paths` in that same P0 commit. This contract's workflow is the *additional* end-to-end guard.

## 5. Legitimate-change protocol (golden-file discipline)

When the generator legitimately changes output shape: regenerate `threats.sarif` from the committed `threats.md` in the SAME commit as the generator change (the test enforces this by failing otherwise). Never hand-edit the committed SARIF; never regenerate `threats.md` itself to satisfy the test (it is the LLM-authored source of truth — ADR-046 D1 tier boundary).
