# GitHub Profile Refresh — SHIPPED IN PR #1 (T020)

**Status**: PR #1 OPEN (https://github.com/davidmatousek/davidmatousek/pull/1) — content finalized 2026-05-28; pending maintainer self-merge (T021, ≥24h cooling-off).
**Canonical content**: PR #1 (8 commits) is the source of truth. The minimal draft below is the original proposal, retained for history.

## Final shipped direction (supersedes the minimal draft below)

Per explicit maintainer direction, T020 was reframed from the minimal Q7 flagship-row delta into a **full profile repositioning for a CISO / VP Cybersecurity audience**:

- **Lead**: "Cybersecurity Leader · Application, AI & Cloud Security · Risk & Compliance" (no longer "fractional CISO"-led; fractional CISO kept as a supporting credential).
- **Hook**: "I don't just advise on security — I build it. Creator of [tachi] and [AOD]."
- **What I build**: tachi (flagship, OWASP 50/50 tagline + STRIDE+AI+MAESTRO one-liner) + AOD — Agentic Oriented Development (newly launched, agentic-oriented-development.com, repo secondary).
- **Tone**: confident, not soliciting (rejected "If you're hiring…"); CISO/VP keywords kept in the capstone as the operating level.
- **Removed**: retired "LinkedIn Top Voice in Cybersecurity" credential (program discontinued).
- **US-4 AC mapping**: AC-1 (tachi first viewport) — met via hook; detailed flagship block is mid-page under "What I build". AC-2 (50/50 tagline) ✓. AC-3 (STRIDE+AI one-liner) ✓. AC-4 (AOD visible) ✓ — AOD elevated to co-flagship.
- **Exceeds** PRD Q7 "minimal" lean by maintainer choice — the profile now serves David's career positioning, with tachi/AOD as proof-of-building. See project memory `user_career_positioning.md` + `feedback_no_linkedin_top_voice.md`.

**Open (maintainer)**: self-merge after cooling-off (T021); optional — keep/drop side projects (GitHubDevOps, StockWatcher); confirm the Cybersecurity Content repo link (`DavidMatousek-Cybersecurity-Content`).

---

_[original minimal draft retained below for history]_

**Discipline**: `[MANUAL-ONLY]` — PR open + ≥24h hold + self-merge (T021) are maintainer actions (R4 mitigation).
**URL capture target**: `specs/296-50-50-owasp-coverage-distribution-launch/notes/profile-pr-url.txt`.

## US-4 acceptance anchors

- **AC-1**: profile README **first viewport** contains the tachi flagship surface.
- **AC-2**: 50/50 OWASP coverage tagline present.
- **AC-3**: STRIDE+AI threat-modeling harness one-line description present.
- **AC-4**: AOD-Kit secondary position — visible, not removed.
- Footer wording at author discretion within ADR-044 dual-frame alignment (Architect plan-layer L-3).

## Reconciliation note (template vs real profile)

The plan §Wave 3 template assumed standalone `## Flagship project` / `## Methodology backing` sections. The **actual** profile uses an `## Open Source` block with `### Security Tooling` / `### Agentic Development` / `### Developer Tools` tables (tachi + AOD-Kit already present, lower on the page). To satisfy US-4 AC-1 ("first viewport"), the recommended delta **elevates** tachi with a compact flagship block high on the page, and refreshes the existing table row for consistency. AOD-Kit's existing row is untouched (AC-4 satisfied).

---

## RECOMMENDED DELTA (minimal — ~+8 lines, 1 row edited)

### Edit 1 — insert flagship block immediately AFTER the intro bio paragraph and BEFORE `## What I'm Working On`

Insert this block (lands tachi in the first viewport per AC-1):

```markdown
## Flagship project: tachi

**[tachi](https://github.com/pratik-saptarshi/tachi-rust)** — Threat Modeling and Vulnerability Detection Harness for Claude Code. An AI-reasoning security scanner (STRIDE + AI + MAESTRO) that reasons over your architecture description to catch the logic-level risks SAST can't reach. **OWASP 50/50 coverage** across LLM 2025 + Agentic 2026 + ML 2023 + Mobile 2024 + Web/API 2021/2023 — every catalogued threat in all five frameworks has a detection agent, with byte-deterministic reproducible verification.
```

### Edit 2 — refresh the existing tachi row in the `### Security Tooling` table (consistency)

**Before:**
```markdown
| [tachi](https://github.com/pratik-saptarshi/tachi-rust) | Automated threat modeling toolkit. STRIDE + AI-specific threats in one command. |
```

**After:**
```markdown
| [tachi](https://github.com/pratik-saptarshi/tachi-rust) | STRIDE + AI + MAESTRO threat-modeling harness for Claude Code. OWASP 50/50 coverage (LLM + Agentic + ML + Mobile + Web/API). |
```

### What stays unchanged (deliberate)

- `## What I'm Working On` (AOD book series) — maintainer's existing content, untouched.
- AOD-Kit row in `### Agentic Development` table — secondary, visible (AC-4). ✓
- `### Developer Tools` table, `## Connect`, social badges/footer — unchanged (author discretion, ADR-044 alignment satisfied by no-change).

---

## ALTERNATIVE (if the maintainer prefers the literal plan template)

Add both template sections (`## Flagship project: tachi` + `## Methodology backing: AOD-Kit`) as a standalone pair above `## Open Source`, and remove the now-redundant tachi + AOD-Kit rows from the Open Source tables. ~20-line delta, larger, more restructuring. The recommended delta above is preferred for Q7 minimalism + lower review surface.

> **OPEN ITEM (out of scope for T020, flag-only)**: the `### Security Tooling` "Cybersecurity Content" row links `davidmatousek/DavidMatousek-Cybersecurity-Content`, while F-1's article PR targets `davidmatousek/Cybersecurity-Content`. Confirm the canonical content-repo name (ties into the T018 LinkedIn article-URL resolution). Do NOT fix it inside the T020 PR unless the maintainer chooses to.

## PR-open instructions (T020 — MANUAL-ONLY maintainer action)

The profile repo is external (`davidmatousek/davidmatousek`) and not cloned locally. To open the PR:

```bash
# 1. Clone (or cd into an existing clone)
gh repo clone davidmatousek/davidmatousek /tmp/profile-refresh && cd /tmp/profile-refresh

# 2. Branch
git checkout -b refresh-tachi-flagship-50-50

# 3. Apply Edit 1 + Edit 2 above to README.md (and/or profile/README per repo layout)

# 4. Commit + push + open PR
git add README.md
git commit -m "docs: elevate tachi to flagship — 50/50 OWASP coverage tagline"
git push -u origin refresh-tachi-flagship-50-50
gh pr create --title "docs: tachi flagship refresh — 50/50 OWASP coverage" \
  --body "Elevates tachi to a flagship surface with the 50/50 OWASP coverage tagline + STRIDE+AI+MAESTRO one-liner. AOD-Kit secondary, visible. Minimal scope (no 'Now' section) per F-296 Q7 lean."

# 5. Record PR URL
echo "<PR_URL>" > /Users/david/Projects/tachi/specs/296-50-50-owasp-coverage-distribution-launch/notes/profile-pr-url.txt
```

## Pre-merge checklist (T021 — after ≥24h hold)

- [ ] Render before/after on github.com (R4 mitigation).
- [ ] First viewport shows the tachi flagship block (AC-1).
- [ ] 50/50 tagline present (AC-2); STRIDE+AI one-liner present (AC-3).
- [ ] AOD-Kit still visible (AC-4).
- [ ] No asset-tag mention (FR-007 sequencing guard).
- [ ] Self-merge after ≥24h hold; update `notes/profile-pr-url.txt` with merged-state URL.
