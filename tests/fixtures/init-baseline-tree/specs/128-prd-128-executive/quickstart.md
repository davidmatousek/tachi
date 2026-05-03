# Quickstart: Executive Threat Architecture Infographic (F-128)

**Audience**: Developers implementing F-128 or testers validating it after merge.
**Prerequisites**: tachi repository checked out; Python 3.11+; Typst CLI installed; Gemini API access configured (for image generation).

This quickstart shows the end-to-end pipeline run for the new `executive-architecture` template against the canonical `agentic-app` example.

---

## Step 1: Verify input files exist

```bash
cd /path/to/tachi
ls examples/agentic-app/sample-report/
```

Expected files (pre-F-128 baseline):
- `threats.md` (required input)
- `risk-scores.md` (optional tier upgrade)
- `compensating-controls.md` (optional tier upgrade — takes precedence)
- `threat-baseball-card.jpg`, `threat-system-architecture.jpg`, `threat-risk-funnel.jpg` (existing infographics)

If `threats.md` is missing, run the threat model first:
```bash
/tachi.threat-model --architecture examples/agentic-app/architecture.md
```

## Step 2: Generate the executive-architecture infographic

```bash
/tachi.infographic --template executive-architecture --target-dir examples/agentic-app/sample-report/
```

This invokes the `tachi-threat-infographic` agent which:
1. Calls `python scripts/extract-infographic-data.py --template executive-architecture --target-dir examples/agentic-app/sample-report/`
2. Receives the JSON payload from stdout
3. Renders `threat-executive-architecture-spec.md` from the payload (six sections)
4. Constructs the Gemini prompt with portrait orientation, layer ordering, callout instructions
5. Invokes the Gemini API to produce `threat-executive-architecture.jpg`

**Expected output files added to the folder**:
- `threat-executive-architecture-spec.md` (always)
- `threat-executive-architecture.jpg` (if Gemini API succeeds)

### Verify the spec file

```bash
cat examples/agentic-app/sample-report/threat-executive-architecture-spec.md | head -40
```

Expected sections (in order):
1. `## Metadata`
2. `## Architecture Layers`
3. `## Threat Callouts`
4. `## Severity Distribution`
5. `## Visual Layout Directives`
6. `## Gemini Prompt Construction Notes`

### Verify the image file

```bash
file examples/agentic-app/sample-report/threat-executive-architecture.jpg
```

Expected: `JPEG image data, ... 1 component, ... `

If the image was not produced (Gemini failure or quota), confirm the spec file is still present and the agent log explains the failure. Re-run only the image generation step:

```bash
/tachi.infographic --template executive-architecture --target-dir examples/agentic-app/sample-report/ --image-only
```

## Step 3: Compile the PDF security report

```bash
/tachi.security-report --target-dir examples/agentic-app/sample-report/
```

This invokes the `tachi-report-assembler` agent which:
1. Calls `python scripts/extract-report-data.py --target-dir examples/agentic-app/sample-report/`
2. Generates `report-data.typ` with:
   - `#let has-executive-architecture = true` (because the JPEG was just created)
   - `#let executive-architecture-image-path = "..."` (relative path)
3. Invokes Typst CLI: `typst compile templates/tachi/security-report/main.typ`
4. Writes the resulting PDF to `examples/agentic-app/sample-report/security-report.pdf`

## Step 4: Verify the PDF page positioning

Open the PDF (e.g., with `open` on macOS) and confirm the page sequence:

| Page | Content | Notes |
|------|---------|-------|
| 1 | Cover page | Always |
| 2 | Disclaimer (if enabled) | Conditional |
| 3 | Table of Contents | Always |
| 4 | Methodology (if enabled) | Conditional |
| 5 | Assessment Scope | Always |
| 6 | Executive Summary | Always |
| **7** | **Executive Threat Architecture** | **NEW for F-128** — gated by `has-executive-architecture` |
| 8+ | Attack Path Analysis pages | Conditional on `has-attack-trees` |
| 9+ | Risk Reduction Funnel | Conditional on `has-funnel-image` |
| 10+ | Risk Summary Dashboard (baseball-card) | Conditional |
| 11+ | System Architecture | Conditional |
| ... | MAESTRO sections (if applicable) | Conditional |
| ... | Detailed Findings | Always |
| ... | Control Coverage | Conditional |
| ... | Remediation Roadmap | Conditional |

The key acceptance criterion: **the Executive Threat Architecture page must appear immediately after the Executive Summary**, before any other infographic pages.

## Step 5: Verify the visual content

The Executive Threat Architecture page should display:

- **Title**: "Executive Threat Architecture" (TOC-visible heading)
- **Image**: Portrait JPEG showing horizontal layered architecture bands with pastel fills, labeled by layer name (e.g., "Untrusted Edge", "Application Tier", "Data Store")
- **Callouts**: Red dashed-border boxes with warning icons, each containing a ≤25-word plain-English description of one Critical or High finding, connected to the layer it affects
- **Caption**: A brief descriptive caption below the image
- **Standard report styling**: Header, footer, page number consistent with other report pages

## Step 6: Verify backward compatibility

Run the report compilation against the 5 unmodified examples and confirm byte-identical PDFs to baseline:

```bash
for example in web-app microservices ascii-web-api mermaid-agentic-app free-text-microservice; do
  /tachi.security-report --target-dir examples/${example}/sample-report/
  cmp examples/${example}/sample-report/security-report.pdf \
      examples/${example}/sample-report/security-report.pdf.baseline
  echo "${example}: $?"
done
```

All five comparisons MUST report `0` (byte-identical).

If any example reports a non-zero exit code, this is a backward compatibility regression and the cause must be identified and fixed before merging F-128.

---

## Edge Case Walkthroughs

### Edge case A: No Critical/High findings

```bash
# Construct a synthetic threat model with only Medium/Low/Note findings
mkdir -p /tmp/test-no-critical
cp tests/fixtures/threats-medium-only.md /tmp/test-no-critical/threats.md

# Run extraction
/tachi.infographic --template executive-architecture --target-dir /tmp/test-no-critical
```

**Expected**:
- Exit code 0
- Spec file created with `skip_image: true` in metadata
- No JPEG generated (agent reads `skip_image` and does not invoke Gemini)
- If you then compile a PDF: the executive architecture page is omitted (boolean gating works)

### Edge case B: Missing threats.md

```bash
mkdir -p /tmp/test-empty
/tachi.infographic --template executive-architecture --target-dir /tmp/test-empty
```

**Expected**:
- Exit code 1
- Stderr: `[extract-infographic-data] ERROR: threats.md missing in /tmp/test-empty`

### Edge case C: No trust zones in threats.md

```bash
# Threat model with Section 1 components but no Section 2 trust boundaries
cp tests/fixtures/threats-no-trust-zones.md /tmp/test-no-zones/threats.md
/tachi.infographic --template executive-architecture --target-dir /tmp/test-no-zones
```

**Expected**:
- Exit code 0
- Spec file metadata has `fallback_used: true`
- Layers in payload have `source_kind: "dfd_type"` (grouped by DFD component type)

### Edge case D: No scope data at all

```bash
# Threat model with empty Section 1 AND empty Section 2
cp tests/fixtures/threats-no-scope.md /tmp/test-no-scope/threats.md
/tachi.infographic --template executive-architecture --target-dir /tmp/test-no-scope
```

**Expected**:
- Exit code 2
- Stderr: `[extract-infographic-data] ERROR: threats.md present but no parseable scope data`

---

## Debugging Tips

| Symptom | Probable Cause | Resolution |
|---------|----------------|------------|
| Spec file missing all callouts but threats.md has Critical findings | Components in findings not matching components in trust zones | Check that finding `component` field matches one of the components in the trust zone definition |
| PDF is missing the executive architecture page even though JPEG exists | `extract-report-data.py` did not detect the image | Verify file size > 0 and filename is exactly `threat-executive-architecture.jpg` |
| PDF page appears in the wrong position | Insertion point in `main.typ` is incorrect | Check that the `if has-executive-architecture` block is between the Executive Summary and Attack Path Analysis blocks |
| Unit tests fail with "no module named tachi_parsers" | PYTHONPATH not set | Run from repo root or set `PYTHONPATH=$PWD/scripts` |
| Gemini image is portrait but the layout is wrong | Gemini prompt needs iteration | Update the prompt construction in `.claude/agents/tachi/threat-infographic.md` and re-run |

---

## Acceptance Test Summary

When you can complete these checks against the regenerated agentic-app example, F-128 is ready for `/aod.deliver`:

- [ ] `threat-executive-architecture-spec.md` exists and has 6 sections
- [ ] `threat-executive-architecture.jpg` exists and is a valid JPEG
- [ ] PDF page 7 is "Executive Threat Architecture" (after Executive Summary, before Attack Paths)
- [ ] All 5 unmodified examples produce byte-identical PDFs to baseline
- [ ] Unit tests pass (≥80% coverage on new extraction branch)
- [ ] A non-technical reviewer can identify the most exposed layer in under 30 seconds when shown only pages 1–7 of the regenerated PDF
