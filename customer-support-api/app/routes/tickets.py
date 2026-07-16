from datetime import datetime
import csv
import io
from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app import db, limiter, cache
from sqlalchemy.orm import joinedload
from app.models.ticket import Ticket, TicketStatusHistory, TicketAssignment, PriorityChangeHistory
from app.models.agent import Agent
from app.schemas.ticket import (
    TicketSchema, TicketCreateSchema, TicketUpdateSchema,
    TicketAssignSchema, TicketStatusUpdateSchema, TicketFilterSchema,
    TicketPriorityUpdateSchema, TicketHistorySchema
)
from app.utils.errors import (
    NotFoundError, ForbiddenError, ValidationException
)
from app.utils.security import get_current_user, role_required

tickets_bp = Blueprint('tickets', __name__)
ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)
ticket_create_schema = TicketCreateSchema()
ticket_update_schema = TicketUpdateSchema()
ticket_assign_schema = TicketAssignSchema()
ticket_status_schema = TicketStatusUpdateSchema()
ticket_filter_schema = TicketFilterSchema()
ticket_priority_schema = TicketPriorityUpdateSchema()
ticket_history_schema = TicketHistorySchema(many=True)


def get_ticket_or_404(ticket_id, user=None):
    """Get ticket by ID with optional access check and eager loading."""
    ticket = Ticket.query.options(
        joinedload(Ticket.customer),
        joinedload(Ticket.assigned_agent)
    ).get(ticket_id)
    
    if not ticket:
        raise NotFoundError(f'Ticket {ticket_id} not found')
    
    if user:
        # Customers can only see their own tickets
        if user.role == 'customer' and ticket.customer_id != user.id:
            raise ForbiddenError('Access denied to this ticket')
    
    return ticket


@tickets_bp.route('', methods=['GET'])
@jwt_required()
def get_tickets():
    """
    Get tickets with filtering and pagination
    ---
    tags:
      - Tickets
    security:
      - Bearer: []
    parameters:
      - in: query
        name: status
        type: string
        enum: [open, assigned, in_progress, waiting, resolved, closed]
      - in: query
        name: priority
        type: string
        enum: [low, medium, high, urgent]
      - in: query
        name: category
        type: string
      - in: query
        name: search
        type: string
        description: Search in subject and description
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
        description: List of tickets
    """
    user = get_current_user()
    
    try:
        filters = ticket_filter_schema.load(request.args)
    except ValidationError as err:
        raise ValidationException('Invalid filters', errors=err.messages)
    
    query = Ticket.query
    
    # Role-based filtering
    if user.role == 'customer':
        query = query.filter_by(customer_id=user.id)
    elif user.role == 'agent':
        # Agents see assigned tickets or unassigned
        query = query.filter(
            db.or_(
                Ticket.assigned_to_id == user.id,
                Ticket.assigned_to_id.is_(None)
            )
        )
    # Admins see all tickets
    
    # Apply filters per PRD FR-025, FR-026
    if filters.get('status'):
        query = query.filter_by(status=filters['status'])
    if filters.get('statuses'):  # Multiple status selection
        query = query.filter(Ticket.status.in_(filters['statuses']))
    if filters.get('priority'):
        query = query.filter_by(priority=filters['priority'])
    if filters.get('category'):
        query = query.filter_by(category=filters['category'])
    if filters.get('assigned_to_id'):
        query = query.filter_by(assigned_to_id=filters['assigned_to_id'])
    if filters.get('unassigned'):
        query = query.filter(Ticket.assigned_to_id.is_(None))
    if filters.get('customer_id') and user.role in ['agent', 'admin']:
        query = query.filter_by(customer_id=filters['customer_id'])
    if filters.get('ticket_number'):
        query = query.filter(Ticket.ticket_number.ilike(f"%{filters['ticket_number']}%"))
    if filters.get('customer_email') and user.role in ['agent', 'admin']:
        from app.models.customer import Customer
        query = query.join(Customer).filter(Customer.email.ilike(f"%{filters['customer_email']}%"))
    
    # Date range filters
    if filters.get('created_from'):
        query = query.filter(Ticket.created_at >= filters['created_from'])
    if filters.get('created_to'):
        query = query.filter(Ticket.created_at <= filters['created_to'])
    if filters.get('updated_from'):
        query = query.filter(Ticket.updated_at >= filters['updated_from'])
    if filters.get('updated_to'):
        query = query.filter(Ticket.updated_at <= filters['updated_to'])
    if filters.get('resolved_from'):
        query = query.filter(Ticket.resolved_at >= filters['resolved_from'])
    if filters.get('resolved_to'):
        query = query.filter(Ticket.resolved_at <= filters['resolved_to'])
    
    if filters.get('search'):
        search_term = f"%{filters['search']}%"
        query = query.filter(
            db.or_(
                Ticket.subject.ilike(search_term),
                Ticket.description.ilike(search_term),
                Ticket.ticket_number.ilike(search_term)
            )
        )
    
    # Pagination
    page = filters.get('page', 1)
    per_page = filters.get('per_page', 20)
    
    pagination = query.order_by(Ticket.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'status': 'success',
        'data': {
            'tickets': tickets_schema.dump(pagination.items),
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': pagination.pages,
                'total_items': pagination.total
            }
        }
    }), 200


@tickets_bp.route('/<int:ticket_id>', methods=['GET'])
@jwt_required()
def get_ticket(ticket_id):
    """
    Get a specific ticket
    ---
    tags:
      - Tickets
    security:
      - Bearer: []
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
    responses:
      200:
        description: Ticket details
      404:
        description: Ticket not found
    """
    user = get_current_user()
    ticket = get_ticket_or_404(ticket_id, user)
    
    return jsonify({
        'status': 'success',
        'data': ticket_schema.dump(ticket)
    }), 200


@tickets_bp.route('', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def create_ticket():
    """
    Create a new support ticket
    ---
    tags:
      - Tickets
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - subject
            - description
          properties:
            subject:
              type: string
              example: Cannot login to my account
              minLength: 5
              maxLength: 200
            description:
              type: string
              example: I've been trying to login but keep getting an error message...
              minLength: 20
            priority:
              type: string
              enum: [low, medium, high, urgent]
              default: medium
            category:
              type: string
              enum: [technical, billing, general, feature_request, bug_report]
    responses:
      201:
        description: Ticket created
      400:
        description: Validation error
    """
    user = get_current_user()
    
    # Only customers can create tickets (or agents on behalf of customers)
    if user.role not in ['customer', 'agent', 'admin']:
        raise ForbiddenError('Only customers can create tickets')
    
    try:
        data = ticket_create_schema.load(request.json)
    except ValidationError as err:
        raise ValidationException('Validation failed', errors=err.messages)
    
    ticket = Ticket(
        ticket_number=Ticket.generate_ticket_number(),
        subject=data['subject'],
        description=data['description'],
        priority=data.get('priority', 'medium'),
        category=data.get('category'),
        customer_id=user.id if user.role == 'customer' else request.json.get('customer_id', user.id)
    )
    
    db.session.add(ticket)
    db.session.flush()  # Get the ID before calculating SLA
    
    # Calculate SLA deadlines per PRD FR-020
    ticket.calculate_sla_deadlines()
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Ticket created successfully',
        'data': ticket_schema.dump(ticket)
    }), 201


@tickets_bp.route('/<int:ticket_id>', methods=['PUT'])
@jwt_required()
def update_ticket(ticket_id):
    """
    Update a ticket
    ---
    tags:
      - Tickets
    security:
      - Bearer: []
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            subject:
              type: string
            description:
              type: string
            priority:
              type: string
              enum: [low, medium, high, urgent]
            category:
              type: string
    responses:
      200:
        description: Ticket updated
      404:
        description: Ticket not found
    """
    user = get_current_user()
    ticket = get_ticket_or_404(ticket_id, user)
    
    # Customers can only update open tickets
    if user.role == 'customer' and ticket.status not in ['open', 'waiting']:
        raise ForbiddenError('Cannot update ticket in current status')
    
    try:
        data = ticket_update_schema.load(request.json)
    except ValidationError as err:
        raise ValidationException('Validation failed', errors=err.messages)
    
    for key, value in data.items():
        setattr(ticket, key, value)
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Ticket updated successfully',
        'data': ticket_schema.dump(ticket)
    }), 200


@tickets_bp.route('/<int:ticket_id>/assign', methods=['POST'])
@role_required('agent', 'admin')
def assign_ticket(ticket_id):
    """
    Assign ticket to an agent
    ---
    tags:
      - Tickets
    security:
      - Bearer: []
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - agent_id
          properties:
            agent_id:
              type: integer
    responses:
      200:
        description: Ticket assigned
      400:
        description: Agent cannot accept more tickets
      404:
        description: Ticket or agent not found
    """
    user = get_current_user()
    ticket = get_ticket_or_404(ticket_id)
    
    try:
        data = ticket_assign_schema.load(request.json)
    except ValidationError as err:
        raise ValidationException('Validation failed', errors=err.messages)
    
    agent = Agent.query.get(data['agent_id'])
    if not agent:
        raise NotFoundError('Agent not found')
    
    if not agent.can_accept_tickets:
        raise ValidationException('Agent cannot accept more tickets')
    
    ticket.assigned_to_id = agent.id
    ticket.update_status('assigned', user.id)
    
    # Track assignment history per PRD FR-010
    assignment = TicketAssignment(
        ticket_id=ticket.id,
        assigned_to_id=agent.id,
        assigned_by_id=user.id
    )
    db.session.add(assignment)
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': f'Ticket assigned to {agent.name}',
        'data': ticket_schema.dump(ticket)
    }), 200


@tickets_bp.route('/<int:ticket_id>/status', methods=['PUT'])
@jwt_required()
def update_ticket_status(ticket_id):
    """
    Update ticket status
    ---
    tags:
      - Tickets
    security:
      - Bearer: []
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - status
          properties:
            status:
              type: string
              enum: [open, assigned, in_progress, waiting, resolved, closed]
            reason:
              type: string
    responses:
      200:
        description: Status updated
      400:
        description: Invalid status transition
    """
    user = get_current_user()
    ticket = get_ticket_or_404(ticket_id, user)
    
    try:
        data = ticket_status_schema.load(request.json)
    except ValidationError as err:
        raise ValidationException('Validation failed', errors=err.messages)
    
    new_status = data['status']
    
    # Validate transition
    if not ticket.can_transition_to(new_status):
        raise ValidationException(
            f"Cannot transition from '{ticket.status}' to '{new_status}'",
            errors={'status': [f"Invalid transition from {ticket.status}"]}
        )
    
    # Role-based restrictions
    if user.role == 'customer':
        allowed_statuses = ['closed']  # Customers can only close
        if new_status not in allowed_statuses:
            raise ForbiddenError('Customers can only close tickets')
    
    ticket.update_status(new_status, user.id)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': f'Ticket status updated to {new_status}',
        'data': ticket_schema.dump(ticket)
    }), 200


@tickets_bp.route('/<int:ticket_id>/priority', methods=['PUT'])
@role_required('agent', 'admin')
def update_ticket_priority(ticket_id):
    """
    Update ticket priority (requires reason per PRD FR-024)
    ---
    tags:
      - Tickets
    security:
      - Bearer: []
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - priority
            - reason
          properties:
            priority:
              type: string
              enum: [low, medium, high, urgent]
            reason:
              type: string
              description: Required reason for priority change
    responses:
      200:
        description: Priority updated
      400:
        description: Validation error
    """
    user = get_current_user()
    ticket = get_ticket_or_404(ticket_id)
    
    try:
        data = ticket_priority_schema.load(request.json)
    except ValidationError as err:
        raise ValidationException('Validation failed', errors=err.messages)
    
    old_priority = ticket.priority
    new_priority = data['priority']
    
    if old_priority == new_priority:
        return jsonify({
            'status': 'success',
            'message': 'Priority unchanged',
            'data': ticket_schema.dump(ticket)
        }), 200
    
    # Track priority change history per PRD FR-024
    priority_change = PriorityChangeHistory(
        ticket_id=ticket.id,
        old_priority=old_priority,
        new_priority=new_priority,
        reason=data['reason'],
        changed_by_id=user.id
    )
    db.session.add(priority_change)
    
    ticket.priority = new_priority
    # Recalculate SLA deadlines based on new priority
    ticket.calculate_sla_deadlines()
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': f'Priority updated from {old_priority} to {new_priority}',
        'data': ticket_schema.dump(ticket)
    }), 200


@tickets_bp.route('/<int:ticket_id>/history', methods=['GET'])
@jwt_required()
def get_ticket_history(ticket_id):
    """
    Get ticket history (status changes, assignments, priority changes)
    ---
    tags:
      - Tickets
    security:
      - Bearer: []
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
    responses:
      200:
        description: Ticket history
      404:
        description: Ticket not found
    """
    user = get_current_user()
    ticket = get_ticket_or_404(ticket_id, user)
    
    # Get status history
    status_history = TicketStatusHistory.query.filter_by(
        ticket_id=ticket_id
    ).order_by(TicketStatusHistory.changed_at.desc()).all()
    
    # Get assignment history
    assignment_history = TicketAssignment.query.filter_by(
        ticket_id=ticket_id
    ).order_by(TicketAssignment.assigned_at.desc()).all()
    
    # Get priority change history
    priority_history = PriorityChangeHistory.query.filter_by(
        ticket_id=ticket_id
    ).order_by(PriorityChangeHistory.changed_at.desc()).all()
    
    return jsonify({
        'status': 'success',
        'data': {
            'status_changes': [{
                'id': h.id,
                'old_status': h.old_status,
                'new_status': h.new_status,
                'reason': h.reason,
                'changed_at': h.changed_at.isoformat(),
                'changed_by': {'id': h.changed_by.id, 'email': h.changed_by.email} if h.changed_by else None
            } for h in status_history],
            'assignments': [{
                'id': a.id,
                'assigned_to': {'id': a.assigned_to.id, 'name': a.assigned_to.name} if a.assigned_to else None,
                'assigned_by': {'id': a.assigned_by.id, 'email': a.assigned_by.email} if a.assigned_by else None,
                'assigned_at': a.assigned_at.isoformat()
            } for a in assignment_history],
            'priority_changes': [{
                'id': p.id,
                'old_priority': p.old_priority,
                'new_priority': p.new_priority,
                'reason': p.reason,
                'changed_at': p.changed_at.isoformat(),
                'changed_by': {'id': p.changed_by.id, 'email': p.changed_by.email} if p.changed_by else None
            } for p in priority_history]
        }
    }), 200


@tickets_bp.route('/export', methods=['GET'])
@role_required('agent', 'admin')
def export_tickets_csv():
    """
    Export tickets to CSV per PRD FR-028
    ---
    tags:
      - Tickets
    security:
      - Bearer: []
    parameters:
      - in: query
        name: status
        type: string
      - in: query
        name: priority
        type: string
    responses:
      200:
        description: CSV file download
    """
    user = get_current_user()
    
    query = Ticket.query
    
    # Apply basic filters
    status = request.args.get('status')
    priority = request.args.get('priority')
    
    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority=priority)
    
    tickets = query.order_by(Ticket.created_at.desc()).all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header row
    writer.writerow([
        'Ticket Number', 'Subject', 'Status', 'Priority', 'Category',
        'Customer ID', 'Assigned To', 'Created At', 'Updated At',
        'Resolved At', 'SLA Response Due', 'SLA Resolution Due',
        'Response Breached', 'Resolution Breached'
    ])
    
    # Data rows
    for ticket in tickets:
        writer.writerow([
            ticket.ticket_number,
            ticket.subject,
            ticket.status,
            ticket.priority,
            ticket.category or '',
            ticket.customer_id,
            ticket.assigned_to_id or '',
            ticket.created_at.isoformat() if ticket.created_at else '',
            ticket.updated_at.isoformat() if ticket.updated_at else '',
            ticket.resolved_at.isoformat() if ticket.resolved_at else '',
            ticket.sla_response_due_at.isoformat() if ticket.sla_response_due_at else '',
            ticket.sla_resolution_due_at.isoformat() if ticket.sla_resolution_due_at else '',
            'Yes' if ticket.sla_response_breached else 'No',
            'Yes' if ticket.sla_resolution_breached else 'No'
        ])
    
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=tickets_export_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'}
    )


@tickets_bp.route('/<int:ticket_id>', methods=['DELETE'])
@role_required('admin')
def delete_ticket(ticket_id):
    """
    Delete a ticket (admin only)
    ---
    tags:
      - Tickets
    security:
      - Bearer: []
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
    responses:
      200:
        description: Ticket deleted
      404:
        description: Ticket not found
    """
    ticket = get_ticket_or_404(ticket_id)
    
    db.session.delete(ticket)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Ticket deleted successfully'
    }), 200
