from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app import db
from app.models.customer import Customer
from app.schemas.customer import CustomerSchema, CustomerUpdateSchema
from app.utils.errors import NotFoundError, ForbiddenError, ValidationException
from app.utils.security import get_current_user, role_required

customers_bp = Blueprint('customers', __name__)
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
customer_update_schema = CustomerUpdateSchema()


@customers_bp.route('', methods=['GET'])
@role_required('agent', 'admin')
def get_customers():
    """
    Get all customers (agents/admins only)
    ---
    tags:
      - Customers
    security:
      - Bearer: []
    parameters:
      - in: query
        name: search
        type: string
        description: Search by name or email
      - in: query
        name: page
        type: integer
        default: 1
      - in: query
        name: per_page
        type: integer
        default: 20
    responses:
      200:
        description: List of customers
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    search = request.args.get('search')
    
    query = Customer.query
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                Customer.name.ilike(search_term),
                Customer.email.ilike(search_term)
            )
        )
    
    pagination = query.order_by(Customer.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'status': 'success',
        'data': {
            'customers': customers_schema.dump(pagination.items),
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': pagination.pages,
                'total_items': pagination.total
            }
        }
    }), 200


@customers_bp.route('/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_customer(customer_id):
    """
    Get customer details
    ---
    tags:
      - Customers
    security:
      - Bearer: []
    parameters:
      - in: path
        name: customer_id
        type: integer
        required: true
    responses:
      200:
        description: Customer details
      404:
        description: Customer not found
    """
    user = get_current_user()
    customer = Customer.query.get(customer_id)
    
    if not customer:
        raise NotFoundError('Customer not found')
    
    # Customers can only view their own profile
    if user.role == 'customer' and user.id != customer_id:
        raise ForbiddenError('Access denied')
    
    return jsonify({
        'status': 'success',
        'data': customer_schema.dump(customer)
    }), 200


@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@jwt_required()
def update_customer(customer_id):
    """
    Update customer profile
    ---
    tags:
      - Customers
    security:
      - Bearer: []
    parameters:
      - in: path
        name: customer_id
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            name:
              type: string
            phone:
              type: string
            company:
              type: string
    responses:
      200:
        description: Customer updated
      404:
        description: Customer not found
    """
    user = get_current_user()
    customer = Customer.query.get(customer_id)
    
    if not customer:
        raise NotFoundError('Customer not found')
    
    # Customers can only update their own profile, admins can update any
    if user.role == 'customer' and user.id != customer_id:
        raise ForbiddenError('Access denied')
    if user.role == 'agent':
        raise ForbiddenError('Agents cannot update customer profiles')
    
    try:
        data = customer_update_schema.load(request.json)
    except ValidationError as err:
        raise ValidationException('Validation failed', errors=err.messages)
    
    for key, value in data.items():
        setattr(customer, key, value)
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Customer updated successfully',
        'data': customer_schema.dump(customer)
    }), 200


@customers_bp.route('/<int:customer_id>/tickets', methods=['GET'])
@jwt_required()
def get_customer_tickets(customer_id):
    """
    Get all tickets for a customer
    ---
    tags:
      - Customers
    security:
      - Bearer: []
    parameters:
      - in: path
        name: customer_id
        type: integer
        required: true
      - in: query
        name: status
        type: string
    responses:
      200:
        description: Customer's tickets
    """
    from app.models.ticket import Ticket
    from app.schemas.ticket import TicketSchema
    
    user = get_current_user()
    customer = Customer.query.get(customer_id)
    
    if not customer:
        raise NotFoundError('Customer not found')
    
    # Access control
    if user.role == 'customer' and user.id != customer_id:
        raise ForbiddenError('Access denied')
    
    query = Ticket.query.filter_by(customer_id=customer_id)
    
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)
    
    tickets = query.order_by(Ticket.created_at.desc()).all()
    tickets_schema = TicketSchema(many=True)
    
    return jsonify({
        'status': 'success',
        'data': tickets_schema.dump(tickets)
    }), 200
