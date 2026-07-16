# CI/CD Deliverables

This document lists all artifacts, reports, and deployed assets produced by the CI/CD pipeline.

---

## Table of Contents

- [Build Artifacts](#build-artifacts)
- [Docker Images](#docker-images)
- [Deployed Assets](#deployed-assets)
- [Test Reports](#test-reports)
- [Security Reports](#security-reports)
- [Performance Reports](#performance-reports)
- [Code Quality Reports](#code-quality-reports)
- [Accessing Deliverables](#accessing-deliverables)

---

## Build Artifacts

Artifacts are stored in GitHub Actions and available for download after each pipeline run.

| Artifact Name | Contents | Retention | Download Size |
|---------------|----------|-----------|---------------|
| `frontend-build` | Compiled React app (HTML, JS, CSS, assets) | 3 days | ~5-20 MB |
| `k6-performance-results` | Load test results (JSON) | 1 day | ~1 MB |
| `bandit-security-report` | Python security scan (JSON) | 1 day | ~100 KB |

### How to Download

**GitHub UI:**
1. Go to **Actions** → Select workflow run
2. Scroll to **Artifacts** section
3. Click artifact name to download

**GitHub CLI:**
```bash
# List artifacts from recent run
gh run view <run-id>

# Download specific artifact
gh run download <run-id> -n frontend-build

# Download all artifacts
gh run download <run-id>
```

---

## Docker Images

Container images are pushed to registries on successful builds.

### GitHub Container Registry (Primary)

| Image | Tags | Registry |
|-------|------|----------|
| `support-api` | `latest`, `main`, `develop`, `<sha>` | `ghcr.io/<org>/<repo>` |

```bash
# Pull latest production image
docker pull ghcr.io/<org>/support-ticket-api:latest

# Pull specific commit
docker pull ghcr.io/<org>/support-ticket-api:<commit-sha>

# Pull staging version
docker pull ghcr.io/<org>/support-ticket-api:develop
```

### Docker Hub (Optional)

| Image | Tags | Registry |
|-------|------|----------|
| `support-api` | `latest`, `main`, `develop`, `<sha>` | `docker.io/<username>/support-api` |

### Image Metadata

Each image includes labels:
- `org.opencontainers.image.source` - Repository URL
- `org.opencontainers.image.revision` - Git commit SHA
- `org.opencontainers.image.created` - Build timestamp

---

## Deployed Assets

### Staging Environment

| Component | Location | URL |
|-----------|----------|-----|
| Frontend | S3: `${STAGING_S3_BUCKET}` | `https://staging.example.com` |
| Backend | ECS: `staging` cluster | `https://staging-api.example.com` |
| CDN | CloudFront: `${STAGING_CLOUDFRONT_ID}` | - |

**Deployed on:** Push to `develop` branch

### Production Environment

| Component | Location | URL |
|-----------|----------|-----|
| Frontend (Blue) | S3: `${PROD_S3_BUCKET}-blue` | - |
| Frontend (Green) | S3: `${PROD_S3_BUCKET}-green` | - |
| Frontend (Active) | CloudFront: `${PROD_CLOUDFRONT_ID}` | `https://example.com` |
| Backend | ECS: `production` cluster | `https://api.example.com` |

**Deployed on:** Push to `main` branch

### Blue-Green Slot Tracking

Active slot is stored in AWS SSM Parameter Store:
```bash
# Check active slot
aws ssm get-parameter --name "/production/active-slot" --query "Parameter.Value"
```

---

## Test Reports

### Unit Test Coverage

| Stack | Tool | Report Location | Dashboard |
|-------|------|-----------------|-----------|
| Backend | pytest-cov | `backend/coverage.xml`, `backend/htmlcov/` | Codecov |
| Frontend | Jest | `frontend/coverage/lcov.info` | Codecov |

**Codecov Dashboard:** `https://codecov.io/gh/<org>/<repo>`

### Test Results

| Test Type | Backend | Frontend |
|-----------|---------|----------|
| Unit | `tests/test_*.py` | `npm run test:unit` |
| Integration | `tests/test_integration*.py` | `npm run test:integration` |
| E2E | `tests/test_api*.py` | `npm run test:e2e` |

---

## Security Reports

### SAST (Static Analysis)

| Tool | Language | Report Format | Location |
|------|----------|---------------|----------|
| CodeQL | Python, JavaScript | SARIF | GitHub Security tab |
| Bandit | Python | JSON | `bandit-security-report` artifact |

### Dependency Scanning

| Tool | Scope | Report Format | Location |
|------|-------|---------------|----------|
| Trivy | All dependencies | SARIF | GitHub Security tab |
| Snyk | npm, pip | Dashboard | Snyk.io |
| Safety | Python | Text | Pipeline logs |
| pip-audit | Python | Text | Pipeline logs |
| npm audit | JavaScript | JSON | Pipeline logs |

### Accessing Security Reports

**GitHub Security Tab:**
1. Go to **Security** → **Code scanning alerts**
2. Filter by tool (CodeQL, Trivy)

**Bandit Report:**
```bash
# Download from artifacts
gh run download <run-id> -n bandit-security-report
cat bandit-report.json | jq '.results'
```

---

## Performance Reports

### Load Testing (k6)

| Metric | Threshold | Report |
|--------|-----------|--------|
| P95 Response Time | < 500ms | `k6-summary.json` |
| P99 Response Time | < 1000ms | `k6-summary.json` |
| Error Rate | < 10% | `k6-summary.json` |
| Request Failure Rate | < 5% | `k6-summary.json` |

**Report Location:** `k6-performance-results` artifact

```bash
# Download and view
gh run download <run-id> -n k6-performance-results
cat k6-summary.json | jq '.metrics'
```

### Lighthouse CI

| Metric | Target | Category |
|--------|--------|----------|
| Performance | > 80 | Core Web Vitals |
| Accessibility | > 90 | A11y |
| Best Practices | > 80 | Security, UX |
| SEO | > 80 | Discoverability |

**Report Location:** 
- Temporary public storage (link in pipeline logs)
- `lighthouse-ci` artifact (if configured)

---

## Code Quality Reports

### SonarCloud

| Metric | Gate | Dashboard |
|--------|------|-----------|
| Code Coverage | > 80% | SonarCloud |
| Duplications | < 3% | SonarCloud |
| Maintainability | A rating | SonarCloud |
| Reliability | A rating | SonarCloud |
| Security | A rating | SonarCloud |

**Dashboard:** `https://sonarcloud.io/project/overview?id=<project-key>`

### Linting Results

| Tool | Language | Location |
|------|----------|----------|
| Flake8 | Python | Pipeline logs |
| Black | Python | Pipeline logs |
| isort | Python | Pipeline logs |
| mypy | Python | Pipeline logs |
| ESLint | JavaScript/TypeScript | Pipeline logs |

---

## Accessing Deliverables

### Quick Reference

| Deliverable | Access Method |
|-------------|---------------|
| Build artifacts | GitHub Actions → Artifacts |
| Docker images | `docker pull ghcr.io/<org>/<repo>:<tag>` |
| Coverage reports | Codecov dashboard |
| Security alerts | GitHub Security tab |
| Code quality | SonarCloud dashboard |
| Performance | k6 artifact or pipeline logs |
| Deployed app | Staging/Production URLs |

### GitHub CLI Commands

```bash
# List recent workflow runs
gh run list --limit 10

# View specific run details
gh run view <run-id>

# Download all artifacts from a run
gh run download <run-id>

# View workflow logs
gh run view <run-id> --log
```

### AWS CLI Commands

```bash
# List S3 bucket contents
aws s3 ls s3://${STAGING_S3_BUCKET}/

# Check ECS service status
aws ecs describe-services --cluster staging --services support-api

# View CloudWatch logs
aws logs tail /ecs/support-api --follow
```

---

## Retention Policy

| Deliverable | Retention |
|-------------|-----------|
| GitHub Artifacts | 3-7 days |
| Docker Images (latest) | Permanent |
| Docker Images (SHA tags) | 90 days |
| Codecov Reports | Permanent |
| SonarCloud History | Permanent |
| S3 Deployments | Current version only |
| CloudWatch Logs | 30 days |

---

## Summary

Each successful pipeline run produces:

1. **Artifacts** - Frontend build, test results, security reports
2. **Docker Image** - Tagged and pushed to container registry
3. **Deployment** - Updated staging or production environment
4. **Reports** - Coverage, security, performance metrics
5. **Notifications** - Slack messages on success/failure
