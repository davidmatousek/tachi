# DevOps Documentation - tachi

**Last Updated**: 2026-03-21
**Owner**: DevOps Agent
**Status**: Template

---

## Overview

This directory contains deployment and infrastructure documentation for tachi.

---

## Structure

### 01_Local/
Local development environment setup
- Docker Compose configuration
- Development database setup
- Environment variables
- Troubleshooting

### 02_Staging/
Staging environment documentation
- Staging infrastructure
- Deployment procedures
- Testing workflows
- Access credentials

### 03_Production/
Production environment documentation
- Production infrastructure
- Deployment procedures
- Monitoring and alerts
- Incident response
- Pre-deployment checklist

### CI_CD_GUIDE.md
CI/CD setup instructions for common platforms

---

## Deployment Policy (MANDATORY)

**ALL deployments MUST go through the devops agent.**

Before deploying to ANY environment:
1. Invoke devops agent (never run deploy commands directly)
2. DevOps reads: `docs/architecture/04_deployment_environments/{env}.md`
3. DevOps reads: `docs/devops/{01_Local|02_Staging|03_Production}/README.md`
4. DevOps outputs verification summary
5. Only then proceed with deployment

**Never deploy without verification** - Mismatched targets can cause data loss or service disruption.

---

## Environment Strategy

```
Development (Local):
  - Docker Compose for services
  - Local PostgreSQL
  - Fast iteration
  - Cost: $0

Staging ({{STAGING_PLATFORM}}):
  - Production-like configuration
  - Separate database
  - Auto-deploy on PR
  - Cost: {{STAGING_COST}}

Production ({{PRODUCTION_PLATFORM}}):
  - Auto-scaling
  - Monitoring and alerts
  - Manual promotion
  - Cost: {{PRODUCTION_COST}}
```

---

## Quick Links

- [Local Setup](01_Local/README.md)
- [Staging Deployment](02_Staging/README.md)
- [Production Deployment](03_Production/README.md)
- [CI/CD Guide](CI_CD_GUIDE.md)

---

**Maintained By**: DevOps Agent
