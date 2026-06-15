#!/usr/bin/env python3
"""Citation-URL link-rot checker for tachi taxonomy YAMLs (Feature #183, BLP-05 Wave 3).

Discovers every external citation URL referenced by ``schemas/taxonomy/*.yaml``
(``citation`` in ``crosswalk.yaml``; ``url`` in all other catalogs), probes each
for link-rot via a polite, per-host-throttled HTTP HEAD/ranged-GET sweep, and
renders a single self-updating GitHub tracking issue body. Zero runtime
dependency beyond pyyaml and the ambient ``gh`` binary (NFR-002): no third-party
HTTP client — stdlib ``urllib`` only. Importing this module opens NO socket and
spawns NO subprocess (NFR-001): all network code lives inside ``classify_url`` /
``HostThrottler`` and all ``gh`` subprocess calls in ``manage_tracking_issue`` —
both reachable only from ``main()`` and never executed at module scope.

Exit-code legend (load-bearing — this is a MONITOR, not a GATE):
    0  ran successfully — INCLUDING when link-rot was found (rot is reported via
       the tracking issue, never via the exit code).
    2  genuine infrastructure error ONLY (cannot read the taxonomy dir, malformed
       YAML, gh/auth failure). Never returned merely because rotted URLs exist.
"""

from __future__ import annotations

import argparse
import calendar
import concurrent.futures
import dataclasses
import datetime
import email.utils
import enum
import glob
import http.client
import json
import pathlib
import random
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

import yaml

# =============================================================================
# Constants
# =============================================================================

EXIT_SUCCESS = 0
EXIT_INFRA_ERROR = 2

CROSSWALK_BASENAME = "crosswalk.yaml"
URL_SCHEME_PREFIXES = ("http://", "https://")  # mirrors the integrity test's ^https?://

USER_AGENT = (
    "tachi-linkrot-monitor/1.0 "
    "(+https://github.com/davidmatousek/tachi; citation integrity check)"
)
REQUEST_HEADERS = {"User-Agent": USER_AGENT, "Accept": "text/html,*/*"}

MAX_REDIRECTS = 5
RETRY_AFTER_CAP_SECONDS = 30.0

# Transient-retry policy (T011, NFR-004): 5xx / timeout / DNS / conn-reset get up
# to MAX_TRANSIENT_RETRIES additional attempts with exponential backoff + jitter
# (1→2→4s). 4xx is NEVER retried (deterministic). Total attempts = 1 + retries.
MAX_TRANSIENT_RETRIES = 2
RETRY_BASE_SECONDS = 1.0

ISSUE_TITLE_SENTINEL = "[link-rot] Taxonomy citation link-rot — open findings"
MACHINE_BLOCK_START = "<!--linkrot:start-->"
MACHINE_BLOCK_END = "<!--linkrot:end-->"

SENTINEL_URL = "https://example.invalid/tachi-linkrot-sentinel"


class InfraError(Exception):
    """Raised on a genuine infrastructure failure — main() maps this to exit 2."""


# =============================================================================
# Data model (data-model.md)
# =============================================================================


class Verdict(enum.Enum):
    """Classification outcome for one URL (data-model.md §Verdict)."""

    HEALTHY = "healthy"          # final 2xx — writes ledger, reported nowhere
    LINK_ROT = "link_rot"        # final 404/410/post-retry hard-4xx — confirmed rot
    NEEDS_REVIEW = "needs_review"  # 401/403/429 — manual-verification section
    TRANSIENT = "transient"      # 5xx/timeout/DNS/conn after retries — not reported


@dataclasses.dataclass(frozen=True)
class SourceLocation:
    """Where a URL is cited. One URL maps to many (data-model.md §SourceLocation)."""

    file: str                    # basename, e.g. "mitre-attack.yaml"
    kind: str                    # "catalog" | "crosswalk"
    record_ref: str              # catalog: record id; crosswalk: "src:id → dst:id"

    def display(self) -> str:
        """Human display form used in the tracking-issue sub-bullets."""
        if self.kind == "crosswalk":
            return f"crosswalk edge {self.record_ref}"
        return f"{self.file}: {self.record_ref}"


@dataclasses.dataclass
class Classification:
    """Result of fetching one URL (data-model.md §Classification)."""

    url: str
    verdict: Verdict
    final_status: int | None = None  # None for DNS/conn failure/timeout
    final_url: str | None = None     # post-redirect URL if it differed
    detail: str = ""                 # short reason, e.g. "HEAD 405 → GET 200"


# =============================================================================
# T003 — Discovery (FR-003)
# =============================================================================


def _is_external_url(value: object) -> bool:
    """True iff *value* is an ``^https?://`` string. Drops repo file-path citations."""
    return isinstance(value, str) and value.startswith(URL_SCHEME_PREFIXES)


def _crosswalk_record_ref(edge: dict) -> str:
    """Build the ``"<src.taxonomy>:<src.id> → <dst.taxonomy>:<dst.id>"`` reference."""
    src, dst = edge.get("source", {}), edge.get("target", {})
    return (
        f"{src.get('taxonomy')}:{src.get('id')} → "
        f"{dst.get('taxonomy')}:{dst.get('id')}"
    )


def discover_urls(taxonomy_glob: str) -> dict[str, list[SourceLocation]]:
    """Glob taxonomy YAMLs and return a deduped ``{url: [SourceLocation, ...]}`` map.

    Field rule (FR-003): ``crosswalk.yaml`` → each edge's ``citation``; every other
    matched YAML → each record's ``url``. A uniform ``^https?://`` filter is applied
    to BOTH surfaces (architect CONCERN-2), dropping repo-file-path ``url:`` values
    identically. A malformed/unreadable YAML raises ``InfraError`` (→ exit 2).
    """
    paths = sorted(glob.glob(taxonomy_glob))
    if not paths:
        raise InfraError(f"no taxonomy YAMLs matched glob: {taxonomy_glob!r}")

    back_refs: dict[str, list[SourceLocation]] = {}
    for path_str in paths:
        path = pathlib.Path(path_str)
        basename = path.name
        try:
            with open(path, encoding="utf-8") as handle:
                parsed = yaml.safe_load(handle)
        except (OSError, yaml.YAMLError) as exc:
            raise InfraError(f"cannot read/parse taxonomy YAML {basename}: {exc}") from exc

        if not isinstance(parsed, list):
            raise InfraError(f"{basename}: expected a list of records, got {type(parsed).__name__}")

        if basename == CROSSWALK_BASENAME:
            for edge in parsed:
                citation = edge.get("citation") if isinstance(edge, dict) else None
                if _is_external_url(citation):
                    loc = SourceLocation(basename, "crosswalk", _crosswalk_record_ref(edge))
                    back_refs.setdefault(citation, []).append(loc)
        else:
            for record in parsed:
                url = record.get("url") if isinstance(record, dict) else None
                if _is_external_url(url):
                    loc = SourceLocation(basename, "catalog", str(record.get("id")))
                    back_refs.setdefault(url, []).append(loc)

    return back_refs


def url_host(url: str) -> str | None:
    """Return the throttling/grouping key — ``urlsplit(url).hostname`` (FR-005)."""
    return urllib.parse.urlsplit(url).hostname


# =============================================================================
# T004 — Per-host throttling (FR-005, NFR-003)
# =============================================================================


class HostThrottler:
    """Per-host concurrency cap + politeness delay over a shared thread pool.

    Wraps a ``ThreadPoolExecutor(max_workers=global_concurrency)`` and lazily
    creates a ``Semaphore(max_host_concurrency)`` per host. All network code is
    confined to ``fetch`` — never executed at module scope (NFR-001).
    """

    def __init__(
        self,
        global_concurrency: int,
        max_host_concurrency: int,
        politeness_ms: int,
        connect_timeout: float,
        read_timeout: float,
    ) -> None:
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=global_concurrency)
        self.max_host_concurrency = max_host_concurrency
        self.politeness_seconds = politeness_ms / 1000.0
        # urllib uses a single timeout per call; use the larger of connect/read.
        self.timeout = max(connect_timeout, read_timeout)
        self._semaphores: dict[str, threading.Semaphore] = {}
        self._lock = threading.Lock()
        # A no-redirect opener: we follow redirects manually (≤5 hops) in classify_url.
        self.opener = urllib.request.build_opener(_NoRedirect())

    def _semaphore_for(self, host: str | None) -> threading.Semaphore:
        key = host or ""
        with self._lock:
            sem = self._semaphores.get(key)
            if sem is None:
                sem = threading.Semaphore(self.max_host_concurrency)
                self._semaphores[key] = sem
            return sem

    def fetch(self, url: str, method: str, extra_headers: dict[str, str] | None = None):
        """Issue one throttled request; return ``http.client.HTTPResponse``.

        Acquires the host semaphore, issues the request, sleeps the politeness
        delay, then releases. Honors ``Retry-After`` on 429/503 (up to a cap).
        """
        host = url_host(url)
        sem = self._semaphore_for(host)
        headers = dict(REQUEST_HEADERS)
        if extra_headers:
            headers.update(extra_headers)
        sem.acquire()
        try:
            request = urllib.request.Request(url, method=method, headers=headers)
            try:
                return self.opener.open(request, timeout=self.timeout)
            except urllib.error.HTTPError as http_error:
                self._honor_retry_after(http_error)
                return http_error  # HTTPError exposes .code/.headers like a response
        finally:
            if self.politeness_seconds:
                time.sleep(self.politeness_seconds)
            sem.release()

    @staticmethod
    def _honor_retry_after(http_error: urllib.error.HTTPError) -> None:
        """Sleep per a 429/503 ``Retry-After`` header (int seconds or HTTP-date), capped."""
        if http_error.code not in (429, 503):
            return
        value = http_error.headers.get("Retry-After") if http_error.headers else None
        if not value:
            return
        seconds: float | None = None
        try:
            seconds = float(int(value))
        except ValueError:
            parsed = email.utils.parsedate_to_datetime(value)
            if parsed is not None:
                seconds = max(0.0, parsed.timestamp() - time.time())
        if seconds is not None:
            time.sleep(min(seconds, RETRY_AFTER_CAP_SECONDS))

    def shutdown(self) -> None:
        """Release the underlying thread pool."""
        self.executor.shutdown(wait=True)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Disables urllib's automatic redirect following — we cap hops manually (≤5)."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D102
        return None


# =============================================================================
# T005 — Classification core fetch path (FR-004, detection half)
# =============================================================================

# Statuses that mean "method not allowed / forbidden HEAD" → retry once as ranged GET.
_HEAD_RETRY_AS_GET = frozenset({403, 405, 501})
# Final 4xx statuses that classify as confirmed link-rot.
_HARD_ROT_STATUSES = frozenset({400, 404, 410, 451})
# 4xx statuses that mean "probably bot-blocked, needs a human" — never auto-rot.
_NEEDS_REVIEW_STATUSES = frozenset({401, 403, 429})


class _TransientRetry(Exception):
    """Internal signal: a single attempt hit a retryable transient condition.

    Carries a short ``token`` (e.g. ``"timeout"``, ``"500"``, ``"dns"``,
    ``"conn-reset"``) and the ``final_url`` reached so far. Raised by
    :func:`_classify_once` for 5xx-final statuses and connection-level
    exceptions; caught by :func:`classify_url`, which decides whether to retry
    (with exponential backoff) or give up and emit a final ``TRANSIENT`` verdict.
    Never escapes this module — it is purely a control-flow signal (NFR-001).
    """

    def __init__(self, token: str, final_url: str) -> None:
        super().__init__(token)
        self.token = token
        self.final_url = final_url


def _transient_token_for_exception(exc: BaseException) -> str:
    """Map a connection-level exception to a short retry/detail token.

    Discriminates DNS failure, timeout, and connection-reset from a generic
    connection error so the ``detail`` string is diagnostic (data-model.md
    §Classification — e.g. ``"timeout x3"``).
    """
    # urllib wraps the underlying socket error in URLError.reason; for a bare
    # timeout/socket error (no .reason attr) getattr falls back to exc itself,
    # so this single check covers both the wrapped and unwrapped cases.
    reason = getattr(exc, "reason", exc)
    if isinstance(reason, (TimeoutError, socket.timeout)):
        return "timeout"
    if isinstance(reason, socket.gaierror):
        return "dns"
    if isinstance(reason, ConnectionResetError):
        return "conn-reset"
    if isinstance(reason, ConnectionError):
        return "conn"
    return "conn"


def _classify_once(url: str, throttler: HostThrottler) -> Classification:
    """Run ONE probe attempt (HEAD→ranged-GET fallback, ≤5 manual redirects).

    Returns a terminal :class:`Classification` for any 2xx/4xx final status or a
    redirect-hop-exceeded condition (all deterministic — no retry). Raises
    :class:`_TransientRetry` for a 5xx-final status or a connection-level
    exception (timeout / DNS / conn-reset / generic conn), so the caller's retry
    loop can re-attempt. The HEAD→GET fallback and redirect following match the
    Wave-1 flow exactly; only the 5xx/exception paths now signal a retry.
    """
    current = url
    detail_parts: list[str] = []
    try:
        for _hop in range(MAX_REDIRECTS + 1):
            response = throttler.fetch(current, "HEAD")
            status = response.status if hasattr(response, "status") else response.code
            detail_parts.append(f"HEAD {status}")

            # HEAD often disallowed — retry this same URL once as a ranged GET.
            if status in _HEAD_RETRY_AS_GET:
                response = throttler.fetch(current, "GET", {"Range": "bytes=0-0"})
                status = response.status if hasattr(response, "status") else response.code
                detail_parts.append(f"GET {status}")

            # Manual redirect following, capped at MAX_REDIRECTS hops.
            if status in (301, 302, 303, 307, 308):
                location = response.headers.get("Location") if response.headers else None
                if not location:
                    # A redirect with no Location is broken, not transient → rot.
                    return _classification(url, Verdict.LINK_ROT, status, current,
                                           "redirect with no Location")
                current = urllib.parse.urljoin(current, location)
                continue

            # 5xx → retryable transient: signal the caller to back off and retry.
            if 500 <= status < 600:
                raise _TransientRetry(str(status), current)

            # 2xx / 4xx (and any other non-5xx, non-redirect) are deterministic.
            return _verdict_for_status(url, status, current, " → ".join(detail_parts))

        # Loop exhausted → exceeded MAX_REDIRECTS hops → treated as broken (rot).
        return _classification(url, Verdict.LINK_ROT, None, current,
                               f"redirect loop / >{MAX_REDIRECTS} hops")

    except urllib.error.HTTPError as http_error:
        # The throttler normally surfaces HTTPError as a response-like object, so
        # this is a defensive fallback. An HTTPError carries a real status code, so
        # classify on it deterministically (a 5xx still routes to a retry) rather
        # than treating it as an opaque connection failure.
        status = http_error.code
        if 500 <= status < 600:
            raise _TransientRetry(str(status), current) from http_error
        return _verdict_for_status(url, status, current, f"HTTPError {status}")
    except (urllib.error.URLError, http.client.HTTPException, OSError) as exc:
        # Connection-level failure (timeout / DNS / reset / conn) → retryable.
        raise _TransientRetry(_transient_token_for_exception(exc), current) from exc


def _backoff_sleep(attempt: int) -> None:
    """Sleep exponentially with jitter before the next transient retry.

    ``delay = RETRY_BASE_SECONDS * (2 ** attempt) + uniform(0, RETRY_BASE_SECONDS)``
    yields ~1→2→4s across attempts 0,1,2 plus sub-second jitter to avoid
    thundering-herd alignment against a recovering host (NFR-004).
    """
    delay = RETRY_BASE_SECONDS * (2 ** attempt) + random.uniform(0, RETRY_BASE_SECONDS)
    time.sleep(delay)


def classify_url(url: str, throttler: HostThrottler) -> Classification:
    """Probe one URL and return its :class:`Classification` (FR-004 full).

    Flow: issue ``HEAD``; on 405/403/501 retry once as a ranged ``GET``
    (``Range: bytes=0-0``); follow ≤5 redirects manually; classify on the FINAL
    status. 2xx/4xx short-circuit immediately (deterministic — never retried).
    A 5xx-final status or a connection-level failure (timeout / DNS / conn-reset)
    is retried up to :data:`MAX_TRANSIENT_RETRIES` times with exponential backoff
    + jitter (1→2→4s); if still failing after retries the verdict is a final
    ``TRANSIENT`` with a count-annotated ``detail`` (e.g. ``"timeout x3"`` or
    ``"500 x3"``). A single fetch failure NEVER crashes the run — it is caught
    here and returned as a verdict so the sweep continues (no silent failure).

    Verdict mapping (data-model.md §Verdict):
        final 2xx                          → HEALTHY
        final 404/410/400/451              → LINK_ROT
        401/403/429                        → NEEDS_REVIEW
        redirect loop / >5 hops            → LINK_ROT (broken)
        5xx / timeout / DNS / conn (retries exhausted) → TRANSIENT
    """
    last_token = "transient"
    last_url = url
    # attempts 0..MAX_TRANSIENT_RETRIES inclusive → 1 initial + N retries.
    for attempt in range(MAX_TRANSIENT_RETRIES + 1):
        try:
            return _classify_once(url, throttler)
        except _TransientRetry as retry:
            last_token = retry.token
            last_url = retry.final_url
            if attempt < MAX_TRANSIENT_RETRIES:
                _backoff_sleep(attempt)
                continue
        except (ValueError, http.client.HTTPException, OSError) as exc:
            # Defensive net: an unexpected per-URL failure (e.g. a malformed
            # redirect target) must degrade to a non-reported TRANSIENT, never
            # crash the worker thread / abort the whole sweep (no silent failure).
            return _classification(url, Verdict.TRANSIENT, None, last_url,
                                   f"fetch error: {type(exc).__name__}")

    # Retries exhausted — emit a final TRANSIENT annotated with the attempt count.
    total_attempts = MAX_TRANSIENT_RETRIES + 1
    return _classification(url, Verdict.TRANSIENT, None, last_url,
                           f"{last_token} x{total_attempts}")


def _verdict_for_status(url: str, status: int, final_url: str, detail: str) -> Classification:
    """Map a deterministic (2xx/4xx) final HTTP status to a :class:`Classification`.

    5xx never reaches here — :func:`_classify_once` raises :class:`_TransientRetry`
    for 5xx before calling this. Any non-2xx/non-rot/non-needs-review status that
    does reach here (e.g. an unexpected 3xx that was not a recognized redirect) is
    treated conservatively as ``TRANSIENT`` (not reported).
    """
    if 200 <= status < 300:
        verdict = Verdict.HEALTHY
    elif status in _HARD_ROT_STATUSES:
        verdict = Verdict.LINK_ROT
    elif status in _NEEDS_REVIEW_STATUSES:
        verdict = Verdict.NEEDS_REVIEW
    else:
        verdict = Verdict.TRANSIENT
    return _classification(url, verdict, status, final_url, detail)


def _classification(url: str, verdict: Verdict, status: int | None,
                    final_url: str | None, detail: str) -> Classification:
    """Construct a Classification, recording ``final_url`` only when it differs."""
    return Classification(
        url=url,
        verdict=verdict,
        final_status=status,
        final_url=final_url if final_url and final_url != url else None,
        detail=detail,
    )


# =============================================================================
# T014 — Last-success ledger (FR-006, contracts/cache-ledger.schema.json)
# =============================================================================

LEDGER_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"  # schema: ISO-8601 UTC, second precision


def _now_utc() -> float:
    """Current POSIX timestamp (UTC). Wrapped for test-time monkeypatching."""
    return time.time()


def _format_ledger_timestamp(epoch_seconds: float) -> str:
    """Format a POSIX timestamp as a schema-conformant ISO-8601 UTC string."""
    return time.strftime(LEDGER_TIMESTAMP_FORMAT, time.gmtime(epoch_seconds))


def _parse_ledger_timestamp(value: str) -> float | None:
    """Parse a ledger ``last_ok`` ISO-8601 UTC string to a POSIX timestamp.

    Tolerates a trailing ``Z`` and (defensively) sub-second/offset variants.
    Returns ``None`` on any unparseable value so callers treat it as a cache
    miss (re-check) rather than crashing — the ledger is never a source of truth.
    """
    if not isinstance(value, str) or not value:
        return None
    text = value.strip()
    try:
        return calendar.timegm(time.strptime(text, LEDGER_TIMESTAMP_FORMAT))
    except ValueError:
        pass
    # Fallback: let datetime handle offsets / fractional seconds (e.g. "+00:00").
    try:
        normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
        parsed = datetime.datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=datetime.timezone.utc)
        return parsed.timestamp()
    except ValueError:
        return None


class Ledger:
    """Per-URL last-success cache (FR-006; cache-ledger.schema.json).

    An OPTIMIZATION ONLY — never a source of truth. A missing or corrupt file is
    an empty ledger ("check everything"), never "assume healthy". Only a final
    2xx (``HEALTHY``) outcome refreshes ``last_ok``; a 4xx / needs-review /
    transient outcome updates ``last_status`` for context but NEVER ``last_ok``,
    so a rotted URL is re-checked every run until it 2xx-recovers.

    In-memory shape mirrors the on-disk JSON: ``{url: {"last_ok": iso8601,
    "last_status": int}}``.
    """

    def __init__(self, entries: dict[str, dict[str, object]] | None = None) -> None:
        self._entries: dict[str, dict[str, object]] = entries or {}

    @classmethod
    def load(cls, path: str) -> "Ledger":
        """Load the ledger JSON at *path*; missing/corrupt → empty (never crash).

        A read or parse failure logs a single note to stderr and yields an empty
        ledger, guaranteeing a cache miss degrades to "check everything" rather
        than aborting the run (FR-006 / no silent failure).
        """
        ledger_path = pathlib.Path(path)
        if not ledger_path.exists():
            print(f"note: no ledger at {path!r} — checking every URL (cache miss)",
                  file=sys.stderr)
            return cls({})
        try:
            with open(ledger_path, encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            print(f"note: ignoring unreadable/corrupt ledger {path!r} "
                  f"({type(exc).__name__}: {exc}) — checking every URL",
                  file=sys.stderr)
            return cls({})
        if not isinstance(data, dict):
            print(f"note: ledger {path!r} is not a JSON object — checking every URL",
                  file=sys.stderr)
            return cls({})
        # Keep only well-formed entries; drop the rest (defensive, non-fatal).
        entries: dict[str, dict[str, object]] = {}
        for url, entry in data.items():
            if isinstance(url, str) and isinstance(entry, dict):
                entries[url] = dict(entry)
        return cls(entries)

    def should_skip(self, url: str, ttl_days: int, *, no_cache: bool = False) -> bool:
        """True iff *url* has a fresh ``last_ok`` within *ttl_days* (else re-check).

        Returns ``False`` whenever ``no_cache`` is set (full sweep), the URL is
        absent, ``last_ok`` is missing/unparseable, or it is older than the TTL —
        i.e. the safe default is always "check it".
        """
        if no_cache:
            return False
        entry = self._entries.get(url)
        if not entry:
            return False
        last_ok = _parse_ledger_timestamp(entry.get("last_ok"))  # type: ignore[arg-type]
        if last_ok is None:
            return False
        age_seconds = _now_utc() - last_ok
        return age_seconds < ttl_days * 86400.0

    def record(self, classification: Classification) -> None:
        """Update the ledger from one classification (write rule, FR-006).

        ONLY a final 2xx (``HEALTHY``) refreshes ``last_ok`` to now. Every outcome
        with a concrete ``final_status`` updates ``last_status`` for context, but a
        4xx / needs-review / transient NEVER touches ``last_ok`` (so it stays
        re-checked until recovery). A status-less transient (timeout/DNS) records
        nothing — there is no observed final status to remember.
        """
        url = classification.url
        is_healthy = classification.verdict is Verdict.HEALTHY
        if not is_healthy and classification.final_status is None:
            return  # nothing observed worth caching (e.g. timeout/DNS transient)
        entry = self._entries.setdefault(url, {})
        if classification.final_status is not None:
            entry["last_status"] = classification.final_status
        if is_healthy:
            entry["last_ok"] = _format_ledger_timestamp(_now_utc())
        # NB: save() persists only entries that carry BOTH last_ok and last_status
        # (the schema's required keys). An entry seen solely as a 4xx — last_status
        # but no last_ok — is therefore dropped on save and re-checked next run.

    def previously_healthy_date(self, url: str) -> str | None:
        """Return the date (``YYYY-MM-DD``) of *url*'s last 2xx, if any.

        Drives the optional "previously healthy ``<date>``" suffix on a rotted
        URL's tracking-issue line (T012). Returns ``None`` when no ``last_ok`` is
        on record (e.g. cache miss / never-healthy URL).
        """
        entry = self._entries.get(url)
        if not entry:
            return None
        last_ok = entry.get("last_ok")
        epoch = _parse_ledger_timestamp(last_ok)  # type: ignore[arg-type]
        if epoch is None:
            return None
        return time.strftime("%Y-%m-%d", time.gmtime(epoch))

    def save(self, path: str) -> None:
        """Write the ledger to *path* as schema-conformant JSON ({url:{last_ok,last_status}}).

        Only entries that satisfy the schema's ``required: [last_ok, last_status]``
        are persisted; an entry observed solely as a 4xx (no prior ``last_ok``) is
        omitted so the URL is naturally re-checked on the next run. A write failure
        is non-fatal (the ledger is an optimization) — it logs a note and returns.
        """
        serializable: dict[str, dict[str, object]] = {}
        for url, entry in self._entries.items():
            last_ok = entry.get("last_ok")
            last_status = entry.get("last_status")
            if isinstance(last_ok, str) and isinstance(last_status, int):
                serializable[url] = {"last_ok": last_ok, "last_status": last_status}
        try:
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(serializable, handle, indent=2, sort_keys=True)
                handle.write("\n")
        except OSError as exc:
            print(f"note: could not write ledger {path!r} ({type(exc).__name__}: {exc})",
                  file=sys.stderr)


# =============================================================================
# T006 — Issue body rendering (FR-007, data-model.md §TrackingIssueBody)
# =============================================================================


def _append_host_grouped_findings(
    lines: list[str],
    findings: list[Classification],
    sources: dict[str, list[SourceLocation]],
    *,
    bold_status: bool,
    previously_healthy: dict[str, str] | None = None,
) -> None:
    """Append a host-grouped finding list to *lines* (shared by both sections).

    Each host becomes an ``### <host>`` subheading; each finding a per-URL line
    (URL · final status, optionally bolded; optional "previously healthy
    ``<date>``" suffix when *previously_healthy* carries a date for that URL),
    followed by one sub-bullet per :class:`SourceLocation` display form. Matches
    data-model.md §TrackingIssueBody exactly.
    """
    by_host: dict[str, list[Classification]] = {}
    for finding in findings:
        by_host.setdefault(url_host(finding.url) or "(unknown host)", []).append(finding)

    for host in sorted(by_host):
        lines.append("")
        lines.append(f"### {host}")
        for finding in by_host[host]:
            status: int | str = (
                finding.final_status if finding.final_status is not None else "broken"
            )
            status_md = f"**{status}**" if bold_status else f"{status}"
            line = f"- `{finding.url}` — {status_md}"
            healthy_date = (previously_healthy or {}).get(finding.url)
            if healthy_date:
                line += f" — previously healthy {healthy_date}"
            lines.append(line)
            for location in sources.get(finding.url, []):
                lines.append(f"  - {location.display()}")


def render_issue_body(
    confirmed_rot: list[Classification],
    needs_review: list[Classification],
    sources: dict[str, list[SourceLocation]],
    run_timestamp: str,
    previously_healthy: dict[str, str] | None = None,
) -> str:
    """Render the tracking-issue Markdown body (data-model.md §TrackingIssueBody).

    Two sections inside one machine-parseable block delimited by the exact markers
    ``<!--linkrot:start-->`` … ``<!--linkrot:end-->`` (rewritten in place each run
    so the next run can diff state):

    1. **Confirmed link-rot (N)** — the ``LINK_ROT`` findings; N is the SOLE
       open/close driver (a rotted line may carry a "previously healthy
       ``<date>``" suffix sourced from the ledger's ``last_ok``).
    2. **Needs manual verification (M) — possibly bot-blocked** — the
       ``NEEDS_REVIEW`` findings (401/403/429). M is informational only and NEVER
       affects the open/close decision.

    ``TRANSIENT`` findings are never rendered. Both sections group by host.
    """
    lines: list[str] = [MACHINE_BLOCK_START, "", f"## Confirmed link-rot ({len(confirmed_rot)})"]
    _append_host_grouped_findings(
        lines, confirmed_rot, sources,
        bold_status=True, previously_healthy=previously_healthy,
    )

    # ---- EXTENSION POINT (T012): needs-manual-verification section, grouped by
    #      host, INSIDE the machine block (before the closing delimiter). This is
    #      informational only — it does NOT affect the confirmed-rot open/close
    #      count. TRANSIENT is never rendered anywhere. ----
    if needs_review:
        lines.append("")
        lines.append(f"## Needs manual verification ({len(needs_review)}) — possibly bot-blocked")
        _append_host_grouped_findings(lines, needs_review, sources, bold_status=False)

    lines.append(MACHINE_BLOCK_END)
    lines.append("")
    lines.append(f"_Last run: {run_timestamp} · sentinel: `{ISSUE_TITLE_SENTINEL}`_")
    return "\n".join(lines)


# =============================================================================
# T015 — Tracking-issue lifecycle via native gh (FR-007, NFR-006/NFR-007)
# =============================================================================

LINEAGE_LABEL = "follow-on-180"   # existing lineage label applied on create
LINKROT_LABEL = "link-rot"        # convenience label (best-effort ensure)
LINKROT_LABEL_COLOR = "b35900"    # rust/amber — "rot"; cosmetic only


@dataclasses.dataclass
class IssueOutcome:
    """Result of a tracking-issue lifecycle pass (feeds the --json summary)."""

    action: str            # "created" | "updated" | "closed" | "none"
    number: int | None = None


def _run_gh(args: list[str], *, fatal: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a ``gh`` subcommand, capturing output (NEVER at import time).

    With ``fatal=True`` (default) a non-zero exit, a missing ``gh`` binary, or an
    auth failure raises :class:`InfraError` (→ main returns exit 2). With
    ``fatal=False`` the same conditions are swallowed (the returned process may
    have a non-zero ``returncode``) for best-effort calls (label create, delta
    comment) whose failure must degrade gracefully rather than block the run.
    """
    try:
        completed = subprocess.run(
            ["gh", *args],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        if fatal:
            raise InfraError("gh CLI not found on PATH (required for issue I/O)") from exc
        return subprocess.CompletedProcess(["gh", *args], 127, "", str(exc))
    except OSError as exc:
        if fatal:
            raise InfraError(f"failed to invoke gh: {exc}") from exc
        return subprocess.CompletedProcess(["gh", *args], 1, "", str(exc))

    if fatal and completed.returncode != 0:
        raise InfraError(
            f"gh {' '.join(args[:2])} failed (exit {completed.returncode}): "
            f"{completed.stderr.strip() or completed.stdout.strip()}"
        )
    return completed


def _find_open_issue(sentinel_title: str) -> int | None:
    """Return the number of the open issue whose title EXACTLY equals the sentinel.

    Uses ``gh issue list --search '"<sentinel>" in:title'`` (a substring/keyword
    search), then filters in Python for an EXACT title match so a near-miss title
    can never be mistaken for the canonical tracking issue. A gh failure here is
    fatal (→ exit 2) — we cannot safely create/close without a reliable lookup.
    """
    completed = _run_gh([
        "issue", "list",
        "--state", "open",
        "--search", f'"{sentinel_title}" in:title',
        "--json", "number,title",
        "--limit", "50",
    ])
    try:
        rows = json.loads(completed.stdout or "[]")
    except json.JSONDecodeError as exc:
        raise InfraError(f"could not parse gh issue list JSON: {exc}") from exc
    for row in rows:
        if isinstance(row, dict) and row.get("title") == sentinel_title:
            number = row.get("number")
            if isinstance(number, int):
                return number
    return None


def _ensure_linkrot_label() -> None:
    """Best-effort create the convenience ``link-rot`` label (failure is non-fatal).

    Mirrors ``gh label create link-rot --color … 2>/dev/null || true`` — the title
    sentinel is the real dedup mechanism, so a label that already exists or cannot
    be created must NOT abort the run (tracking-issue.md).
    """
    _run_gh(["label", "create", LINKROT_LABEL, "--color", LINKROT_LABEL_COLOR],
            fatal=False)


def _delta_comment_body(confirmed_rot: list[Classification], run_date: str) -> str:
    """Build the dated best-effort delta comment posted alongside an issue edit."""
    return (
        f"Updated {run_date}: {len(confirmed_rot)} confirmed link-rot finding(s) "
        f"in the machine block above. See the body for per-URL detail and source "
        f"locations."
    )


def manage_tracking_issue(
    confirmed_rot: list[Classification],
    needs_review: list[Classification],
    rendered_body: str,
    run_timestamp: str,
) -> IssueOutcome:
    """Drive the single sentinel-titled tracking issue via ``gh`` (FR-007).

    Confirmed rot (the ``LINK_ROT`` count) is the SOLE open/close driver;
    ``needs_review`` never opens or keeps an issue open on its own — it only rides
    along inside an issue that confirmed rot has already opened. Lifecycle
    (tracking-issue.md), keyed by :data:`ISSUE_TITLE_SENTINEL`:

    * rot>0, no open issue  → create (sentinel title, machine-block body, lineage label)
    * rot>0, open issue     → edit body (rewrite block) + best-effort dated delta comment
    * rot==0, open issue    → comment "all citations healthy" THEN close (audit trail)
    * rot==0, no open issue → no-op

    Genuine gh failures (auth, not installed, non-zero create/edit/close) raise
    :class:`InfraError` → exit 2. Only the delta comment is best-effort. MUST be
    called only from :func:`main` (non-dry-run) — never at import time (NFR-001):
    every subprocess call is reachable only through this function.
    """
    has_rot = len(confirmed_rot) > 0
    open_number = _find_open_issue(ISSUE_TITLE_SENTINEL)

    if has_rot and open_number is None:
        # Create the one tracking issue. Best-effort ensure the convenience label
        # exists first; its failure is swallowed and never blocks the create.
        _ensure_linkrot_label()
        completed = _run_gh([
            "issue", "create",
            "--title", ISSUE_TITLE_SENTINEL,
            "--body", rendered_body,
            "--label", LINEAGE_LABEL,
        ])
        return IssueOutcome("created", _issue_number_from_url(completed.stdout))

    if has_rot and open_number is not None:
        # Rewrite the machine block in place (fatal on failure), THEN post a
        # best-effort dated delta comment (failure logged, never blocks the edit).
        _run_gh(["issue", "edit", str(open_number), "--body", rendered_body])
        comment = _run_gh(
            ["issue", "comment", str(open_number),
             "--body", _delta_comment_body(confirmed_rot, run_timestamp)],
            fatal=False,
        )
        if comment.returncode != 0:
            print(f"note: delta comment on issue #{open_number} failed "
                  f"(exit {comment.returncode}); edit succeeded — continuing",
                  file=sys.stderr)
        return IssueOutcome("updated", open_number)

    if not has_rot and open_number is not None:
        # Recovery: ALWAYS comment before closing (audit trail), both fatal — a
        # failed close would silently leave a stale open issue.
        _run_gh(["issue", "comment", str(open_number),
                 "--body", f"All citations healthy as of {run_timestamp}. Closing."])
        _run_gh(["issue", "close", str(open_number)])
        return IssueOutcome("closed", open_number)

    # rot==0 & no open issue → nothing to do.
    return IssueOutcome("none", None)


def _issue_number_from_url(create_stdout: str) -> int | None:
    """Extract the issue number from ``gh issue create`` stdout (an issue URL).

    ``gh issue create`` prints the new issue URL (``…/issues/331``); parse the
    trailing path segment. Returns ``None`` if it cannot be parsed (non-fatal —
    the issue was created regardless; only the reported number is lost).
    """
    text = (create_stdout or "").strip().rstrip("/")
    if not text:
        return None
    tail = text.rsplit("/", 1)[-1]
    return int(tail) if tail.isdigit() else None


# =============================================================================
# T002 — CLI + T007 — main() detection flow (FR-001)
# =============================================================================


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser (contracts/checker-cli.md — authoritative)."""
    parser = argparse.ArgumentParser(
        prog="check-citation-urls.py",
        description="Citation-URL link-rot checker for tachi taxonomy YAMLs (#183).",
    )
    parser.add_argument("--taxonomy-glob", default="schemas/taxonomy/*.yaml",
                        help="discovery glob (overridable for tests)")
    parser.add_argument("--ledger-path", default="linkrot-ledger.json",
                        help="last-success ledger (cache-restored)")
    parser.add_argument("--no-cache", action="store_true",
                        help="ignore ledger; check every URL (forces full sweep)")
    parser.add_argument("--ttl-days", type=int, default=21,
                        help="skip URLs whose last_ok is newer than this")
    parser.add_argument("--max-host-concurrency", type=int, default=3,
                        help="per-host in-flight cap (2–3)")
    parser.add_argument("--global-concurrency", type=int, default=10,
                        help="global thread-pool ceiling")
    parser.add_argument("--politeness-ms", type=int, default=150,
                        help="inter-request delay within a host bucket")
    parser.add_argument("--connect-timeout", type=float, default=10,
                        help="connect timeout (seconds)")
    parser.add_argument("--read-timeout", type=float, default=15,
                        help="read timeout (seconds)")
    parser.add_argument("--inject-sentinel-rot", action="store_true",
                        help="append a pre-classified synthetic rot finding (no fetch)")
    parser.add_argument("--dry-run", action="store_true",
                        help="classify + render, but perform no gh issue I/O")
    parser.add_argument("--json", action="store_true",
                        help="emit the machine summary to stdout")
    return parser


def _sentinel_classification() -> tuple[Classification, SourceLocation]:
    """Pre-classified synthetic rot finding for deterministic validation (TL-2)."""
    return (
        Classification(url=SENTINEL_URL, verdict=Verdict.LINK_ROT,
                       final_status=404, detail="injected sentinel"),
        SourceLocation(file="(sentinel)", kind="catalog", record_ref="validation"),
    )


def main(argv: list[str] | None = None) -> int:
    """Run the detection flow; return an exit code (0 success even with rot, 2 infra)."""
    args = build_parser().parse_args(argv)

    # --- Discovery (FR-003). A failure here is infra (→ exit 2). ---
    try:
        sources = discover_urls(args.taxonomy_glob)
    except InfraError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_INFRA_ERROR

    # --- Optional deterministic sentinel injection (TL-2, no fetch). The
    #     sentinel is pre-classified LINK_ROT and is NEVER fetched nor written to
    #     the ledger (T016); it only drives the gh create/close decision. ---
    sentinel_injected = False
    if args.inject_sentinel_rot:
        _, sentinel_loc = _sentinel_classification()
        sources.setdefault(SENTINEL_URL, []).append(sentinel_loc)
        sentinel_injected = True

    # --- Ledger (FR-006): load, then TTL-skip fresh URLs from the fetch set. The
    #     ledger is an OPTIMIZATION — never a source of truth. The sentinel is
    #     excluded from fetching regardless (it is injected pre-classified). ---
    ledger = Ledger.load(args.ledger_path)
    candidate_urls = [url for url in sources if url != SENTINEL_URL]
    fetch_urls = [
        url for url in candidate_urls
        if not ledger.should_skip(url, args.ttl_days, no_cache=args.no_cache)
    ]
    skipped_cached = len(candidate_urls) - len(fetch_urls)

    # --- Classification sweep through the per-host throttler (FR-001/FR-005). ---
    throttler = HostThrottler(
        global_concurrency=args.global_concurrency,
        max_host_concurrency=args.max_host_concurrency,
        politeness_ms=args.politeness_ms,
        connect_timeout=args.connect_timeout,
        read_timeout=args.read_timeout,
    )
    classifications: list[Classification] = []
    try:
        futures = {
            throttler.executor.submit(classify_url, url, throttler): url
            for url in fetch_urls
        }
        for future in concurrent.futures.as_completed(futures):
            classifications.append(future.result())
    finally:
        throttler.shutdown()

    # --- Ledger write rule (FR-006): record every real fetched outcome, then
    #     persist. Only a 2xx refreshes last_ok. The sentinel is NEVER recorded
    #     (it has no real network outcome). Respects --no-cache for the read side
    #     (should_skip already returned False); writing still refreshes the cache
    #     so a subsequent cached run benefits. ---
    for classification in classifications:
        ledger.record(classification)
    ledger.save(args.ledger_path)

    if sentinel_injected:
        classifications.append(_sentinel_classification()[0])

    # --- Partition by verdict. Confirmed rot (LINK_ROT) is the SOLE open/close
    #     driver; the injected sentinel counts here so it drives create/close. ---
    confirmed_rot = [c for c in classifications if c.verdict is Verdict.LINK_ROT]
    needs_review = [c for c in classifications if c.verdict is Verdict.NEEDS_REVIEW]
    healthy = [c for c in classifications if c.verdict is Verdict.HEALTHY]
    transient = [c for c in classifications if c.verdict is Verdict.TRANSIENT]

    # --- "previously healthy <date>" context for rotted URLs, from the ledger. ---
    previously_healthy = {
        finding.url: date
        for finding in confirmed_rot
        if (date := ledger.previously_healthy_date(finding.url)) is not None
    }

    run_timestamp = time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime())
    body = render_issue_body(
        confirmed_rot, needs_review, sources, run_timestamp,
        previously_healthy=previously_healthy,
    )

    # --- Issue I/O via gh (T015). Suppressed ENTIRELY under --dry-run (which just
    #     prints the body). A genuine gh failure raises InfraError → exit 2. ---
    issue_outcome = IssueOutcome("none", None)
    if args.dry_run:
        print(body)
    else:
        try:
            issue_outcome = manage_tracking_issue(
                confirmed_rot, needs_review, body, run_timestamp,
            )
        except InfraError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return EXIT_INFRA_ERROR

    if args.json:
        summary = {
            "checked": len(fetch_urls),
            "skipped_cached": skipped_cached,
            "healthy": len(healthy),
            "link_rot": len(confirmed_rot),
            "needs_review": len(needs_review),
            "transient": len(transient),
            "issue_action": issue_outcome.action,
            "issue_number": issue_outcome.number,
            "sentinel_injected": sentinel_injected,
        }
        print(json.dumps(summary, indent=2))

    # Monitor, not gate: success even when link_rot > 0 (rot rides the issue).
    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
