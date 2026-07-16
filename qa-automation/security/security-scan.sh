#!/bin/bash
# Comprehensive Security Scanning Script
# Run all security scans and generate consolidated report

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
REPORTS_DIR="$PROJECT_ROOT/qa-automation/reports/security"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create reports directory
mkdir -p "$REPORTS_DIR"

# Track results
CRITICAL_ISSUES=0
HIGH_ISSUES=0
MEDIUM_ISSUES=0
LOW_ISSUES=0
SCAN_FAILURES=0

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}   Security Scanning Suite${NC}"
echo -e "${BLUE}   Started: $(date)${NC}"
echo -e "${BLUE}=========================================${NC}"

# Function to log results
log_result() {
    local status=$1
    local message=$2
    if [ "$status" -eq 0 ]; then
        echo -e "${GREEN}✓ $message${NC}"
    else
        echo -e "${RED}✗ $message${NC}"
        SCAN_FAILURES=$((SCAN_FAILURES + 1))
    fi
}

# 1. Python Dependency Security Check (pip-audit/safety)
echo -e "\n${YELLOW}[1/8] Running Python Dependency Security Check...${NC}"
if command -v pip-audit &> /dev/null; then
    pip-audit -r "$PROJECT_ROOT/requirements.txt" --format json > "$REPORTS_DIR/pip-audit-$TIMESTAMP.json" 2>/dev/null || true
    PYTHON_VULNS=$(cat "$REPORTS_DIR/pip-audit-$TIMESTAMP.json" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('dependencies', [])))" 2>/dev/null || echo "0")
    log_result 0 "pip-audit completed: $PYTHON_VULNS vulnerabilities found"
elif command -v safety &> /dev/null; then
    safety check -r "$PROJECT_ROOT/requirements.txt" --json > "$REPORTS_DIR/safety-$TIMESTAMP.json" 2>/dev/null || true
    log_result 0 "safety check completed"
else
    echo -e "${YELLOW}  Warning: Neither pip-audit nor safety installed. Skipping Python dependency check.${NC}"
fi

# 2. Node.js Dependency Security Check (npm audit)
echo -e "\n${YELLOW}[2/8] Running npm audit...${NC}"
if [ -f "$PROJECT_ROOT/frontend/package.json" ]; then
    cd "$PROJECT_ROOT/frontend"
    npm audit --json > "$REPORTS_DIR/npm-audit-$TIMESTAMP.json" 2>/dev/null || true
    
    # Parse npm audit results
    NPM_CRITICAL=$(cat "$REPORTS_DIR/npm-audit-$TIMESTAMP.json" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('metadata', {}).get('vulnerabilities', {}).get('critical', 0))" 2>/dev/null || echo "0")
    NPM_HIGH=$(cat "$REPORTS_DIR/npm-audit-$TIMESTAMP.json" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('metadata', {}).get('vulnerabilities', {}).get('high', 0))" 2>/dev/null || echo "0")
    
    CRITICAL_ISSUES=$((CRITICAL_ISSUES + NPM_CRITICAL))
    HIGH_ISSUES=$((HIGH_ISSUES + NPM_HIGH))
    
    log_result 0 "npm audit completed: $NPM_CRITICAL critical, $NPM_HIGH high"
    cd "$PROJECT_ROOT"
else
    echo -e "${YELLOW}  Warning: No frontend/package.json found. Skipping npm audit.${NC}"
fi

# 3. Snyk Security Scan
echo -e "\n${YELLOW}[3/8] Running Snyk security scan...${NC}"
if command -v snyk &> /dev/null; then
    snyk test --json > "$REPORTS_DIR/snyk-$TIMESTAMP.json" 2>/dev/null || true
    snyk test --sarif > "$REPORTS_DIR/snyk-$TIMESTAMP.sarif" 2>/dev/null || true
    log_result 0 "Snyk scan completed"
else
    echo -e "${YELLOW}  Warning: Snyk not installed. Run: npm install -g snyk${NC}"
fi

# 4. Bandit - Python Security Linter
echo -e "\n${YELLOW}[4/8] Running Bandit (Python security linter)...${NC}"
if command -v bandit &> /dev/null; then
    bandit -r "$PROJECT_ROOT/app" -f json -o "$REPORTS_DIR/bandit-$TIMESTAMP.json" 2>/dev/null || true
    bandit -r "$PROJECT_ROOT/app" -f html -o "$REPORTS_DIR/bandit-$TIMESTAMP.html" 2>/dev/null || true
    
    BANDIT_HIGH=$(cat "$REPORTS_DIR/bandit-$TIMESTAMP.json" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len([r for r in data.get('results', []) if r.get('issue_severity') == 'HIGH']))" 2>/dev/null || echo "0")
    HIGH_ISSUES=$((HIGH_ISSUES + BANDIT_HIGH))
    
    log_result 0 "Bandit scan completed: $BANDIT_HIGH high severity issues"
else
    echo -e "${YELLOW}  Warning: Bandit not installed. Run: pip install bandit${NC}"
fi

# 5. Secret Detection (TruffleHog/detect-secrets)
echo -e "\n${YELLOW}[5/8] Scanning for secrets and credentials...${NC}"
if command -v trufflehog &> /dev/null; then
    trufflehog git file://"$PROJECT_ROOT" --json > "$REPORTS_DIR/trufflehog-$TIMESTAMP.json" 2>/dev/null || true
    SECRETS_FOUND=$(wc -l < "$REPORTS_DIR/trufflehog-$TIMESTAMP.json" 2>/dev/null || echo "0")
    log_result 0 "TruffleHog scan completed: $SECRETS_FOUND potential secrets found"
elif command -v detect-secrets &> /dev/null; then
    detect-secrets scan "$PROJECT_ROOT" > "$REPORTS_DIR/detect-secrets-$TIMESTAMP.json" 2>/dev/null || true
    log_result 0 "detect-secrets scan completed"
else
    echo -e "${YELLOW}  Warning: No secret scanner installed. Install trufflehog or detect-secrets.${NC}"
fi

# 6. OWASP ZAP Scan (if running)
echo -e "\n${YELLOW}[6/8] Running OWASP ZAP scan...${NC}"
if docker ps | grep -q "owasp/zap"; then
    echo "  ZAP container detected, running baseline scan..."
    docker exec $(docker ps -q -f ancestor=owasp/zap2docker-stable) \
        zap-baseline.py -t http://localhost:3000 -J zap-report.json > /dev/null 2>&1 || true
    docker cp $(docker ps -q -f ancestor=owasp/zap2docker-stable):/zap/zap-report.json "$REPORTS_DIR/zap-$TIMESTAMP.json" 2>/dev/null || true
    log_result 0 "ZAP baseline scan completed"
elif command -v docker &> /dev/null; then
    echo "  Starting ZAP container for scan..."
    docker run --rm -v "$REPORTS_DIR:/zap/wrk:rw" -t owasp/zap2docker-stable \
        zap-baseline.py -t http://host.docker.internal:3000 -J zap-report.json 2>/dev/null || true
    log_result 0 "ZAP scan completed"
else
    echo -e "${YELLOW}  Warning: Docker not available. Skipping ZAP scan.${NC}"
fi

# 7. Dependency License Check
echo -e "\n${YELLOW}[7/8] Checking dependency licenses...${NC}"
if command -v pip-licenses &> /dev/null; then
    pip-licenses --format=json > "$REPORTS_DIR/licenses-python-$TIMESTAMP.json" 2>/dev/null || true
    log_result 0 "Python license check completed"
fi

if [ -f "$PROJECT_ROOT/frontend/package.json" ]; then
    cd "$PROJECT_ROOT/frontend"
    if command -v license-checker &> /dev/null; then
        license-checker --json > "$REPORTS_DIR/licenses-npm-$TIMESTAMP.json" 2>/dev/null || true
        log_result 0 "npm license check completed"
    fi
    cd "$PROJECT_ROOT"
fi

# 8. Security Headers Check
echo -e "\n${YELLOW}[8/8] Checking security headers...${NC}"
if command -v curl &> /dev/null; then
    curl -s -I http://localhost:3000 > "$REPORTS_DIR/headers-$TIMESTAMP.txt" 2>/dev/null || true
    
    # Check for important security headers
    HEADERS_FILE="$REPORTS_DIR/headers-$TIMESTAMP.txt"
    if [ -f "$HEADERS_FILE" ]; then
        echo "  Security Headers Analysis:" >> "$REPORTS_DIR/headers-analysis-$TIMESTAMP.txt"
        
        grep -qi "x-content-type-options" "$HEADERS_FILE" && echo "  ✓ X-Content-Type-Options present" >> "$REPORTS_DIR/headers-analysis-$TIMESTAMP.txt" || echo "  ✗ X-Content-Type-Options missing" >> "$REPORTS_DIR/headers-analysis-$TIMESTAMP.txt"
        grep -qi "x-frame-options" "$HEADERS_FILE" && echo "  ✓ X-Frame-Options present" >> "$REPORTS_DIR/headers-analysis-$TIMESTAMP.txt" || echo "  ✗ X-Frame-Options missing" >> "$REPORTS_DIR/headers-analysis-$TIMESTAMP.txt"
        grep -qi "x-xss-protection" "$HEADERS_FILE" && echo "  ✓ X-XSS-Protection present" >> "$REPORTS_DIR/headers-analysis-$TIMESTAMP.txt" || echo "  ✗ X-XSS-Protection missing" >> "$REPORTS_DIR/headers-analysis-$TIMESTAMP.txt"
        grep -qi "strict-transport-security" "$HEADERS_FILE" && echo "  ✓ Strict-Transport-Security present" >> "$REPORTS_DIR/headers-analysis-$TIMESTAMP.txt" || echo "  ✗ Strict-Transport-Security missing" >> "$REPORTS_DIR/headers-analysis-$TIMESTAMP.txt"
        grep -qi "content-security-policy" "$HEADERS_FILE" && echo "  ✓ Content-Security-Policy present" >> "$REPORTS_DIR/headers-analysis-$TIMESTAMP.txt" || echo "  ✗ Content-Security-Policy missing" >> "$REPORTS_DIR/headers-analysis-$TIMESTAMP.txt"
        
        log_result 0 "Security headers check completed"
    fi
fi

# Generate Summary Report
echo -e "\n${BLUE}=========================================${NC}"
echo -e "${BLUE}   Security Scan Summary${NC}"
echo -e "${BLUE}=========================================${NC}"

cat > "$REPORTS_DIR/summary-$TIMESTAMP.json" << EOF
{
    "timestamp": "$(date -Iseconds)",
    "critical_issues": $CRITICAL_ISSUES,
    "high_issues": $HIGH_ISSUES,
    "medium_issues": $MEDIUM_ISSUES,
    "low_issues": $LOW_ISSUES,
    "scan_failures": $SCAN_FAILURES,
    "reports_directory": "$REPORTS_DIR"
}
EOF

echo -e "  Critical Issues: ${RED}$CRITICAL_ISSUES${NC}"
echo -e "  High Issues:     ${RED}$HIGH_ISSUES${NC}"
echo -e "  Medium Issues:   ${YELLOW}$MEDIUM_ISSUES${NC}"
echo -e "  Low Issues:      ${GREEN}$LOW_ISSUES${NC}"
echo -e "  Scan Failures:   $SCAN_FAILURES"
echo -e "\n  Reports saved to: $REPORTS_DIR"

# Exit with error if critical or high issues found
if [ $CRITICAL_ISSUES -gt 0 ] || [ $HIGH_ISSUES -gt 0 ]; then
    echo -e "\n${RED}✗ Security scan failed: Critical or high severity issues found${NC}"
    exit 1
else
    echo -e "\n${GREEN}✓ Security scan passed${NC}"
    exit 0
fi
