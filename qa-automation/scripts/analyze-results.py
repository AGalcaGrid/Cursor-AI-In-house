#!/usr/bin/env python3
"""
QA Results Analyzer with AI-Generated Recommendations
Analyzes QA results and provides actionable improvement suggestions
"""

import json
import os
import glob
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class Priority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Category(Enum):
    TESTING = "Testing"
    SECURITY = "Security"
    PERFORMANCE = "Performance"
    CODE_QUALITY = "Code Quality"
    ACCESSIBILITY = "Accessibility"
    RELIABILITY = "Reliability"
    MAINTAINABILITY = "Maintainability"


@dataclass
class Recommendation:
    """Represents an improvement recommendation"""
    category: str
    priority: str
    title: str
    description: str
    action: str
    impact: str
    effort: str = "medium"
    tags: List[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class QAResultsAnalyzer:
    """Analyzes QA results and generates AI-powered recommendations"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.qa_root = self.project_root / 'qa-automation'
        self.reports_dir = self.qa_root / 'reports'
        
        self.results = {
            'tests': {},
            'security': {},
            'performance': {},
            'code_quality': {}
        }
        self.recommendations: List[Recommendation] = []
        self.thresholds = self._load_thresholds()
    
    def _load_thresholds(self) -> Dict:
        """Load performance thresholds configuration"""
        thresholds_file = self.qa_root / 'performance' / 'performance-thresholds.json'
        if thresholds_file.exists():
            with open(thresholds_file) as f:
                return json.load(f)
        return {}
    
    def analyze_test_results(self):
        """Analyze test results and generate recommendations"""
        # Analyze pytest results
        pytest_xml = self.project_root / 'test-results.xml'
        if pytest_xml.exists():
            self._analyze_pytest_xml(pytest_xml)
        
        # Analyze coverage
        coverage_file = self.project_root / 'coverage.xml'
        if coverage_file.exists():
            self._analyze_coverage_xml(coverage_file)
        
        # Check for test patterns
        self._analyze_test_patterns()
    
    def _analyze_pytest_xml(self, xml_path: Path):
        """Analyze pytest XML results"""
        import xml.etree.ElementTree as ET
        
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            testsuite = root.find('testsuite') or root
            
            tests = int(testsuite.get('tests', 0))
            failures = int(testsuite.get('failures', 0))
            errors = int(testsuite.get('errors', 0))
            skipped = int(testsuite.get('skipped', 0))
            
            self.results['tests']['backend'] = {
                'total': tests,
                'passed': tests - failures - errors - skipped,
                'failed': failures,
                'errors': errors,
                'skipped': skipped,
                'pass_rate': ((tests - failures - errors) / tests * 100) if tests > 0 else 0
            }
            
            # Generate recommendations based on results
            if failures > 0:
                self.recommendations.append(Recommendation(
                    category=Category.TESTING.value,
                    priority=Priority.HIGH.value,
                    title=f"Fix {failures} Failing Tests",
                    description=f"There are {failures} failing tests that need attention.",
                    action="Review test failures in test-results.xml and fix the underlying issues.",
                    impact="Ensures code reliability and prevents regressions",
                    effort="medium",
                    tags=["testing", "backend", "urgent"]
                ))
            
            if skipped > 5:
                self.recommendations.append(Recommendation(
                    category=Category.TESTING.value,
                    priority=Priority.MEDIUM.value,
                    title=f"Review {skipped} Skipped Tests",
                    description=f"There are {skipped} skipped tests that may need attention.",
                    action="Review skipped tests and either fix or remove them if obsolete.",
                    impact="Improves test suite maintainability",
                    effort="low",
                    tags=["testing", "maintenance"]
                ))
                
        except Exception as e:
            print(f"Error analyzing pytest results: {e}")
    
    def _analyze_coverage_xml(self, xml_path: Path):
        """Analyze coverage XML"""
        import xml.etree.ElementTree as ET
        
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            line_rate = float(root.get('line-rate', 0)) * 100
            branch_rate = float(root.get('branch-rate', 0)) * 100
            
            self.results['tests']['coverage'] = {
                'line_coverage': line_rate,
                'branch_coverage': branch_rate
            }
            
            if line_rate < 80:
                self.recommendations.append(Recommendation(
                    category=Category.TESTING.value,
                    priority=Priority.HIGH.value if line_rate < 60 else Priority.MEDIUM.value,
                    title="Increase Test Coverage",
                    description=f"Current line coverage is {line_rate:.1f}%. Target is 80%.",
                    action="Add unit tests for uncovered code paths, focusing on critical business logic.",
                    impact="Reduces bugs and improves code confidence",
                    effort="high",
                    tags=["testing", "coverage"]
                ))
            
            # Find low coverage files
            for package in root.findall('.//package'):
                for cls in package.findall('.//class'):
                    filename = cls.get('filename', '')
                    file_line_rate = float(cls.get('line-rate', 0)) * 100
                    
                    if file_line_rate < 50 and 'test' not in filename.lower():
                        self.results['tests'].setdefault('low_coverage_files', []).append({
                            'file': filename,
                            'coverage': file_line_rate
                        })
                        
        except Exception as e:
            print(f"Error analyzing coverage: {e}")
    
    def _analyze_test_patterns(self):
        """Analyze test patterns and structure"""
        test_dirs = [
            self.project_root / 'tests',
            self.qa_root / 'tests'
        ]
        
        test_counts = {
            'unit': 0,
            'integration': 0,
            'e2e': 0,
            'performance': 0
        }
        
        for test_dir in test_dirs:
            if test_dir.exists():
                for pattern, category in [
                    ('**/unit/**/*.py', 'unit'),
                    ('**/integration/**/*.py', 'integration'),
                    ('**/e2e/**/*.py', 'e2e'),
                    ('**/performance/**/*.py', 'performance')
                ]:
                    test_counts[category] += len(list(test_dir.glob(pattern)))
        
        self.results['tests']['structure'] = test_counts
        
        # Recommendations based on test structure
        if test_counts['integration'] == 0:
            self.recommendations.append(Recommendation(
                category=Category.TESTING.value,
                priority=Priority.MEDIUM.value,
                title="Add Integration Tests",
                description="No integration tests found in the project.",
                action="Create integration tests to verify component interactions and API contracts.",
                impact="Catches integration issues before production",
                effort="medium",
                tags=["testing", "integration"]
            ))
        
        if test_counts['e2e'] == 0:
            self.recommendations.append(Recommendation(
                category=Category.TESTING.value,
                priority=Priority.MEDIUM.value,
                title="Add End-to-End Tests",
                description="No E2E tests found in the project.",
                action="Implement E2E tests using Playwright or Selenium for critical user flows.",
                impact="Validates complete user journeys",
                effort="high",
                tags=["testing", "e2e"]
            ))
    
    def analyze_security_results(self):
        """Analyze security scan results"""
        security_dir = self.reports_dir / 'security'
        
        # Find latest security summary
        summaries = sorted(glob.glob(str(security_dir / 'summary-*.json')), reverse=True)
        if summaries:
            with open(summaries[0]) as f:
                data = json.load(f)
                self.results['security'] = data
                
                if data.get('critical_issues', 0) > 0:
                    self.recommendations.append(Recommendation(
                        category=Category.SECURITY.value,
                        priority=Priority.CRITICAL.value,
                        title="Fix Critical Security Vulnerabilities",
                        description=f"{data['critical_issues']} critical vulnerabilities require immediate attention.",
                        action="Review security reports and update affected dependencies immediately.",
                        impact="Prevents potential security breaches",
                        effort="high",
                        tags=["security", "critical", "urgent"]
                    ))
                
                if data.get('high_issues', 0) > 0:
                    self.recommendations.append(Recommendation(
                        category=Category.SECURITY.value,
                        priority=Priority.HIGH.value,
                        title="Address High Severity Vulnerabilities",
                        description=f"{data['high_issues']} high severity vulnerabilities detected.",
                        action="Schedule updates for vulnerable packages within the current sprint.",
                        impact="Reduces attack surface",
                        effort="medium",
                        tags=["security", "high"]
                    ))
        
        # Analyze npm audit
        npm_audits = sorted(glob.glob(str(security_dir / 'npm-audit-*.json')), reverse=True)
        if npm_audits:
            self._analyze_npm_audit(npm_audits[0])
        
        # Analyze bandit results
        bandit_reports = sorted(glob.glob(str(security_dir / 'bandit-*.json')), reverse=True)
        if bandit_reports:
            self._analyze_bandit(bandit_reports[0])
    
    def _analyze_npm_audit(self, audit_path: str):
        """Analyze npm audit results"""
        try:
            with open(audit_path) as f:
                data = json.load(f)
                
            vulns = data.get('vulnerabilities', {})
            self.results['security']['npm'] = {
                'total': len(vulns),
                'by_severity': {}
            }
            
            for name, vuln in vulns.items():
                severity = vuln.get('severity', 'unknown')
                self.results['security']['npm']['by_severity'][severity] = \
                    self.results['security']['npm']['by_severity'].get(severity, 0) + 1
                    
        except Exception as e:
            print(f"Error analyzing npm audit: {e}")
    
    def _analyze_bandit(self, bandit_path: str):
        """Analyze bandit security results"""
        try:
            with open(bandit_path) as f:
                data = json.load(f)
            
            results = data.get('results', [])
            by_severity = {}
            
            for issue in results:
                severity = issue.get('issue_severity', 'UNKNOWN')
                by_severity[severity] = by_severity.get(severity, 0) + 1
            
            self.results['security']['bandit'] = {
                'total': len(results),
                'by_severity': by_severity
            }
            
            if by_severity.get('HIGH', 0) > 0:
                self.recommendations.append(Recommendation(
                    category=Category.SECURITY.value,
                    priority=Priority.HIGH.value,
                    title="Fix Bandit Security Issues",
                    description=f"{by_severity['HIGH']} high severity code security issues found.",
                    action="Review bandit report and fix security anti-patterns in Python code.",
                    impact="Prevents security vulnerabilities in application code",
                    effort="medium",
                    tags=["security", "code-review", "python"]
                ))
                
        except Exception as e:
            print(f"Error analyzing bandit results: {e}")
    
    def analyze_performance_results(self):
        """Analyze performance test results"""
        # Analyze k6 results
        k6_reports = sorted(glob.glob(str(self.reports_dir / 'k6-*.json')), reverse=True)
        if k6_reports:
            self._analyze_k6(k6_reports[0])
        
        # Analyze Lighthouse results
        lighthouse_reports = sorted(glob.glob(str(self.reports_dir / 'lighthouse-*.json')), reverse=True)
        if lighthouse_reports:
            self._analyze_lighthouse(lighthouse_reports[0])
    
    def _analyze_k6(self, k6_path: str):
        """Analyze k6 load test results"""
        try:
            with open(k6_path) as f:
                data = json.load(f)
            
            metrics = data.get('metrics', {})
            
            self.results['performance']['k6'] = {
                'avg_response_time': metrics.get('http_req_duration', {}).get('values', {}).get('avg', 0),
                'p95_response_time': metrics.get('http_req_duration', {}).get('values', {}).get('p(95)', 0),
                'p99_response_time': metrics.get('http_req_duration', {}).get('values', {}).get('p(99)', 0),
                'error_rate': metrics.get('http_req_failed', {}).get('values', {}).get('rate', 0),
                'requests_per_second': metrics.get('http_reqs', {}).get('values', {}).get('rate', 0)
            }
            
            k6_results = self.results['performance']['k6']
            thresholds = self.thresholds.get('api', {}).get('responseTime', {}).get('thresholds', {})
            
            if k6_results['p95_response_time'] > thresholds.get('p95', 500):
                self.recommendations.append(Recommendation(
                    category=Category.PERFORMANCE.value,
                    priority=Priority.HIGH.value,
                    title="Optimize API Response Time",
                    description=f"P95 response time is {k6_results['p95_response_time']:.0f}ms, exceeding {thresholds.get('p95', 500)}ms threshold.",
                    action="Profile slow endpoints, add database indexes, implement caching.",
                    impact="Improves user experience and system scalability",
                    effort="high",
                    tags=["performance", "api", "optimization"]
                ))
            
            if k6_results['error_rate'] > 0.01:
                self.recommendations.append(Recommendation(
                    category=Category.RELIABILITY.value,
                    priority=Priority.HIGH.value,
                    title="Reduce API Error Rate",
                    description=f"Error rate is {k6_results['error_rate']*100:.2f}%, exceeding 1% threshold.",
                    action="Review error logs, add retry logic, improve error handling.",
                    impact="Improves system reliability",
                    effort="medium",
                    tags=["reliability", "errors", "api"]
                ))
                
        except Exception as e:
            print(f"Error analyzing k6 results: {e}")
    
    def _analyze_lighthouse(self, lighthouse_path: str):
        """Analyze Lighthouse audit results"""
        try:
            with open(lighthouse_path) as f:
                data = json.load(f)
            
            categories = data.get('categories', {})
            audits = data.get('audits', {})
            
            self.results['performance']['lighthouse'] = {
                'performance': int(categories.get('performance', {}).get('score', 0) * 100),
                'accessibility': int(categories.get('accessibility', {}).get('score', 0) * 100),
                'best_practices': int(categories.get('best-practices', {}).get('score', 0) * 100),
                'seo': int(categories.get('seo', {}).get('score', 0) * 100)
            }
            
            # Core Web Vitals
            self.results['performance']['core_web_vitals'] = {
                'LCP': audits.get('largest-contentful-paint', {}).get('numericValue', 0),
                'FID': audits.get('max-potential-fid', {}).get('numericValue', 0),
                'CLS': audits.get('cumulative-layout-shift', {}).get('numericValue', 0),
                'FCP': audits.get('first-contentful-paint', {}).get('numericValue', 0),
                'TTI': audits.get('interactive', {}).get('numericValue', 0),
                'TBT': audits.get('total-blocking-time', {}).get('numericValue', 0)
            }
            
            lh = self.results['performance']['lighthouse']
            
            if lh['performance'] < 80:
                self.recommendations.append(Recommendation(
                    category=Category.PERFORMANCE.value,
                    priority=Priority.MEDIUM.value if lh['performance'] >= 60 else Priority.HIGH.value,
                    title="Improve Lighthouse Performance Score",
                    description=f"Performance score is {lh['performance']}, below 80 target.",
                    action="Optimize images, reduce JavaScript bundle, implement code splitting, use lazy loading.",
                    impact="Improves page load time and user experience",
                    effort="high",
                    tags=["performance", "frontend", "lighthouse"]
                ))
            
            if lh['accessibility'] < 90:
                self.recommendations.append(Recommendation(
                    category=Category.ACCESSIBILITY.value,
                    priority=Priority.MEDIUM.value,
                    title="Improve Accessibility Score",
                    description=f"Accessibility score is {lh['accessibility']}, below 90 target.",
                    action="Add ARIA labels, improve color contrast, ensure keyboard navigation, add alt text.",
                    impact="Makes application accessible to all users",
                    effort="medium",
                    tags=["accessibility", "a11y", "frontend"]
                ))
            
            # Core Web Vitals recommendations
            cwv = self.results['performance']['core_web_vitals']
            cwv_thresholds = self.thresholds.get('frontend', {}).get('coreWebVitals', {}).get('thresholds', {})
            
            if cwv['LCP'] > cwv_thresholds.get('LCP', {}).get('good', 2500):
                self.recommendations.append(Recommendation(
                    category=Category.PERFORMANCE.value,
                    priority=Priority.HIGH.value,
                    title="Improve Largest Contentful Paint (LCP)",
                    description=f"LCP is {cwv['LCP']:.0f}ms, exceeding 2500ms threshold.",
                    action="Optimize hero images, preload critical resources, use CDN.",
                    impact="Improves perceived load time",
                    effort="medium",
                    tags=["performance", "cwv", "lcp"]
                ))
            
            if cwv['CLS'] > cwv_thresholds.get('CLS', {}).get('good', 0.1):
                self.recommendations.append(Recommendation(
                    category=Category.PERFORMANCE.value,
                    priority=Priority.MEDIUM.value,
                    title="Reduce Cumulative Layout Shift (CLS)",
                    description=f"CLS is {cwv['CLS']:.3f}, exceeding 0.1 threshold.",
                    action="Add size attributes to images/videos, avoid inserting content above existing content.",
                    impact="Prevents unexpected layout shifts",
                    effort="low",
                    tags=["performance", "cwv", "cls"]
                ))
                
        except Exception as e:
            print(f"Error analyzing Lighthouse results: {e}")
    
    def analyze_code_quality(self):
        """Analyze code quality results"""
        # Analyze ESLint
        eslint_reports = glob.glob(str(self.project_root / '**/eslint-report.json'), recursive=True)
        if eslint_reports:
            self._analyze_eslint(eslint_reports[0])
        
        # Analyze Pylint
        pylint_report = self.project_root / 'pylint-report.json'
        if pylint_report.exists():
            self._analyze_pylint(pylint_report)
    
    def _analyze_eslint(self, eslint_path: str):
        """Analyze ESLint results"""
        try:
            with open(eslint_path) as f:
                data = json.load(f)
            
            total_errors = sum(f.get('errorCount', 0) for f in data)
            total_warnings = sum(f.get('warningCount', 0) for f in data)
            
            self.results['code_quality']['eslint'] = {
                'files_checked': len(data),
                'errors': total_errors,
                'warnings': total_warnings
            }
            
            if total_errors > 0:
                self.recommendations.append(Recommendation(
                    category=Category.CODE_QUALITY.value,
                    priority=Priority.MEDIUM.value,
                    title="Fix ESLint Errors",
                    description=f"{total_errors} ESLint errors found across {len(data)} files.",
                    action="Run 'npx eslint --fix' and manually fix remaining issues.",
                    impact="Improves code consistency and catches potential bugs",
                    effort="low",
                    tags=["code-quality", "eslint", "frontend"]
                ))
                
        except Exception as e:
            print(f"Error analyzing ESLint results: {e}")
    
    def _analyze_pylint(self, pylint_path: Path):
        """Analyze Pylint results"""
        try:
            with open(pylint_path) as f:
                data = json.load(f)
            
            by_type = {}
            for issue in data:
                issue_type = issue.get('type', 'unknown')
                by_type[issue_type] = by_type.get(issue_type, 0) + 1
            
            self.results['code_quality']['pylint'] = {
                'total_issues': len(data),
                'by_type': by_type
            }
            
            if by_type.get('error', 0) > 0:
                self.recommendations.append(Recommendation(
                    category=Category.CODE_QUALITY.value,
                    priority=Priority.MEDIUM.value,
                    title="Fix Pylint Errors",
                    description=f"{by_type['error']} Pylint errors found.",
                    action="Review pylint-report.json and fix code issues.",
                    impact="Reduces potential bugs and improves code quality",
                    effort="medium",
                    tags=["code-quality", "pylint", "python"]
                ))
                
        except Exception as e:
            print(f"Error analyzing Pylint results: {e}")
    
    def generate_improvement_plan(self) -> Dict:
        """Generate a prioritized improvement plan"""
        # Sort recommendations by priority
        priority_order = {
            Priority.CRITICAL.value: 0,
            Priority.HIGH.value: 1,
            Priority.MEDIUM.value: 2,
            Priority.LOW.value: 3
        }
        
        sorted_recommendations = sorted(
            self.recommendations,
            key=lambda x: priority_order.get(x.priority, 4)
        )
        
        # Group by category
        by_category = {}
        for rec in sorted_recommendations:
            category = rec.category
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(rec.to_dict())
        
        # Calculate health score
        health_score = self._calculate_health_score()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'health_score': health_score,
            'summary': {
                'total_recommendations': len(self.recommendations),
                'critical': len([r for r in self.recommendations if r.priority == Priority.CRITICAL.value]),
                'high': len([r for r in self.recommendations if r.priority == Priority.HIGH.value]),
                'medium': len([r for r in self.recommendations if r.priority == Priority.MEDIUM.value]),
                'low': len([r for r in self.recommendations if r.priority == Priority.LOW.value])
            },
            'results': self.results,
            'recommendations_by_category': by_category,
            'recommendations': [r.to_dict() for r in sorted_recommendations]
        }
    
    def _calculate_health_score(self) -> int:
        """Calculate overall project health score"""
        score = 100
        
        # Deduct for critical/high recommendations
        for rec in self.recommendations:
            if rec.priority == Priority.CRITICAL.value:
                score -= 15
            elif rec.priority == Priority.HIGH.value:
                score -= 8
            elif rec.priority == Priority.MEDIUM.value:
                score -= 3
            elif rec.priority == Priority.LOW.value:
                score -= 1
        
        return max(0, min(100, score))
    
    def run(self) -> Dict:
        """Run full analysis"""
        print("Analyzing QA results...")
        
        self.analyze_test_results()
        self.analyze_security_results()
        self.analyze_performance_results()
        self.analyze_code_quality()
        
        improvement_plan = self.generate_improvement_plan()
        
        # Save results
        output_path = self.reports_dir / f'analysis-{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_path, 'w') as f:
            json.dump(improvement_plan, f, indent=2)
        
        print(f"\nAnalysis complete!")
        print(f"Health Score: {improvement_plan['health_score']}/100")
        print(f"Total Recommendations: {improvement_plan['summary']['total_recommendations']}")
        print(f"  - Critical: {improvement_plan['summary']['critical']}")
        print(f"  - High: {improvement_plan['summary']['high']}")
        print(f"  - Medium: {improvement_plan['summary']['medium']}")
        print(f"  - Low: {improvement_plan['summary']['low']}")
        print(f"\nResults saved to: {output_path}")
        
        return improvement_plan


if __name__ == '__main__':
    analyzer = QAResultsAnalyzer()
    analyzer.run()
