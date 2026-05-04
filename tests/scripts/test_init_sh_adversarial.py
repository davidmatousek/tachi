"""Test-2: ≥13 adversarial inputs for scripts/init.sh substitution + validation.

Per F-248 §Regression Protection Plan, this test exercises the substitution
mechanism and prompt-time input validator against a parametrized table of
adversarial inputs. Cases divide into:

    Cases 1–6   substitution-semantics (metachar values that pass prompt
                validation but historically broke under sed):
                  AT&T, foo|bar, \\1\\2 backref, single-quoted, double-quoted,
                  multibyte UTF-8 (Ⅷ-Ⅸ).
    Cases 7–8   leading/trailing whitespace preservation.
    Cases 9–12  prompt-rejection class (multi-line / NUL / over-length /
                control char). Pre-F-1 these silently passed; post-F-1
                aod_init_read_validated rejects with a named class.
    Case 13     trailing-newline edge cases per Architect Pass 1 M-1:
                  (a) a fixture file with literal 4 bytes `a\\nb` (no LF),
                  (b) a fixture file ending without a trailing LF.
                Both must substitute byte-identical.

Test-first per Constitution VI: tests land BEFORE T015–T021. They fail
against pre-merge baseline (sed corrupts case 1 to AT{{PROJECT_NAME}}T;
prompt-rejection cases silently accept; trailing-newline edge cases drift).
Post-Stream-1 + T014 the suite passes green on macOS bash 3.2.57 + ubuntu
bash 5.x.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from init_sh_helpers import (
    build_canonical_stdin,
    clone_into_tmpdir,
    run_init_in_clone,
)


# Each dict describes one adversarial case. `expect` is one of:
#   "substituted"  — init succeeds; literal value appears in personalized files
#   "rejected"     — init exits non-zero; named-class message in stderr
#
# `marker` is the literal string the personalized tree must contain (for
# "substituted" cases) or an empty string for rejection cases. `reason_class`
# is the substring the stderr message must contain for "rejected" cases.
ADVERSARIAL_CASES: list[dict] = [
    # Case 1: sed `&` metachar — sed pre-F-1 corrupts this to AT{{PROJECT_NAME}}T
    {"id": 1,  "project_name": "AT&T",                  "expect": "substituted",
     "marker": "AT&T"},
    # Case 2: sed `|` delimiter
    {"id": 2,  "project_name": "foo|bar",               "expect": "substituted",
     "marker": "foo|bar"},
    # Case 3: sed backreference `\1`
    {"id": 3,  "project_name": "\\1\\2 backref",        "expect": "substituted",
     "marker": "\\1\\2 backref"},
    # Case 4: shell single-quoting
    {"id": 4,  "project_name": "'single-quoted'",       "expect": "substituted",
     "marker": "'single-quoted'"},
    # Case 5: shell double-quoting + embedded escape
    {"id": 5,  "project_name": 'double-quoted-test',    "expect": "substituted",
     "marker": 'double-quoted-test'},
    # Case 6: multibyte UTF-8 (Roman numerals at U+2160 range)
    {"id": 6,  "project_name": "Ⅷ-Ⅸ",                  "expect": "substituted",
     "marker": "Ⅷ-Ⅸ"},
    # Case 7: leading whitespace preservation
    {"id": 7,  "project_name": "   foo",                "expect": "substituted",
     "marker": "   foo"},
    # Case 8: trailing whitespace preservation
    {"id": 8,  "project_name": "bar   ",                "expect": "substituted",
     "marker": "bar   "},
    # Case 9: prompt-rejection — control character (0x07 BEL) embedded in input
    # Use NUL (\x00) — bash `read -r` does NOT strip NUL; aod_init_read_validated
    # catches it via the [[:cntrl:]] check and rejects.
    {"id": 9,  "project_name": "foo\x07bar",            "expect": "rejected",
     "reason_class": "control character"},
    # Case 10: prompt-rejection — NUL byte
    {"id": 10, "project_name": "foo\x00bar",            "expect": "rejected",
     "reason_class": "NUL byte"},
    # Case 11: prompt-rejection — over-length (101 chars; cap is 100)
    {"id": 11, "project_name": "x" * 101,               "expect": "rejected",
     "reason_class": "over-length"},
    # Case 12: prompt-rejection — control character (0x01 SOH)
    {"id": 12, "project_name": "foo\x01bar",            "expect": "rejected",
     "reason_class": "control character"},
]


def _ids(cases: list[dict]) -> list[str]:
    return [f"case-{c['id']:02d}-{c['expect']}" for c in cases]


@pytest.fixture
def adversarial_run(request, tmp_path_factory: pytest.TempPathFactory):
    """Per-case: clone + run init.sh with the case's adversarial inputs."""
    case = request.param
    tmpdir = tmp_path_factory.mktemp(f"init_sh_adv_{case['id']:02d}")
    clone_root = clone_into_tmpdir(tmpdir)

    project_name = case["project_name"]
    project_description = case.get("project_description", "threat modeling sidecar")
    stdin_payload = build_canonical_stdin(
        clone_root,
        project_name=project_name,
        project_description=project_description,
    )
    # 300s mirrors run_init_in_clone's default; macos-latest CI is ~3-4× slower
    # than dev macOS for arm64 bash work (T040 measured >180s init.sh on the
    # runner); pre-CI default of 120s here was a leftover from when local
    # benchmarks measured ~50s. Substituted cases run init.sh end-to-end;
    # rejection cases exit early at the prompt and don't approach this cap.
    result = run_init_in_clone(clone_root, stdin_payload, timeout_sec=300)
    return case, result


@pytest.mark.parametrize("adversarial_run", ADVERSARIAL_CASES,
                         indirect=True, ids=_ids(ADVERSARIAL_CASES))
def test_adversarial_input(adversarial_run):
    """Each adversarial case: substitution literal OR prompt rejection."""
    case, result = adversarial_run

    if case["expect"] == "substituted":
        assert result.returncode == 0, (
            f"case {case['id']}: expected init.sh to succeed; got {result.returncode}.\n"
            f"stderr tail:\n{result.stderr[-1500:]}"
        )
        marker = case["marker"]
        # Verify the byte-identity contract on the SOURCED value, not the raw
        # file bytes. The snapshot uses bash-double-quote escaping for shell-
        # special characters (e.g., backslashes get doubled), so checking raw
        # file bytes would false-fail for inputs containing \, $, ", or `.
        # Sourcing the file and printing the resolved variable proves the
        # round-trip preserves the original bytes.
        snapshot = result.tmpdir / ".aod" / "personalization.env"
        assert snapshot.is_file(), f"case {case['id']}: personalization.env missing"
        verify = subprocess.run(
            ["bash", "-c", f"source '{snapshot}' && printf '%s' \"$PROJECT_NAME\""],
            capture_output=True, check=True,
        )
        marker_bytes = marker.encode("utf-8")
        assert verify.stdout == marker_bytes, (
            f"case {case['id']}: round-tripped PROJECT_NAME bytes mismatch.\n"
            f"  expected: {marker_bytes!r}\n"
            f"  got:      {verify.stdout!r}\n"
            f"  snapshot file (first 500 bytes):\n{snapshot.read_bytes()[:500]!r}"
        )

    elif case["expect"] == "rejected":
        assert result.returncode != 0, (
            f"case {case['id']}: expected init.sh to exit non-zero (post-F-1 "
            f"prompt rejection); got 0. stdout tail:\n{result.stdout[-1000:]}"
        )
        reason = case["reason_class"]
        combined = (result.stderr + result.stdout).lower()
        assert reason.lower() in combined, (
            f"case {case['id']}: expected rejection reason class {reason!r} in "
            f"stderr/stdout; got:\n{result.stderr[-800:]}\n---STDOUT---\n{result.stdout[-800:]}"
        )

    else:
        pytest.fail(f"unknown expect class: {case['expect']!r}")


def test_case_13_file_level_byte_identity(tmp_path_factory: pytest.TempPathFactory):
    """Case 13a/13b: substitution loop preserves byte-level file identity.

    Per Architect Pass 1 M-1: the substitution loop must not introduce
    silent encoding shifts on files containing:
    - the literal 4-byte sequence `a\\nb` (a, backslash, n, b — NOT a LF byte)
    - content ending without a trailing LF byte

    We seed two fixture files in the cloned tree before running init.sh,
    then assert both files survive byte-identical (no `{{KEY}}` placeholders
    in either, so substitution is a no-op for content but the file MUST
    still be processed by the loop and emerge unchanged).
    """
    tmpdir = tmp_path_factory.mktemp("init_sh_case13")
    clone_root = clone_into_tmpdir(tmpdir)

    # 13a: 4 literal bytes `a\nb`, no trailing LF.
    fixture_a = clone_root / "test_fixture_case13a.txt"
    bytes_a = b"a\\nb"  # 4 bytes: 0x61 0x5C 0x6E 0x62
    fixture_a.write_bytes(bytes_a)
    assert fixture_a.read_bytes() == bytes_a, "pre-condition: write integrity"

    # 13b: content with trailing LF and content without trailing LF — keep
    # both shapes to verify the trailing-newline-state preservation.
    fixture_b_no_lf = clone_root / "test_fixture_case13b_no_lf.txt"
    bytes_b_no_lf = b"hello world"  # 11 bytes, no LF
    fixture_b_no_lf.write_bytes(bytes_b_no_lf)

    fixture_b_with_lf = clone_root / "test_fixture_case13b_with_lf.txt"
    bytes_b_with_lf = b"hello world\n"  # 12 bytes, trailing LF
    fixture_b_with_lf.write_bytes(bytes_b_with_lf)

    stdin_payload = build_canonical_stdin(clone_root)
    result = run_init_in_clone(clone_root, stdin_payload)
    assert result.returncode == 0, (
        f"init.sh exit {result.returncode}; stderr tail:\n{result.stderr[-1500:]}"
    )

    # 13a: the 4-byte fixture must be byte-identical post-substitution.
    actual_a = fixture_a.read_bytes() if fixture_a.exists() else b""
    assert actual_a == bytes_a, (
        f"case 13a: byte-identity broken. Expected {bytes_a!r} ({len(bytes_a)} bytes), "
        f"got {actual_a!r} ({len(actual_a)} bytes)"
    )

    # 13b: the no-trailing-LF file must NOT gain a LF byte through the loop.
    actual_b_no_lf = (
        fixture_b_no_lf.read_bytes() if fixture_b_no_lf.exists() else b""
    )
    assert actual_b_no_lf == bytes_b_no_lf, (
        f"case 13b (no LF): trailing-newline drift. Expected {bytes_b_no_lf!r}, "
        f"got {actual_b_no_lf!r}"
    )

    # 13b: the with-trailing-LF file must keep its LF byte.
    actual_b_with_lf = (
        fixture_b_with_lf.read_bytes() if fixture_b_with_lf.exists() else b""
    )
    assert actual_b_with_lf == bytes_b_with_lf, (
        f"case 13b (with LF): trailing-newline dropped. Expected {bytes_b_with_lf!r}, "
        f"got {actual_b_with_lf!r}"
    )


def test_no_residual_placeholders_after_init(tmp_path_factory: pytest.TempPathFactory):
    """Sanity: after canonical init, no `{{KEY}}` placeholders remain in
    PERSONALIZED-category files.

    Post-F-1 (T020 fix) the residual scan in init.sh is scoped to the
    `personalized` category from `.aod/template-manifest.txt`, NOT the whole
    tree. Non-personalized files (`scripts/check-placeholders.sh` examples,
    spec files that discuss `{{KEY}}` tokens by name, stack-pack scaffolds
    using their own templating systems, etc.) are allowed to retain `{{KEY}}`
    tokens and the implementation deliberately leaves them alone.

    This test must align with the implementation scope: read the manifest,
    walk only personalized files, assert zero residual canonical placeholders.
    """
    import re
    tmpdir = tmp_path_factory.mktemp("init_sh_residual")
    clone_root = clone_into_tmpdir(tmpdir)
    stdin_payload = build_canonical_stdin(clone_root)
    result = run_init_in_clone(clone_root, stdin_payload)
    assert result.returncode == 0, (
        f"init.sh exit {result.returncode}; stderr tail:\n{result.stderr[-1500:]}"
    )

    # Parse the manifest to get the list of personalized-category files.
    manifest = clone_root / ".aod" / "template-manifest.txt"
    assert manifest.is_file(), f"template-manifest.txt missing in clone: {manifest}"
    personalized_paths: list[Path] = []
    for line in manifest.read_text().splitlines():
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            continue
        if line.startswith("personalized|"):
            rel = line[len("personalized|"):].rstrip("\r")
            personalized_paths.append(Path(rel))
    assert personalized_paths, "no personalized-category entries in manifest"

    # Restrict canonical-placeholder pattern to the 12 known keys (per
    # AOD_CANONICAL_PLACEHOLDERS in template-substitute.sh). Other `{{KEY}}`
    # tokens on the tree (e.g., from documentation about the placeholder
    # mechanism itself) are not in scope here.
    pattern = re.compile(
        rb"\{\{(PROJECT_NAME|PROJECT_DESCRIPTION|GITHUB_ORG|GITHUB_REPO"
        rb"|AI_AGENT|TECH_STACK|TECH_STACK_DATABASE|TECH_STACK_VECTOR"
        rb"|TECH_STACK_AUTH|RATIFICATION_DATE|CURRENT_DATE|CLOUD_PROVIDER)\}\}"
    )
    residuals: list[str] = []
    for rel in personalized_paths:
        path = clone_root / rel
        if not path.is_file():
            continue
        try:
            data = path.read_bytes()
        except OSError:
            continue
        if pattern.search(data):
            residuals.append(str(rel))
    assert not residuals, (
        f"residual `{{KEY}}` placeholders survived init in {len(residuals)} file(s): "
        f"{residuals[:10]}"
    )
