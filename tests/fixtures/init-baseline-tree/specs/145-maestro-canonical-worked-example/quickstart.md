# Feature 145 Quickstart: Regenerating the Canonical MAESTRO Example

**Audience**: Tachi maintainer or future MAESTRO feature developer who needs to regenerate `examples/maestro-reference/` from its authored `architecture.md` input.

**Scope**: Local developer environment. The backward-compatibility test suite is developer-only (no CI job runs it — see plan.md WG-3).

---

## Prerequisites

```bash
# Tachi repo + Python 3.11
cd /path/to/tachi
python3.11 --version

# Mermaid CLI (hard prerequisite per ADR-022 — required for attack-tree rendering)
npm install -g @mermaid-js/mermaid-cli
which mmdc   # MUST print a path

# Typst compiler
which typst  # MUST print a path

# Gemini API key for infographic JPEG generation (one-time during authoring;
# not needed on re-runs after JPEGs are committed)
export GEMINI_API_KEY="..."

# pytest (developer-only)
pip install -r requirements-dev.txt
```

---

## Full Regeneration (from architecture.md)

Run these commands from the repo root. Slash commands are invoked via the tachi CLI or Claude Code session.

### 1. Validate architecture input

```bash
# /tachi.architecture reads examples/maestro-reference/architecture.md and
# validates Mermaid syntax + Component Summary table + dispatch keyword presence.
# On a frozen body authored in Wave 1, this invocation in "create" mode will
# also compute SHA-256 and inject v1.0 frontmatter (Feature 120 / FR-012).
/tachi.architecture examples/maestro-reference
```

### 2. Run the threat-modeling pipeline

```bash
# Orchestrator runs 6 STRIDE + 5 AI agents, Phase 3.5 chain correlation,
# Phase 3.6 agentic pattern synthesis. Emits:
#   - threats.md + threats.sarif
#   - threat-report.md (MAESTRO Findings + Cross-Layer Chains + Agentic Pattern Analysis)
#   - attack-trees/<finding-id>-attack-tree.md (one per Critical/High finding)
#   - attack-chains.md (conditional on chain surfacing)
/tachi.threat-model examples/maestro-reference

# Expected output quality gates (FR-007 / FR-008):
#   - threats.md: findings tagged across >=6 of 7 MAESTRO layers
#   - threat-report.md Cross-Layer Attack Chains section: >=1 chain spanning >=3 layers
#   - threat-report.md Agentic Pattern Analysis section: >=3 of 6 canonical patterns populated
```

### 3. Risk scoring

```bash
# Emits risk-scores.md + risk-scores.sarif with 4-dimensional composite scores.
/tachi.risk-score examples/maestro-reference
```

### 4. Compensating controls analysis

```bash
# Emits compensating-controls.md + compensating-controls.sarif mapping existing
# controls to threats and calculating residual risk.
/tachi.compensating-controls examples/maestro-reference
```

### 5. Infographic generation (all 6 templates)

```bash
# Emits 6 JPEGs + 6 spec files via Gemini API:
#   - threat-baseball-card.jpg/.md
#   - threat-system-architecture.jpg/.md
#   - threat-executive-architecture.jpg/.md (Feature 128)
#   - threat-risk-funnel.jpg/.md
#   - threat-maestro-stack.jpg/.md (Feature 091)
#   - threat-maestro-heatmap.jpg/.md (Feature 091)
/tachi.infographic all examples/maestro-reference
```

### 6. Security report PDF

```bash
# Emits security-report.pdf via Typst. Includes:
#   - Cover / disclaimer / TOC / executive summary
#   - Executive architecture infographic page (Feature 128)
#   - Attack path pages for Critical/High findings (Feature 112)
#   - MAESTRO Findings page (Feature 091)
#   - Body sections + infographic pages
/tachi.security-report examples/maestro-reference
```

---

## Baseline Regeneration (for Regression Fixture)

The `security-report.pdf.baseline` file is the anchor for byte-identity regression checks. Regenerate it under `SOURCE_DATE_EPOCH` pin:

```bash
# 1. Generate deterministic baseline PDF
SOURCE_DATE_EPOCH=1700000000 \
  python scripts/extract-report-data.py \
    --target-dir examples/maestro-reference \
    --output templates/tachi/security-report/report-data.typ \
    --template-dir templates/tachi/security-report

SOURCE_DATE_EPOCH=1700000000 \
  typst compile \
    templates/tachi/security-report/main.typ \
    examples/maestro-reference/security-report.pdf.baseline \
    --root .

# 2. Verify byte-identity on repeat regeneration
# (Run twice and diff — they MUST be identical)
SOURCE_DATE_EPOCH=1700000000 \
  python scripts/extract-report-data.py \
    --target-dir examples/maestro-reference \
    --output templates/tachi/security-report/report-data.typ \
    --template-dir templates/tachi/security-report

SOURCE_DATE_EPOCH=1700000000 \
  typst compile \
    templates/tachi/security-report/main.typ \
    /tmp/security-report-check.pdf \
    --root .

cmp examples/maestro-reference/security-report.pdf.baseline /tmp/security-report-check.pdf
# MUST be silent (identical). If not, do NOT commit the baseline — diagnose
# root cause (likely a script or template non-determinism regression).

# 3. Clean temp file
rm -f /tmp/security-report-check.pdf templates/tachi/security-report/report-data.typ
```

---

## Regression Verification

After the baseline is committed:

```bash
# Run the byte-identity regression against the new baseline
pytest tests/scripts/test_backward_compatibility.py \
  -k "maestro-reference" \
  --no-header -v

# Verify the 5 existing baselines still pass (backward-compat invariant)
pytest tests/scripts/test_backward_compatibility.py \
  -k "web-app or microservices or ascii-web-api or mermaid-agentic-app or free-text-microservice" \
  --no-header -v

# OR run all 6 in one command
pytest tests/scripts/test_backward_compatibility.py --no-header -v
# Expect 6 passes: 5 existing + 1 maestro-reference
```

---

## Cross-Artifact Consistency

```bash
# /aod.analyze validates cross-artifact consistency between spec.md, plan.md,
# tasks.md. MUST pass before the feature is marked delivered.
/aod.analyze
```

---

## Iteration Loop (if Wave 2 gates fail)

If the pipeline output does not meet FR-007 / FR-008 quality gates, apply the fallback ranking per plan.md Wave 3:

### Fallback (a) — Keyword-tune

Edit component names and descriptions in `architecture.md` to match the detection keyword tables:
- [maestro-layers-shared.md](../../.claude/skills/tachi-shared/references/maestro-layers-shared.md) — layer classification keywords
- [maestro-agentic-patterns-shared.md](../../.claude/skills/tachi-shared/references/maestro-agentic-patterns-shared.md) — R-01/R-02/R-03 trigger keywords
- [attack-chain-patterns-shared.md](../../.claude/skills/tachi-shared/references/attack-chain-patterns-shared.md) — (STRIDE, MAESTRO-layer) transition pairs

Common adjustments:
- Persistent-state component NOT classifying as L5: ensure description contains `log` or `monitoring` or `observability` or `outcome tracking` BEFORE any L6 keywords (L5-before-L6 ordering is load-bearing).
- Inter-agent data flow NOT satisfying R-01: ensure the flow description contains `coordinate` or `delegation` or `shared channel`, and both endpoint components have `agent` or `orchestrator` in their names.

### Fallback (b) — Extend architecture

Add 2-3 additional multi-agent components to strengthen preconditions:
- Additional specialist agent (e.g., "Validation Agent") to enrich R-01 topology
- Additional persistent-state component (e.g., "Clinical Memory Cache") for R-02
- Additional inter-agent channel to deepen R-05 surface

### Fallback (c) — Relax FR-004 coverage

LAST RESORT per team-lead review M3 ranking. If 2 iteration rounds of (a) and (b) do not surface the required coverage, relax FR-004 from 7/7 to 6/7 MAESTRO layers (still satisfies FR-007 which already requires only 6/7).

Convene architect + team-lead to approve the relaxation before committing. Document the approved relaxation in research.md with the specific gap (which layer was dropped and why).

---

## Commit Sequence

The final commit order (Wave 5 → Wave 6):

1. Commit `architecture.md` body (no frontmatter yet, per Path B)
2. Commit all pipeline-generated artifacts under `examples/maestro-reference/`
3. Commit `security-report.pdf.baseline` after byte-identity verification (two consecutive regenerations byte-identical)
4. Commit `tests/scripts/test_backward_compatibility.py` update (add `"maestro-reference"` to `BASELINE_EXAMPLES`)
5. Commit `examples/README.md` update (new table row + first-read callout)
6. Run `/tachi.architecture examples/maestro-reference` in "create" mode — this computes SHA-256 over the frozen body and injects Feature 120 v1.0 frontmatter. Commit the frontmatter change separately to make the two-pass checksum approach auditable.
7. Run `/aod.analyze` — MUST pass with no inconsistencies
8. Open PR for Triad review + merge

---

## Common Pitfalls

- **Committing intermediate architecture.md frontmatter**: Path B (FR-012) requires frontmatter injection only after the architecture body is frozen. Intermediate commits of frontmatter during Wave 3 iteration are prohibited — they create stale checksums that would fail `/tachi.architecture` validation on re-invocation.
- **Confusing `sample-report/` subdirectory with flat**: The chosen structure is Option Y (flat). Do NOT accidentally create `examples/maestro-reference/sample-report/` — team-lead L4 structural DoD discipline enforces this.
- **Baseline regeneration without `SOURCE_DATE_EPOCH`**: The env var MUST be set for the PDF Info dictionary / XMP metadata timestamps to pin. Missing it means byte-identity can never be achieved on a re-run (Typst will emit fresh timestamps).
- **mmdc not on PATH**: The pipeline will fail loudly at Phase 5 (attack tree rendering) per Feature 130 preflight gate. If you see "Attack path rendering" in a stderr message, install mmdc.
- **Modifying existing baselines**: The 5 existing non-multi-agent baselines MUST remain byte-identical. If `pytest tests/scripts/test_backward_compatibility.py` fails on one of them, STOP — root cause the regression before proceeding.
- **Modifying any `.claude/agents/tachi/**.md`**: The zero-edit invariant (Feature 082 / ADR-026 Decision 1) is enforced by `tests/scripts/test_backward_compatibility.py::test_feature_142_zero_edit_invariant_on_detection_agents`. Any diff against `main..HEAD` on a detection-tier file fails the test.
