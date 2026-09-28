"""Sibling-parity regression suite: infographic JSON vs. report-data.typ (T019).

For the same fixture and data tier, contracts/extraction-data-contract.md's
"Sibling-parity set" requires the infographic JSON and report-data.typ values
to agree on: the posture level and label, the severity counts, the delta
counts (NEW/UPDATED/UNCHANGED/resolved, including a bracketed-status baseline
and an ID-mismatch baseline), and the MAESTRO layer distribution plus the
most-exposed layer.

Fixtures (tests/scripts/fixtures/fidelity_373/; see that directory's
README.md for hand-computed expected values, independently re-verified
against the raw fixture files below):
  - posture_mmdc_free/            -- severity counts + posture level/label (tier 1)
  - baseline_resolved_4c/         -- delta counts, bracketed Section 7 statuses (tier 3)
  - baseline_status_id_mismatch/  -- delta counts, a Section 7 / tier-1 ID-set mismatch (tier 1)
  - maestro_heading_h3/           -- MAESTRO layer distribution + most-exposed layer (tier 3)

NOT covered here: the K11 join-path parity case (funnel_join_inherent_less/,
architect finding F2). tasks.md T019 assigns that case to K11's own carve
unit -- it lands in its own K11 commit (T023), not this one.

Posture-level/label emission (``metadata.risk_posture_{level,label}`` on the
infographic side, ``#let risk-posture-level``/``#let risk-posture-label`` on
the report side) is tasks.md T025 (Lane B2a + B2b, W2). As of this commit
neither lane has landed it, so ``test_posture_level_label_agree_posture_mmdc_free``
is written to the contract and is expected to fail red until T025 lands on
both sides -- per the "never bend a test to match an implementation that
contradicts the contract" rule it is not weakened, skipped, or xfail-marked.
The severity-count, delta-count and MAESTRO parity tests below exercise
shared tachi_parsers.py logic that shipped in W1 (T016/T020/T024) and are
expected green independent of T025.
"""

import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
EXTRACT_INFOGRAPHIC = SCRIPTS_DIR / "extract-infographic-data.py"
EXTRACT_REPORT = SCRIPTS_DIR / "extract-report-data.py"
REPORT_TEMPLATE_DIR = REPO_ROOT / "templates" / "tachi" / "security-report"
FIDELITY_FIXTURES_DIR = REPO_ROOT / "tests" / "scripts" / "fixtures" / "fidelity_373"


# --------------------------------------------------------------------------- #
# CLI runners (subprocess -- exercises the real, written JSON/Typst output,
# mirroring run_extract() in test_extract_infographic_data.py / test_extract_report_data.py).
# --------------------------------------------------------------------------- #
def _run_infographic(target_dir, template):
    """Run extract-infographic-data.py and return (returncode, stderr, payload)."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        output_path = f.name
    try:
        cmd = [
            sys.executable, str(EXTRACT_INFOGRAPHIC),
            "--target-dir", str(target_dir),
            "--template", template,
            "--output", output_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        payload = None
        if result.returncode == 0 and os.path.exists(output_path):
            content = Path(output_path).read_text(encoding="utf-8")
            if content.strip():
                payload = json.loads(content)
        return result.returncode, result.stderr, payload
    finally:
        try:
            os.unlink(output_path)
        except OSError:
            pass


def _run_report(target_dir):
    """Run extract-report-data.py and return (returncode, stderr, typst_content)."""
    with tempfile.NamedTemporaryFile(suffix=".typ", delete=False) as f:
        output_path = f.name
    try:
        cmd = [
            sys.executable, str(EXTRACT_REPORT),
            "--target-dir", str(target_dir),
            "--template-dir", str(REPORT_TEMPLATE_DIR),
            "--output", output_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        content = None
        if result.returncode == 0 and os.path.exists(output_path):
            content = Path(output_path).read_text(encoding="utf-8")
        return result.returncode, result.stderr, content
    finally:
        try:
            os.unlink(output_path)
        except OSError:
            pass


# --------------------------------------------------------------------------- #
# Scalar `#let name = value` readers for report-data.typ (distinct from the
# record-array `#let name = (...)` helpers in test_extract_report_data.py).
# --------------------------------------------------------------------------- #
def _typst_let_value(content, name):
    """Return the raw RHS text of a top-level ``#let name = ...`` line, or None."""
    m = re.search(rf'^#let {re.escape(name)} = (.+)$', content, re.MULTILINE)
    return m.group(1).strip() if m else None


def _typst_let_str(content, name):
    """Return the unquoted string value of a ``#let name = "..."`` line, or None."""
    raw = _typst_let_value(content, name)
    if raw is None or not (raw.startswith('"') and raw.endswith('"')):
        return raw
    return raw[1:-1]


def _typst_let_int(content, name):
    """Return the integer value of a ``#let name = N`` line, or None."""
    raw = _typst_let_value(content, name)
    return int(raw) if raw is not None else None


# --------------------------------------------------------------------------- #
# Module loaders for the MAESTRO case (pure-function comparison, mirroring
# _load_extract_report_module() in test_maestro_cross_surface_consistency.py).
# --------------------------------------------------------------------------- #
def _load_infographic_module():
    """Import the hyphenated extract-infographic-data.py as a module."""
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))
    spec = importlib.util.spec_from_file_location("extract_infographic_data", EXTRACT_INFOGRAPHIC)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_report_module():
    """Import the hyphenated extract-report-data.py as a module."""
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))
    spec = importlib.util.spec_from_file_location("extract_report_data", EXTRACT_REPORT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------- #
# posture_mmdc_free/ (tier 1: threats.md + risk-scores.md + compensating-
# controls.md, no baseline). Residual severity counts {critical:0, high:1,
# medium:1, low:1} -> posture "high"/"HIGH RISK" (data-model.md §5).
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="module")
def posture_mmdc_free_outputs():
    """Run both extractors once against posture_mmdc_free/ and cache the outputs."""
    fixture = FIDELITY_FIXTURES_DIR / "posture_mmdc_free"
    ig_rc, ig_stderr, ig_payload = _run_infographic(fixture, "baseball-card")
    assert ig_rc == 0, f"infographic extractor failed: {ig_stderr}"
    rp_rc, rp_stderr, rp_content = _run_report(fixture)
    assert rp_rc == 0, f"report extractor failed: {rp_stderr}"
    return ig_payload, rp_content


def test_posture_level_label_agree_posture_mmdc_free(posture_mmdc_free_outputs):
    """metadata.risk_posture_{level,label} == #let risk-posture-level/-label (T025).

    EXPECTED RED until tasks.md T025 lands on both Lane B2a (infographic) and
    Lane B2b (report) -- see the module docstring. Written to the contract
    regardless of today's implementation state.
    """
    ig_payload, rp_content = posture_mmdc_free_outputs

    ig_level = ig_payload["metadata"].get("risk_posture_level")
    ig_label = ig_payload["metadata"].get("risk_posture_label")
    rp_level = _typst_let_str(rp_content, "risk-posture-level")
    rp_label = _typst_let_str(rp_content, "risk-posture-label")

    assert ig_level == "high", f"infographic metadata.risk_posture_level: {ig_level!r}"
    assert ig_label == "HIGH RISK", f"infographic metadata.risk_posture_label: {ig_label!r}"
    assert rp_level == "high", f"report #let risk-posture-level: {rp_level!r}"
    assert rp_label == "HIGH RISK", f"report #let risk-posture-label: {rp_label!r}"
    assert ig_level == rp_level, (
        f"posture level mismatch: infographic={ig_level!r} report={rp_level!r}"
    )
    assert ig_label == rp_label, (
        f"posture label mismatch: infographic={ig_label!r} report={rp_label!r}"
    )


def test_severity_counts_agree_posture_mmdc_free(posture_mmdc_free_outputs):
    """severity_distribution counts == #let {critical,high,medium,low}-count.

    Both surfaces derive residual severity counts from the same shared
    tachi_parsers.parse_compensating_controls_md (post-clamp, K11); this is
    W1-committed logic and is expected green regardless of T025.
    """
    ig_payload, rp_content = posture_mmdc_free_outputs

    ig_counts = {e["label"].lower(): e["count"] for e in ig_payload["severity_distribution"]}
    expected = {"critical": 0, "high": 1, "medium": 1, "low": 1}
    assert ig_counts == expected, f"infographic severity_distribution counts: {ig_counts!r}"

    rp_counts = {
        "critical": _typst_let_int(rp_content, "critical-count"),
        "high": _typst_let_int(rp_content, "high-count"),
        "medium": _typst_let_int(rp_content, "medium-count"),
        "low": _typst_let_int(rp_content, "low-count"),
    }
    assert rp_counts == expected, f"report severity counts: {rp_counts!r}"
    assert ig_counts == rp_counts

    assert ig_payload["metadata"]["total_findings"] == 3
    assert _typst_let_int(rp_content, "total-findings") == 3


# --------------------------------------------------------------------------- #
# baseline_resolved_4c/ (tier 3: threats.md only). Section 7 mixes every
# bracketed NEW spelling N6 must normalize (bare, [NEW], **[NEW]**, `[NEW]`);
# ## 4c. Resolved Findings carries 2 real rows + 1 skipped placeholder row.
# --------------------------------------------------------------------------- #
def test_delta_counts_agree_bracketed_status_baseline():
    """delta_counts agree across surfaces for a baseline whose Section 7 Status
    column mixes bracketed NEW spellings that must all normalize to NEW
    (K12, N6; data-model.md §6)."""
    fixture = FIDELITY_FIXTURES_DIR / "baseline_resolved_4c"
    expected = {"new": 4, "updated": 1, "unchanged": 1, "resolved": 2}

    ig_rc, ig_stderr, ig_payload = _run_infographic(fixture, "baseball-card")
    assert ig_rc == 0, f"infographic extractor failed: {ig_stderr}"
    rp_rc, rp_stderr, rp_content = _run_report(fixture)
    assert rp_rc == 0, f"report extractor failed: {rp_stderr}"

    ig_counts = ig_payload["delta"]["delta_counts"]
    assert ig_counts == expected, f"infographic delta_counts: {ig_counts!r}"

    rp_counts = {
        "new": _typst_let_int(rp_content, "delta-new-count"),
        "updated": _typst_let_int(rp_content, "delta-updated-count"),
        "unchanged": _typst_let_int(rp_content, "delta-unchanged-count"),
        "resolved": _typst_let_int(rp_content, "delta-resolved-count"),
    }
    assert rp_counts == expected, f"report delta counts: {rp_counts!r}"
    assert ig_counts == rp_counts


# --------------------------------------------------------------------------- #
# baseline_status_id_mismatch/ (tier 1: threats.md + compensating-controls.md).
# Section 7's status-map ID set {A-1,A-2,A-3} differs from the tier-1 finding
# ID set {A-1,A-2,A-4} (architect finding F1 / re-review NM-1): delta_counts
# must still be computed over the full normalized Section 7 map, unrestricted
# by the tier's own ID set.
# --------------------------------------------------------------------------- #
def test_delta_counts_agree_id_mismatch_baseline():
    """delta_counts agree across surfaces when Section 7's status-map ID set
    differs from the tier-1 finding ID set (K12 / FR-K12.1-K12.2, NM-1)."""
    fixture = FIDELITY_FIXTURES_DIR / "baseline_status_id_mismatch"
    expected = {"new": 1, "updated": 1, "unchanged": 1, "resolved": 0}

    ig_rc, ig_stderr, ig_payload = _run_infographic(fixture, "baseball-card")
    assert ig_rc == 0, f"infographic extractor failed: {ig_stderr}"
    rp_rc, rp_stderr, rp_content = _run_report(fixture)
    assert rp_rc == 0, f"report extractor failed: {rp_stderr}"

    ig_counts = ig_payload["delta"]["delta_counts"]
    assert ig_counts == expected, f"infographic delta_counts: {ig_counts!r}"

    rp_counts = {
        "new": _typst_let_int(rp_content, "delta-new-count"),
        "updated": _typst_let_int(rp_content, "delta-updated-count"),
        "unchanged": _typst_let_int(rp_content, "delta-unchanged-count"),
        "resolved": _typst_let_int(rp_content, "delta-resolved-count"),
    }
    assert rp_counts == expected, f"report delta counts: {rp_counts!r}"
    assert ig_counts == rp_counts


# --------------------------------------------------------------------------- #
# maestro_heading_h3/ (tier 3: threats.md only). Section 6 uses a ### (not
# canonical ####) "Risk by MAESTRO Layer" heading (K10, FR-K10.1). Compared
# via direct pure-function calls (extract_maestro_data / parse_maestro_data)
# rather than the CLI: the infographic CLI's maestro-heatmap template omits
# most_exposed_layer, and its maestro-stack template backfills the
# distribution to all 7 canonical layers (a deliberately LOCAL, main()-only
# transform per the code comment at that call site) -- neither JSON view is
# the right basis for a raw sibling-parity comparison. Calling the two
# shared-shape parser functions directly on the same threats.md content is
# the precedented approach (see _pdf_state() in
# test_maestro_cross_surface_consistency.py).
# --------------------------------------------------------------------------- #
def test_maestro_layer_distribution_and_most_exposed_agree_h3_heading():
    """MAESTRO layer distribution and most-exposed layer agree across surfaces
    for a threats.md whose Section 6 heading is ### instead of #### (K10)."""
    content = (FIDELITY_FIXTURES_DIR / "maestro_heading_h3" / "threats.md").read_text(
        encoding="utf-8"
    )

    ig = _load_infographic_module().extract_maestro_data(content)
    rp = _load_report_module().parse_maestro_data(content)

    assert ig["has_maestro_data"] is True
    assert rp["has_maestro_data"] is True

    expected_distribution = [
        {
            "layer_id": "L1",
            "layer_name": "Foundation Model",
            "finding_count": 3,
            "highest_severity": "Critical",
        },
        {
            "layer_id": "L4",
            "layer_name": "Deployment Infrastructure",
            "finding_count": 2,
            "highest_severity": "High",
        },
    ]
    shared_keys = ("layer_id", "layer_name", "finding_count", "highest_severity")
    ig_distribution = [
        {k: layer[k] for k in shared_keys} for layer in ig["maestro_layer_distribution"]
    ]
    rp_distribution = [
        {k: layer[k] for k in shared_keys} for layer in rp["maestro_layer_distribution"]
    ]
    assert ig_distribution == expected_distribution, f"infographic: {ig_distribution!r}"
    assert rp_distribution == expected_distribution, f"report: {rp_distribution!r}"
    assert ig_distribution == rp_distribution

    assert ig["most_exposed_layer"] == "L1 — Foundation Model"
    assert rp["most_exposed_layer"] == "L1 — Foundation Model"
    assert ig["most_exposed_layer"] == rp["most_exposed_layer"]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
