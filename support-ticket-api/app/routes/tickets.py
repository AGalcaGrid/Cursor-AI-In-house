from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app import db, cache
from app.models.ticket import Ticket
from app.models.user import User
from app.models.assignment import Assignment
from app.models.comment import Comment
from app.schemas.ticket import (
    TicketSchema, TicketCreateSchema, TicketUpdateSchema,
    TicketStatusSchema, TicketPrioritySchema, TicketAssignSchema
)
from app.schemas.assignment import AssignmentSchema
from app.utils.errors import NotFoundError, ForbiddenError, ValidationError as APIValidationError
from app.services.email_service import EmailService
from app.services.assignment_service import AssignmentService

tickets_bp = Blueprint('tickets', __name__)
ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)
ticket_create_schema = TicketCreateSchema()
ticket_update_schema = TicketUpdateSchema()
ticket_status_schema = TicketStatusSchema()
ticket_priority_schema = TicketPrioritySchema()
ticket_assign_schema = TicketAssignSchema()
assignment_schema = AssignmentSchema()
assignments_schema = AssignmentSchema(many=True)


def get_current_user():
    """Get current authenticated user."""
    user_id = get_jwt_identity()
    return User.query.get(int(user_id))


def invalidate_ticket_cache():
    """Invalidate ticket-related cache."""
    cache.clear()


@tickets_bp.route('', methods=['GET'])
@jwt_required()
def get_tickets():
    """
    Get tickets with filtering and pagination (FR-025, FR-026, FR-027)
    ---
    tags:
      - Tickets
    security:
      - Bearer: []
    parameters:
      - in: query
        name: status
        type: string
        enum: [open, assigned, in_progress, waiting, resolved, closed, reopened]
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
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', current_app.config.get('TICKETS_PER_PAGE', 20), type=int)
    
    # Build query based on user role (FR-033)
    if user.is_admin():
        query = Ticket.query
    elif user.is_agent():
        query = Ticket.query.filter(
            (Ticket.assigned_to_id == user.id) | (Ticket.assigned_to_id.is_(None))
        )
    else:  # Customer
        query = Ticket.query.filter_by(customer_email=user.email)
    
    # Apply filters (FR-025, FR-026)
    status = request.args.get('status')
    priority = request.args.get('priority')
    category = request.args.get('category')
    search = request.args.get('search')
    
    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority=priority)
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(
            (Ticket.subject.ilike(f'%{search}%')) |
            (Ticket.description.ilike(f'%{search}%')) |
            (Ticket.ticket_number.ilike(f'%{search}%'))
        )
    
    pagination = query.order_by(Ticket.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'status': 'success',
        'tickets': tickets_schema.dump(pagination.items),
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200


@tickets_bp.route('', methods=['POST'])
@jwt_required()
def create_ticket():
    """
    Create a new ticket (FR-001, FR-002, FR-004)
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
            - customer_email
          properties:
            subject:
              type: string
              example: Cannot login to my account
            description:
              type: string
              example: I have been trying to login but getting an error message...
            priority:
              type: string
              enum: [low, medium, high, urgent]
              default: medium
            category:
              type: string
              enum: [technical, billing, general, feature_request]
              default: general
            customer_email:
              type: string
              example: customer@example.com
    responses:
      201:
        description: Ticket created successfully
      400:
        description: Validation error
    """
    user = get_current_user()
    
    try:
        data = ticket_create_schema.load(request.json)
    except ValidationError as err:
        raise APIValidationError('Validation failed', errors=err.messages)
    
    # Use authenticated user's email if not provided
    customer_email = data.get('customer_email') or user.email
    
    # Generate unique ticket number (FR-002)
    ticket_number = Ticket.generate_ticket_number()
    
    ticket = Ticket(
        ticket_number=ticket_number,
        subject=data['subject'],
        description=data['description'],
        priority=data.get('priority', 'medium'),
        category=data.get('category', 'general'),
        customer_email=customer_email,
        status='open'  # FR-004
    )
    
    db.session.add(ticket)
    db.session.flush()
    
    # Calculate SLA deadlines (FR-020)
    ticket.calculate_sla_deadlines()
    
    db.session.commit()
    invalidate_ticket_cache()
    
    # Send email notification (FR-003)
    EmailService.notify_ticket_created(ticket)
    
    return jsonify({
        'status': 'success',
        'message': 'Ticket created successfully',
        'ticket': ticket_schema.dump(ticket)
    }), 201


@tickets_bp.route('/<int:ticket_id>', methods=['GET'])
@jwt_required()
def get_ticket(ticket_id):
    """
    Get ticket details
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
      403:
        description: Access denied
      404:
        description: Ticket not found
    """
    user = get_current_user()
    ticket = Ticket.query.get(ticket_id)
    
    if not ticket:
        raise NotFoundError('Ticket not found')
    
    if not user.can_view_ticket(ticket):
        raise ForbiddenError('Access denied to this ticket')
    
    return jsonify({
        'status': 'success',
        'ticket': ticket_schema.dump(ticket)
    }), 200


@tickets_bp.route('/<int:ticket_id>', methods=['PUT'])
@jwt_required()
def update_ticket(ticket_id):
    """
    Update ticket details
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
            category:
              type: string
    responses:
      200:
        description: Ticket updated
      403:
        description: Access denied
      404:
        description: Ticket not found
    """
    user = get_current_user()
    ticket = Ticket.query.get(ticket_id)
    
    if not ticket:
        raise NotFoundError('Ticket not found')
    
    if not user.can_modify_ticket(ticket):
        raise ForbiddenError('You do not have permission to modify this ticket')
    
    try:
        data = ticket_update_schema.load(request.json)
    except ValidationError as err:
        raise APIValidationError('Validation failed', errors=err.messages)
    
    for key, value in data.items():
        setattr(ticket, key, value)
    
    db.session.commit()
    invalidate_ticket_cache()
    
    return jsonify({
        'status': 'success',
        'message': 'Ticket updated successfully',
        'ticket': ticket_schema.dump(ticket)
    }), 200


@tickets_bp.route('/<int:ticket_id>', methods=['DELETE'])
@jwt_required()
def delete_ticket(ticket_id):
    """
    Delete ticket (admin only)
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
      403:
        description: Admin access required
      404:
        description: Ticket not found
    """
    user = get_current_user()
    
    if not user.is_admin():
        raise ForbiddenError('Admin access required')
    
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        raise NotFoundError('Ticket not found')
    
    db.session.delete(ticket)
    db.session.commit()
    invalidate_ticket_cache()
    
    return jsonify({
        'status': 'success',
        'message': 'Ticket deleted successfully'
    }), 200


@tickets_bp.route('/<int:ticket_id>/status', methods=['PUT'])
@jwt_required()
def update_status(ticket_id):
    """
    Update ticket status (FR-011, FR-012, FR-013)
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
              enum: [open, assigned, in_progress, waiting, resolved, closed, reopened]
            reason:
              type: string
    responses:
      200:
        description: Status updated
      400:
        description: Invalid status transition
      403:
        description: Access denied
    """
    user = get_current_user()
    ticket = Ticket.query.get(ticket_id)
    
    if not ticket:
        raise NotFoundError('Ticket not found')
    
    # Customers can only close or reopen their own tickets
    if user.is_customer():
        if ticket.customer_email != user.email:
            raise ForbiddenError('Access denied')
        allowed_statuses = ['closed', 'reopened']
        try:
            data = ticket_status_schema.load(request.json)
        except ValidationError as err:
            raise APIValidationError('Validation failed', errors=err.messages)
        if data['status'] not in allowed_statuses:
            raise ForbiddenError('Customers can only close or reopen tickets')
    else:
        if not user.can_modify_ticket(ticket):
            raise ForbiddenError('Access denied')
        try:
            data = ticket_status_schema.load(request.json)
        except ValidationError as err:
            raise APIValidationError('Validation failed', errors=err.messages)
    
    new_status = data['status']
    
    # Validate transition (FR-012)
    if not ticket.can_transition_to(new_status):
        raise APIValidationError(
            f"Cannot transition from '{ticket.status}' to '{new_status}'",
            errors={'status': [f"Invalid transition from {ticket.status}"]}
        )
    
    old_status = ticket.update_status(new_status, user.id)
    db.session.commit()
    invalidate_ticket_cache()
    
    # Send email notification (FR-014)
    recipients = [ticket.customer_email]
    if ticket.assigned_agent and ticket.assigned_agent.email != user.email:
        recipients.append(ticket.assigned_agent.email)
    EmailService.notify_status_changed(ticket, old_status, new_status, recipients)
    
    return jsonify({
        'status': 'success',
        'message': f'Ticket status updated from {old_status} to {new_status}',
        'ticket': ticket_schema.dump(ticket)
    }), 200


@tickets_bp.route('/<int:ticket_id>/priority', methods=['PUT'])
@jwt_required()
def update_priority(ticket_id):
    """
    Update ticket priority (FR-023, FR-024)
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
    responses:
      200:
        description: Priority updated
      403:
        description: Agents and admins only
    """
    user = get_current_user()
    ticket = Ticket.query.get(ticket_id)
    
    if not ticket:
        raise NotFoundError('Ticket not found')
    
    # Only agents and admins can change priority (FR-023)
    if user.is_customer():
        raise ForbiddenError('Only agents and admins can change priority')
    
    if not user.can_modify_ticket(ticket) and not user.is_admin():
        raise ForbiddenError('Access denied')
    
    try:
        data = ticket_priority_schema.load(request.json)
    except ValidationError as err:
        raise APIValidationError('Validation failed', errors=err.messages)
    
    old_priority = ticket.priority
    ticket.priority = data['priority']
    
    # Recalculate SLA deadlines
    ticket.calculate_sla_deadlines()
    
    # Create internal comment with reason (FR-024)
    reason_comment = Comment(
        ticket_id=ticket.id,
        user_id=user.id,
        content=f"Priority changed from {old_priority.upper()} to {data['priority'].upper()}. Reason: {data['reason']}",
        is_internal=True
    )
    db.session.add(reason_comment)
    
    db.session.commit()
    invalidate_ticket_cache()
    
    return jsonify({
        'status': 'success',
        'message': f'Priority updated from {old_priority} to {data["priority"]}',
        'ticket': ticket_schema.dump(ticket)
    }), 200


@tickets_bp.route('/<int:ticket_id>/assign', methods=['POST'])
@jwt_required()
def assign_ticket(ticket_id):
    """
    Assign ticket to agent (FR-005, FR-008, FR-010)
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
      403:
        description: Admin access required
      404:
        description: Ticket or agent not found
    """
    user = get_current_user()
    
    # Only admins can assign tickets (FR-005)
    if not user.is_admin():
        raise ForbiddenError('Admin access required to assign tickets')
    
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        raise NotFoundError('Ticket not found')
    
    try:
        data = ticket_assign_schema.load(request.json)
    except ValidationError as err:
        raise APIValidationError('Validation failed', errors=err.messages)
    
    agent = User.query.get(data['agent_id'])
    if not agent:
        raise NotFoundError('Agent not found')
    
    if not agent.is_agent() and not agent.is_admin():
        raise APIValidationError('User is not an agent')
    
    # Create assignment record (FR-010)
    assignment = Assignment(
        ticket_id=ticket.id,
        assigned_to_id=agent.id,
        assigned_by_id=user.id
    )
    db.session.add(assignment)
    
    # Update ticket
    ticket.assigned_to_id = agent.id
    if ticket.status == 'open':
        ticket.status = 'assigned'  # FR-008
    
    db.session.commit()
    invalidate_ticket_cache()
    
    # Send email notification to agent (FR-007)
    EmailService.notify_ticket_assigned(ticket, agent)
    
    return jsonify({
        'status': 'success',
        'message': f'Ticket assigned to {agent.name}',
        'ticket': ticket_schema.dump(ticket),
        'assignment': assignment_schema.dump(assignment)
    }), 200


@tickets_bp.route('/<int:ticket_id>/history', methods=['GET'])
@jwt_required()
def get_ticket_history(ticket_id):
    """
    Get ticket assignment history (FR-010)
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
        description: Assignment history
      404:
        description: Ticket not found
    """
    user = get_current_user()
    ticket = Ticket.query.get(ticket_id)
    
    if not ticket:
        raise NotFoundError('Ticket not found')
    
    if not user.can_view_ticket(ticket):
        raise ForbiddenError('Access denied')
    
    assignments = ticket.assignments.order_by(Assignment.assigned_at.desc()).all()
    
    return jsonify({
        'status': 'success',
        'ticket_number': ticket.ticket_number,
        'history': assignments_schema.dump(assignments)
    }), 200


@tickets_bp.route('/<int:ticket_id>/auto-assign', methods=['POST'])
@jwt_required()
def auto_assign_ticket(ticket_id):
    """
    Auto-assign ticket to best available agent (FR-006)
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
        description: Ticket auto-assigned
      400:
        description: No available agents
      403:
        description: Admin access required
      404:
        description: Ticket not found
    """
    user = get_current_user()
    
    if not user.is_admin():
        raise ForbiddenError('Admin access required')
    
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        raise NotFoundError('Ticket not found')
    
    agent = AssignmentService.auto_assign_ticket(ticket, user)
    
    if not agent:
        raise APIValidationError('No available agents to assign ticket')
    
    invalidate_ticket_cache()
    
    return jsonify({
        'status': 'success',
        'message': f'Ticket auto-assigned to {agent.name}',
        'ticket': ticket_schema.dump(ticket)
    }), 200
