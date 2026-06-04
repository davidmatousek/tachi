"""Cross-surface MAESTRO coverage_state consistency regression (T015, F-311).

Proves the three rendering surfaces agree on every canonical MAESTRO layer's
``coverage_state`` for ``examples/microservices``, and that the consistency gate
catches divergence.

Contract: ``specs/311-maestro-matrix-model-b-clean-vs-na/contracts/
cross-surface-consistency.contract.md`` — for EVERY canonical layer L1..L7::

    state(threats.md §6 cell) == state(report-data.typ coverage_state)
                              == state(maestro-stack.json coverage_state)

where state ∈ {findings, clean, not_applicable}. On disagreement the failure
names the offending layer ID(s) and the divergent surface(s)
(ADR-047 FR-010/FR-011, SC-001/SC-002).

The three surfaces and their single decision authority (ADR-047 D2):
  * Markdown — threats.md §6 cell, classified ONLY by the shared
    ``classify_maestro_coverage_state`` (Section-1 component mapping is NEVER
    routed into a state — ADR-047 D3).
  * PDF — ``report-data.typ`` IR; state rides the
    ``maestro_findings_by_layer`` GROUP records (the ONLY structure main.typ
    passes to the MAESTRO page — HIGH-A).
  * Infographic — ``maestro-stack.json`` IR; state on each
    ``per_layer_summaries`` record.

PDF and infographic IR are REGENERATED at test time (the render IR is not
committed — Architect MEDIUM-A); the committed ``threats.md`` is already
regenerated to Model-B and is read as-is.
"""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
EXTRACT_REPORT = SCRIPTS_DIR / "extract-report-data.py"
EXTRACT_INFOGRAPHIC = SCRIPTS_DIR / "extract-infographic-data.py"
MICROSERVICES = REPO_ROOT / "examples" / "microservices"

CANONICAL_LAYERS = ["L1", "L2", "L3", "L4", "L5", "L6", "L7"]
EXPECTED_STATE = {
    "L1": "not_applicable",
    "L2": "findings",
    "L3": "not_applicable",
    "L4": "findings",
    "L5": "not_applicable",
    "L6": "not_applicable",
    "L7": "clean",
}

# Em dash (U+2014) is the canonical layer-label separator; en dash (U+2013) is
# tolerated on read, mirroring _layer_id_of in scripts/populate-maestro-coverage.py.
_EM_DASH = "—"
_EN_DASH = "–"
_MAESTRO_HEADING = "Risk by MAESTRO Layer"
_UNCLASSIFIED = "Unclassified"


# --------------------------------------------------------------------------- #
# Pure comparison helper (keeps the negative test clean).
# --------------------------------------------------------------------------- #
def _disagreeing_layers(markdown_state, pdf_state, ig_state):
    """Return, per layer, the three surface states where they don't all agree.

    For every canonical layer whose markdown/PDF/infographic states are not all
    equal, the returned dict maps the layer ID to its per-surface states. An
    empty result means full cross-surface agreement. Pure.
    """
    disagree = {}
    for layer in CANONICAL_LAYERS:
        states = {
            "markdown": markdown_state.get(layer),
            "pdf": pdf_state.get(layer),
            "infographic": ig_state.get(layer),
        }
        if len(set(states.values())) > 1:
            disagree[layer] = states
    return disagree


# --------------------------------------------------------------------------- #
# (1) Markdown surface — threats.md §6 via the shared classifier (ADR-047 D2).
# --------------------------------------------------------------------------- #
def _layer_id_of(layer_cell):
    """``"L4 — Deployment Infrastructure"`` -> ``"L4"`` (em dash, en-dash fallback)."""
    parts = layer_cell.split(_EM_DASH, 1)
    if len(parts) < 2:
        parts = layer_cell.split(_EN_DASH, 1)
    return parts[0].strip()


def _split_row(line):
    """Split a markdown table row into stripped cells, dropping the outer pipes."""
    cells = [c.strip() for c in line.split("|")]
    if cells and cells[0] == "":
        cells = cells[1:]
    if cells and cells[-1] == "":
        cells = cells[:-1]
    return cells


def _markdown_state():
    """Classify each threats.md §6 layer cell via the shared classifier.

    State is a pure function of the carried §6 token (finding count + highest
    severity) — Section 1 is NEVER read (ADR-047 D3). The ``Unclassified`` row
    is skipped (only L1..L7 are asserted).
    """
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))
    from tachi_parsers import classify_maestro_coverage_state

    content = (MICROSERVICES / "threats.md").read_text(encoding="utf-8")
    lines = content.splitlines()

    # Find the "Risk by MAESTRO Layer" table region (heading-level agnostic).
    heading_idx = None
    for i, line in enumerate(lines):
        if line.lstrip("#").strip() == _MAESTRO_HEADING:
            heading_idx = i
            break
    assert heading_idx is not None, (
        "Could not find the 'Risk by MAESTRO Layer' heading in "
        f"{MICROSERVICES / 'threats.md'}"
    )

    states = {}
    seen_separator = False
    for line in lines[heading_idx + 1 :]:
        stripped = line.strip()
        if not stripped.startswith("|"):
            # End of the contiguous table block (only break after we entered it).
            if states or seen_separator:
                break
            continue
        cells = _split_row(line)
        if len(cells) < 3:
            continue
        layer_label, finding_count, highest_severity = cells[0], cells[1], cells[2]
        # Skip the header row and the separator row.
        if layer_label == "MAESTRO Layer":
            continue
        if set(layer_label) <= {"-", ":"}:
            seen_separator = True
            continue
        layer_id = _layer_id_of(layer_label)
        if layer_id == _UNCLASSIFIED:
            continue
        states[layer_id] = classify_maestro_coverage_state(
            int(finding_count), highest_severity
        )
    return states


# --------------------------------------------------------------------------- #
# (2) PDF surface — report-data.typ IR via module import (regenerated at test
#     time; render IR is NOT committed — Architect MEDIUM-A).
# --------------------------------------------------------------------------- #
def _load_extract_report_module():
    """Import the hyphenated ``extract-report-data.py`` as a module.

    ``scripts`` is placed on ``sys.path`` first so the script's own
    ``from tachi_parsers import ...`` line resolves, matching __main__ execution.
    """
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))
    spec = importlib.util.spec_from_file_location("extract_report_data", EXTRACT_REPORT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _pdf_state():
    """coverage_state per layer from the maestro_findings_by_layer GROUP records.

    This grouped structure is the ONLY one main.typ passes to the MAESTRO page
    (HIGH-A). Asserts exactly one group per canonical layer.
    """
    module = _load_extract_report_module()
    content = (MICROSERVICES / "threats.md").read_text(encoding="utf-8")
    result = module.parse_maestro_data(content)
    groups = result["maestro_findings_by_layer"]
    states = {}
    for layer in CANONICAL_LAYERS:
        matches = [g for g in groups if g["layer_id"] == layer]
        assert len(matches) == 1, (
            f"Expected exactly one {layer} group in maestro_findings_by_layer, "
            f"got {len(matches)}: {[g['layer_id'] for g in groups]!r}"
        )
        states[layer] = matches[0].get("coverage_state")
    return states


# --------------------------------------------------------------------------- #
# (3) Infographic surface — maestro-stack.json IR via subprocess (Python-only;
#     maestro-stack emits JSON, no Typst/mmdc needed).
# --------------------------------------------------------------------------- #
def _maestro_stack_state():
    """coverage_state per layer from maestro-stack.json per_layer_summaries."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        out = f.name
    try:
        cmd = [
            sys.executable,
            str(EXTRACT_INFOGRAPHIC),
            "--target-dir", str(MICROSERVICES),
            "--template", "maestro-stack",
            "--output", out,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        assert r.returncode == 0, f"infographic extractor failed: {r.stderr}"
        payload = json.loads(Path(out).read_text(encoding="utf-8"))
    finally:
        try:
            os.unlink(out)
        except OSError:
            pass
    return {
        s["layer_id"]: s["coverage_state"]
        for s in payload["template_data"]["per_layer_summaries"]
    }


# --------------------------------------------------------------------------- #
# Positive test.
# --------------------------------------------------------------------------- #
def test_microservices_three_surfaces_agree():
    """All three surfaces match EXPECTED_STATE and agree per layer (FR-010/FR-011).

    Builds the markdown/PDF/infographic per-layer state dicts (each keyed
    L1..L7), then asserts (a) each surface equals the committed fixture map and
    (b) ``_disagreeing_layers`` is empty. On failure the message names the
    offending layer(s) and which surface(s) diverged (SC-001/SC-002).
    """
    markdown_state = _markdown_state()
    pdf_state = _pdf_state()
    ig_state = _maestro_stack_state()

    # Each surface covers exactly the 7 canonical layers.
    for name, state in (
        ("markdown", markdown_state),
        ("pdf", pdf_state),
        ("infographic", ig_state),
    ):
        assert set(state) == set(CANONICAL_LAYERS), (
            f"{name} surface must emit all 7 canonical layers, got {sorted(state)}"
        )

    # (a) Each surface equals the committed fixture state map.
    assert markdown_state == EXPECTED_STATE, (
        f"markdown surface state {markdown_state!r} != expected {EXPECTED_STATE!r}"
    )
    assert pdf_state == EXPECTED_STATE, (
        f"pdf surface state {pdf_state!r} != expected {EXPECTED_STATE!r}"
    )
    assert ig_state == EXPECTED_STATE, (
        f"infographic surface state {ig_state!r} != expected {EXPECTED_STATE!r}"
    )

    # (b) Cross-surface agreement: no layer disagrees across the three surfaces.
    disagree = _disagreeing_layers(markdown_state, pdf_state, ig_state)
    assert not disagree, (
        "Cross-surface MAESTRO coverage_state divergence "
        f"(offending layer(s) → per-surface states): {disagree!r}"
    )


# --------------------------------------------------------------------------- #
# Negative test.
# --------------------------------------------------------------------------- #
def test_forced_l7_divergence_is_caught():
    """A tampered PDF state on L7 is caught by the gate (FR-010 AC-3 / ADR-047 D3).

    Uses the real markdown + infographic states but tampers a COPY of the PDF
    state so ``pdf["L7"] = "not_applicable"`` (the surfaces agree on L7="clean"),
    then asserts ``_disagreeing_layers`` names ``L7`` and ONLY L7 — proving the
    consistency gate would catch a real surface drift.
    """
    markdown_state = _markdown_state()
    ig_state = _maestro_stack_state()
    pdf_state = dict(_pdf_state())  # tamper a copy, never the source

    pdf_state["L7"] = "not_applicable"

    result = _disagreeing_layers(markdown_state, pdf_state, ig_state)
    assert "L7" in result, (
        "Forced L7 PDF divergence was NOT caught by _disagreeing_layers — the "
        f"consistency gate is blind. result={result!r}"
    )
    # Only L7 should be flagged (the other six remain in agreement).
    assert set(result) == {"L7"}, (
        f"Expected only L7 to diverge, got {sorted(result)}"
    )
    # The reported per-surface states pinpoint pdf as the divergent surface.
    assert result["L7"]["pdf"] == "not_applicable"
    assert result["L7"]["markdown"] == "clean"
    assert result["L7"]["infographic"] == "clean"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
