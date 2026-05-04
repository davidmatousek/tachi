"""Canary test for the load-bearing shopt shim in template-substitute.sh.

This module exists to close TC-1 from Feature 250 (adversarial unit
extraction hot-fix). It is a permanent CI canary that detects accidental
removal of a single load-bearing line in
``.aod/scripts/bash/template-substitute.sh``::

    shopt -u patsub_replacement 2>/dev/null||true

That line disables bash 5.2+'s ``patsub_replacement`` option. Without it,
the ``&`` character inside a substitution replacement value is treated as
a "match-text" backref, which corrupts inputs like ``project_name='AT&T'``
into ``'ATtachiT'`` — the original F-248 regression class.

The shim is harmless on bash 3.2 (macOS dev) because the unknown ``shopt``
silently no-ops via ``2>/dev/null || true``, but it is load-bearing on
bash 5.x runners (ubuntu-latest CI today; macOS-latest CI from bash 5.x
onward). A future cleanup PR mistaking the line for dead code would
silently re-introduce the F-248 substitution-helper regressions affecting
case_1_ampersand and the case_3 / case_6 substitution paths.

This test is unit-level by design: it performs a pure file-read assertion.
It does NOT invoke ``init.sh``, does NOT subprocess-call any helper, and
runs in well under 100ms. The intent is a fast, deterministic CI guard
that fires immediately on accidental shim removal with a load-bearing
diagnostic that tells the developer exactly what to restore.
"""

from __future__ import annotations

from pathlib import Path


def test_template_substitute_shim_present() -> None:
    """Assert the load-bearing shopt shim is in template-substitute.sh.

    The shim disables bash 5.2+'s patsub_replacement option so `&` in
    replacement values is treated literally (not as a match-text backref).
    Removing it would re-introduce the F-248 'AT&T → ATtachiT'
    corruption on bash 5.x runners (macOS-latest CI from bash 5.x onward,
    ubuntu-latest CI today).

    On bash 3.2 (macOS dev) the shopt is unknown and silently no-ops via
    `2>/dev/null || true`, so the line is harmless cross-platform but
    load-bearing on bash 5.x. This canary catches accidental removal.
    """
    helper_path = Path(".aod/scripts/bash/template-substitute.sh")
    helper_text = helper_path.read_text()
    assert "shopt -u patsub_replacement" in helper_text, (
        f"Load-bearing shim removed from {helper_path}. "
        "This shim disables bash 5.2+'s patsub_replacement option so '&' "
        "in replacement values is treated literally. Without it, "
        "case_1_ampersand (project_name='AT&T') would corrupt to "
        "'ATtachiT' on bash 5.x runners — the original F-248 "
        "regression class. Restore the line `shopt -u patsub_replacement "
        "2>/dev/null||true` near the top of the helper function."
    )
