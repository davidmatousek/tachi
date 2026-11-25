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

(b) FR-012a's derived-taxa contract (T015, commit 56343db), now on the
    renderer. F-362 made ``scripts/generate-risk-scores-sarif.py`` take its
    OWASP-LLM taxa from ``schemas/taxonomy/owasp.yaml`` at both former
    hardcoded sites (``TAXONOMIES`` and ``supported_taxonomies()``), replacing
    two independently-hardcoded, driftable 2025-era lists. F-374 retired that
    generator (ADR-050 D1, #357). ``scripts/render-risk-scores.py`` writes
    ``risk-scores.sarif`` now, and it takes the file's ``taxonomies`` and the
    driver's ``supportedTaxonomies`` from ``scripts/sarif_common.py``, where
    they are embedded so that the core path needs no PyYAML. ADR-050 D16
    moves the contract with the emitter: "the renderer emits the taxa, so
    FR-012a's taxa contract moves to it". This module renders one
    ``risk-scores.sarif`` through the renderer, in-process, and compares what
    the written file carries at both sites with ground truth loaded a SECOND,
    independent way (a direct ``yaml.safe_load`` of the catalog, never through
    the code under test — an assertion built from the same loader it's
    checking would be self-fulfilling and prove nothing). The embedded values
    can no longer derive from the catalog at run time, so this comparison is
    what fails when a catalog edition bump isn't copied into
    ``sarif_common.py``; ``test_sarif_identity.py`` section 14 pins the same
    values on the emitter's side.

    The third F-362 site, ``derive_owasp_reference`` (the ``owasp-reference``
    property of an OI or MI result), went with the generator. The renderer
    writes no such property: it is not in the 1.1 ``risk-scores.sarif``
    template or in ``contracts/sarif-result.md``, so there is no site left to
    pin, and the test that pinned its edition tokens is retired, not moved.

SAME-COMMIT obligation (KB 3 lockstep): this module's filename is wired into
``.github/workflows/tachi-pytest.yml`` — both the ``paths:`` trigger list and
the ``pytest`` invocation — and the surfaces it reads must sit in the
``&hardening_paths`` anchor, so that each change to them triggers this gate
(architect MEDIUM-1, kept by ADR-050 D16): ``schemas/taxonomy/owasp.yaml``
(the catalog) and, in place of the retired generator, the renderer and what it
loads (``scripts/render-risk-scores.py`` and its helpers, ``tachi-stage.py``
and ``populate-affected-assets.py``) plus the project harness that
``tests/scripts/test_render_risk_scores.py`` provides.

References:
  - specs/362-remap-owasp-llm-top10-2026/spec.md FR-012(a) (PRD FR-11)
  - specs/362-remap-owasp-llm-top10-2026/plan.md D2
  - docs/architecture/02_ADRs/ADR-048-llm-top10-2026-alias-cutover.md D1
  - docs/architecture/02_ADRs/ADR-050-large-architecture-output-authority.md
    D1 (the retirement) and D16 (the migration)
  - .aod/results/senior-backend-engineer-T015.md (the emitter fix this
    module guards)

Hyphenated script filenames (``generate-threats-sarif.py``,
``render-risk-scores.py``, ``tachi-stage.py``) are not importable via
``import``; loaded via ``importlib.util.spec_from_file_location`` — the
established repo pattern (see
``tests/scripts/test_affected_assets_wiring.py::_load_script_module``,
``tests/scripts/test_catalog_drift_guard.py``).
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from .conftest import TAXONOMY_DIR, load_yaml_or_empty

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_script_module(filename: str, modname: str):
    """Load a hyphenated ``scripts/<filename>`` module by file location.

    Mirrors ``tests/scripts/test_affected_assets_wiring.py::_load_script_module``
    exactly. None of the three scripts this module loads executes file I/O or
    ``main()`` at import time (each guards its CLI entry point behind
    ``if __name__ == "__main__":``), so loading is side-effect-free beyond
    binding module-level names.
    """
    path = REPO_ROOT / "scripts" / filename
    spec = importlib.util.spec_from_file_location(modname, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_gen_threats = _load_script_module("generate-threats-sarif.py", "generate_threats_sarif")

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
# (b) FR-012a derived-taxa contract — the renderer's ``taxonomies`` and
#     ``supportedTaxonomies``, as the written ``risk-scores.sarif`` carries them
# -----------------------------------------------------------------------------

def _independent_llm_ground_truth() -> list[dict]:
    """Load ``schemas/taxonomy/owasp.yaml`` via the test suite's own YAML
    helper (``conftest.load_yaml_or_empty``) — NEVER through
    ``render-risk-scores.py``, ``sarif_common.py`` or the retired generator's
    ``_extract`` reuse of ``extract-report-data.py``. An assertion built from
    the module under test would be self-fulfilling; this is the independent
    ground truth T015 section 3 also used.

    Sorted by ``id`` (not relying on the catalog file's own alphabetical
    ordering) so the ordering assertions below are genuinely independent of
    the file order that the catalog happens to have.
    """
    records = load_yaml_or_empty(TAXONOMY_DIR / "owasp.yaml")
    llm_records = [
        r for r in records if isinstance(r, dict) and r.get("id", "").startswith("LLM")
    ]
    return sorted(llm_records, key=lambda r: r["id"])


_GROUND_TRUTH = _independent_llm_ground_truth()
_EXPECTED_TAXA = [{"id": r["id"], "name": r["name"]} for r in _GROUND_TRUTH]
_EXPECTED_URLS = {r["url"] for r in _GROUND_TRUTH}
_EXPECTED_EDITIONS = {str(r["full_id"]).split("-")[2] for r in _GROUND_TRUTH}


def _owasp_llm_entry(taxonomy_list: list[dict]) -> dict:
    """Pick the single ``name == "OWASP-LLM"`` entry out of a taxonomy list.

    Works for both the run's ``taxonomies`` (entries carry ``taxa``) and the
    driver's ``supportedTaxonomies`` (entries carry ``index`` instead) — both
    are lists of dicts keyed by ``name``.
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
    """The single ``informationUri`` that the renderer writes for the OWASP-LLM
    taxonomy relies on all 10 LLM records sharing one ``url``. Pin that
    precondition independently."""
    assert len(_EXPECTED_URLS) == 1, (
        f"ground-truth LLM catalog records disagree on url: {sorted(_EXPECTED_URLS)}"
    )


def test_ground_truth_precondition_uniform_edition():
    """The edition that the renderer writes in both ``version`` fields (the
    ``full_id`` year segment) relies on all 10 LLM records agreeing on one
    edition. Pin that precondition independently."""
    assert len(_EXPECTED_EDITIONS) == 1, (
        f"ground-truth LLM catalog records disagree on full_id edition: "
        f"{sorted(_EXPECTED_EDITIONS)}"
    )


# --- The renderer's file: one real run, read back from disk ---

@pytest.fixture(scope="module")
def rendered_run(tmp_path_factory) -> dict:
    """The one run of ``risk-scores.sarif`` that ``render-risk-scores.py`` writes, as the parsed file's first run.

    One in-process pass of the stage, as ``/tachi.risk-score`` runs it (``tachi-stage.py`` plans, a valid part for
    every batch, ``reconcile``, then the renderer), on the project harness of ``test_render_risk_scores.py`` — a synthetic
    nine-finding project, so nothing here reads a real architecture. The harness module is imported when this fixture
    first runs, so the module's other cases never depend on it. The taxa don't depend on which findings the file holds:
    the renderer writes the same three taxonomies into every file.
    """
    from . import test_render_risk_scores as renderer_harness

    stage = _load_script_module("tachi-stage.py", "tachi_stage_for_owasp_contract")
    renderer = _load_script_module("render-risk-scores.py", "render_risk_scores_for_owasp_contract")
    project = renderer_harness.Project(stage, renderer, tmp_path_factory.mktemp("owasp-contract"))
    result = project.run()
    assert result.code in (0, 5), result.describe()
    return project.sarif["runs"][0]


@pytest.fixture(scope="module")
def taxonomies(rendered_run) -> list[dict]:
    """The run's ``taxonomies``: the entries that carry ``taxa``."""
    return rendered_run["taxonomies"]


@pytest.fixture(scope="module")
def supported_taxonomies(rendered_run) -> list[dict]:
    """The driver's ``supportedTaxonomies``: the entries that carry ``index`` instead of ``taxa``."""
    return rendered_run["tool"]["driver"]["supportedTaxonomies"]


# --- The run's taxonomies ---

def test_taxonomies_owasp_llm_taxa_matches_catalog_exactly(taxonomies):
    entry = _owasp_llm_entry(taxonomies)
    assert entry["taxa"] == _EXPECTED_TAXA


def test_taxonomies_owasp_llm_taxa_ordered_llm01_through_llm10(taxonomies):
    entry = _owasp_llm_entry(taxonomies)
    assert [t["id"] for t in entry["taxa"]] == [f"LLM{n:02d}" for n in range(1, 11)]


def test_taxonomies_owasp_llm_version_is_2026(taxonomies):
    entry = _owasp_llm_entry(taxonomies)
    assert entry["version"] == "2026"


def test_taxonomies_owasp_llm_information_uri_matches_catalog(taxonomies):
    entry = _owasp_llm_entry(taxonomies)
    assert entry["informationUri"] == next(iter(_EXPECTED_URLS))


# --- The driver's supportedTaxonomies ---

def test_supported_taxonomies_owasp_llm_version_is_2026(supported_taxonomies):
    entry = _owasp_llm_entry(supported_taxonomies)
    assert entry["version"] == "2026"


def test_supported_taxonomies_owasp_llm_information_uri_matches_catalog(supported_taxonomies):
    entry = _owasp_llm_entry(supported_taxonomies)
    assert entry["informationUri"] == next(iter(_EXPECTED_URLS))


# --- Edition (no hand-maintained edition literal that could silently lag the catalog) ---
# The "2026" literal pins above are the deliberate edition tripwire (they fail
# loudly at the next edition bump so a human re-verifies the remap); the tests
# below additionally prove the WRITTEN values co-move with the catalog rather
# than being a second hand-maintained literal that could silently lag.

def test_taxonomies_owasp_llm_version_matches_catalog_edition(taxonomies):
    entry = _owasp_llm_entry(taxonomies)
    assert entry["version"] == next(iter(_EXPECTED_EDITIONS))


def test_supported_taxonomies_owasp_llm_version_matches_catalog_edition(supported_taxonomies):
    entry = _owasp_llm_entry(supported_taxonomies)
    assert entry["version"] == next(iter(_EXPECTED_EDITIONS))
