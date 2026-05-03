"""Unit tests for the executive-architecture template in extract-infographic-data.py.

Exercises both subprocess invocation (for end-to-end behavior and exit codes) and
direct module-level calls through the ``extract_infographic_data`` conftest fixture
(for helper-function and payload-shape assertions).
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "extract-infographic-data.py"
FIXTURES_DIR = REPO_ROOT / "tests" / "scripts" / "fixtures" / "exec_arch"
GOLDEN_DIR = REPO_ROOT / "tests" / "scripts" / "fixtures" / "golden"


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
