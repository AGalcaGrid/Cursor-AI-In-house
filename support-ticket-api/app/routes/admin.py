from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from app import db, cache
from app.models.ticket import Ticket
from app.models.user import User
from app.models.comment import Comment
from app.schemas.user import UserSchema
from app.schemas.ticket import TicketSchema
from app.utils.errors import ForbiddenError
from app.services.export_service import ExportService
from app.services.sla_service import SLAService
from flask import Response

admin_bp = Blueprint('admin', __name__)
user_schema = UserSchema()
users_schema = UserSchema(many=True)
tickets_schema = TicketSchema(many=True)


def get_current_user():
    """Get current authenticated user."""
    user_id = get_jwt_identity()
    return User.query.get(int(user_id))


@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60, key_prefix='admin_dashboard')
def get_dashboard():
    """
    Get admin dashboard statistics (FR-029)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: Dashboard statistics
      403:
        description: Admin access required
    """
    user = get_current_user()
    
    if not user.is_admin():
        raise ForbiddenError('Admin access required')
    
    # Ticket statistics
    total_tickets = Ticket.query.count()
    open_tickets = Ticket.query.filter_by(status='open').count()
    assigned_tickets = Ticket.query.filter_by(status='assigned').count()
    in_progress_tickets = Ticket.query.filter_by(status='in_progress').count()
    waiting_tickets = Ticket.query.filter_by(status='waiting').count()
    resolved_tickets = Ticket.query.filter_by(status='resolved').count()
    closed_tickets = Ticket.query.filter_by(status='closed').count()
    
    # Priority breakdown
    priority_stats = db.session.query(
        Ticket.priority,
        func.count(Ticket.id)
    ).filter(
        Ticket.status.notin_(['resolved', 'closed'])
    ).group_by(Ticket.priority).all()
    
    # Category breakdown
    category_stats = db.session.query(
        Ticket.category,
        func.count(Ticket.id)
    ).group_by(Ticket.category).all()
    
    # SLA compliance (FR-021)
    sla_breached = Ticket.query.filter(
        (Ticket.sla_response_breached == True) | (Ticket.sla_resolution_breached == True)
    ).count()
    
    active_tickets = Ticket.query.filter(
        Ticket.status.notin_(['closed'])
    ).count()
    
    sla_compliance = ((active_tickets - sla_breached) / active_tickets * 100) if active_tickets > 0 else 100
    
    # Average resolution time
    resolved = Ticket.query.filter(
        Ticket.resolved_at.isnot(None)
    ).all()
    
    if resolved:
        total_resolution_time = sum(
            (t.resolved_at - t.created_at).total_seconds() for t in resolved
        )
        avg_resolution_hours = (total_resolution_time / len(resolved)) / 3600
    else:
        avg_resolution_hours = 0
    
    # Agent workload
    agent_workload = db.session.query(
        User.id,
        User.name,
        func.count(Ticket.id).label('ticket_count')
    ).join(Ticket, User.id == Ticket.assigned_to_id).filter(
        Ticket.status.notin_(['resolved', 'closed']),
        User.role.in_(['agent', 'admin'])
    ).group_by(User.id, User.name).all()
    
    return jsonify({
        'status': 'success',
        'dashboard': {
            'tickets': {
                'total': total_tickets,
                'open': open_tickets,
                'assigned': assigned_tickets,
                'in_progress': in_progress_tickets,
                'waiting': waiting_tickets,
                'resolved': resolved_tickets,
                'closed': closed_tickets
            },
            'by_priority': {p: c for p, c in priority_stats},
            'by_category': {c: cnt for c, cnt in category_stats},
            'sla': {
                'compliance_rate': round(sla_compliance, 2),
                'breached_count': sla_breached
            },
            'performance': {
                'avg_resolution_hours': round(avg_resolution_hours, 2)
            },
            'agent_workload': [
                {'id': a[0], 'name': a[1], 'open_tickets': a[2]}
                for a in agent_workload
            ]
        }
    }), 200


@admin_bp.route('/reports/tickets', methods=['GET'])
@jwt_required()
def get_ticket_report():
    """
    Get ticket reports (FR-030)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - in: query
        name: period
        type: string
        enum: [daily, weekly, monthly]
        default: daily
      - in: query
        name: days
        type: integer
        default: 7
    responses:
      200:
        description: Ticket report
      403:
        description: Admin access required
    """
    user = get_current_user()
    
    if not user.is_admin():
        raise ForbiddenError('Admin access required')
    
    days = request.args.get('days', 7, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Tickets created per day
    daily_stats = db.session.query(
        func.date(Ticket.created_at).label('date'),
        func.count(Ticket.id).label('count')
    ).filter(
        Ticket.created_at >= start_date
    ).group_by(func.date(Ticket.created_at)).all()
    
    # Tickets by status
    status_stats = db.session.query(
        Ticket.status,
        func.count(Ticket.id)
    ).filter(
        Ticket.created_at >= start_date
    ).group_by(Ticket.status).all()
    
    return jsonify({
        'status': 'success',
        'report': {
            'period': f'Last {days} days',
            'daily_volume': [
                {'date': str(d), 'count': c} for d, c in daily_stats
            ],
            'by_status': {s: c for s, c in status_stats}
        }
    }), 200


@admin_bp.route('/reports/sla', methods=['GET'])
@jwt_required()
def get_sla_report():
    """
    Get SLA compliance report (FR-030)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: SLA report
      403:
        description: Admin access required
    """
    user = get_current_user()
    
    if not user.is_admin():
        raise ForbiddenError('Admin access required')
    
    # SLA statistics by priority
    sla_stats = []
    for priority in ['urgent', 'high', 'medium', 'low']:
        total = Ticket.query.filter_by(priority=priority).count()
        response_breached = Ticket.query.filter_by(
            priority=priority, sla_response_breached=True
        ).count()
        resolution_breached = Ticket.query.filter_by(
            priority=priority, sla_resolution_breached=True
        ).count()
        
        sla_stats.append({
            'priority': priority,
            'total': total,
            'response_breached': response_breached,
            'resolution_breached': resolution_breached,
            'compliance_rate': round(((total - resolution_breached) / total * 100) if total > 0 else 100, 2)
        })
    
    # Tickets approaching SLA deadline (FR-021)
    approaching_deadline = []
    active_tickets = Ticket.query.filter(
        Ticket.status.notin_(['resolved', 'closed'])
    ).all()
    
    for ticket in active_tickets:
        if ticket.is_approaching_sla():
            approaching_deadline.append({
                'ticket_number': ticket.ticket_number,
                'subject': ticket.subject,
                'priority': ticket.priority,
                'sla_resolution_due': ticket.sla_resolution_due.isoformat() if ticket.sla_resolution_due else None
            })
    
    return jsonify({
        'status': 'success',
        'report': {
            'by_priority': sla_stats,
            'approaching_deadline': approaching_deadline
        }
    }), 200


@admin_bp.route('/reports/export/tickets', methods=['GET'])
@jwt_required()
def export_tickets():
    """
    Export tickets to CSV or PDF (FR-028, FR-031)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - in: query
        name: format
        type: string
        enum: [csv, pdf]
        default: csv
      - in: query
        name: status
        type: string
      - in: query
        name: priority
        type: string
    responses:
      200:
        description: File download
      403:
        description: Admin access required
    """
    user = get_current_user()
    
    if not user.is_admin() and not user.is_agent():
        raise ForbiddenError('Access denied')
    
    # Build query with filters
    query = Ticket.query
    
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)
    
    priority = request.args.get('priority')
    if priority:
        query = query.filter_by(priority=priority)
    
    tickets = query.order_by(Ticket.created_at.desc()).all()
    
    export_format = request.args.get('format', 'csv').lower()
    
    if export_format == 'pdf':
        pdf_data = ExportService.tickets_to_pdf(tickets)
        return Response(
            pdf_data,
            mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment; filename=tickets_report_{datetime.now().strftime("%Y%m%d")}.pdf'}
        )
    else:
        csv_data = ExportService.tickets_to_csv(tickets)
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=tickets_report_{datetime.now().strftime("%Y%m%d")}.csv'}
        )


@admin_bp.route('/reports/export/agents', methods=['GET'])
@jwt_required()
def export_agent_report():
    """
    Export agent performance report to PDF (FR-031)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: PDF file download
      403:
        description: Admin access required
    """
    user = get_current_user()
    
    if not user.is_admin():
        raise ForbiddenError('Admin access required')
    
    # Get agent performance data
    agents = User.query.filter(User.role.in_(['agent', 'admin'])).all()
    
    agent_data = []
    for agent in agents:
        total_tickets = Ticket.query.filter_by(assigned_to_id=agent.id).count()
        resolved_tickets = Ticket.query.filter_by(
            assigned_to_id=agent.id,
            status='resolved'
        ).count()
        
        # Calculate average resolution time
        resolved = Ticket.query.filter(
            Ticket.assigned_to_id == agent.id,
            Ticket.resolved_at.isnot(None)
        ).all()
        
        if resolved:
            total_time = sum((t.resolved_at - t.created_at).total_seconds() for t in resolved)
            avg_hours = (total_time / len(resolved)) / 3600
        else:
            avg_hours = 0
        
        # SLA compliance
        breached = Ticket.query.filter(
            Ticket.assigned_to_id == agent.id,
            (Ticket.sla_response_breached == True) | (Ticket.sla_resolution_breached == True)
        ).count()
        
        compliance = ((total_tickets - breached) / total_tickets * 100) if total_tickets > 0 else 100
        
        agent_data.append({
            'name': agent.name,
            'total_tickets': total_tickets,
            'resolved_tickets': resolved_tickets,
            'avg_resolution_hours': avg_hours,
            'sla_compliance': compliance
        })
    
    pdf_data = ExportService.agent_report_to_pdf(agent_data)
    return Response(
        pdf_data,
        mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment; filename=agent_report_{datetime.now().strftime("%Y%m%d")}.pdf'}
    )


@admin_bp.route('/sla/check', methods=['POST'])
@jwt_required()
def run_sla_check():
    """
    Manually trigger SLA check and escalation (FR-022)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: SLA check completed
      403:
        description: Admin access required
    """
    user = get_current_user()
    
    if not user.is_admin():
        raise ForbiddenError('Admin access required')
    
    warnings, breaches = SLAService.run_sla_check()
    
    return jsonify({
        'status': 'success',
        'message': 'SLA check completed',
        'warnings_sent': warnings,
        'breaches_found': breaches
    }), 200


@admin_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    """
    Create a new user (agent or admin) - Admin only
    ---
    tags:
      - Admin
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
            - role
          properties:
            name:
              type: string
            email:
              type: string
            password:
              type: string
            role:
              type: string
              enum: [agent, admin]
    responses:
      201:
        description: User created
      400:
        description: Validation error
      403:
        description: Admin access required
      409:
        description: Email already exists
    """
    user = get_current_user()
    
    if not user.is_admin():
        raise ForbiddenError('Admin access required')
    
    data = request.json
    
    # Validate required fields
    if not all(k in data for k in ['name', 'email', 'password', 'role']):
        return jsonify({
            'status': 'error',
            'message': 'Missing required fields: name, email, password, role'
        }), 400
    
    # Validate role
    if data['role'] not in ['agent', 'admin']:
        return jsonify({
            'status': 'error',
            'message': 'Role must be agent or admin'
        }), 400
    
    # Check if email exists
    existing = User.query.filter_by(email=data['email']).first()
    if existing:
        return jsonify({
            'status': 'error',
            'message': 'Email already exists'
        }), 409
    
    # Create user
    new_user = User(
        name=data['name'],
        email=data['email'],
        role=data['role']
    )
    new_user.set_password(data['password'])
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': f'{data["role"].title()} created successfully',
        'user': user_schema.dump(new_user)
    }), 201


@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    """
    List all users - Admin only
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - in: query
        name: role
        type: string
        enum: [customer, agent, admin]
    responses:
      200:
        description: List of users
      403:
        description: Admin access required
    """
    user = get_current_user()
    
    if not user.is_admin():
        raise ForbiddenError('Admin access required')
    
    query = User.query
    
    role = request.args.get('role')
    if role:
        query = query.filter_by(role=role)
    
    users = query.order_by(User.created_at.desc()).all()
    
    return jsonify({
        'status': 'success',
        'users': users_schema.dump(users)
    }), 200


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """
    Update a user - Admin only
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            name:
              type: string
            role:
              type: string
              enum: [customer, agent, admin]
            is_active:
              type: boolean
    responses:
      200:
        description: User updated
      403:
        description: Admin access required
      404:
        description: User not found
    """
    current_user = get_current_user()
    
    if not current_user.is_admin():
        raise ForbiddenError('Admin access required')
    
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({
            'status': 'error',
            'message': 'User not found'
        }), 404
    
    data = request.json
    
    if 'name' in data:
        target_user.name = data['name']
    if 'role' in data and data['role'] in ['customer', 'agent', 'admin']:
        target_user.role = data['role']
    if 'is_active' in data:
        target_user.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'User updated successfully',
        'user': user_schema.dump(target_user)
    }), 200
