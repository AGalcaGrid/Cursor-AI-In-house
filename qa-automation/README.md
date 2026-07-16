# QA Automation Suite

Comprehensive QA automation system for the CoursorProject workspace. Includes automated testing, code quality checks, security scanning, performance monitoring, and AI-generated improvement recommendations.

## 📁 Directory Structure

```
qa-automation/
├── tests/
│   ├── unit/                    # Unit tests (pytest)
│   ├── integration/             # Integration tests
│   ├── e2e/                     # End-to-end tests (Selenium)
│   │   └── pages/               # Page Object Model
│   └── performance/             # Performance tests
├── quality/
│   ├── eslint.config.js         # Frontend linting
│   ├── pylint.rc                # Backend linting
│   └── sonar-project.properties # SonarQube config
├── security/
│   ├── zap-config.yaml          # OWASP ZAP configuration
│   ├── snyk.config              # Snyk configuration
│   └── security-scan.sh         # Security scanning script
├── performance/
│   ├── lighthouse.config.js     # Lighthouse CI config
│   ├── k6-load-test.js          # k6 load testing
│   └── performance-thresholds.json
├── reports/
│   └── generate-report.py       # Dashboard generator
├── scripts/
│   ├── run-all-qa.sh            # Master QA script
│   └── analyze-results.py       # AI recommendations
└── requirements.txt             # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

```bash
# Python dependencies
pip install -r qa-automation/requirements.txt

# Node.js dependencies (for frontend testing)
npm install -g lighthouse @lhci/cli

# k6 for load testing (macOS)
brew install k6

# OWASP ZAP (Docker)
docker pull owasp/zap2docker-stable
```

### Run Complete QA Suite

```bash
# Make script executable
chmod +x qa-automation/scripts/run-all-qa.sh

# Run all QA checks
./qa-automation/scripts/run-all-qa.sh
```

## 🧪 Testing

### Unit Tests (Backend)

```bash
# Run pytest with coverage
pytest tests/unit/ -v --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_api_endpoints.py -v
```

### Unit Tests (Frontend)

```bash
cd frontend
npm run test -- --coverage
```

### Integration Tests

```bash
pytest qa-automation/tests/integration/ -v
```

### E2E Tests (Selenium)

```bash
# Set environment variables
export BASE_URL=http://localhost:3000
export HEADLESS=true

# Run E2E tests
pytest qa-automation/tests/e2e/ -v
```

### E2E Tests (Playwright)

```bash
npx playwright test
```

## 📝 Code Quality

### ESLint (Frontend)

```bash
cd frontend
npx eslint src/ --config ../qa-automation/quality/eslint.config.js
```

### Pylint (Backend)

```bash
pylint app/ --rcfile=qa-automation/quality/pylint.rc
```

### SonarQube Analysis

```bash
sonar-scanner -Dproject.settings=qa-automation/quality/sonar-project.properties
```

## 🔒 Security Scanning

### Run All Security Scans

```bash
chmod +x qa-automation/security/security-scan.sh
./qa-automation/security/security-scan.sh
```

### Individual Scans

```bash
# npm audit
npm audit --json > reports/security/npm-audit.json

# pip-audit
pip-audit -r requirements.txt --format json

# Bandit (Python security)
bandit -r app/ -f json -o reports/security/bandit.json

# OWASP ZAP
docker run -t owasp/zap2docker-stable zap-baseline.py -t http://localhost:3000
```

## ⚡ Performance Testing

### Lighthouse Audit

```bash
# Single audit
npx lighthouse http://localhost:3000 --output=html --output-path=qa-automation/reports/lighthouse.html

# Lighthouse CI
npx lhci autorun --config=qa-automation/performance/lighthouse.config.js
```

### k6 Load Testing

```bash
# Run load test
k6 run qa-automation/performance/k6-load-test.js

# Run with custom options
k6 run --vus 50 --duration 5m qa-automation/performance/k6-load-test.js

# Output to JSON
k6 run --out json=reports/k6-results.json qa-automation/performance/k6-load-test.js
```

## 📊 Reports & Dashboard

### Generate QA Dashboard

```bash
python qa-automation/reports/generate-report.py
# Opens: reports/qa-dashboard.html
```

### Analyze Results with AI Recommendations

```bash
python qa-automation/scripts/analyze-results.py
# Outputs: reports/analysis-{timestamp}.json
```

## 🎯 Performance Thresholds

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| API P95 Response | <500ms | 500-1000ms | >1000ms |
| API Error Rate | <1% | 1-5% | >5% |
| Lighthouse Performance | >80 | 60-80 | <60 |
| Lighthouse Accessibility | >90 | 80-90 | <80 |
| Test Coverage | >80% | 60-80% | <60% |
| LCP | <2.5s | 2.5-4s | >4s |
| CLS | <0.1 | 0.1-0.25 | >0.25 |

## 🔧 Configuration

### Environment Variables

```bash
# Testing
export BASE_URL=http://localhost:3000
export API_URL=http://localhost:5000
export HEADLESS=true
export TEST_USER_EMAIL=test@example.com
export TEST_USER_PASSWORD=password123

# Security
export SNYK_TOKEN=your-snyk-token

# Performance
export LIGHTHOUSE_AUTH_TOKEN=your-auth-token
```

### CI/CD Integration

Add to your GitHub Actions workflow:

```yaml
- name: Run QA Suite
  run: |
    pip install -r qa-automation/requirements.txt
    chmod +x qa-automation/scripts/run-all-qa.sh
    ./qa-automation/scripts/run-all-qa.sh

- name: Upload Reports
  uses: actions/upload-artifact@v3
  with:
    name: qa-reports
    path: qa-automation/reports/
```

## 📈 AI-Generated Recommendations

The `analyze-results.py` script provides intelligent recommendations based on:

- **Test Results**: Coverage gaps, failing tests, missing test types
- **Security**: Vulnerability severity, outdated dependencies
- **Performance**: Response times, Core Web Vitals, Lighthouse scores
- **Code Quality**: Linting errors, complexity issues

Example output:
```json
{
  "health_score": 75,
  "recommendations": [
    {
      "category": "Testing",
      "priority": "high",
      "title": "Increase Test Coverage",
      "description": "Current coverage is 65%. Target is 80%.",
      "action": "Add unit tests for uncovered modules.",
      "impact": "Reduces regression bugs"
    }
  ]
}
```

## 🤝 Contributing

1. Add new tests in appropriate directories
2. Update thresholds in `performance-thresholds.json`
3. Run full QA suite before submitting PRs
4. Ensure all checks pass

## 📄 License

MIT License - See LICENSE file for details.
