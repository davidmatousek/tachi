"""Test-4: post-init `.aod/memory/constitution.md` byte-equals the clean template.

Per F-248 FR-008 / AC-8.3, after `scripts/init.sh` completes, the post-F-1
constitution cleanup uses `cp .aod/templates/constitution-clean.md
.aod/memory/constitution.md` (replacing the pre-F-1 sed cleanup). Both files
go through the substitution loop in the same init run, so their bytes
should match exactly after the cp.

Test-first per Constitution VI: this test lands BEFORE T032 (sed → cp
migration). Pre-F-1, the sed-cleaned constitution.md MAY differ from the
yet-to-exist constitution-clean.md template (since the template doesn't
exist pre-merge in tachi). Post-Stream-1+T032, the two files are byte-
identical because both flow through the same substitution loop and the cp
is the cleanup step.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from init_sh_helpers import build_canonical_stdin, clone_into_tmpdir, run_init_in_clone


@pytest.fixture(scope="module")
def init_run(tmp_path_factory: pytest.TempPathFactory):
    """Module-scoped: run init.sh once with canonical inputs."""
    tmpdir = tmp_path_factory.mktemp("init_sh_constitution")
    clone_root = clone_into_tmpdir(tmpdir)
    stdin_payload = build_canonical_stdin(clone_root)
    result = run_init_in_clone(clone_root, stdin_payload)
    if result.returncode != 0:
        pytest.fail(
            f"init.sh exited {result.returncode}; stderr tail:\n{result.stderr[-1500:]}"
        )
    return result


def test_constitution_byte_equals_clean_template(init_run):
    """The post-init constitution byte-equals .aod/templates/constitution-clean.md.

    Both files pass through the substitution loop with the same canonical
    placeholder values. After the cp step (T032), they MUST be byte-identical.
    Pre-F-1 (sed-cleanup path) the two files diverge because the clean
    template either does not exist or is regenerated independently; the test
    fails there as expected for test-first.
    """
    clone_root = init_run.tmpdir
    constitution = clone_root / ".aod" / "memory" / "constitution.md"
    template_clean = clone_root / ".aod" / "templates" / "constitution-clean.md"

    assert constitution.is_file(), (
        f"post-init constitution missing: {constitution}"
    )
    assert template_clean.is_file(), (
        f"clean template missing: {template_clean} "
        "(should ship in repo as part of F-1 deliverable)"
    )

    constitution_bytes = constitution.read_bytes()
    template_bytes = template_clean.read_bytes()
    assert constitution_bytes == template_bytes, (
        f"byte-comparison failed:\n"
        f"  constitution length: {len(constitution_bytes)}\n"
        f"  template length: {len(template_bytes)}\n"
        f"  first divergence (truncated): "
        f"{_first_divergence(constitution_bytes, template_bytes)}"
    )


def _first_divergence(a: bytes, b: bytes, context: int = 60) -> str:
    """Return a short string describing the first byte where a ≠ b."""
    n = min(len(a), len(b))
    for i in range(n):
        if a[i] != b[i]:
            lo = max(0, i - context)
            hi = min(n, i + context)
            return f"@offset {i}: actual={a[lo:hi]!r} | template={b[lo:hi]!r}"
    if len(a) != len(b):
        return f"length differs: actual={len(a)} template={len(b)}"
    return "no divergence detected (this is unexpected)"
