from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from sqlalchemy import func, case

from app import db, cache
from app.models.ticket import Ticket
from app.models.customer import Customer
from app.models.agent import Agent
from app.models.comment import Comment
from app.schemas.agent import AgentSchema
from app.utils.security import role_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard', methods=['GET'])
@role_required('admin')
@cache.cached(timeout=60, key_prefix='admin_dashboard')
def get_dashboard():
    """
    Get admin dashboard statistics
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: Dashboard statistics
    """
    # Ticket statistics
    total_tickets = Ticket.query.count()
    open_tickets = Ticket.query.filter_by(status='open').count()
    in_progress_tickets = Ticket.query.filter(
        Ticket.status.in_(['assigned', 'in_progress', 'waiting'])
    ).count()
    resolved_tickets = Ticket.query.filter_by(status='resolved').count()
    closed_tickets = Ticket.query.filter_by(status='closed').count()
    
    # Priority breakdown
    priority_stats = db.session.query(
        Ticket.priority,
        func.count(Ticket.id)
    ).filter(
        Ticket.status.notin_(['resolved', 'closed'])
    ).group_by(Ticket.priority).all()
    
    # Tickets by category
    category_stats = db.session.query(
        Ticket.category,
        func.count(Ticket.id)
    ).group_by(Ticket.category).all()
    
    # Agent statistics
    total_agents = Agent.query.count()
    available_agents = Agent.query.filter_by(is_available=True).count()
    
    # Customer statistics
    total_customers = Customer.query.count()
    
    # Recent activity (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    new_tickets_24h = Ticket.query.filter(Ticket.created_at >= yesterday).count()
    resolved_24h = Ticket.query.filter(Ticket.resolved_at >= yesterday).count()
    
    # SLA breaches (response or resolution)
    sla_response_breached = Ticket.query.filter_by(sla_response_breached=True).filter(
        Ticket.status.notin_(['resolved', 'closed'])
    ).count()
    sla_resolution_breached = Ticket.query.filter_by(sla_resolution_breached=True).filter(
        Ticket.status.notin_(['resolved', 'closed'])
    ).count()
    
    return jsonify({
        'status': 'success',
        'data': {
            'tickets': {
                'total': total_tickets,
                'open': open_tickets,
                'in_progress': in_progress_tickets,
                'resolved': resolved_tickets,
                'closed': closed_tickets,
                'new_24h': new_tickets_24h,
                'resolved_24h': resolved_24h,
                'sla_response_breached': sla_response_breached,
                'sla_resolution_breached': sla_resolution_breached
            },
            'priority_breakdown': {
                priority: count for priority, count in priority_stats
            },
            'category_breakdown': {
                category or 'uncategorized': count for category, count in category_stats
            },
            'agents': {
                'total': total_agents,
                'available': available_agents
            },
            'customers': {
                'total': total_customers
            }
        }
    }), 200


@admin_bp.route('/reports/tickets', methods=['GET'])
@role_required('admin')
def get_ticket_report():
    """
    Get detailed ticket report
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - in: query
        name: start_date
        type: string
        format: date
        description: Start date (YYYY-MM-DD)
      - in: query
        name: end_date
        type: string
        format: date
        description: End date (YYYY-MM-DD)
    responses:
      200:
        description: Ticket report
    """
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Ticket.query
    
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Ticket.created_at >= start)
        except ValueError:
            pass
    
    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(Ticket.created_at < end)
        except ValueError:
            pass
    
    # Tickets by status
    status_breakdown = db.session.query(
        Ticket.status,
        func.count(Ticket.id)
    ).group_by(Ticket.status).all()
    
    # Tickets by priority
    priority_breakdown = db.session.query(
        Ticket.priority,
        func.count(Ticket.id)
    ).group_by(Ticket.priority).all()
    
    # Average resolution time (for resolved tickets)
    resolved_tickets = Ticket.query.filter(
        Ticket.resolved_at.isnot(None)
    ).all()
    
    if resolved_tickets:
        total_resolution_time = sum(
            (t.resolved_at - t.created_at).total_seconds() 
            for t in resolved_tickets
        )
        avg_resolution_hours = (total_resolution_time / len(resolved_tickets)) / 3600
    else:
        avg_resolution_hours = 0
    
    # Average first response time
    responded_tickets = Ticket.query.filter(
        Ticket.first_response_at.isnot(None)
    ).all()
    
    if responded_tickets:
        total_response_time = sum(
            (t.first_response_at - t.created_at).total_seconds() 
            for t in responded_tickets
        )
        avg_response_hours = (total_response_time / len(responded_tickets)) / 3600
    else:
        avg_response_hours = 0
    
    return jsonify({
        'status': 'success',
        'data': {
            'status_breakdown': {
                status: count for status, count in status_breakdown
            },
            'priority_breakdown': {
                priority: count for priority, count in priority_breakdown
            },
            'metrics': {
                'avg_resolution_time_hours': round(avg_resolution_hours, 2),
                'avg_first_response_hours': round(avg_response_hours, 2),
                'total_tickets': query.count()
            }
        }
    }), 200


@admin_bp.route('/reports/agents', methods=['GET'])
@role_required('admin')
def get_agent_report():
    """
    Get agent performance report
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: Agent performance report
    """
    agents = Agent.query.all()
    agent_stats = []
    
    for agent in agents:
        # Total tickets handled
        total_assigned = Ticket.query.filter_by(assigned_to_id=agent.id).count()
        
        # Currently active tickets
        active_tickets = Ticket.query.filter(
            Ticket.assigned_to_id == agent.id,
            Ticket.status.in_(['assigned', 'in_progress', 'waiting'])
        ).count()
        
        # Resolved tickets
        resolved = Ticket.query.filter(
            Ticket.assigned_to_id == agent.id,
            Ticket.status.in_(['resolved', 'closed'])
        ).count()
        
        # Comments/responses
        total_comments = Comment.query.filter_by(author_id=agent.id).count()
        
        agent_stats.append({
            'agent': AgentSchema(only=['id', 'name', 'email', 'department']).dump(agent),
            'stats': {
                'total_assigned': total_assigned,
                'active_tickets': active_tickets,
                'resolved_tickets': resolved,
                'total_responses': total_comments,
                'is_available': agent.is_available,
                'can_accept_tickets': agent.can_accept_tickets
            }
        })
    
    return jsonify({
        'status': 'success',
        'data': agent_stats
    }), 200


@admin_bp.route('/tickets/unassigned', methods=['GET'])
@role_required('admin', 'agent')
def get_unassigned_tickets():
    """
    Get all unassigned tickets
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: Unassigned tickets
    """
    from app.schemas.ticket import TicketSchema
    
    tickets = Ticket.query.filter(
        Ticket.assigned_to_id.is_(None),
        Ticket.status == 'open'
    ).order_by(
        case(
            (Ticket.priority == 'urgent', 1),
            (Ticket.priority == 'high', 2),
            (Ticket.priority == 'medium', 3),
            (Ticket.priority == 'low', 4)
        ),
        Ticket.created_at.asc()
    ).all()
    
    tickets_schema = TicketSchema(many=True)
    
    return jsonify({
        'status': 'success',
        'data': tickets_schema.dump(tickets)
    }), 200


@admin_bp.route('/tickets/sla-breached', methods=['GET'])
@role_required('admin')
def get_sla_breached_tickets():
    """
    Get tickets that have breached SLA
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - in: query
        name: type
        type: string
        enum: [response, resolution, all]
        default: all
    responses:
      200:
        description: SLA breached tickets
    """
    from app.schemas.ticket import TicketSchema
    
    breach_type = request.args.get('type', 'all')
    
    query = Ticket.query.filter(
        Ticket.status.notin_(['resolved', 'closed'])
    )
    
    if breach_type == 'response':
        query = query.filter(Ticket.sla_response_breached == True)
    elif breach_type == 'resolution':
        query = query.filter(Ticket.sla_resolution_breached == True)
    else:  # all
        query = query.filter(
            db.or_(
                Ticket.sla_response_breached == True,
                Ticket.sla_resolution_breached == True
            )
        )
    
    tickets = query.order_by(Ticket.created_at.asc()).all()
    tickets_schema = TicketSchema(many=True)
    
    return jsonify({
        'status': 'success',
        'data': tickets_schema.dump(tickets)
    }), 200


@admin_bp.route('/reports/sla', methods=['GET'])
@role_required('admin')
def get_sla_report():
    """
    Get SLA compliance report per PRD FR-030
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - in: query
        name: start_date
        type: string
        format: date
      - in: query
        name: end_date
        type: string
        format: date
    responses:
      200:
        description: SLA compliance report
    """
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Ticket.query
    
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Ticket.created_at >= start)
        except ValueError:
            pass
    
    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(Ticket.created_at < end)
        except ValueError:
            pass
    
    total_tickets = query.count()
    
    # Response SLA compliance
    tickets_with_response = query.filter(Ticket.first_response_at.isnot(None)).count()
    response_breached = query.filter(Ticket.sla_response_breached == True).count()
    response_compliant = tickets_with_response - response_breached if tickets_with_response > response_breached else 0
    
    # Resolution SLA compliance
    resolved_tickets = query.filter(Ticket.status.in_(['resolved', 'closed'])).count()
    resolution_breached = query.filter(Ticket.sla_resolution_breached == True).count()
    resolution_compliant = resolved_tickets - resolution_breached if resolved_tickets > resolution_breached else 0
    
    # SLA by priority
    sla_by_priority = {}
    for priority in ['urgent', 'high', 'medium', 'low']:
        priority_query = query.filter(Ticket.priority == priority)
        priority_total = priority_query.count()
        priority_response_breached = priority_query.filter(Ticket.sla_response_breached == True).count()
        priority_resolution_breached = priority_query.filter(Ticket.sla_resolution_breached == True).count()
        
        sla_by_priority[priority] = {
            'total': priority_total,
            'response_breached': priority_response_breached,
            'resolution_breached': priority_resolution_breached,
            'response_compliance_rate': round((priority_total - priority_response_breached) / priority_total * 100, 2) if priority_total > 0 else 100,
            'resolution_compliance_rate': round((priority_total - priority_resolution_breached) / priority_total * 100, 2) if priority_total > 0 else 100
        }
    
    # Overall compliance rates
    response_compliance_rate = round(response_compliant / tickets_with_response * 100, 2) if tickets_with_response > 0 else 100
    resolution_compliance_rate = round(resolution_compliant / resolved_tickets * 100, 2) if resolved_tickets > 0 else 100
    
    return jsonify({
        'status': 'success',
        'data': {
            'summary': {
                'total_tickets': total_tickets,
                'tickets_with_response': tickets_with_response,
                'resolved_tickets': resolved_tickets,
                'response_sla_breached': response_breached,
                'resolution_sla_breached': resolution_breached,
                'response_compliance_rate': response_compliance_rate,
                'resolution_compliance_rate': resolution_compliance_rate
            },
            'by_priority': sla_by_priority
        }
    }), 200


@admin_bp.route('/reports/export', methods=['POST'])
@role_required('admin')
def export_report():
    """
    Export report data per PRD FR-031
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
            - report_type
            - format
          properties:
            report_type:
              type: string
              enum: [tickets, agents, sla]
            format:
              type: string
              enum: [csv, json]
            start_date:
              type: string
              format: date
            end_date:
              type: string
              format: date
    responses:
      200:
        description: Report data
    """
    import csv
    import io
    from flask import Response
    
    data = request.json or {}
    report_type = data.get('report_type', 'tickets')
    export_format = data.get('format', 'json')
    
    if report_type == 'tickets':
        tickets = Ticket.query.order_by(Ticket.created_at.desc()).limit(1000).all()
        
        if export_format == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Ticket Number', 'Subject', 'Status', 'Priority', 'Category', 'Created At'])
            for t in tickets:
                writer.writerow([t.ticket_number, t.subject, t.status, t.priority, t.category, t.created_at.isoformat()])
            output.seek(0)
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename=tickets_report_{datetime.utcnow().strftime("%Y%m%d")}.csv'}
            )
        else:
            from app.schemas.ticket import TicketSchema
            return jsonify({
                'status': 'success',
                'data': TicketSchema(many=True).dump(tickets)
            }), 200
    
    elif report_type == 'agents':
        agents = Agent.query.all()
        agent_data = []
        for agent in agents:
            agent_data.append({
                'id': agent.id,
                'name': agent.name,
                'email': agent.email,
                'department': agent.department,
                'total_tickets': Ticket.query.filter_by(assigned_to_id=agent.id).count(),
                'active_tickets': agent.current_ticket_count,
                'is_available': agent.is_available
            })
        
        if export_format == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['ID', 'Name', 'Email', 'Department', 'Total Tickets', 'Active Tickets', 'Available'])
            for a in agent_data:
                writer.writerow([a['id'], a['name'], a['email'], a['department'], a['total_tickets'], a['active_tickets'], a['is_available']])
            output.seek(0)
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename=agents_report_{datetime.utcnow().strftime("%Y%m%d")}.csv'}
            )
        else:
            return jsonify({
                'status': 'success',
                'data': agent_data
            }), 200
    
    return jsonify({
        'status': 'error',
        'message': 'Invalid report type'
    }), 400
