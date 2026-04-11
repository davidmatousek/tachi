# Quickstart: Loud-Failure Preflight Gate for mmdc (F-130)

**Audience**: Developers verifying F-130 locally, reviewers validating the PR, and anyone reproducing the underlying bug to confirm the fix holds.

**Prerequisites**:
- tachi repository checked out on branch `130-prd-130-fix` (or after merge, on `main`)
- Python 3.11+, `pytest`, `typst` CLI on `PATH`
- For the happy path (sections c and d): `@mermaid-js/mermaid-cli` (`mmdc`) installed globally via `npm install -g @mermaid-js/mermaid-cli`

This quickstart walks through the four validation paths required by F-130:

1. Reproduce the silent-failure bug on a shell without `mmdc` (pre-fix behavior).
2. Validate the loud-failure behavior on a shell without `mmdc` (post-fix behavior).
3. Validate the happy path still passes the 5 byte-deterministic PDF baselines (zero regression).
4. Regenerate an example's PDF and `.baseline` file (for future releases).

Cross-references:
- [spec.md](spec.md) — user stories US1/US2/US3 and FR-130.1 canonical error message
- [plan.md](plan.md) — Phase 1 Design, Quickstart outline (authoritative)
- [`docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md`](../../docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md) — CLI-prerequisite posture decision
- [`docs/architecture/02_ADRs/ADR-021-deterministic-pdf-comparison.md`](../../docs/architecture/02_ADRs/ADR-021-deterministic-pdf-comparison.md) — `SOURCE_DATE_EPOCH` reproducibility rationale

---

## (a) Local reproduction of the bug

Show the developer how to reproduce the silent failure on a shell where `mmdc` has been removed from `PATH`. This simulates a fresh developer machine or CI runner that lacks the Mermaid CLI.

Start from the repo root:

```bash
cd /path/to/tachi
```

Remove `mmdc` from `PATH` for the current shell only (this does not uninstall it):

```bash
export PATH=$(echo "$PATH" | tr ':' '\n' | grep -v mmdc | tr '\n' ':')
which mmdc    # expect: no output, exit code 1
```

Run the data-extraction script on an example that ships attack trees:

```bash
python3 scripts/extract-report-data.py \
  --target-dir examples/mermaid-agentic-app/ \
  --output /tmp/out.typ \
  --template-dir templates/tachi/security-report/
```

**Before F-130** (pre-fix, on `main` prior to commit `db0073c`):
- Exit code: `0` (the pipeline lied — it claimed success)
- `render_mermaid_to_png()` printed a warning to stderr and set `has_image = False` on every attack tree
- Downstream, `templates/tachi/security-report/attack-path.typ` silently rendered raw Mermaid source as plain text inside a `block(...)` fallback
- Final PDF: board-ready cover, professional styling, and attack path pages containing unrendered `graph TD` / `flowchart LR` source code where diagrams should have been. This is the production incident that motivated F-130.

**After F-130** (this branch):
- Exit code: non-zero (pipeline aborts at preflight)
- Stderr contains the canonical three-line error message exactly as emitted by `scripts/extract-report-data.py::render_mermaid_to_png()`:

  ```
  Attack path rendering requires @mermaid-js/mermaid-cli (mmdc).
  Install with: npm install -g @mermaid-js/mermaid-cli
  Then re-run /tachi.security-report.
  ```

- No PDF is produced. No silent fallback is attempted.

---

## (b) Validation after the fix

Confirm that the loud-failure behavior is wired up correctly. Three independent checks: the unit test suite, a shell-level invocation on a `mmdc`-stripped `PATH`, and a stderr grep for the canonical tokens.

### b.1 Preflight unit tests

```bash
pytest tests/scripts/test_mmdc_preflight.py -v
```

**Expected**: `9 passed`. The suite covers four preflight cases (including the edge case where `attack_trees` is empty) plus five mid-render aggregator cases that assert distinct `RuntimeError` shapes for preflight vs. mid-render failures (architect refinements R5 and R7).

### b.2 Shell-level abort check

Still on a shell with `mmdc` removed from `PATH` (see section (a)):

```bash
python3 scripts/extract-report-data.py \
  --target-dir examples/mermaid-agentic-app/ \
  --output /tmp/out.typ \
  --template-dir templates/tachi/security-report/ \
  2> /tmp/stderr.txt
echo "exit=$?"
```

**Expected**: `exit=1` (or any non-zero). `/tmp/out.typ` is either absent or partial — it is NOT a shippable artifact.

### b.3 Canonical-token grep

```bash
grep "@mermaid-js/mermaid-cli" /tmp/stderr.txt
grep "npm install -g @mermaid-js/mermaid-cli" /tmp/stderr.txt
grep "Attack path rendering" /tmp/stderr.txt
```

**Expected**: each `grep` prints one matching line and exits `0`. All three canonical tokens (FR-130.1) must be present in the stderr output.

---

## (c) Happy path validation with baseline test

Once the loud-failure path is confirmed, prove the fix introduces zero byte-level regression on the deterministic baselines. This is the guardrail that protects the 5 unchanged examples from the F-130 refactor.

Restore `mmdc` to `PATH` (open a new shell, or run `hash -r` after reinstalling), and confirm it is available:

```bash
which mmdc          # expect: a path, e.g. /usr/local/bin/mmdc
mmdc --version      # expect: a version number, e.g. 10.x.x
```

Run the backward-compatibility test under the reproducibility epoch:

```bash
SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py -v
```

**Expected**: `5 passed`. The test is parametrized over `BASELINE_EXAMPLES`:

1. `web-app`
2. `microservices`
3. `ascii-web-api`
4. `mermaid-agentic-app`
5. `free-text-microservice`

Each case extracts report data, compiles the PDF under `SOURCE_DATE_EPOCH=1700000000`, and compares the output byte-for-byte against the committed `security-report.pdf.baseline`. A single non-zero `cmp` would fail the test.

**Baseline artifacts** (R9 guardrail — architect refinement, High priority):

- [`.aod/results/130-baseline-pretest.md`](../../.aod/results/130-baseline-pretest.md) — pre-refactor snapshot captured by T002 before any F-130 code change
- [`.aod/results/130-baseline-posttest.md`](../../.aod/results/130-baseline-posttest.md) — post-refactor snapshot captured by T022 after US1/US2 implementation

Both files record the same 5/5 pass state. If this test ever regresses mid-refactor, compare the two result files first to localize which example drifted.

---

## (d) Regeneration instructions

When a code change legitimately alters PDF output (font changes, layout tweaks, new template features, infographic updates), the corresponding `.baseline` files must be regenerated in the same commit as the code change. F-130 itself regenerated `examples/mermaid-agentic-app/security-report.pdf.baseline` under T020 because the attack path pages now render real diagrams (previously they were silent fallback blocks — byte-different, intentionally).

### When to regenerate

- After a code change that affects rendering output (Typst template edits, `extract-report-data.py` output-schema changes, new infographic templates)
- At release time, to freeze a new baseline set for a tagged version
- Never as a shortcut to "make the test pass" without understanding why the output changed — the regeneration commit message must explain the drift

### How to regenerate a single example

For `<example>` in `{web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice}`:

```bash
SOURCE_DATE_EPOCH=1700000000 python3 scripts/extract-report-data.py \
  --target-dir examples/<example>/ \
  --output templates/tachi/security-report/report-data.typ \
  --template-dir templates/tachi/security-report/ && \
SOURCE_DATE_EPOCH=1700000000 typst compile \
  templates/tachi/security-report/main.typ \
  examples/<example>/security-report.pdf \
  --root .
```

Then promote the fresh PDF to the new baseline:

```bash
cp examples/<example>/security-report.pdf examples/<example>/security-report.pdf.baseline
```

### Verify byte-identity after regeneration

Re-run the compile a second time and compare against the new baseline to confirm determinism:

```bash
SOURCE_DATE_EPOCH=1700000000 python3 scripts/extract-report-data.py \
  --target-dir examples/<example>/ \
  --output templates/tachi/security-report/report-data.typ \
  --template-dir templates/tachi/security-report/
SOURCE_DATE_EPOCH=1700000000 typst compile \
  templates/tachi/security-report/main.typ \
  /tmp/<example>-verify.pdf \
  --root .
diff <(xxd examples/<example>/security-report.pdf.baseline) <(xxd /tmp/<example>-verify.pdf)
```

**Expected**: `diff` prints nothing and exits `0`. If `diff` reports differences, the pipeline is non-deterministic under the epoch and the baseline cannot be safely committed — investigate before proceeding (see ADR-021).

### Committing the update

Per T020 convention, the regenerated `.baseline` file MUST be committed in the **same commit** as the code change that caused the drift. The commit message must explicitly reference the regeneration and name the affected example(s), e.g.:

```
fix(130): regenerate mermaid-agentic-app baseline after attack path fix

Attack path pages now render real Mermaid diagrams via mmdc instead
of falling back to raw source blocks. Baseline PDF updated accordingly
under SOURCE_DATE_EPOCH=1700000000 per ADR-021.

Refs #130
```

### Regenerating all 5 baselines at once

If a global change (e.g., a shared template edit) affects every example, regenerate the full set with the existing Makefile target:

```bash
SOURCE_DATE_EPOCH=1700000000 make examples
```

Then spot-check with the backward-compat test:

```bash
SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py -v
```

**Expected**: `5 passed` against the freshly regenerated baselines. Commit all 5 `.baseline` updates together with the code change.

---

## Acceptance summary

F-130 is ready for `/aod.deliver` when all four quickstart sections pass on a clean checkout:

- [ ] (a) Pre-fix bug is reproducible on `main` prior to commit `db0073c` (historical check; not required on this branch)
- [ ] (b) `pytest tests/scripts/test_mmdc_preflight.py -v` reports `9 passed` on this branch
- [ ] (b) Shell-level abort on `mmdc`-stripped `PATH` exits non-zero with all three canonical tokens in stderr
- [ ] (c) `SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py -v` reports `5 passed` (matches `.aod/results/130-baseline-posttest.md`)
- [ ] (d) The regeneration command runs deterministically: re-running twice produces byte-identical PDFs under the same epoch
