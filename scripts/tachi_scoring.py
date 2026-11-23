"""Scoring constants and stored-value arithmetic for the tachi renderers (ADR-050 D5, D10).

The risk-scores and compensating-controls renderers import this module for every number they
write, so the arithmetic lives in one place that tests can pin. It is standard-library only
(Python 3.9 and later) and imports no local module, so it carries no bytecode guard of its
own: each entry script sets ``sys.dont_write_bytecode`` before it imports this one (ADR-049 D8).
PyYAML is a test-only dependency: ``tests/scripts/test_cvss_category_defaults.py`` compares every
embedded constant with ``schemas/risk-scoring.yaml``, ``schemas/compensating-controls.yaml`` and
``reachability-analysis.md``, so a copy that drifts fails CI (R-32, KB 26).

Rules this module holds:

* **No float enters stored-value arithmetic.** Stored values are ``Decimal`` values built from
  strings (or from JSON parsed with ``parse_float=Decimal``). ``q1``, ``band`` and the helpers
  below refuse a float with ``TypeError``, because ``Decimal(4.55)`` is 4.5499... and would
  silently round to 4.5. The one float path is the CVSS calculator, which follows FIRST's
  equations in float and returns a ``Decimal`` built from an integer count of tenths.
* **Two roundings, never mixed.** ``q1`` is half-up to one decimal (4.55 gives 4.6). It rounds
  the sub-score means, the composite, the residual and the reduction percentage. CVSS Roundup
  is FIRST's Appendix A integer method, and only the CVSS calculator uses it.
* **Rounding comes before banding.** ``band`` refuses a value that is not already on the 0.1
  grid, so its inclusive minimums are applied to the rounded value.
* **The date is an input.** Nothing here reads the clock.
* **A module-private ``decimal`` context** runs every computation, so another module's
  ``getcontext()`` changes cannot move a result.

Refusals: a wrong type raises ``TypeError``; a value that is the right type but unusable raises
``ValueError``. Callers that treat both as "unusable input" catch the pair.
"""
from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from datetime import date, timedelta
from decimal import (
    ROUND_DOWN,
    ROUND_HALF_UP,
    Context,
    Decimal,
    DivisionByZero,
    FloatOperation,
    InvalidOperation,
    Overflow,
    localcontext,
)

# The module-private context. FloatOperation is trapped as a second guard behind the explicit
# type checks: a float that reached Decimal arithmetic here would raise instead of rounding.
_CTX = Context(
    prec=28,
    rounding=ROUND_HALF_UP,
    traps=[InvalidOperation, DivisionByZero, Overflow, FloatOperation],
)
_TENTH = Decimal("0.1")
_ZERO = Decimal("0.0")
_ONE = Decimal("1")
_TEN = Decimal("10.0")


# =============================================================================
# Embedded constants (Decimal strings; drift-tested against the schemas and the references)
# =============================================================================

# schemas/risk-scoring.yaml -> weights
WEIGHTS = {
    "cvss_base": Decimal("0.35"),
    "exploitability": Decimal("0.30"),
    "scalability": Decimal("0.15"),
    "reachability": Decimal("0.20"),
}

# schemas/risk-scoring.yaml -> severity_bands, highest band first. A minimum is inclusive and
# Low runs down to 0.0. The schemas' ``max`` values are not stored: each is the next band's
# minimum less 0.1, and the drift test checks that.
SEVERITY_BANDS = {
    "Critical": {"min": Decimal("9.0"), "sla": "24h", "disposition": "Mitigate"},
    "High": {"min": Decimal("7.0"), "sla": "7d", "disposition": "Mitigate"},
    "Medium": {"min": Decimal("4.0"), "sla": "30d", "disposition": "Review"},
    "Low": {"min": Decimal("0.0"), "sla": "90d", "disposition": "Review"},
}

# schemas/risk-scoring.yaml -> category_defaults
CATEGORY_DEFAULT_VECTORS = {
    "spoofing": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N",
    "tampering": "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L",
    "repudiation": "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N",
    "info-disclosure": "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N",
    "denial-of-service": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H",
    "privilege-escalation": "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H",
    "agentic": "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L",
    "llm": "CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N",
}

# ADR-050 D10: a category for every finding-ID prefix. S, T, R, I, D and E are the STRIDE
# categories; AG, AGP and TE are agentic; LLM, OI and MI are llm. Phase 3 files OI, MI and TE
# findings under the AI tables, so a finding scores the same whether or not #356 folds its
# prefix into LLM-N or AG-N. ``tachi_parsers.STRIDE_PREFIXES`` is unchanged on purpose: its
# "Other" roll-up is what the PDF renders.
PREFIX_CATEGORY = {
    "S": "spoofing",
    "T": "tampering",
    "R": "repudiation",
    "I": "info-disclosure",
    "D": "denial-of-service",
    "E": "privilege-escalation",
    "AG": "agentic",
    "AGP": "agentic",
    "LLM": "llm",
    "OI": "llm",
    "MI": "llm",
    "TE": "agentic",
}

# schemas/risk-scoring.yaml -> asset_modifiers. Each tag forces impact bits to H (floor only),
# and the elevated score is clamped at the ceiling (R-25, asset-modifiers.md). The tag set is
# closed at six.
TAG_FORCES = {
    "pii": ("C:H",),
    "phi": ("C:H",),
    "auth": ("C:H", "I:H"),
    "secrets": ("C:H", "I:H"),
    "financial": ("I:H",),
    "safety": ("A:H",),
}
MODIFIER_CEILING = Decimal("9.2")

# schemas/compensating-controls.yaml -> reduction_factor_p0, keyed by control status.
# AOD-SIMPLIFICATION: P0 factors only, as D5 lists — upgrade: add reduction_factor_p1 + drift test
REDUCTION_FACTOR_P0 = {
    "found": Decimal("0.50"),
    "partial": Decimal("0.25"),
    "missing": Decimal("0.00"),
}

# reachability-analysis.md: the zone baselines, the per-trust-level clamp ranges, the zone-name
# keyword adjustments (case-insensitive substring match, net sum applied), the per-layer and
# per-boundary architecture adjustments with their caps in layers and boundaries, and the
# flat default used when there is no trust-zone data.
# AOD-SIMPLIFICATION: constants only, no reachability function — upgrade: add it where R is built
REACHABILITY_BASELINES = {
    "Untrusted": Decimal("9.0"),
    "Semi-Trusted": Decimal("5.5"),
    "Trusted": Decimal("2.5"),
}
REACHABILITY_RANGES = {
    "Untrusted": (Decimal("8.0"), Decimal("10.0")),
    "Semi-Trusted": (Decimal("4.0"), Decimal("7.0")),
    "Trusted": (Decimal("1.0"), Decimal("4.0")),
}
REACHABILITY_DEFAULT = Decimal("5.0")
REACHABILITY_DEFAULT_RANGE = (Decimal("0.0"), Decimal("10.0"))
REACHABILITY_KEYWORDS = (
    (("internet", "public", "external"), Decimal("0.5")),
    (("user", "client"), Decimal("0.5")),
    (("dmz", "perimeter", "gateway"), Decimal("0.5")),
    (("internal", "backend", "core"), Decimal("-0.5")),
    (("database", "storage", "data store"), Decimal("-0.5")),
)
AUTH_BARRIER_ADJUSTMENT = Decimal("-1.5")
AUTH_BARRIER_CAP = 3
NETWORK_BOUNDARY_ADJUSTMENT = Decimal("-1.0")
NETWORK_BOUNDARY_CAP = 3


# =============================================================================
# Refusals shared by the helpers
# =============================================================================


def _show(value: object) -> str:
    """A short, escaped form of a refused value, safe to put in an error message."""
    return repr(value)[:60]


def _as_decimal(value: object, what: str) -> Decimal:
    """``value`` as a finite ``Decimal``: a ``Decimal`` or an ``int``, never a float or a bool."""
    if isinstance(value, Decimal):
        number = value
    elif isinstance(value, int) and not isinstance(value, bool):
        number = Decimal(value)
    else:
        raise TypeError(
            f"{what} must be a Decimal or an int, not {type(value).__name__}: "
            "a float never enters stored-value arithmetic (ADR-050 D5)"
        )
    if not number.is_finite():
        raise ValueError(f"{what} is not finite: {number}")
    return number


def _stored(value: object, what: str) -> Decimal:
    """A stored score: in 0.0 to 10.0 and already on the 0.1 grid (4.50 passes, 4.55 does not)."""
    number = _as_decimal(value, what)
    if not _ZERO <= number <= _TEN:
        raise ValueError(f"{what} {number} is outside 0.0 to 10.0")
    if number != number.quantize(_TENTH, rounding=ROUND_DOWN, context=_CTX):
        raise ValueError(f"{what} {number} is not quantized to 0.1: round it with q1() first")
    return number


# =============================================================================
# q1 and band
# =============================================================================


def q1(value: Decimal | int) -> Decimal:
    """Round to one decimal, half-up: ``q1(Decimal("4.55"))`` is ``Decimal("4.6")``.

    Python's ``round(4.55, 1)`` gives 4.5, and ``Decimal``'s default context rounds half-even.
    Neither is the rule ADR-050 D5 pins. A float raises ``TypeError``; a value too large to
    hold one decimal in the module's precision raises ``ValueError``.
    """
    number = _as_decimal(value, "value")
    try:
        return number.quantize(_TENTH, rounding=ROUND_HALF_UP, context=_CTX)
    except InvalidOperation:
        raise ValueError(f"value {number} is too large to round to one decimal") from None


def band(score: Decimal | int) -> str:
    """The severity band of a stored score: Critical, High, Medium or Low.

    Minimums are inclusive (9.0 is Critical, 7.0 High, 4.0 Medium). The score must already be
    on the 0.1 grid and inside 0.0 to 10.0: ``band(Decimal("4.55"))`` raises ``ValueError``,
    so a caller rounds with ``q1`` first and a value cannot be banded as 4.5 while it prints
    as 4.55.
    """
    number = _stored(score, "score")
    return next(name for name, rule in SEVERITY_BANDS.items() if number >= rule["min"])


# =============================================================================
# CVSS 3.1 (FIRST specification section 7; Appendix A Roundup)
# =============================================================================

# Metric weights from the specification's section 7.4. They are float by design: the equations
# are FIRST's, and the 16 examples below pin the float result.
_AV = {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2}
_AC = {"L": 0.77, "H": 0.44}
_PR = {"U": {"N": 0.85, "L": 0.62, "H": 0.27}, "C": {"N": 0.85, "L": 0.68, "H": 0.5}}
_UI = {"N": 0.85, "R": 0.62}
_CIA = {"H": 0.56, "L": 0.22, "N": 0.0}
_METRIC_ORDER = ("AV", "AC", "PR", "UI", "S", "C", "I", "A")
_LEVEL = {"N": 0, "L": 1, "H": 2}
# ``fullmatch`` with no ``$``: a trailing newline does not pass.
_VECTOR_RE = re.compile(
    r"CVSS:3\.1/AV:[NALP]/AC:[LH]/PR:[NLH]/UI:[NR]/S:[UC]/C:[HLN]/I:[HLN]/A:[HLN]"
)

# Base metrics and v3.1 base scores of examples in FIRST's "CVSS v3.1 Examples" document
# (https://www.first.org/cvss/v3.1/examples), transcribed from each example's metric table.
# ``self_test()`` runs them; the scores are strings so they compare as ``Decimal``.
FIRST_EXAMPLES = (
    ("CVE-2013-0375", "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N", "6.4"),
    ("CVE-2014-3566", "CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:N/A:N", "3.1"),
    ("CVE-2012-1516", "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H", "9.9"),
    ("CVE-2009-0783", "CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L", "4.2"),
    ("CVE-2012-0384", "CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H", "7.2"),
    ("CVE-2014-0160", "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N", "7.5"),
    ("CVE-2014-6271", "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H", "9.8"),
    ("CVE-2008-1447", "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:H/A:N", "6.8"),
    ("CVE-2014-2005", "CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H", "6.8"),
    ("CVE-2013-6014", "CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:H", "9.3"),
    ("CVE-2017-5942", "CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N", "6.1"),
    ("CVE-2011-1265", "CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H", "8.8"),
    ("CVE-2014-2019", "CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N", "4.6"),
    ("CVE-2012-5376", "CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H", "9.6"),
    ("CVE-2016-5729", "CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H", "8.2"),
    ("CVE-2018-3652", "CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H", "7.6"),
)


def roundup(value: float) -> Decimal:
    """CVSS 3.1 Roundup: the smallest one-decimal number >= ``value`` (specification section 7).

    Computed on integers as Appendix A prescribes, so float noise cannot add 0.1:
    ``roundup(0.1 + 0.2)`` is ``Decimal("0.3")``, not 0.4. The result enters ``Decimal`` as an
    integer count of tenths. This is not half-up rounding and ``q1`` never calls it.
    """
    scaled = round(value * 100000)
    tenths = scaled // 10000 if scaled % 10000 == 0 else scaled // 10000 + 1
    return Decimal(tenths).scaleb(-1, context=_CTX)


def _metrics(vector: str) -> dict[str, str]:
    """The metric letters of a full CVSS 3.1 base vector, or ``ValueError``."""
    if not isinstance(vector, str) or _VECTOR_RE.fullmatch(vector) is None:
        raise ValueError(f"not a full CVSS 3.1 base vector: {_show(vector)}")
    return dict(part.split(":") for part in vector.split("/")[1:])


def base_score(vector: str) -> Decimal:
    """The CVSS 3.1 base score of a full base vector (specification section 7.1)."""
    m = _metrics(vector)
    changed = m["S"] == "C"
    iss = 1 - (1 - _CIA[m["C"]]) * (1 - _CIA[m["I"]]) * (1 - _CIA[m["A"]])
    impact = 7.52 * (iss - 0.029) - 3.25 * (iss - 0.02) ** 15 if changed else 6.42 * iss
    exploitability = 8.22 * _AV[m["AV"]] * _AC[m["AC"]] * _PR[m["S"]][m["PR"]] * _UI[m["UI"]]
    if impact <= 0:
        return _ZERO
    raw = 1.08 * (impact + exploitability) if changed else impact + exploitability
    return roundup(min(raw, 10))


def elevate(vector: str, tags: Iterable[str]) -> str:
    """The vector with every asset tag's forced impact bits raised to ``H`` (floor only).

    Per bit, the result is the higher of the vector's value and every tag's forced value
    (``H`` over ``L`` over ``N``), so a bit that is already ``H`` is untouched and no bit falls.
    A tag outside the closed six raises ``ValueError``. The ceiling and R-25's ``max`` belong to
    the caller: ``max(assessed, min(base_score(elevate(v, tags)), MODIFIER_CEILING))``.
    """
    metrics = _metrics(vector)
    for tag in tags:
        forced = TAG_FORCES.get(tag)
        if forced is None:
            raise ValueError(f"unknown asset tag {_show(tag)}: the set is {sorted(TAG_FORCES)}")
        for bit in forced:
            name, level = bit.split(":")
            if _LEVEL[level] > _LEVEL[metrics[name]]:
                metrics[name] = level
    return "CVSS:3.1/" + "/".join(f"{name}:{metrics[name]}" for name in _METRIC_ORDER)


def default_score(category: str) -> Decimal:
    """The CVSS base score of a category's default vector (``cvss-vectors.md``)."""
    vector = CATEGORY_DEFAULT_VECTORS.get(category)
    if vector is None:
        known = sorted(CATEGORY_DEFAULT_VECTORS)
        raise ValueError(f"unknown category {_show(category)}: expected one of {known}")
    return base_score(vector)


def bounds(default: Decimal | int) -> tuple[Decimal, Decimal]:
    """The +/-1.0 score bounds around a category default: ``max(0, d - 1)`` to ``min(10, d + 1)``.

    A NEW finding in a baseline-aware run is clamped to these (stored as ``score_bounds``).
    """
    centre = _stored(default, "category default")
    with localcontext(_CTX):
        return q1(max(_ZERO, centre - _ONE)), q1(min(_TEN, centre + _ONE))


def self_test() -> None:
    """Run FIRST's 16 examples through ``base_score``; raise ``AssertionError`` on any miss.

    The renderer calls this at start-up and fails closed, so a calculator that has drifted from
    the specification stops the run before it writes a score. It raises explicitly rather than
    using ``assert``, which ``python -O`` strips.
    """
    misses = []
    for example, vector, expected in FIRST_EXAMPLES:
        got = base_score(vector)
        if got != Decimal(expected):
            misses.append(f"{example} {vector}: got {got}, expected {expected}")
    if misses:
        raise AssertionError("CVSS 3.1 self-test failed: " + "; ".join(misses))


# =============================================================================
# The stored-value arithmetic that rounds with q1
# =============================================================================


def sub_score_mean(values: Sequence[Decimal | int]) -> Decimal:
    """The mean of four sub-scores, half-up to one decimal (exploitability and scalability).

    ``(Known Techniques + Attack Complexity + Tooling Availability + Skill Level) / 4`` and
    ``(Scriptability + Target Scope + Resource Requirements + Detection Difficulty) / 4``.
    The sum and the division by four are exact, so a mean that ends in 5 at the hundredths
    rounds up. Exactly four values, each from 0.0 to 10.0, are required.
    """
    if len(values) != 4:
        raise ValueError(f"a sub-score mean takes exactly four values, not {len(values)}")
    numbers = [_as_decimal(value, "sub-score") for value in values]
    for number in numbers:
        if not _ZERO <= number <= _TEN:
            raise ValueError(f"sub-score {number} is outside 0.0 to 10.0")
    with localcontext(_CTX):
        return q1(sum(numbers, Decimal(0)) / 4)


def composite(
    cvss_base: Decimal | int,
    exploitability: Decimal | int,
    scalability: Decimal | int,
    reachability: Decimal | int,
) -> Decimal:
    """The weighted composite ``0.35C + 0.30E + 0.15S + 0.20R``, half-up to one decimal.

    The four inputs are stored one-decimal values and the weighted sum is exact, so a sum that
    ends in 5 at the hundredths (6.35) rounds up (6.4) however the same sum would fall in float.
    """
    parts = (
        ("cvss_base", cvss_base),
        ("exploitability", exploitability),
        ("scalability", scalability),
        ("reachability", reachability),
    )
    with localcontext(_CTX):
        total = sum((WEIGHTS[name] * _stored(value, name) for name, value in parts), Decimal(0))
        return q1(total)


def residual_score(composite_score: Decimal | int, reduction_factor: Decimal | int) -> Decimal:
    """The residual score ``inherent * (1 - factor)``, half-up to one decimal.

    ``residual_score(Decimal("9.1"), Decimal("0.50"))`` is 4.6, from 4.55. The factor must be
    from 0 to 1, so the result stays inside 0.0 to 10.0.
    """
    inherent = _stored(composite_score, "composite score")
    factor = _as_decimal(reduction_factor, "reduction factor")
    if not _ZERO <= factor <= _ONE:
        raise ValueError(f"reduction factor {factor} is outside 0 to 1")
    with localcontext(_CTX):
        return q1(inherent * (_ONE - factor))


def reduction_percentage(inherent_total: Decimal | int, residual_total: Decimal | int) -> Decimal:
    """The overall reduction ``(inherent - residual) / inherent * 100``, half-up to one decimal.

    The totals are exact sums of the stored scores. A zero inherent total gives 0.0.
    """
    inherent = _as_decimal(inherent_total, "inherent total")
    residual = _as_decimal(residual_total, "residual total")
    if inherent < 0 or residual < 0:
        raise ValueError("a risk total cannot be negative")
    if inherent == 0:
        return q1(0)
    with localcontext(_CTX):
        return q1((inherent - residual) * 100 / inherent)


# =============================================================================
# Distributions that must sum to 100 (ADR-017 D2's largest remainder, in integers)
# =============================================================================


def largest_remainder(counts: Mapping[str, int]) -> dict[str, int]:
    """Integer percentages of ``counts`` that sum to exactly 100.

    The largest-remainder (Hamilton) method on integers: each label gets ``100 * n // total``,
    and the shortfall is handed out one point at a time to the labels with the largest
    ``100 * n % total``, with ties going to the label that sorts first. All zero when the total
    is 0. The result keeps the input's key order. Counts must be non-negative ``int`` values;
    the total is their exact sum.
    """
    for label, count in counts.items():
        if isinstance(count, bool) or not isinstance(count, int):
            raise TypeError(f"count for {_show(label)} must be an int, not {type(count).__name__}")
        if count < 0:
            raise ValueError(f"count for {_show(label)} is negative: {count}")
    total = sum(counts.values())
    if total == 0:
        return {label: 0 for label in counts}
    shares = {label: 100 * count // total for label, count in counts.items()}
    by_remainder = sorted(counts, key=lambda label: (-(100 * counts[label] % total), label))
    for label in by_remainder[: 100 - sum(shares.values())]:
        shares[label] += 1
    return shares


# =============================================================================
# The prefix resolver (ADR-050 D10)
# =============================================================================


def category_for_prefix(prefix: str) -> str:
    """The scoring category of a finding-ID prefix, for all 12 prefixes (``PREFIX_CATEGORY``).

    One resolver serves the CVSS defaults and bounds, the controls' STRIDE-to-control mapping
    and the SARIF rule IDs. ``category_for_prefix("AGP")`` is ``"agentic"``. An unknown prefix
    raises ``ValueError``. The caller passes the prefix of an ID it has already validated.
    """
    category = PREFIX_CATEGORY.get(prefix)
    if category is None:
        raise ValueError(
            f"unknown finding-ID prefix {_show(prefix)}: expected one of {list(PREFIX_CATEGORY)}"
        )
    return category


# =============================================================================
# Dates and SLAs (the date is an input; the clock never enters rendered output)
# =============================================================================

_DATE_RE = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})")
_SLA_RE = re.compile(r"([0-9]{1,6})([hd])")


def parse_date(text: str) -> date:
    """A strict ``YYYY-MM-DD`` calendar date (ASCII digits only), or ``ValueError``."""
    match = _DATE_RE.fullmatch(text) if isinstance(text, str) else None
    if match is None:
        raise ValueError(f"not a YYYY-MM-DD date: {_show(text)}")
    try:
        return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except ValueError:
        raise ValueError(f"not a calendar date: {_show(text)}") from None


def sla_days(sla: str) -> int:
    """The days an SLA string allows: ``<n>h`` gives ceil(n / 24), ``<n>d`` gives n.

    ``24h`` is 1, ``25h`` is 2, ``7d`` is 7. Anything else is unparseable and raises
    ``ValueError``: no unit, an upper-case unit, a sign, a space, a decimal point, a
    non-ASCII digit, or more than six digits.
    """
    match = _SLA_RE.fullmatch(sla) if isinstance(sla, str) else None
    if match is None:
        raise ValueError(f"unparseable SLA {_show(sla)}: expected <n>h or <n>d")
    count = int(match.group(1))
    return -(-count // 24) if match.group(2) == "h" else count


def review_date(start: str, sla: str) -> str:
    """``start`` plus the SLA's days, in calendar arithmetic, as ``YYYY-MM-DD``.

    ``review_date("2026-01-29", "30d")`` is ``"2026-02-28"``. ``start`` is an input date, never
    the clock. A date past 9999-12-31 raises ``ValueError``.
    """
    begin = parse_date(start)
    try:
        return (begin + timedelta(days=sla_days(sla))).isoformat()
    except OverflowError:
        raise ValueError(f"{start} plus {sla} is past 9999-12-31") from None
