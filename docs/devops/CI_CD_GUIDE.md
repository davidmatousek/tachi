# CI/CD Setup Guide - tachi

**Last Updated**: 2026-03-21
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
