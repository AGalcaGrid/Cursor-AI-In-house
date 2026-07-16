from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app import db
from app.models.agent import Agent
from app.models.ticket import Ticket
from app.schemas.agent import AgentSchema, AgentCreateSchema, AgentUpdateSchema
from app.schemas.ticket import TicketSchema
from app.utils.errors import NotFoundError, ConflictError, ValidationException
from app.utils.security import get_current_user, role_required

agents_bp = Blueprint('agents', __name__)
agent_schema = AgentSchema()
agents_schema = AgentSchema(many=True)
agent_create_schema = AgentCreateSchema()
agent_update_schema = AgentUpdateSchema()


@agents_bp.route('', methods=['GET'])
@role_required('agent', 'admin')
def get_agents():
    """
    Get all agents
    ---
    tags:
      - Agents
    security:
      - Bearer: []
    parameters:
      - in: query
        name: available
        type: boolean
        description: Filter by availability
      - in: query
        name: department
        type: string
    responses:
      200:
        description: List of agents
    """
    query = Agent.query
    
    available = request.args.get('available')
    if available is not None:
        query = query.filter_by(is_available=available.lower() == 'true')
    
    department = request.args.get('department')
    if department:
        query = query.filter_by(department=department)
    
    agents = query.order_by(Agent.name).all()
    
    return jsonify({
        'status': 'success',
        'data': agents_schema.dump(agents)
    }), 200


@agents_bp.route('/<int:agent_id>', methods=['GET'])
@role_required('agent', 'admin')
def get_agent(agent_id):
    """
    Get agent details
    ---
    tags:
      - Agents
    security:
      - Bearer: []
    parameters:
      - in: path
        name: agent_id
        type: integer
        required: true
    responses:
      200:
        description: Agent details
      404:
        description: Agent not found
    """
    agent = Agent.query.get(agent_id)
    if not agent:
        raise NotFoundError('Agent not found')
    
    return jsonify({
        'status': 'success',
        'data': agent_schema.dump(agent)
    }), 200


@agents_bp.route('', methods=['POST'])
@role_required('admin')
def create_agent():
    """
    Create a new agent (admin only)
    ---
    tags:
      - Agents
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - email
            - password
          properties:
            name:
              type: string
              example: Jane Smith
            email:
              type: string
              example: jane@support.com
            password:
              type: string
              example: SecurePass123
            department:
              type: string
              example: Technical Support
            max_tickets:
              type: integer
              default: 10
    responses:
      201:
        description: Agent created
      409:
        description: Email already exists
    """
    from app.models.user import User
    
    try:
        data = agent_create_schema.load(request.json)
    except ValidationError as err:
        raise ValidationException('Validation failed', errors=err.messages)
    
    if User.query.filter_by(email=data['email']).first():
        raise ConflictError('Email already registered')
    
    agent = Agent(
        name=data['name'],
        email=data['email'],
        department=data.get('department'),
        max_tickets=data.get('max_tickets', 10),
        role='agent'
    )
    agent.set_password(data['password'])
    
    db.session.add(agent)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Agent created successfully',
        'data': agent_schema.dump(agent)
    }), 201


@agents_bp.route('/<int:agent_id>', methods=['PUT'])
@role_required('admin')
def update_agent(agent_id):
    """
    Update agent details (admin only)
    ---
    tags:
      - Agents
    security:
      - Bearer: []
    parameters:
      - in: path
        name: agent_id
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            name:
              type: string
            department:
              type: string
            is_available:
              type: boolean
            max_tickets:
              type: integer
    responses:
      200:
        description: Agent updated
      404:
        description: Agent not found
    """
    agent = Agent.query.get(agent_id)
    if not agent:
        raise NotFoundError('Agent not found')
    
    try:
        data = agent_update_schema.load(request.json)
    except ValidationError as err:
        raise ValidationException('Validation failed', errors=err.messages)
    
    for key, value in data.items():
        setattr(agent, key, value)
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Agent updated successfully',
        'data': agent_schema.dump(agent)
    }), 200


@agents_bp.route('/<int:agent_id>/tickets', methods=['GET'])
@role_required('agent', 'admin')
def get_agent_tickets(agent_id):
    """
    Get tickets assigned to an agent
    ---
    tags:
      - Agents
    security:
      - Bearer: []
    parameters:
      - in: path
        name: agent_id
        type: integer
        required: true
      - in: query
        name: status
        type: string
    responses:
      200:
        description: Agent's tickets
    """
    user = get_current_user()
    
    # Agents can only see their own tickets
    if user.role == 'agent' and user.id != agent_id:
        agent_id = user.id
    
    agent = Agent.query.get(agent_id)
    if not agent:
        raise NotFoundError('Agent not found')
    
    query = Ticket.query.filter_by(assigned_to_id=agent_id)
    
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)
    
    tickets = query.order_by(Ticket.created_at.desc()).all()
    tickets_schema = TicketSchema(many=True)
    
    return jsonify({
        'status': 'success',
        'data': tickets_schema.dump(tickets)
    }), 200


@agents_bp.route('/<int:agent_id>/availability', methods=['PUT'])
@jwt_required()
def update_availability(agent_id):
    """
    Update agent availability
    ---
    tags:
      - Agents
    security:
      - Bearer: []
    parameters:
      - in: path
        name: agent_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - is_available
          properties:
            is_available:
              type: boolean
    responses:
      200:
        description: Availability updated
    """
    user = get_current_user()
    
    # Agents can update their own availability, admins can update any
    if user.role == 'agent' and user.id != agent_id:
        raise NotFoundError('Agent not found')
    
    agent = Agent.query.get(agent_id)
    if not agent:
        raise NotFoundError('Agent not found')
    
    is_available = request.json.get('is_available')
    if is_available is None:
        raise ValidationException('is_available is required')
    
    agent.is_available = is_available
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': f'Agent is now {"available" if is_available else "unavailable"}',
        'data': agent_schema.dump(agent)
    }), 200
