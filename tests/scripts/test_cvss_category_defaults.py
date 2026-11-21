"""Fix 397 (N13) — every documented CVSS category default equals its vector's score.

`schemas/risk-scoring.yaml` -> `category_defaults` holds the canonical CVSS 3.1 vector for
each threat category, and the scoring reference computes each category's default base score
from it (`cvss-vectors.md`, "Category resolution"). The reference and the Claude Code adapter
copy of the risk scorer also print those scores in tables that the scorer reads directly, so
a hand-typed number that drifts from its vector moves the +/-1.0 bound for every NEW finding
in that category. The agentic row did exactly that: documented as 9.1 and 9.0, computed 9.9.

This module recomputes the scores with a stdlib CVSS 3.1 implementation (FIRST CVSS v3.1
specification, section 7 equations and the Appendix A Roundup), self-tested on reference
examples from FIRST's "CVSS v3.1 Examples" document, and asserts that:
  * each table's vector equals the schema's vector for that category;
  * each printed base score equals the computed score;
  * each bounded range equals [max(0.0, d - 1.0), min(10.0, d + 1.0)];
  * the "Default vector:" lines in the AI-specific guidance equal the schema's vectors.

Stdlib + pytest (+ the suite's PyYAML) only. Gated in `.github/workflows/tachi-pytest.yml`.
"""
from __future__ import annotations

import math
import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas" / "risk-scoring.yaml"
REFERENCE = ROOT / ".claude" / "skills" / "tachi-risk-scoring" / "references" / "cvss-vectors.md"
ADAPTER = ROOT / "adapters" / "claude-code" / "agents" / "risk-scorer.md"

# CVSS 3.1 base metric weights (FIRST CVSS v3.1 specification, section 7.4).
_AV = {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2}
_AC = {"L": 0.77, "H": 0.44}
_PR = {"U": {"N": 0.85, "L": 0.62, "H": 0.27}, "C": {"N": 0.85, "L": 0.68, "H": 0.5}}
_UI = {"N": 0.85, "R": 0.62}
_CIA = {"H": 0.56, "L": 0.22, "N": 0.0}
_VECTOR_RE = re.compile(
    r"^CVSS:3\.1/AV:[NALP]/AC:[LH]/PR:[NLH]/UI:[NR]/S:[UC]/C:[HLN]/I:[HLN]/A:[HLN]$"
)

# Base metrics and v3.1 base scores of examples in FIRST's "CVSS v3.1 Examples" document
# (https://www.first.org/cvss/v3.1/examples), transcribed from each example's metric table.
FIRST_EXAMPLES = [
    ("CVE-2013-0375", "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N", 6.4),
    ("CVE-2014-3566", "CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:N/A:N", 3.1),
    ("CVE-2012-1516", "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H", 9.9),
    ("CVE-2009-0783", "CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L", 4.2),
    ("CVE-2012-0384", "CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H", 7.2),
    ("CVE-2014-0160", "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N", 7.5),
    ("CVE-2014-6271", "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H", 9.8),
    ("CVE-2008-1447", "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:H/A:N", 6.8),
    ("CVE-2014-2005", "CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H", 6.8),
    ("CVE-2013-6014", "CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:H", 9.3),
    ("CVE-2017-5942", "CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N", 6.1),
    ("CVE-2011-1265", "CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H", 8.8),
    ("CVE-2014-2019", "CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N", 4.6),
    ("CVE-2012-5376", "CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H", 9.6),
    ("CVE-2016-5729", "CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H", 8.2),
    ("CVE-2018-3652", "CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H", 7.6),
]


def roundup(value: float) -> float:
    """CVSS 3.1 Roundup: the smallest one-decimal number >= value (specification section 7),
    computed on integers as Appendix A prescribes, so floating-point noise cannot add 0.1."""
    int_input = round(value * 100000)
    if int_input % 10000 == 0:
        return int_input / 100000.0
    return (math.floor(int_input / 10000) + 1) / 10.0


def base_score(vector: str) -> float:
    """CVSS 3.1 base score of a full base vector (specification section 7.1)."""
    assert _VECTOR_RE.match(vector), f"not a full CVSS 3.1 base vector: {vector!r}"
    m = dict(part.split(":") for part in vector.split("/")[1:])
    changed = m["S"] == "C"
    iss = 1 - (1 - _CIA[m["C"]]) * (1 - _CIA[m["I"]]) * (1 - _CIA[m["A"]])
    impact = 7.52 * (iss - 0.029) - 3.25 * (iss - 0.02) ** 15 if changed else 6.42 * iss
    exploitability = 8.22 * _AV[m["AV"]] * _AC[m["AC"]] * _PR[m["S"]][m["PR"]] * _UI[m["UI"]]
    if impact <= 0:
        return 0.0
    if changed:
        return roundup(min(1.08 * (impact + exploitability), 10))
    return roundup(min(impact + exploitability, 10))


def _schema_defaults() -> dict[str, str]:
    data = yaml.safe_load(SCHEMA.read_text(encoding="utf-8"))
    defaults = data["category_defaults"]
    assert len(defaults) == 8, f"expected 8 category defaults, found {sorted(defaults)}"
    return defaults


def _table_rows(text: str, heading: str) -> list[list[str]]:
    """Data rows (cells stripped, backticks removed) of the first table after ``heading``."""
    assert text.count(heading) == 1, f"expected exactly one {heading!r}"
    rows: list[list[str]] = []
    for line in text.split(heading, 1)[1].splitlines():
        if line.startswith("|"):
            cells = [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
            if set("".join(cells)) - set("-: "):  # skip the header separator row
                rows.append(cells)
        elif rows:
            break
    return rows[1:]  # drop the header row


def test_roundup_matches_the_specification_examples() -> None:
    assert roundup(4.02) == 4.1  # section 7: "Roundup (4.02) returns 4.1"
    assert roundup(4.00) == 4.0  # section 7: "and Roundup (4.00) returns 4.0"
    assert roundup(0.1 + 0.2) == 0.3  # Appendix A: 0.30000000000000004 must not become 0.4


@pytest.mark.parametrize(("vector", "expected"), [e[1:] for e in FIRST_EXAMPLES],
                         ids=[e[0] for e in FIRST_EXAMPLES])
def test_calculator_reproduces_first_reference_examples(vector: str, expected: float) -> None:
    assert base_score(vector) == expected


@pytest.mark.parametrize("path", [REFERENCE, ADAPTER], ids=["reference", "adapter"])
def test_vector_reference_table_matches_schema_and_computed_scores(path: Path) -> None:
    defaults = _schema_defaults()
    rows = _table_rows(path.read_text(encoding="utf-8"), "Category Default Vector Reference")
    assert {row[0] for row in rows} == set(defaults), f"{path.name}: table categories differ"
    for category, vector, score, *_ in rows:
        assert vector == defaults[category], f"{path.name}: {category} vector differs from schema"
        assert float(score) == base_score(vector), (
            f"{path.name}: {category} documents {score}, its vector scores {base_score(vector)}"
        )


def test_bounded_range_table_matches_the_computed_defaults() -> None:
    defaults = _schema_defaults()
    rows = _table_rows(REFERENCE.read_text(encoding="utf-8"),
                       "**Category defaults with bounded ranges**")
    assert {row[0] for row in rows} == set(defaults)
    for category, _prefix, default, bounded in rows:
        computed = base_score(defaults[category])
        assert float(default) == computed, f"{category}: documents {default}, computed {computed}"
        low, high = (float(x) for x in re.split(r"\s*[–-]\s*", bounded))
        assert (low, high) == (round(max(0.0, computed - 1.0), 1), round(min(10.0, computed + 1.0), 1)), (
            f"{category}: bounded range {bounded} does not equal default +/-1.0 clamped to [0, 10]"
        )


@pytest.mark.parametrize("path", [REFERENCE, ADAPTER], ids=["reference", "adapter"])
def test_ai_guidance_default_vectors_match_schema(path: Path) -> None:
    defaults = _schema_defaults()
    found = dict(re.findall(r"\(`([a-z-]+)`\)\*\*:\n- Default vector: `([^`]+)`",
                            path.read_text(encoding="utf-8")))
    assert set(found) == {"agentic", "llm"}, f"{path.name}: guidance blocks found: {sorted(found)}"
    for category, vector in found.items():
        assert vector == defaults[category], f"{path.name}: {category} guidance vector differs"
