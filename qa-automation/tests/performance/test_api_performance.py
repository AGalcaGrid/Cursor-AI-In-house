import pytest
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed


class TestAPIPerformance:
    """Performance tests for API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from app import create_app
        app = create_app('testing')
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def auth_headers(self, client):
        """Get authentication headers"""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        token = response.json.get('token')
        return {'Authorization': f'Bearer {token}'}
    
    def measure_response_time(self, func, iterations=10):
        """Measure average response time over multiple iterations"""
        times = []
        for _ in range(iterations):
            start = time.time()
            func()
            end = time.time()
            times.append((end - start) * 1000)  # Convert to ms
        
        return {
            'avg': statistics.mean(times),
            'min': min(times),
            'max': max(times),
            'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
            'p95': sorted(times)[int(len(times) * 0.95)] if len(times) >= 20 else max(times)
        }
    
    def test_login_performance(self, client):
        """Test login endpoint performance"""
        def login():
            return client.post('/api/auth/login', json={
                'email': 'test@example.com',
                'password': 'password123'
            })
        
        metrics = self.measure_response_time(login, iterations=20)
        
        assert metrics['avg'] < 500, f"Average login time {metrics['avg']}ms exceeds 500ms threshold"
        assert metrics['p95'] < 1000, f"P95 login time {metrics['p95']}ms exceeds 1000ms threshold"
    
    def test_get_tickets_performance(self, client, auth_headers):
        """Test get tickets endpoint performance"""
        def get_tickets():
            return client.get('/api/tickets', headers=auth_headers)
        
        metrics = self.measure_response_time(get_tickets, iterations=20)
        
        assert metrics['avg'] < 200, f"Average response time {metrics['avg']}ms exceeds 200ms threshold"
        assert metrics['p95'] < 500, f"P95 response time {metrics['p95']}ms exceeds 500ms threshold"
    
    def test_create_ticket_performance(self, client, auth_headers):
        """Test create ticket endpoint performance"""
        counter = [0]
        
        def create_ticket():
            counter[0] += 1
            return client.post('/api/tickets', json={
                'title': f'Performance Test Ticket {counter[0]}',
                'description': 'Testing performance',
                'priority': 'low'
            }, headers=auth_headers)
        
        metrics = self.measure_response_time(create_ticket, iterations=20)
        
        assert metrics['avg'] < 300, f"Average create time {metrics['avg']}ms exceeds 300ms threshold"
    
    def test_concurrent_requests(self, client, auth_headers):
        """Test API under concurrent load"""
        num_concurrent = 10
        results = []
        
        def make_request():
            start = time.time()
            response = client.get('/api/tickets', headers=auth_headers)
            end = time.time()
            return {
                'status': response.status_code,
                'time': (end - start) * 1000
            }
        
        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(make_request) for _ in range(num_concurrent)]
            for future in as_completed(futures):
                results.append(future.result())
        
        # All requests should succeed
        success_count = sum(1 for r in results if r['status'] == 200)
        assert success_count == num_concurrent, f"Only {success_count}/{num_concurrent} requests succeeded"
        
        # Average time should be reasonable
        avg_time = statistics.mean([r['time'] for r in results])
        assert avg_time < 1000, f"Average concurrent request time {avg_time}ms exceeds 1000ms"
    
    def test_database_query_performance(self, client, auth_headers):
        """Test database query performance with pagination"""
        def get_paginated():
            return client.get('/api/tickets?page=1&per_page=50', headers=auth_headers)
        
        metrics = self.measure_response_time(get_paginated, iterations=10)
        
        assert metrics['avg'] < 300, f"Paginated query time {metrics['avg']}ms exceeds 300ms"
    
    def test_search_performance(self, client, auth_headers):
        """Test search endpoint performance"""
        def search():
            return client.get('/api/tickets?search=test', headers=auth_headers)
        
        metrics = self.measure_response_time(search, iterations=10)
        
        assert metrics['avg'] < 500, f"Search time {metrics['avg']}ms exceeds 500ms threshold"


class TestMemoryUsage:
    """Tests for memory usage patterns"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from app import create_app
        app = create_app('testing')
        with app.test_client() as client:
            yield client
    
    def test_no_memory_leak_on_repeated_requests(self, client):
        """Test that repeated requests don't cause memory leaks"""
        import tracemalloc
        
        tracemalloc.start()
        
        # Make many requests
        for i in range(100):
            client.get('/api/health')
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Memory usage should be reasonable (less than 50MB growth)
        assert peak < 50 * 1024 * 1024, f"Peak memory usage {peak / 1024 / 1024:.2f}MB exceeds threshold"
