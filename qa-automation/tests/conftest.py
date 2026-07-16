"""
Root conftest.py for QA Automation Tests
Shared fixtures and configuration for all test types
"""

import pytest
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "security: Security tests")
    config.addinivalue_line("markers", "slow: Slow running tests")


@pytest.fixture(scope="session")
def project_root():
    """Return project root path"""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def qa_root():
    """Return QA automation root path"""
    return PROJECT_ROOT / 'qa-automation'


@pytest.fixture(scope="session")
def base_url():
    """Base URL for frontend"""
    return os.environ.get("BASE_URL", "http://localhost:3000")


@pytest.fixture(scope="session")
def api_url():
    """Base URL for API"""
    return os.environ.get("API_URL", "http://localhost:5000")


@pytest.fixture(scope="session")
def test_credentials():
    """Test user credentials"""
    return {
        "email": os.environ.get("TEST_USER_EMAIL", "test@example.com"),
        "password": os.environ.get("TEST_USER_PASSWORD", "password123")
    }


@pytest.fixture
def api_client(api_url):
    """Create an API client for testing"""
    import requests
    
    class APIClient:
        def __init__(self, base_url):
            self.base_url = base_url
            self.session = requests.Session()
            self.token = None
        
        def login(self, email, password):
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"email": email, "password": password}
            )
            if response.status_code == 200:
                self.token = response.json().get("token")
                self.session.headers["Authorization"] = f"Bearer {self.token}"
            return response
        
        def get(self, endpoint, **kwargs):
            return self.session.get(f"{self.base_url}{endpoint}", **kwargs)
        
        def post(self, endpoint, **kwargs):
            return self.session.post(f"{self.base_url}{endpoint}", **kwargs)
        
        def put(self, endpoint, **kwargs):
            return self.session.put(f"{self.base_url}{endpoint}", **kwargs)
        
        def delete(self, endpoint, **kwargs):
            return self.session.delete(f"{self.base_url}{endpoint}", **kwargs)
    
    return APIClient(api_url)


@pytest.fixture
def authenticated_api_client(api_client, test_credentials):
    """Create an authenticated API client"""
    api_client.login(test_credentials["email"], test_credentials["password"])
    return api_client
