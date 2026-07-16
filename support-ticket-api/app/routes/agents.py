from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.user import User
from app.models.ticket import Ticket
from app.schemas.user import UserSchema, AgentSchema
from app.schemas.ticket import TicketSchema
from app.utils.errors import NotFoundError, ForbiddenError

agents_bp = Blueprint('agents', __name__)
user_schema = UserSchema()
agent_schema = AgentSchema()
agents_schema = AgentSchema(many=True)
tickets_schema = TicketSchema(many=True)


def get_current_user():
    """Get current authenticated user."""
    user_id = get_jwt_identity()
    return User.query.get(int(user_id))


@agents_bp.route('', methods=['GET'])
@jwt_required()
def get_agents():
    """
    List all agents
    ---
    tags:
      - Agents
    security:
      - Bearer: []
    responses:
      200:
        description: List of agents
      403:
        description: Admin access required
    """
    user = get_current_user()
    
    if not user.is_admin():
        raise ForbiddenError('Admin access required')
    
    agents = User.query.filter(User.role.in_(['agent', 'admin'])).all()
    
    return jsonify({
        'status': 'success',
        'agents': agents_schema.dump(agents)
    }), 200


@agents_bp.route('/<int:agent_id>', methods=['GET'])
@jwt_required()
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
    user = get_current_user()
    
    if not user.is_admin() and user.id != agent_id:
        raise ForbiddenError('Access denied')
    
    agent = User.query.get(agent_id)
    if not agent or agent.is_customer():
        raise NotFoundError('Agent not found')
    
    return jsonify({
        'status': 'success',
        'agent': agent_schema.dump(agent)
    }), 200


@agents_bp.route('/<int:agent_id>/tickets', methods=['GET'])
@jwt_required()
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
      403:
        description: Access denied
      404:
        description: Agent not found
    """
    user = get_current_user()
    
    if not user.is_admin() and user.id != agent_id:
        raise ForbiddenError('Access denied')
    
    agent = User.query.get(agent_id)
    if not agent or agent.is_customer():
        raise NotFoundError('Agent not found')
    
    query = Ticket.query.filter_by(assigned_to_id=agent_id)
    
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)
    
    tickets = query.order_by(Ticket.created_at.desc()).all()
    
    return jsonify({
        'status': 'success',
        'agent': agent_schema.dump(agent),
        'tickets': tickets_schema.dump(tickets)
    }), 200


@agents_bp.route('/<int:agent_id>/availability', methods=['PUT'])
@jwt_required()
def update_availability(agent_id):
    """
    Update agent availability status
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
            - availability_status
          properties:
            availability_status:
              type: string
              enum: [available, busy, offline]
    responses:
      200:
        description: Availability updated
      403:
        description: Access denied
      404:
        description: Agent not found
    """
    user = get_current_user()
    
    if not user.is_admin() and user.id != agent_id:
        raise ForbiddenError('Access denied')
    
    agent = User.query.get(agent_id)
    if not agent or agent.is_customer():
        raise NotFoundError('Agent not found')
    
    data = request.json
    status = data.get('availability_status')
    
    if status not in ['available', 'busy', 'offline']:
        raise ForbiddenError('Invalid availability status')
    
    agent.availability_status = status
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': f'Availability updated to {status}',
        'agent': agent_schema.dump(agent)
    }), 200
