# ADR-021: SOURCE_DATE_EPOCH for Deterministic PDF Comparison

**Status**: Accepted
**Date**: 2026-04-09
**Deciders**: Architect, DevOps agent (root-cause isolation), Orchestrator
**Related Feature**: Feature 128 — Executive Threat Architecture Infographic

---

## Context

Feature 128 introduced a backward-compatibility test harness (`tests/scripts/test_backward_compatibility.py`, T024) that must guarantee the tachi PDF generation pipeline produces **byte-identical output** for 5 unmodified example projects before and after the feature's additive changes. The harness compares a fresh pipeline run against committed `examples/*/security-report.pdf.baseline` files using `cmp`. If any byte differs, the test fails.

During Wave 2 baseline generation (T003c), the DevOps agent discovered that running the extraction + Typst pipeline **twice against identical inputs** produces **non-byte-identical PDFs**. Root-cause isolation revealed that Typst's PDF generator embeds wall-clock timestamps in:

1. **PDF metadata**: `/ModDate` and `/CreationDate` in the document dictionary
2. **XMP metadata**: `xmp:CreateDate`, `xmp:ModifyDate`, `xmp:MetadataDate` stream entries
3. **Derived fields**: `xmpMM:InstanceID` (derived from the creation timestamp)

All non-metadata bytes — page streams, fonts, images, cross-reference tables — are identical between runs. Only the timestamp-derived fields differ. This is a **documented property of Typst's default behavior**, not a bug in the tachi pipeline.

Without a fix, `test_backward_compatibility.py` could never pass, and the backward-compatibility guarantee for Feature 128 could not be asserted.

---

## Decision

**We adopt `SOURCE_DATE_EPOCH=1700000000` (the reproducible-builds.org standard environment variable) as the fixed-value convention for all baseline generation and all backward-compatibility test runs.**

**Scope**:
- Baseline generation (F-128 Wave 2, `examples/*/security-report.pdf.baseline`): set `SOURCE_DATE_EPOCH=1700000000` before `typst compile`.
- Backward-compatibility test (`tests/scripts/test_backward_compatibility.py`): set `SOURCE_DATE_EPOCH=1700000000` in the subprocess environment before invoking the pipeline.
- **Production usage is UNCHANGED**: real users running `/tachi.security-report` continue to get PDFs with wall-clock timestamps. The environment variable is set **only** on the test path.

**Value**: `1700000000` = 2023-11-14 22:13:20 UTC. Any fixed value would work; the specific number is arbitrary but must be consistent between baseline generation and test runs.

---

## Rationale

1. **Industry standard**: `SOURCE_DATE_EPOCH` is the [reproducible-builds.org convention](https://reproducible-builds.org/specs/source-date-epoch/) honored by gcc, cargo, Python setuptools, Debian packaging, and Typst. Adopting a well-known convention is lower risk than inventing a bespoke mechanism.
2. **Zero source-code changes**: The fix lives entirely in test fixtures and CI wrappers. `scripts/extract-report-data.py`, `main.typ`, `templates/tachi/security-report/*.typ`, and all tachi runtime code are untouched. No maintenance burden on the runtime pipeline.
3. **Preserves byte-identical comparison semantics**: The test can still use `cmp` to detect real regressions in page content, layout, or structure. It does not weaken the backward-compatibility guarantee — it removes only the environmental noise (wall-clock timestamps) that was masking the signal.
4. **Production behavior unchanged**: Real users of `/tachi.security-report` get PDFs with accurate creation timestamps, which is the correct default for security reports (timestamp provenance matters for audit).
5. **Verified empirically**: The DevOps agent ran the full pipeline twice with `SOURCE_DATE_EPOCH=1700000000` and confirmed all 5 example PDFs become byte-deterministic across runs. Without the env var, the same two runs produce differing PDFs.
6. **Composable with other determinism guarantees**: `scripts/extract-report-data.py` already produces byte-identical JSON/Typst data for identical inputs (Feature 071, [ADR-017](./ADR-017-deterministic-infographic-extraction.md)). `SOURCE_DATE_EPOCH` extends that same guarantee to the final Typst compile step.

---

## Alternatives Considered

### Alternative 1: Modify the Pipeline to Strip or Normalize PDF Metadata Post-Compile

**Pros**:
- Full control over the comparison surface
- No environment variable dependency

**Cons**:
- Requires modifying `scripts/extract-report-data.py` or adding a post-processing step
- Couples tachi to a specific PDF library for metadata manipulation
- Higher review surface and maintenance burden
- Risks breaking on future Typst upgrades that reshape metadata

**Why Not Chosen**: High complexity for a test-path-only concern. Invasive changes to runtime code for a developer-only test contract violates the separation between runtime and test infrastructure.

### Alternative 2: Fuzzy PDF Comparison (Diff Content, Ignore Metadata)

**Pros**:
- No environment variable required
- Allows production-like PDFs in baselines

**Cons**:
- Requires custom PDF parsing tooling to identify "content" vs "metadata" bytes
- Weakens the backward-compatibility guarantee — any future PDF library update could change metadata location or format, silently masking real regressions
- The line between "metadata" and "content" is PDF-specification-dependent and fragile

**Why Not Chosen**: Weakens the test guarantee and adds custom tooling that would become maintenance burden. `cmp`-based byte-exact comparison is the strongest contract possible, and `SOURCE_DATE_EPOCH` preserves it.

### Alternative 3: Generate Baselines in CI from the Parent Revision at Test Time

**Pros**:
- No committed binary baseline files
- Baselines always match the current upstream state

**Cons**:
- Couples the test to git history and network access
- Local test runs become slow and fragile (checkout, build, discard)
- Obscures test intent (baseline is no longer reviewable in PR diffs)

**Why Not Chosen**: Violates the F-128 Decision 1 choice (committed `.baseline` files) which was already approved for repeatability, self-containment, and traceability. This alternative replaces one problem with several worse ones.

---

## Consequences

### Positive

- Backward-compatibility test is stable across developer laptops, CI runners, and post-merge audits
- Real regressions are detected immediately (page content changes, layout drift, structural changes)
- Zero runtime code changes — production PDFs remain fully timestamped
- Establishes a reusable convention: any future test that needs deterministic PDF output can set the same environment variable
- Composable with the Feature 071 extraction determinism guarantee ([ADR-017](./ADR-017-deterministic-infographic-extraction.md))

### Negative

- Tests must remember to set `SOURCE_DATE_EPOCH` before invoking the pipeline (documented in test fixture setup; failures are loud and immediate)
- Baseline PDFs embed a fake timestamp (2023-11-14) rather than their true generation date — noted in the `.baseline` file naming convention and PR descriptions
- Future contributors adding new `.baseline` files must use the same fixed epoch value (convention documented in `tests/scripts/README.md` and the Tech Stack doc)

### Mitigation

- `tests/scripts/test_backward_compatibility.py` sets `SOURCE_DATE_EPOCH` at fixture scope, not in each test function — single point of truth
- Baseline generation is manually gated (`make test-baseline-regenerate` or equivalent); contributors cannot accidentally commit a non-deterministic baseline because the test itself would immediately fail
- `.baseline` files are reviewed in PR diffs via size + checksum; any unintended change surfaces during code review

---

## Related Decisions

- **F-128 Decision 1**: Baseline PDF Storage via committed `.baseline` files — this ADR provides the determinism prerequisite for that choice to work
- **F-128 Decision 3**: Original SOURCE_DATE_EPOCH escalation and devops root-cause analysis (captured in `specs/128-prd-128-executive/decisions.md`)
- [ADR-017: Deterministic Infographic Extraction](./ADR-017-deterministic-infographic-extraction.md) — extraction-side determinism; this ADR is the compile-side counterpart
- [ADR-014: Gemini API as Optional, Best-Effort Image Generation](./ADR-014-gemini-api-optional-image-generation.md) — baseline determinism applies only to the 5 examples without the new executive-architecture JPEG; the 6th example (agentic-app) is intentionally regenerated

---

## References

- [reproducible-builds.org SOURCE_DATE_EPOCH specification](https://reproducible-builds.org/specs/source-date-epoch/)
- [Typst documentation on reproducible builds](https://github.com/typst/typst/blob/main/docs/reference/foundations/datetime.md)
- `specs/128-prd-128-executive/decisions.md` — Decision 3 for root-cause analysis and empirical verification
- `tests/scripts/test_backward_compatibility.py` — the consuming test harness
- `examples/*/security-report.pdf.baseline` — the committed baselines this decision enables

---

**Status Note**: Accepted 2026-04-09 during Feature 128 implementation. No superseding decisions anticipated — reproducible-builds is a stable industry convention and Typst support is upstream-maintained.
