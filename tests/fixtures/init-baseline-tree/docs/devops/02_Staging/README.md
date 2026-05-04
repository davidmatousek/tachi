# Staging Environment - tachi

**Last Updated**: 2026-05-04
**Owner**: DevOps Agent
**Status**: Template

---

## Overview

Staging is a production-like environment for testing before production deployment.

---

## Infrastructure

**Platform**: {{STAGING_PLATFORM}}
**Region**: {{STAGING_REGION}}

### Services
- **Frontend**: {{STAGING_FRONTEND_URL}}
- **Backend API**: {{STAGING_BACKEND_URL}}
- **Database**: {{STAGING_DATABASE_INFO}}

---

## Deployment

### Automatic Deployment
- **Trigger**: Pull request created/updated
- **Platform**: {{PLATFORM_NAME}} (e.g., Vercel, Netlify)
- **Preview URL**: Auto-generated per PR

### Manual Deployment
```bash
# Deploy to staging
{{DEPLOY_COMMAND}}

# Example for Vercel
vercel --scope={{TEAM}} --env=staging
```

---

## Testing in Staging

### Pre-Production Testing Checklist
- [ ] Create test user accounts
- [ ] Test all critical user workflows
- [ ] Verify database migrations applied
- [ ] Check error tracking is working
- [ ] Validate environment variables
- [ ] Test external integrations

### Smoke Tests
```bash
# Health check
curl {{STAGING_API_URL}}/health

# Basic API test
curl {{STAGING_API_URL}}/api/test
```

---

## Environment Variables

Managed via {{PLATFORM}} dashboard or CLI.

**Access**:
- Dashboard: {{PLATFORM_DASHBOARD_URL}}
- CLI: `{{PLATFORM_CLI}} env ls --scope={{SCOPE}}`

---

## Promotion to Production

### Pre-Promotion Checklist
- [ ] All staging tests passed
- [ ] No errors in staging logs (24 hours)
- [ ] Performance metrics acceptable
- [ ] Security scan passed
- [ ] Database migrations tested
- [ ] Team sign-off obtained

### Promotion Process
1. Verify staging is stable (48 hours minimum)
2. Create production deployment PR
3. Get team approval
4. Merge to main branch
5. Monitor production deployment
6. Verify production health checks

---

**Template Instructions**: Update URLs and platform-specific details.
