from app.tasks import celery


@celery.task(bind=True, max_retries=3)
def send_email_notification(self, recipient_email, subject, body, html_body=None):
    """
    Send email notification asynchronously.
    
    Args:
        recipient_email: Email address to send to
        subject: Email subject
        body: Plain text body
        html_body: Optional HTML body
    """
    try:
        from flask_mail import Message
        from app import db
        from flask import current_app
        
        # Import mail here to avoid circular imports
        from flask_mail import Mail
        mail = Mail(current_app)
        
        msg = Message(
            subject=subject,
            recipients=[recipient_email],
            body=body,
            html=html_body
        )
        mail.send(msg)
        return {'status': 'success', 'recipient': recipient_email}
    except Exception as exc:
        self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@celery.task
def send_ticket_created_notification(ticket_id):
    """Send notification when a new ticket is created."""
    from app import db
    from app.models.ticket import Ticket
    from app.models.customer import Customer
    
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return {'status': 'error', 'message': 'Ticket not found'}
    
    customer = Customer.query.get(ticket.customer_id)
    if not customer:
        return {'status': 'error', 'message': 'Customer not found'}
    
    subject = f"Ticket Created: {ticket.ticket_number}"
    body = f"""
Dear {customer.name},

Your support ticket has been created successfully.

Ticket Number: {ticket.ticket_number}
Subject: {ticket.subject}
Priority: {ticket.priority}
Status: {ticket.status}

We will respond to your request as soon as possible.

Thank you for contacting support.
"""
    
    send_email_notification.delay(customer.email, subject, body)
    return {'status': 'queued', 'ticket_id': ticket_id}


@celery.task
def send_ticket_assigned_notification(ticket_id, agent_id):
    """Send notification when a ticket is assigned to an agent."""
    from app import db
    from app.models.ticket import Ticket
    from app.models.agent import Agent
    
    ticket = Ticket.query.get(ticket_id)
    agent = Agent.query.get(agent_id)
    
    if not ticket or not agent:
        return {'status': 'error', 'message': 'Ticket or agent not found'}
    
    subject = f"New Ticket Assigned: {ticket.ticket_number}"
    body = f"""
Hello {agent.name},

A new ticket has been assigned to you.

Ticket Number: {ticket.ticket_number}
Subject: {ticket.subject}
Priority: {ticket.priority}
Category: {ticket.category or 'N/A'}

Please review and respond to this ticket.
"""
    
    send_email_notification.delay(agent.email, subject, body)
    return {'status': 'queued', 'ticket_id': ticket_id, 'agent_id': agent_id}


@celery.task
def send_ticket_status_changed_notification(ticket_id, old_status, new_status):
    """Send notification when ticket status changes."""
    from app import db
    from app.models.ticket import Ticket
    from app.models.customer import Customer
    
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return {'status': 'error', 'message': 'Ticket not found'}
    
    customer = Customer.query.get(ticket.customer_id)
    if not customer:
        return {'status': 'error', 'message': 'Customer not found'}
    
    subject = f"Ticket Update: {ticket.ticket_number}"
    body = f"""
Dear {customer.name},

Your support ticket status has been updated.

Ticket Number: {ticket.ticket_number}
Subject: {ticket.subject}
Previous Status: {old_status}
New Status: {new_status}

You can view your ticket for more details.

Thank you for your patience.
"""
    
    send_email_notification.delay(customer.email, subject, body)
    return {'status': 'queued', 'ticket_id': ticket_id}


@celery.task
def send_comment_notification(ticket_id, comment_id, is_internal=False):
    """Send notification when a new comment is added."""
    from app import db
    from app.models.ticket import Ticket
    from app.models.comment import Comment
    from app.models.customer import Customer
    from app.models.agent import Agent
    
    if is_internal:
        return {'status': 'skipped', 'reason': 'Internal comment'}
    
    ticket = Ticket.query.get(ticket_id)
    comment = Comment.query.get(comment_id)
    
    if not ticket or not comment:
        return {'status': 'error', 'message': 'Ticket or comment not found'}
    
    customer = Customer.query.get(ticket.customer_id)
    
    subject = f"New Response on Ticket: {ticket.ticket_number}"
    body = f"""
Dear {customer.name},

A new response has been added to your support ticket.

Ticket Number: {ticket.ticket_number}
Subject: {ticket.subject}

Response:
{comment.content[:500]}{'...' if len(comment.content) > 500 else ''}

Please log in to view the full response and reply.
"""
    
    send_email_notification.delay(customer.email, subject, body)
    return {'status': 'queued', 'ticket_id': ticket_id, 'comment_id': comment_id}
