import pytest
from tests.conftest import auth_header


class TestCustomerList:
    """Tests for listing customers."""
    
    def test_list_customers_agent(self, client, agent_token, customer):
        """Test agent can list customers."""
        response = client.get('/api/customers', headers=auth_header(agent_token))
        assert response.status_code == 200
        assert response.json['status'] == 'success'
        assert 'customers' in response.json['data']
    
    def test_list_customers_admin(self, client, admin_token, customer):
        """Test admin can list customers."""
        response = client.get('/api/customers', headers=auth_header(admin_token))
        assert response.status_code == 200
        assert len(response.json['data']['customers']) >= 1
    
    def test_list_customers_forbidden_customer(self, client, customer_token):
        """Test customer cannot list all customers."""
        response = client.get('/api/customers', headers=auth_header(customer_token))
        assert response.status_code == 403
    
    def test_list_customers_search(self, client, agent_token, customer):
        """Test searching customers."""
        response = client.get('/api/customers?search=Test',
            headers=auth_header(agent_token))
        assert response.status_code == 200


class TestCustomerGet:
    """Tests for getting customer details."""
    
    def test_get_customer_self(self, client, customer_token, customer):
        """Test customer can get their own details."""
        response = client.get(f'/api/customers/{customer.id}',
            headers=auth_header(customer_token))
        assert response.status_code == 200
        assert response.json['data']['email'] == 'customer@test.com'
    
    def test_get_customer_agent(self, client, agent_token, customer):
        """Test agent can get customer details."""
        response = client.get(f'/api/customers/{customer.id}',
            headers=auth_header(agent_token))
        assert response.status_code == 200
    
    def test_get_customer_not_found(self, client, agent_token):
        """Test getting non-existent customer."""
        response = client.get('/api/customers/99999',
            headers=auth_header(agent_token))
        assert response.status_code == 404
    
    def test_get_customer_forbidden_other(self, client, app, _db, customer_token):
        """Test customer cannot get another customer's details."""
        from app.models.customer import Customer
        
        # Create another customer
        other = Customer(
            name='Other Customer',
            email='other@test.com',
            role='customer'
        )
        other.set_password('TestPass123')
        _db.session.add(other)
        _db.session.commit()
        
        response = client.get(f'/api/customers/{other.id}',
            headers=auth_header(customer_token))
        assert response.status_code == 403


class TestCustomerUpdate:
    """Tests for updating customer details."""
    
    def test_update_customer_self(self, client, customer_token, customer):
        """Test customer can update their own details."""
        response = client.put(f'/api/customers/{customer.id}',
            headers=auth_header(customer_token),
            json={'name': 'Updated Name', 'phone': '9876543210'})
        assert response.status_code == 200
        assert response.json['data']['name'] == 'Updated Name'
    
    def test_update_customer_admin(self, client, admin_token, customer):
        """Test admin can update customer details."""
        response = client.put(f'/api/customers/{customer.id}',
            headers=auth_header(admin_token),
            json={'company': 'New Company'})
        assert response.status_code == 200
    
    def test_update_customer_forbidden_agent(self, client, agent_token, customer):
        """Test agent cannot update customer details."""
        response = client.put(f'/api/customers/{customer.id}',
            headers=auth_header(agent_token),
            json={'name': 'Hacked Name'})
        assert response.status_code == 403


class TestCustomerTickets:
    """Tests for customer tickets endpoint."""
    
    def test_get_customer_tickets_self(self, client, customer_token, customer, ticket):
        """Test customer can get their own tickets."""
        response = client.get(f'/api/customers/{customer.id}/tickets',
            headers=auth_header(customer_token))
        assert response.status_code == 200
        assert len(response.json['data']) >= 1
    
    def test_get_customer_tickets_agent(self, client, agent_token, customer, ticket):
        """Test agent can get customer's tickets."""
        response = client.get(f'/api/customers/{customer.id}/tickets',
            headers=auth_header(agent_token))
        assert response.status_code == 200
    
    def test_get_customer_tickets_with_filter(self, client, customer_token, customer, ticket):
        """Test filtering customer tickets by status."""
        response = client.get(f'/api/customers/{customer.id}/tickets?status=open',
            headers=auth_header(customer_token))
        assert response.status_code == 200
