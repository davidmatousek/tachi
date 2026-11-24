"""Fix 397 (N13) and F-374 (ADR-050 D5, D10) — the shipped scoring module and every constant in it.

`scripts/tachi_scoring.py` is the one place the renderers get their scoring arithmetic: the
CVSS 3.1 calculator (promoted from this module, where Patch A first put it), the embedded
constants, half-up `q1`, `band`, largest remainder, the date and SLA arithmetic and the prefix
resolver. This module imports it and asserts that:

  * the calculator reproduces FIRST's 16 reference examples, `self_test()` runs them and fails
    closed, and the arithmetic holds the D5 goldens (4.55 gives 4.6, `band(4.55)` raises,
    Roundup of 0.1 + 0.2 is 0.3, largest-remainder ties go to the first label);
  * every embedded constant equals its source: `schemas/risk-scoring.yaml` (weights, bands, SLAs,
    dispositions, category vectors, tag forces, ceiling), `schemas/compensating-controls.yaml`
    (the P0 reduction factors and its copy of the bands) and `reachability-analysis.md`
    (baselines, ranges, keyword adjustments, caps), so a hand-typed number that drifts from its
    source fails CI (R-32, KB 26);
  * the documented tables agree with the calculator, as Patch A pinned: each table's vector
    equals the schema's vector, each printed base score equals the computed score, each bounded
    range equals [max(0, d - 1), min(10, d + 1)], and the AI guidance's "Default vector:" lines
    equal the schema's. The agentic row drifted exactly this way: documented 9.1 and 9.0,
    computed 9.9.

The shipped module is stdlib-only and imports no local module. PyYAML is test-only, here and in
the suite's conftest. Gated in `.github/workflows/tachi-pytest.yml`, whose `paths:` must carry
this module's input surfaces: `scripts/tachi_scoring.py`, `schemas/risk-scoring.yaml`,
`schemas/compensating-controls.yaml`, `cvss-vectors.md`, `reachability-analysis.md` and the
adapter copy of the risk scorer.
"""
from __future__ import annotations

import ast
import itertools
import math
import re
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
SHIPPED = ROOT / "scripts" / "tachi_scoring.py"
SCHEMA = ROOT / "schemas" / "risk-scoring.yaml"
CONTROLS_SCHEMA = ROOT / "schemas" / "compensating-controls.yaml"
REFERENCES = ROOT / ".claude" / "skills" / "tachi-risk-scoring" / "references"
REFERENCE = REFERENCES / "cvss-vectors.md"
REACHABILITY = REFERENCES / "reachability-analysis.md"
ADAPTER = ROOT / "adapters" / "claude-code" / "agents" / "risk-scorer.md"

_keep_bytecode_flag = sys.dont_write_bytecode
sys.dont_write_bytecode = True  # a .pyc under scripts/ would dirty the tree under test (ADR-049 D8)
sys.path.insert(0, str(ROOT / "scripts"))
try:
    import tachi_scoring as ts  # noqa: E402  -- after the path change, by design
finally:
    sys.dont_write_bytecode = _keep_bytecode_flag

D = Decimal
ALL_VECTORS = [
    f"CVSS:3.1/AV:{av}/AC:{ac}/PR:{pr}/UI:{ui}/S:{s}/C:{c}/I:{i}/A:{a}"
    for av, ac, pr, ui, s, c, i, a in itertools.product(
        "NALP", "LH", "NLH", "NR", "UC", "HLN", "HLN", "HLN"
    )
]


def _yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _dec(value: object) -> Decimal:
    """A schema number as ``Decimal``. A YAML float goes through its repr, never ``Decimal(float)``."""
    return D(repr(value)) if isinstance(value, float) else D(value)


def _schema_defaults() -> dict[str, str]:
    defaults = _yaml(SCHEMA)["category_defaults"]
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


def _module_tree() -> ast.Module:
    return ast.parse(SHIPPED.read_text(encoding="utf-8"), filename=str(SHIPPED))


def _imported_roots(tree: ast.Module) -> set[str]:
    """The top-level package of every ``import`` and ``from ... import`` anywhere in the tree."""
    roots = {alias.name.split(".")[0]
             for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    roots |= {(node.module or "").split(".")[0]
              for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    return roots


# =============================================================================
# The calculator: CVSS 3.1 section 7, Appendix A Roundup, FIRST's 16 examples
# =============================================================================


def test_roundup_matches_the_specification_examples() -> None:
    assert ts.roundup(4.02) == D("4.1")  # section 7: "Roundup (4.02) returns 4.1"
    assert ts.roundup(4.00) == D("4.0")  # section 7: "and Roundup (4.00) returns 4.0"
    # Appendix A: 0.1 + 0.2 is 0.30000000000000004, and a naive ceiling turns it into 0.4.
    assert math.ceil((0.1 + 0.2) * 10) / 10 == 0.4
    assert ts.roundup(0.1 + 0.2) == D("0.3")


def test_roundup_is_not_half_up_rounding() -> None:
    assert ts.roundup(4.01) == D("4.1")  # Roundup goes up from any excess...
    assert ts.q1(D("4.01")) == D("4.0")  # ...where half-up does not
    assert ts.roundup(4.04) == D("4.1")
    assert ts.roundup(0.0) == D("0.0")
    assert ts.roundup(10) == D("10.0")


def test_calculator_results_carry_exactly_one_decimal() -> None:
    assert str(ts.roundup(4.00)) == "4.0"
    assert str(ts.roundup(0.0)) == "0.0"
    assert str(ts.roundup(10.0)) == "10.0"
    assert str(ts.base_score("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:N")) == "0.0"  # no impact
    for _example, vector, expected in ts.FIRST_EXAMPLES:
        assert str(ts.base_score(vector)) == expected


@pytest.mark.parametrize(("vector", "expected"), [e[1:] for e in ts.FIRST_EXAMPLES],
                         ids=[e[0] for e in ts.FIRST_EXAMPLES])
def test_calculator_reproduces_first_reference_examples(vector: str, expected: str) -> None:
    assert ts.base_score(vector) == D(expected)


def test_first_examples_are_the_sixteen_and_self_test_passes() -> None:
    assert len(ts.FIRST_EXAMPLES) == 16
    assert len({example[0] for example in ts.FIRST_EXAMPLES}) == 16
    assert ts.self_test() is None


def test_self_test_fails_closed_when_the_calculator_drifts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ts, "roundup", lambda value: D("0.0"))
    with pytest.raises(AssertionError, match="self-test failed") as failure:
        ts.self_test()
    assert "CVE-2013-0375" in str(failure.value) and "CVE-2018-3652" in str(failure.value)


def test_maximum_and_minimum_scores() -> None:
    assert ts.base_score("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H") == D("10.0")
    assert ts.base_score("CVSS:3.1/AV:P/AC:H/PR:H/UI:R/S:U/C:L/I:N/A:N") == D("1.6")
    assert ts.base_score("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:N") == D("0.0")


def test_every_base_vector_scores_one_decimal_between_zero_and_ten() -> None:
    assert len(ALL_VECTORS) == 2592
    for vector in ALL_VECTORS:
        score = ts.base_score(vector)
        assert D("0.0") <= score <= D("10.0")
        assert score == ts.q1(score)  # already on the 0.1 grid


@pytest.mark.parametrize("vector", [
    "",
    "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
    "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H\n",  # `$` would let this through
    "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H",
    "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H/E:P",  # temporal metrics are not a base vector
    "CVSS:3.1/AV:X/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
    "cvss:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
    " CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
    None,
    7,
])
def test_calculator_refuses_anything_but_a_full_base_vector(vector: object) -> None:
    with pytest.raises(ValueError, match="not a full CVSS 3.1 base vector"):
        ts.base_score(vector)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="not a full CVSS 3.1 base vector"):
        ts.elevate(vector, [])  # type: ignore[arg-type]


def test_the_shipped_module_has_no_assert_statements() -> None:
    # `python -O` strips `assert`, and the self-test must fail closed under it.
    assert [node.lineno for node in ast.walk(_module_tree()) if isinstance(node, ast.Assert)] == []


def test_the_shipped_module_never_reads_the_clock() -> None:
    tree = _module_tree()
    attributes = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    clock = {"today", "now", "utcnow", "time", "time_ns", "monotonic", "perf_counter",
             "localtime", "gmtime", "ctime", "strftime", "fromtimestamp"}
    assert "time" not in _imported_roots(tree)
    assert attributes & clock == set()


def test_the_shipped_module_imports_only_the_standard_library() -> None:
    # No local module and no PyYAML: the core path must run with `yaml` unimportable (S-11).
    imported = _imported_roots(_module_tree())
    assert imported <= {"__future__", "re", "collections", "datetime", "decimal"}, imported


# =============================================================================
# q1, band and the arithmetic that rounds with q1
# =============================================================================


@pytest.mark.parametrize(("value", "expected"), [
    ("4.55", "4.6"),    # the documented case: Python's round() gives 4.5
    ("4.54", "4.5"),
    ("4.45", "4.5"),    # half-even would give 4.4
    ("4.5", "4.5"),
    ("0.05", "0.1"),
    ("0.049", "0.0"),
    ("2.675", "2.7"),
    ("9.95", "10.0"),
    ("10", "10.0"),
    ("0", "0.0"),
    ("4.875", "4.9"),   # residual-risk.md: 6.5 * (1 - 0.25)
])
def test_q1_rounds_half_up_to_one_decimal(value: str, expected: str) -> None:
    result = ts.q1(D(value))
    assert result == D(expected)
    assert str(result) == expected


def test_q1_accepts_an_int_and_python_round_is_the_bug_it_replaces() -> None:
    assert ts.q1(7) == D("7.0") and str(ts.q1(7)) == "7.0"
    assert round(4.55, 1) == 4.5  # why q1 exists: the float 4.55 is 4.5499999999999998...
    assert ts.q1(D("4.55")) == D("4.6")


@pytest.mark.parametrize("value", [4.55, 4.5, 0.0, True, "4.55", None, [4]])
def test_q1_refuses_anything_but_a_decimal_or_an_int(value: object) -> None:
    with pytest.raises(TypeError, match="never enters stored-value arithmetic|must be a Decimal"):
        ts.q1(value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [D("NaN"), D("sNaN"), D("Infinity"), D("-Infinity")])
def test_q1_refuses_a_value_that_is_not_finite(value: Decimal) -> None:
    with pytest.raises(ValueError, match="not finite"):
        ts.q1(value)


@pytest.mark.parametrize("value", [D("1E+30"), D("1E+400")])
def test_q1_refuses_a_value_too_large_for_one_decimal(value: Decimal) -> None:
    with pytest.raises(ValueError, match="too large"):
        ts.q1(value)


def test_the_private_context_ignores_the_callers_decimal_context() -> None:
    import decimal

    # A caller that has narrowed or re-moded its own context must not move a result.
    with decimal.localcontext(decimal.Context(prec=1, rounding=decimal.ROUND_DOWN)):
        ts.self_test()
        assert str(ts.base_score("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H")) == "10.0"
        assert ts.roundup(4.02) == D("4.1")
        assert ts.q1(D("4.55")) == D("4.6")
        assert ts.band(D("9.0")) == "Critical"
        assert ts.sub_score_mean([D("9.9"), D("9.9"), D("9.9"), D("9.7")]) == D("9.9")  # 9.85
        assert ts.composite(D("8.1"), D("1.9"), D("3.1"), D("3.4")) == D("4.6")
        assert ts.residual_score(D("9.1"), D("0.50")) == D("4.6")
        assert ts.reduction_percentage(D("234.5"), D("178.2")) == D("24.0")
        assert ts.reduction_percentage(D("0.3"), D("0.1")) == D("66.7")
        assert ts.bounds(D("8.2")) == (D("7.2"), D("9.2"))
        assert ts.bounds(D("0.5")) == (D("0.0"), D("1.5"))


@pytest.mark.parametrize(("score", "expected"), [
    ("10.0", "Critical"), ("9.1", "Critical"), ("9.0", "Critical"),
    ("8.9", "High"), ("7.0", "High"),
    ("6.9", "Medium"), ("4.0", "Medium"),
    ("3.9", "Low"), ("0.1", "Low"), ("0.0", "Low"),
    ("4.50", "Medium"),  # a one-decimal value written with a trailing zero is on the grid
])
def test_band_minimums_are_inclusive(score: str, expected: str) -> None:
    assert ts.band(D(score)) == expected


def test_band_accepts_an_int() -> None:
    assert [ts.band(n) for n in (0, 3, 4, 6, 7, 8, 9, 10)] == [
        "Low", "Low", "Medium", "Medium", "High", "High", "Critical", "Critical"]


@pytest.mark.parametrize("score", [
    "4.55", "3.95", "6.95", "8.95", "6.999", "0.05", "9.01", "4.0000001"])
def test_band_refuses_an_unquantized_value(score: str) -> None:
    with pytest.raises(ValueError, match="not quantized to 0.1"):
        ts.band(D(score))


@pytest.mark.parametrize("score", [4.55, 4.5, 7.0, 9.0, 0.0])
def test_band_refuses_a_float_even_when_it_is_exactly_representable(score: float) -> None:
    with pytest.raises(TypeError):
        ts.band(score)  # type: ignore[arg-type]


@pytest.mark.parametrize("score", ["-0.1", "10.1", "11", "1E+500"])
def test_band_refuses_a_score_outside_zero_to_ten(score: str) -> None:
    with pytest.raises(ValueError, match="outside 0.0 to 10.0"):
        ts.band(D(score))


def test_a_value_is_rounded_with_q1_first_and_then_banded() -> None:
    # 3.95 is Low if it is cut to 3.9 and Medium once it rounds half-up to 4.0.
    assert ts.band(ts.q1(D("3.95"))) == "Medium"
    assert ts.band(ts.q1(D("3.94"))) == "Low"
    assert ts.band(ts.q1(D("6.95"))) == "High"
    assert ts.band(ts.q1(D("8.95"))) == "Critical"
    assert ts.band(ts.q1(D("8.94"))) == "High"


def test_band_order_and_governance_follow_severity_bands_md() -> None:
    assert list(ts.SEVERITY_BANDS) == ["Critical", "High", "Medium", "Low"]
    minimums = [rule["min"] for rule in ts.SEVERITY_BANDS.values()]
    assert minimums == sorted(minimums, reverse=True) and minimums[-1] == D("0.0")
    # severity-bands.md: SLA duration parsing, review date = scoring date + N days.
    days = {"Critical": 1, "High": 7, "Medium": 30, "Low": 90}
    for name, rule in ts.SEVERITY_BANDS.items():
        assert ts.sla_days(rule["sla"]) == days[name]
        assert ts.review_date("2026-03-27", rule["sla"]) == (
            date(2026, 3, 27) + timedelta(days=days[name])).isoformat()
    assert [r["disposition"] for r in ts.SEVERITY_BANDS.values()] == [
        "Mitigate", "Mitigate", "Review", "Review"]


# scoring-dimensions.md: the "Typical Score" of each guidance row is the mean of four
# sub-scores to one decimal, and every one of these rounds half-up (8.75 is 8.8).
DOC_MEANS = [
    ((9, 9, 8, 9), "8.8"), ((7, 6, 5, 6), "6.0"), ((6, 5, 4, 5), "5.0"), ((5, 6, 3, 6), "5.0"),
    ((6, 7, 5, 7), "6.3"), ((4, 3, 2, 3), "3.0"),
    ((8, 6, 8, 5), "6.8"), ((5, 4, 7, 4), "5.0"), ((3, 3, 8, 7), "5.3"), ((7, 6, 8, 4), "6.3"),
    ((9, 8, 5, 3), "6.3"), ((6, 5, 8, 5), "6.0"), ((4, 5, 8, 6), "5.8"), ((7, 7, 9, 6), "7.3"),
]


@pytest.mark.parametrize(("values", "expected"), DOC_MEANS)
def test_sub_score_mean_reproduces_the_documented_typical_scores(values: tuple, expected: str) -> None:
    assert ts.sub_score_mean([D(v) for v in values]) == D(expected)
    assert ts.sub_score_mean(list(values)) == D(expected)  # ints are accepted too


def test_sub_score_mean_rounds_half_up_on_decimal_sub_scores() -> None:
    assert ts.sub_score_mean([D("0.1"), D("0.2"), D("0"), D("0")]) == D("0.1")  # 0.075
    assert ts.sub_score_mean([D("10"), D("10"), D("10"), D("10")]) == D("10.0")
    assert str(ts.sub_score_mean([0, 0, 0, 0])) == "0.0"


@pytest.mark.parametrize("values", [[], [1, 2, 3], [1, 2, 3, 4, 5], "1234"])
def test_sub_score_mean_takes_exactly_four_values(values: object) -> None:
    with pytest.raises((ValueError, TypeError)):
        ts.sub_score_mean(values)  # type: ignore[arg-type]


def test_sub_score_mean_refuses_a_float_and_an_out_of_range_value() -> None:
    with pytest.raises(TypeError):
        ts.sub_score_mean([1.5, 2, 3, 4])  # type: ignore[list-item]
    for bad in ("-0.1", "10.1"):
        with pytest.raises(ValueError, match="outside 0.0 to 10.0"):
            ts.sub_score_mean([D(bad), D(1), D(1), D(1)])


# Composites found by search over the one-decimal grid. In each, the exact weighted sum ends in
# 5 at the hundredths, so the result depends on rounding half-up in Decimal. Float arithmetic
# with round(sum, 1) gives the lower value for four of them, and for the first and the last that
# moves the band.
TIE_COMPOSITES = [
    (("8.2", "2.9", "1", "0.3"), "3.95", "4.0", "Medium"),    # float gives 3.9: Low
    (("8.1", "1.9", "3.1", "3.4"), "4.55", "4.6", "Medium"),  # float gives 4.5
    (("9.5", "6.7", "3.3", "4.6"), "6.75", "6.8", "Medium"),  # float gives 6.7
    (("4.5", "8.8", "7.7", "7.9"), "6.95", "7.0", "High"),
    (("10", "7.3", "8.4", "10"), "8.95", "9.0", "Critical"),  # float gives 8.9: High
]
# Composites that are exactly 4.0, 7.0 and 9.0, the band boundaries.
BOUNDARY_COMPOSITES = [
    (("6.5", "1.6", "1.9", "4.8"), "4.0", "Medium"),
    (("4.4", "10", "8", "6.3"), "7.0", "High"),
    (("9.8", "9.5", "8.8", "7"), "9.0", "Critical"),
]


@pytest.mark.parametrize(("inputs", "exact", "expected", "expected_band"), TIE_COMPOSITES)
def test_composite_rounds_exact_ties_half_up(inputs: tuple, exact: str, expected: str,
                                              expected_band: str) -> None:
    c, e, s, r = (D(v) for v in inputs)
    total = D("0.35") * c + D("0.30") * e + D("0.15") * s + D("0.20") * r
    assert total == D(exact)  # the sum is exact in Decimal, ending in 5 at the hundredths
    assert ts.composite(c, e, s, r) == D(expected)
    assert ts.band(ts.composite(c, e, s, r)) == expected_band


@pytest.mark.parametrize(("inputs", "expected", "expected_band"), BOUNDARY_COMPOSITES)
def test_composite_lands_exactly_on_the_band_boundaries(inputs: tuple, expected: str,
                                                        expected_band: str) -> None:
    result = ts.composite(*(D(v) for v in inputs))
    assert result == D(expected) and str(result) == expected
    assert ts.band(result) == expected_band


def test_composite_of_equal_inputs_is_that_input_for_every_score_on_the_grid() -> None:
    # The weights sum to 1.00, so a drifted weight breaks this for most values.
    assert sum(ts.WEIGHTS.values()) == D("1.00")
    for tenths in range(101):
        x = D(tenths) / 10
        assert ts.composite(x, x, x, x) == ts.q1(x)


def test_composite_uses_the_documented_weights() -> None:
    assert ts.composite(D("10"), D("0"), D("0"), D("0")) == D("3.5")
    assert ts.composite(D("0"), D("10"), D("0"), D("0")) == D("3.0")
    assert ts.composite(D("0"), D("0"), D("10"), D("0")) == D("1.5")
    assert ts.composite(D("0"), D("0"), D("0"), D("10")) == D("2.0")
    assert str(ts.composite(0, 0, 0, 0)) == "0.0"


def test_composite_refuses_an_unquantized_float_or_out_of_range_input() -> None:
    with pytest.raises(ValueError, match="not quantized to 0.1"):
        ts.composite(D("7.05"), D("6"), D("5"), D("4"))
    with pytest.raises(TypeError):
        ts.composite(D("7.0"), 6.5, D("5"), D("4"))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="outside 0.0 to 10.0"):
        ts.composite(D("7.0"), D("6"), D("5"), D("10.1"))


@pytest.mark.parametrize(("inherent", "factor", "expected"), [
    # residual-risk.md, "Worked examples"
    ("7.8", "0.50", "3.9"), ("6.5", "0.25", "4.9"), ("8.2", "0.00", "8.2"),
    ("9.1", "0.50", "4.6"),  # 4.55: Python's round() gives 4.5
])
def test_residual_score_reproduces_the_documented_worked_examples(inherent: str, factor: str,
                                                                  expected: str) -> None:
    assert ts.residual_score(D(inherent), D(factor)) == D(expected)


def test_residual_score_with_every_p0_factor_stays_on_the_grid() -> None:
    for name, factor in ts.REDUCTION_FACTOR_P0.items():
        for tenths in range(101):
            inherent = D(tenths) / 10
            result = ts.residual_score(inherent, factor)
            assert D("0.0") <= result <= inherent, name
            assert result == ts.q1(result)


def test_residual_score_refuses_bad_inputs() -> None:
    for factor in ("-0.01", "1.01"):
        with pytest.raises(ValueError, match="outside 0 to 1"):
            ts.residual_score(D("5.0"), D(factor))
    with pytest.raises(ValueError, match="not quantized to 0.1"):
        ts.residual_score(D("4.55"), D("0.5"))
    with pytest.raises(TypeError):
        ts.residual_score(D("5.0"), 0.5)  # type: ignore[arg-type]


def test_reduction_percentage_reproduces_the_documented_summary() -> None:
    # residual-risk.md: inherent 234.5, residual 178.2, delta 56.3, 24.0 percent.
    assert ts.reduction_percentage(D("234.5"), D("178.2")) == D("24.0")
    assert ts.reduction_percentage(D("100"), D("0")) == D("100.0")
    assert ts.reduction_percentage(D("100"), D("100")) == D("0.0")
    assert str(ts.reduction_percentage(D("10"), D("10.0"))) == "0.0"  # never "-0.0"
    assert ts.reduction_percentage(D("0.3"), D("0.1")) == D("66.7")
    assert ts.reduction_percentage(D("2000"), D("1519")) == D("24.1")  # exactly 24.05, half-up
    assert str(ts.reduction_percentage(0, 0)) == "0.0"  # no inherent risk, no reduction


def test_reduction_percentage_refuses_bad_inputs() -> None:
    with pytest.raises(ValueError, match="negative"):
        ts.reduction_percentage(D("-1"), D("0"))
    with pytest.raises(ValueError, match="negative"):
        ts.reduction_percentage(D("10"), D("-1"))
    with pytest.raises(TypeError):
        ts.reduction_percentage(234.5, D("178.2"))  # type: ignore[arg-type]


# =============================================================================
# Largest remainder: ADR-017 D2's rule, on integers
# =============================================================================


def test_largest_remainder_breaks_ties_by_label_ascending() -> None:
    assert ts.largest_remainder({"a": 1, "b": 1, "c": 1}) == {"a": 34, "b": 33, "c": 33}
    reordered = ts.largest_remainder({"c": 1, "b": 1, "a": 1})
    assert reordered == {"a": 34, "b": 33, "c": 33}
    assert list(reordered) == ["c", "b", "a"]  # the input's key order is kept
    seven = ts.largest_remainder({label: 1 for label in "gfedcba"})  # 100 = 7 * 14 + 2
    assert seven == {"a": 15, "b": 15, "c": 14, "d": 14, "e": 14, "f": 14, "g": 14}


def test_largest_remainder_hands_the_shortfall_to_the_largest_remainders() -> None:
    assert ts.largest_remainder({"x": 1, "y": 2}) == {"x": 33, "y": 67}
    assert ts.largest_remainder({"a": 1, "b": 3, "c": 5}) == {"a": 11, "b": 33, "c": 56}
    # a and b hold remainder 4, c and d remainder 2; the shortfall is 2, so a and b win
    assert ts.largest_remainder({"b": 1, "a": 1, "c": 2, "d": 2}) == {
        "a": 17, "b": 17, "c": 33, "d": 33}


def test_largest_remainder_edges() -> None:
    assert ts.largest_remainder({"only": 7}) == {"only": 100}
    assert ts.largest_remainder({"a": 0, "b": 0}) == {"a": 0, "b": 0}  # a zero total gives all zero
    assert ts.largest_remainder({}) == {}
    assert ts.largest_remainder({"a": 0, "b": 5, "c": 0}) == {"a": 0, "b": 100, "c": 0}
    assert ts.largest_remainder({"Critical": 1, "High": 0, "Medium": 0, "Low": 2}) == {
        "Critical": 33, "High": 0, "Medium": 0, "Low": 67}


def test_largest_remainder_always_sums_to_one_hundred_and_stays_within_one_point() -> None:
    # Every distribution of 0 to 6 over one to five labels, plus a few larger counts.
    cases = [dict(zip("abcde", counts)) for size in range(1, 6)
             for counts in itertools.product(range(7), repeat=size)]
    cases += [{"a": 17, "b": 33, "c": 1000}, {"a": 1, "b": 99999, "c": 1}, {"x": 3, "y": 3, "z": 1}]
    for counts in cases:
        shares = ts.largest_remainder(counts)
        total = sum(counts.values())
        if total == 0:
            assert set(shares.values()) == {0}
            continue
        assert sum(shares.values()) == 100, counts
        for label, count in counts.items():
            assert 100 * count // total <= shares[label] <= 100 * count // total + 1, counts
        flipped = dict(reversed(list(counts.items())))
        assert ts.largest_remainder(flipped) == shares  # the order of the input never matters


def test_largest_remainder_refuses_anything_but_non_negative_ints() -> None:
    for bad in (1.5, 2.0, True, "3", None, D("2")):
        with pytest.raises(TypeError, match="must be an int"):
            ts.largest_remainder({"a": 1, "b": bad})  # type: ignore[dict-item]
    with pytest.raises(ValueError, match="negative"):
        ts.largest_remainder({"a": 1, "b": -1})


# =============================================================================
# The prefix resolver (D10): a category for every prefix
# =============================================================================

EXPECTED_PREFIX_CATEGORY = {
    "S": "spoofing", "T": "tampering", "R": "repudiation", "I": "info-disclosure",
    "D": "denial-of-service", "E": "privilege-escalation",
    "AG": "agentic", "AGP": "agentic", "TE": "agentic",
    "LLM": "llm", "OI": "llm", "MI": "llm",
}


def test_the_prefix_resolver_covers_all_twelve_prefixes() -> None:
    assert len(EXPECTED_PREFIX_CATEGORY) == 12
    assert dict(ts.PREFIX_CATEGORY) == EXPECTED_PREFIX_CATEGORY
    for prefix, category in EXPECTED_PREFIX_CATEGORY.items():
        assert ts.category_for_prefix(prefix) == category
        assert category in ts.CATEGORY_DEFAULT_VECTORS  # every prefix reaches a default vector
        assert ts.default_score(category) == ts.base_score(ts.CATEGORY_DEFAULT_VECTORS[category])


@pytest.mark.parametrize("prefix", [
    "", "X", "s", "Llm", "LLM-", "S-1", "S ", "AGPX", "AG\n", "TE\n", None])
def test_the_prefix_resolver_refuses_an_unknown_prefix(prefix: object) -> None:
    with pytest.raises(ValueError, match="unknown finding-ID prefix"):
        ts.category_for_prefix(prefix)  # type: ignore[arg-type]


def test_a_prefix_not_folded_into_llm_or_ag_scores_like_the_prefix_it_would_fold_into() -> None:
    # #356: Phase 3 may fold OI, MI and TE findings into the LLM-N and AG-N sequences, and a
    # finding must score the same either way, so the category and its default agree.
    for folded, home in (("OI", "LLM"), ("MI", "LLM"), ("TE", "AG"), ("AGP", "AG")):
        assert ts.category_for_prefix(folded) == ts.category_for_prefix(home)
        assert ts.bounds(ts.default_score(ts.category_for_prefix(folded))) == ts.bounds(
            ts.default_score(ts.category_for_prefix(home)))


# =============================================================================
# Dates and SLAs
# =============================================================================


@pytest.mark.parametrize(("sla", "days"), [
    ("24h", 1), ("1h", 1), ("23h", 1), ("25h", 2), ("48h", 2), ("49h", 3), ("0h", 0), ("12h", 1),
    ("7d", 7), ("30d", 30), ("90d", 90), ("0d", 0), ("007d", 7), ("999999d", 999999),
])
def test_sla_days(sla: str, days: int) -> None:
    assert ts.sla_days(sla) == days


@pytest.mark.parametrize("sla", [
    "", "7", "d", "h", "7 d", " 7d", "7d ", "7D", "24H", "1w", "1m", "-1d", "+1d", "1.5d", "1e1d",
    "7dd", "7d\n", "0x10d", "1234567d", "\u0667d", "\uff17d", None, 7,
])
def test_sla_days_refuses_anything_but_n_hours_or_n_days(sla: object) -> None:
    with pytest.raises(ValueError, match="unparseable SLA"):
        ts.sla_days(sla)  # type: ignore[arg-type]


@pytest.mark.parametrize(("start", "sla", "expected"), [
    ("2026-03-27", "7d", "2026-04-03"),    # severity-bands.md: scorer runs 2026-03-27, High
    ("2026-01-29", "30d", "2026-02-28"),   # severity-bands.md: month boundary
    ("2026-12-31", "24h", "2027-01-01"),   # year boundary
    ("2028-02-28", "1d", "2028-02-29"),    # leap day
    ("2026-02-28", "1d", "2026-03-01"),
    ("2026-01-01", "0d", "2026-01-01"),
    ("2026-01-01", "25h", "2026-01-03"),
    ("0999-12-31", "1d", "1000-01-01"),    # four-digit years stay zero-padded
])
def test_review_date_is_calendar_arithmetic(start: str, sla: str, expected: str) -> None:
    assert ts.review_date(start, sla) == expected


@pytest.mark.parametrize("text", [
    "", "2026-1-1", "26-01-01", "2026/01/01", "20260101", "2026-01-01T00:00:00", "2026-01-01 ",
    " 2026-01-01", "2026-01-01\n", "2026-02-30", "2026-13-01", "2026-00-10", "2026-01-00",
    "0000-01-01", "\uff12\uff10\uff12\uff16-01-01", "\u0662\u0660\u0662\u0666-\u0660\u0661-\u0660\u0661",
    None, 20260101,
])
def test_parse_date_refuses_anything_but_a_strict_calendar_date(text: object) -> None:
    with pytest.raises(ValueError, match="not a"):
        ts.parse_date(text)  # type: ignore[arg-type]


def test_parse_date_returns_a_date_and_review_date_refuses_what_it_cannot_add() -> None:
    assert ts.parse_date("2026-11-22") == date(2026, 11, 22)
    with pytest.raises(ValueError, match="past 9999-12-31"):
        ts.review_date("9999-12-31", "1d")
    with pytest.raises(ValueError, match="past 9999-12-31"):
        ts.review_date("9999-01-01", "999999d")
    with pytest.raises(ValueError, match="unparseable SLA"):
        ts.review_date("2026-01-01", "7")
    with pytest.raises(ValueError, match="not a YYYY-MM-DD date"):
        ts.review_date("2026-1-1", "7d")


# =============================================================================
# elevate(), the category defaults and their bounds
# =============================================================================


def _default(category: str) -> str:
    return ts.CATEGORY_DEFAULT_VECTORS[category]


@pytest.mark.parametrize(("category", "tags", "bits"), [
    # asset-modifiers.md, "Floor-Only Semantics": the five rows of the table
    ("info-disclosure", ["pii"], "C:H/I:N/A:N"),
    ("tampering", ["financial"], "C:N/I:H/A:L"),
    ("info-disclosure", ["secrets"], "C:H/I:H/A:N"),
    ("denial-of-service", ["safety"], "C:N/I:N/A:H"),
    ("tampering", ["pii", "auth"], "C:H/I:H/A:L"),
])
def test_elevate_follows_the_floor_only_table(category: str, tags: list[str], bits: str) -> None:
    result = ts.elevate(_default(category), tags)
    assert result.endswith("/" + bits)
    assert result.split("/")[:5] == _default(category).split("/")[:5]  # the exploit metrics hold


def test_elevate_reproduces_the_worked_example() -> None:
    # asset-modifiers.md: T-2, tampering on a PII store: 7.1 becomes 8.3, under the 9.2 ceiling.
    elevated = ts.elevate(_default("tampering"), ["pii"])
    assert elevated == "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L"
    assert ts.base_score(elevated) == D("8.3")
    assert ts.elevate(_default("info-disclosure"), ["pii"]) == _default("info-disclosure")  # no-op


def test_the_modifier_ceiling_clamps_an_elevation_that_would_pass_it() -> None:
    elevated = ts.elevate(_default("spoofing"), ["auth", "safety"])
    assert ts.base_score(elevated) == D("9.8")
    assert min(ts.base_score(elevated), ts.MODIFIER_CEILING) == D("9.2")
    assert ts.MODIFIER_CEILING == D("9.2")


def test_elevate_with_no_tags_returns_the_same_vector() -> None:
    for vector in ALL_VECTORS[::97]:
        assert ts.elevate(vector, []) == vector
        assert ts.elevate(vector, ()) == vector


def test_elevate_never_lowers_a_bit_or_a_score_and_is_idempotent_for_every_vector() -> None:
    level = {"N": 0, "L": 1, "H": 2}
    tag_sets = [[tag] for tag in ts.TAG_FORCES] + [list(ts.TAG_FORCES)]
    for vector in ALL_VECTORS:
        for tags in tag_sets:
            elevated = ts.elevate(vector, tags)
            assert re.fullmatch(
                r"CVSS:3\.1/AV:[NALP]/AC:[LH]/PR:[NLH]/UI:[NR]/S:[UC]/C:[HLN]/I:[HLN]/A:[HLN]", elevated)
            before = dict(part.split(":") for part in vector.split("/")[1:])
            after = dict(part.split(":") for part in elevated.split("/")[1:])
            assert all(level[after[k]] >= level[before[k]] for k in ("C", "I", "A"))  # floor only
            assert all(after[k] == before[k] for k in ("AV", "AC", "PR", "UI", "S"))  # no other move
            assert ts.base_score(elevated) >= ts.base_score(vector)
            assert ts.elevate(elevated, tags) == elevated


def test_elevate_is_the_union_of_its_tags_in_any_order() -> None:
    vectors = ALL_VECTORS[::37]
    names = list(ts.TAG_FORCES)
    for vector in vectors:
        union = ts.elevate(vector, names)
        for size in (2, 3):
            for combo in itertools.combinations(names, size):
                forward = ts.elevate(vector, combo)
                assert ts.elevate(vector, reversed(combo)) == forward
                step = vector
                for tag in combo:
                    step = ts.elevate(step, [tag])
                assert step == forward
                assert ts.elevate(forward, names) == union


@pytest.mark.parametrize("tags", [["PII"], ["unknown"], ["pii", "nope"], "pii", [""], [None]])
def test_elevate_refuses_a_tag_outside_the_closed_six(tags: object) -> None:
    with pytest.raises(ValueError, match="unknown asset tag"):
        ts.elevate(_default("tampering"), tags)  # type: ignore[arg-type]


def test_default_scores_match_cvss_vectors_md() -> None:
    assert {c: str(ts.default_score(c)) for c in ts.CATEGORY_DEFAULT_VECTORS} == {
        "spoofing": "8.2", "tampering": "7.1", "repudiation": "4.3", "info-disclosure": "6.5",
        "denial-of-service": "7.5", "privilege-escalation": "9.9", "agentic": "9.9", "llm": "9.3"}
    with pytest.raises(ValueError, match="unknown category"):
        ts.default_score("Spoofing")


def test_bounds_clamp_at_zero_and_ten() -> None:
    # cvss-vectors.md, "Edge cases at extremes"
    assert ts.bounds(D("9.5")) == (D("8.5"), D("10.0"))
    assert ts.bounds(D("1.0")) == (D("0.0"), D("2.0"))
    assert ts.bounds(D("0.5")) == (D("0.0"), D("1.5"))
    assert ts.bounds(D("9.9")) == (D("8.9"), D("10.0"))
    assert ts.bounds(D("8.2")) == (D("7.2"), D("9.2"))
    assert ts.bounds(D("0.0")) == (D("0.0"), D("1.0"))
    assert ts.bounds(D("10.0")) == (D("9.0"), D("10.0"))
    low, high = ts.bounds(D("9"))
    assert (str(low), str(high)) == ("8.0", "10.0")  # an int-like default still gives one decimal


def test_bounds_refuse_an_unquantized_float_or_out_of_range_default() -> None:
    with pytest.raises(ValueError, match="not quantized to 0.1"):
        ts.bounds(D("8.25"))
    with pytest.raises(TypeError):
        ts.bounds(8.2)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="outside 0.0 to 10.0"):
        ts.bounds(D("10.5"))


# =============================================================================
# Embedded constants against their sources: schemas/risk-scoring.yaml
# =============================================================================


def test_embedded_weights_match_the_schema() -> None:
    weights = _yaml(SCHEMA)["weights"]
    assert set(ts.WEIGHTS) == set(weights)
    for name, value in weights.items():
        assert ts.WEIGHTS[name] == _dec(value), name
    assert sum(ts.WEIGHTS.values()) == D("1.00")


def test_embedded_bands_slas_and_dispositions_match_both_schemas() -> None:
    risk = _yaml(SCHEMA)["severity_bands"]
    controls = _yaml(CONTROLS_SCHEMA)["severity_bands"]
    assert list(ts.SEVERITY_BANDS) == list(risk) == list(controls)
    names = list(ts.SEVERITY_BANDS)
    for index, (name, rule) in enumerate(ts.SEVERITY_BANDS.items()):
        for schema in (risk, controls):
            assert _dec(schema[name]["min"]) == rule["min"], name
        assert risk[name]["sla"] == rule["sla"], name
        assert risk[name]["disposition"] == rule["disposition"], name
        # a schema's max is not stored: it is the next band's minimum less 0.1, and the top is 10.0
        above = ts.SEVERITY_BANDS[names[index - 1]]["min"] if index else D("10.1")
        expected_max = above - D("0.1")
        for schema in (risk, controls):
            assert _dec(schema[name]["max"]) == expected_max, name


def test_embedded_category_vectors_match_the_schema() -> None:
    assert dict(ts.CATEGORY_DEFAULT_VECTORS) == _schema_defaults()


def test_embedded_asset_modifiers_match_the_schema() -> None:
    modifiers = _yaml(SCHEMA)["asset_modifiers"]
    assert ts.MODIFIER_CEILING == _dec(modifiers["modifier_ceiling"])
    forces = {tag: tuple(rule["forces"]) for tag, rule in modifiers["tags"].items()}
    assert forces == dict(ts.TAG_FORCES)
    assert len(ts.TAG_FORCES) == 6  # the enum is frozen at six (ADR-026, F-260)


# =============================================================================
# ... and schemas/compensating-controls.yaml
# =============================================================================


def test_embedded_p0_reduction_factors_match_the_controls_schema() -> None:
    factors = _yaml(CONTROLS_SCHEMA)["reduction_factor_p0"]
    assert set(ts.REDUCTION_FACTOR_P0) == set(factors)
    for status, value in factors.items():
        assert ts.REDUCTION_FACTOR_P0[status] == _dec(value), status


def test_the_category_vocabulary_agrees_across_both_schemas_and_the_resolver() -> None:
    controls = _yaml(CONTROLS_SCHEMA)
    categories = set(ts.CATEGORY_DEFAULT_VECTORS)
    assert set(controls["stride_control_mapping"]) == categories
    assert set(ts.PREFIX_CATEGORY.values()) == categories  # every category has a prefix, and no other
    assert set(_yaml(SCHEMA)["category_defaults"]) == categories


# =============================================================================
# ... and reachability-analysis.md
# =============================================================================


def _reachability_text() -> str:
    return REACHABILITY.read_text(encoding="utf-8")


def _range(text: str) -> tuple[Decimal, Decimal]:
    low, high = re.findall(r"[0-9]+\.[0-9]+", text)
    return D(low), D(high)


def test_reachability_baselines_and_ranges_match_the_baseline_table() -> None:
    rows = _table_rows(_reachability_text(), "### Zone-to-Reachability Baseline Mapping")
    assert {row[0] for row in rows} == set(ts.REACHABILITY_BASELINES) == set(ts.REACHABILITY_RANGES)
    for trust_level, _examples, score_range, baseline, _rationale in rows:
        assert D(baseline) == ts.REACHABILITY_BASELINES[trust_level], trust_level
        assert _range(score_range) == ts.REACHABILITY_RANGES[trust_level], trust_level
        low, high = ts.REACHABILITY_RANGES[trust_level]
        assert (low + high) / 2 == ts.REACHABILITY_BASELINES[trust_level]  # "the midpoint of the range"


def test_reachability_clamp_ranges_and_the_default_match_the_clamp_table() -> None:
    text = _reachability_text()
    rows = {row[0]: _range(row[1]) for row in _table_rows(text, "### Final Score Clamping")}
    default_range = rows.pop("Default (no zone data)")
    assert rows == dict(ts.REACHABILITY_RANGES)
    assert default_range == ts.REACHABILITY_DEFAULT_RANGE
    default = re.findall(r"\*\*Default reachability score\*\*: ([0-9.]+) \(medium exposure\)", text)
    assert [D(x) for x in default] == [ts.REACHABILITY_DEFAULT]
    low, high = ts.REACHABILITY_DEFAULT_RANGE
    assert low <= ts.REACHABILITY_DEFAULT <= high


def test_reachability_keyword_adjustments_match_the_keyword_table() -> None:
    rows = _table_rows(_reachability_text(), "Apply these zone name keyword adjustments:")
    documented = []
    for keywords, adjustment, _rationale in rows:
        amount = re.match(r"([+-][0-9.]+) from default baseline", adjustment)
        assert amount, adjustment
        documented.extend((word, D(amount.group(1))) for word in re.findall(r'"([^"]+)"', keywords))
    embedded = [(word, amount) for words, amount in ts.REACHABILITY_KEYWORDS for word in words]
    assert sorted(documented) == sorted(embedded)
    assert len(rows) == len(ts.REACHABILITY_KEYWORDS) == 5
    assert len({word for word, _ in embedded}) == len(embedded)  # no keyword adjusts twice


def test_reachability_architecture_adjustments_and_caps_match_the_text() -> None:
    text = _reachability_text()

    def only(pattern: str) -> tuple[str, ...]:
        """The groups of the one match of ``pattern`` (a pattern with one group gives one)."""
        found = re.findall(pattern, text)
        assert len(found) == 1, f"expected exactly one match of {pattern!r}, found {found}"
        return found[0] if isinstance(found[0], tuple) else (found[0],)

    (auth_each,) = only(r"#### Authentication Barrier Adjustment: (-[0-9.]+) per layer")
    auth_cap, auth_total = only(r"Maximum authentication barrier count per finding: "
                                r"\*\*([0-9]+)\*\* \(cap at (-[0-9.]+) total adjustment\)")
    (net_each,) = only(r"#### Network Segmentation Adjustment: (-[0-9.]+) per boundary")
    net_cap, net_total = only(r"Maximum network segmentation count per finding: "
                              r"\*\*([0-9]+)\*\* \(cap at (-[0-9.]+) total adjustment\)")
    (combined,) = only(r"\*\*Maximum total architecture adjustment\*\*: (-[0-9.]+)")
    assert D(auth_each) == ts.AUTH_BARRIER_ADJUSTMENT and int(auth_cap) == ts.AUTH_BARRIER_CAP
    assert D(net_each) == ts.NETWORK_BOUNDARY_ADJUSTMENT and int(net_cap) == ts.NETWORK_BOUNDARY_CAP
    assert ts.AUTH_BARRIER_ADJUSTMENT * ts.AUTH_BARRIER_CAP == D(auth_total)
    assert ts.NETWORK_BOUNDARY_ADJUSTMENT * ts.NETWORK_BOUNDARY_CAP == D(net_total)
    assert D(auth_total) + D(net_total) == D(combined)


# =============================================================================
# The documented tables agree with the calculator (Fix 397, N13)
# =============================================================================


@pytest.mark.parametrize("path", [REFERENCE, ADAPTER], ids=["reference", "adapter"])
def test_vector_reference_table_matches_schema_and_computed_scores(path: Path) -> None:
    defaults = _schema_defaults()
    rows = _table_rows(path.read_text(encoding="utf-8"), "Category Default Vector Reference")
    assert {row[0] for row in rows} == set(defaults), f"{path.name}: table categories differ"
    for category, vector, score, *_ in rows:
        assert vector == defaults[category], f"{path.name}: {category} vector differs from schema"
        assert D(score) == ts.base_score(vector), (
            f"{path.name}: {category} documents {score}, its vector scores {ts.base_score(vector)}"
        )


def test_bounded_range_table_matches_the_computed_defaults() -> None:
    defaults = _schema_defaults()
    rows = _table_rows(REFERENCE.read_text(encoding="utf-8"),
                       "**Category defaults with bounded ranges**")
    assert {row[0] for row in rows} == set(defaults)
    for category, _prefix, default, bounded in rows:
        computed = ts.base_score(defaults[category])
        assert D(default) == computed, f"{category}: documents {default}, computed {computed}"
        assert D(default) == ts.default_score(category)
        low, high = (D(x) for x in re.split(r"\s*[–-]\s*", bounded))
        assert (low, high) == (max(D("0.0"), computed - 1), min(D("10.0"), computed + 1)), (
            f"{category}: bounded range {bounded} does not equal default +/-1.0 clamped to [0, 10]"
        )
        assert (low, high) == ts.bounds(computed) == ts.bounds(ts.default_score(category))


@pytest.mark.parametrize("path", [REFERENCE, ADAPTER], ids=["reference", "adapter"])
def test_ai_guidance_default_vectors_match_schema(path: Path) -> None:
    defaults = _schema_defaults()
    found = dict(re.findall(r"\(`([a-z-]+)`\)\*\*:\n- Default vector: `([^`]+)`",
                            path.read_text(encoding="utf-8")))
    assert set(found) == {"agentic", "llm"}, f"{path.name}: guidance blocks found: {sorted(found)}"
    for category, vector in found.items():
        assert vector == defaults[category], f"{path.name}: {category} guidance vector differs"
