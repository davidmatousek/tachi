# Stack Pack Consumer Test Guide

**Purpose**: Validate the full AOD Kit consumer experience — from `git clone` to a working application — using the `nextjs-supabase` stack pack.

**What you're building**: A cybersecurity consulting site (davidmatousek.com) with advisory packages, professional bio, and contact form.

**Time estimate**: ~30 minutes (target for SC-001)

---

## Prerequisites

- Claude Code installed (`claude` CLI)
- Node.js and Git installed
- npm (ships with Node.js)
- GitHub CLI (`gh`) installed and authenticated
- A GitHub account with repo creation permissions

---

## Phase 1: Clone & Initialize

Navigate to your projects directory (e.g., `~/Projects/` or `~/code/`) — the clone command will create a new subfolder here:

```bash
# Clone the public template
git clone https://github.com/davidmatousek/agentic-oriented-development-kit.git davidmatousek-com
cd davidmatousek-com

# Run interactive setup
make init
```

**When prompted, enter:**

| Prompt | Value |
|--------|-------|
| Project Name | `davidmatousek-com` |
| Description | `Cybersecurity consulting site for davidmatousek.com` |
| GitHub Org | `davidmatousek` |
| GitHub Repo | `davidmatousek-com` |
| AI Agent | `1` (Claude Code) |
| Tech Stack | `1` (Next.js + Supabase) |

> **Note**: Selecting a stack pack auto-fills all technology defaults (database, auth, cloud provider, etc.) from its `defaults.env`. No additional prompts needed. The "Other" path prompts for database and cloud provider only.

```bash
# Verify setup
make check
```

**Expected output:**
- All checks pass (green checkmarks)
- 2 stack packs available
- No pack active

### Post-Init Verification

Confirm that `make init` replaced all template placeholders:

```bash
# Should return NO results — all placeholders replaced
grep -rn '{{' .aod/memory/constitution.md
```

> **Note**: When a stack pack is selected during init, its `defaults.env` automatically fills `PostgreSQL`, `Not yet defined`, `Not yet defined`, and `2026-05-04`. No manual editing should be required.

---

## Phase 2: Activate Stack Pack

Open Claude Code in your project directory:

```bash
# CLI
claude

# Or open the project folder in VS Code and use the Claude Code extension
```

Run these commands inside Claude Code:

```
# List available packs — verify both show up
/aod.stack list

# Activate the Next.js pack
/aod.stack use nextjs-supabase

# Scaffold the project structure
/aod.stack scaffold
```

### Verification Checklist

After activation:
- [ ] `.aod/stack-active.json` exists with `"pack": "nextjs-supabase"`
- [ ] `.claude/rules/stack/` contains `conventions.md`, `security.md`, `persona-loader.md`
- [ ] Activation summary shows loaded rules and available persona supplements

After scaffold:
- [ ] `package.json` exists with Next.js, Supabase, and Prisma dependencies
- [ ] `app/layout.tsx` and `app/page.tsx` exist
- [ ] `lib/supabase/client.ts` and `lib/supabase/server.ts` exist
- [ ] `lib/auth/withAuth.ts` exists
- [ ] `prisma/schema.prisma` exists
- [ ] `middleware.ts` exists
- [ ] `biome.json` and `tsconfig.json` exist

---

## Phase 3: Install Dependencies & Review Product Vision

Install the scaffolded project's dependencies:

```bash
npm install
```

> **Note:** If `npm` is not found, you may need to install Node.js (`brew install node` on macOS) or ensure your shell PATH includes it (e.g., `export PATH="/opt/homebrew/bin:$PATH"` for Homebrew).

Then review the seeded product vision that `make init` generated from your project description:

```bash
cat docs/product/01_Product_Vision/product-vision.md
```

You should see your project description as the mission statement, with `[To be refined]` markers for the remaining sections. **Don't fill these in manually** — `/aod.define` in the next phase will walk you through a guided Vision Refinement Workshop to populate them.

---

## Phase 4: AOD Lifecycle (Governance)

```bash
# Create a GitHub repo (needed for issue tracking)
gh repo create davidmatousek/davidmatousek-com --private --source=. --push
```

Run the full Triad workflow inside Claude Code:

```
# Step 1: Define the PRD
/aod.define consulting site for davidmatousek.com — cybersecurity executive consulting with 20+ years experience, 7 advisory packages (AOD Strategy, 6 Pillars Audit, Product-Led Transformation, AI Security Assessment, Secure SDLC Accelerator, Fractional CISO, AOD Mentorship), professional bio, contact form, and booking via Calendly

# Step 2: Create the spec (PM sign-off required)
/aod.spec

# Step 3: Create the technical plan (PM + Architect sign-off required)
/aod.project-plan

# Step 4: Generate tasks (PM + Architect + Team-Lead sign-off required)
/aod.tasks

# Step 5: Build it
/aod.build
```

### Governance Verification

- [ ] `.aod/spec.md` contains PM sign-off block
- [ ] `.aod/plan.md` contains PM + Architect sign-off blocks
- [ ] `.aod/tasks.md` contains PM + Architect + Team-Lead sign-off blocks
- [ ] Feature branch follows `NNN-feature-name` format
- [ ] Each governance gate required approval before proceeding

---

## Phase 5: Validate Stack Pack Impact

After `/aod.build` completes, verify the stack pack conventions were enforced.

### Convention Enforcement

- [ ] Pages use **Server Components** by default (no `"use client"` unless interactive)
- [ ] File structure follows **STACK.md convention** (`app/`, `components/`, `lib/`)
- [ ] Styling uses **Tailwind + shadcn/ui** (no CSS modules, no styled-components)
- [ ] Package manager is **npm** (`package-lock.json` exists)
- [ ] Formatting uses **Biome** (no `.eslintrc`, no `.prettierrc`)

### Security Pattern Enforcement (Contact Form)

- [ ] All form inputs validated with **Zod schemas** (not raw `formData.get()`)
- [ ] Server Action uses **withAuth()** wrapper or server-side session validation
- [ ] Data persisted via **Prisma** parameterized queries (no raw SQL, no `$queryRawUnsafe`)
- [ ] `middleware.ts` enforces auth on protected routes

### Anti-Pattern Absence

- [ ] No Pages Router usage (all routes in `app/`, not `pages/`)
- [ ] No CSS modules (`.module.css` files)
- [ ] No `yarn.lock` or `pnpm-lock.yaml`
- [ ] No `useEffect` for data fetching
- [ ] No `any` types in TypeScript

---

## Phase 6: Deliver

Close the feature with documentation updates and cleanup:

```
# Close the feature
/aod.deliver
```

### Delivery Verification

- [ ] Definition of Done checklist passes
- [ ] Documentation updated (PRD index, changelog, etc.)
- [ ] Feature branch merged or ready for PR
- [ ] Delivery retrospective captured (surprises, lessons learned)

---

## Phase 7: Reversibility Test

```
# Remove the stack pack
/aod.stack remove
```

### Clean Removal Verification

- [ ] `.aod/stack-active.json` is deleted
- [ ] `.claude/rules/stack/` is empty or deleted
- [ ] Project files (`app/`, `lib/`, `prisma/`) are **untouched**
- [ ] Governance artifacts (`.aod/spec.md`, `plan.md`, `tasks.md`) are **untouched**
- [ ] Running `/aod.stack list` shows no active pack

---

## Phase 8 (Bonus): Cross-Session Consistency

Open a **second Claude Code session** in the same project (with the pack re-activated) and ask:

> "Add a new /resources page that lists downloadable security assessment templates"

### Consistency Verification

- [ ] New page uses Server Components (same as Phase 4 output)
- [ ] Styling uses Tailwind + shadcn/ui (same patterns)
- [ ] Any data access uses Prisma (same ORM)
- [ ] File naming follows the same kebab-case convention
- [ ] No contradictory patterns introduced

---

## Success Criteria Summary

| ID | Criterion | Target | Pass/Fail |
|----|-----------|--------|-----------|
| SC-001 | Cold start to `/aod.build` | < 30 minutes | |
| SC-003 | Security patterns in output | 100% (Zod + auth + Prisma) | |
| SC-005 | Pack works end-to-end | Activate + scaffold + build succeeds | |
| SC-006 | Clean reversibility | Zero residual state after remove | |
| SC-007 | Context budget | < 800 lines per invocation | |
| SC-002 | Cross-session consistency | Identical patterns (bonus) | |

---

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| `make init` fails | Ensure Node.js and Git are installed (`node -v`, `git --version`) |
| `/aod.stack use` says pack not found | Verify `stacks/nextjs-supabase/STACK.md` exists |
| Scaffold conflicts with existing files | Choose overwrite/skip per-file when prompted |
| `.env.example` overwrite prompt during scaffold | The base template ships a generic `.env.example`. The scaffold may detect this conflict — choose **Overwrite** to get the stack-specific environment variables |
| Governance sign-off loops | Address reviewer feedback, re-submit until APPROVED |
| `gh repo create` fails | Ensure `gh auth login` completed successfully |

---

## Notes

- This test uses the **public template** repo, not the private `product-led-spec-kit`
- The consulting site content (bio, packages, rates) can be customized during `/aod.define`
- Stack pack conventions are enforced through two surfaces: rules files (passive) and `/aod.build` prompt injection (active)
- Core governance agents (PM, Architect, Team-Lead) are **not** affected by stack packs — they remain stack-agnostic
