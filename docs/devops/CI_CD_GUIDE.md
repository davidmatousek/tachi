# CI/CD Setup Guide - tachi

**Last Updated**: 2026-04-06
**Owner**: DevOps Agent

---

## Overview

This guide provides instructions for setting up CI/CD pipelines for tachi. Choose your platform based on your hosting provider.

---

## When to Add CI/CD

Add CI/CD after you have:
1. ✅ Working local development environment
2. ✅ At least one deployable feature
3. ✅ Basic test coverage (unit tests)
4. ✅ Defined deployment environments

---

## Platform Guides

### GitHub Actions (Recommended)

**Best For**: Projects hosted on GitHub, flexible workflow needs

**Setup**:
1. Create `.github/workflows/ci.yml`
2. Define workflow stages (lint, test, build, deploy)
3. Add repository secrets (Settings → Secrets and Variables)

**Example Workflow**:
```yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      - run: npm ci
      - run: npm test
      - run: npm run lint

  deploy-staging:
    needs: test
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Staging
        run: |
          # Platform-specific deployment command
          echo "Deploy to staging"

  deploy-production:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Production
        run: |
          # Platform-specific deployment command
          echo "Deploy to production"
```

**Resources**:
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

---

### Vercel (Frontend/Full-Stack)

**Best For**: Next.js, React, Vue, static sites

**Setup**:
1. Install Vercel CLI: `npm i -g vercel`
2. Link project: `vercel link`
3. Configure via `vercel.json` or dashboard

**Auto-Deploy**:
- **PR**: Auto-deploys to preview URL
- **main branch**: Auto-deploys to production

**Configuration** (`vercel.json`):
```json
{
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "{{FRAMEWORK}}",
  "regions": ["{{REGION}}"]
}
```

**Resources**:
- [Vercel Documentation](https://vercel.com/docs)
- [GitHub Integration](https://vercel.com/docs/concepts/git/vercel-for-github)

---

### Railway (Backend/Full-Stack)

**Best For**: Node.js, Python, Go, Docker-based apps

**Setup**:
1. Connect GitHub repository
2. Configure build command
3. Set environment variables
4. Define services in `railway.toml`

**Resources**:
- [Railway Documentation](https://docs.railway.app/)

---

### GitLab CI

**Best For**: Projects on GitLab

**Setup**: Create `.gitlab-ci.yml`

**Example**:
```yaml
stages:
  - test
  - deploy

test:
  stage: test
  script:
    - npm ci
    - npm test

deploy:
  stage: deploy
  script:
    - echo "Deploy to production"
  only:
    - main
```

---

### tachi Threat Model (GitHub Actions Adapter)

**Best For**: Automated threat analysis on PRs that modify architecture files

Feature 021 introduced a ready-to-use GitHub Actions workflow at `adapters/github-actions/tachi-threat-model.yml`. This is not a general CI/CD pipeline -- it is a specialized security workflow that runs tachi's 14 threat agents against architecture changes and uploads findings to GitHub Code Scanning.

**Installation**:
```bash
cp adapters/github-actions/tachi-threat-model.yml .github/workflows/
```

**Required Secret**:
| Secret | Description |
|--------|-------------|
| `LLM_API_KEY` | Anthropic API key (set in Settings > Secrets and variables > Actions) |

**Prerequisites**:
- GitHub Actions enabled on the repository
- GitHub Advanced Security enabled (for SARIF upload to Code Scanning)

**Triggers**:
- **Automatic**: Pull requests modifying `docs/architecture/**`, `*.mermaid`, `*.puml`, or `*.drawio`
- **Manual**: Workflow dispatch from the Actions tab with configurable inputs (architecture path, LLM model, max tokens)

**Outputs**:
- `threats.md` -- Full threat model analysis in markdown (downloadable artifact)
- `threats.sarif` -- SARIF 2.1.0 findings uploaded to Code Scanning (visible in Security > Code scanning alerts)

**How It Differs from Standard CI/CD**:
Unlike linting or test workflows, this adapter invokes an LLM API at runtime. It reads source agent prompts from `agents/` and sends architecture input to the Anthropic API. No agent files are copied or transformed -- the orchestrator prompt is used as the system instruction.

**Error Handling**: The workflow handles missing API keys, authentication failures, rate limiting (with retry), timeouts, and empty responses with actionable error messages.

**Full Documentation**: See `adapters/github-actions/README.md` for detailed configuration, permissions, SARIF deduplication, and verification steps.

---

### Automated Release Tagging (release-please)

**Best For**: Automated version tagging, GitHub Release creation, and CHANGELOG generation from conventional commits

Feature 086 introduced a release-please workflow that automates version management. When commits land on `main`, release-please analyzes conventional commit messages and either opens a release PR (bumping the version and updating CHANGELOG.md) or updates an existing release PR with new changes. Merging the release PR creates a GitHub Release with a Git tag.

**Workflow File**: `.github/workflows/release-please.yml`

**Trigger**: Push to `main` branch

**Configuration Files**:
| File | Purpose |
|------|---------|
| `release-please-config.json` | Release type (`simple`), changelog section mapping |
| `.release-please-manifest.json` | Current version baseline (started at `4.0.0`) |

**Changelog Sections** (mapped from conventional commit types):
| Commit Type | Section |
|-------------|---------|
| `feat` | Features |
| `fix` | Bug Fixes |
| `docs` | Documentation |
| `chore`, `refactor`, `perf`, `test`, `style` | Miscellaneous |

**How It Works**:
1. Developer merges a feature branch to `main` (via PR)
2. release-please workflow runs automatically on push
3. If releasable commits exist, release-please opens (or updates) a release PR titled `chore(main): release X.Y.Z`
4. The release PR contains the updated `CHANGELOG.md` and version bump
5. When the release PR is merged, release-please creates a GitHub Release with the corresponding Git tag

**Required Permissions**:
```yaml
permissions:
  contents: write        # Create tags and releases
  pull-requests: write   # Open and update release PRs
```

**No Repository Secrets Required**: release-please uses the default `GITHUB_TOKEN` provided by GitHub Actions.

**Infrastructure Impact**: No new environment variables, Docker services, or deployment changes. The workflow runs entirely within GitHub Actions.

---

## Essential CI/CD Components

### 1. Linting
```yaml
- name: Lint Code
  run: npm run lint
```

### 2. Type Checking
```yaml
- name: Type Check
  run: npm run typecheck
```

### 3. Unit Tests
```yaml
- name: Run Tests
  run: npm test
```

### 4. Build Verification
```yaml
- name: Build Application
  run: npm run build
```

### 5. Security Scanning
```yaml
- name: Security Audit
  run: npm audit --audit-level=moderate
```

---

## Environment Variables in CI/CD

### GitHub Actions
```yaml
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  API_KEY: ${{ secrets.API_KEY }}
  LLM_API_KEY: ${{ secrets.LLM_API_KEY }}  # Required by tachi-threat-model workflow
```

### Vercel
- Set via dashboard: Settings → Environment Variables
- Or CLI: `vercel env add VARIABLE_NAME`

---

## Best Practices

### DO ✅
- Run tests before deployment
- Use separate workflows for staging and production
- Cache dependencies to speed up builds
- Set up failure notifications
- Use environment-specific secrets

### DON'T ❌
- Commit secrets to repository
- Skip tests in CI
- Deploy directly to production without staging
- Ignore failed builds
- Use hardcoded credentials

---

## Monitoring CI/CD

Track these metrics:
- **Build Time**: Target <5 minutes
- **Success Rate**: Target >95%
- **Deployment Frequency**: Measure velocity
- **Mean Time to Recovery**: Track incident response

---

## Troubleshooting

### Build Fails on CI but Works Locally
- Check Node.js versions match
- Verify all dependencies in package.json
- Check environment variables are set
- Review CI logs for specific errors

### Slow Builds
- Enable dependency caching
- Parallelize test suites
- Optimize build commands
- Use smaller Docker base images

---

## Next Steps

After setting up CI/CD:
1. ✅ Add status badges to README
2. ✅ Configure branch protection rules
3. ✅ Set up deployment notifications
4. ✅ Document deployment process in README
5. ✅ Train team on CI/CD workflows

---

**Template Instructions**: Choose ONE platform and set up basic CI/CD. Expand with additional checks as project matures.
