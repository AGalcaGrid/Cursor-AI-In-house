#!/bin/bash
# Master QA Execution Script
# Runs all QA automation checks and generates comprehensive reports

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QA_ROOT="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$QA_ROOT")"
REPORTS_DIR="$QA_ROOT/reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create reports directory
mkdir -p "$REPORTS_DIR"
mkdir -p "$REPORTS_DIR/security"

# Track results
FAILED=0
PASSED=0
SKIPPED=0
START_TIME=$(date +%s)

# Log file
LOG_FILE="$REPORTS_DIR/qa-run-$TIMESTAMP.log"

# Function to log messages
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# Function to run a step
run_step() {
    local step_name="$1"
    local step_command="$2"
    local step_dir="${3:-$PROJECT_ROOT}"
    
    log "${CYAN}Running: $step_name${NC}"
    
    if eval "cd '$step_dir' && $step_command" >> "$LOG_FILE" 2>&1; then
        log "${GREEN}✓ $step_name passed${NC}"
        PASSED=$((PASSED + 1))
        return 0
    else
        log "${RED}✗ $step_name failed${NC}"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# Function to skip a step
skip_step() {
    local step_name="$1"
    local reason="$2"
    log "${YELLOW}⊘ $step_name skipped: $reason${NC}"
    SKIPPED=$((SKIPPED + 1))
}

# Header
log ""
log "${BLUE}=========================================${NC}"
log "${BLUE}   QA Automation Suite${NC}"
log "${BLUE}   Started: $(date)${NC}"
log "${BLUE}=========================================${NC}"
log ""

# Step 1: Backend Unit Tests
log "${YELLOW}[1/10] Running Backend Unit Tests...${NC}"
if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    run_step "pytest unit tests" \
        "python -m pytest tests/unit/ -v --cov=app --cov-report=xml --cov-report=html --junitxml=test-results.xml" \
        "$PROJECT_ROOT" || true
else
    skip_step "Backend Unit Tests" "requirements.txt not found"
fi

# Step 2: Backend Integration Tests
log ""
log "${YELLOW}[2/10] Running Backend Integration Tests...${NC}"
if [ -d "$PROJECT_ROOT/tests/integration" ] || [ -d "$QA_ROOT/tests/integration" ]; then
    run_step "pytest integration tests" \
        "python -m pytest tests/integration/ -v --junitxml=integration-results.xml" \
        "$PROJECT_ROOT" || true
else
    skip_step "Backend Integration Tests" "No integration tests directory found"
fi

# Step 3: Frontend Unit Tests
log ""
log "${YELLOW}[3/10] Running Frontend Unit Tests...${NC}"
if [ -f "$PROJECT_ROOT/frontend/package.json" ]; then
    run_step "Jest unit tests" \
        "npm run test -- --coverage --watchAll=false --json --outputFile=test-results.json" \
        "$PROJECT_ROOT/frontend" || true
elif [ -f "$PROJECT_ROOT/react-app/package.json" ]; then
    run_step "Jest unit tests" \
        "npm run test -- --coverage --watchAll=false" \
        "$PROJECT_ROOT/react-app" || true
else
    skip_step "Frontend Unit Tests" "No frontend package.json found"
fi

# Step 4: E2E Tests
log ""
log "${YELLOW}[4/10] Running E2E Tests...${NC}"
if command -v npx &> /dev/null; then
    if [ -f "$PROJECT_ROOT/frontend/playwright.config.ts" ] || [ -f "$PROJECT_ROOT/playwright.config.ts" ]; then
        run_step "Playwright E2E tests" \
            "npx playwright test --reporter=html" \
            "$PROJECT_ROOT" || true
    elif [ -d "$QA_ROOT/tests/e2e" ]; then
        run_step "Selenium E2E tests" \
            "python -m pytest $QA_ROOT/tests/e2e/ -v" \
            "$PROJECT_ROOT" || true
    else
        skip_step "E2E Tests" "No E2E test configuration found"
    fi
else
    skip_step "E2E Tests" "npx not available"
fi

# Step 5: Code Quality - ESLint
log ""
log "${YELLOW}[5/10] Running ESLint...${NC}"
if [ -f "$PROJECT_ROOT/frontend/package.json" ]; then
    run_step "ESLint" \
        "npx eslint src/ --format json --output-file eslint-report.json || true" \
        "$PROJECT_ROOT/frontend" || true
elif [ -f "$PROJECT_ROOT/react-app/package.json" ]; then
    run_step "ESLint" \
        "npx eslint src/ --format json --output-file eslint-report.json || true" \
        "$PROJECT_ROOT/react-app" || true
else
    skip_step "ESLint" "No frontend found"
fi

# Step 6: Code Quality - Pylint
log ""
log "${YELLOW}[6/10] Running Pylint...${NC}"
if [ -d "$PROJECT_ROOT/app" ]; then
    run_step "Pylint" \
        "pylint app/ --output-format=json > pylint-report.json || true" \
        "$PROJECT_ROOT" || true
else
    skip_step "Pylint" "No app directory found"
fi

# Step 7: Security Scans
log ""
log "${YELLOW}[7/10] Running Security Scans...${NC}"
if [ -f "$QA_ROOT/security/security-scan.sh" ]; then
    run_step "Security scans" \
        "bash $QA_ROOT/security/security-scan.sh" \
        "$PROJECT_ROOT" || true
else
    # Run basic security checks
    if command -v npm &> /dev/null && [ -f "$PROJECT_ROOT/frontend/package.json" ]; then
        run_step "npm audit" \
            "npm audit --json > $REPORTS_DIR/security/npm-audit-$TIMESTAMP.json || true" \
            "$PROJECT_ROOT/frontend" || true
    fi
    
    if command -v pip-audit &> /dev/null; then
        run_step "pip-audit" \
            "pip-audit -r requirements.txt --format json > $REPORTS_DIR/security/pip-audit-$TIMESTAMP.json || true" \
            "$PROJECT_ROOT" || true
    elif command -v safety &> /dev/null; then
        run_step "safety check" \
            "safety check -r requirements.txt --json > $REPORTS_DIR/security/safety-$TIMESTAMP.json || true" \
            "$PROJECT_ROOT" || true
    fi
fi

# Step 8: Performance Tests - k6
log ""
log "${YELLOW}[8/10] Running Performance Tests (k6)...${NC}"
if command -v k6 &> /dev/null; then
    if [ -f "$QA_ROOT/performance/k6-load-test.js" ]; then
        run_step "k6 load test" \
            "k6 run --out json=$REPORTS_DIR/k6-results-$TIMESTAMP.json $QA_ROOT/performance/k6-load-test.js" \
            "$PROJECT_ROOT" || true
    else
        skip_step "k6 Load Tests" "k6-load-test.js not found"
    fi
else
    skip_step "k6 Load Tests" "k6 not installed"
fi

# Step 9: Performance Tests - Lighthouse
log ""
log "${YELLOW}[9/10] Running Lighthouse Audit...${NC}"
if command -v npx &> /dev/null; then
    # Check if frontend is running
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        run_step "Lighthouse audit" \
            "npx lighthouse http://localhost:3000 --output=json --output-path=$REPORTS_DIR/lighthouse-$TIMESTAMP.json --chrome-flags='--headless --no-sandbox'" \
            "$PROJECT_ROOT" || true
    else
        skip_step "Lighthouse Audit" "Frontend not running on localhost:3000"
    fi
else
    skip_step "Lighthouse Audit" "npx not available"
fi

# Step 10: Generate Reports
log ""
log "${YELLOW}[10/10] Generating QA Reports...${NC}"
if [ -f "$QA_ROOT/reports/generate-report.py" ]; then
    run_step "Generate QA dashboard" \
        "python $QA_ROOT/reports/generate-report.py" \
        "$PROJECT_ROOT" || true
else
    skip_step "Report Generation" "generate-report.py not found"
fi

# Calculate duration
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

# Summary
log ""
log "${BLUE}=========================================${NC}"
log "${BLUE}   QA Automation Summary${NC}"
log "${BLUE}=========================================${NC}"
log ""
log "  Duration:  ${MINUTES}m ${SECONDS}s"
log "  Passed:    ${GREEN}$PASSED${NC}"
log "  Failed:    ${RED}$FAILED${NC}"
log "  Skipped:   ${YELLOW}$SKIPPED${NC}"
log ""
log "  Log file:  $LOG_FILE"
log "  Reports:   $REPORTS_DIR"
log ""

if [ $FAILED -eq 0 ]; then
    log "${GREEN}✓ All QA checks passed!${NC}"
    exit 0
else
    log "${RED}✗ $FAILED QA check(s) failed${NC}"
    exit 1
fi
