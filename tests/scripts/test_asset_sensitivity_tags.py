"""Unit tests for the Issue #260 asset-sensitivity tag parser.

Exercises :func:`parse_component_asset_map` and :data:`VALID_ASSET_TAGS` in
``scripts/tachi_parsers.py``. The parser scans a Mermaid architecture
description for ``[asset:tag1,tag2]`` blocks embedded in quoted node labels
and returns a ``component_asset_map`` consumed by the risk-scorer's Section
3.5 modifier pass.

Test coverage targets:

* Empty / no-mermaid / no-tag inputs return an empty dict.
* Quoted rectangle, cylinder, and subroutine bracket shapes all parse.
* Display-name extraction strips the asset block and ``<br/>`` cleanly.
* Tag normalization is case-insensitive and tolerant of whitespace.
* Multi-tag and multi-component inputs round-trip with sorted, deduped lists.
* Unknown tags emit a stderr warning and are dropped.
* Duplicate component declarations merge tag sets with a stderr warning.
* Asset blocks outside `````mermaid`` fences are ignored.
* Raw-Mermaid input (no fence) still parses.

Stdlib-only per PAT-014 — no PyYAML, no Path operations beyond importlib.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from tachi_parsers import (  # noqa: E402  -- import after sys.path mutation
    VALID_ASSET_TAGS,
    parse_component_asset_map,
)


# =============================================================================
# Empty / negative inputs
# =============================================================================


@pytest.mark.parametrize("content", ["", "   ", "\n\n", None])
def test_empty_input_returns_empty_dict(content):
    """Empty, whitespace-only, and None content all collapse to {}."""
    assert parse_component_asset_map(content or "") == {}


def test_no_mermaid_block_returns_empty_dict():
    """Plain prose without any Mermaid syntax produces no map entries."""
    content = (
        "# My Architecture\n\n"
        "This system has a database that stores PII. "
        "We protect it with auth controls.\n"
    )
    assert parse_component_asset_map(content) == {}


def test_mermaid_block_without_asset_tags_returns_empty_dict():
    """Mermaid diagrams with no [asset:] blocks produce no entries."""
    content = (
        "```mermaid\n"
        "flowchart TD\n"
        "    User[User]\n"
        "    DB[(Database)]\n"
        "    User --> DB\n"
        "```\n"
    )
    assert parse_component_asset_map(content) == {}


# =============================================================================
# Bracket-shape coverage
# =============================================================================


def test_quoted_rectangle_node_parses():
    """``id["label<br/>[asset:tag]"]`` — Mermaid rectangle shape."""
    content = (
        "```mermaid\n"
        '    Vault["Secrets Vault<br/>[asset:secrets]"]\n'
        "```\n"
    )
    assert parse_component_asset_map(content) == {"Secrets Vault": ["secrets"]}


def test_quoted_cylinder_node_parses():
    """``id[("label<br/>[asset:tag]")]`` — Mermaid cylinder (data store) shape."""
    content = (
        "```mermaid\n"
        '    DB[("Postgres DB<br/>[asset:pii,auth]")]\n'
        "```\n"
    )
    assert parse_component_asset_map(content) == {"Postgres DB": ["auth", "pii"]}


def test_quoted_subroutine_node_parses():
    """``id[["label<br/>[asset:tag]"]]`` — Mermaid subroutine shape."""
    content = (
        "```mermaid\n"
        '    Svc[["Payment Service<br/>[asset:financial]"]]\n'
        "```\n"
    )
    assert parse_component_asset_map(content) == {"Payment Service": ["financial"]}


# =============================================================================
# Display-name extraction
# =============================================================================


def test_br_tag_stripped_from_display_name():
    """``<br/>`` is removed and surrounding whitespace collapsed."""
    content = (
        "```mermaid\n"
        '    DB["My Database<br/>[asset:pii]"]\n'
        "```\n"
    )
    result = parse_component_asset_map(content)
    assert "My Database" in result


def test_display_name_falls_back_to_node_id_when_label_is_only_asset_block():
    """When the label contains only an asset block, the node id is the key."""
    content = (
        "```mermaid\n"
        '    SecretsVault["[asset:secrets]"]\n'
        "```\n"
    )
    result = parse_component_asset_map(content)
    assert result == {"SecretsVault": ["secrets"]}


def test_multiline_br_tag_variants():
    """``<br>`` and ``<br />`` (with space, no slash) parse identically."""
    content = (
        "```mermaid\n"
        '    DB1["Store One<br>[asset:pii]"]\n'
        '    DB2["Store Two<br />[asset:phi]"]\n'
        '    DB3["Store Three<br/>[asset:auth]"]\n'
        "```\n"
    )
    result = parse_component_asset_map(content)
    assert result == {
        "Store One": ["pii"],
        "Store Two": ["phi"],
        "Store Three": ["auth"],
    }


# =============================================================================
# Tag normalization
# =============================================================================


def test_tags_lowercased():
    """Tag names are case-insensitive on input; canonical storage is lowercase."""
    content = (
        "```mermaid\n"
        '    DB["Database<br/>[asset:PII,Auth]"]\n'
        "```\n"
    )
    assert parse_component_asset_map(content) == {"Database": ["auth", "pii"]}


def test_tags_whitespace_tolerant():
    """Whitespace around commas in the tag list is stripped."""
    content = (
        "```mermaid\n"
        '    DB["Database<br/>[asset: pii , auth ]"]\n'
        "```\n"
    )
    assert parse_component_asset_map(content) == {"Database": ["auth", "pii"]}


def test_tags_deduped_within_node():
    """Repeated tags inside a single asset block are deduplicated."""
    content = (
        "```mermaid\n"
        '    DB["Database<br/>[asset:pii,pii,pii]"]\n'
        "```\n"
    )
    assert parse_component_asset_map(content) == {"Database": ["pii"]}


def test_tag_list_sorted():
    """Returned tag list is sorted alphabetically for deterministic output."""
    content = (
        "```mermaid\n"
        '    DB["Database<br/>[asset:secrets,pii,auth]"]\n'
        "```\n"
    )
    assert parse_component_asset_map(content) == {
        "Database": ["auth", "pii", "secrets"],
    }


def test_all_six_tags_recognized():
    """The full closed enum (pii|phi|auth|secrets|financial|safety) all parse."""
    content = (
        "```mermaid\n"
        '    A["A<br/>[asset:pii]"]\n'
        '    B["B<br/>[asset:phi]"]\n'
        '    C["C<br/>[asset:auth]"]\n'
        '    D["D<br/>[asset:secrets]"]\n'
        '    E["E<br/>[asset:financial]"]\n'
        '    F["F<br/>[asset:safety]"]\n'
        "```\n"
    )
    result = parse_component_asset_map(content)
    assert set(result.keys()) == {"A", "B", "C", "D", "E", "F"}
    assert all(len(tags) == 1 for tags in result.values())
    assert {tag for tags in result.values() for tag in tags} == set(VALID_ASSET_TAGS)


# =============================================================================
# Unknown tag handling
# =============================================================================


def test_unknown_tag_dropped_with_warning(capsys):
    """Tags outside the closed enum are dropped and a stderr warning is emitted."""
    content = (
        "```mermaid\n"
        '    DB["Database<br/>[asset:pii,unknown_tag,auth]"]\n'
        "```\n"
    )
    result = parse_component_asset_map(content)
    captured = capsys.readouterr()

    assert result == {"Database": ["auth", "pii"]}
    assert "unknown asset tag" in captured.err.lower()
    assert "unknown_tag" in captured.err


def test_only_unknown_tags_produces_no_entry(capsys):
    """When every tag is unknown, the component is omitted from the result."""
    content = (
        "```mermaid\n"
        '    DB["Database<br/>[asset:foo,bar,baz]"]\n'
        "```\n"
    )
    result = parse_component_asset_map(content)
    captured = capsys.readouterr()

    assert result == {}
    # Three unknown tags → three warnings.
    assert captured.err.lower().count("unknown asset tag") == 3


# =============================================================================
# Duplicate node declarations
# =============================================================================


def test_duplicate_component_declarations_merge_tags(capsys):
    """Two declarations of the same component union their tag sets with a warning."""
    content = (
        "```mermaid\n"
        '    DB["Database<br/>[asset:pii]"]\n'
        '    DB["Database<br/>[asset:auth]"]\n'
        "```\n"
    )
    result = parse_component_asset_map(content)
    captured = capsys.readouterr()

    assert result == {"Database": ["auth", "pii"]}
    assert "multiple asset declarations" in captured.err.lower()


def test_duplicate_component_same_tag_no_warning(capsys):
    """Re-declaring the same tag on the same component is a silent no-op."""
    content = (
        "```mermaid\n"
        '    DB["Database<br/>[asset:pii]"]\n'
        '    DB["Database<br/>[asset:pii]"]\n'
        "```\n"
    )
    result = parse_component_asset_map(content)
    captured = capsys.readouterr()

    assert result == {"Database": ["pii"]}
    assert "multiple asset declarations" not in captured.err.lower()


# =============================================================================
# Fence-scope discipline
# =============================================================================


def test_asset_block_outside_mermaid_fence_ignored():
    """``[asset:...]`` text in prose paragraphs is not parsed."""
    content = (
        "# Architecture\n\n"
        "Our database carries [asset:pii] tags but this is just prose.\n\n"
        "```mermaid\n"
        '    DB["Real DB<br/>[asset:auth]"]\n'
        "```\n\n"
        "Trailing prose with [asset:financial] also ignored.\n"
    )
    assert parse_component_asset_map(content) == {"Real DB": ["auth"]}


def test_raw_mermaid_without_fence_still_parses():
    """When no fence is present, the entire content is scanned as Mermaid."""
    content = (
        "flowchart TD\n"
        '    DB["Database<br/>[asset:pii]"]\n'
        "    User --> DB\n"
    )
    assert parse_component_asset_map(content) == {"Database": ["pii"]}


def test_multiple_fences_all_scanned():
    """Multiple fenced Mermaid blocks are all scanned."""
    content = (
        "```mermaid\n"
        '    DB1["Store One<br/>[asset:pii]"]\n'
        "```\n\n"
        "Some prose between blocks.\n\n"
        "```mermaid\n"
        '    DB2["Store Two<br/>[asset:auth]"]\n'
        "```\n"
    )
    assert parse_component_asset_map(content) == {
        "Store One": ["pii"],
        "Store Two": ["auth"],
    }


# =============================================================================
# Worked-example smoke test
# =============================================================================


def test_agentic_app_worked_example_parses():
    """The Issue #260 worked example file produces the expected map."""
    example_path = (
        REPO_ROOT
        / "examples"
        / "agentic-app"
        / "architecture-with-asset-tags.md"
    )
    if not example_path.is_file():
        pytest.skip(f"Worked example not present at {example_path}")

    content = example_path.read_text(encoding="utf-8")
    result = parse_component_asset_map(content)

    # Only the four annotated components from the worked example.
    assert set(result.keys()) == {
        "Knowledge Base",
        "Audit Logger",
        "Long-Running Learning Loop",
        "Clinical Advisory Sub-Agent",
    }
    assert result["Knowledge Base"] == ["phi", "pii"]
    assert result["Audit Logger"] == ["auth"]
    assert result["Long-Running Learning Loop"] == ["safety"]
    assert result["Clinical Advisory Sub-Agent"] == ["phi"]


# =============================================================================
# Enum constant
# =============================================================================


def test_valid_asset_tags_is_closed_six_value_enum():
    """The exported enum matches the schema contract (Issue #260 prototype)."""
    assert VALID_ASSET_TAGS == (
        "pii",
        "phi",
        "auth",
        "secrets",
        "financial",
        "safety",
    )
