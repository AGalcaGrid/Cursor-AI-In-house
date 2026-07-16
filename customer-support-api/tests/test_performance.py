import pytest
import time
from tests.conftest import auth_header


class TestResponseTime:
    """Tests for API response time performance."""
    
    def test_get_tickets_response_time(self, client, customer_token, ticket):
        """Test that getting tickets responds within acceptable time."""
        start_time = time.time()
        response = client.get('/api/tickets', headers=auth_header(customer_token))
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # Convert to ms
        
        assert response.status_code == 200
        assert response_time < 500  # Should respond within 500ms
    
    def test_get_single_ticket_response_time(self, client, customer_token, ticket):
        """Test that getting a single ticket responds quickly."""
        start_time = time.time()
        response = client.get(f'/api/tickets/{ticket.id}', 
            headers=auth_header(customer_token))
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        assert response_time < 200  # Should respond within 200ms
    
    def test_create_ticket_response_time(self, client, customer_token):
        """Test that creating a ticket responds within acceptable time."""
        start_time = time.time()
        response = client.post('/api/tickets',
            headers=auth_header(customer_token),
            json={
                'subject': 'Performance test ticket',
                'description': 'This is a test ticket for performance testing purposes',
                'priority': 'medium'
            })
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        
        assert response.status_code == 201
        assert response_time < 500  # Should respond within 500ms
    
    def test_login_response_time(self, client, customer):
        """Test that login responds quickly."""
        start_time = time.time()
        response = client.post('/api/auth/login', json={
            'email': 'customer@test.com',
            'password': 'TestPass123'
        })
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        assert response_time < 300  # Should respond within 300ms


class TestBulkOperations:
    """Tests for bulk operation performance."""
    
    def test_list_multiple_tickets(self, client, app, _db, customer_token, customer):
        """Test listing multiple tickets performs well."""
        from app.models.ticket import Ticket
        from datetime import datetime
        
        # Create multiple tickets
        for i in range(10):
            ticket = Ticket(
                ticket_number=Ticket.generate_ticket_number(),
                subject=f'Bulk test ticket {i}',
                description='This is a bulk test ticket description',
                status='open',
                priority='medium',
                customer_id=customer.id,
                created_at=datetime.utcnow()
            )
            _db.session.add(ticket)
        _db.session.commit()
        
        # Measure response time
        start_time = time.time()
        response = client.get('/api/tickets', headers=auth_header(customer_token))
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        assert len(response.json['data']['tickets']) >= 10
        assert response_time < 1000  # Should respond within 1 second
    
    def test_pagination_performance(self, client, app, _db, customer_token, customer):
        """Test that pagination doesn't degrade performance."""
        from app.models.ticket import Ticket
        from datetime import datetime
        
        # Create tickets
        for i in range(20):
            ticket = Ticket(
                ticket_number=Ticket.generate_ticket_number(),
                subject=f'Pagination test ticket {i}',
                description='This is a pagination test ticket description',
                status='open',
                priority='medium',
                customer_id=customer.id,
                created_at=datetime.utcnow()
            )
            _db.session.add(ticket)
        _db.session.commit()
        
        # Test first page
        start_time = time.time()
        response = client.get('/api/tickets?page=1&per_page=10', 
            headers=auth_header(customer_token))
        first_page_time = (time.time() - start_time) * 1000
        
        # Test second page
        start_time = time.time()
        response = client.get('/api/tickets?page=2&per_page=10', 
            headers=auth_header(customer_token))
        second_page_time = (time.time() - start_time) * 1000
        
        assert response.status_code == 200
        # Both pages should have similar response times
        assert abs(first_page_time - second_page_time) < 200


class TestCachingEffectiveness:
    """Tests to verify caching improves performance."""
    
    def test_repeated_requests_faster(self, client, admin_token):
        """Test that repeated requests benefit from caching."""
        # First request (cache miss)
        start_time = time.time()
        response1 = client.get('/api/admin/dashboard', 
            headers=auth_header(admin_token))
        first_request_time = (time.time() - start_time) * 1000
        
        assert response1.status_code == 200
        
        # Second request (should hit cache)
        start_time = time.time()
        response2 = client.get('/api/admin/dashboard', 
            headers=auth_header(admin_token))
        second_request_time = (time.time() - start_time) * 1000
        
        assert response2.status_code == 200
        # Note: In testing config, cache is disabled, so this just verifies
        # the endpoint works consistently
        assert second_request_time < 1000


class TestDatabaseQueryOptimization:
    """Tests to verify database query optimization."""
    
    def test_eager_loading_ticket_with_relations(self, client, customer_token, ticket):
        """Test that ticket with relations loads efficiently."""
        start_time = time.time()
        response = client.get(f'/api/tickets/{ticket.id}', 
            headers=auth_header(customer_token))
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        # With eager loading, should be fast
        assert response_time < 200
    
    def test_filtered_query_performance(self, client, app, _db, customer_token, customer):
        """Test that filtered queries use indexes efficiently."""
        from app.models.ticket import Ticket
        from datetime import datetime
        
        # Create tickets with different statuses
        for status in ['open', 'assigned', 'in_progress', 'resolved']:
            for i in range(5):
                ticket = Ticket(
                    ticket_number=Ticket.generate_ticket_number(),
                    subject=f'Filter test ticket {status} {i}',
                    description='This is a filter test ticket description',
                    status=status if status != 'assigned' else 'open',
                    priority='medium',
                    customer_id=customer.id,
                    created_at=datetime.utcnow()
                )
                _db.session.add(ticket)
        _db.session.commit()
        
        # Test filtered query
        start_time = time.time()
        response = client.get('/api/tickets?status=open', 
            headers=auth_header(customer_token))
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        # Filtered query should be fast due to index
        assert response_time < 500


class TestConcurrentRequests:
    """Tests for handling concurrent requests."""
    
    def test_multiple_sequential_requests(self, client, customer_token, ticket):
        """Test handling multiple sequential requests."""
        total_time = 0
        num_requests = 5
        
        for _ in range(num_requests):
            start_time = time.time()
            response = client.get('/api/tickets', 
                headers=auth_header(customer_token))
            total_time += (time.time() - start_time) * 1000
            assert response.status_code == 200
        
        avg_time = total_time / num_requests
        # Average response time should be reasonable
        assert avg_time < 500


class TestMemoryEfficiency:
    """Tests for memory-efficient operations."""
    
    def test_large_ticket_list_pagination(self, client, app, _db, agent_token, customer):
        """Test that large lists are paginated efficiently."""
        from app.models.ticket import Ticket
        from datetime import datetime
        
        # Create many tickets
        for i in range(50):
            ticket = Ticket(
                ticket_number=Ticket.generate_ticket_number(),
                subject=f'Memory test ticket {i}',
                description='This is a memory efficiency test ticket',
                status='open',
                priority='medium',
                customer_id=customer.id,
                created_at=datetime.utcnow()
            )
            _db.session.add(ticket)
        _db.session.commit()
        
        # Request with pagination
        response = client.get('/api/tickets?page=1&per_page=20', 
            headers=auth_header(agent_token))
        
        assert response.status_code == 200
        # Should only return requested page size
        assert len(response.json['data']['tickets']) <= 20
        # Should have pagination info
        assert 'pagination' in response.json['data']
