# CI/CD Workflow Guide

This guide explains how to use the GitHub Actions CI/CD pipeline for the Support Ticket API project.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Branch Strategy](#branch-strategy)
- [GitHub Secrets Setup](#github-secrets-setup)
- [Pipeline Stages](#pipeline-stages)
- [Triggering Deployments](#triggering-deployments)
- [Monitoring Pipeline Runs](#monitoring-pipeline-runs)
- [Rollback Procedures](#rollback-procedures)
- [Troubleshooting](#troubleshooting)

---

## Overview

The project uses **GitHub Actions** for CI/CD with three workflow files:

| Workflow | File | Purpose |
|----------|------|---------|
| Full CI/CD | `ci-cd.yml` | Standard build, test, deploy pipeline |
| PR Checks | `pr-checks.yml` | Code quality gates for pull requests |
| Optimized Pipeline | `optimized-pipeline.yml` | Advanced pipeline with blue-green deployments |

---

## Prerequisites

Before using the CI/CD pipeline:

1. **GitHub Repository**: Push your code to GitHub
2. **AWS Account**: For S3, CloudFront, ECS deployments
3. **Docker Hub Account** (optional): For container registry
4. **Monitoring Tools** (optional): Datadog, Slack for notifications

---

## Branch Strategy

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Feature   │────▶│   develop   │────▶│    main     │
│   Branch    │     │  (Staging)  │     │ (Production)│
└─────────────┘     └─────────────┘     └─────────────┘
                           │                   │
                           ▼                   ▼
                    Deploy to Staging   Deploy to Production
```

### Branch Rules

| Branch | Triggers | Deployment Target |
|--------|----------|-------------------|
| `feature/*` | PR checks only | None |
| `develop` | Full pipeline | **Staging** |
| `main` | Full pipeline + performance tests | **Production** |

### Workflow

1. Create feature branch from `develop`
2. Open PR to `develop` → PR checks run
3. Merge to `develop` → Deploys to staging
4. Open PR from `develop` to `main`
5. Merge to `main` → Deploys to production (blue-green)

---

## GitHub Secrets Setup

Navigate to: **Repository → Settings → Secrets and variables → Actions**

### Required Secrets

#### AWS Credentials
```
AWS_ACCESS_KEY_ID        # IAM user access key
AWS_SECRET_ACCESS_KEY    # IAM user secret key
```

#### S3 Buckets
```
STAGING_S3_BUCKET        # e.g., my-app-staging
PROD_S3_BUCKET           # e.g., my-app-production
```

#### CloudFront
```
STAGING_CLOUDFRONT_ID    # CloudFront distribution ID for staging
PROD_CLOUDFRONT_ID       # CloudFront distribution ID for production
```

#### Docker (if using Docker Hub)
```
DOCKER_USERNAME          # Docker Hub username
DOCKER_PASSWORD          # Docker Hub access token
```

#### Notifications
```
SLACK_WEBHOOK            # Slack incoming webhook URL
```

#### Security Scanning
```
SONAR_TOKEN              # SonarCloud token
SNYK_TOKEN               # Snyk API token
```

#### Monitoring
```
DATADOG_API_KEY          # Datadog API key
```

### Repository Variables

Navigate to: **Settings → Secrets and variables → Actions → Variables**

```
AWS_REGION               # e.g., us-east-1
STAGING_URL              # e.g., https://staging.example.com
PRODUCTION_URL           # e.g., https://example.com
API_URL                  # Backend API URL for frontend build
```

---

## Pipeline Stages

### Standard Pipeline (`ci-cd.yml`)

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Backend Test │    │Frontend Test │    │              │
│   (pytest)   │    │   (jest)     │    │              │
└──────┬───────┘    └──────┬───────┘    │              │
       │                   │            │              │
       ▼                   ▼            │              │
┌──────────────┐    ┌──────────────┐    │              │
│Backend Build │    │Frontend Build│    │              │
│   (Docker)   │    │   (npm)      │    │              │
└──────┬───────┘    └──────┬───────┘    │              │
       │                   │            │              │
       └─────────┬─────────┘            │              │
                 │                      │              │
                 ▼                      │              │
       ┌─────────────────┐              │              │
       │ Deploy Staging  │◀─────────────┤ develop      │
       │    (S3/ECS)     │              │              │
       └─────────────────┘              │              │
                                        │              │
       ┌─────────────────┐              │              │
       │Deploy Production│◀─────────────┤ main         │
       │    (S3/ECS)     │              │              │
       └─────────────────┘              │              │
```

### Optimized Pipeline (`optimized-pipeline.yml`)

**8 Stages:**

1. **Build** - Parallel frontend/backend builds with caching
2. **Code Quality** - Black, isort, Flake8, ESLint, SonarCloud
3. **Security SAST** - CodeQL analysis
4. **Security Dependencies** - Trivy, Snyk, Bandit, npm audit
5. **Testing** - Matrix: unit/integration/e2e tests
6. **Performance** - k6 load tests, Lighthouse CI
7. **Deploy** - Blue-green deployment with health checks
8. **Monitoring** - Datadog events, deployment tracking

---

## Triggering Deployments

### Automatic Triggers

| Action | Result |
|--------|--------|
| Push to `develop` | Deploy to staging |
| Push to `main` | Deploy to production |
| Open PR to `main` | Run PR checks (no deploy) |

### Manual Deployment

For emergency deployments, use workflow dispatch:

1. Go to **Actions** tab in GitHub
2. Select **Optimized CI/CD Pipeline**
3. Click **Run workflow**
4. Options:
   - `skip_tests`: Set to `true` for emergency deploy
   - `environment`: Choose `staging` or `production`

```bash
# Or via GitHub CLI
gh workflow run optimized-pipeline.yml \
  -f skip_tests=true \
  -f environment=production
```

---

## Monitoring Pipeline Runs

### GitHub Actions UI

1. Go to **Actions** tab
2. Click on the workflow run
3. View job logs and artifacts

### Notifications

- **Slack**: Automatic notifications on deploy success/failure
- **GitHub**: Deployment status in commit history

### Artifacts

Each run produces artifacts:
- `frontend-build` - Built frontend assets
- `k6-performance-results` - Load test results
- `bandit-security-report` - Security scan results

Download from the workflow run page.

---

## Rollback Procedures

### Automatic Rollback

The optimized pipeline includes automatic rollback:

1. Deploys to inactive slot (blue/green)
2. Runs health checks (30 attempts)
3. Monitors for 5 minutes
4. If error rate > 20%, triggers rollback
5. Switches traffic back to previous slot

### Manual Rollback

#### Option 1: Revert Commit

```bash
# Revert the problematic commit
git revert HEAD
git push origin main
# Pipeline will deploy the reverted state
```

#### Option 2: Redeploy Previous Version

```bash
# Find the last working commit
git log --oneline -10

# Create a branch from that commit
git checkout -b hotfix/rollback <commit-sha>
git push origin hotfix/rollback

# Merge to main
gh pr create --base main --head hotfix/rollback --title "Rollback to stable"
gh pr merge --merge
```

#### Option 3: AWS Console (Emergency)

For S3/CloudFront:
```bash
# Restore previous S3 version
aws s3 sync s3://backup-bucket/ s3://prod-bucket/ --delete

# Invalidate CloudFront
aws cloudfront create-invalidation --distribution-id XXXXX --paths "/*"
```

For ECS:
```bash
# Rollback to previous task definition
aws ecs update-service --cluster production \
  --service support-api \
  --task-definition support-api:PREVIOUS_VERSION
```

---

## Troubleshooting

### Common Issues

#### 1. Pipeline fails at "Install dependencies"

**Cause**: Cache corruption or version mismatch

**Fix**: Clear cache
```yaml
# Bump CACHE_VERSION in workflow file
env:
  CACHE_VERSION: v3  # was v2
```

#### 2. Docker build fails

**Cause**: Missing Dockerfile or build context

**Fix**: Ensure `backend/Dockerfile` exists and is valid

#### 3. Deploy fails with AWS credentials error

**Cause**: Expired or invalid AWS credentials

**Fix**: 
1. Regenerate IAM access keys
2. Update `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` secrets

#### 4. Health check fails after deployment

**Cause**: Application not starting correctly

**Fix**:
1. Check ECS/container logs
2. Verify environment variables
3. Check database connectivity

#### 5. Tests pass locally but fail in CI

**Cause**: Environment differences

**Fix**:
- Check Python/Node versions match
- Verify test database configuration
- Check for hardcoded localhost URLs

### Viewing Logs

```bash
# GitHub CLI - view recent runs
gh run list --limit 5

# View specific run logs
gh run view <run-id> --log

# Download artifacts
gh run download <run-id>
```

### Re-running Failed Jobs

1. Go to the failed workflow run
2. Click **Re-run failed jobs** (top right)
3. Or re-run entire workflow: **Re-run all jobs**

---

## Quick Reference

### Commands

```bash
# Push to trigger staging deploy
git push origin develop

# Push to trigger production deploy
git push origin main

# View pipeline status
gh run list

# Manual deploy
gh workflow run optimized-pipeline.yml

# Cancel running workflow
gh run cancel <run-id>
```

### Key URLs

| Resource | URL |
|----------|-----|
| GitHub Actions | `https://github.com/<org>/<repo>/actions` |
| Staging | Configured in `STAGING_URL` variable |
| Production | Configured in `PRODUCTION_URL` variable |
| Swagger Docs | `<API_URL>/apidocs/` |

---

## Support

For pipeline issues:
1. Check workflow logs in GitHub Actions
2. Review this guide's troubleshooting section
3. Check AWS CloudWatch logs for deployment issues
