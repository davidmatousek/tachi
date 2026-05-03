# T031 — PDF Byte-Identity Regression on Zero-Finding Fixture (Post-US3)

**Status**: PASS

**Date/time of run**: 2026-04-25 (Wave 5)

**Task**: Re-verify the F-128 → F-212 contract is preserved on zero-qualifying-findings input AFTER the L3 payload extension lands (Wave 4 US3). Same procedure as T011 (Wave 3 baseline) on the post-US3 codebase. FR-212-22 / SC-212-7 final regression gate before Phase 6.

**Acceptance criteria**: zero byte differences vs the Wave 0 baseline.

## Environment

| Component | Path / Version |
|-----------|----------------|
| Branch | `212-improve-executive-architecture-infographic` |
| HEAD at run | `bfde573 feat(212): wave 4 — US3 implementation (T023-T030) + iteration-3 final image` |
| Python | `/Users/david/.local/share/uv/python/cpython-3.12.11-macos-aarch64-none/bin/python3` (3.12.11) |
| Typst | `/opt/homebrew/bin/typst` |
| Working dir | `/tmp/t031-regen/` (input + output staging) |
| `SOURCE_DATE_EPOCH` | `1700000000` (matches baseline T002 + T011 capture) |

## Input fixture

`tests/scripts/fixtures/exec_arch/no_critical_high/threats.md` — same fixture used by T011 (Wave 3). Single Spoofing finding (S-1, LOW/LOW), no Critical/High findings. Three Recommended Actions rows. Zero qualifying for callouts → `threat-executive-architecture.jpg` is absent → `has-executive-architecture` resolves false → exec-architecture page omitted entirely from the assembled PDF.

## Commands executed

```bash
mkdir -p /tmp/t031-regen
cp tests/scripts/fixtures/exec_arch/no_critical_high/threats.md /tmp/t031-regen/threats.md

SOURCE_DATE_EPOCH=1700000000 \
  /Users/david/.local/share/uv/python/cpython-3.12.11-macos-aarch64-none/bin/python3 \
  scripts/extract-report-data.py \
  --target-dir /tmp/t031-regen \
  --output templates/tachi/security-report/report-data.typ \
  --template-dir templates/tachi/security-report/

# Output: "Tier 3 selected, parsing artifacts..." / "report-data.typ generated (3 findings, Tier 3)"

SOURCE_DATE_EPOCH=1700000000 \
  /opt/homebrew/bin/typst compile \
  templates/tachi/security-report/main.typ \
  /tmp/t031-regen/security-report.pdf \
  --root .

cmp -s specs/212-improve-executive-architecture-infographic/artifacts/baseline-zero-finding.pdf \
       /tmp/t031-regen/security-report.pdf
# Exit: 0
```

## Result — PASS

`cmp -s` exited **0** (byte-identical, no first-difference offset to report).

### File sizes

| File | Bytes |
|------|-------|
| `specs/212-*/artifacts/baseline-zero-finding.pdf` | 1,107,679 |
| `/tmp/t031-regen/security-report.pdf` | 1,107,679 |

### SHA-256 hashes

| File | SHA-256 |
|------|---------|
| Baseline (Wave 0) | `1ff48532f301114c463bd39babbff726a3857d9a71a7c37103fde835b625d458` |
| T011 regen (Wave 3) | `1ff48532f301114c463bd39babbff726a3857d9a71a7c37103fde835b625d458` |
| T031 regen (Wave 5, post-US3) | `1ff48532f301114c463bd39babbff726a3857d9a71a7c37103fde835b625d458` |

All three SHA-256 hashes are identical — confirming byte-identical output across the Wave 0 → Wave 3 → Wave 5 progression. Each F-212 wave (US1 prompt rewrite, US2 callout selection rework, US3 payload schema extension) is provably non-disruptive to the F-128 zero-finding skip-behavior contract.

## Interpretation

The F-128 skip-behavior contract is preserved through every F-212 wave on the branch:
- **Wave 2 prompt rewrite (T007/T008)**: Modified the Gemini prompt in `.claude/skills/tachi-infographics/references/executive-architecture.md` and the verbatim-lock note in `gemini-prompt-construction.md`. Neither file is read by the PDF assembly path.
- **Wave 3 US2 callout selection (T016/T017)**: Modified `_select_critical_high_callouts()` in `scripts/extract-infographic-data.py`. The zero-finding fixture has zero qualifying input → the function returns `[]` → no exec-arch page is generated → the algorithm changes cannot influence this fixture's PDF output.
- **Wave 4 US3 payload extension (T023-T030)**: Added `_build_flow_edges()` + `_build_clusters()` helpers and extended `_build_executive_architecture_payload()` return dict with `flow_edges` and `clusters` keys. The skip-on-zero-qualifying-findings path returns early at the `if not layers: return {"error": "no_scope_data"}` short-circuit (or downstream, the consumer skips image generation when total_qualifying == 0). Either way, `flow_edges`/`clusters` payload keys never reach the PDF assembler — Typst only consumes the binding booleans `has-executive-architecture` and `executive-architecture-image-path`. Even if those keys did reach Typst, the zero-finding fixture's `data_flows`/`trust_boundaries` arrays for the no_critical_high test are empty → `flow_edges == []` and `clusters == []` → no rendered output.
- **Determinism (ADR-017 + ADR-021)**: Both runs share `SOURCE_DATE_EPOCH=1700000000`, eliminating timestamp-based non-determinism (PDF metadata, font subset embedding hints).

The FR-212-22 / SC-212-7 regression gate **holds across all three user stories**. Wave 5 Lane 5A T031 is cleared.

## Forward gate references

- **Wave 6 (Phase 6)**: T035 full pytest regression, T036 PM final visual sign-off, T037 draft PR sync. The byte-identity result here is independent of those tasks.
- **Delivery gate**: this regression must continue to pass through the squash-merge of PR #213 to `main`. A regression fixture should be added in a follow-up to lock this byte-identity check into the automated test suite (currently exists as a manual replay procedure).
