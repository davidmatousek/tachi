"""Synthetic + live test for the ORDERED_FRAMEWORKS catalog-drift guard (Feature 329).

The guard (`scripts/check-catalog-drift.py`) is the entire value of this feature, so
its trustworthiness MUST be proven by test (FR-007) — but never by rendering real
PDFs in the test or CI path (NFR-001). This module therefore combines:

  1. ONE live-tree assertion — the real CI gate. It computes the live
     ``ORDERED_FRAMEWORKS`` fingerprints, reads the committed sidecar, and asserts
     they agree. It **fails (not skips)** on a missing/partial/unparseable sidecar
     (FR-008 / Risk-5), so deleting the sidecar to silence the guard reddens CI.

  2. SYNTHETIC cases — the *logic* proof against crafted record sets:
        catch:  grow (add/remove) · constant-count ID swap (HIGH-2) ·
                out_of_scope flip (HIGH-3)                              → drift  (T008)
        ignore: citation-string-only / #333 class · non-member change ·
                clean tree                                             → no drift (T009)
        future: a synthetic 6th ORDERED_FRAMEWORKS member              → covered (T011)

Cache discipline (FR-007 / Risk-3): the renderer's loader is ``@functools.lru_cache``.
The live-tree case ``cache_clear()``-s it before reading; every synthetic case
**monkeypatches the loader outright** (the FR-007-sanctioned alternative), so it never
reads a stale cache for the wrong reason — a false-green a guard cannot afford.
"""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
GUARD_PATH = REPO_ROOT / "scripts" / "check-catalog-drift.py"

# Import the hyphenated guard module via importlib (the established repo pattern;
# see tests/scripts/test_attack_chain_extraction.py). The guard execs
# extract-report-data.py once at import to bind the renderer's loader.
_spec = importlib.util.spec_from_file_location("check_catalog_drift", str(GUARD_PATH))
guard = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(guard)


# ---------------------------------------------------------------------------
# Synthetic harness — fake loader + sidecar builder
# ---------------------------------------------------------------------------
# A minimal baseline record set for every live ORDERED_FRAMEWORKS member. The
# synthetic cases mutate ONE member and assert the guard pins exactly it. The
# `mitre-attack` set carries an out_of_scope record so its raw and in-scope
# partitions diverge (exercising both fingerprints independently).
BASELINE_RECORDS = {
    "owasp": [{"id": "LLM01"}, {"id": "LLM02"}],
    "mitre-attack": [{"id": "T1001"}, {"id": "T1059", "out_of_scope": True}],
    "mitre-atlas": [{"id": "AML.T0001"}],
    "nist-ai-rmf": [{"id": "MEASURE-2.1"}],
    "cwe": [{"id": "CWE-79"}, {"id": "CWE-89"}],
}


def _make_fake_loader(record_sets):
    """Build a stand-in for ``_load_framework_yaml_records`` over ``record_sets``.

    Mirrors the real loader's signature and its in-scope filter semantics exactly
    (``isinstance(r, dict) and r.get("out_of_scope", False)`` excluded when
    ``in_scope_only=True``), so the guard's fingerprints over the fake match what it
    would compute over real YAML of the same shape.
    """
    def _fake(framework_name, in_scope_only=False):
        records = record_sets[framework_name]
        if in_scope_only:
            return [
                r for r in records
                if not (isinstance(r, dict) and r.get("out_of_scope", False))
            ]
        return list(records)

    return _fake


def _install(monkeypatch, record_sets):
    """Monkeypatch the guard's loader to serve ``record_sets`` (auto-reverted)."""
    monkeypatch.setattr(
        guard, "_load_framework_yaml_records", _make_fake_loader(record_sets)
    )


def _sidecar_for(monkeypatch, record_sets):
    """Compute the pre-drift sidecar (``{"frameworks": {...}}``) for ``record_sets``.

    Uses the guard's own fingerprint functions so the expected values are self-
    consistent with what the guard will recompute on the (later-mutated) tree.
    """
    _install(monkeypatch, record_sets)
    return {"frameworks": guard.all_fingerprints()}


def _clone(record_sets):
    return copy.deepcopy(record_sets)


# ---------------------------------------------------------------------------
# 1. The live-tree gate (the real CI gate) + fail-closed (FR-008)
# ---------------------------------------------------------------------------
def test_live_tree_fingerprints_match_sidecar():
    """Real gate: the live tree's fingerprints equal the committed sidecar's.

    This is the assertion CI actually runs. ``read_sidecar`` raises (the test
    fails, not skips) if the sidecar is missing/partial/unparseable — FR-008.
    """
    guard._load_framework_yaml_records.cache_clear()  # FR-007: no stale cache
    sidecar = guard.read_sidecar()                    # fails-closed if absent
    live = guard.all_fingerprints()
    drift = guard.find_drift(live, sidecar)
    assert drift == [], (
        f"live ORDERED_FRAMEWORKS tree drifted from the committed sidecar: {drift}. "
        f"Run scripts/regenerate-ca-baselines.sh."
    )


def test_missing_sidecar_fails_closed(tmp_path):
    """A missing sidecar is a failure, never a pass (FR-008 / Risk-5)."""
    with pytest.raises(guard.SidecarError):
        guard.read_sidecar(tmp_path / "does-not-exist.json")


def test_unparseable_sidecar_fails_closed(tmp_path):
    """A truncated/corrupt sidecar is a failure, never a pass (FR-008)."""
    bad = tmp_path / "ca-baseline-fingerprints.json"
    bad.write_text('{"frameworks": {', encoding="utf-8")  # truncated JSON
    with pytest.raises(guard.SidecarError):
        guard.read_sidecar(bad)


def test_malformed_sidecar_fails_closed(tmp_path):
    """A sidecar missing the ``frameworks`` map is a failure (FR-008)."""
    bad = tmp_path / "ca-baseline-fingerprints.json"
    bad.write_text('{"source_date_epoch": "1700000000"}', encoding="utf-8")
    with pytest.raises(guard.SidecarError):
        guard.read_sidecar(bad)


def test_partial_sidecar_member_absent_is_drift(monkeypatch):
    """A live member ABSENT from the sidecar's frameworks ⇒ drift (FR-008)."""
    _install(monkeypatch, BASELINE_RECORDS)
    live = guard.all_fingerprints()
    partial = {"frameworks": {fw: fp for fw, fp in live.items() if fw != "cwe"}}
    drift = guard.find_drift(live, partial)
    assert "cwe" in drift


def test_run_check_exit_1_on_missing_sidecar(monkeypatch, tmp_path):
    """End-to-end: ``--check`` returns exit 1 when the sidecar is missing (FR-008)."""
    monkeypatch.setattr(guard, "SIDECAR_PATH", tmp_path / "absent.json")
    assert guard._run_check() == 1


# ---------------------------------------------------------------------------
# 2. Catch cases (T008) — real drift MUST fail
# ---------------------------------------------------------------------------
def test_grow_detected(monkeypatch):
    """Adding an in-scope record (the F-186 grow) drifts both fingerprints."""
    sidecar = _sidecar_for(monkeypatch, BASELINE_RECORDS)
    mutated = _clone(BASELINE_RECORDS)
    mutated["cwe"].append({"id": "CWE-90"})  # 2 -> 3 records
    _install(monkeypatch, mutated)
    drift = guard.find_drift(guard.all_fingerprints(), sidecar)
    assert "cwe" in drift
    assert "owasp" not in drift  # untouched members stay clean (precision)


def test_id_swap_detected(monkeypatch):
    """A constant-count ID rename/swap drifts the in-scope fingerprint (HIGH-2)."""
    sidecar = _sidecar_for(monkeypatch, BASELINE_RECORDS)
    mutated = _clone(BASELINE_RECORDS)
    mutated["cwe"][1] = {"id": "CWE-352"}  # CWE-89 -> CWE-352, count unchanged (2)
    _install(monkeypatch, mutated)
    live = guard.all_fingerprints()
    drift = guard.find_drift(live, sidecar)
    assert "cwe" in drift
    # The bare count did NOT change — the fingerprint, not the count, caught it.
    assert live["cwe"]["in_scope_count"] == sidecar["frameworks"]["cwe"]["in_scope_count"]


def test_out_of_scope_flip_detected(monkeypatch):
    """Flipping a record's out_of_scope at constant raw count drifts both
    partitions (HIGH-3) — the in-scope set changes even though raw_count holds."""
    sidecar = _sidecar_for(monkeypatch, BASELINE_RECORDS)
    mutated = _clone(BASELINE_RECORDS)
    # T1059 was out_of_scope: flip it in-scope. raw_count stays 2; in-scope 1 -> 2.
    mutated["mitre-attack"][1] = {"id": "T1059"}
    _install(monkeypatch, mutated)
    live = guard.all_fingerprints()
    drift = guard.find_drift(live, sidecar)
    assert "mitre-attack" in drift
    assert live["mitre-attack"]["raw_count"] == (
        sidecar["frameworks"]["mitre-attack"]["raw_count"]
    )  # raw count unchanged — the in-scope partition shift is what bit


def test_two_members_drift_both_named(monkeypatch):
    """When two members drift in one change, find_drift names BOTH (edge case)."""
    sidecar = _sidecar_for(monkeypatch, BASELINE_RECORDS)
    mutated = _clone(BASELINE_RECORDS)
    mutated["cwe"].append({"id": "CWE-90"})
    mutated["owasp"].append({"id": "LLM03"})
    _install(monkeypatch, mutated)
    drift = guard.find_drift(guard.all_fingerprints(), sidecar)
    assert set(drift) >= {"cwe", "owasp"}


def test_failure_message_names_framework_and_regen(monkeypatch):
    """The failure message (FR-006) names the framework, shows counts, and points
    to the regen entry point."""
    sidecar = _sidecar_for(monkeypatch, BASELINE_RECORDS)
    mutated = _clone(BASELINE_RECORDS)
    mutated["cwe"].append({"id": "CWE-90"})
    _install(monkeypatch, mutated)
    live = guard.all_fingerprints()
    drift = guard.find_drift(live, sidecar)
    message = guard.format_failure(drift, live, sidecar)
    assert "cwe" in message
    assert "regenerate-ca-baselines.sh" in message
    assert "2 -> 3" in message  # human-readable count summary


# ---------------------------------------------------------------------------
# 3. Ignore cases (T009 / US2) — count-neutral edits MUST stay green
# ---------------------------------------------------------------------------
def test_citation_edit_ignored(monkeypatch):
    """A citation-string-only edit (the real #333 shape — mitre-atlas 36->36,
    nist-ai-rmf 72->72) leaves every ``(id, out_of_scope)`` fingerprint unchanged,
    so the guard stays GREEN. A guard that false-reds here is worse than no guard
    (NFR-001 / FR-003 / US-2)."""
    sidecar = _sidecar_for(monkeypatch, BASELINE_RECORDS)
    mutated = _clone(BASELINE_RECORDS)
    # Change only a non-fingerprint field; id + out_of_scope untouched.
    mutated["mitre-atlas"][0]["references"] = ["https://example.org/new-citation"]
    mutated["nist-ai-rmf"][0]["description"] = "reworded description, same id"
    _install(monkeypatch, mutated)
    drift = guard.find_drift(guard.all_fingerprints(), sidecar)
    assert drift == [], f"count-neutral #333-class edit must not drift, got {drift}"


def test_non_member_change_ignored(monkeypatch):
    """A change to a non-``ORDERED_FRAMEWORKS`` catalog (e.g. ``nist-ai-600-1``,
    the #184 Surface-C catalog) is ignored — only members are CA-coupled (US-2)."""
    assert "nist-ai-600-1" not in guard.ORDERED_FRAMEWORKS
    sidecar = _sidecar_for(monkeypatch, BASELINE_RECORDS)
    live = guard.all_fingerprints()
    # The guard's target set is exactly ORDERED_FRAMEWORKS — a non-member never
    # appears in the live map, so a non-member edit cannot move the guard.
    assert "nist-ai-600-1" not in live
    assert guard.find_drift(live, sidecar) == []


def test_clean_tree_passes(monkeypatch):
    """A clean synthetic tree (live == sidecar) exits with no drift (SC-001 clean)."""
    sidecar = _sidecar_for(monkeypatch, BASELINE_RECORDS)
    assert guard.find_drift(guard.all_fingerprints(), sidecar) == []


# ---------------------------------------------------------------------------
# 4. Future-member coverage (T011 / US4) — dynamic, zero guard-code change
# ---------------------------------------------------------------------------
def test_future_member_covered_dynamically(monkeypatch):
    """Adding a 6th member to ``ORDERED_FRAMEWORKS`` extends coverage with no
    guard-code edit (FR-004): ``all_fingerprints`` iterates the tuple at runtime,
    and the new member participates in fail-closed drift detection."""
    extended = _clone(BASELINE_RECORDS)
    extended["future-framework"] = [
        {"id": "FF-001"},
        {"id": "FF-002", "out_of_scope": True},
    ]
    _install(monkeypatch, extended)
    monkeypatch.setattr(guard, "ORDERED_FRAMEWORKS", tuple(extended.keys()))

    live = guard.all_fingerprints()
    assert "future-framework" in live  # fingerprinted automatically (no code change)

    # A sidecar with no entry for the new member ⇒ drift (fail-closed): a second
    # silent-gap class cannot open for a future member.
    sidecar_without_new = {
        "frameworks": {fw: live[fw] for fw in live if fw != "future-framework"}
    }
    assert "future-framework" in guard.find_drift(live, sidecar_without_new)
