"""Offline parity + classifier tests for the citation link-rot checker (Feature #183).

**This module is network-free by mandate (NFR-001).** Importing it AND running
every test in it opens NO outbound socket, resolves NO DNS, and spawns NO
subprocess — ever. The checker under test
(``scripts/check-citation-urls.py``) confines all network code to
``classify_url`` / ``HostThrottler.fetch`` and all ``gh`` subprocess calls to
``manage_tracking_issue``; both are reachable only from ``main()`` and never run
at import. The tests here either (a) install socket/DNS/subprocess guards and
assert the module imports cleanly with none firing, (b) re-derive the discovery
keyset purely from the YAML on disk, or (c) drive ``classify_url`` through a
stubbed transport with all sleeps monkeypatched to no-ops.

Tasks covered:
  * T009 — NFR-001 determinism-boundary test (SC-004): import opens no socket /
    resolves no DNS / spawns no subprocess.
  * T010 — FR-008 dual-surface offline parity guard (SC-008; architect
    CONCERN-1 + CONCERN-2): set-parity in BOTH directions between the checker's
    ``discover_urls`` keyset and the independently re-derived union of the two
    integrity surfaces (crosswalk ``citation`` + catalog ``url``).
  * T013 — classifier disposition matrix (SC-006): each HTTP scenario maps to
    the correct ``Verdict``, driven through a stubbed transport.
"""

import importlib.util
import re
import socket
import ssl  # noqa: F401  — pre-imported so the socket guard cannot break ssl.SSLSocket
import http.client  # noqa: F401  — pre-imported for the same reason
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


# =============================================================================
# Shared constants (mirror tests/schemas/test_taxonomy_integrity.py exactly)
# =============================================================================

REPO_ROOT = Path(__file__).resolve().parents[2]
TAXONOMY_DIR = REPO_ROOT / "schemas" / "taxonomy"
CHECKER_PATH = REPO_ROOT / "scripts" / "check-citation-urls.py"
TAXONOMY_GLOB = "schemas/taxonomy/*.yaml"

# Authoritative catalog list — identical to test_taxonomy_integrity.CATALOG_FILENAMES.
CATALOG_FILENAMES = [
    "owasp.yaml",
    "mitre-attack.yaml",
    "mitre-atlas.yaml",
    "nist-ai-rmf.yaml",
    "nist-ai-600-1.yaml",
    "cwe.yaml",
    "tachi-control-category.yaml",
    "tachi-stride-ai-category.yaml",
]

CROSSWALK_FILENAME = "crosswalk.yaml"

# Identical to test_taxonomy_integrity.URL_REGEX — the ^https?:// filter that
# both the integrity tests and the checker apply to drop repo-file-path values.
URL_REGEX = re.compile(r"^https?://")

# Catalogs whose ``url:`` fields are repo file-paths (not ^https?://) and must
# therefore contribute ZERO monitored URLs to both surfaces (CONCERN-2).
FILE_PATH_URL_CATALOGS = ("tachi-control-category.yaml", "tachi-stride-ai-category.yaml")

# Non-trivial-size floors so a silent ``url:``→``link:`` (or ``citation:``→…)
# field rename that zeroes a surface fails LOUDLY (a now-empty A==B would
# otherwise pass). Calibrated BELOW the true repo values (B1≈191, B2≈883) so the
# floors catch a zero-out, never a benign content edit. The architect CONCERN-1
# point: if a catalog ``url:`` were renamed, both B2 and A drop ~all URLs — the
# B2 floor turns that silent regression into a hard failure.
CROSSWALK_SURFACE_FLOOR = 150   # crosswalk ``citation`` URLs (deduped) — true ≈191
CATALOG_SURFACE_FLOOR = 600     # catalog ``url`` URLs (deduped)     — true ≈883


# =============================================================================
# Module loader (the checker filename is hyphenated → not import-able directly)
# =============================================================================

def _load_checker(module_name: str = "_citation_url_checker"):
    """Load ``scripts/check-citation-urls.py`` via importlib.

    The filename has hyphens, so ``import`` cannot reach it. We register the
    module in ``sys.modules`` BEFORE ``exec_module`` because the module defines
    frozen dataclasses, which resolve their qualified names against
    ``sys.modules`` during class creation.
    """
    spec = importlib.util.spec_from_file_location(module_name, str(CHECKER_PATH))
    assert spec is not None and spec.loader is not None, (
        f"could not build import spec for {CHECKER_PATH}"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def checker():
    """Load the checker module once and share it across this module's tests."""
    return _load_checker()


# =============================================================================
# Independent re-derivation of the two integrity surfaces (for T010)
# =============================================================================

def _crosswalk_citation_surface():
    """Surface B1 — every ``crosswalk.yaml`` edge ``citation`` matching ^https?://.

    This is EXACTLY what ``test_citation_shape()`` guards. Re-derived here from the
    YAML on disk (NOT via ``discover_urls``) so the parity test is a true
    cross-check rather than a tautology. The ^https?:// filter (CONCERN-2) drops
    any file-path citation identically to the checker.
    """
    with open(TAXONOMY_DIR / CROSSWALK_FILENAME, encoding="utf-8") as handle:
        edges = yaml.safe_load(handle)
    surface = set()
    for edge in edges:
        citation = edge.get("citation") if isinstance(edge, dict) else None
        if isinstance(citation, str) and URL_REGEX.match(citation):
            surface.add(citation)
    return surface


def _catalog_url_surface():
    """Surface B2 — every catalog record ``url`` matching ^https?://.

    This is EXACTLY what ``test_framework_yamls_load()`` validates (its
    ``_is_url_or_existing_file`` check on each record's ``url``). Re-derived
    independently from the YAML on disk. The ^https?:// filter (CONCERN-2) is
    applied UNIFORMLY, dropping the repo-file-path ``url:`` values in
    ``tachi-control-category.yaml`` / ``tachi-stride-ai-category.yaml`` exactly as
    the checker does. Returns ``(union_surface, per_catalog_counts)``.
    """
    surface = set()
    per_catalog = {}
    for name in CATALOG_FILENAMES:
        with open(TAXONOMY_DIR / name, encoding="utf-8") as handle:
            records = yaml.safe_load(handle)
        urls = set()
        for record in records:
            url = record.get("url") if isinstance(record, dict) else None
            if isinstance(url, str) and URL_REGEX.match(url):
                urls.add(url)
        per_catalog[name] = urls
        surface |= urls
    return surface, per_catalog


# =============================================================================
# Stubbed transport for the classifier matrix (T013) — no socket ever opens
# =============================================================================

class _FakeResponse:
    """A minimal stand-in for ``http.client.HTTPResponse`` / ``HTTPError``.

    The checker reads ``.status`` (falling back to ``.code``) and
    ``.headers.get("Location")`` / ``.headers.get("Retry-After")``. We expose
    both ``status`` and ``code`` (identical) and a plain-dict ``headers`` whose
    ``.get`` mirrors the response/HTTPError surface.
    """

    def __init__(self, status, headers=None):
        self.status = status
        self.code = status
        self.headers = dict(headers or {})


class _ScriptedFetch:
    """A scripted replacement for ``HostThrottler.fetch`` — the sole transport.

    Construct with a per-``(method, url)`` mapping of response *sequences* (a
    list popped left-to-right) and/or a default sequence. A value may be:
      * a ``_FakeResponse`` (or ``(status, headers)`` tuple) → returned as a response;
      * an ``Exception`` instance → raised (e.g. ``TimeoutError`` to simulate a
        timeout, exactly as ``urllib`` would surface a connection failure).

    Every call is recorded in ``self.calls`` so a test can assert the HEAD→GET
    fallback, redirect hops, and — crucially — that this fake was the ONLY
    transport used (no real socket opened).
    """

    def __init__(self, *, by_key=None, default=None):
        # by_key: {(method, url): [item, ...]}; default: [item, ...] fallback
        self._by_key = {k: list(v) for k, v in (by_key or {}).items()}
        self._default = list(default or [])
        self.calls = []

    def __call__(self, url, method, extra_headers=None):
        self.calls.append((method, url, dict(extra_headers or {})))
        key = (method, url)
        if key in self._by_key and self._by_key[key]:
            item = self._by_key[key].pop(0)
        elif self._default:
            item = self._default.pop(0)
        else:
            raise AssertionError(
                f"_ScriptedFetch: no scripted response for {method} {url!r} "
                f"(calls so far: {self.calls})"
            )
        if isinstance(item, BaseException):
            raise item
        if isinstance(item, tuple):
            status, headers = item
            return _FakeResponse(status, headers)
        return item


def _install_scripted_transport(checker, monkeypatch, scripted):
    """Wire a ``_ScriptedFetch`` in as ``HostThrottler.fetch`` and neuter sleeps.

    Monkeypatches ``HostThrottler.fetch`` (so no real ``urllib`` call happens),
    the module-level ``_backoff_sleep`` to a counting no-op (CRITICAL — otherwise
    transient retries sleep ~1+2 ≈ 3s), and ``time.sleep`` inside the module to a
    no-op (defensive, in case ``_honor_retry_after`` is ever reached). Returns a
    list whose length is the ``_backoff_sleep`` invocation count.
    """
    backoff_calls = []

    def _fake_fetch(self, url, method, extra_headers=None):
        return scripted(url, method, extra_headers)

    def _fake_backoff(attempt):
        backoff_calls.append(attempt)

    monkeypatch.setattr(checker.HostThrottler, "fetch", _fake_fetch, raising=True)
    monkeypatch.setattr(checker, "_backoff_sleep", _fake_backoff, raising=True)
    monkeypatch.setattr(checker.time, "sleep", lambda *_a, **_k: None, raising=True)
    return backoff_calls


def _make_throttler(checker):
    """Build a real ``HostThrottler`` instance (its ``fetch`` is monkeypatched).

    We still need a throttler object so ``classify_url(url, throttler)`` has a
    receiver; its ``fetch`` method is replaced before any test body runs, so the
    ThreadPoolExecutor it constructs is never used to open a socket. We shut it
    down at the end of each test via the returned object.
    """
    return checker.HostThrottler(
        global_concurrency=1,
        max_host_concurrency=1,
        politeness_ms=0,
        connect_timeout=1.0,
        read_timeout=1.0,
    )


# -----------------------------------------------------------------------------
# Hard socket/DNS/subprocess guards (shared by T009 and the T013 matrix)
# -----------------------------------------------------------------------------

class _NetworkGuardTripped(AssertionError):
    """Raised if any guarded network/subprocess primitive is invoked."""


def _install_network_guards():
    """Install guards that raise on ANY socket connect / DNS resolve / subprocess.

    Returns ``(originals, tripped)`` where ``originals`` is what ``_restore`` needs
    and ``tripped`` is a mutable list that records the name of any guard that
    fired (so a test can assert it stayed empty). ``socket``/``ssl``/
    ``http.client``/``subprocess`` MUST already be imported at module top so the
    stdlib's own ``ssl.SSLSocket(socket)`` class definition is not broken by the
    guard during a fresh import of the checker.
    """
    tripped = []
    originals = {
        "getaddrinfo": socket.getaddrinfo,
        "connect": socket.socket.connect,
        "create_connection": socket.create_connection,
        "subprocess_run": subprocess.run,
        "subprocess_popen": subprocess.Popen,
    }

    def _guard(name):
        def _tripwire(*_args, **_kwargs):
            tripped.append(name)
            raise _NetworkGuardTripped(f"network/subprocess guard fired: {name}")
        return _tripwire

    socket.getaddrinfo = _guard("socket.getaddrinfo")
    socket.socket.connect = _guard("socket.socket.connect")
    socket.create_connection = _guard("socket.create_connection")
    subprocess.run = _guard("subprocess.run")
    subprocess.Popen = _guard("subprocess.Popen")
    return originals, tripped


def _restore_network_guards(originals):
    """Restore the originals saved by ``_install_network_guards``."""
    socket.getaddrinfo = originals["getaddrinfo"]
    socket.socket.connect = originals["connect"]
    socket.create_connection = originals["create_connection"]
    subprocess.run = originals["subprocess_run"]
    subprocess.Popen = originals["subprocess_popen"]


# =============================================================================
# T009 — NFR-001 determinism-boundary test (SC-004)
# =============================================================================

def test_import_opens_no_socket_dns_or_subprocess():
    """Loading the checker module fires NO socket / DNS / subprocess guard (NFR-001).

    Installs hard guards on ``socket.getaddrinfo``, ``socket.socket.connect``,
    ``socket.create_connection``, ``subprocess.run`` and ``subprocess.Popen``,
    then loads the checker FRESH via importlib and asserts it imports cleanly with
    none of the guards firing. ``socket``/``ssl``/``http.client``/``subprocess``
    are pre-imported at module top so the guard cannot break stdlib's own
    ``ssl.SSLSocket(socket)`` definition. Originals are always restored.
    """
    originals, tripped = _install_network_guards()
    try:
        module = _load_checker("_citation_url_checker_guarded")
    finally:
        _restore_network_guards(originals)

    assert tripped == [], (
        f"importing the checker tripped network/subprocess guard(s): {tripped} "
        f"— all network/gh code MUST be deferred to runtime (NFR-001)"
    )
    assert module is not None, "checker module failed to load under network guards"


def test_network_and_subprocess_surface_is_deferred_not_executed(checker):
    """The network + subprocess entry points EXIST but are only reachable via main().

    Documents the determinism boundary (NFR-001): the module exposes the network
    surface (``classify_url`` / ``HostThrottler.fetch``) and the subprocess surface
    (``manage_tracking_issue``), yet importing the module (done by the ``checker``
    fixture, which loads it WITHOUT firing any guard — see the import test) ran
    none of them. We assert the callables are present (so the surface is real) and
    that the documented confinement holds: these are functions/methods, not
    import-time side effects.
    """
    # Network surface present...
    assert callable(checker.classify_url), "classify_url must be the network entry point"
    assert callable(checker.HostThrottler.fetch), "HostThrottler.fetch issues the request"
    # ...subprocess surface present...
    assert callable(checker.manage_tracking_issue), "manage_tracking_issue drives gh I/O"
    assert callable(getattr(checker, "_run_gh", None)), "_run_gh wraps subprocess.run"
    # ...and main() is the sole caller of both (it exists and is callable).
    assert callable(checker.main), "main() is the only runtime entry point"
    # The module-level _backoff_sleep exists and is the seam tests neutralize.
    assert callable(checker._backoff_sleep), "_backoff_sleep is the retry-sleep seam"
    # _NoRedirect is the manual-redirect handler used by the (deferred) opener.
    assert isinstance(checker._NoRedirect, type), "_NoRedirect must be a handler class"


# =============================================================================
# T010 — FR-008 dual-surface offline parity guard (SC-008; CONCERN-1 + CONCERN-2)
# =============================================================================

def test_discover_urls_set_parity_with_integrity_surfaces(checker):
    """``discover_urls`` keyset == UNION of the two integrity surfaces, both ways.

    This is the load-bearing FR-008 guard (architect CONCERN-1). Surfaces:
      * A  = checker's ``discover_urls(schemas/taxonomy/*.yaml)`` keyset — the URLs
             it will MONITOR.
      * B  = B1 ∪ B2, re-derived INDEPENDENTLY here (NOT via discover_urls):
          - B1 = every ``crosswalk.yaml`` edge ``citation`` matching ^https?://
                 (exactly what ``test_citation_shape()`` guards).
          - B2 = every catalog record ``url`` matching ^https?:// across all 8
                 ``CATALOG_FILENAMES`` (exactly what ``test_framework_yamls_load()``
                 guards).

    Field rule (encoded explicitly): ``crosswalk.yaml`` → ``citation``; every other
    ``schemas/taxonomy/*.yaml`` → ``url``. The ^https?:// filter is applied
    UNIFORMLY to B1 and B2 (CONCERN-2) so file-path ``url:`` values drop
    identically in the re-derivation AND in discover_urls.

    On failure the message shows ``A - B`` (URLs the checker monitors that NO
    integrity surface guards) and ``B - A`` (URLs an integrity surface guards that
    the checker would MISS). Parity must be EXACT — never loosen the assertion.
    """
    surface_a = set(checker.discover_urls(TAXONOMY_GLOB).keys())
    surface_b1 = _crosswalk_citation_surface()
    surface_b2, _per_catalog = _catalog_url_surface()
    surface_b = surface_b1 | surface_b2

    only_in_checker = surface_a - surface_b
    only_in_integrity = surface_b - surface_a
    assert surface_a == surface_b, (
        "FR-008 PARITY BREACH between checker discovery (A) and integrity "
        f"surfaces (B = crosswalk citation ∪ catalog url).\n"
        f"  |A|={len(surface_a)}  |B|={len(surface_b)} "
        f"(|B1 crosswalk citation|={len(surface_b1)}, |B2 catalog url|={len(surface_b2)})\n"
        f"  A - B (monitored but NO integrity surface guards) [{len(only_in_checker)}]: "
        f"{sorted(only_in_checker)[:20]}\n"
        f"  B - A (guarded but checker would MISS) [{len(only_in_integrity)}]: "
        f"{sorted(only_in_integrity)[:20]}"
    )


def test_integrity_surfaces_are_non_trivially_large():
    """Both re-derived surfaces are non-trivially large — guards CONCERN-1 zero-out.

    A silent field rename (e.g. catalog ``url:`` → ``link:``) would zero B2 *and*
    the checker's A simultaneously, leaving A==B vacuously true on an empty set.
    These floors turn that silent regression into a LOUD failure: the catalog
    ``url`` surface must stay >= CATALOG_SURFACE_FLOOR and the crosswalk
    ``citation`` surface >= CROSSWALK_SURFACE_FLOOR.
    """
    surface_b1 = _crosswalk_citation_surface()
    surface_b2, _per_catalog = _catalog_url_surface()
    assert len(surface_b2) >= CATALOG_SURFACE_FLOOR, (
        f"catalog ``url`` surface collapsed to {len(surface_b2)} "
        f"(floor {CATALOG_SURFACE_FLOOR}) — a ``url:`` field rename would zero this "
        f"AND the checker's monitored set; failing loudly per CONCERN-1"
    )
    assert len(surface_b1) >= CROSSWALK_SURFACE_FLOOR, (
        f"crosswalk ``citation`` surface collapsed to {len(surface_b1)} "
        f"(floor {CROSSWALK_SURFACE_FLOOR}) — a ``citation:`` field rename would "
        f"zero this AND the checker's monitored set; failing loudly per CONCERN-1"
    )


def test_file_path_url_catalogs_contribute_no_monitored_urls(checker):
    """The two file-path-``url`` catalogs contribute ZERO monitored URLs (CONCERN-2).

    ``tachi-control-category.yaml`` (8 file-path ``url:`` values) and
    ``tachi-stride-ai-category.yaml`` (11) carry NO ^https?:// urls, so the uniform
    filter must drop them identically in BOTH the re-derivation and in
    ``discover_urls``. We assert (a) each contributes an empty re-derived url set,
    and (b) none of their record ``url`` values appears in the checker's monitored
    keyset — so parity never regresses on them.
    """
    _surface_b2, per_catalog = _catalog_url_surface()
    surface_a = set(checker.discover_urls(TAXONOMY_GLOB).keys())

    for name in FILE_PATH_URL_CATALOGS:
        assert per_catalog[name] == set(), (
            f"{name}: expected ZERO url-shaped urls (all ``url:`` values are repo "
            f"file paths), got {sorted(per_catalog[name])}"
        )
        # Cross-check: read the raw file-path url values and confirm discover_urls
        # dropped every one of them (none leaked into the monitored set).
        with open(TAXONOMY_DIR / name, encoding="utf-8") as handle:
            records = yaml.safe_load(handle)
        raw_urls = {
            r.get("url") for r in records if isinstance(r, dict) and r.get("url")
        }
        leaked = raw_urls & surface_a
        assert leaked == set(), (
            f"{name}: file-path ``url:`` value(s) leaked into the monitored set "
            f"(CONCERN-2 filter regression): {sorted(leaked)}"
        )


# =============================================================================
# T013 — classifier disposition matrix (SC-006, offline, stubbed transport)
# =============================================================================

def test_status_200_is_healthy(checker, monkeypatch):
    """A final HEAD 200 → HEALTHY."""
    url = "https://example.test/ok"
    scripted = _ScriptedFetch(by_key={("HEAD", url): [(200, {})]})
    _install_scripted_transport(checker, monkeypatch, scripted)
    throttler = _make_throttler(checker)
    try:
        result = checker.classify_url(url, throttler)
    finally:
        throttler.shutdown()
    assert result.verdict is checker.Verdict.HEALTHY, result
    assert result.final_status == 200
    # Only the scripted fake was used as transport — no real socket opened.
    assert scripted.calls == [("HEAD", url, {})]


def test_redirect_301_then_200_is_healthy(checker, monkeypatch):
    """HEAD 301 (with Location) → HEAD 200 at the target → HEALTHY, final_url differs."""
    url = "https://example.test/old"
    target = "https://example.test/new"
    scripted = _ScriptedFetch(by_key={
        ("HEAD", url): [(301, {"Location": target})],
        ("HEAD", target): [(200, {})],
    })
    _install_scripted_transport(checker, monkeypatch, scripted)
    throttler = _make_throttler(checker)
    try:
        result = checker.classify_url(url, throttler)
    finally:
        throttler.shutdown()
    assert result.verdict is checker.Verdict.HEALTHY, result
    assert result.final_status == 200
    assert result.final_url == target, "final_url must record the post-redirect target"
    assert [m for (m, _u, _h) in scripted.calls] == ["HEAD", "HEAD"]


def test_status_404_is_link_rot(checker, monkeypatch):
    """A final HEAD 404 → LINK_ROT (confirmed rot)."""
    url = "https://example.test/gone"
    scripted = _ScriptedFetch(by_key={("HEAD", url): [(404, {})]})
    _install_scripted_transport(checker, monkeypatch, scripted)
    throttler = _make_throttler(checker)
    try:
        result = checker.classify_url(url, throttler)
    finally:
        throttler.shutdown()
    assert result.verdict is checker.Verdict.LINK_ROT, result
    assert result.final_status == 404


def test_status_410_is_link_rot(checker, monkeypatch):
    """A final HEAD 410 (Gone) → LINK_ROT (confirmed rot)."""
    url = "https://example.test/gone-for-good"
    scripted = _ScriptedFetch(by_key={("HEAD", url): [(410, {})]})
    _install_scripted_transport(checker, monkeypatch, scripted)
    throttler = _make_throttler(checker)
    try:
        result = checker.classify_url(url, throttler)
    finally:
        throttler.shutdown()
    assert result.verdict is checker.Verdict.LINK_ROT, result
    assert result.final_status == 410


def test_status_403_head_then_403_get_is_needs_review(checker, monkeypatch):
    """HEAD 403 → ranged-GET retry also 403 → NEEDS_REVIEW (never confirmed rot).

    403 ∈ _HEAD_RETRY_AS_GET, so the checker re-issues the same URL as a ranged
    GET; the GET also returns 403, and 403 ∈ _NEEDS_REVIEW_STATUSES → NEEDS_REVIEW.
    """
    url = "https://example.test/forbidden"
    scripted = _ScriptedFetch(by_key={
        ("HEAD", url): [(403, {})],
        ("GET", url): [(403, {})],
    })
    _install_scripted_transport(checker, monkeypatch, scripted)
    throttler = _make_throttler(checker)
    try:
        result = checker.classify_url(url, throttler)
    finally:
        throttler.shutdown()
    assert result.verdict is checker.Verdict.NEEDS_REVIEW, result
    assert result.final_status == 403
    # Confirms the HEAD→GET fallback fired.
    assert [m for (m, _u, _h) in scripted.calls] == ["HEAD", "GET"]


def test_status_429_is_needs_review(checker, monkeypatch):
    """A final HEAD 429 (Too Many Requests) → NEEDS_REVIEW."""
    url = "https://example.test/rate-limited"
    scripted = _ScriptedFetch(by_key={("HEAD", url): [(429, {})]})
    _install_scripted_transport(checker, monkeypatch, scripted)
    throttler = _make_throttler(checker)
    try:
        result = checker.classify_url(url, throttler)
    finally:
        throttler.shutdown()
    assert result.verdict is checker.Verdict.NEEDS_REVIEW, result
    assert result.final_status == 429


def test_status_500_every_attempt_is_transient_and_retries(checker, monkeypatch):
    """A 500 on every attempt → TRANSIENT after retries; _backoff_sleep called 2×.

    MAX_TRANSIENT_RETRIES=2 → 1 initial + 2 retries = 3 attempts. The detail string
    is annotated with the attempt count ("500 x3"), and the backoff sleep is
    invoked exactly twice (between the three attempts).
    """
    url = "https://example.test/server-error"
    # Need a response for each of the 3 attempts (HEAD only — 500 is not in the
    # HEAD-retry-as-GET set, so no GET fallback occurs).
    scripted = _ScriptedFetch(by_key={("HEAD", url): [(500, {}), (500, {}), (500, {})]})
    backoff_calls = _install_scripted_transport(checker, monkeypatch, scripted)
    throttler = _make_throttler(checker)
    try:
        result = checker.classify_url(url, throttler)
    finally:
        throttler.shutdown()
    assert result.verdict is checker.Verdict.TRANSIENT, result
    assert "x3" in result.detail, f"expected attempt-count annotation, got {result.detail!r}"
    assert "500" in result.detail, f"expected 500 token in detail, got {result.detail!r}"
    assert len(backoff_calls) == 2, (
        f"_backoff_sleep should fire on the 2 retries, fired {len(backoff_calls)}×"
    )
    assert [m for (m, _u, _h) in scripted.calls] == ["HEAD", "HEAD", "HEAD"]


def test_timeout_every_attempt_is_transient(checker, monkeypatch):
    """A timeout on every attempt → TRANSIENT with a "timeout" detail token.

    The fake transport raises ``TimeoutError`` for each attempt (exactly how a
    connection timeout surfaces). After retries are exhausted the verdict is
    TRANSIENT and the detail carries the ``timeout`` token.
    """
    url = "https://example.test/slow"
    scripted = _ScriptedFetch(by_key={
        ("HEAD", url): [TimeoutError("timed out"), TimeoutError("timed out"),
                        TimeoutError("timed out")],
    })
    backoff_calls = _install_scripted_transport(checker, monkeypatch, scripted)
    throttler = _make_throttler(checker)
    try:
        result = checker.classify_url(url, throttler)
    finally:
        throttler.shutdown()
    assert result.verdict is checker.Verdict.TRANSIENT, result
    assert "timeout" in result.detail, f"expected timeout token, got {result.detail!r}"
    assert result.final_status is None, "a timeout has no observed final status"
    assert len(backoff_calls) == 2


def test_head_405_then_get_200_is_healthy(checker, monkeypatch):
    """HEAD 405 (Method Not Allowed) → ranged-GET 200 → HEALTHY (HEAD→GET fallback).

    405 ∈ _HEAD_RETRY_AS_GET → retry the same URL as a ranged GET; GET 200 →
    HEALTHY. The detail records the HEAD 405 → GET 200 sequence.
    """
    url = "https://example.test/head-not-allowed"
    scripted = _ScriptedFetch(by_key={
        ("HEAD", url): [(405, {})],
        ("GET", url): [(200, {})],
    })
    _install_scripted_transport(checker, monkeypatch, scripted)
    throttler = _make_throttler(checker)
    try:
        result = checker.classify_url(url, throttler)
    finally:
        throttler.shutdown()
    assert result.verdict is checker.Verdict.HEALTHY, result
    assert result.final_status == 200
    assert "405" in result.detail and "GET 200" in result.detail, (
        f"detail should show the HEAD 405 → GET 200 fallback, got {result.detail!r}"
    )
    assert [m for (m, _u, _h) in scripted.calls] == ["HEAD", "GET"]


def test_redirect_loop_is_link_rot(checker, monkeypatch):
    """A redirect that always 301s back to itself → LINK_ROT (broken, >5 hops)."""
    url = "https://example.test/loop"
    # Every HEAD on this URL 301s to the SAME url → never terminates within 5 hops.
    scripted = _ScriptedFetch(default=[(301, {"Location": url})] * 10)
    _install_scripted_transport(checker, monkeypatch, scripted)
    throttler = _make_throttler(checker)
    try:
        result = checker.classify_url(url, throttler)
    finally:
        throttler.shutdown()
    assert result.verdict is checker.Verdict.LINK_ROT, result
    assert "hops" in result.detail or "loop" in result.detail, (
        f"detail should flag the redirect loop / hop-exceed, got {result.detail!r}"
    )


def test_more_than_five_hops_is_link_rot(checker, monkeypatch):
    """Six distinct 301 hops (would-continue) → LINK_ROT (>5 hops broken).

    MAX_REDIRECTS=5 → the loop runs hops 0..5 (6 iterations); supplying six
    distinct 301 redirects exhausts the cap and the URL is classified broken.
    """
    hops = [f"https://example.test/hop{i}" for i in range(8)]
    by_key = {}
    # hops[0] is the entry url; each hop 301s to the next distinct url.
    for i in range(7):
        by_key[("HEAD", hops[i])] = [(301, {"Location": hops[i + 1]})]
    scripted = _ScriptedFetch(by_key=by_key)
    _install_scripted_transport(checker, monkeypatch, scripted)
    throttler = _make_throttler(checker)
    try:
        result = checker.classify_url(hops[0], throttler)
    finally:
        throttler.shutdown()
    assert result.verdict is checker.Verdict.LINK_ROT, result
    assert "hops" in result.detail or "loop" in result.detail, (
        f"detail should flag the >5-hop exceed, got {result.detail!r}"
    )
    # Exactly MAX_REDIRECTS + 1 == 6 HEAD attempts before the cap trips.
    head_calls = [c for c in scripted.calls if c[0] == "HEAD"]
    assert len(head_calls) == checker.MAX_REDIRECTS + 1, (
        f"expected {checker.MAX_REDIRECTS + 1} HEAD hops, got {len(head_calls)}"
    )


def test_classifier_matrix_opens_no_real_socket(checker, monkeypatch):
    """A representative classify_url run fires NO socket/DNS guard (matrix-wide NFR-001).

    Wraps a multi-status sweep with the SAME hard guards as the import test
    (T009): if ``classify_url`` ever fell through to a real ``urllib`` call, the
    socket/DNS guard would fire. The stubbed ``HostThrottler.fetch`` is the only
    transport, so the guards must stay un-tripped across HEALTHY / LINK_ROT /
    NEEDS_REVIEW / TRANSIENT scenarios.
    """
    scenarios = {
        "https://example.test/a": [(200, {})],
        "https://example.test/b": [(404, {})],
        "https://example.test/c": [(429, {})],
    }
    scripted = _ScriptedFetch(by_key={("HEAD", u): list(seq) for u, seq in scenarios.items()})
    backoff_calls = _install_scripted_transport(checker, monkeypatch, scripted)
    throttler = _make_throttler(checker)

    originals, tripped = _install_network_guards()
    try:
        results = [checker.classify_url(u, throttler) for u in scenarios]
    finally:
        _restore_network_guards(originals)
        throttler.shutdown()

    assert tripped == [], (
        f"classify_url tripped network/subprocess guard(s) — a real socket was "
        f"opened despite the stubbed transport: {tripped}"
    )
    verdicts = {r.url: r.verdict for r in results}
    assert verdicts["https://example.test/a"] is checker.Verdict.HEALTHY
    assert verdicts["https://example.test/b"] is checker.Verdict.LINK_ROT
    assert verdicts["https://example.test/c"] is checker.Verdict.NEEDS_REVIEW
    assert backoff_calls == [], "no retries expected for deterministic 2xx/4xx scenarios"
