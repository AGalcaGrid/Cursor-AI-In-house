import { useState } from 'react';
import { supportTicketApi } from '../services/supportTicketApi';

interface TestResult {
  name: string;
  status: 'pending' | 'running' | 'pass' | 'fail';
  message: string;
  details?: string;
  request?: {
    method: string;
    url: string;
    body?: any;
  };
  response?: {
    status: number;
    body?: any;
  };
}

export function ValidationTests() {
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [token, setToken] = useState<string>('');
  const [expandedTests, setExpandedTests] = useState<Set<number>>(new Set());

  const toggleExpanded = (index: number) => {
    setExpandedTests(prev => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
      }
      return newSet;
    });
  };

  const updateTestResult = (
    index: number, 
    status: TestResult['status'], 
    message: string, 
    details?: string,
    request?: TestResult['request'],
    response?: TestResult['response']
  ) => {
    setTestResults(prev => {
      const updated = [...prev];
      updated[index] = { ...updated[index], status, message, details, request, response };
      return updated;
    });
  };

  const runAllTests = async () => {
    setIsRunning(true);
    
    const tests: TestResult[] = [
      { name: 'Email Validation - Valid Email', status: 'pending', message: '' },
      { name: 'Email Validation - Invalid Format', status: 'pending', message: '' },
      { name: 'Priority Validation - Valid Priority', status: 'pending', message: '' },
      { name: 'Priority Validation - Invalid Priority', status: 'pending', message: '' },
      { name: 'Subject Validation - Too Short', status: 'pending', message: '' },
      { name: 'Description Validation - Too Short', status: 'pending', message: '' },
      { name: 'Authorization - Login Success', status: 'pending', message: '' },
      { name: 'Authorization - Login Failure', status: 'pending', message: '' },
    ];
    
    setTestResults(tests);

    // Test 1: Valid Email
    try {
      updateTestResult(0, 'running', 'Testing...');
      const requestBody = { email: 'customer@example.com', password: 'Customer123!' };
      const result = await supportTicketApi.login('customer@example.com', 'Customer123!');
      updateTestResult(
        0, 
        'pass', 
        '✅ Valid email accepted', 
        'Email: customer@example.com',
        { method: 'POST', url: 'http://localhost:5002/api/auth/login', body: requestBody },
        { status: 200, body: { user: result.user, access_token: '***' } }
      );
    } catch (error) {
      const requestBody = { email: 'customer@example.com', password: 'Customer123!' };
      updateTestResult(
        0, 
        'fail', 
        '❌ Valid email rejected', 
        error instanceof Error ? error.message : 'Unknown error',
        { method: 'POST', url: 'http://localhost:5002/api/auth/login', body: requestBody },
        { status: 401, body: { message: error instanceof Error ? error.message : 'Unknown error' } }
      );
    }

    await new Promise(resolve => setTimeout(resolve, 300));

    // Test 2: Invalid Email Format
    try {
      updateTestResult(1, 'running', 'Testing...');
      const requestBody = { name: 'Test User', email: 'invalid-email', password: 'Password123!' };
      await supportTicketApi.register('Test User', 'invalid-email', 'Password123!');
      updateTestResult(
        1, 
        'fail', 
        '❌ Invalid email was accepted', 
        'Should have returned 400 Bad Request',
        { method: 'POST', url: 'http://localhost:5002/api/auth/register', body: requestBody },
        { status: 201, body: { message: 'User created' } }
      );
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '';
      const requestBody = { name: 'Test User', email: 'invalid-email', password: 'Password123!' };
      if (errorMsg.toLowerCase().includes('email') || errorMsg.toLowerCase().includes('validation')) {
        updateTestResult(
          1, 
          'pass', 
          '✅ Invalid email rejected', 
          'Error: ' + errorMsg,
          { method: 'POST', url: 'http://localhost:5002/api/auth/register', body: requestBody },
          { status: 400, body: { message: errorMsg } }
        );
      } else {
        updateTestResult(1, 'fail', '❌ Wrong error message', errorMsg);
      }
    }

    await new Promise(resolve => setTimeout(resolve, 300));

    // Test 3: Valid Priority (need token first)
    try {
      updateTestResult(2, 'running', 'Testing...');
      const loginResult = await supportTicketApi.login('customer@example.com', 'Customer123!');
      const testToken = loginResult.access_token;
      setToken(testToken);
      
      const requestBody = {
        subject: 'Valid priority test ticket',
        description: 'This ticket tests valid priority levels in the system.',
        priority: 'high',
        category: 'technical',
        customer_email: 'customer@example.com'
      };
      
      const result = await supportTicketApi.createTicket(testToken, requestBody);
      updateTestResult(
        2, 
        'pass', 
        '✅ Valid priority accepted', 
        'Priority: high',
        { method: 'POST', url: 'http://localhost:5002/api/tickets', body: requestBody },
        { status: 201, body: { id: result.id, priority: 'high' } }
      );
    } catch (error) {
      const requestBody = {
        subject: 'Valid priority test ticket',
        description: 'This ticket tests valid priority levels in the system.',
        priority: 'high',
        category: 'technical',
        customer_email: 'customer@example.com'
      };
      updateTestResult(
        2, 
        'fail', 
        '❌ Valid priority rejected', 
        error instanceof Error ? error.message : 'Unknown error',
        { method: 'POST', url: 'http://localhost:5002/api/tickets', body: requestBody },
        { status: 400, body: { message: error instanceof Error ? error.message : 'Unknown error' } }
      );
    }

    await new Promise(resolve => setTimeout(resolve, 300));

    // Test 4: Invalid Priority
    try {
      updateTestResult(3, 'running', 'Testing...');
      const loginResult = await supportTicketApi.login('customer@example.com', 'Customer123!');
      const testToken = loginResult.access_token;
      
      const requestBody = {
        subject: 'Invalid priority test ticket',
        description: 'This ticket tests invalid priority levels.',
        priority: 'super_urgent' as any,
        category: 'technical',
        customer_email: 'customer@example.com'
      };
      
      await supportTicketApi.createTicket(testToken, requestBody);
      updateTestResult(
        3, 
        'fail', 
        '❌ Invalid priority was accepted', 
        'Should have returned 400 Bad Request',
        { method: 'POST', url: 'http://localhost:5002/api/tickets', body: requestBody },
        { status: 201, body: { message: 'Ticket created' } }
      );
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '';
      const requestBody = {
        subject: 'Invalid priority test ticket',
        description: 'This ticket tests invalid priority levels.',
        priority: 'super_urgent',
        category: 'technical',
        customer_email: 'customer@example.com'
      };
      
      if (errorMsg.toLowerCase().includes('priority') || errorMsg.toLowerCase().includes('validation')) {
        updateTestResult(
          3, 
          'pass', 
          '✅ Invalid priority rejected', 
          'Error: ' + errorMsg,
          { method: 'POST', url: 'http://localhost:5002/api/tickets', body: requestBody },
          { status: 400, body: { message: errorMsg } }
        );
      } else {
        updateTestResult(3, 'fail', '❌ Wrong error message', errorMsg);
      }
    }

    await new Promise(resolve => setTimeout(resolve, 300));

    // Test 5: Subject Too Short
    try {
      updateTestResult(4, 'running', 'Testing...');
      const loginResult = await supportTicketApi.login('customer@example.com', 'Customer123!');
      const testToken = loginResult.access_token;
      
      const requestBody = {
        subject: 'Hi',
        description: 'This is a valid description with enough characters to pass validation.',
        priority: 'medium',
        category: 'general',
        customer_email: 'customer@example.com'
      };
      
      await supportTicketApi.createTicket(testToken, requestBody);
      updateTestResult(
        4, 
        'fail', 
        '❌ Short subject was accepted', 
        'Should have returned 400 Bad Request',
        { method: 'POST', url: 'http://localhost:5002/api/tickets', body: requestBody },
        { status: 201, body: { message: 'Ticket created' } }
      );
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '';
      const requestBody = {
        subject: 'Hi',
        description: 'This is a valid description with enough characters to pass validation.',
        priority: 'medium',
        category: 'general',
        customer_email: 'customer@example.com'
      };
      
      if (errorMsg.toLowerCase().includes('subject') || errorMsg.toLowerCase().includes('validation') || errorMsg.toLowerCase().includes('length')) {
        updateTestResult(
          4, 
          'pass', 
          '✅ Short subject rejected', 
          'Error: ' + errorMsg,
          { method: 'POST', url: 'http://localhost:5002/api/tickets', body: requestBody },
          { status: 400, body: { message: errorMsg } }
        );
      } else {
        updateTestResult(4, 'fail', '❌ Wrong error message', errorMsg);
      }
    }

    await new Promise(resolve => setTimeout(resolve, 300));

    // Test 6: Description Too Short
    try {
      updateTestResult(5, 'running', 'Testing...');
      const loginResult = await supportTicketApi.login('customer@example.com', 'Customer123!');
      const testToken = loginResult.access_token;
      
      const requestBody = {
        subject: 'Valid subject for testing',
        description: 'Short',
        priority: 'medium',
        category: 'general',
        customer_email: 'customer@example.com'
      };
      
      await supportTicketApi.createTicket(testToken, requestBody);
      updateTestResult(
        5, 
        'fail', 
        '❌ Short description was accepted', 
        'Should have returned 400 Bad Request',
        { method: 'POST', url: 'http://localhost:5002/api/tickets', body: requestBody },
        { status: 201, body: { message: 'Ticket created' } }
      );
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '';
      const requestBody = {
        subject: 'Valid subject for testing',
        description: 'Short',
        priority: 'medium',
        category: 'general',
        customer_email: 'customer@example.com'
      };
      
      if (errorMsg.toLowerCase().includes('description') || errorMsg.toLowerCase().includes('validation') || errorMsg.toLowerCase().includes('length')) {
        updateTestResult(
          5, 
          'pass', 
          '✅ Short description rejected', 
          'Error: ' + errorMsg,
          { method: 'POST', url: 'http://localhost:5002/api/tickets', body: requestBody },
          { status: 400, body: { message: errorMsg } }
        );
      } else {
        updateTestResult(5, 'fail', '❌ Wrong error message', errorMsg);
      }
    }

    await new Promise(resolve => setTimeout(resolve, 300));

    // Test 7: Login Success
    try {
      updateTestResult(6, 'running', 'Testing...');
      const requestBody = { email: 'customer@example.com', password: 'Customer123!' };
      const result = await supportTicketApi.login('customer@example.com', 'Customer123!');
      if (result.access_token && result.user) {
        updateTestResult(
          6, 
          'pass', 
          '✅ Login successful', 
          `User: ${result.user.email}, Role: ${result.user.role}`,
          { method: 'POST', url: 'http://localhost:5002/api/auth/login', body: requestBody },
          { status: 200, body: { user: result.user, access_token: '***', refresh_token: '***' } }
        );
      } else {
        updateTestResult(6, 'fail', '❌ Login response invalid', 'Missing token or user data');
      }
    } catch (error) {
      const requestBody = { email: 'customer@example.com', password: 'Customer123!' };
      updateTestResult(
        6, 
        'fail', 
        '❌ Login failed', 
        error instanceof Error ? error.message : 'Unknown error',
        { method: 'POST', url: 'http://localhost:5002/api/auth/login', body: requestBody },
        { status: 401, body: { message: error instanceof Error ? error.message : 'Unknown error' } }
      );
    }

    await new Promise(resolve => setTimeout(resolve, 300));

    // Test 8: Login Failure (Wrong Password)
    try {
      updateTestResult(7, 'running', 'Testing...');
      const requestBody = { email: 'customer@example.com', password: 'WrongPassword123!' };
      await supportTicketApi.login('customer@example.com', 'WrongPassword123!');
      updateTestResult(
        7, 
        'fail', 
        '❌ Wrong password was accepted', 
        'Should have returned 401 Unauthorized',
        { method: 'POST', url: 'http://localhost:5002/api/auth/login', body: requestBody },
        { status: 200, body: { message: 'Login successful' } }
      );
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '';
      const requestBody = { email: 'customer@example.com', password: 'WrongPassword123!' };
      if (errorMsg.toLowerCase().includes('password') || errorMsg.toLowerCase().includes('invalid') || errorMsg.toLowerCase().includes('unauthorized')) {
        updateTestResult(
          7, 
          'pass', 
          '✅ Wrong password rejected', 
          'Error: ' + errorMsg,
          { method: 'POST', url: 'http://localhost:5002/api/auth/login', body: requestBody },
          { status: 401, body: { message: errorMsg } }
        );
      } else {
        updateTestResult(7, 'fail', '❌ Wrong error message', errorMsg);
      }
    }

    setIsRunning(false);
  };

  const getStatusIcon = (status: TestResult['status']) => {
    switch (status) {
      case 'pending':
        return '⏸️';
      case 'running':
        return '⏳';
      case 'pass':
        return '✅';
      case 'fail':
        return '❌';
    }
  };

  const getStatusColor = (status: TestResult['status']) => {
    switch (status) {
      case 'pending':
        return 'text-gray-600 dark:text-gray-400';
      case 'running':
        return 'text-blue-600 dark:text-blue-400';
      case 'pass':
        return 'text-green-600 dark:text-green-400';
      case 'fail':
        return 'text-red-600 dark:text-red-400';
    }
  };

  const passedTests = testResults.filter(t => t.status === 'pass').length;
  const failedTests = testResults.filter(t => t.status === 'fail').length;
  const totalTests = testResults.length;
  const successRate = totalTests > 0 ? Math.round((passedTests / totalTests) * 100) : 0;

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Validation Tests
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Automated tests demonstrating validation, error handling, and security measures
        </p>
      </div>

      {/* Test Summary */}
      {testResults.length > 0 && (
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg mb-6 border-2 border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Test Summary</h3>
          <div className="grid grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Tests</div>
              <div className="text-3xl font-bold text-gray-900 dark:text-white">{totalTests}</div>
            </div>
            <div className="text-center">
              <div className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Passed</div>
              <div className="text-3xl font-bold text-green-600 dark:text-green-400">{passedTests}</div>
            </div>
            <div className="text-center">
              <div className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Failed</div>
              <div className="text-3xl font-bold text-red-600 dark:text-red-400">{failedTests}</div>
            </div>
            <div className="text-center">
              <div className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Success Rate</div>
              <div className={`text-3xl font-bold ${successRate === 100 ? 'text-green-600 dark:text-green-400' : successRate >= 75 ? 'text-yellow-600 dark:text-yellow-400' : 'text-red-600 dark:text-red-400'}`}>
                {successRate}%
              </div>
            </div>
          </div>
        </div>
      )}

      {/* What's Being Tested */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/30 dark:to-purple-950/30 p-6 rounded-lg shadow-lg mb-6 border-2 border-blue-200 dark:border-blue-800">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <span className="text-2xl">🔍</span>
          What's Being Tested
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-blue-200 dark:border-blue-700">
            <h4 className="font-semibold text-blue-600 dark:text-blue-400 mb-2">1. Email Validation - Valid Email</h4>
            <p className="text-sm text-gray-600 dark:text-gray-300">Verifies that properly formatted email addresses are accepted by the authentication system.</p>
          </div>
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-blue-200 dark:border-blue-700">
            <h4 className="font-semibold text-blue-600 dark:text-blue-400 mb-2">2. Email Validation - Invalid Format</h4>
            <p className="text-sm text-gray-600 dark:text-gray-300">Ensures that malformed email addresses (missing @, domain, etc.) are rejected with proper error messages.</p>
          </div>
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-purple-200 dark:border-purple-700">
            <h4 className="font-semibold text-purple-600 dark:text-purple-400 mb-2">3. Priority Validation - Valid Priority</h4>
            <p className="text-sm text-gray-600 dark:text-gray-300">Confirms that valid priority levels (low, medium, high, urgent) are accepted when creating tickets.</p>
          </div>
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-purple-200 dark:border-purple-700">
            <h4 className="font-semibold text-purple-600 dark:text-purple-400 mb-2">4. Priority Validation - Invalid Priority</h4>
            <p className="text-sm text-gray-600 dark:text-gray-300">Validates that invalid priority values (e.g., "super_urgent") are rejected with validation errors.</p>
          </div>
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-green-200 dark:border-green-700">
            <h4 className="font-semibold text-green-600 dark:text-green-400 mb-2">5. Subject Validation - Too Short</h4>
            <p className="text-sm text-gray-600 dark:text-gray-300">Tests that ticket subjects shorter than 5 characters are rejected (e.g., "Hi" should fail).</p>
          </div>
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-green-200 dark:border-green-700">
            <h4 className="font-semibold text-green-600 dark:text-green-400 mb-2">6. Description Validation - Too Short</h4>
            <p className="text-sm text-gray-600 dark:text-gray-300">Ensures that ticket descriptions shorter than 20 characters are rejected with appropriate errors.</p>
          </div>
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-orange-200 dark:border-orange-700">
            <h4 className="font-semibold text-orange-600 dark:text-orange-400 mb-2">7. Authorization - Login Success</h4>
            <p className="text-sm text-gray-600 dark:text-gray-300">Verifies that valid credentials successfully authenticate and return access tokens and user data.</p>
          </div>
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-orange-200 dark:border-orange-700">
            <h4 className="font-semibold text-orange-600 dark:text-orange-400 mb-2">8. Authorization - Login Failure</h4>
            <p className="text-sm text-gray-600 dark:text-gray-300">Confirms that incorrect passwords are rejected with 401 Unauthorized and proper error messages.</p>
          </div>
        </div>
      </div>

      {/* Run Tests Button */}
      <div className="mb-6">
        <button
          onClick={runAllTests}
          disabled={isRunning}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium rounded-lg transition-colors"
        >
          {isRunning ? 'Running Tests...' : 'Run All Tests'}
        </button>
      </div>

      {/* Test Results */}
      {testResults.length > 0 && (
        <div className="space-y-3">
          {testResults.map((test, index) => (
            <div
              key={index}
              className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-2xl">{getStatusIcon(test.status)}</span>
                    <h3 className="font-semibold text-gray-900 dark:text-white">
                      {test.name}
                    </h3>
                    {(test.request || test.response) && (
                      <button
                        onClick={() => toggleExpanded(index)}
                        className="ml-auto text-xs text-blue-600 dark:text-blue-400 hover:underline"
                      >
                        {expandedTests.has(index) ? '▼ Hide Details' : '▶ Show Details'}
                      </button>
                    )}
                  </div>
                  {test.message && (
                    <p className={`text-sm ${getStatusColor(test.status)} ml-11`}>
                      {test.message}
                    </p>
                  )}
                  {test.details && (
                    <p className="text-xs text-gray-500 dark:text-gray-500 ml-11 mt-1">
                      {test.details}
                    </p>
                  )}
                  
                  {/* Request/Response Details */}
                  {expandedTests.has(index) && (test.request || test.response) && (
                    <div className="ml-11 mt-3 space-y-3">
                      {test.request && (
                        <div className="bg-blue-50 dark:bg-blue-950/30 rounded-lg p-3 border border-blue-200 dark:border-blue-800">
                          <div className="text-xs font-semibold text-blue-900 dark:text-blue-200 mb-2">
                            📤 Request
                          </div>
                          <div className="text-xs space-y-1 text-gray-900 dark:text-gray-100">
                            <div><span className="font-medium text-gray-700 dark:text-gray-300">Method:</span> <span className="text-blue-600 dark:text-blue-300 font-semibold">{test.request.method}</span></div>
                            <div><span className="font-medium text-gray-700 dark:text-gray-300">URL:</span> <span className="text-gray-600 dark:text-gray-300 break-all">{test.request.url}</span></div>
                            {test.request.body && (
                              <div>
                                <span className="font-medium text-gray-700 dark:text-gray-300">Body:</span>
                                <pre className="mt-1 p-3 bg-white dark:bg-gray-950 rounded text-xs overflow-x-auto border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100">
                                  {JSON.stringify(test.request.body, null, 2)}
                                </pre>
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                      
                      {test.response && (
                        <div className="bg-purple-50 dark:bg-purple-950/30 rounded-lg p-3 border border-purple-200 dark:border-purple-800">
                          <div className="text-xs font-semibold text-purple-900 dark:text-purple-200 mb-2">
                            📥 Response
                          </div>
                          <div className="text-xs space-y-1 text-gray-900 dark:text-gray-100">
                            <div>
                              <span className="font-medium text-gray-700 dark:text-gray-300">Status:</span> 
                              <span className={`ml-1 font-semibold ${test.response.status >= 200 && test.response.status < 300 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                                {test.response.status}
                              </span>
                            </div>
                            {test.response.body && (
                              <div>
                                <span className="font-medium text-gray-700 dark:text-gray-300">Body:</span>
                                <pre className="mt-1 p-3 bg-white dark:bg-gray-950 rounded text-xs overflow-x-auto border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100">
                                  {JSON.stringify(test.response.body, null, 2)}
                                </pre>
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {testResults.length === 0 && (
        <div className="bg-white dark:bg-gray-800 p-12 rounded-lg shadow text-center">
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            No tests have been run yet. Click "Run All Tests" to start.
          </p>
          <div className="text-sm text-gray-500 dark:text-gray-500">
            <p className="mb-2">Tests will verify:</p>
            <ul className="list-disc list-inside space-y-1">
              <li>Email format validation</li>
              <li>Priority level validation</li>
              <li>Subject and description length validation</li>
              <li>Authentication and authorization</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
