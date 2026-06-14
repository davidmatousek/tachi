#!/usr/bin/env python3
"""Citation-URL link-rot checker for tachi taxonomy YAMLs (Feature #183, BLP-05 Wave 3).

Discovers every external citation URL referenced by ``schemas/taxonomy/*.yaml``
(``citation`` in ``crosswalk.yaml``; ``url`` in all other catalogs), probes each
for link-rot via a polite, per-host-throttled HTTP HEAD/ranged-GET sweep, and
renders a single self-updating GitHub tracking issue body. Zero runtime
dependency beyond pyyaml — stdlib only (NFR-002). Importing this module opens
NO socket (NFR-001): all network code lives inside ``classify_url`` /
``HostThrottler`` and is reachable only from ``main()``.

Exit-code legend (load-bearing — this is a MONITOR, not a GATE):
    0  ran successfully — INCLUDING when link-rot was found (rot is reported via
       the tracking issue, never via the exit code).
    2  genuine infrastructure error ONLY (cannot read the taxonomy dir, malformed
       YAML, gh/auth failure). Never returned merely because rotted URLs exist.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import dataclasses
import email.utils
import enum
import glob
import http.client
import json
import pathlib
import random
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


def classify_url(url: str, throttler: HostThrottler) -> Classification:
    """Probe one URL and return its :class:`Classification` (FR-004 detection half).

    Flow: issue ``HEAD``; on 405/403/501 retry once as a ranged ``GET``
    (``Range: bytes=0-0``); follow ≤5 redirects manually; classify on the FINAL
    status. A single fetch failure NEVER crashes the run — it is caught here and
    returned as a placeholder verdict so the sweep continues (no silent failure).

    Verdict mapping for this wave:
        final 2xx                          → HEALTHY
        final 404/410/post-retry hard-4xx  → LINK_ROT
        401/403/429                        → NEEDS_REVIEW
        anything else / fetch failure      → TRANSIENT (placeholder)

    NOTE: the full transient/needs-review retry+backoff semantics arrive in T011.
    This function is deliberately structured so that path can be slotted in at the
    EXTENSION POINT marked below without reshaping the verdict mapping.
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
                    return _classification(url, Verdict.TRANSIENT, status, current,
                                           "redirect with no Location")
                current = urllib.parse.urljoin(current, location)
                continue

            return _verdict_for_status(url, status, current, " → ".join(detail_parts))

        # Loop exhausted → exceeded MAX_REDIRECTS hops → treated as broken (rot).
        return _classification(url, Verdict.LINK_ROT, None, current,
                               f"redirect loop / >{MAX_REDIRECTS} hops")

    # ---- EXTENSION POINT (T011): replace the blanket TRANSIENT below with
    #      exponential-backoff retries (1→2→4s + jitter) for 5xx/timeout/conn,
    #      DNS-vs-timeout discrimination, and final-status re-classification. ----
    except (urllib.error.URLError, http.client.HTTPException, OSError, ValueError) as exc:
        _ = random  # jitter source reserved for the T011 backoff path
        return _classification(url, Verdict.TRANSIENT, None, current,
                               f"fetch failed: {type(exc).__name__}")


def _verdict_for_status(url: str, status: int, final_url: str, detail: str) -> Classification:
    """Map a final HTTP status to a :class:`Classification` (this wave's mapping)."""
    if 200 <= status < 300:
        verdict = Verdict.HEALTHY
    elif status in _HARD_ROT_STATUSES:
        verdict = Verdict.LINK_ROT
    elif status in _NEEDS_REVIEW_STATUSES:
        verdict = Verdict.NEEDS_REVIEW
    else:
        # 5xx and any unmapped status — refined by T011's retry/backoff path.
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
# T006 — Issue body rendering (FR-007, data-model.md §TrackingIssueBody)
# =============================================================================


def render_issue_body(
    confirmed_rot: list[Classification],
    sources: dict[str, list[SourceLocation]],
    run_timestamp: str,
) -> str:
    """Render the tracking-issue Markdown body for the confirmed-rot findings.

    The entire machine-parseable region is wrapped in the exact delimiters
    ``<!--linkrot:start-->`` … ``<!--linkrot:end-->`` so the next run can diff
    state. Findings are grouped by host. The needs-review section is added in
    T012 at the EXTENSION POINT below.
    """
    lines: list[str] = [MACHINE_BLOCK_START, "", f"## Confirmed link-rot ({len(confirmed_rot)})"]

    by_host: dict[str, list[Classification]] = {}
    for finding in confirmed_rot:
        by_host.setdefault(url_host(finding.url) or "(unknown host)", []).append(finding)

    for host in sorted(by_host):
        lines.append("")
        lines.append(f"### {host}")
        for finding in by_host[host]:
            status = finding.final_status if finding.final_status is not None else "broken"
            lines.append(f"- `{finding.url}` — **{status}**")
            for location in sources.get(finding.url, []):
                lines.append(f"  - {location.display()}")

    # ---- EXTENSION POINT (T012): append the "## Needs manual verification (M)"
    #      section here, grouped by host, BEFORE the closing delimiter. ----

    lines.append(MACHINE_BLOCK_END)
    lines.append("")
    lines.append(f"_Last run: {run_timestamp} · sentinel: `{ISSUE_TITLE_SENTINEL}`_")
    return "\n".join(lines)


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

    # --- Optional deterministic sentinel injection (TL-2, no fetch). ---
    sentinel_injected = False
    if args.inject_sentinel_rot:
        sentinel_class, sentinel_loc = _sentinel_classification()
        sources.setdefault(sentinel_class.url, []).append(sentinel_loc)
        sentinel_injected = True

    fetch_urls = [url for url in sources if url != SENTINEL_URL]

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

    if sentinel_injected:
        classifications.append(_sentinel_classification()[0])

    # --- Partition by verdict. ---
    confirmed_rot = [c for c in classifications if c.verdict is Verdict.LINK_ROT]
    needs_review = [c for c in classifications if c.verdict is Verdict.NEEDS_REVIEW]
    healthy = [c for c in classifications if c.verdict is Verdict.HEALTHY]
    transient = [c for c in classifications if c.verdict is Verdict.TRANSIENT]

    run_timestamp = time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime())
    body = render_issue_body(confirmed_rot, sources, run_timestamp)

    # --- Issue I/O is added in T015. For now --dry-run just prints the body. ---
    # (gh create/edit/close wiring is intentionally absent this wave.)
    if args.dry_run:
        print(body)

    if args.json:
        summary = {
            "checked": len(fetch_urls),
            "skipped_cached": 0,          # ledger TTL skip arrives in T010
            "healthy": len(healthy),
            "link_rot": len(confirmed_rot),
            "needs_review": len(needs_review),
            "transient": len(transient),
            "issue_action": "none",       # gh wiring arrives in T015
            "issue_number": None,
            "sentinel_injected": sentinel_injected,
        }
        print(json.dumps(summary, indent=2))

    # Monitor, not gate: success even when link_rot > 0 (rot rides the issue).
    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
