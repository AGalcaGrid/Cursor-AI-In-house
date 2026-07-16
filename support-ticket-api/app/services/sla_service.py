"""
SLA Service for monitoring and escalating SLA breaches (FR-022)
"""
from datetime import datetime, timedelta
from app import db
from app.models.ticket import Ticket
from app.models.user import User
from app.models.comment import Comment
from app.services.email_service import EmailService


class SLAService:
    """Service for SLA monitoring and escalation."""
    
    @staticmethod
    def get_admins():
        """Get all admin users for escalation notifications."""
        return User.query.filter_by(role='admin', is_active=True).all()
    
    @classmethod
    def check_sla_warnings(cls):
        """
        Check for tickets approaching SLA deadline and send warnings.
        Should be called periodically (e.g., every 15 minutes).
        """
        # Get tickets that are approaching SLA (within 2 hours)
        warning_threshold = datetime.utcnow() + timedelta(hours=2)
        
        approaching_tickets = Ticket.query.filter(
            Ticket.status.notin_(['resolved', 'closed']),
            Ticket.sla_resolution_due.isnot(None),
            Ticket.sla_resolution_due <= warning_threshold,
            Ticket.sla_resolution_due > datetime.utcnow(),
            Ticket.sla_resolution_breached == False
        ).all()
        
        warnings_sent = 0
        for ticket in approaching_tickets:
            recipients = []
            
            # Notify assigned agent
            if ticket.assigned_agent:
                recipients.append(ticket.assigned_agent.email)
            
            # Notify admins for urgent/high priority
            if ticket.priority in ['urgent', 'high']:
                admins = cls.get_admins()
                recipients.extend([a.email for a in admins])
            
            if recipients:
                EmailService.notify_sla_warning(
                    ticket,
                    ticket.sla_resolution_due,
                    list(set(recipients))  # Remove duplicates
                )
                warnings_sent += 1
        
        return warnings_sent
    
    @classmethod
    def check_sla_breaches(cls):
        """
        Check for SLA breaches and trigger escalation (FR-022).
        Should be called periodically (e.g., every 5 minutes).
        """
        now = datetime.utcnow()
        
        # Check response SLA breaches
        response_breached = Ticket.query.filter(
            Ticket.status.notin_(['resolved', 'closed']),
            Ticket.sla_response_due.isnot(None),
            Ticket.sla_response_due < now,
            Ticket.first_response_at.is_(None),
            Ticket.sla_response_breached == False
        ).all()
        
        for ticket in response_breached:
            ticket.sla_response_breached = True
            cls._escalate_ticket(ticket, 'response')
        
        # Check resolution SLA breaches
        resolution_breached = Ticket.query.filter(
            Ticket.status.notin_(['resolved', 'closed']),
            Ticket.sla_resolution_due.isnot(None),
            Ticket.sla_resolution_due < now,
            Ticket.sla_resolution_breached == False
        ).all()
        
        for ticket in resolution_breached:
            ticket.sla_resolution_breached = True
            cls._escalate_ticket(ticket, 'resolution')
        
        db.session.commit()
        
        return len(response_breached) + len(resolution_breached)
    
    @classmethod
    def _escalate_ticket(cls, ticket, breach_type):
        """
        Escalate a ticket that has breached SLA.
        - Notify admins
        - Add internal comment
        - Optionally increase priority
        """
        admins = cls.get_admins()
        admin_emails = [a.email for a in admins]
        
        # Add assigned agent to notification
        if ticket.assigned_agent:
            admin_emails.append(ticket.assigned_agent.email)
        
        # Send breach notification
        EmailService.notify_sla_breached(ticket, list(set(admin_emails)))
        
        # Add internal comment about escalation
        escalation_comment = Comment(
            ticket_id=ticket.id,
            user_id=admins[0].id if admins else None,
            content=f"⚠️ SLA BREACH: {breach_type.upper()} SLA has been breached. "
                    f"This ticket requires immediate attention. "
                    f"Priority: {ticket.priority.upper()}, "
                    f"Assigned to: {ticket.assigned_agent.name if ticket.assigned_agent else 'Unassigned'}",
            is_internal=True
        )
        db.session.add(escalation_comment)
        
        # Auto-escalate priority for non-urgent tickets
        if ticket.priority not in ['urgent', 'high']:
            old_priority = ticket.priority
            if ticket.priority == 'low':
                ticket.priority = 'medium'
            elif ticket.priority == 'medium':
                ticket.priority = 'high'
            
            # Add priority change comment
            priority_comment = Comment(
                ticket_id=ticket.id,
                user_id=admins[0].id if admins else None,
                content=f"Priority automatically escalated from {old_priority.upper()} to {ticket.priority.upper()} due to SLA breach.",
                is_internal=True
            )
            db.session.add(priority_comment)
    
    @classmethod
    def run_sla_check(cls):
        """
        Run full SLA check - warnings and breaches.
        Returns tuple of (warnings_sent, breaches_found).
        """
        warnings = cls.check_sla_warnings()
        breaches = cls.check_sla_breaches()
        return warnings, breaches
