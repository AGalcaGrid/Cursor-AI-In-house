import csv
import io
from datetime import datetime, timedelta
from app.tasks import celery


@celery.task(bind=True)
def generate_ticket_report(self, user_id, report_type='daily', start_date=None, end_date=None):
    """
    Generate ticket report asynchronously.
    
    Args:
        user_id: ID of the user requesting the report
        report_type: Type of report (daily, weekly, monthly)
        start_date: Optional start date string (YYYY-MM-DD)
        end_date: Optional end date string (YYYY-MM-DD)
    """
    from app import db
    from app.models.ticket import Ticket
    from app.models.agent import Agent
    from sqlalchemy import func
    
    # Calculate date range based on report type
    now = datetime.utcnow()
    if start_date:
        start = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        if report_type == 'daily':
            start = now - timedelta(days=1)
        elif report_type == 'weekly':
            start = now - timedelta(weeks=1)
        else:  # monthly
            start = now - timedelta(days=30)
    
    if end_date:
        end = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        end = now
    
    # Query tickets in date range
    tickets = Ticket.query.filter(
        Ticket.created_at >= start,
        Ticket.created_at <= end
    ).all()
    
    # Calculate statistics
    total_tickets = len(tickets)
    status_counts = {}
    priority_counts = {}
    category_counts = {}
    
    for ticket in tickets:
        status_counts[ticket.status] = status_counts.get(ticket.status, 0) + 1
        priority_counts[ticket.priority] = priority_counts.get(ticket.priority, 0) + 1
        if ticket.category:
            category_counts[ticket.category] = category_counts.get(ticket.category, 0) + 1
    
    # Calculate resolution metrics
    resolved_tickets = [t for t in tickets if t.resolved_at]
    if resolved_tickets:
        total_resolution_time = sum(
            (t.resolved_at - t.created_at).total_seconds() 
            for t in resolved_tickets
        )
        avg_resolution_hours = (total_resolution_time / len(resolved_tickets)) / 3600
    else:
        avg_resolution_hours = 0
    
    # SLA metrics
    sla_response_breached = sum(1 for t in tickets if t.sla_response_breached)
    sla_resolution_breached = sum(1 for t in tickets if t.sla_resolution_breached)
    
    report_data = {
        'report_type': report_type,
        'date_range': {
            'start': start.isoformat(),
            'end': end.isoformat()
        },
        'summary': {
            'total_tickets': total_tickets,
            'resolved_tickets': len(resolved_tickets),
            'avg_resolution_hours': round(avg_resolution_hours, 2),
            'sla_response_breached': sla_response_breached,
            'sla_resolution_breached': sla_resolution_breached
        },
        'by_status': status_counts,
        'by_priority': priority_counts,
        'by_category': category_counts,
        'generated_at': datetime.utcnow().isoformat(),
        'generated_by': user_id
    }
    
    return report_data


@celery.task(bind=True)
def generate_agent_performance_report(self, user_id, agent_id=None):
    """
    Generate agent performance report asynchronously.
    
    Args:
        user_id: ID of the user requesting the report
        agent_id: Optional specific agent ID, or None for all agents
    """
    from app import db
    from app.models.ticket import Ticket
    from app.models.agent import Agent
    from app.models.comment import Comment
    
    if agent_id:
        agents = [Agent.query.get(agent_id)]
    else:
        agents = Agent.query.all()
    
    agent_stats = []
    
    for agent in agents:
        if not agent:
            continue
            
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
        
        # Average resolution time
        resolved_tickets = Ticket.query.filter(
            Ticket.assigned_to_id == agent.id,
            Ticket.resolved_at.isnot(None)
        ).all()
        
        if resolved_tickets:
            total_time = sum(
                (t.resolved_at - t.created_at).total_seconds() 
                for t in resolved_tickets
            )
            avg_resolution_hours = (total_time / len(resolved_tickets)) / 3600
        else:
            avg_resolution_hours = 0
        
        # Comments/responses
        total_comments = Comment.query.filter_by(author_id=agent.id).count()
        
        agent_stats.append({
            'agent_id': agent.id,
            'name': agent.name,
            'email': agent.email,
            'department': agent.department,
            'stats': {
                'total_assigned': total_assigned,
                'active_tickets': active_tickets,
                'resolved_tickets': resolved,
                'total_responses': total_comments,
                'avg_resolution_hours': round(avg_resolution_hours, 2),
                'is_available': agent.is_available
            }
        })
    
    return {
        'report_type': 'agent_performance',
        'generated_at': datetime.utcnow().isoformat(),
        'generated_by': user_id,
        'agents': agent_stats
    }


@celery.task(bind=True)
def export_tickets_to_csv(self, user_id, filters=None):
    """
    Export tickets to CSV format asynchronously.
    
    Args:
        user_id: ID of the user requesting the export
        filters: Optional dict of filters to apply
    """
    from app import db
    from app.models.ticket import Ticket
    
    query = Ticket.query
    
    if filters:
        if filters.get('status'):
            query = query.filter_by(status=filters['status'])
        if filters.get('priority'):
            query = query.filter_by(priority=filters['priority'])
        if filters.get('category'):
            query = query.filter_by(category=filters['category'])
    
    tickets = query.order_by(Ticket.created_at.desc()).limit(10000).all()
    
    # Generate CSV content
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
    
    csv_content = output.getvalue()
    
    return {
        'status': 'completed',
        'total_records': len(tickets),
        'generated_at': datetime.utcnow().isoformat(),
        'generated_by': user_id,
        'csv_content': csv_content
    }
