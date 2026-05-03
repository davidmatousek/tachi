# AC Coverage Migration Guide

**Purpose**: Step-by-step retrofit guide for template adopters whose feature specs contain legacy prose acceptance criteria. After upgrading to Feature 139's verification-first `/aod.deliver`, specs that do not follow the strict Given/When/Then format will fail fast with a pointer back to this document.

**Direction**: `your existing specs → Given/When/Then`. One-time retrofit per in-flight feature. Archive specs (already-shipped features) are optional.

**Sibling guide**: If you also need to migrate away from the deprecated `--require-tests` flag or update delivery templates, see `DELIVERY_HARD_GATE_MIGRATION.md`. This document covers AC-coverage-only.

---

## Who this is for

You are affected if any of the following are true for features you still plan to deliver (or re-deliver) after upgrading:

- Your `spec.md` lists acceptance criteria as plain sentences (e.g., "User can log in with valid credentials")
- Your `spec.md` uses numbered ACs without `**Given**` / `**When**` / `**Then**` prefixes
- Your ACs describe outcomes that are genuinely not automatable (visual design, human approval) but have no machine-readable marker saying so

If every in-flight feature already uses Given/When/Then format, no action is needed — the upgraded `/aod.deliver` will parse those ACs without complaint.

**What the new `/aod.deliver` does on first post-upgrade run against a legacy spec**: The strict parser scans for numbered AC list items beginning with `**Given**`. If the spec has numbered AC entries but none match, the gate halts delivery with a message that names the offending ACs and links to this guide. No commits are made. No "Delivered" status is written. You retrofit the spec, re-run `/aod.deliver`, and proceed.

---

## What changed

The `/aod.deliver` gate previously accepted any prose under an "Acceptance Criteria" heading as sufficient documentation. Feature 139 replaces that with a strict parser that enforces three rules:

1. Each AC in `spec.md` MUST begin with `**Given**` (bold-literal, not italicized, not quoted) and MUST be followed by `**When**` and `**Then**` lines to complete the scenario.
2. Every parsed AC MUST have at least one Gherkin scenario in the E2E suite tagged with its canonical identifier (e.g., `@US-002-AC-1`), OR be marked with an inline `[MANUAL-ONLY] <reason>` escape hatch where `<reason>` is at least 10 characters.
3. When a non-empty spec contains numbered AC list items but none parse as strict-compliant, delivery halts fast with a migration message pointing at this document.

The canonical AC identifier format is `US-{NN}-AC-{N}` — story number (zero-padded) and position within that story's AC list. Scenarios reference the identifier via Gherkin tags so the AC-coverage gate can build a coverage map deterministically.

---

## Before/After retrofit patterns

The five patterns below cover the majority of legacy AC shapes. Retrofit each AC in your spec using whichever pattern fits.

### Pattern 1 — Simple prose to Given/When/Then

Most common shape: a single sentence describing a user action and expected outcome.

```markdown
# BEFORE
**Acceptance Criteria**:
1. User can log in with valid credentials
2. User sees dashboard after successful login
```

```markdown
# AFTER
**Acceptance Scenarios**:

1. **Given** I am an unauthenticated user on the login page, **When** I submit a valid email and password, **Then** I am redirected to the dashboard with a session cookie set.
2. **Given** I have successfully authenticated, **When** the dashboard renders, **Then** my name, email, and a logout control are visible in the header.
```

Note how the retrofit makes the implicit precondition ("unauthenticated user") and the verification surface ("session cookie set", "name/email/logout control visible") explicit — that's the whole point. E2E scenarios can now be written against these specific assertions.

### Pattern 2 — Prose with implicit precondition

Legacy ACs often assume state without stating it. The strict format forces you to surface the Given.

```markdown
# BEFORE
1. Password reset email arrives within 30 seconds
```

```markdown
# AFTER
1. **Given** I have requested a password reset for an account that exists in the system, **When** the backend dispatches the reset email through the configured transactional-email provider, **Then** the recipient inbox receives a deliverable message within 30 seconds of the request timestamp.
```

The "account that exists" precondition was implicit; the E2E test now knows it must provision a real account before measuring latency. The "configured transactional-email provider" surfaces the dependency under test.

### Pattern 3 — Prose with multiple outcomes

A single legacy AC that bundles multiple outcomes must either split into separate ACs or use `And`/`But` clauses within one scenario. Splitting is usually cleaner because it gives each outcome its own identifier and scenario.

```markdown
# BEFORE
1. Invalid credentials show an error message and lock the account after 3 attempts
```

```markdown
# AFTER (split into two ACs — preferred)
1. **Given** I am on the login page with no prior failed attempts for this account, **When** I submit an invalid password, **Then** an error message "Invalid email or password" appears and no account-lock cookie is set.
2. **Given** I have failed authentication twice within the last 15 minutes for the same account, **When** I submit a third invalid password, **Then** the account enters the locked state and subsequent valid-password attempts are rejected for 15 minutes.
```

```markdown
# AFTER (single AC with And clause — acceptable when outcomes are one unit)
1. **Given** I am on the login page with no prior failed attempts, **When** I submit an invalid password, **Then** an error message appears **And** the failed-attempt counter for this account increments by one.
```

### Pattern 4 — Visual or qualitative AC (use `[MANUAL-ONLY]`)

Some ACs describe outcomes that no E2E suite can sensibly verify — visual design review, copy approval from marketing, accessibility manual audit. Mark these with `[MANUAL-ONLY] <reason>` inline so the coverage gate permits the AC without a scenario.

```markdown
# BEFORE
1. Dashboard looks polished and matches brand guidelines
```

```markdown
# AFTER (marker before Given)
1. [MANUAL-ONLY] Visual design review required; copy approval from marketing pending. **Given** the dashboard is rendered in the production-like staging environment, **When** the design team reviews it against brand.md tokens, **Then** they sign off on the rendered output in the delivery document's Manual Validation section.
```

```markdown
# AFTER (marker on Given line — also accepted)
1. **Given** [MANUAL-ONLY] Visual design review required; accessibility manual audit pending. The dashboard is rendered in the production-like staging environment, **When** the design team reviews it against brand.md tokens, **Then** they sign off on the rendered output in the delivery document.
```

Both placements parse. Use whichever reads more naturally. The parser requires the `<reason>` to be at least 10 characters — a deliberate floor to discourage empty or placeholder reasons.

### Pattern 5 — Measurable performance target

Performance ACs must still follow Given/When/Then. Put load conditions in the Given, the measurement action in the When, and the latency/throughput assertion in the Then.

```markdown
# BEFORE
1. Search results load fast
```

```markdown
# AFTER
1. **Given** the index contains 100,000 documents and the search service is warm (at least one prior query within the last 60 seconds), **When** a user submits a single-keyword query with no filters, **Then** the p95 response latency across a 100-request sample MUST be under 500 milliseconds.
```

Vague targets ("fast") disappear. The E2E test can now assert a concrete number against a concrete setup.

---

## `[MANUAL-ONLY]` marker rules

### Syntax

The marker has two legal placements per AC:

```
# Placement A — before the Given line (most readable)
1. [MANUAL-ONLY] <reason ≥10 chars>. **Given** ..., **When** ..., **Then** ...

# Placement B — inline with the Given line
1. **Given** [MANUAL-ONLY] <reason ≥10 chars>. ..., **When** ..., **Then** ...
```

Both are parsed identically. Placement A is recommended because it visually separates the "this AC is not automated" flag from the scenario body.

### Reason length

The `<reason>` following `[MANUAL-ONLY]` MUST be at least 10 characters. The parser enforces this. The ceiling is a soft convention (keep it under 300 characters for readability); nothing rejects longer reasons, but the audit log and delivery document truncate display at the line-atomic budget.

### When to use `[MANUAL-ONLY]`

Legitimate use cases:

- **Visual design review** — colors, typography, spacing, brand-consistency checks that E2E frameworks cannot meaningfully assert
- **Copy approval** — marketing or legal review of user-facing text, where "matches the approved copy document" is a human judgment call
- **External stakeholder validation** — customer demo sign-off, client UAT, regulatory reviewer approval
- **Accessibility manual audit** — screen-reader flow review, cognitive-load assessment, manual keyboard-navigation pass beyond what automated tools (axe-core, WAVE) can catch
- **Physical hardware or real-world conditions** — a scale calibrates, a printer produces an output, a QR code scans under varied lighting

### When NOT to use `[MANUAL-ONLY]`

If any of these apply, the AC should have an automated scenario, not a marker:

- **"Will add tests later"** — time-constrained skipping. Use `--no-tests=<reason>` at delivery time instead; that flag is audited with an explicit opt-out record.
- **"Cannot test in CI"** — usually means the test is mockable or the environment needs work. Investigate before marking manual-only.
- **"Flaky in automation"** — fix the flake. Marker-ing flaky ACs hides real gaps.
- **"Takes too long to run"** — separate concern. Keep the test, run it on a slower cadence (nightly, pre-release).
- **"Reviewer will eyeball it"** — not sufficient. The marker requires a named human or team process, not ambient review.

The marker is a promise that *something* other than automated E2E assertions will verify this AC. If nothing will, the AC should be deleted from the spec (no verification plan = not an AC).

---

## Verifying your retrofit

Retrofit one feature, then confirm the parser accepts it before batch-updating others.

### Step 1 — Run `/aod.analyze` for a static check

```bash
# Option A: slash command (interactive)
/aod.analyze

# Option B: direct bash (scripts a CI check)
bash .aod/scripts/bash/ac-coverage-parse.sh \
  .aod/spec.md \
  <(find tests/e2e -name '*.feature') \
  > /tmp/ac-coverage.json
```

The static check parses your `spec.md` and reports:

- `total_acs`: count of parsed ACs
- `covered_acs`: count of ACs with at least one matching scenario tag
- `uncovered_acs`: names of ACs that have no scenario and no `[MANUAL-ONLY]` marker
- `manual_only_acs`: list of `[MANUAL-ONLY]` ACs with their reasons

If the JSON shows `uncovered_acs` is empty and every AC parsed, you are ready to deliver.

### Step 2 — Run `/aod.deliver` locally against the retrofitted feature

```bash
/aod.deliver
```

Confirm three things in the output:

1. No "uncovered acceptance criteria" halt message.
2. The delivery document's "Test Scenarios" section renders an AC-to-scenario table with every row populated (either a scenario name or `[MANUAL-ONLY] <reason>`).
3. The parser reports every `**Given**` parsed cleanly — no "missing When" or "missing Then" warnings.

If step 2 shows gaps, add the missing scenarios (or mark the AC `[MANUAL-ONLY]` with a valid reason) and re-run.

### Step 3 — Commit the retrofit

```bash
git add .aod/spec.md tests/e2e/*.feature
git commit -m "retrofit(NNN): convert ACs to Given/When/Then format

Addresses Feature 139 AC-coverage enforcement. See docs/guides/AC_COVERAGE_MIGRATION.md.
"
```

The commit is intentionally scoped to the retrofit. Keep it separate from feature work so the diff is reviewable.

---

## Rollout recommendation

1. **Retrofit one in-flight feature first**. Pick the feature you planned to deliver next. Use it as a dry run for the retrofit process. Surface tool gaps or edge cases before they hit everyone.
2. **Retrofit all in-flight features before delivery**. Any feature that has not yet hit `/aod.deliver` will need retrofit before its next delivery attempt. Schedule this work as a one-line task in the feature's tasks.md ("retrofit ACs to Given/When/Then per AC_COVERAGE_MIGRATION.md") — it typically takes 15-45 minutes per feature depending on AC count.
3. **Archive retrofit is OPTIONAL**. Features already shipped (archived in `specs/NNN-*/`) do not need retrofit. Their delivery is done; the old prose ACs stay as historical record. Retrofit these only if you plan to re-deliver (e.g., a major rework). The archive-retrofit has no correctness benefit for shipped work.
4. **Update your team's spec-authoring habit**. New specs created via `/aod.spec` will follow the updated template automatically. Team members drafting ACs by hand should adopt the Given/When/Then format from the start to avoid retrofit work.

### Time budget per retrofit

| Feature AC count | Typical retrofit time |
|---|---|
| 1-5 ACs | 10-15 minutes |
| 6-15 ACs | 15-30 minutes |
| 16-30 ACs | 30-60 minutes |
| 30+ ACs | Split into multiple commits; budget 45-90 minutes |

Most time goes into surfacing implicit preconditions (Pattern 2) and deciding whether to split bundled ACs (Pattern 3). The mechanical reformatting is fast.

---

## Troubleshooting

Common parse failures and their fixes. Run `/aod.analyze` locally to reproduce these before diving in.

### "AC does not begin with **Given**"

```
# WRONG
1. User logs in with valid credentials and sees the dashboard

# ERROR
parse error at spec.md line 42: AC-1 missing **Given** prefix

# FIX
1. **Given** I am an unauthenticated user, **When** I submit valid credentials, **Then** I see the dashboard.
```

The `**Given**` token must be bold-literal (two asterisks on each side) at the start of the AC content. Other bolding (single asterisk, underscores) is not recognized. Leading whitespace after the list-item number is fine; the parser strips it.

### "AC has [MANUAL-ONLY] without a reason"

```
# WRONG
1. [MANUAL-ONLY] **Given** the dashboard renders, **When** reviewed, **Then** it looks good.

# ERROR
parse error at spec.md line 42: AC-1 has [MANUAL-ONLY] marker but reason is empty or whitespace

# FIX
1. [MANUAL-ONLY] Visual design review required; brand compliance sign-off pending. **Given** the dashboard renders, **When** reviewed, **Then** it looks good.
```

The marker requires prose immediately after `[MANUAL-ONLY]` (before the closing period or before the `**Given**` token). An empty-ish marker is rejected.

### "AC reason is fewer than 10 characters"

```
# WRONG
1. [MANUAL-ONLY] TBD. **Given** ...

# ERROR
parse error at spec.md line 42: AC-1 [MANUAL-ONLY] reason "TBD" is 3 chars; minimum is 10

# FIX
1. [MANUAL-ONLY] Copy approval from marketing team required. **Given** ...
```

The 10-character floor exists to discourage placeholder reasons. If you genuinely cannot write 10 characters of justification, the AC probably does not belong in the spec.

### "Multiple Givens in one AC"

```
# WRONG
1. **Given** I am logged in, **Given** I have admin rights, **When** I open the admin panel, **Then** I see user management controls.

# ERROR
parse error at spec.md line 42: AC-1 has 2 **Given** tokens; expected exactly 1

# FIX (use And/But clauses within a single Given block)
1. **Given** I am logged in **And** I have admin rights, **When** I open the admin panel, **Then** I see user management controls.
```

Gherkin's convention is one `Given`, one `When`, one `Then` per scenario. Compound preconditions use `And`/`But` within the Given block. Multiple top-level `**Given**` tokens indicate a spec formatting error.

### "Missing **When** or **Then**"

```
# WRONG
1. **Given** I am logged in, the dashboard is accessible.

# ERROR
parse error at spec.md line 42: AC-1 has **Given** but no **When**

# FIX
1. **Given** I am logged in, **When** I navigate to /dashboard, **Then** the dashboard renders within 2 seconds.
```

All three clauses are mandatory. Partial scenarios are rejected at parse time so uncovered expectations cannot hide in prose fragments.

### "Whole-spec fail-fast with migration pointer"

```
# ERROR (triggered when spec has numbered AC items but none parse strict)
halt: specs/NNN-*/spec.md contains 5 numbered acceptance-criterion items
      but 0 parse in strict Given/When/Then format.
      This is a legacy spec requiring retrofit.
      See: docs/guides/AC_COVERAGE_MIGRATION.md
```

This is the banner error the upgraded `/aod.deliver` emits for unretrofitted specs. Fix by converting at least one AC to Given/When/Then format — the fail-fast triggers only when the spec has ACs AND zero are strict-compliant, not when individual ACs fail.

---

## Further reading

- **ADR-013 — Delivery Verification First** (`docs/architecture/02_ADRs/ADR-013-delivery-verification-first.md`): architectural rationale for the hard-gate flip and the scope of this enforcement.
- **Feature 139 Spec — US-4** (`specs/139-delivery-verified-not-documented/spec.md`): the user story and acceptance scenarios that drove the strict-parser requirement. Ironically, the spec itself is written in the format it enforces — use it as a reference exemplar.
- **Spec template** (`.aod/templates/spec-template.md`): the canonical template new specs inherit. The AC-format rule is documented inline under "Functional Requirements".
- **Sibling migration guide** (`docs/guides/DELIVERY_HARD_GATE_MIGRATION.md`): covers `--require-tests` deprecation, config defaults, and delivery-template updates. Read alongside this document if you are doing a full 139 upgrade.
- **Definition of Done** (`docs/standards/DEFINITION_OF_DONE.md`): how AC-coverage fits into the broader DoD checklist that `/aod.deliver` validates.

---

**Last updated**: 2026-04-23
**Maintained by**: Product Manager + Architect (Triad governance)
**Source**: Feature 139 — Delivery Means Verified, Not Documented
