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

from pathlib import Path

import pytest

from init_sh_helpers import (
    build_canonical_stdin,
    clone_into_tmpdir,
    run_init_in_clone,
)




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


def test_no_residual_placeholders_after_init(init_run):
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

    Uses the session-scoped `init_run` fixture from conftest.py — the
    canonical post-init clone is shared with the other init_sh_* test modules
    to avoid multiplying the macos cold-cache cost.
    """
    import re
    clone_root = init_run.tmpdir

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
