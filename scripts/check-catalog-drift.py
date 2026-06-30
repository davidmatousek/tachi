#!/usr/bin/env python3
"""check-catalog-drift.py — ORDERED_FRAMEWORKS catalog-drift CI guard (Feature 329).

The 6-PDF byte-identity suite (`tests/scripts/test_backward_compatibility.py`)
byte-compares committed Coverage-Attestation (CA) page baselines, but it is wired
into no CI workflow — so when an `ORDERED_FRAMEWORKS` member catalog changes its
render-coupled record set without the 6 CA baselines being regenerated, the suite
goes *silently red on main* (the F-186 → F-185 path; KB Entry 15).

This guard closes that gap **without rendering anything**. For every live
`ORDERED_FRAMEWORKS` member it recomputes a deterministic *render-coupled
fingerprint* — the ordered list of `(id, out_of_scope)` records, in both the raw
and in-scope partitions — by **reusing the renderer's own record loader**
(`_load_framework_yaml_records`), so its notion of "what the CA page depends on"
is the renderer's by construction. It compares each fingerprint against a committed
**sidecar** (`examples/ca-baseline-fingerprints.json`) that is emitted as the final
step of the CA-baseline regeneration script — so a stale sidecar ≡ stale baselines
and the expected fingerprints cannot be advanced without a real regen (cheat-
resistance; OQ-1 / Risk-1).

Determinism boundary (NFR-001): the guard's result depends ONLY on the YAML
in-scope record fingerprints and the committed sidecar — never on Typst version,
fonts, platform, or wall-clock. Zero rendering, zero network in this path. This is
the single property that justifies shipping (b) the fingerprint guard over (a)
wiring the full byte-identity suite into CI.

Modes (added in T005/T006):
    --check   (default) compare live fingerprints against the sidecar; exit 1 on drift.
    --emit              (re)write the sidecar from the live tree — invoked ONLY as the
                        final step of scripts/regenerate-ca-baselines.sh, never by hand.

See specs/329-ordered-frameworks-ci-guard/contracts/sidecar.contract.md for the
fingerprint algorithm, the sidecar schema, and the regen-emission contract.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

# --- Paths (resolved from this file; the guard renders nothing) ---------------
REPO_ROOT = Path(__file__).resolve().parent.parent
EXTRACT_SCRIPT = REPO_ROOT / "scripts" / "extract-report-data.py"
SIDECAR_PATH = REPO_ROOT / "examples" / "ca-baseline-fingerprints.json"

# Provenance recorded in the sidecar; the guard does NOT depend on it for the
# comparison (it renders nothing — NFR-001). Mirrors the byte-identity suite's
# pinned epoch so the sidecar self-documents the tree the baselines were rendered against.
SOURCE_DATE_EPOCH = "1700000000"
SIDECAR_GENERATED_BY = (
    "scripts/regenerate-ca-baselines.sh "
    "(do not hand-edit; advance only by re-running the regen)"
)


def _load_extract_module():
    """Import the hyphenated ``scripts/extract-report-data.py`` via importlib.

    The established repo reuse pattern (see
    ``tests/scripts/test_attack_chain_extraction.py``): the renderer's module is
    not importable by name (hyphen), so load it from its file path. We reuse its
    ``_load_framework_yaml_records`` loader and ``ORDERED_FRAMEWORKS`` tuple rather
    than re-implementing the YAML walk (FR-001 / code-economy rung 2) — the guard's
    coupling notion is then the renderer's *by construction*.

    The scripts dir is prepended to ``sys.path`` first so the module's own sibling
    imports (e.g. ``tachi_parsers``) resolve. ``_load_framework_yaml_records``
    imports ``yaml`` lazily inside its body, so this exec does not require pyyaml
    at module-load time (the stdlib-only module-load invariant holds).
    """
    scripts_dir = str(REPO_ROOT / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    spec = importlib.util.spec_from_file_location(
        "extract_report_data", str(EXTRACT_SCRIPT)
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_extract = _load_extract_module()

# Module-level bindings so tests can monkeypatch the loader (synthetic record
# sets) or the framework tuple (the FR-004 dynamic-member case) and clear the
# loader's ``@functools.lru_cache`` via ``cache_clear()`` (FR-007 / Risk-3).
ORDERED_FRAMEWORKS = _extract.ORDERED_FRAMEWORKS
_load_framework_yaml_records = _extract._load_framework_yaml_records


# --- Fingerprint core (T004 / FR-001) -----------------------------------------
def _canonical(record):
    """Project a record to its render-coupled identity ``[id, bool(out_of_scope)]``.

    C-2 (Architect): mirror the loader's ``isinstance(r, dict)`` guard so a
    malformed non-dict top-level record fails **closed** to a deterministic marker
    (detected downstream as drift) rather than raising ``AttributeError`` on
    ``.get()``. Note the loader does NOT isinstance-filter the *raw* record set, so
    a non-dict can reach this function in raw mode — it must not crash the guard.
    """
    if isinstance(record, dict):
        return [record.get("id"), bool(record.get("out_of_scope", False))]
    return ["<non-dict>", repr(record)]


def _serialize(seq):
    """Deterministic serialization of an ordered record sequence.

    ``ensure_ascii=False`` + compact separators; order is **preserved, never
    sorted** — YAML document order is what renders onto the CA page, so sorting
    would mask a reorder that changes the rendered rows.
    """
    return json.dumps(
        [_canonical(r) for r in seq],
        ensure_ascii=False,
        separators=(",", ":"),
    )


def _sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def member_fingerprint(fw):
    """Compute the render-coupled fingerprint for one framework.

    ``raw_fingerprint`` digests ALL records (catches add/remove and any
    ``out_of_scope`` flip — HIGH-3). ``in_scope_fingerprint`` digests the in-scope
    partition (catches in-scope add/remove and ID rename/swap at constant count —
    HIGH-2). Counts are retained for the human-readable failure summary only; the
    comparison keys on the fingerprints, never the bare counts (so the count-neutral
    #333 class stays green — FR-003).
    """
    records = _load_framework_yaml_records(fw)
    in_scope = _load_framework_yaml_records(fw, in_scope_only=True)
    return {
        "raw_fingerprint": _sha256(_serialize(records)),
        "in_scope_fingerprint": _sha256(_serialize(in_scope)),
        "raw_count": len(records),
        "in_scope_count": len(in_scope),
    }


def all_fingerprints():
    """Fingerprint every live ``ORDERED_FRAMEWORKS`` member.

    Derives its target set from the tuple at runtime (FR-004): adding a future
    member extends coverage with zero guard-code change.
    """
    return {fw: member_fingerprint(fw) for fw in ORDERED_FRAMEWORKS}


# --- Sidecar I/O (T005 read / T006 write) -------------------------------------
class SidecarError(Exception):
    """The sidecar is missing, unparseable, or structurally invalid.

    Fail-closed (FR-008 / Risk-5): the ``--check`` path converts any of these into
    a non-zero exit, never a pass — so deleting or truncating the sidecar cannot
    silence the guard.
    """


def read_sidecar(path=None):
    """Load and structurally validate the sidecar; fail closed on any problem.

    Raises :class:`SidecarError` on a missing file, a JSON parse/read error, or a
    missing/wrong-typed ``frameworks`` map. Per-member completeness (a live member
    absent from ``frameworks``) is enforced later in :func:`find_drift`, also fail-
    closed.

    ``path`` defaults to the module-level :data:`SIDECAR_PATH`, resolved at call
    time (not bound at definition) so a reassignment of the global is honored.
    """
    path = Path(SIDECAR_PATH if path is None else path)
    if not path.exists():
        raise SidecarError(
            f"sidecar not found: {path} "
            f"(emit it via scripts/regenerate-ca-baselines.sh)"
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise SidecarError(f"sidecar unparseable ({path}): {exc}")
    if not isinstance(data, dict) or not isinstance(data.get("frameworks"), dict):
        raise SidecarError(
            f"sidecar malformed — missing or non-object 'frameworks' map ({path})"
        )
    return data


# --- Drift determination (T005 / FR-003 / FR-008) -----------------------------
def find_drift(live, sidecar):
    """Frameworks whose live fingerprint diverges from the recorded sidecar.

    A live member **absent** from the sidecar's ``frameworks`` map is drift (fail-
    closed, FR-008): a member with no recorded expectation must redden, not pass.
    The comparison keys on the raw OR in-scope **fingerprint** (FR-003) — never a
    file diff — so a count-neutral edit that leaves both fingerprints unchanged
    stays green (the #333 class).
    """
    recorded = sidecar["frameworks"]
    drift = []
    for fw, live_fp in live.items():
        expected = recorded.get(fw)
        if (
            expected is None
            or live_fp["raw_fingerprint"] != expected.get("raw_fingerprint")
            or live_fp["in_scope_fingerprint"] != expected.get("in_scope_fingerprint")
        ):
            drift.append(fw)
    return drift


_REMEDIATION = (
    "Fix: regenerate the 6 CA baselines AND emit the sidecar:\n"
    "  scripts/regenerate-ca-baselines.sh        "
    "# see specs/185-cwe-catalog-expansion/contracts/baseline-regen.contract.md "
    "(ADR-037 D-9)"
)


def format_failure(drift, live, sidecar):
    """Self-evident failure message for stderr (FR-006).

    Per drifted framework: names it, shows expected→actual counts and 8-char
    fingerprint prefixes for both partitions, then the single remediation entry
    point. Names **all** offending frameworks (the two-members-drift edge case),
    not just the first.
    """
    recorded = sidecar["frameworks"]
    lines = []
    for fw in drift:
        live_fp = live[fw]
        expected = recorded.get(fw)
        if expected is None:
            lines.append(
                f"catalog-drift: {fw} is a live ORDERED_FRAMEWORKS member with no "
                f"sidecar entry — the sidecar is stale (fail-closed)."
            )
            continue
        lines.append(
            f"catalog-drift: {fw} render-coupled fingerprint changed without a "
            f"CA-baseline regen."
        )
        lines.append(
            f"  in_scope: {expected.get('in_scope_count')} -> "
            f"{live_fp['in_scope_count']} records  "
            f"(fingerprint {str(expected.get('in_scope_fingerprint'))[:8]}… -> "
            f"{live_fp['in_scope_fingerprint'][:8]}…)"
        )
        lines.append(
            f"  raw:      {expected.get('raw_count')} -> "
            f"{live_fp['raw_count']} records  "
            f"(fingerprint {str(expected.get('raw_fingerprint'))[:8]}… -> "
            f"{live_fp['raw_fingerprint'][:8]}…)"
        )
    lines.append(_REMEDIATION)
    return "\n".join(lines)


# --- CLI ----------------------------------------------------------------------
def _run_check():
    """``--check`` (default, the CI gate): exit 1 on drift, 0 on a clean tree."""
    try:
        sidecar = read_sidecar()
    except SidecarError as exc:
        print(f"catalog-drift: {exc}", file=sys.stderr)
        print(_REMEDIATION, file=sys.stderr)
        return 1
    live = all_fingerprints()
    drift = find_drift(live, sidecar)
    if drift:
        print(format_failure(drift, live, sidecar), file=sys.stderr)
        return 1
    return 0


def _run_emit():
    """``--emit``: (re)write the sidecar from the live tree.

    Invoked ONLY as the final step of ``scripts/regenerate-ca-baselines.sh`` — never
    by hand (OQ-1 cheat-resistance / Risk-1). Because the regen script re-renders the
    6 baselines immediately before this call, the emitted fingerprints are a genuine
    byproduct of a real regen: the expected values cannot be advanced without one.

    Writes deterministic JSON (``sort_keys=True``, ``indent=2``, trailing newline) so
    the committed artifact is byte-stable across emits on an unchanged tree.
    """
    payload = {
        "_generated_by": SIDECAR_GENERATED_BY,
        "source_date_epoch": SOURCE_DATE_EPOCH,
        "frameworks": all_fingerprints(),
    }
    SIDECAR_PATH.write_text(
        json.dumps(payload, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"catalog-drift: wrote sidecar {SIDECAR_PATH} "
        f"({len(payload['frameworks'])} frameworks)",
        file=sys.stderr,
    )
    return 0


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(
        prog="check-catalog-drift.py",
        description=(
            "Fail when an ORDERED_FRAMEWORKS member's render-coupled fingerprint "
            "drifts from the committed sidecar without a CA-baseline regen."
        ),
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--check",
        action="store_true",
        help="(default) compare live fingerprints to the sidecar; exit 1 on drift",
    )
    mode.add_argument(
        "--emit",
        action="store_true",
        help="(re)write the sidecar from the live tree — regen-script use ONLY",
    )
    args = parser.parse_args(argv)

    if args.emit:
        return _run_emit()
    return _run_check()


if __name__ == "__main__":
    sys.exit(main())
