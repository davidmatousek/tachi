# Deployment Environments - tachi

**Last Updated**: 2026-03-21
**Owner**: Architect + DevOps

---

## Overview

This directory documents all deployment environments for tachi.

---

## Environment Overview

| Environment | Purpose | URL | Database | Auto-Deploy |
|-------------|---------|-----|----------|-------------|
| **Development** | Local dev | localhost | Local | No |
| **Staging** | Pre-production testing | {{STAGING_URL}} | {{STAGING_DB}} | On PR |
| **Production** | Live users | {{PRODUCTION_URL}} | {{PRODUCTION_DB}} | On merge to main |

---

## Environment Files

### development.md
- Local development setup
- Dependencies and prerequisites
- Environment variables
- Common issues and troubleshooting

### staging.md
- Staging environment configuration
- Access and credentials
- Testing procedures
- Promotion to production checklist

### production.md
- Production infrastructure
- Monitoring and alerts
- Incident response
- Rollback procedures

---

## Environment Variable Strategy

```bash
# Development (.env.local - gitignored)
DATABASE_URL=postgresql://localhost:5432/tachi_dev
API_URL=http://localhost:3001

# Staging (Platform environment variables)
DATABASE_URL={{STAGING_DATABASE_URL}}
API_URL={{STAGING_API_URL}}

# Production (Platform environment variables)
DATABASE_URL={{PRODUCTION_DATABASE_URL}}
API_URL={{PRODUCTION_API_URL}}
```

---

## Deployment Policy

**CRITICAL**: ALL deployments MUST go through the devops agent.

Before deploying:
1. Invoke devops agent (never run deploy commands directly)
2. DevOps reads: `docs/architecture/04_deployment_environments/{env}.md`
3. DevOps reads: `docs/devops/{01_Local|02_Staging|03_Production}/README.md`
4. DevOps outputs verification summary
5. Only then proceed with deployment

---

**Template Instructions**: Create separate markdown files for each environment. Update as infrastructure evolves.
