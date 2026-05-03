# DevOps — Next.js + Supabase Supplement

## Stack Context

Vercel for Next.js hosting (production + automatic preview deployments per PR), Supabase managed PostgreSQL + Auth + Storage + Realtime (separate projects per environment), GitHub Actions for CI pipeline, Prisma for database schema migrations, npm as default package manager, Biome for linting and formatting, environment variables managed through Vercel Dashboard.

## Conventions

- ALWAYS deploy Next.js to Vercel via Git integration -- push to `main` triggers production deployment, push to PR branch triggers preview deployment
- ALWAYS manage environment variables through Vercel Dashboard with separate values for Production, Preview, and Development scopes
- ALWAYS use separate Supabase projects per environment -- never share a Supabase project between production and preview/development
- ALWAYS use Supabase CLI (`supabase start`) for local development -- local Supabase instance with auth, storage, database, and realtime
- ALWAYS run Prisma migrations in CI: `prisma migrate dev` (local), `prisma migrate deploy` (CI/production build step)
- ALWAYS include `prisma generate && next build` as the Vercel build command -- Prisma client must be generated before Next.js build
- ALWAYS run the full CI gate in GitHub Actions before merge: `npx biome check .` → `npx tsc --noEmit` → `npm test` → `next build`
- ALWAYS pin exact dependency versions in `package.json` -- no `^` or `~` prefixes
- ALWAYS commit `package-lock.json` to git -- never delete or gitignore it
- ALWAYS pin Node.js version in `.nvmrc` and match it in Vercel project settings (use current LTS)
- ALWAYS verify Supabase point-in-time recovery is enabled before running production migrations
- ALWAYS migrate the staging Supabase project first -- validate migration success before applying to production
- ALWAYS use Vercel instant rollback to revert a bad production deployment -- never force-push a fix
- ALWAYS configure GitHub branch protection on `main`: require CI status checks, require PR review

## Anti-Patterns

- NEVER deploy from a local machine -- all production and preview deployments go through Vercel Git integration
- NEVER store secrets in `.env` files committed to git -- use Vercel environment variables for deployed environments and `.env.local` (gitignored) for local development
- NEVER expose `SUPABASE_SERVICE_ROLE_KEY` or `DATABASE_URL` with `NEXT_PUBLIC_` prefix -- these are server-only secrets
- NEVER run `prisma migrate deploy` against production without verifying the migration against staging first
- NEVER use yarn -- use npm (or pnpm if the project has `pnpm-lock.yaml`)
- NEVER skip CI checks -- all PRs must pass Biome lint, TypeScript type-check, Vitest tests, and Next.js build before merge
- NEVER use Supabase Dashboard for schema changes -- use Prisma migrations for reproducibility and version control
- NEVER point preview deployments at the production Supabase project -- use a staging project or Supabase branching
- NEVER manually edit Prisma migration files after creation -- generate a new migration instead
- NEVER delete or regenerate `package-lock.json` to fix dependency issues -- resolve conflicts properly

## Guardrails

- Required CI checks before merge: Biome lint (`npx biome check .`), TypeScript (`npx tsc --noEmit`), Vitest (`npm test`), Next.js build (`next build`)
- Required Vercel environment variables: `DATABASE_URL`, `DIRECT_URL`, `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
- Vercel build command: `prisma generate && next build`
- Vercel install command: `npm ci`
- Node.js version: pinned in `.nvmrc` and Vercel settings (LTS)
- GitHub Actions workflow location: `.github/workflows/ci.yml`
- Production deployment: merge to `main` only -- Vercel Git integration handles the rest
- Preview deployment: automatic per PR -- no manual setup required
- Deployment rollback: Vercel instant rollback to previous successful deployment
- Database backup: Supabase point-in-time recovery must be enabled on production project before any migration
- Migration order: local (`prisma migrate dev`) → staging (`prisma migrate deploy`) → production (`prisma migrate deploy`)
- Branch protection on `main`: require passing CI status checks, require at least one PR approval
