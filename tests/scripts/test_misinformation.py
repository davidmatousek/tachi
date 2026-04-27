"""Unit tests for the ``misinformation`` threat agent schema contract (T005).

TDD expectation: this file is authored at Wave 1.1 BEFORE the schema bump at
T006. Case B (``MI-{N}`` prefixes) MUST fail against schema 1.6's regex
``^(S|T|R|I|D|E|AG|LLM|AGP|OI)-\\d+$``; T006 extends the alternation to
``|MI`` and bumps ``schema_version`` to ``"1.7"``, at which point all three
cases pass. Do NOT mark tests ``xfail`` or ``skip`` — the Case B failure is
the TDD fence post that T006 is required to remove.

Scope: regex unit coverage only. F-A2 referential-integrity validation on
``MI-{N}`` ``source_attribution`` citations is exercised by T038 against the
regenerated ``examples/agentic-app/`` artifacts, not here.
"""

from __future__ import annotations

import re

import pytest


# ---------------------------------------------------------------------------
# Case A — Pre-1.7 ID prefixes remain valid (backward-compat guarantee).
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "valid_id",
    [
        "S-1",
        "T-1",
        "R-1",
        "I-1",
        "D-1",
        "E-1",
        "AG-1",
        "LLM-1",
        "AGP-1",
        "OI-1",
    ],
)
def test_pre_1_7_ids_valid(id_pattern: re.Pattern, valid_id: str) -> None:
    """All pre-1.7 ID prefixes (STRIDE + AG + LLM + AGP + OI) MUST remain valid."""
    assert id_pattern.match(valid_id) is not None, (
        f"Pre-1.7 ID {valid_id!r} MUST remain valid in the schema 1.7 regex "
        f"(backward compatibility requirement)."
    )


# ---------------------------------------------------------------------------
# Case B — ``MI`` prefix is new in 1.7 (fails against 1.6; T006 resolves).
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "mi_id",
    [
        "MI-1",
        "MI-10",
        "MI-99",
    ],
)
def test_mi_prefix_valid(id_pattern: re.Pattern, mi_id: str) -> None:
    """``MI-{N}`` IDs MUST match the 1.7 regex. FAILS against 1.6 by design."""
    assert id_pattern.match(mi_id) is not None, (
        f"MI-{{N}} ID {mi_id!r} MUST match the 1.7 regex. If this is failing, "
        f"the schema_version is still 1.6 and T006 has not been executed."
    )


# ---------------------------------------------------------------------------
# Case C — Non-matching inputs MUST be rejected.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "invalid_id",
    [
        "MI1",      # missing hyphen
        "MIA-1",    # 3-letter prefix
        "mi-1",     # lowercase prefix
        "",         # empty string
        "MI-abc",   # non-digit suffix
        "MI-",      # trailing hyphen, no digit
    ],
)
def test_invalid_patterns_rejected(id_pattern: re.Pattern, invalid_id: str) -> None:
    """Malformed IDs (bad shape, case, suffix) MUST NOT match the regex."""
    assert id_pattern.match(invalid_id) is None, (
        f"Malformed ID {invalid_id!r} MUST NOT match the finding.id.pattern regex."
    )
