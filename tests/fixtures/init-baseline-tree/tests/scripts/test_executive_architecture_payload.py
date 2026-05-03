"""Drift-guard tests for the executive-architecture L3 payload schema (FR-212-13..19).

Validates that ``_build_executive_architecture_payload()`` emits the two new
top-level keys ``flow_edges`` and ``clusters`` per the contract in
``specs/212-improve-executive-architecture-infographic/contracts/payload-schema.md``.

These tests are authored in Wave 2 (T021/T022) BEFORE the L3 implementation
lands in Wave 4 (T023-T028); all 12 tests are expected to RED-BAR until the
producer/consumer wiring is delivered. Once green, they serve as the ongoing
drift guard for the additive schema invariant (ADR-028).
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
SKILL_REF_PATH = (
    REPO_ROOT
    / ".claude"
    / "skills"
    / "tachi-infographics"
    / "references"
    / "executive-architecture.md"
)


def run_extract(target_dir, template="executive-architecture", env_overrides=None):
    """Invoke ``extract-infographic-data.py`` and return (rc, stdout, stderr, payload).

    Mirrors the helper in ``test_extract_infographic_data.py`` so style stays consistent.
    Allows env overrides (e.g. ``SOURCE_DATE_EPOCH``) for the determinism test.
    """
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
        env = os.environ.copy()
        if env_overrides:
            env.update(env_overrides)
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
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


# -----------------------------------------------------------------------------
# flow_edges drift-guard tests (FR-212-13, FR-212-14, FR-212-16, FR-212-17)
# -----------------------------------------------------------------------------

def test_flow_edges_absent():
    """No ``### Data Flows`` section -> ``flow_edges`` key present and equal to ``[]``."""
    returncode, _stdout, stderr, payload = run_extract(
        FIXTURES_DIR / "flow-edges-absent"
    )
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert payload is not None, "Expected JSON payload to be written"
    assert "flow_edges" in payload, (
        "FR-212-13: 'flow_edges' MUST be present on every payload "
        "(empty list when source absent, never missing)"
    )
    assert payload["flow_edges"] == [], (
        "FR-212-13: 'flow_edges' MUST be [] when '### Data Flows' is absent"
    )


def test_flow_edges_empty():
    """``### Data Flows`` header but empty body -> ``flow_edges == []``."""
    returncode, _stdout, stderr, payload = run_extract(
        FIXTURES_DIR / "flow-edges-empty"
    )
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert payload is not None
    assert "flow_edges" in payload, (
        "FR-212-13: 'flow_edges' MUST be present even when section body is empty"
    )
    assert payload["flow_edges"] == [], (
        "FR-212-13: 'flow_edges' MUST be [] when section body is empty (header only)"
    )


def test_flow_edges_single():
    """Single data-flow row -> 1 record with source/destination/data/protocol fields."""
    returncode, _stdout, stderr, payload = run_extract(
        FIXTURES_DIR / "flow-edges-single"
    )
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert payload is not None
    assert "flow_edges" in payload
    edges = payload["flow_edges"]
    assert len(edges) == 1, f"Expected exactly 1 flow edge, got {len(edges)}"
    record = edges[0]
    expected_fields = {"source", "destination", "data", "protocol"}
    assert expected_fields.issubset(set(record.keys())), (
        f"FR-212-14: flow_edges record MUST carry fields {expected_fields}; "
        f"got {set(record.keys())}"
    )
    # Verify producer-aligned values for the fixture's lone row
    assert record["source"] == "Web UI"
    assert record["destination"] == "API Gateway"
    assert record["data"] == "Login Request"
    assert record["protocol"] == "HTTPS"


def test_flow_edges_multi_sorted():
    """5 rows with mixed-case names -> sorted by ``(source.casefold(), destination.casefold())``."""
    returncode, _stdout, stderr, payload = run_extract(
        FIXTURES_DIR / "flow-edges-multi"
    )
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert payload is not None
    assert "flow_edges" in payload
    edges = payload["flow_edges"]
    assert len(edges) == 5, f"Expected 5 flow edges, got {len(edges)}"

    # Reconstruct what casefold-sorted order should produce from the fixture
    expected_keys = sorted(
        [(e["source"].casefold(), e["destination"].casefold()) for e in edges]
    )
    actual_keys = [(e["source"].casefold(), e["destination"].casefold()) for e in edges]
    assert actual_keys == expected_keys, (
        "FR-212-16: flow_edges MUST be sorted ascending by "
        "(source.casefold(), destination.casefold()). "
        f"actual={actual_keys} expected={expected_keys}"
    )


def test_flow_edges_truncation():
    """55 rows -> truncated to 50 after deterministic sort and warning emitted (FR-212-17)."""
    returncode, _stdout, stderr, payload = run_extract(
        FIXTURES_DIR / "flow-edges-overflow"
    )
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert payload is not None
    assert "flow_edges" in payload
    edges = payload["flow_edges"]
    assert len(edges) == 50, (
        f"FR-212-17: flow_edges MUST be truncated to first 50 entries; got {len(edges)}"
    )
    # First 50 of svc-001..svc-055 sorted alpha = svc-001..svc-050
    assert edges[0]["source"] == "svc-001"
    assert edges[-1]["source"] == "svc-050"
    # Warning log line MUST be emitted on stderr per FR-212-17
    assert "flow_edges" in stderr.lower() or "truncated" in stderr.lower(), (
        f"FR-212-17: expected truncation warning on stderr; got: {stderr}"
    )


# -----------------------------------------------------------------------------
# clusters drift-guard tests (FR-212-13, FR-212-15, FR-212-16)
# -----------------------------------------------------------------------------

def test_clusters_absent():
    """No ``### Trust Zones`` section -> ``clusters`` key present and equal to ``[]``."""
    returncode, _stdout, stderr, payload = run_extract(
        FIXTURES_DIR / "clusters-absent"
    )
    # The clusters-absent fixture omits Trust Zones but keeps Components/Data Flows,
    # so the extractor uses the DFD-type fallback for layers and still emits a payload.
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert payload is not None
    assert "clusters" in payload, (
        "FR-212-13: 'clusters' MUST be present on every payload "
        "(empty list when source absent, never missing)"
    )
    assert payload["clusters"] == [], (
        "FR-212-13: 'clusters' MUST be [] when '### Trust Zones' is absent"
    )


def test_clusters_multi_sorted():
    """3 trust zones with mixed levels -> sorted by ``(_TRUST_LEVEL_ORDER, name.casefold())``."""
    returncode, _stdout, stderr, payload = run_extract(
        FIXTURES_DIR / "clusters-multi-trust-levels"
    )
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert payload is not None
    assert "clusters" in payload
    clusters = payload["clusters"]
    assert len(clusters) == 3, f"Expected 3 clusters, got {len(clusters)}"

    # Per FR-212-16: trusted=0, semi-trusted=1, untrusted=2; ascending
    # Fixture has: Untrusted Edge / Trusted Core / Semi-Internal
    # Expected order: Trusted Core (0), Semi-Internal (1), Untrusted Edge (2)
    expected_names = ["Trusted Core", "Semi-Internal", "Untrusted Edge"]
    actual_names = [c["name"] for c in clusters]
    assert actual_names == expected_names, (
        "FR-212-16: clusters MUST be sorted by (_TRUST_LEVEL_ORDER[trust_level], "
        f"name.casefold()). expected={expected_names} actual={actual_names}"
    )


def test_clusters_members_sorted():
    """Cluster members sorted ascending case-insensitive within each cluster (FR-212-16)."""
    returncode, _stdout, stderr, payload = run_extract(
        FIXTURES_DIR / "clusters-single"
    )
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert payload is not None
    assert "clusters" in payload
    clusters = payload["clusters"]
    assert len(clusters) >= 1
    cluster = clusters[0]
    assert "members" in cluster, (
        "FR-212-15: clusters[*].members field MUST be present "
        "(populated from producer's 'components')"
    )
    members = cluster["members"]
    # clusters-single fixture seeds 'zeta, Backend, alpha, API Gateway' into one zone
    expected_sorted = sorted(members, key=str.casefold)
    assert members == expected_sorted, (
        "FR-212-16: clusters[*].members MUST be sorted ascending case-insensitively. "
        f"actual={members} expected={expected_sorted}"
    )


def test_clusters_trust_level_rename():
    """Producer key ``trust-level`` -> consumer key ``trust_level``; hyphen form forbidden."""
    returncode, _stdout, stderr, payload = run_extract(
        FIXTURES_DIR / "clusters-multi-trust-levels"
    )
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert payload is not None
    assert "clusters" in payload
    clusters = payload["clusters"]
    assert len(clusters) >= 1
    for cluster in clusters:
        assert "trust_level" in cluster, (
            "FR-212-15: every cluster record MUST carry 'trust_level' "
            "(renamed from producer's 'trust-level')"
        )
        assert cluster["trust_level"], (
            "FR-212-15: cluster.trust_level MUST be populated"
        )
        assert "trust-level" not in cluster, (
            "FR-212-15: producer's 'trust-level' (hyphen) MUST NOT leak into "
            "the consumer payload — renamed to 'trust_level' (underscore)"
        )


# -----------------------------------------------------------------------------
# Field-name lock + determinism + co-landing guards
# -----------------------------------------------------------------------------

def test_destination_field_name_lock():
    """flow_edges[*] uses 'destination' (NOT 'target') — Architect MEDIUM-2 lock."""
    returncode, _stdout, stderr, payload = run_extract(
        FIXTURES_DIR / "flow-edges-single"
    )
    assert returncode == 0, f"Expected exit 0, got {returncode}. stderr: {stderr}"
    assert payload is not None
    assert "flow_edges" in payload
    record = payload["flow_edges"][0]
    assert "destination" in record, (
        "FR-212-14 + Architect MEDIUM-2: flow_edges[*] MUST carry 'destination' "
        "(matches parse_scope_data.data_flows[].destination producer field)"
    )
    assert "target" not in record, (
        "FR-212-14 + Architect MEDIUM-2: 'target' is the FORBIDDEN drift name; "
        "field MUST be 'destination'"
    )


def test_determinism():
    """Two runs on the same fixture under SOURCE_DATE_EPOCH yield byte-identical payloads."""
    env = {"SOURCE_DATE_EPOCH": "1700000000"}
    rc1, _, _, payload1 = run_extract(
        FIXTURES_DIR / "flow-edges-multi", env_overrides=env
    )
    rc2, _, _, payload2 = run_extract(
        FIXTURES_DIR / "flow-edges-multi", env_overrides=env
    )
    assert rc1 == 0 and rc2 == 0
    assert payload1 is not None and payload2 is not None
    # Strip generation_timestamp before comparison: SOURCE_DATE_EPOCH support for
    # this field is L3-orthogonal; FR-212-23 / ADR-017 guarantees determinism on
    # the new arrays (flow_edges, clusters) which we assert below.
    p1 = json.loads(json.dumps(payload1))
    p2 = json.loads(json.dumps(payload2))
    p1["metadata"].pop("generation_timestamp", None)
    p2["metadata"].pop("generation_timestamp", None)
    assert json.dumps(p1, sort_keys=True) == json.dumps(p2, sort_keys=True), (
        "FR-212-23 / ADR-017: payload MUST be byte-identical across runs "
        "(modulo generation_timestamp)"
    )
    # Targeted determinism assertion on the new keys
    assert p1["flow_edges"] == p2["flow_edges"], (
        "FR-212-23: flow_edges MUST be deterministic"
    )
    assert p1["clusters"] == p2["clusters"], (
        "FR-212-23: clusters MUST be deterministic"
    )


def test_prompt_co_landing():
    """Skill prompt references 'flow_edges' and 'clusters' by name (FR-212-18)."""
    assert SKILL_REF_PATH.exists(), (
        f"Expected skill reference at {SKILL_REF_PATH}"
    )
    content = SKILL_REF_PATH.read_text(encoding="utf-8")
    assert "flow_edges" in content, (
        "FR-212-18: executive-architecture.md skill reference MUST contain "
        "the literal substring 'flow_edges' so Gemini reads structured edges "
        "instead of inferring them from component names"
    )
    assert "clusters" in content, (
        "FR-212-18: executive-architecture.md skill reference MUST contain "
        "the literal substring 'clusters' so Gemini renders trust-zone groups "
        "from structured data"
    )
