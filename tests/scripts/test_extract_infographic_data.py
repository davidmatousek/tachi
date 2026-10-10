"""Unit tests for the executive-architecture template in extract-infographic-data.py.

Exercises both subprocess invocation (for end-to-end behavior and exit codes) and
direct module-level calls through the ``extract_infographic_data`` conftest fixture
(for helper-function and payload-shape assertions).
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "extract-infographic-data.py"
FIXTURES_DIR = REPO_ROOT / "tests" / "scripts" / "fixtures" / "exec_arch"
GOLDEN_DIR = REPO_ROOT / "tests" / "scripts" / "fixtures" / "golden"

# Feature 373 US-3a (K9/K10/K12) extractor-level regression fixtures. See
# that directory's README.md for hand-computed expected values; the pure
# tachi_parsers.py-level pins for these same fixtures live in
# test_tachi_parsers.py (tasks.md T016) -- the tests below instead exercise
# extract-infographic-data.py's own wiring (extract_severity,
# parse_maestro_layer_distribution, and the CLI's delta_counts call site).
FIDELITY_FIXTURES_DIR = REPO_ROOT / "tests" / "scripts" / "fixtures" / "fidelity_373"


def _read_fidelity_fixture(subdir: str, filename: str) -> str:
    return (FIDELITY_FIXTURES_DIR / subdir / filename).read_text(encoding="utf-8")


def run_extract(target_dir, template, extra_args=None):
    """Run extract-infographic-data.py and return (returncode, stdout, stderr, payload)."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        output_path = f.name
    try:
        cmd = [
            sys.executable,
            str(SCRIPT_PATH),
            "--target-dir", str(target_dir),
            "--template", template,
            "--output", output_path,
        ]
        if extra_args:
            cmd.extend(extra_args)
        result = subprocess.run(cmd, capture_output=True, text=True)
        payload = None
        if result.returncode == 0 and os.path.exists(output_path):
            try:
                with open(output_path, "r", encoding="utf-8") as fh:
                    content = fh.read()
                if content.strip():
                    payload = json.loads(content)
            except (OSError, json.JSONDecodeError):
                payload = None
        return result.returncode, result.stdout, result.stderr, payload
    finally:
        try:
            os.unlink(output_path)
        except OSError:
            pass


def test_executive_architecture_happy_path():
    """Agentic-app fixture: exit 0, ≥1 layer, ≥1 callout, skip_image=False."""
    returncode, _stdout, stderr, payload = run_extract(
        FIXTURES_DIR / "agentic_app", "executive-architecture"
    )
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert payload is not None, "Expected JSON payload to be written"
    assert "metadata" in payload
    assert "layers" in payload
    assert "callouts" in payload
    assert "severity_distribution" in payload
    assert len(payload["layers"]) >= 1, "Expected at least 1 layer"
    assert len(payload["callouts"]) >= 1, "Expected at least 1 callout"
    assert payload["metadata"]["skip_image"] is False
    for callout in payload["callouts"]:
        assert callout["severity"] in ("Critical", "High"), (
            f"Expected Critical/High, got {callout['severity']}"
        )


def test_executive_architecture_with_risk_scores_tier():
    """Agentic-app fixture with risk-scores.md: tier_source=risk-scores, composite scores present.

    The agentic-app fixture includes both risk-scores.md AND compensating-controls.md.
    To force the risk-scores tier we create a temporary fixture dir with only threats.md
    and risk-scores.md.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        src = FIXTURES_DIR / "agentic_app"
        (tmp / "threats.md").write_bytes((src / "threats.md").read_bytes())
        (tmp / "risk-scores.md").write_bytes((src / "risk-scores.md").read_bytes())
        returncode, _stdout, stderr, payload = run_extract(
            tmp, "executive-architecture"
        )
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert payload is not None
    assert payload["metadata"]["tier_source"] == "risk-scores"
    # With risk-scores tier, at least some callouts should have non-null composite_score
    non_null_scores = [
        c for c in payload["callouts"] if c.get("composite_score") is not None
    ]
    assert len(non_null_scores) >= 1, (
        "Expected at least one callout with non-null composite_score in risk-scores tier"
    )


def test_executive_architecture_with_compensating_controls_tier():
    """Agentic-app fixture with compensating-controls.md: tier_source=compensating-controls."""
    returncode, _stdout, stderr, payload = run_extract(
        FIXTURES_DIR / "agentic_app", "executive-architecture"
    )
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert payload is not None
    assert payload["metadata"]["tier_source"] == "compensating-controls"


def test_executive_architecture_no_critical_high_skip_image():
    """no_critical_high fixture: exit 0, skip_image=True, callouts empty."""
    returncode, _stdout, stderr, payload = run_extract(
        FIXTURES_DIR / "no_critical_high", "executive-architecture"
    )
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert payload is not None
    assert payload["metadata"]["skip_image"] is True
    assert payload["callouts"] == []
    assert payload["severity_distribution"]["critical_count"] == 0
    assert payload["severity_distribution"]["high_count"] == 0


# =============================================================================
# T036 M-2 (K13 half) -- executive-architecture's risk-posture fields had no
# CI assertion (code-reviewer-373.md M-2): metadata.risk_posture_level/_label
# are added to the payload only `if risk_posture_level is not None`
# (extract-infographic-data.py:1275), and the one real caller (main()) always
# supplies both -- so dropping the two keywords at the main() call site would
# silently omit exec-arch's posture with no test catching it. Pinned against
# the agentic_app fixture's hand-verified value (data-model.md §5: residual
# severity counts after the K11 clamp -> 7 Critical/High findings -> high).
# =============================================================================

def test_executive_architecture_risk_posture_fields_gated():
    """agentic_app fixture: metadata carries risk_posture_level/_label (K13, data-model §5)."""
    returncode, _stdout, stderr, payload = run_extract(
        FIXTURES_DIR / "agentic_app", "executive-architecture"
    )
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert payload is not None
    assert payload["metadata"].get("risk_posture_level") == "high", (
        "T036 M-2: executive-architecture metadata must carry risk_posture_level "
        f"computed from this tier's severity counts; got {payload['metadata'].get('risk_posture_level')!r}"
    )
    assert payload["metadata"].get("risk_posture_label") == "HIGH RISK", (
        "T036 M-2: executive-architecture metadata must carry risk_posture_label; "
        f"got {payload['metadata'].get('risk_posture_label')!r}"
    )


# =============================================================================
# T036 M-2 (K15 half) -- executive-architecture's and maestro-stack's
# allow_list.finding_ids had no CI assertion (code-reviewer-373.md M-2).
# Kept in its own block, separated from the K13 block above by this banner,
# so a future TW-6 K15 carve (reverting T027-T029) can remove exactly this
# block mechanically.
#
# The maestro-stack golden fixture (agentic_app) and maestro_partial both
# carry NO "MAESTRO Layer" column on their Section 3/4 tables, so their
# per_finding_maestro is always [] and allow_list.finding_ids is already []
# before any regression -- a wrong key or branch in compute_allow_list's
# maestro-stack branch would still emit [] and pass every existing gate
# (review's exact concern). The new maestro_top_findings fixture carries
# that column so the non-empty case -- and the 2-per-layer cap -- are
# actually exercised.
# =============================================================================

def test_executive_architecture_allow_list_matches_callouts():
    """agentic_app fixture: allow_list.finding_ids == sorted(callout finding IDs) (K15, data-model §8)."""
    returncode, _stdout, stderr, payload = run_extract(
        FIXTURES_DIR / "agentic_app", "executive-architecture"
    )
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert payload is not None
    expected = sorted({c["finding_id"] for c in payload["callouts"]})
    assert payload["allow_list"]["finding_ids"] == expected, (
        "T036 M-2: executive-architecture allow_list.finding_ids must equal "
        f"the callout IDs; expected {expected}, got {payload['allow_list']['finding_ids']}"
    )
    # Hand-verified pin (code-reviewer-373.md M-2) so a change to either side
    # that happens to keep them mutually consistent still gets caught.
    assert payload["allow_list"]["finding_ids"] == ["AG-1", "E-2", "E-3", "LLM-1"]


def test_maestro_stack_allow_list_matches_top_findings_and_is_capped():
    """maestro_top_findings fixture: allow_list.finding_ids == per-layer top-finding IDs, non-empty.

    S-4 (the 3rd-ranked finding in L7 — Agent Ecosystem) must be excluded: the
    per-layer cap keeps only the top 2 (by severity desc, then id asc), and
    compute_allow_list's maestro-stack branch must read exactly that capped
    set, not the full per-finding MAESTRO table.
    """
    returncode, _stdout, stderr, payload = run_extract(
        FIXTURES_DIR / "maestro_top_findings", "maestro-stack"
    )
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert payload is not None
    expected = sorted(
        tf["id"]
        for layer in payload["template_data"]["per_layer_summaries"]
        for tf in layer["top_findings"]
    )
    assert expected, "fixture must exercise at least one non-empty layer"
    assert payload["allow_list"]["finding_ids"] == expected, (
        "T036 M-2: maestro-stack allow_list.finding_ids must equal the "
        f"per-layer top-finding IDs; expected {expected}, got "
        f"{payload['allow_list']['finding_ids']}"
    )
    assert payload["allow_list"]["finding_ids"] == ["S-1", "S-2", "S-3", "T-1", "T-2"], (
        "T036 M-2: S-4 must be excluded by the 2-per-layer cap; "
        f"got {payload['allow_list']['finding_ids']}"
    )


def test_executive_architecture_no_threats_md():
    """Empty folder: exit 1, stderr mentions threats.md."""
    with tempfile.TemporaryDirectory() as tmpdir:
        returncode, _stdout, stderr, _payload = run_extract(
            Path(tmpdir), "executive-architecture"
        )
    assert returncode == 1, f"Expected exit 1, got {returncode}. stderr: {stderr}"
    assert "threats.md" in stderr, (
        f"Expected stderr to mention threats.md; got: {stderr}"
    )


def test_executive_architecture_no_scope_data():
    """no_scope_data fixture: exit 2, stderr mentions parseable scope."""
    returncode, _stdout, stderr, _payload = run_extract(
        FIXTURES_DIR / "no_scope_data", "executive-architecture"
    )
    assert returncode == 2, f"Expected exit 2, got {returncode}. stderr: {stderr}"
    # The script uses "parseable scope data" in its error message
    assert "parseable scope data" in stderr.lower() or "scope data" in stderr.lower(), (
        f"Expected stderr to mention scope data; got: {stderr}"
    )


def test_executive_architecture_trust_zone_fallback_to_dfd():
    """no_trust_zones fixture: exit 0, fallback_used=True, all layers source_kind=dfd_type."""
    returncode, _stdout, stderr, payload = run_extract(
        FIXTURES_DIR / "no_trust_zones", "executive-architecture"
    )
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert payload is not None
    assert payload["metadata"]["fallback_used"] is True
    assert len(payload["layers"]) >= 1
    for layer in payload["layers"]:
        assert layer["source_kind"] == "dfd_type", (
            f"Expected source_kind=dfd_type, got {layer['source_kind']}"
        )


def test_executive_architecture_per_layer_ceiling_and_tie_break():
    """multiple_per_layer fixture: per-layer ceiling = 4 callouts; tie-break orders S-1..S-4.

    The fixture has one trust zone "Edge Layer" with 5 gateways (Alpha, Beta, Gamma,
    Delta, Epsilon), each with a Critical finding (S-1..S-5). All 5 findings are
    Critical, so the severity tie-break falls to finding_id ascending.

    Pre-F-212 behavior (per-layer-dedup) emitted exactly 1 callout — the tie-break
    winner S-1. Post-F-212 (FR-212-9 per-layer ceiling = 4) the same single layer
    receives 4 callouts (capped at the ceiling) and the tie-break still selects
    the four lex-smallest finding ids: S-1, S-2, S-3, S-4. The fifth finding S-5
    surfaces via the layer_overflow annotation rather than a callout.
    """
    returncode, _stdout, stderr, payload = run_extract(
        FIXTURES_DIR / "multiple_per_layer", "executive-architecture"
    )
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert payload is not None
    edge_callouts = [
        c for c in payload["callouts"] if c["layer_name"] == "Edge Layer"
    ]
    # FR-212-9 per-layer ceiling: a single layer with 5 qualifying findings
    # receives exactly 4 callouts (the ceiling), not all 5 and not just 1.
    assert len(edge_callouts) == 4, (
        f"Expected 4 callouts for 'Edge Layer' (per-layer ceiling), "
        f"got {len(edge_callouts)}"
    )
    # Tie-break: severity all-Critical → composite-score all-None → finding_id
    # asc. The four lex-smallest ids must appear in ascending order.
    assert [c["finding_id"] for c in edge_callouts] == ["S-1", "S-2", "S-3", "S-4"], (
        f"Expected tie-break ordering [S-1, S-2, S-3, S-4]; "
        f"got {[c['finding_id'] for c in edge_callouts]}"
    )

    # FR-212-9 layer_overflow annotation: 5 qualifying - 4 allocated = 1 more.
    edge_layer = next(
        layer for layer in payload["layers"] if layer["name"] == "Edge Layer"
    )
    assert edge_layer.get("layer_overflow") == "+ 1 more in this layer", (
        f"Expected layer_overflow='+ 1 more in this layer'; "
        f"got {edge_layer.get('layer_overflow')!r}"
    )


def test_executive_architecture_deterministic_output():
    """Same input twice produces identical payloads (ignoring generation_timestamp).

    The script does not expose a --frozen-time flag for the executive-architecture
    branch, so we compare all fields EXCEPT metadata.generation_timestamp.
    """
    returncode1, _, _, payload1 = run_extract(
        FIXTURES_DIR / "agentic_app", "executive-architecture"
    )
    returncode2, _, _, payload2 = run_extract(
        FIXTURES_DIR / "agentic_app", "executive-architecture"
    )
    assert returncode1 == 0 and returncode2 == 0
    assert payload1 is not None and payload2 is not None
    # Remove timestamp for comparison
    p1 = json.loads(json.dumps(payload1))
    p2 = json.loads(json.dumps(payload2))
    p1["metadata"].pop("generation_timestamp", None)
    p2["metadata"].pop("generation_timestamp", None)
    assert p1 == p2, "Payloads should be identical (ignoring generation_timestamp)"


def test_executive_architecture_orphaned_finding_dropped():
    """orphaned_finding fixture: the Critical finding S-2 on 'Component D' is dropped.

    Component D is not in any trust zone, so S-2 should not appear in callouts.
    Component A (edge zone) should still have S-1 as its callout.
    """
    returncode, _stdout, stderr, payload = run_extract(
        FIXTURES_DIR / "orphaned_finding", "executive-architecture"
    )
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert payload is not None
    callout_ids = {c["finding_id"] for c in payload["callouts"]}
    assert "S-2" not in callout_ids, (
        "Orphaned Critical finding S-2 (on Component D) should be dropped"
    )
    assert "S-1" in callout_ids, (
        "Finding S-1 (on Component A in Edge Zone) should be in callouts"
    )


def test_executive_architecture_component_name_normalization():
    """mixed_case_components: findings with kebab/underscore/lowercase match title-case layers.

    Trust zones use 'API Gateway', 'Auth Service', 'Database'.
    Findings reference 'api-gateway', 'auth_service', 'database'.
    Normalization should match them to their layers.
    """
    returncode, _stdout, stderr, payload = run_extract(
        FIXTURES_DIR / "mixed_case_components", "executive-architecture"
    )
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert payload is not None
    # Expect three callouts (S-1 on Edge, T-1 on Application, I-1 on Data)
    callout_ids = {c["finding_id"] for c in payload["callouts"]}
    assert "S-1" in callout_ids, (
        "api-gateway finding S-1 should match 'API Gateway' layer"
    )
    assert "T-1" in callout_ids, (
        "auth_service finding T-1 should match 'Auth Service' layer"
    )
    assert "I-1" in callout_ids, (
        "database finding I-1 should match 'Database' layer"
    )


# -----------------------------------------------------------------------------
# Direct helper-function tests (for coverage of new code paths)
# -----------------------------------------------------------------------------

def test_normalize_component_name_helper(extract_infographic_data):
    """_normalize_component_name strips whitespace, lowercases, and removes punctuation."""
    normalize = extract_infographic_data._normalize_component_name
    assert normalize("API Gateway") == "apigateway"
    assert normalize("api-gateway") == "apigateway"
    assert normalize("api_gateway") == "apigateway"
    assert normalize("  API   Gateway  ") == "apigateway"
    assert normalize("APIGateway") == "apigateway"
    assert normalize("") == ""
    assert normalize(None) == ""


def test_compute_dfd_type_layers_helper(extract_infographic_data):
    """_compute_dfd_type_layers groups components by type alphabetically."""
    compute = extract_infographic_data._compute_dfd_type_layers

    # Happy path: 3 types, sorted alphabetically
    scope = {
        "components": [
            {"name": "Web UI", "type": "External Entity", "description": ""},
            {"name": "API Gateway", "type": "api", "description": ""},
            {"name": "Backend", "type": "service", "description": ""},
            {"name": "DB", "type": "datastore", "description": ""},
            {"name": "Aux Service", "type": "service", "description": ""},
        ]
    }
    layers = compute(scope)
    assert layers is not None
    layer_names = [layer["name"] for layer in layers]
    assert layer_names == sorted(layer_names), "Layers should be alphabetically sorted"
    # Multi-component layers should be alphabetically sorted within
    service_layer = next(layer for layer in layers if layer["name"] == "service")
    assert service_layer["components"] == ["Aux Service", "Backend"]
    assert service_layer["component_count"] == 2
    assert service_layer["source_kind"] == "dfd_type"

    # Empty components → None
    assert compute({"components": []}) is None
    assert compute({}) is None

    # Components with missing type/name are skipped
    assert compute({
        "components": [
            {"name": "", "type": "api", "description": ""},
            {"name": "X", "type": "", "description": ""},
        ]
    }) is None


def test_select_critical_high_callouts_helper(extract_infographic_data):
    """_select_critical_high_callouts drops orphans and applies tie-break."""
    select = extract_infographic_data._select_critical_high_callouts

    layers = [
        {"name": "Edge", "position": 0, "components": ["API Gateway"],
         "component_count": 1, "source_kind": "trust_zone"},
        {"name": "App", "position": 1, "components": ["Auth Service"],
         "component_count": 1, "source_kind": "trust_zone"},
    ]

    # Orphaned finding should be dropped
    findings_with_orphan = [
        {"id": "S-1", "component": "API Gateway", "threat": "spoof the gateway",
         "risk_level": "Critical"},
        {"id": "S-2", "component": "Ghost", "threat": "orphaned critical",
         "risk_level": "Critical"},
    ]
    callouts = select(findings_with_orphan, layers)
    ids = {c["finding_id"] for c in callouts}
    assert "S-1" in ids
    assert "S-2" not in ids

    # Tie-break: Critical > High
    tie_break_findings = [
        {"id": "A-1", "component": "API Gateway", "threat": "high-severity",
         "risk_level": "High"},
        {"id": "B-2", "component": "API Gateway", "threat": "critical-severity",
         "risk_level": "Critical"},
    ]
    callouts = select(tie_break_findings, layers)
    edge_callout = next(c for c in callouts if c["layer_name"] == "Edge")
    assert edge_callout["finding_id"] == "B-2"  # Critical wins

    # Tie-break: composite_score
    score_tie_findings = [
        {"id": "X-1", "component": "Auth Service", "threat": "lower score",
         "severity": "Critical", "composite_score": "7.0"},
        {"id": "X-2", "component": "Auth Service", "threat": "higher score",
         "severity": "Critical", "composite_score": "9.5"},
    ]
    callouts = select(score_tie_findings, layers)
    app_callout = next(c for c in callouts if c["layer_name"] == "App")
    assert app_callout["finding_id"] == "X-2"  # Higher score wins
    assert app_callout["composite_score"] == 9.5

    # Tie-break: finding_id ascending
    id_tie_findings = [
        {"id": "B-9", "component": "API Gateway", "threat": "b9 threat",
         "risk_level": "Critical"},
        {"id": "A-1", "component": "API Gateway", "threat": "a1 threat",
         "risk_level": "Critical"},
    ]
    callouts = select(id_tie_findings, layers)
    edge_callout = next(c for c in callouts if c["layer_name"] == "Edge")
    assert edge_callout["finding_id"] == "A-1"  # A-1 < B-9 lexicographically

    # Filtered out: Medium severity
    med_findings = [
        {"id": "M-1", "component": "API Gateway", "threat": "medium",
         "risk_level": "Medium"},
    ]
    assert select(med_findings, layers) == []

    # residual_severity field also works (tier 1 compensating-controls)
    cc_findings = [
        {"id": "R-1", "component": "API Gateway", "threat": "cc threat",
         "residual_severity": "Critical", "residual_score": "9.0"},
    ]
    callouts = select(cc_findings, layers)
    assert len(callouts) == 1
    assert callouts[0]["finding_id"] == "R-1"


def test_build_executive_architecture_payload_helper(extract_infographic_data):
    """_build_executive_architecture_payload assembles full payload with metadata."""
    build = extract_infographic_data._build_executive_architecture_payload

    # Happy path: trust zones → untrusted first reversal
    scope = {
        "components": [],
        "data_flows": [],
        "trust_boundaries": [
            {"zone": "Trusted Core", "trust-level": "Trusted", "components": "DB"},
            {"zone": "Edge", "trust-level": "Untrusted", "components": "API Gateway"},
            {"zone": "Internal", "trust-level": "Semi-Trusted", "components": "Backend"},
        ],
        "boundary_crossings": [],
    }
    findings = [
        {"id": "S-1", "component": "API Gateway", "threat": "spoofed gateway",
         "risk_level": "Critical"},
        {"id": "T-1", "component": "Backend", "threat": "tampering on backend",
         "risk_level": "High"},
        {"id": "I-1", "component": "DB", "threat": "info disclosure",
         "risk_level": "Medium"},  # excluded
    ]
    payload = build("threats", findings, scope, "/tmp/threats.md")
    assert payload["metadata"]["template_name"] == "executive-architecture"
    assert payload["metadata"]["tier_source"] == "threats"
    assert payload["metadata"]["source_file"] == "/tmp/threats.md"
    assert payload["metadata"]["fallback_used"] is False
    assert payload["metadata"]["skip_image"] is False
    assert payload["severity_distribution"]["critical_count"] == 1
    assert payload["severity_distribution"]["high_count"] == 1
    assert payload["severity_distribution"]["total_qualifying"] == 2
    # Trust zones reversed: untrusted first (position 0)
    assert payload["layers"][0]["source_kind"] == "trust_zone"
    untrusted_layer = payload["layers"][0]
    assert untrusted_layer["position"] == 0
    # Callouts should reference S-1 (Edge / API Gateway) and T-1 (Internal / Backend)
    callout_ids = {c["finding_id"] for c in payload["callouts"]}
    assert "S-1" in callout_ids
    assert "T-1" in callout_ids

    # Skip-image case: no Critical/High
    findings_low = [
        {"id": "L-1", "component": "API Gateway", "threat": "low issue",
         "risk_level": "Low"},
    ]
    payload = build("threats", findings_low, scope, "/tmp/threats.md")
    assert payload["metadata"]["skip_image"] is True
    assert payload["callouts"] == []
    assert payload["severity_distribution"]["total_qualifying"] == 0

    # Fallback: no trust zones, DFD-type fallback used
    fallback_scope = {
        "components": [
            {"name": "Public API", "type": "api", "description": ""},
            {"name": "Backend", "type": "service", "description": ""},
        ],
        "data_flows": [],
        "trust_boundaries": [],
        "boundary_crossings": [],
    }
    payload = build("threats", findings[:2], fallback_scope, "/tmp/threats.md")
    assert payload["metadata"]["fallback_used"] is True
    assert all(layer["source_kind"] == "dfd_type" for layer in payload["layers"])

    # Error: no scope data at all
    empty_scope = {
        "components": [],
        "data_flows": [],
        "trust_boundaries": [],
        "boundary_crossings": [],
    }
    result = build("threats", [], empty_scope, "/tmp/threats.md")
    assert result == {"error": "no_scope_data"}


@pytest.mark.parametrize(
    "template",
    [
        "baseball-card",
        "system-architecture",
        "risk-funnel",
        "maestro-stack",
        "maestro-heatmap",
    ],
)
def test_existing_templates_unchanged(template):
    """Pre-existing templates produce byte-identical output to the frozen golden files.

    Goldens in ``tests/scripts/fixtures/golden/`` are the backward-compatibility
    baseline — any drift indicates a regression in an existing template.
    """
    golden_path = GOLDEN_DIR / f"{template}.json"
    assert golden_path.exists(), f"Missing golden file: {golden_path}"
    returncode, _stdout, stderr, payload = run_extract(
        FIXTURES_DIR / "agentic_app", template
    )
    assert returncode == 0, f"Expected exit 0 for {template}, got {returncode}. stderr: {stderr}"
    assert payload is not None
    with open(golden_path, "r", encoding="utf-8") as fh:
        expected = json.load(fh)
    assert payload == expected, (
        f"Template {template} output drifted from golden baseline. "
        "Backward compatibility regression."
    )


# -----------------------------------------------------------------------------
# F-212 L2 — Per-layer floor-rule fixture matrix (TDD red-bar tests)
#
# These tests codify the FR-212-8 / FR-212-9 / FR-212-11 / FR-212-12 invariants
# for the reworked _select_critical_high_callouts() (US-212-2). They are
# intentionally authored RED-BAR before the L2 implementation lands in T016/T017
# (Wave 3): the existing per-layer-dedup logic emits ≤1 callout per layer, so
# these assertions do not yet hold on most fixtures. The tests will go GREEN
# once the Largest Remainder Method allocator with floor + ceiling rules ships.
#
# Fixture matrix (created in T012):
#   - absent                  — 0 qualifying findings → skip_image=True, callouts=[]
#   - single-layer            — 1 qualifying layer / 2 findings
#   - two-layer               — 2 qualifying layers / 3+2 findings
#   - three-layer             — 3 qualifying layers / 4+3+2 findings
#   - all-layers-qualifying   — 5 qualifying layers / 11 findings (>8 cap)
# -----------------------------------------------------------------------------

# Map fixture directory → expected behavior anchor.
# - qualifying_findings: total Critical+High findings present in threats.md
# - qualifying_layer_count: layers with ≥1 qualifying finding (NOT len(layers))
_F212_L2_FIXTURES = [
    ("absent", 0, 0),
    ("single-layer", 2, 1),
    ("two-layer", 5, 2),
    ("three-layer", 9, 3),
    ("all-layers-qualifying", 11, 5),
]

_QUALIFYING_SEVERITIES = {"Critical", "High"}
_PER_LAYER_CEILING = 4
_TOTAL_CAP = 8


def _qualifying_layer_names(payload):
    """Return the set of layer names that have ≥1 callout in the payload.

    The reworked L2 _select_critical_high_callouts must populate ≥1 callout for
    every layer that has ≥1 qualifying finding (per-layer floor) when total-cap
    permits, so the set returned by this helper should equal the set of layer
    names that contained ≥1 qualifying finding (computed from `payload['layers']`
    + `payload['callouts']`).
    """
    return {c["layer_name"] for c in payload["callouts"]}


@pytest.mark.parametrize(
    "fixture_name,total_qualifying,qualifying_layer_count",
    _F212_L2_FIXTURES,
    ids=[f[0] for f in _F212_L2_FIXTURES],
)
def test_per_layer_floor_invariant(
    fixture_name, total_qualifying, qualifying_layer_count
):
    """F-212 L2: per-layer floor + total-cap + per-layer ceiling invariants.

    For every fixture in the matrix, the payload's callouts[] MUST satisfy:
      (a) len(callouts) ≤ 8 (FR-212-9 total-cap)
      (b) every qualifying layer has ≥1 callout when qualifying_layer_count ≤ 8
          (FR-212-9 per-layer floor)
      (c) no single layer has more than 4 callouts (FR-212-9 per-layer ceiling)
      (d) on the `absent` fixture, metadata.skip_image == True AND callouts == []
          (preserves PRD-128 skip-image contract for zero-finding inputs)

    RED-BAR pre-F-212: the legacy per-layer-dedup logic emits at most 1 callout
    per layer, so single-layer and most multi-layer fixtures will fail (b)
    because layers with multiple qualifying findings still receive only 1
    callout. The `absent` case (d) should already pass because skip_image and
    empty callouts are independent of the L2 selection algorithm.
    """
    returncode, _stdout, stderr, payload = run_extract(
        FIXTURES_DIR / fixture_name, "executive-architecture"
    )
    assert returncode == 0, (
        f"[{fixture_name}] Expected exit 0, got {returncode}. stderr: {stderr}"
    )
    assert payload is not None, f"[{fixture_name}] Expected payload to be written"

    # (d) absent fixture: skip-image short-circuit + empty callouts.
    if fixture_name == "absent":
        assert payload["metadata"]["skip_image"] is True, (
            f"[{fixture_name}] Expected metadata.skip_image=True for "
            f"zero-qualifying-finding input"
        )
        assert payload["callouts"] == [], (
            f"[{fixture_name}] Expected empty callouts[] for "
            f"zero-qualifying-finding input; got {len(payload['callouts'])}"
        )
        return  # Remaining invariants are vacuous when callouts==[].

    callouts = payload["callouts"]

    # (a) Total-cap: ≤ 8 callouts.
    assert len(callouts) <= _TOTAL_CAP, (
        f"[{fixture_name}] FR-212-9 total-cap violated: "
        f"len(callouts)={len(callouts)} > {_TOTAL_CAP}"
    )

    # (a') Density (FR-212-8): 6–8 callouts when system-wide qualifying count ≥ 6.
    # When total_qualifying < 6, total-floor rule emits all qualifying findings
    # exactly (no synthetic inflation) — so we expect callouts == total_qualifying.
    # This is the assertion that makes the test red-bar pre-F-212: the legacy
    # per-layer-dedup logic emits ≤ qualifying_layer_count callouts, never the
    # 6–8 system-wide density target.
    if total_qualifying >= 6:
        assert 6 <= len(callouts) <= _TOTAL_CAP, (
            f"[{fixture_name}] FR-212-8 density violated: "
            f"system-wide qualifying count={total_qualifying} ≥ 6 should yield "
            f"6-8 callouts; got {len(callouts)}"
        )
    else:
        assert len(callouts) == total_qualifying, (
            f"[{fixture_name}] FR-212-9 total-floor violated: "
            f"system-wide qualifying count={total_qualifying} < 6 should yield "
            f"exactly {total_qualifying} callouts; got {len(callouts)}"
        )

    # (b) Per-layer floor: every qualifying layer represented when count ≤ 8.
    if qualifying_layer_count <= _TOTAL_CAP:
        represented_layers = _qualifying_layer_names(payload)
        assert len(represented_layers) == qualifying_layer_count, (
            f"[{fixture_name}] FR-212-9 per-layer floor violated: "
            f"expected all {qualifying_layer_count} qualifying layers to have "
            f"≥1 callout, got {len(represented_layers)} represented layers "
            f"({sorted(represented_layers)})"
        )

    # (c) Per-layer ceiling: no layer exceeds 4 callouts.
    per_layer_counts = {}
    for c in callouts:
        per_layer_counts[c["layer_name"]] = per_layer_counts.get(
            c["layer_name"], 0
        ) + 1
    for layer_name, count in per_layer_counts.items():
        assert count <= _PER_LAYER_CEILING, (
            f"[{fixture_name}] FR-212-9 per-layer ceiling violated: "
            f"layer '{layer_name}' has {count} callouts > {_PER_LAYER_CEILING}"
        )


def test_callouts_deterministic():
    """F-212 L2: two consecutive runs on identical input emit byte-identical callouts[].

    Determinism is the ADR-017 invariant restated for callouts[] in FR-212-12.
    The pre-F-212 implementation already satisfies this contract (sort_key is
    deterministic in `_select_critical_high_callouts`); this test guards
    against regressions when the L2 Largest-Remainder allocator lands.

    Both runs are invoked under SOURCE_DATE_EPOCH=1700000000 (ADR-021) so
    timestamps and other env-derived values are frozen — the comparison is
    therefore byte-strict on json.dumps(..., sort_keys=True) of the callouts
    array.
    """
    target = FIXTURES_DIR / "three-layer"
    env_overlay = ["--frozen-time"] if False else None  # extractor lacks the flag
    # Set SOURCE_DATE_EPOCH via env for both runs; the script does not honor a
    # CLI flag for the executive-architecture branch, so we set env on the
    # subprocess rather than altering run_extract.
    env = dict(os.environ)
    env["SOURCE_DATE_EPOCH"] = "1700000000"

    payloads = []
    for _ in range(2):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            output_path = f.name
        try:
            cmd = [
                sys.executable,
                str(SCRIPT_PATH),
                "--target-dir", str(target),
                "--template", "executive-architecture",
                "--output", output_path,
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, env=env
            )
            assert result.returncode == 0, (
                f"Expected exit 0, got {result.returncode}. stderr: {result.stderr}"
            )
            with open(output_path, "r", encoding="utf-8") as fh:
                payloads.append(json.load(fh))
        finally:
            try:
                os.unlink(output_path)
            except OSError:
                pass

    # Byte-identical callouts[] across both runs.
    callouts1 = json.dumps(payloads[0]["callouts"], sort_keys=True)
    callouts2 = json.dumps(payloads[1]["callouts"], sort_keys=True)
    assert callouts1 == callouts2, (
        "FR-212-12 determinism violated: callouts[] differ between two "
        "consecutive runs on identical input under SOURCE_DATE_EPOCH=1700000000."
    )


def test_superset_invariant():
    """F-212 L2: every layer that qualifies under the OLD per-layer-dedup logic
    appears in the NEW callouts[] with ≥1 entry (Team-Lead LOW-2 resolution).

    This is the mechanically-enforceable restatement of US-212-2 acceptance
    scenario 5 — "for every qualifying layer that contained ≥1 Critical/High
    finding under the old logic, that same layer appears in the new callouts[]
    with ≥1 entry." Implemented as a structural superset check on the new
    payload (no need to also run pre-F-212 code): grouping the new callouts[]
    by layer_name and taking the unique layer set must equal the set of layers
    that have ≥1 qualifying finding in the fixture.

    Uses the `three-layer` fixture (3 qualifying layers / 9 findings) as the
    representative populated case — exercises both the floor invariant and the
    superset relation in one assertion.

    RED-BAR pre-F-212: legacy logic emits exactly 1 callout per qualifying
    layer, so the superset relation IS satisfied for `three-layer` (3 layers,
    3 callouts, identical layer-name set). However, on fixtures where a layer
    has multiple qualifying findings the test still validates that no layer is
    DROPPED in the rework — once L2 lands, the superset must continue to hold
    for every fixture in the matrix, so this test will keep passing as the
    rework proceeds. Marked here as the structural drift guard.
    """
    fixture = FIXTURES_DIR / "three-layer"
    returncode, _stdout, stderr, payload = run_extract(
        fixture, "executive-architecture"
    )
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert payload is not None

    # The three-layer fixture has these 3 qualifying layers (each with ≥1
    # Critical/High finding). This is the OLD per-layer-dedup baseline — every
    # qualifying layer must appear with ≥1 entry in the NEW callouts[].
    expected_qualifying_layers = {"Edge Zone", "Core Zone", "Data Zone"}

    # Compute the NEW post-rework set: unique layer_names across callouts[].
    new_represented_layers = {c["layer_name"] for c in payload["callouts"]}

    missing = expected_qualifying_layers - new_represented_layers
    assert not missing, (
        f"FR-212-11 superset invariant violated: layers {sorted(missing)} "
        f"qualified under the pre-F-212 per-layer-dedup logic but are not "
        f"represented in the new callouts[]. Got layers: "
        f"{sorted(new_represented_layers)}"
    )

    # Every callout's layer must be one of the qualifying layers (no spurious
    # layers introduced by the rework).
    spurious = new_represented_layers - expected_qualifying_layers
    assert not spurious, (
        f"FR-212-11 superset invariant violated: callouts reference layers "
        f"{sorted(spurious)} that did not have qualifying findings under the "
        f"pre-F-212 logic."
    )


# -----------------------------------------------------------------------------
# F-315 US-2 / #312 — maestro-stack 7-layer completeness + code-computed counts
#
# Contract: specs/315-maestro-output-completeness-round-2/
#   contracts/maestro-stack-template-data.contract.md + data-model.md (Decision B).
#
# The maestro-stack template_data MUST (a) present all 7 canonical MAESTRO layers
# (backfilling layers absent from the parsed table with finding_count: 0), and
# (b) emit three code-computed integer counts: layers_with_findings, empty_layers,
# layer_count (=7). Two fixture cases pin correctness:
#   - MIXED  (maestro_partial, a genuine 3-of-7-row table): layers_with_findings=3,
#            empty_layers=4 — proves backfill + correct counting on a partial table.
#   - EMPTY  (agentic_app, table-less): layers_with_findings=0, empty_layers=7 —
#            proves graceful all-empty backfill.
# FR-004: the maestro-heatmap payload is NOT changed by this work (asserted in the
# golden byte-gate test_existing_templates_unchanged + the heatmap golden).
# -----------------------------------------------------------------------------

# Canonical MAESTRO layer IDs in L1->L7 order (mirrors tachi_parsers.MAESTRO_LAYERS).
_CANONICAL_MAESTRO_LAYER_IDS = ["L1", "L2", "L3", "L4", "L5", "L6", "L7"]
# Canonical layer names as the table parser produces them (the segment AFTER the
# em-dash in "L1 — Foundation Model"). Backfilled layers must use these names.
_CANONICAL_MAESTRO_LAYER_NAMES = {
    "L1": "Foundation Model",
    "L2": "Data Operations",
    "L3": "Agent Framework",
    "L4": "Deployment Infrastructure",
    "L5": "Evaluation and Observability",
    "L6": "Security and Compliance",
    "L7": "Agent Ecosystem",
}


def _maestro_stack_template_data(fixture_name):
    """Run the maestro-stack extractor on a fixture and return its template_data."""
    returncode, _stdout, stderr, payload = run_extract(
        FIXTURES_DIR / fixture_name, "maestro-stack"
    )
    assert returncode == 0, (
        f"[{fixture_name}] Expected exit 0, got {returncode}. stderr: {stderr}"
    )
    assert payload is not None, f"[{fixture_name}] Expected JSON payload to be written"
    assert "template_data" in payload, f"[{fixture_name}] Missing template_data"
    return payload["template_data"]


def test_maestro_stack_emits_count_keys_present():
    """FR-002: maestro-stack template_data carries the three code-computed count keys.

    layers_with_findings, empty_layers, layer_count MUST all be present and be ints.
    Checked on both the mixed (maestro_partial) and all-empty (agentic_app) fixtures.
    """
    for fixture_name in ("maestro_partial", "agentic_app"):
        td = _maestro_stack_template_data(fixture_name)
        for key in ("layers_with_findings", "empty_layers", "layer_count"):
            assert key in td, (
                f"[{fixture_name}] maestro-stack template_data missing '{key}'; "
                f"keys present: {sorted(td.keys())}"
            )
            assert isinstance(td[key], int), (
                f"[{fixture_name}] '{key}' must be an int, got {type(td[key]).__name__}"
            )


def test_maestro_stack_count_identity_holds():
    """FR-002 invariant: layers_with_findings + empty_layers == layer_count == 7.

    Holds for every fixture regardless of how many layers carry findings.
    """
    for fixture_name in ("maestro_partial", "agentic_app"):
        td = _maestro_stack_template_data(fixture_name)
        assert td["layer_count"] == 7, (
            f"[{fixture_name}] layer_count must be 7, got {td['layer_count']}"
        )
        assert td["layers_with_findings"] + td["empty_layers"] == td["layer_count"], (
            f"[{fixture_name}] identity violated: "
            f"{td['layers_with_findings']} + {td['empty_layers']} != "
            f"{td['layer_count']}"
        )
        assert td["layers_with_findings"] + td["empty_layers"] == 7, (
            f"[{fixture_name}] layers_with_findings + empty_layers must equal 7"
        )


def test_maestro_stack_mixed_counts_partial_fixture():
    """FR-002/FR-003 mixed case: 3-of-7-row table → 3 with findings, 4 backfilled empty.

    The maestro_partial fixture's "Risk by MAESTRO Layer" table lists exactly 3
    finding-bearing layers (L1, L3, L5). The extractor MUST backfill the 4 absent
    layers (L2, L4, L6, L7) at finding_count 0, yielding the mixed counts.
    """
    td = _maestro_stack_template_data("maestro_partial")
    assert td["layers_with_findings"] == 3, (
        f"Expected layers_with_findings=3 on the 3-of-7 partial table, "
        f"got {td['layers_with_findings']}"
    )
    assert td["empty_layers"] == 4, (
        f"Expected empty_layers=4 (backfilled L2/L4/L6/L7), "
        f"got {td['empty_layers']}"
    )
    assert td["layer_count"] == 7


def test_maestro_stack_all_empty_counts_table_less_fixture():
    """FR-002/FR-003 all-empty case: table-less input → 0 with findings, 7 empty.

    The agentic_app fixture has no "Risk by MAESTRO Layer" table, so all 7 layers
    are backfilled at finding_count 0 (graceful empty state, not an error).
    """
    td = _maestro_stack_template_data("agentic_app")
    assert td["layers_with_findings"] == 0, (
        f"Expected layers_with_findings=0 on a table-less fixture, "
        f"got {td['layers_with_findings']}"
    )
    assert td["empty_layers"] == 7, (
        f"Expected empty_layers=7 on a table-less fixture, "
        f"got {td['empty_layers']}"
    )
    assert td["layer_count"] == 7


def test_maestro_stack_distribution_backfilled_to_seven():
    """FR-003: maestro_layer_distribution always has exactly 7 canonical entries.

    Holds on both the partial (3-row) and table-less fixtures. Entries are in
    canonical L1->L7 order; layers absent from the parsed table are backfilled
    with finding_count 0 and the canonical layer_name produced by the table parser.
    """
    for fixture_name in ("maestro_partial", "agentic_app"):
        td = _maestro_stack_template_data(fixture_name)
        dist = td["maestro_layer_distribution"]
        assert len(dist) == 7, (
            f"[{fixture_name}] expected 7 distribution entries, got {len(dist)}"
        )
        assert [e["layer_id"] for e in dist] == _CANONICAL_MAESTRO_LAYER_IDS, (
            f"[{fixture_name}] distribution not in canonical L1->L7 order: "
            f"{[e['layer_id'] for e in dist]}"
        )
        # Every backfilled (finding_count == 0) entry must carry the canonical
        # name and an integer >= 0 finding_count.
        for e in dist:
            assert isinstance(e["finding_count"], int) and e["finding_count"] >= 0
            if e["finding_count"] == 0:
                assert e["layer_name"] == _CANONICAL_MAESTRO_LAYER_NAMES[e["layer_id"]], (
                    f"[{fixture_name}] backfilled {e['layer_id']} has name "
                    f"{e['layer_name']!r}, expected "
                    f"{_CANONICAL_MAESTRO_LAYER_NAMES[e['layer_id']]!r}"
                )
        # layers_with_findings must equal the number of non-zero entries.
        non_zero = sum(1 for e in dist if e["finding_count"] > 0)
        assert td["layers_with_findings"] == non_zero, (
            f"[{fixture_name}] layers_with_findings ({td['layers_with_findings']}) "
            f"!= non-zero distribution entries ({non_zero})"
        )


def test_maestro_stack_per_layer_summaries_cover_all_seven():
    """FR-003: per_layer_summaries also covers all 7 canonical layers.

    The backfilled 7-entry distribution drives per_layer_summaries, so every
    canonical layer gets a summary even when its finding_count is 0.
    """
    for fixture_name in ("maestro_partial", "agentic_app"):
        td = _maestro_stack_template_data(fixture_name)
        summaries = td["per_layer_summaries"]
        assert len(summaries) == 7, (
            f"[{fixture_name}] expected 7 per_layer_summaries, got {len(summaries)}"
        )
        assert [s["layer_id"] for s in summaries] == _CANONICAL_MAESTRO_LAYER_IDS, (
            f"[{fixture_name}] per_layer_summaries not canonical L1->L7: "
            f"{[s['layer_id'] for s in summaries]}"
        )


def test_maestro_stack_deterministic_byte_identical():
    """ADR-017: two extraction runs on identical input emit byte-identical JSON.

    Compares the full serialized output file (not just template_data) across two
    runs of the maestro-stack extractor on the partial fixture — the new integer
    count keys sort deterministically under json.dumps(sort_keys=True, indent=2).
    """
    target = FIXTURES_DIR / "maestro_partial"
    outputs = []
    for _ in range(2):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            output_path = f.name
        try:
            cmd = [
                sys.executable,
                str(SCRIPT_PATH),
                "--target-dir", str(target),
                "--template", "maestro-stack",
                "--output", output_path,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            assert result.returncode == 0, (
                f"Expected exit 0, got {result.returncode}. stderr: {result.stderr}"
            )
            with open(output_path, "r", encoding="utf-8") as fh:
                outputs.append(fh.read())
        finally:
            try:
                os.unlink(output_path)
            except OSError:
                pass
    assert outputs[0] == outputs[1], (
        "maestro-stack output is not byte-identical across two runs on identical "
        "input (ADR-017 determinism violated)."
    )


# -----------------------------------------------------------------------------
# F-311 US-2 / #311 — maestro-stack coverage_state (clean vs n/a) + backfill survival
#
# Contract: specs/311-maestro-matrix-model-b-clean-vs-na/
#   data-model.md (Entity 2/3 + the examples/microservices fixture map) +
#   contracts/cross-surface-consistency.contract.md + ADR-047 (D2/D3/D4).
#
# The maestro-stack per_layer_summaries MUST carry a `coverage_state` enum
# (findings | clean | not_applicable) derived from THIS layer's carried Section-6
# token via classify_maestro_coverage_state ALONE (ADR-047 D2). D3 fence: it is
# NOT derived from parse_component_layer_mapping()/component_layer_map — that
# Section-1 path stays heatmap-only (the heatmap golden is byte-frozen, asserted
# in test_existing_templates_unchanged[maestro-heatmap]). D4: a *present*
# not_applicable token survives the absent-layer backfill merge and is never
# overwritten to clean/empty.
#
# examples/microservices is the regression anchor (data-model.md): L2/L4=findings,
# L7=clean. (L1/L3/L5/L6 carry the n/a token once the orchestrator/populator
# authors it on baseline regen — Phase D / T018; this infographic-track test
# does not depend on that un-landed change, so it asserts those four layers'
# state from their *carried token* via the same classifier, which is correct both
# before and after T018. The cross-surface gate T015 hard-pins the post-regen map.)
# -----------------------------------------------------------------------------

EXAMPLES_DIR = REPO_ROOT / "examples"

# Canonical Model-B zero-finding tokens — MUST byte-match Phase A
# (tachi_parsers.classify_maestro_coverage_state) and the orchestrator directive.
_CLEAN_TOKEN = "Analyzed — no findings this scan"
_NA_TOKEN = "Not applicable — no components map to this layer"


def _import_classify_coverage_state():
    """Import the shared classifier the extractor inherits (read-only check)."""
    scripts_dir = REPO_ROOT / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from tachi_parsers import classify_maestro_coverage_state
    return classify_maestro_coverage_state


def _summaries_by_layer(template_data):
    """Index per_layer_summaries by layer_id for state assertions."""
    return {s["layer_id"]: s for s in template_data["per_layer_summaries"]}


def test_microservices_per_layer_coverage_state():
    """data-model anchor: coverage_state on the real examples/microservices.

    L2/L4 carry findings (finding_count > 0) → "findings"; L7 is clean (in-scope,
    zero findings). Every zero-finding layer resolves to a valid zero-finding state,
    and every layer's emitted coverage_state equals the shared classifier applied to
    its own carried Section-6 token (proving the maestro-stack inherits the carried
    cell via the classifier — ADR-047 D2 — end-to-end on a real example).
    """
    classify = _import_classify_coverage_state()
    td = _maestro_stack_template_data_for(EXAMPLES_DIR / "microservices")
    by_layer = _summaries_by_layer(td)

    assert set(by_layer) == set(_CANONICAL_MAESTRO_LAYER_IDS), (
        f"microservices must emit all 7 canonical layers, got {sorted(by_layer)}"
    )
    # Findings layers (per data-model fixture map): L2 (8 findings), L4 (14).
    assert by_layer["L2"]["coverage_state"] == "findings", by_layer["L2"]
    assert by_layer["L4"]["coverage_state"] == "findings", by_layer["L4"]
    # L7 is in-scope with zero findings → clean (holds before AND after T018).
    assert by_layer["L7"]["coverage_state"] == "clean", by_layer["L7"]

    for lid, s in by_layer.items():
        # coverage_state is a pure function of the carried token (ADR-047 D2):
        expected = classify(s["finding_count"], s["highest_severity"])
        assert s["coverage_state"] == expected, (
            f"{lid}: coverage_state {s['coverage_state']!r} != classifier(token) "
            f"{expected!r} for carried cell {s['highest_severity']!r}"
        )
        # Every zero-finding layer is a valid zero-finding state (never "findings").
        if s["finding_count"] == 0:
            assert s["coverage_state"] in ("clean", "not_applicable"), (
                f"{lid}: zero-finding layer has invalid state {s['coverage_state']!r}"
            )


def test_present_not_applicable_token_survives_backfill(tmp_path):
    """ADR-047 D4: a PRESENT n/a token survives the backfill merge (not → clean/empty).

    Synthetic Section-6 table with explicit n/a rows (L1, L3), a findings row (L2),
    a clean row (L7), and layers absent from the table (L4/L5/L6). Asserts:
      - present n/a rows  → coverage_state "not_applicable" (the merge did NOT
        overwrite the authored token back to clean/empty);
      - present clean row → "clean"; findings row → "findings";
      - absent (backfilled) layers default to "clean" (D4 default — preserves
        today's table-less behavior; never silently "findings").
    This exercises D4 on the present-row path without mutating the committed
    examples/ source (owned by the Phase-D baseline-regen track).
    """
    threats = tmp_path / "threats.md"
    threats.write_text(
        "---\nproject: NA Survival Fixture\n---\n\n"
        "## 1. System Overview\n\n### Components\n\n"
        "| Component | Type | MAESTRO Layer |\n"
        "|-----------|------|---------------|\n"
        "| Client App | external | L7 — Agent Ecosystem |\n\n"
        "## 6. Risk Summary\n\n#### Risk by MAESTRO Layer\n\n"
        "| MAESTRO Layer | Finding Count | Highest Severity |\n"
        "|---------------|---------------|------------------|\n"
        f"| L1 — Foundation Model | 0 | {_NA_TOKEN} |\n"
        "| L2 — Data Operations | 3 | High |\n"
        f"| L3 — Agent Framework | 0 | {_NA_TOKEN} |\n"
        f"| L7 — Agent Ecosystem | 0 | {_CLEAN_TOKEN} |\n",
        encoding="utf-8",
    )
    td = _maestro_stack_template_data_for(tmp_path)
    by_layer = _summaries_by_layer(td)

    # Present n/a tokens MUST survive — the load-bearing D4 assertion.
    assert by_layer["L1"]["coverage_state"] == "not_applicable", (
        f"present n/a token overwritten on L1: {by_layer['L1']}"
    )
    assert by_layer["L3"]["coverage_state"] == "not_applicable", (
        f"present n/a token overwritten on L3: {by_layer['L3']}"
    )
    # Other present rows classify as authored.
    assert by_layer["L2"]["coverage_state"] == "findings", by_layer["L2"]
    assert by_layer["L7"]["coverage_state"] == "clean", by_layer["L7"]
    # Absent layers backfill to the D4 clean default (never "findings").
    for lid in ("L4", "L5", "L6"):
        assert by_layer[lid]["coverage_state"] == "clean", (
            f"absent layer {lid} did not backfill to clean default: {by_layer[lid]}"
        )


def test_table_less_fixture_backfills_all_to_clean():
    """ADR-047 D4 default: a table-less input backfills all 7 layers to "clean".

    The agentic_app fixture (no Risk-by-MAESTRO-Layer table) is the golden source
    for maestro-stack; every backfilled layer carries coverage_state "clean",
    preserving Model-A behavior when applicability is unknowable. (Locks the
    additive shape of the regenerated maestro-stack.json golden.)
    """
    td = _maestro_stack_template_data("agentic_app")
    for s in td["per_layer_summaries"]:
        assert s["coverage_state"] == "clean", (
            f"table-less backfill: {s['layer_id']} state {s['coverage_state']!r} "
            "!= clean (D4 default)"
        )


def _maestro_stack_template_data_for(target_dir):
    """Run the maestro-stack extractor on an arbitrary target dir; return template_data."""
    returncode, _stdout, stderr, payload = run_extract(target_dir, "maestro-stack")
    assert returncode == 0, (
        f"[{target_dir}] Expected exit 0, got {returncode}. stderr: {stderr}"
    )
    assert payload is not None, f"[{target_dir}] Expected JSON payload to be written"
    assert "template_data" in payload, f"[{target_dir}] Missing template_data"
    return payload["template_data"]


# =============================================================================
# Feature 373 US-3a: K9, K10, K12 extractor-level wiring (tasks.md T019).
# Fixtures: tests/scripts/fixtures/fidelity_373/ (see its README.md for
# hand-computed expected values). The pure tachi_parsers.py-level pins for
# these same fixtures live in test_tachi_parsers.py (T016); the tests below
# instead exercise extract-infographic-data.py's own wiring.
# =============================================================================


def test_k9_shortform_bands_wire_through_extract_severity(extract_infographic_data):
    # US-3a #1-#2 (K9/FR-K9.1-K9.2): short-form headers (Inherent, Status,
    # Residual, Residual Sev.) plus an empty Critical band and an empty
    # last band before Summary Statistics must surface correctly through
    # extract_severity, the infographic extractor's own severity/findings
    # wrapper around parse_compensating_controls_md.
    cc_content = _read_fidelity_fixture("controls_bands_shortform", "compensating-controls.md")
    severity, findings, cc_data = extract_infographic_data.extract_severity(
        1, "", cc_content=cc_content
    )
    assert severity == {"critical": 0, "high": 1, "medium": 1, "low": 0, "note": 0, "total": 2}
    assert [f["id"] for f in findings] == ["T-1", "T-2"]
    assert cc_data is not None


def test_k10_h3_heading_equals_h4_form(extract_infographic_data):
    # US-3a #4 (K10/FR-K10.1): a "###" heading and its "####" twin must
    # produce byte-for-byte identical layer distributions through
    # parse_maestro_layer_distribution -- not merely "parses without
    # error" (already pinned per-fixture in test_tachi_parsers.py).
    h3_content = _read_fidelity_fixture("maestro_heading_h3", "threats.md")
    assert "### Risk by MAESTRO Layer" in h3_content
    h4_content = h3_content.replace("### Risk by MAESTRO Layer", "#### Risk by MAESTRO Layer", 1)
    layers_h3 = extract_infographic_data.parse_maestro_layer_distribution(h3_content)
    layers_h4 = extract_infographic_data.parse_maestro_layer_distribution(h4_content)
    assert layers_h3 == layers_h4
    assert len(layers_h3) == 2


def _delta_via_cli(target_dir, template="baseball-card"):
    """Run the CLI end to end and return (payload, stderr)."""
    returncode, _stdout, stderr, payload = run_extract(target_dir, template)
    assert returncode == 0, f"[{target_dir}] expected exit 0, got {returncode}. stderr: {stderr}"
    assert payload is not None, f"[{target_dir}] expected a JSON payload"
    return payload, stderr


def test_k12_baseline_4c_exact_delta_counts_via_cli():
    # US-3a #5 (K12/FR-K12.1-K12.2): the 4c baseline's bracketed-status
    # variety (bare NEW, [NEW], **[NEW]**, `[NEW]`) plus one placeholder
    # resolved row, wired through the CLI end to end (delta_counts is
    # already wired at this call site since T016; this pins the whole
    # payload shape, not just the underlying compute_delta_counts call).
    payload, _stderr = _delta_via_cli(FIDELITY_FIXTURES_DIR / "baseline_resolved_4c")
    assert payload["delta"]["delta_counts"] == {
        "new": 4, "updated": 1, "unchanged": 1, "resolved": 2,
    }


def test_k12_baseline_4b_legacy_matches_4c_resolved_count_via_cli():
    # US-3a #6: the legacy "## 4b." heading yields the same resolved count
    # as its "## 4c." twin, end to end.
    payload, _stderr = _delta_via_cli(FIDELITY_FIXTURES_DIR / "baseline_resolved_4b_legacy")
    assert payload["delta"]["delta_counts"]["resolved"] == 2


def test_k12_non_baseline_no_status_column_no_warning_via_cli():
    # US-3a #7 (second half): a non-baseline run whose Section 7 has no
    # Status column must not warn, and carries no "delta" key at all
    # end to end (has_baseline gates the key's emission in main()).
    payload, stderr = _delta_via_cli(FIDELITY_FIXTURES_DIR / "non_baseline_no_status_column")
    assert payload.get("delta") is None
    assert "Section 7" not in stderr


def test_k12_id_mismatch_absolute_tallies_and_one_warning_via_cli():
    # US-3a #7 (first half); architect F1/NM-1: both surfaces must report
    # the Section 7 tallies as absolute values (the normalized map's own
    # counts, not restricted to the tier's finding-ID set) and emit
    # exactly one ID-set warning. EXPECTED RED until Lane B2a's T017 wires
    # warn_delta_scope with this tier's finding IDs at this call site --
    # at T019 time nothing in extract-infographic-data.py calls
    # warn_delta_scope yet (the parser-level function is already fully
    # pinned in test_tachi_parsers.py; this is the wiring gap).
    payload, stderr = _delta_via_cli(FIDELITY_FIXTURES_DIR / "baseline_status_id_mismatch")
    assert payload["delta"]["delta_counts"] == {
        "new": 1, "updated": 1, "unchanged": 1, "resolved": 0,
    }
    assert stderr.count("Section 7 status IDs differ from tier finding IDs") == 1
    assert "(1 only-in-map, 1 only-in-tier)" in stderr


# =============================================================================
# Feature 373 US-3b: K11 risk funnel (tasks.md T023). Fixtures:
# tests/scripts/fixtures/fidelity_373/funnel_* and
# controls_warnings_kitchen_sink (see that directory's README.md for
# hand-computed expected values). The pure tachi_parsers.py-level pins
# (classify_control_status, the inherent join, the residual clamp) live in
# test_tachi_parsers.py (T020); the tests below instead exercise
# extract-infographic-data.py's own funnel computation (compute_risk_funnel,
# T021) end to end through the CLI, including the S-9 baseball-card totals
# and the Section 1 / row-count warnings (T021's own follow-on work).
# =============================================================================


def _funnel_via_cli(target_dir, template="risk-funnel"):
    """Run the CLI end to end and return (template_data, stderr)."""
    returncode, _stdout, stderr, payload = run_extract(target_dir, template)
    assert returncode == 0, f"[{target_dir}] expected exit 0, got {returncode}. stderr: {stderr}"
    assert payload is not None, f"[{target_dir}] expected a JSON payload"
    return payload["template_data"], stderr


def _widths(template_data):
    return [t["width"] for t in template_data["funnel_tiers"]]


def _volumes(template_data):
    return [t["volume"] for t in template_data["funnel_tiers"]]


def _reduction_pcts(template_data):
    return [r["percentage"] for r in template_data["reduction_percentages"]]


def test_k11_funnel_step_bound_widths_and_reductions_via_cli():
    # US-3b #1: both raw ratios (raw3=89.4375, raw4=88.3125) exceed their
    # upper clamp bound, so tiers 3 and 4 are STEP-bound rather than
    # ratio-bound (fixtures README).
    td, _stderr = _funnel_via_cli(FIDELITY_FIXTURES_DIR / "funnel_step_bound")
    assert _widths(td) == [100, 90, 80, 70]
    assert _volumes(td) == [None, 16.0, 15.9, 15.7]
    assert _reduction_pcts(td) == [0.0, 0.6, 1.3]
    assert td["risk_reduction"] == 1.9
    assert td["inherent_score"] == 16.0
    assert td["residual_score"] == 15.7
    assert [t["ghost"] for t in td["funnel_tiers"]] == [False, False, False, False]
    assert [t["count"] for t in td["funnel_tiers"][1:]] == [2, 2, 2]


def test_k11_funnel_strong_reduction_floor_bound_width_via_cli():
    # US-3b #2: raw4 (27) is below FLOOR=30, so Tier 4 is FLOOR-bound
    # rather than ratio- or STEP-bound.
    td, _stderr = _funnel_via_cli(FIDELITY_FIXTURES_DIR / "funnel_strong_reduction")
    assert _widths(td) == [100, 90, 54, 30]
    assert _volumes(td) == [None, 10.0, 6.0, 3.0]
    assert _reduction_pcts(td) == [0.0, 40.0, 50.0]
    assert td["risk_reduction"] == 70.0
    assert td["inherent_score"] == 10.0
    assert td["residual_score"] == 3.0


def test_k11_funnel_3tier_shape_via_cli():
    # US-3b #3: risk-scores.md only (no compensating-controls.md) selects
    # 3-tier mode. JSON tier-index 2 ("Unmitigated Risk") mirrors V2
    # exactly (no controls applied yet), and JSON tier-index 3 is always
    # ghost -- there is no residual data in 3-tier mode.
    td, _stderr = _funnel_via_cli(FIDELITY_FIXTURES_DIR / "funnel_3tier")
    tiers = td["funnel_tiers"]
    assert [t["ghost"] for t in tiers] == [False, False, False, True]
    assert _widths(td) == [100, 90, 80, 70]
    assert tiers[2]["volume"] == 14.0
    assert tiers[2]["label"] == "Unmitigated Risk"
    assert _reduction_pcts(td) == [0.0, 0.0, None]
    assert td["risk_reduction"] is None


def test_k11_funnel_threats_only_shape_via_cli():
    # US-3b #7 (first half): neither enrichment artifact is present, so
    # JSON tiers 1-3 are all ghost -- pure STEP cascade, and every
    # reduction is null because a ghost tier wins over "0.0 by
    # definition" for (0->1) too.
    td, _stderr = _funnel_via_cli(FIDELITY_FIXTURES_DIR / "funnel_threats_only")
    tiers = td["funnel_tiers"]
    assert [t["ghost"] for t in tiers] == [False, True, True, True]
    assert _widths(td) == [100, 90, 80, 70]
    assert _volumes(td) == [None, None, None, None]
    assert _reduction_pcts(td) == [None, None, None]
    assert td["risk_reduction"] is None


def test_k11_funnel_volumes_unavailable_shape_via_cli():
    # US-3b #7 (second half)/#8; data-model.md §4.3 condition 1: the
    # Coverage Matrix has no Inherent column at all and no risk-scores.md
    # to join against, so no row carries an inherent score. Volumes are
    # unavailable (not zero) on every tier, but tiers 1-3 stay non-ghost
    # (real, just volumeless), and (0->1) still reads 0.0 since Tier 1
    # (JSON index 0) is real.
    td, stderr = _funnel_via_cli(FIDELITY_FIXTURES_DIR / "funnel_volumes_unavailable")
    tiers = td["funnel_tiers"]
    assert [t["ghost"] for t in tiers] == [False, False, False, False]
    assert _widths(td) == [100, 90, 80, 70]
    assert _volumes(td) == [None, None, None, None]
    assert _reduction_pcts(td) == [0.0, None, None]
    assert td["risk_reduction"] is None
    assert td["inherent_score"] is None
    assert td["residual_score"] is None
    assert (
        "Warning: no controls row carries an inherent score; funnel volumes "
        "and risk reduction are unavailable"
    ) in stderr

    # S-9: the baseball card must agree -- both surfaces null, never a
    # stale Section 1 figure standing in for an unmeasured reduction.
    card_td, _stderr = _funnel_via_cli(
        FIDELITY_FIXTURES_DIR / "funnel_volumes_unavailable", template="baseball-card"
    )
    assert card_td["risk_reduction"] is None
    assert card_td["inherent_score"] is None
    assert card_td["residual_score"] is None


def test_k11_funnel_join_inherent_less_volumes_via_cli():
    # US-3b #6; architect finding F2: the Coverage Matrix has no Inherent
    # column at all; both rows' inherent scores come from the sibling
    # risk-scores.md composites via ID join (already wired at the tier-1
    # extract_severity call site since T020/W1). This is the funnel's own
    # consumption of that join, not the join itself (already pinned at
    # the parser level in test_tachi_parsers.py).
    td, _stderr = _funnel_via_cli(FIDELITY_FIXTURES_DIR / "funnel_join_inherent_less")
    assert _widths(td) == [100, 90, 80, 70]
    assert _volumes(td) == [None, 15.0, 14.5, 14.1]
    assert _reduction_pcts(td) == [0.0, 3.3, 2.8]
    assert td["risk_reduction"] == 6.0
    assert td["inherent_score"] == 15.0
    assert td["residual_score"] == 14.1


def test_k11_controls_status_variants_wire_through_funnel_via_cli():
    # US-3b, K11 status wiring x K9/K11 status classes: Missing (silent),
    # empty (warns), unrecognized/"Foobar" (warns), "Partially Found"
    # (partial), "None found" (warns, classifies none) -- exercised
    # through the same rows that build V2/V3/V4, not merely at
    # classify_control_status's own unit level (test_tachi_parsers.py
    # already pins that in isolation). The clamp (W-9) rides along on the
    # same row set rather than a separate fixture.
    td, stderr = _funnel_via_cli(FIDELITY_FIXTURES_DIR / "controls_warnings_kitchen_sink")
    assert _widths(td) == [100, 90, 80, 70]
    assert _volumes(td) == [None, 57.7, 54.2, 52.7]
    assert _reduction_pcts(td) == [0.0, 6.1, 2.8]
    assert td["risk_reduction"] == 8.7
    assert [t["count"] for t in td["funnel_tiers"][1:]] == [10, 10, 10]
    assert (
        "1 controls rows have a residual above the inherent score "
        "(first: W-9); clamped"
    ) in stderr


def test_k11_controls_warnings_kitchen_sink_section1_and_row_count_via_cli():
    # data-model.md §4.5: the Section 1 comparand warning is deliberately
    # wrong on two of its three fields (inherent total 60.0 vs
    # row-derived 57.7; reduction pct 26.9 vs row-derived 8.7) and
    # deliberately correct on the third (residual total 52.7 both ways),
    # so exactly two field-warnings fire -- per-field, never aggregated,
    # and the matching field never warns (fixtures README). The row-count
    # mismatch (10 controls rows vs 11 risk-scores rows) is a separate
    # class. The exact <field> token isn't pinned by the contract (only
    # the stem "Warning: controls Section 1 <field> <a> differs from
    # row-derived <b>; using rows" is), so this matches on the invariant
    # numbers and wording rather than a guessed field spelling.
    _td, stderr = _funnel_via_cli(FIDELITY_FIXTURES_DIR / "controls_warnings_kitchen_sink")
    assert "Warning: controls rows (10) differ from risk-scores rows (11)" in stderr
    comparand_lines = [
        line for line in stderr.splitlines()
        if line.startswith("Warning: controls Section 1")
    ]
    assert len(comparand_lines) == 2, (
        "expected exactly 2 Section 1 comparand warnings (inherent total, "
        f"reduction pct; residual must NOT warn), got: {comparand_lines}"
    )
    joined = "\n".join(comparand_lines)
    assert re.search(r"60\.0\D+differs from row-derived\D*57\.7", joined)
    assert re.search(r"26\.9%?\D+differs from row-derived\D*8\.7%?", joined)
    assert "52.7" not in joined  # the matching residual field must not warn


def test_rc2_unreadable_risk_scores_table_single_warning_no_row_count_mismatch_via_cli():
    # RC-2 (K11, P0 architect finding F-2): when risk-scores.md's Scored
    # Threat Table can't be found (header drift -- here "## Section 2:
    # Scored Threat Table" instead of the expected "## 2. Scored Threat
    # Table" -- the real-world shape seen on maestro-reference and
    # consumer-agent-app/sample-report), the tier-1 funnel path must parse
    # risk-scores.md only once: exactly one "could not find Scored Threat
    # Table" warning, and no false "differ from risk-scores rows (0)"
    # comparison (data-model.md §4.5; contracts/extraction-data-contract.md
    # Row counts row, both amended at P0). Reuses the kitchen-sink
    # fixture's threats.md/compensating-controls.md (10 controls rows) so
    # the only variable is risk-scores.md's header.
    # test_k11_controls_warnings_kitchen_sink_section1_and_row_count_via_cli
    # above pins the *other* side: a genuinely-readable mismatch (11 vs 10)
    # must still fire.
    src = FIDELITY_FIXTURES_DIR / "controls_warnings_kitchen_sink"
    bad_header_risk_scores = (
        "# Risk Scores -- RC-2 regression (deliberately mis-headed)\n\n"
        "## Section 2: Scored Threat Table\n\n"
        "| ID | Component | Threat | Composite | Severity | CVSS | Exploit. |\n"
        "|---|---|---|---|---|---|---|\n"
        "| W-1 | API | Spoofing | 8.1 | Critical | 9.0 | High |\n"
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        (tmp / "threats.md").write_bytes((src / "threats.md").read_bytes())
        (tmp / "compensating-controls.md").write_bytes(
            (src / "compensating-controls.md").read_bytes()
        )
        (tmp / "risk-scores.md").write_text(bad_header_risk_scores, encoding="utf-8")
        returncode, _stdout, stderr, payload = run_extract(tmp, "risk-funnel")
    assert returncode == 0, f"expected exit 0, got {returncode}. stderr: {stderr}"
    assert payload is not None

    assert stderr.count("could not find Scored Threat Table in risk-scores.md") == 1, (
        f"expected exactly one occurrence, got stderr: {stderr}"
    )
    assert "differ from risk-scores rows" not in stderr, (
        "an unreadable risk-scores table must never be compared as (0) rows; "
        f"got stderr: {stderr}"
    )


def test_k11_baseball_card_and_funnel_agree_on_totals_via_cli():
    # S-9: the baseball card's risk_reduction/inherent_score/residual_score
    # must equal the funnel's row-derived totals, not the (here
    # deliberately wrong) Section 1 prose -- proving the wiring rather
    # than a coincidental match. Row-derived: 8.7 / 57.7 / 52.7; the
    # fixture's own Section 1 text claims 26.9 / 60.0 / 52.7 instead.
    funnel_td, _stderr = _funnel_via_cli(
        FIDELITY_FIXTURES_DIR / "controls_warnings_kitchen_sink", template="risk-funnel"
    )
    card_td, _stderr = _funnel_via_cli(
        FIDELITY_FIXTURES_DIR / "controls_warnings_kitchen_sink", template="baseball-card"
    )
    assert card_td["risk_reduction"] == funnel_td["risk_reduction"] == 8.7
    assert card_td["inherent_score"] == funnel_td["inherent_score"] == 57.7
    assert card_td["residual_score"] == funnel_td["residual_score"] == 52.7


def test_k11_reductions_are_never_negative_across_funnel_fixtures():
    # US-3b #8: the row-level clamp (residual <= inherent, enforced once
    # at parse; test_tachi_parsers.py/T020) guarantees V4 <= V3 <= V2 for
    # every row set, so no emitted reduction percentage -- nor
    # risk_reduction -- can ever be negative, regardless of a raw,
    # pre-clamp residual (like kitchen_sink's W-9: residual 9.5 >
    # inherent 8.0) exceeding inherent before the clamp applies.
    for fixture in (
        "funnel_step_bound", "funnel_strong_reduction",
        "funnel_join_inherent_less", "controls_warnings_kitchen_sink",
    ):
        td, _stderr = _funnel_via_cli(FIDELITY_FIXTURES_DIR / fixture)
        for pct in _reduction_pcts(td):
            assert pct is None or pct >= 0.0, f"[{fixture}] negative reduction: {pct}"
        if td["risk_reduction"] is not None:
            assert td["risk_reduction"] >= 0.0, f"[{fixture}] negative risk_reduction"
