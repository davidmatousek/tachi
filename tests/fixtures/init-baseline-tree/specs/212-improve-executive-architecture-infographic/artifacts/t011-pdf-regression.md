# T011 — PDF Byte-Identity Regression on Zero-Finding Fixture

**Status**: PASS

**Date/time of run**: 2026-04-25 15:20:47 UTC

**Task**: Verify that the F-128 → F-212 contract is preserved on zero-qualifying-findings input. Regenerated PDF on `tests/scripts/fixtures/exec_arch/no_critical_high/threats.md` under `SOURCE_DATE_EPOCH=1700000000` and `cmp`'d against the Wave 0 baseline.

**Acceptance criteria**: FR-212-22, SC-212-7. Required outcome — zero byte differences.

## Environment

| Component | Path / Version |
|-----------|----------------|
| Branch | `212-improve-executive-architecture-infographic` |
| HEAD at run | `045ccce chore(212): checkpoint before build resume` |
| Python | `/Users/david/.local/share/uv/python/cpython-3.12.11-macos-aarch64-none/bin/python3` (3.12.11) |
| Typst | `/opt/homebrew/bin/typst` |
| Working dir | `/tmp/t011-regen/` (input + output staging) |
| `SOURCE_DATE_EPOCH` | `1700000000` (matches baseline T002 capture) |

## Input fixture

`tests/scripts/fixtures/exec_arch/no_critical_high/threats.md` — single Spoofing finding (S-1, LOW/LOW), no Critical/High findings. Three Recommended Actions rows (S-1 Medium, S-2 Low, S-3 Note), but zero qualifying for callouts. Therefore `threat-executive-architecture.jpg` is absent → `has-executive-architecture` resolves false → exec-architecture page omitted entirely.

## Commands executed

```bash
mkdir -p /tmp/t011-regen
cp tests/scripts/fixtures/exec_arch/no_critical_high/threats.md /tmp/t011-regen/threats.md

SOURCE_DATE_EPOCH=1700000000 \
  /Users/david/.local/share/uv/python/cpython-3.12.11-macos-aarch64-none/bin/python3 \
  scripts/extract-report-data.py \
  --target-dir /tmp/t011-regen \
  --output templates/tachi/security-report/report-data.typ \
  --template-dir templates/tachi/security-report/

# Output: "Tier 3 selected, parsing artifacts..." / "report-data.typ generated (3 findings, Tier 3)"

SOURCE_DATE_EPOCH=1700000000 \
  /opt/homebrew/bin/typst compile \
  templates/tachi/security-report/main.typ \
  /tmp/t011-regen/security-report.pdf \
  --root .

cp /tmp/t011-regen/security-report.pdf /tmp/regen-zero-finding.pdf

cmp -s specs/212-improve-executive-architecture-infographic/artifacts/baseline-zero-finding.pdf \
       /tmp/regen-zero-finding.pdf
# Exit: 0
```

## Result — PASS

`cmp -s` exited **0** (byte-identical, no first-difference offset to report).

`cmp` (verbose, no flags) also exited **0** with no output.

### File sizes

| File | Bytes |
|------|-------|
| `specs/212-*/artifacts/baseline-zero-finding.pdf` | 1,107,679 |
| `/tmp/regen-zero-finding.pdf` | 1,107,679 |

### SHA-256 hashes

| File | SHA-256 |
|------|---------|
| Baseline | `1ff48532f301114c463bd39babbff726a3857d9a71a7c37103fde835b625d458` |
| Regenerated | `1ff48532f301114c463bd39babbff726a3857d9a71a7c37103fde835b625d458` |

Hashes match exactly — confirming byte-identical output.

## Interpretation

The F-128 skip-behavior contract is preserved through the F-212 changes already landed on the branch (Waves 0–2: T001-T008, T012-T015, T021-T022). Specifically:
- Wave 2 prompt rewrite (T007/T008) modified the Gemini prompt in `.claude/skills/tachi-infographics/references/executive-architecture.md` and the verbatim-lock note in `gemini-prompt-construction.md`. Neither file is read by the PDF assembly path; the prompt is consumed only at image-generation time, so the PDF rendering path is unaffected.
- The zero-finding fixture has zero qualifying Critical/High findings → no exec-arch image gets generated → `has-executive-architecture` is false → the page is conditionally omitted in `main.typ`. Therefore the algorithm changes pending in T016/T017 (US2 callout rework) cannot influence this fixture's PDF output, even if landed concurrently.
- Both runs share `SOURCE_DATE_EPOCH=1700000000`, eliminating timestamp-based non-determinism (PDF metadata, font subset embedding hints).

The FR-212-22 / SC-212-7 regression gate **holds**. Wave 3 Lane 3A T011 is cleared.

## Forward gate references

- **T031** (US3 Phase 6): re-run this same regression after the L3 payload extension lands. The expected result is identical (PASS, byte-identical).
- **Delivery gate**: this regression must continue to pass through the squash-merge of PR #213 to `main`.
