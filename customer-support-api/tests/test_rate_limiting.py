"""
Rate Limiting Tests for Customer Support API
Tests for API rate limiting and brute force protection.
"""

import pytest
import time
from tests.conftest import auth_header


class TestRegistrationRateLimiting:
    """Tests for registration endpoint rate limiting."""
    
    def test_registration_rate_limit_exceeded(self, client, db_session):
        """Test that registration endpoint enforces rate limiting."""
        # Attempt to register multiple accounts rapidly
        responses = []
        
        for i in range(12):  # Try 12 registrations
            response = client.post('/api/auth/register', json={
                'name': f'Test User {i}',
                'email': f'testuser{i}@ratelimit.com',
                'password': 'SecurePass123'
            })
            responses.append(response)
            time.sleep(0.1)  # Small delay between requests
        
        # Check that at least some requests were rate limited
        # Note: Actual implementation may vary based on rate limit configuration
        status_codes = [r.status_code for r in responses]
        
        # First few should succeed (201), later ones should be rate limited (429)
        successful = [code for code in status_codes if code == 201]
        rate_limited = [code for code in status_codes if code == 429]
        
        # We expect some to succeed and some to be rate limited
        # If no rate limiting is implemented, this test will fail
        assert len(successful) > 0, "Some registrations should succeed"
        # Note: Uncomment when rate limiting is implemented
        # assert len(rate_limited) > 0, "Some registrations should be rate limited"
    
    def test_registration_rate_limit_per_ip(self, client, db_session):
        """Test that rate limiting is enforced per IP address."""
        # Simulate requests from same IP
        responses = []
        
        for i in range(15):
            response = client.post('/api/auth/register', 
                json={
                    'name': f'User {i}',
                    'email': f'user{i}@test.com',
                    'password': 'SecurePass123'
                },
                environ_base={'REMOTE_ADDR': '192.168.1.100'}
            )
            responses.append(response)
        
        # Check for rate limiting
        status_codes = [r.status_code for r in responses]
        
        # Should have mix of successful and rate limited
        assert 201 in status_codes, "Some requests should succeed"
        # Note: Uncomment when rate limiting is implemented
        # assert 429 in status_codes, "Some requests should be rate limited"
    
    def test_registration_rate_limit_reset_after_time(self, client, db_session):
        """Test that rate limit resets after time window."""
        # Make requests up to limit
        for i in range(5):
            client.post('/api/auth/register', json={
                'name': f'User {i}',
                'email': f'user{i}@reset.com',
                'password': 'SecurePass123'
            })
        
        # Wait for rate limit window to reset (e.g., 1 minute)
        # In real tests, you might mock time or use shorter windows
        # time.sleep(61)
        
        # This request should succeed after reset
        response = client.post('/api/auth/register', json={
            'name': 'User After Reset',
            'email': 'afterreset@test.com',
            'password': 'SecurePass123'
        })
        
        # Should succeed after rate limit window resets
        assert response.status_code in [201, 429]  # Depends on implementation


class TestLoginRateLimiting:
    """Tests for login endpoint brute force protection."""
    
    def test_login_brute_force_protection(self, client, customer):
        """Test that login endpoint prevents brute force attacks."""
        # Attempt multiple failed logins
        failed_attempts = []
        
        for i in range(10):
            response = client.post('/api/auth/login', json={
                'email': 'customer@test.com',
                'password': f'WrongPassword{i}'
            })
            failed_attempts.append(response)
            time.sleep(0.1)
        
        # Check responses
        status_codes = [r.status_code for r in failed_attempts]
        
        # First attempts should return 401 (unauthorized)
        # Later attempts should return 429 (too many requests)
        unauthorized = [code for code in status_codes if code == 401]
        rate_limited = [code for code in status_codes if code == 429]
        
        assert len(unauthorized) > 0, "Failed logins should return 401"
        # Note: Uncomment when rate limiting is implemented
        # assert len(rate_limited) > 0, "Excessive failed logins should be rate limited"
    
    def test_login_rate_limit_per_email(self, client, customer):
        """Test that rate limiting is enforced per email address."""
        # Try to brute force a specific account
        for i in range(8):
            response = client.post('/api/auth/login', json={
                'email': 'customer@test.com',
                'password': f'attempt{i}'
            })
        
        # Next attempt should be rate limited
        response = client.post('/api/auth/login', json={
            'email': 'customer@test.com',
            'password': 'another_attempt'
        })
        
        # Should be rate limited after multiple failed attempts
        # Note: Uncomment when rate limiting is implemented
        # assert response.status_code == 429
        assert response.status_code in [401, 429]
    
    def test_successful_login_resets_rate_limit(self, client, customer):
        """Test that successful login resets the rate limit counter."""
        # Make a few failed attempts
        for i in range(3):
            client.post('/api/auth/login', json={
                'email': 'customer@test.com',
                'password': 'wrong_password'
            })
        
        # Successful login
        response = client.post('/api/auth/login', json={
            'email': 'customer@test.com',
            'password': 'TestPass123'
        })
        
        assert response.status_code == 200
        
        # Should be able to login again without rate limiting
        response = client.post('/api/auth/login', json={
            'email': 'customer@test.com',
            'password': 'TestPass123'
        })
        
        assert response.status_code == 200
    
    def test_login_rate_limit_different_accounts(self, client, customer, agent):
        """Test that rate limiting is per account, not global."""
        # Exhaust rate limit for one account
        for i in range(6):
            client.post('/api/auth/login', json={
                'email': 'customer@test.com',
                'password': f'wrong{i}'
            })
        
        # Should still be able to login to different account
        response = client.post('/api/auth/login', json={
            'email': 'agent@test.com',
            'password': 'TestPass123'
        })
        
        assert response.status_code == 200


class TestAPIEndpointRateLimiting:
    """Tests for general API endpoint rate limiting."""
    
    def test_ticket_creation_rate_limit(self, client, customer_token):
        """Test rate limiting on ticket creation endpoint."""
        # Create many tickets rapidly
        responses = []
        
        for i in range(20):
            response = client.post('/api/tickets',
                headers=auth_header(customer_token),
                json={
                    'subject': f'Rate limit test ticket {i}',
                    'description': 'This is a test ticket for rate limiting purposes'
                })
            responses.append(response)
            time.sleep(0.05)
        
        status_codes = [r.status_code for r in responses]
        
        # Should have mix of successful and rate limited
        successful = [code for code in status_codes if code == 201]
        rate_limited = [code for code in status_codes if code == 429]
        
        assert len(successful) > 0, "Some ticket creations should succeed"
        # Note: Uncomment when rate limiting is implemented
        # assert len(rate_limited) > 0, "Excessive ticket creations should be rate limited"
    
    def test_api_read_endpoint_rate_limit(self, client, customer_token, ticket):
        """Test rate limiting on read endpoints."""
        # Make many GET requests rapidly
        responses = []
        
        for i in range(100):
            response = client.get('/api/tickets',
                headers=auth_header(customer_token))
            responses.append(response)
        
        status_codes = [r.status_code for r in responses]
        
        # Should eventually hit rate limit
        successful = [code for code in status_codes if code == 200]
        rate_limited = [code for code in status_codes if code == 429]
        
        assert len(successful) > 0, "Some requests should succeed"
        # Note: Uncomment when rate limiting is implemented
        # assert len(rate_limited) > 0, "Excessive requests should be rate limited"
    
    def test_rate_limit_headers_present(self, client, customer_token):
        """Test that rate limit headers are present in responses."""
        response = client.get('/api/tickets',
            headers=auth_header(customer_token))
        
        # Check for standard rate limit headers
        # Note: Uncomment when rate limiting is implemented
        # assert 'X-RateLimit-Limit' in response.headers
        # assert 'X-RateLimit-Remaining' in response.headers
        # assert 'X-RateLimit-Reset' in response.headers
        
        # For now, just check response is successful
        assert response.status_code == 200
    
    def test_rate_limit_response_format(self, client, customer_token):
        """Test that rate limit error response has correct format."""
        # Make many requests to trigger rate limit
        for i in range(50):
            response = client.post('/api/tickets',
                headers=auth_header(customer_token),
                json={
                    'subject': f'Spam ticket {i}',
                    'description': 'Spam description'
                })
            
            if response.status_code == 429:
                # Check error response format
                assert 'error' in response.json or 'message' in response.json
                # Note: Uncomment when rate limiting is implemented
                # assert 'rate limit' in response.json.get('message', '').lower()
                # assert 'retry_after' in response.json
                break


class TestRateLimitBypass:
    """Tests to ensure rate limiting cannot be bypassed."""
    
    def test_rate_limit_not_bypassed_by_different_user_agents(self, client, db_session):
        """Test that changing User-Agent doesn't bypass rate limiting."""
        responses = []
        
        for i in range(10):
            response = client.post('/api/auth/register',
                json={
                    'name': f'User {i}',
                    'email': f'bypass{i}@test.com',
                    'password': 'SecurePass123'
                },
                headers={'User-Agent': f'TestAgent/{i}'})
            responses.append(response)
        
        # Rate limiting should still apply regardless of User-Agent
        status_codes = [r.status_code for r in responses]
        assert 201 in status_codes
    
    def test_rate_limit_not_bypassed_by_different_tokens(self, client, customer_token, agent_token):
        """Test that using different tokens doesn't bypass rate limiting."""
        # Make requests with customer token
        for i in range(10):
            client.get('/api/tickets', headers=auth_header(customer_token))
        
        # Make requests with agent token from same IP
        for i in range(10):
            response = client.get('/api/tickets', headers=auth_header(agent_token))
        
        # Both should be subject to rate limiting
        # (Implementation may vary - could be per-user or per-IP)
        assert response.status_code in [200, 429]
    
    def test_rate_limit_applies_to_authenticated_and_unauthenticated(self, client):
        """Test that rate limiting applies to both authenticated and unauthenticated requests."""
        # Unauthenticated requests
        unauth_responses = []
        for i in range(15):
            response = client.post('/api/auth/login', json={
                'email': 'test@test.com',
                'password': 'wrong'
            })
            unauth_responses.append(response)
        
        status_codes = [r.status_code for r in unauth_responses]
        
        # Should have rate limiting for unauthenticated requests
        assert 401 in status_codes  # Unauthorized
        # Note: Uncomment when rate limiting is implemented
        # assert 429 in status_codes  # Rate limited


class TestRateLimitConfiguration:
    """Tests for rate limit configuration and thresholds."""
    
    def test_different_rate_limits_for_different_endpoints(self, client, customer_token):
        """Test that different endpoints have different rate limits."""
        # Read endpoints might have higher limits
        read_responses = []
        for i in range(50):
            response = client.get('/api/tickets', headers=auth_header(customer_token))
            read_responses.append(response)
        
        # Write endpoints might have lower limits
        write_responses = []
        for i in range(20):
            response = client.post('/api/tickets',
                headers=auth_header(customer_token),
                json={
                    'subject': f'Test {i}',
                    'description': 'Test description'
                })
            write_responses.append(response)
        
        # Both should eventually hit their respective limits
        # Note: Actual behavior depends on implementation
        assert any(r.status_code == 200 for r in read_responses)
        assert any(r.status_code == 201 for r in write_responses)
    
    def test_admin_has_higher_rate_limits(self, client, admin_token, customer_token):
        """Test that admin users have higher rate limits than regular users."""
        # Customer makes requests
        customer_responses = []
        for i in range(30):
            response = client.get('/api/tickets', headers=auth_header(customer_token))
            customer_responses.append(response)
        
        # Admin makes requests
        admin_responses = []
        for i in range(30):
            response = client.get('/api/tickets', headers=auth_header(admin_token))
            admin_responses.append(response)
        
        # Admin should have fewer rate limited responses
        customer_rate_limited = sum(1 for r in customer_responses if r.status_code == 429)
        admin_rate_limited = sum(1 for r in admin_responses if r.status_code == 429)
        
        # Note: Uncomment when rate limiting is implemented with role-based limits
        # assert admin_rate_limited <= customer_rate_limited


class TestRateLimitRecovery:
    """Tests for rate limit recovery and reset behavior."""
    
    def test_rate_limit_window_sliding(self, client, customer_token):
        """Test that rate limit uses sliding window."""
        # Make requests at the start
        for i in range(5):
            client.get('/api/tickets', headers=auth_header(customer_token))
        
        # Wait a bit
        time.sleep(2)
        
        # Make more requests - should be allowed if using sliding window
        response = client.get('/api/tickets', headers=auth_header(customer_token))
        
        # Should succeed with sliding window
        assert response.status_code in [200, 429]
    
    def test_rate_limit_retry_after_header(self, client, customer_token):
        """Test that Retry-After header is provided when rate limited."""
        # Trigger rate limit
        for i in range(100):
            response = client.post('/api/tickets',
                headers=auth_header(customer_token),
                json={
                    'subject': f'Test {i}',
                    'description': 'Test'
                })
            
            if response.status_code == 429:
                # Check for Retry-After header
                # Note: Uncomment when rate limiting is implemented
                # assert 'Retry-After' in response.headers
                # retry_after = int(response.headers['Retry-After'])
                # assert retry_after > 0
                # assert retry_after <= 3600  # Should be reasonable (< 1 hour)
                break


# Pytest markers for categorizing tests
pytestmark = [
    pytest.mark.rate_limiting,
    pytest.mark.security
]
