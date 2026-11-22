# Quickstart: verifying F-374

How a builder, reviewer or tester exercises this bundle. Two rules apply to every step:
- **Never run pytest, the extractors or the renderers in the main checkout.** They re-render tracked example PNGs (#365). Use a scratch clone of the committed branch tip.
- **Commit before you gate.** The gated harnesses clone the committed HEAD.

## 1. Offline suite (deterministic claims; no model)

```bash
git clone --branch 374-large-architecture-pipeline-resilience <repo-url> /tmp/f374-check
cd /tmp/f374-check
python3 -m pytest tests/scripts/test_tachi_parts.py tests/scripts/test_tachi_stage.py \
  tests/scripts/test_fixture_374.py tests/scripts/test_runtime_floor_374.py \
  tests/scripts/test_contract_text_374.py tests/scripts/test_render_risk_scores.py \
  tests/scripts/test_render_compensating_controls.py tests/scripts/test_sarif_identity.py
```

PR 2 adds `test_threats_md_join.py`, `test_threats_sarif.py`, `test_chain_script.py`, `test_threat_model_checks.py` and `test_report_assembly.py`. CI runs the same lists in `tachi-install-fidelity.yml`, in its `f374-offline` (3.11) and `f374-py39-floor` (3.9) jobs, and `f374-macos` runs `test_sarif_identity.py` alone (ADR-050 D16).

What the suite proves:
- **SC-4:** S-4's variants, including ruling A's tag-driven cases and ruling B's PR 1 ID-reuse case.
- **SC-5, offline half:** the controls fill-or-check under R-34.
- **SC-6:** the two-run identity model, per file.
- **The trust boundary:** the hostile-input cases (NFR-10).
- **S-11:** the core path with `yaml` blocked, and the 3.9 grammar check.

## 2. The synthetic fixture

```bash
python3 tests/scripts/generate_large_arch_fixture.py --out /tmp/f374-fixture --variant all
```

- **Determinism.** The same seed gives byte-identical outputs on Python 3.9 to 3.13 (S-4).
- **The committed copy** lives under `tests/scripts/fixtures/large_arch/`. The fixture test regenerates into a temporary directory and compares byte for byte. It never rewrites tracked files.
- **The sizing check** asserts that each targeted output is at least twice the 64k cap (UTF-8 bytes ÷ 4), and that every batched path gets at least two batches at S-1's sizes.

## 3. The pre-fix baseline (W1, before renderer code lands)

1. Install v4.48.4 into a scratch adopter with `scripts/install.sh --version v4.48.4`.
2. Copy in the fixture's precomputed `threats.md`, and run `/tachi.risk-score` once.
3. Record the overflow or dropped finding, and the per-output token estimates, in `test-results/prefix-baseline.md`. That is SC-1's baseline column.
4. Run the scorer and controls stages once on the shipped example named for SC-8 before this run, below both stages' batching thresholds, at the adopter default effort. If the post-fix run will double as R-27's smoke run, run this baseline under the session profile too. That is SC-8's baseline (P-7).

## 4. The live matrix (`[MANUAL-ONLY]`; W5 for PR 1, W5′ for PR 2)

- **Install** the branch build into a scratch adopter with `scripts/install.sh`. Never copy the adapter directory over `.claude/agents/tachi/` (R-17).
- **PR 1:**
  - `/tachi.risk-score` and `/tachi.compensating-controls` on the fixture, at the adopter default effort and at `effort=max` (R-18);
  - SC-8's run on the shipped example;
  - R-27's smoke run under the published session profile (`/tachi.threat-model` on a shipped example, then both stages), with a before-and-after write listing.
- **PR 2:** `/tachi.threat-model`, baseline-aware against the fixture's synthetic baseline, at the default effort. Its max run covers the report, unless TW-L1 fires (R-28).
- **Recording.** Each run goes in `test-results/live-<stage>-<effort>.md`, with:
  - the counts, batches, overflow events, retries and narrative fallback rate, from the stage record;
  - the wall time;
  - the output tokens, read from the session's usage records: what Claude Code reports for the whole stage, the command's turns and every subagent, thinking included (P-7). The stage record has no token field.

  For SC-8, the PR records each stage's delta against its baseline. Dispositions are decided in advance (TW-L2), with at most two attempts per stage and effort level. The SC-3 transcript audit is structure-only and stays private.

## 5. Optional: Code Scanning evidence

If W5 has room, upload the regroup pair's SARIF to a scratch repository with Code Scanning enabled, using the three categories (`threat-model`, `risk-score` and `compensating-controls`). Then record which alerts close and reopen. Otherwise the release notes say that the alert behavior is modeled from GitHub's documentation (D-7).
