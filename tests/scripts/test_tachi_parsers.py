"""Unit tests for the shared ``scripts/tachi_parsers.py`` helpers.

Currently exercises :func:`classify_maestro_coverage_state` and the
:data:`SEVERITY_ORDINAL` ordinal-0 invariant introduced by Feature 311
(MAESTRO Matrix Model B — clean vs. n/a).

``classify_maestro_coverage_state`` is the single inheritance point both
extractors call to translate the Section-6 "Highest Severity" carried token
into the ``coverage_state`` enum. It is pure (reads only its two arguments),
does NOT read Section 1, and does NOT decide applicability — it classifies the
orchestrator's already-authored decision. See
``specs/311-maestro-matrix-model-b-clean-vs-na/contracts/coverage-state-classifier.contract.md``
and ADR-047 (D2/D3/D5).

Stdlib-only per PAT-014 — no PyYAML, no Path operations beyond importlib.
"""

from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from tachi_parsers import (  # noqa: E402  -- import after sys.path mutation
    SEVERITY_ORDINAL,
    classify_maestro_coverage_state,
)


# Canonical Section-6 zero-finding tokens (ADR-047 D1; data-model.md Entity 1).
# Authored with U+2014 (em-dash); no trailing period in the markdown cell.
_CLEAN_TOKEN = "Analyzed — no findings this scan"
_NA_TOKEN = "Not applicable — no components map to this layer"
# Same n/a phrase written with U+2013 (en-dash) — must still classify as n/a
# (INV-2 dash tolerance; the populator/extractor read-robustness parity).
_NA_TOKEN_ENDASH = "Not applicable – no components map to this layer"


# =============================================================================
# classify_maestro_coverage_state — mapping table (contract T-1..T-5)
# =============================================================================

# T-1: any positive finding count is "findings" regardless of severity.
def test_positive_finding_count_is_findings():
    assert classify_maestro_coverage_state(8, "Critical") == "findings"
    assert classify_maestro_coverage_state(2, "High") == "findings"


# T-2: zero findings + the clean token → "clean".
def test_zero_findings_clean_token_is_clean():
    assert classify_maestro_coverage_state(0, _CLEAN_TOKEN) == "clean"


# T-3: zero findings + the n/a token → "not_applicable".
def test_zero_findings_na_token_is_not_applicable():
    assert classify_maestro_coverage_state(0, _NA_TOKEN) == "not_applicable"


# T-4: zero findings + empty / unrecognized → "clean" (backfill default; INV-4).
def test_zero_findings_empty_is_clean_backfill_default():
    assert classify_maestro_coverage_state(0, "") == "clean"


def test_zero_findings_unrecognized_is_clean():
    assert classify_maestro_coverage_state(0, "n/a-ish unknown") == "clean"


# T-5: en-dash (U+2013) tolerance on the n/a phrase → "not_applicable".
def test_na_token_endash_tolerated_is_not_applicable():
    assert classify_maestro_coverage_state(0, _NA_TOKEN_ENDASH) == "not_applicable"


# =============================================================================
# INV-3 / D5: zero-finding tokens resolve to severity ordinal 0
# =============================================================================

# T-6: neither the n/a nor the clean token is in SEVERITY_ORDINAL, so both
# dict-miss to rank 0 — compute_most_exposed_layer never selects them.
def test_zero_finding_tokens_resolve_to_ordinal_zero():
    assert SEVERITY_ORDINAL.get(_NA_TOKEN, 0) == 0
    assert SEVERITY_ORDINAL.get(_CLEAN_TOKEN, 0) == 0
