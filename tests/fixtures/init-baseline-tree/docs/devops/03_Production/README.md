# Production Environment - tachi

**Last Updated**: 2026-05-04
**Owner**: DevOps Agent
**Status**: Template
**CRITICAL**: Read pre-deployment checklist before ANY production deployment

---

## Overview

Production environment serves live users. All changes require careful validation.

---

## Infrastructure

**Platform**: {{PRODUCTION_PLATFORM}}
**Region**: {{PRODUCTION_REGION}}

### Services
- **Frontend**: {{PRODUCTION_FRONTEND_URL}}
- **Backend API**: {{PRODUCTION_BACKEND_URL}}
- **Database**: {{PRODUCTION_DATABASE_INFO}}

---

## Deployment

### Pre-Deployment Checklist (MANDATORY)

**CRITICAL**: Complete this checklist before EVERY production deployment.

#### Code Validation
- [ ] All tests passing in CI/CD
- [ ] Code review approved
- [ ] Security scan passed
- [ ] Performance benchmarks met

#### Infrastructure Validation
- [ ] Staging deployment successful (48 hours minimum)
- [ ] Database migrations tested in staging
- [ ] Environment variables verified
- [ ] Rollback plan documented

#### Stakeholder Approval
- [ ] PM sign-off (if feature change)
- [ ] Architect sign-off (if infrastructure change)
- [ ] Team-lead sign-off (capacity confirmed)

#### Monitoring Setup
- [ ] Error tracking configured
- [ ] Performance monitoring active
- [ ] Alerts configured
- [ ] Logs accessible

### Deployment Process

```bash
# 1. Invoke devops agent (REQUIRED)
# Use Task tool or agent command

# 2. DevOps agent reads:
#    - docs/architecture/04_deployment_environments/production.md
#    - docs/devops/03_Production/README.md

# 3. DevOps outputs verification summary

# 4. If verification passes, proceed with deployment
{{DEPLOY_COMMAND}}

# Example for Vercel
vercel --prod --scope={{TEAM}}
```

### Post-Deployment Validation

**Immediate (0-5 minutes)**:
- [ ] Health check endpoint responding
- [ ] Frontend loads successfully
- [ ] API endpoints accessible
- [ ] No 500 errors in logs

**Short-term (5-30 minutes)**:
- [ ] User workflows functioning
- [ ] Database queries performing well
- [ ] Error rate within baseline
- [ ] Response times within SLA

**Long-term (30 minutes - 24 hours)**:
- [ ] Monitor error trends
- [ ] Watch performance metrics
- [ ] User feedback monitoring
- [ ] Resource utilization normal

---

## Monitoring

### Health Checks
```bash
# API health
curl {{PRODUCTION_API_URL}}/health

# Database health
# (Platform-specific command)
```

### Key Metrics
- **Response Time**: Target p95 <500ms
- **Error Rate**: Target <1%
- **Uptime**: Target 99.9%
- **Database Connections**: Monitor pool usage

### Alerts
Configure alerts for:
- Error rate > 5%
- Response time p95 > 1000ms
- Server errors (5xx)
- Database connection failures

---

## Incident Response

### Severity Levels

**P0 - Critical**:
- Service completely down
- Data loss risk
- Security breach
- **Response**: Immediate (within 15 minutes)

**P1 - High**:
- Major feature broken
- Significant performance degradation
- **Response**: Within 1 hour

**P2 - Medium**:
- Minor feature issues
- Limited user impact
- **Response**: Within 4 hours

**P3 - Low**:
- Cosmetic issues
- Low user impact
- **Response**: Next business day

### Incident Response Process

1. **Detect**: Alert triggered or user report
2. **Assess**: Determine severity
3. **Communicate**: Notify team (Slack/Discord/Email)
4. **Investigate**: Identify root cause
5. **Resolve**: Deploy fix or rollback
6. **Verify**: Confirm resolution
7. **Document**: Post-mortem (5 Whys)

---

## Rollback Procedures

### When to Rollback
- Critical bugs affecting >10% of users
- Data integrity issues
- Security vulnerabilities
- Performance degradation >50%

### Rollback Process

**Immediate Rollback** (Platform-dependent):
```bash
# Example for Vercel
vercel rollback

# Example for Git-based
git revert <commit-sha>
git push origin main
```

**Post-Rollback**:
1. Verify service restored
2. Identify root cause
3. Fix in development
4. Re-test in staging
5. Re-deploy with fix

---

## Backup and Recovery

### Database Backups
- **Frequency**: {{BACKUP_FREQUENCY}}
- **Retention**: {{BACKUP_RETENTION}}
- **Location**: {{BACKUP_LOCATION}}

### Recovery Procedures
```bash
# Restore from backup
{{RESTORE_COMMAND}}
```

---

## Access and Credentials

**Platform Dashboard**: {{PLATFORM_DASHBOARD_URL}}
**Monitoring**: {{MONITORING_DASHBOARD_URL}}
**Error Tracking**: {{ERROR_TRACKING_URL}}

**Access Control**:
- Production access limited to: {{AUTHORIZED_TEAM}}
- Emergency access: {{EMERGENCY_CONTACT}}

---

**Template Instructions**: Replace all `{{TEMPLATE_VARIABLES}}`. Review and update this document monthly.
