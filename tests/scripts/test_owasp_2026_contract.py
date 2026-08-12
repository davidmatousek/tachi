"""OWASP LLM Top-10 2026 cutover contract tests (F-362 / T017, US2).

Locks two independently-motivated behaviors introduced by the 2026 remap so a
future edition bump (or an accidental regression) cannot silently break either
one:

(a) ``normalize_owasp_id`` (``scripts/generate-threats-sarif.py:387``)
    covering matrix per plan.md D2 / ADR-048 D1: the function's regex is
    deliberately year-agnostic (the year is a digit capture, not a literal
    ``2025``/``2026``), so a 2025-token input and a 2026-token input
    normalize identically. The trailing ``$`` anchor is equally deliberate:
    any suffix after the year (e.g. a transition breadcrumb) fails the match
    and falls through to raw passthrough — this is *why* ADR-048 D1 confines
    breadcrumbs to narrative prose and bans them from machine-parsed token
    surfaces (``references[]``, the ``threats.md`` References column,
    ``source_attribution``). This module pins that failure mode as a named,
    asserted behavior rather than an implicit consequence someone has to
    rediscover later.

(b) FR-012a's derived-taxa contract (T015, commit 56343db):
    ``scripts/generate-risk-scores-sarif.py``'s ``TAXONOMIES`` structure and
    ``supported_taxonomies()`` both derive their OWASP-LLM taxa from
    ``schemas/taxonomy/owasp.yaml`` via an ``importlib`` reuse of
    ``extract-report-data.py::_load_framework_yaml_records`` — replacing what
    used to be two independently-hardcoded, driftable 2025-era taxa lists.
    This module proves the derivation is faithful by comparing both sites
    against ground truth loaded a SECOND, independent way (a direct
    ``yaml.safe_load`` of the catalog, never through the module under test —
    an assertion built from the same loader it's checking would be
    self-fulfilling and prove nothing).

SAME-COMMIT obligation (KB 3 lockstep): this module's filename is wired into
``.github/workflows/tachi-pytest.yml`` in the same commit — both the
``paths:`` trigger list and the ``pytest`` invocation — plus
``scripts/generate-risk-scores-sarif.py`` and ``schemas/taxonomy/owasp.yaml``
added to the ``&hardening_paths`` anchor (architect MEDIUM-1: the exact file
FR-012a guards, and its derive-source, must trigger their own gate).

References:
  - specs/362-remap-owasp-llm-top10-2026/spec.md FR-012(a) (PRD FR-11)
  - specs/362-remap-owasp-llm-top10-2026/plan.md D2
  - docs/architecture/02_ADRs/ADR-048-llm-top10-2026-alias-cutover.md D1
  - .aod/results/senior-backend-engineer-T015.md (the emitter fix this
    module guards)

Hyphenated generator filenames (``generate-threats-sarif.py``,
``generate-risk-scores-sarif.py``) are not importable via ``import``; loaded
via ``importlib.util.spec_from_file_location`` — the established repo
pattern (see ``tests/scripts/test_affected_assets_wiring.py::_load_script_module``,
``tests/scripts/test_catalog_drift_guard.py``).
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_script_module(filename: str, modname: str):
    """Load a hyphenated ``scripts/<filename>`` module by file location.

    Mirrors ``tests/scripts/test_affected_assets_wiring.py::_load_script_module``
    exactly. Neither generator executes file I/O or ``main()`` at import time
    (both guard their CLI entry point behind ``if __name__ == "__main__":``),
    so loading is side-effect-free beyond binding module-level names — for
    ``generate-risk-scores-sarif.py`` that includes the T015 catalog load,
    itself read-only YAML parsing.
    """
    path = REPO_ROOT / "scripts" / filename
    spec = importlib.util.spec_from_file_location(modname, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_gen_threats = _load_script_module("generate-threats-sarif.py", "generate_threats_sarif")
_gen_risk = _load_script_module("generate-risk-scores-sarif.py", "generate_risk_scores_sarif")

normalize_owasp_id = _gen_threats.normalize_owasp_id


# -----------------------------------------------------------------------------
# (a) normalize_owasp_id covering matrix — plan.md D2 / ADR-048 D1
# -----------------------------------------------------------------------------
# Branch structure, read directly from scripts/generate-threats-sarif.py:387:
#   owasp_ref truthy  -> strip -> try LLM regex -> try ASI regex -> try MCP
#                         regex -> raw passthrough (no branch matched)
#   owasp_ref falsy    -> STRIDE-prefix dict lookup (default "")
# There is no dedicated CWE regex branch; a "CWE-NN"-shaped ref exercises the
# same final passthrough as any other unmatched string (see the "unmatched
# strings" group below, which pins that explicitly).


# --- LLM branch: year-agnostic regex, both editions normalize identically ---

@pytest.mark.parametrize(
    ("owasp_ref", "expected"),
    [
        # 2025-token spread (LLM01, LLM05 middle, LLM10) — historical outputs
        # stay interpretable; the regex has no literal year.
        ("OWASP LLM01:2025", "LLM-01"),
        ("OWASP LLM05:2025", "LLM-05"),
        ("OWASP LLM10:2025", "LLM-10"),
        # 2026-token spread — identical normalization, same regex.
        ("OWASP LLM01:2026", "LLM-01"),
        ("OWASP LLM05:2026", "LLM-05"),
        ("OWASP LLM10:2026", "LLM-10"),
    ],
    ids=[
        "2025-llm01",
        "2025-llm05-middle",
        "2025-llm10",
        "2026-llm01",
        "2026-llm05-middle",
        "2026-llm10",
    ],
)
def test_llm_branch_normalizes_both_editions_identically(owasp_ref, expected):
    assert normalize_owasp_id(owasp_ref, "I") == expected


def test_llm_branch_zero_pads_single_digit_capture():
    """Distinguishes real zero-pad reformatting from naive substring
    passthrough: the capture group matches one-or-more digits (not a fixed
    2-digit width), so a single-digit source still normalizes to the
    zero-padded 2-digit output form."""
    assert normalize_owasp_id("OWASP LLM1:2025", "I") == "LLM-01"


# --- Breadcrumb-suffixed passthrough — the ADR-048 D1 rationale, pinned ---

def test_breadcrumb_suffixed_string_is_passthrough_not_normalized():
    """A transition breadcrumb ("(2025: LLM<NN>)") appended after the year
    fails the trailing-``$``-anchored regex and falls through to raw
    passthrough — this is WHY ADR-048 D1 confines breadcrumbs to narrative
    prose and bans them from machine-parsed token surfaces (``references[]``,
    the ``threats.md`` References column, ``source_attribution``)."""
    breadcrumbed = "OWASP LLM01:2026 (2025: LLM01)"
    assert normalize_owasp_id(breadcrumbed, "I") == breadcrumbed


# --- ASI / MCP branches (per docstring; hyphen-optional, zero-pad reformat) ---

@pytest.mark.parametrize(
    ("owasp_ref", "expected"),
    [
        ("ASI-01", "ASI-01"),
        ("ASI01", "ASI-01"),  # hyphen is optional in the source pattern
        ("ASI-7", "ASI-07"),  # single digit still zero-pads
        ("MCP-03", "MCP-03"),
        ("MCP03", "MCP-03"),  # hyphen is optional in the source pattern
    ],
)
def test_asi_mcp_branches(owasp_ref, expected):
    assert normalize_owasp_id(owasp_ref, "I") == expected


# --- CWE-shaped and unknown/garbage strings: both fall to raw passthrough ---

@pytest.mark.parametrize(
    "owasp_ref",
    [
        "CWE-79",  # no dedicated CWE branch exists — same passthrough as garbage
        "garbage-string-xyz",
    ],
)
def test_unmatched_strings_are_passthrough(owasp_ref):
    assert normalize_owasp_id(owasp_ref, "I") == owasp_ref


# --- STRIDE-derived fallback: empty owasp_ref maps by prefix ---

@pytest.mark.parametrize(
    ("prefix", "expected"),
    [
        ("S", "A07"),
        ("T", "A08"),
        ("R", "A09"),
        ("I", "A01"),
        ("D", "A05"),
        ("E", "A01"),
    ],
)
def test_stride_fallback_maps_prefix_to_owasp_2021_category(prefix, expected):
    assert normalize_owasp_id("", prefix) == expected


def test_stride_fallback_unmapped_prefix_returns_empty_string():
    assert normalize_owasp_id("", "X") == ""


# -----------------------------------------------------------------------------
# (b) FR-012a derived-taxa contract — TAXONOMIES + supported_taxonomies()
# -----------------------------------------------------------------------------

def _independent_llm_ground_truth() -> list[dict]:
    """Load ``schemas/taxonomy/owasp.yaml`` directly via ``yaml.safe_load`` —
    NEVER through ``generate-risk-scores-sarif.py`` or its ``_extract`` reuse
    of ``extract-report-data.py``. An assertion built from the module under
    test would be self-fulfilling; this is the independent ground truth
    T015 section 3 also used.

    Sorted by ``id`` (not relying on the catalog file's own alphabetical
    ordering) so the ordering assertions below are genuinely independent of
    the production loader's FR-032 file-order assumption.
    """
    owasp_path = REPO_ROOT / "schemas" / "taxonomy" / "owasp.yaml"
    with owasp_path.open(encoding="utf-8") as fh:
        records = yaml.safe_load(fh)
    llm_records = [
        r for r in records if isinstance(r, dict) and r.get("id", "").startswith("LLM")
    ]
    return sorted(llm_records, key=lambda r: r["id"])


_GROUND_TRUTH = _independent_llm_ground_truth()
_EXPECTED_TAXA = [{"id": r["id"], "name": r["name"]} for r in _GROUND_TRUTH]
_EXPECTED_URLS = {r["url"] for r in _GROUND_TRUTH}


def _owasp_llm_entry(taxonomy_list: list[dict]) -> dict:
    """Pick the single ``name == "OWASP-LLM"`` entry out of a taxonomy list.

    Works for both ``TAXONOMIES`` (entries carry ``taxa``) and
    ``supported_taxonomies()`` (entries carry ``index`` instead) — both are
    lists of dicts keyed by ``name``.
    """
    matches = [t for t in taxonomy_list if t["name"] == "OWASP-LLM"]
    assert len(matches) == 1, (
        f"expected exactly one OWASP-LLM taxonomy entry, found {len(matches)}"
    )
    return matches[0]


# --- Ground-truth preconditions (guard against a vacuous comparison) ---

def test_ground_truth_precondition_ten_llm_records_llm01_through_llm10():
    """If the catalog ever grows/shrinks/renumbers the LLM set, this fails
    loudly here rather than letting the comparisons below silently degrade
    into a vacuous match."""
    assert [r["id"] for r in _GROUND_TRUTH] == [f"LLM{n:02d}" for n in range(1, 11)]


def test_ground_truth_precondition_uniform_url():
    """T015's single ``informationUri`` derivation relies on all 10 LLM
    records sharing one ``url``. Pin that precondition independently."""
    assert len(_EXPECTED_URLS) == 1, (
        f"ground-truth LLM catalog records disagree on url: {sorted(_EXPECTED_URLS)}"
    )


# --- TAXONOMIES structure ---

def test_taxonomies_owasp_llm_taxa_matches_catalog_exactly():
    entry = _owasp_llm_entry(_gen_risk.TAXONOMIES)
    assert entry["taxa"] == _EXPECTED_TAXA


def test_taxonomies_owasp_llm_taxa_ordered_llm01_through_llm10():
    entry = _owasp_llm_entry(_gen_risk.TAXONOMIES)
    assert [t["id"] for t in entry["taxa"]] == [f"LLM{n:02d}" for n in range(1, 11)]


def test_taxonomies_owasp_llm_version_is_2026():
    entry = _owasp_llm_entry(_gen_risk.TAXONOMIES)
    assert entry["version"] == "2026"


def test_taxonomies_owasp_llm_information_uri_matches_catalog():
    entry = _owasp_llm_entry(_gen_risk.TAXONOMIES)
    assert entry["informationUri"] == next(iter(_EXPECTED_URLS))


# --- supported_taxonomies() ---

def test_supported_taxonomies_owasp_llm_version_is_2026():
    entry = _owasp_llm_entry(_gen_risk.supported_taxonomies())
    assert entry["version"] == "2026"


def test_supported_taxonomies_owasp_llm_information_uri_matches_catalog():
    entry = _owasp_llm_entry(_gen_risk.supported_taxonomies())
    assert entry["informationUri"] == next(iter(_EXPECTED_URLS))
