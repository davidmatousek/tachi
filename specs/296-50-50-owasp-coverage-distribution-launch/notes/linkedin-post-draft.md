# LinkedIn Post — DRAFT (T017)

**Status**: DRAFT (Wave 3, 2026-05-28) — ready for T018 publication.
**Target publish**: Day 4 AM (or Day 5 AM if Wave 2 slipped) — **BLOCKED by T016 (Cybersec article merge) per Q2 lean.**
**Publication surface**: maintainer LinkedIn account (web or mobile), native-content-first.
**URL capture target**: `specs/296-50-50-owasp-coverage-distribution-launch/notes/linkedin-post-url.txt` (T018).

## Blocking dependency (Q2 lean = publish AFTER article merge)

Per spec FR-002 + plan §Q2 lean (c): this post MUST publish **after** the Cybersec article (T016) merges, because the post body links to the article. At publication (T018) the article URL in the body MUST resolve 200 OK.

> **OPEN ITEM for T018**: the merged Cybersec article URL is not yet recorded in `notes/cybersec-article-pr-url.txt`. Also note a repo-name ambiguity — the maintainer profile links the content repo as `davidmatousek/DavidMatousek-Cybersecurity-Content`, while plan.md/tasks.md reference `davidmatousek/Cybersecurity-Content`. **Resolve the canonical article URL and confirm the repo name before publishing**, then replace the `[Cybersec article URL]` token in the body below.

## Tone discipline anchor (spec US-2 AC-1; plan §Wave 3; PRD H-1 framing)

Name the **gap** (Daniel Wood's specific BLP-02 feedback) → name the **fix** (six BLP-02 features through v4.36.0) → ship the **receipts** (PR #293). **No sycophancy**, no "excited to announce", no hashtag spam. The post earns reach by being verifiable, not promotional.

## Post body (native-content-first, ~250 words — publish this between the `---` markers)

---

50/50 OWASP coverage milestone for tachi — every catalogued threat in LLM 2025, Agentic 2026, ML 2023, Mobile 2024, and Web/API 2021/2023 now has a detection agent.

What "10/10" means, precisely: the agent for each framework slot catches every threat catalogued in that OWASP framework. Not zero-false-positive, not whole-application coverage — catalogued-threat coverage, with reproducible verification.

This milestone responds to Daniel Wood's BLP-02 enterprise-hardening thread (2026-05-02), which flagged three gaps in tachi's enterprise posture. Three iterations later, all six BLP-02 features shipped through v4.36.0 (2026-05-14), and the 50/50 coverage closure (BLP-01) landed 2026-05-01.

How to verify it yourself, without trusting a marketing claim: clone tachi, run `/tachi.security-report` on any example architecture with `SOURCE_DATE_EPOCH=1700000000` set, and the Coverage Attestation page bytes match the committed baseline. Byte-deterministic anchor — ADR-021 + ADR-029 + ADR-037.

Full per-bucket breakdown + the verification walkthrough: [Cybersec article URL]

Repo: https://github.com/pratik-saptarshi/tachi-rust
BLP-02 closure receipts: https://github.com/pratik-saptarshi/tachi-rust/pull/293

---

## LinkedIn algorithm discipline (2026 — plan §Wave 3 + research §4)

- **Native content first**: the core insight (what 50/50 means + how to verify) lives in the post body, not behind a link.
- **Article URL in-body is acceptable**: link-in-body reduces reach ~18.8%, but link-in-comments-as-primary-CTA is suppressed ~80%. In-body is the lesser penalty. Keep the article link in the body as drafted.
- **No hashtags**: LinkedIn 2026 topic detection replaced the hashtag signal; hashtag spam now reads as noise.
- **Timing**: schedule for peak-audience window — the first 60–90 min of engagement governs total reach. Post during a weekday business-hours window for the maintainer's audience.

## Receipts verified at draft time (2026-05-28)

| Claim | Source | Status |
|---|---|---|
| BLP-01 50/50 closure shipped 2026-05-01 | project memory `project_blp01_threat_coverage.md` | ✓ |
| BLP-02 6/6 features through v4.36.0 (2026-05-14) | project memory `project_blp02_enterprise_hardening.md` | ✓ |
| PR #293 = BLP-02 closure (F-292/F-6) | git history + memory | ✓ |
| Daniel Wood BLP-02 thread 2026-05-02 | plan.md §Wave 3 template | ✓ (attribution preserved verbatim) |
| Coverage Attestation byte-determinism (ADR-021/029/037) | plan.md §Wave 3 | ✓ |

## Pre-publication checklist (T018 — re-run before posting)

- [ ] Cybersec article merged (T016 complete) and canonical URL resolved + 200 OK.
- [ ] `[Cybersec article URL]` token replaced with the real URL in the body.
- [ ] Repo-name ambiguity resolved (`Cybersecurity-Content` vs `DavidMatousek-Cybersecurity-Content`).
- [ ] tachi repo link resolves (200 OK).
- [ ] PR #293 link resolves (200 OK).
- [ ] No asset-tag mention present (FR-007 sequencing guard).
- [ ] No sycophancy / no hashtag spam.
- [ ] Daniel Wood attribution reads as gap-naming, not flattery.
- [ ] Posted during peak-audience window.
- [ ] URL captured to `notes/linkedin-post-url.txt` immediately after publication (SC-009 timestamp must post-date `narrative-defensibility-check.md` first commit).

## US-2 AC-3 note (T019 — non-automatable)

Algorithmic-reach validation is maintainer judgment. After publishing, record in `notes/linkedin-post-url.txt`: the chosen format (native-content-first), the article-URL location (body vs first comment — drafted as in-body), and the publication time window. Reach metrics observation is deferred to F-3 (BLP-04 Wave 2 adoption-signal capture).
