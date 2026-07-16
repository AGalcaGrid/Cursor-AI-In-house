/**
 * k6 Load Testing Script
 * Comprehensive performance testing for Support Ticket API
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';
import { randomString, randomIntBetween } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// Custom metrics
const errorRate = new Rate('errors');
const loginDuration = new Trend('login_duration');
const ticketCreateDuration = new Trend('ticket_create_duration');
const ticketListDuration = new Trend('ticket_list_duration');
const successfulLogins = new Counter('successful_logins');
const failedLogins = new Counter('failed_logins');

// Test configuration
export const options = {
  // Load test stages
  stages: [
    { duration: '1m', target: 10 },   // Warm up: ramp to 10 users
    { duration: '3m', target: 50 },   // Ramp up: increase to 50 users
    { duration: '5m', target: 50 },   // Steady state: maintain 50 users
    { duration: '3m', target: 100 },  // Peak load: increase to 100 users
    { duration: '5m', target: 100 },  // Sustained peak: maintain 100 users
    { duration: '2m', target: 50 },   // Scale down: reduce to 50 users
    { duration: '1m', target: 0 },    // Cool down: ramp down to 0
  ],
  
  // Performance thresholds
  thresholds: {
    // HTTP request duration
    'http_req_duration': ['p(95)<500', 'p(99)<1000'],
    'http_req_duration{type:login}': ['p(95)<300'],
    'http_req_duration{type:api}': ['p(95)<200'],
    
    // Error rate
    'http_req_failed': ['rate<0.01'],  // Less than 1% errors
    'errors': ['rate<0.05'],           // Less than 5% custom errors
    
    // Custom metrics
    'login_duration': ['p(95)<500'],
    'ticket_create_duration': ['p(95)<400'],
    'ticket_list_duration': ['p(95)<300'],
    
    // Throughput
    'http_reqs': ['rate>10'],  // At least 10 requests per second
  },
  
  // Tags for result filtering
  tags: {
    testType: 'load',
    environment: __ENV.ENVIRONMENT || 'staging'
  },
  
  // Summary configuration
  summaryTrendStats: ['avg', 'min', 'med', 'max', 'p(90)', 'p(95)', 'p(99)'],
};

// Environment configuration
const BASE_URL = __ENV.BASE_URL || 'http://localhost:5000';
const FRONTEND_URL = __ENV.FRONTEND_URL || 'http://localhost:3000';

// Test data
const testUsers = [
  { email: 'test1@example.com', password: 'password123' },
  { email: 'test2@example.com', password: 'password123' },
  { email: 'test3@example.com', password: 'password123' },
  { email: 'test4@example.com', password: 'password123' },
  { email: 'test5@example.com', password: 'password123' },
];

// Helper function to get random user
function getRandomUser() {
  return testUsers[randomIntBetween(0, testUsers.length - 1)];
}

// Setup function - runs once before tests
export function setup() {
  console.log('Starting load test against:', BASE_URL);
  
  // Verify API is accessible
  const healthCheck = http.get(`${BASE_URL}/api/health`);
  if (healthCheck.status !== 200) {
    throw new Error(`API health check failed: ${healthCheck.status}`);
  }
  
  return { startTime: new Date().toISOString() };
}

// Main test function
export default function(data) {
  const user = getRandomUser();
  let token = null;
  
  // Group: Authentication
  group('Authentication', function() {
    // Login
    const loginStart = new Date();
    const loginRes = http.post(
      `${BASE_URL}/api/auth/login`,
      JSON.stringify({
        email: user.email,
        password: user.password
      }),
      {
        headers: { 'Content-Type': 'application/json' },
        tags: { type: 'login' }
      }
    );
    
    loginDuration.add(new Date() - loginStart);
    
    const loginSuccess = check(loginRes, {
      'login status is 200': (r) => r.status === 200,
      'login has token': (r) => r.json('token') !== undefined,
      'login response time < 500ms': (r) => r.timings.duration < 500,
    });
    
    if (loginSuccess) {
      successfulLogins.add(1);
      token = loginRes.json('token');
    } else {
      failedLogins.add(1);
      errorRate.add(1);
    }
  });
  
  // Skip remaining tests if login failed
  if (!token) {
    sleep(1);
    return;
  }
  
  const authHeaders = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };
  
  // Group: Ticket Operations
  group('Ticket Operations', function() {
    // List tickets
    const listStart = new Date();
    const listRes = http.get(
      `${BASE_URL}/api/tickets`,
      { headers: authHeaders, tags: { type: 'api' } }
    );
    ticketListDuration.add(new Date() - listStart);
    
    check(listRes, {
      'list tickets status is 200': (r) => r.status === 200,
      'list tickets response time < 300ms': (r) => r.timings.duration < 300,
    }) || errorRate.add(1);
    
    // Create ticket
    const createStart = new Date();
    const createRes = http.post(
      `${BASE_URL}/api/tickets`,
      JSON.stringify({
        title: `Load Test Ticket ${randomString(8)}`,
        description: `This is a load test ticket created at ${new Date().toISOString()}`,
        priority: ['low', 'medium', 'high'][randomIntBetween(0, 2)]
      }),
      { headers: authHeaders, tags: { type: 'api' } }
    );
    ticketCreateDuration.add(new Date() - createStart);
    
    const createSuccess = check(createRes, {
      'create ticket status is 201': (r) => r.status === 201,
      'create ticket has id': (r) => r.json('id') !== undefined || r.json('ticket') !== undefined,
      'create ticket response time < 400ms': (r) => r.timings.duration < 400,
    });
    
    if (!createSuccess) {
      errorRate.add(1);
    }
    
    // Get single ticket (if created successfully)
    if (createRes.status === 201) {
      const ticketId = createRes.json('id') || createRes.json('ticket')?.id;
      if (ticketId) {
        const getRes = http.get(
          `${BASE_URL}/api/tickets/${ticketId}`,
          { headers: authHeaders, tags: { type: 'api' } }
        );
        
        check(getRes, {
          'get ticket status is 200': (r) => r.status === 200,
          'get ticket response time < 200ms': (r) => r.timings.duration < 200,
        }) || errorRate.add(1);
        
        // Update ticket
        const updateRes = http.put(
          `${BASE_URL}/api/tickets/${ticketId}`,
          JSON.stringify({
            status: 'in_progress'
          }),
          { headers: authHeaders, tags: { type: 'api' } }
        );
        
        check(updateRes, {
          'update ticket status is 200': (r) => r.status === 200,
        }) || errorRate.add(1);
      }
    }
  });
  
  // Group: Search and Filter
  group('Search and Filter', function() {
    // Search tickets
    const searchRes = http.get(
      `${BASE_URL}/api/tickets?search=test`,
      { headers: authHeaders, tags: { type: 'api' } }
    );
    
    check(searchRes, {
      'search status is 200': (r) => r.status === 200,
      'search response time < 500ms': (r) => r.timings.duration < 500,
    }) || errorRate.add(1);
    
    // Filter by status
    const filterRes = http.get(
      `${BASE_URL}/api/tickets?status=open`,
      { headers: authHeaders, tags: { type: 'api' } }
    );
    
    check(filterRes, {
      'filter status is 200': (r) => r.status === 200,
    }) || errorRate.add(1);
    
    // Pagination
    const paginatedRes = http.get(
      `${BASE_URL}/api/tickets?page=1&per_page=10`,
      { headers: authHeaders, tags: { type: 'api' } }
    );
    
    check(paginatedRes, {
      'pagination status is 200': (r) => r.status === 200,
    }) || errorRate.add(1);
  });
  
  // Think time between iterations
  sleep(randomIntBetween(1, 3));
}

// Teardown function - runs once after all tests
export function teardown(data) {
  console.log('Load test completed');
  console.log('Started at:', data.startTime);
  console.log('Ended at:', new Date().toISOString());
}

// Handle summary
export function handleSummary(data) {
  return {
    'reports/k6-summary.json': JSON.stringify(data, null, 2),
    'reports/k6-summary.html': htmlReport(data),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}

// Generate HTML report
function htmlReport(data) {
  const metrics = data.metrics;
  return `
<!DOCTYPE html>
<html>
<head>
  <title>k6 Load Test Report</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
    .container { max-width: 1200px; margin: 0 auto; }
    .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }
    .metric-card { background: white; padding: 20px; margin: 10px 0; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    .metric-title { font-weight: bold; color: #2c3e50; }
    .metric-value { font-size: 24px; color: #27ae60; }
    .metric-value.warning { color: #f39c12; }
    .metric-value.error { color: #e74c3c; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>k6 Load Test Report</h1>
      <p>Generated: ${new Date().toISOString()}</p>
    </div>
    <div class="grid">
      <div class="metric-card">
        <div class="metric-title">Total Requests</div>
        <div class="metric-value">${metrics.http_reqs?.values?.count || 0}</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Avg Response Time</div>
        <div class="metric-value">${(metrics.http_req_duration?.values?.avg || 0).toFixed(2)}ms</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">P95 Response Time</div>
        <div class="metric-value">${(metrics.http_req_duration?.values?.['p(95)'] || 0).toFixed(2)}ms</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Error Rate</div>
        <div class="metric-value ${(metrics.http_req_failed?.values?.rate || 0) > 0.01 ? 'error' : ''}">${((metrics.http_req_failed?.values?.rate || 0) * 100).toFixed(2)}%</div>
      </div>
    </div>
  </div>
</body>
</html>
  `;
}

// Text summary helper
function textSummary(data, options) {
  const metrics = data.metrics;
  return `
========================================
k6 Load Test Summary
========================================
Total Requests:     ${metrics.http_reqs?.values?.count || 0}
Avg Response Time:  ${(metrics.http_req_duration?.values?.avg || 0).toFixed(2)}ms
P95 Response Time:  ${(metrics.http_req_duration?.values?.['p(95)'] || 0).toFixed(2)}ms
P99 Response Time:  ${(metrics.http_req_duration?.values?.['p(99)'] || 0).toFixed(2)}ms
Error Rate:         ${((metrics.http_req_failed?.values?.rate || 0) * 100).toFixed(2)}%
Successful Logins:  ${metrics.successful_logins?.values?.count || 0}
Failed Logins:      ${metrics.failed_logins?.values?.count || 0}
========================================
  `;
}
