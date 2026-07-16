from datetime import datetime
from app.tasks import celery


@celery.task
def check_sla_breaches():
    """
    Periodic task to check and update SLA breach status for all active tickets.
    Should be scheduled to run every 15-30 minutes.
    """
    from app import db
    from app.models.ticket import Ticket
    
    # Get all active tickets (not resolved or closed)
    active_tickets = Ticket.query.filter(
        Ticket.status.notin_(['resolved', 'closed'])
    ).all()
    
    breached_count = 0
    now = datetime.utcnow()
    
    for ticket in active_tickets:
        was_response_breached = ticket.sla_response_breached
        was_resolution_breached = ticket.sla_resolution_breached
        
        ticket.check_sla_breach()
        
        # Track if newly breached
        if ticket.sla_response_breached and not was_response_breached:
            breached_count += 1
            send_sla_breach_alert.delay(ticket.id, 'response')
        
        if ticket.sla_resolution_breached and not was_resolution_breached:
            breached_count += 1
            send_sla_breach_alert.delay(ticket.id, 'resolution')
    
    db.session.commit()
    
    return {
        'status': 'completed',
        'checked_tickets': len(active_tickets),
        'new_breaches': breached_count,
        'checked_at': now.isoformat()
    }


@celery.task
def send_sla_breach_alert(ticket_id, breach_type):
    """
    Send alert when SLA is breached.
    
    Args:
        ticket_id: ID of the breached ticket
        breach_type: 'response' or 'resolution'
    """
    from app import db
    from app.models.ticket import Ticket
    from app.models.agent import Agent
    from app.tasks.email_tasks import send_email_notification
    
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return {'status': 'error', 'message': 'Ticket not found'}
    
    # Notify assigned agent if exists
    if ticket.assigned_to_id:
        agent = Agent.query.get(ticket.assigned_to_id)
        if agent:
            subject = f"SLA BREACH ALERT: {ticket.ticket_number}"
            body = f"""
URGENT: SLA Breach Alert

Ticket Number: {ticket.ticket_number}
Subject: {ticket.subject}
Priority: {ticket.priority}
Breach Type: {breach_type.upper()} SLA

{'Response was due by: ' + ticket.sla_response_due_at.isoformat() if breach_type == 'response' else ''}
{'Resolution is due by: ' + ticket.sla_resolution_due_at.isoformat() if breach_type == 'resolution' else ''}

Please take immediate action on this ticket.
"""
            send_email_notification.delay(agent.email, subject, body)
    
    return {
        'status': 'alert_sent',
        'ticket_id': ticket_id,
        'breach_type': breach_type
    }


@celery.task
def send_sla_warning(ticket_id, breach_type, hours_remaining):
    """
    Send warning before SLA breach.
    
    Args:
        ticket_id: ID of the ticket approaching SLA
        breach_type: 'response' or 'resolution'
        hours_remaining: Hours until SLA breach
    """
    from app import db
    from app.models.ticket import Ticket
    from app.models.agent import Agent
    from app.tasks.email_tasks import send_email_notification
    
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return {'status': 'error', 'message': 'Ticket not found'}
    
    if ticket.assigned_to_id:
        agent = Agent.query.get(ticket.assigned_to_id)
        if agent:
            subject = f"SLA Warning: {ticket.ticket_number}"
            body = f"""
SLA Warning

Ticket Number: {ticket.ticket_number}
Subject: {ticket.subject}
Priority: {ticket.priority}

Warning: {breach_type.upper()} SLA will be breached in approximately {hours_remaining} hours.

Please prioritize this ticket to avoid SLA breach.
"""
            send_email_notification.delay(agent.email, subject, body)
    
    return {
        'status': 'warning_sent',
        'ticket_id': ticket_id,
        'breach_type': breach_type,
        'hours_remaining': hours_remaining
    }


@celery.task
def check_approaching_sla():
    """
    Check for tickets approaching SLA deadline and send warnings.
    Should be scheduled to run every hour.
    """
    from app import db
    from app.models.ticket import Ticket
    
    now = datetime.utcnow()
    warning_threshold_hours = 2  # Warn 2 hours before breach
    
    # Get tickets approaching response SLA
    from datetime import timedelta
    warning_time = now + timedelta(hours=warning_threshold_hours)
    
    approaching_response = Ticket.query.filter(
        Ticket.status.notin_(['resolved', 'closed']),
        Ticket.first_response_at.is_(None),
        Ticket.sla_response_breached == False,
        Ticket.sla_response_due_at <= warning_time,
        Ticket.sla_response_due_at > now
    ).all()
    
    for ticket in approaching_response:
        hours_remaining = (ticket.sla_response_due_at - now).total_seconds() / 3600
        send_sla_warning.delay(ticket.id, 'response', round(hours_remaining, 1))
    
    # Get tickets approaching resolution SLA
    approaching_resolution = Ticket.query.filter(
        Ticket.status.notin_(['resolved', 'closed']),
        Ticket.sla_resolution_breached == False,
        Ticket.sla_resolution_due_at <= warning_time,
        Ticket.sla_resolution_due_at > now
    ).all()
    
    for ticket in approaching_resolution:
        hours_remaining = (ticket.sla_resolution_due_at - now).total_seconds() / 3600
        send_sla_warning.delay(ticket.id, 'resolution', round(hours_remaining, 1))
    
    return {
        'status': 'completed',
        'response_warnings': len(approaching_response),
        'resolution_warnings': len(approaching_resolution),
        'checked_at': now.isoformat()
    }
