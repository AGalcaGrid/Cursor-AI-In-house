"""
Email Service for sending notifications (FR-003, FR-007, FR-014, FR-018, FR-035)
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, render_template_string
from threading import Thread


class EmailService:
    """Service for sending email notifications."""
    
    # Email templates
    TEMPLATES = {
        'ticket_created': {
            'subject': 'Ticket Created: {ticket_number}',
            'body': '''
            <h2>Your Support Ticket Has Been Created</h2>
            <p>Dear Customer,</p>
            <p>Your support ticket has been successfully created.</p>
            <table style="border-collapse: collapse; margin: 20px 0;">
                <tr><td style="padding: 8px; font-weight: bold;">Ticket Number:</td><td style="padding: 8px;">{ticket_number}</td></tr>
                <tr><td style="padding: 8px; font-weight: bold;">Subject:</td><td style="padding: 8px;">{subject}</td></tr>
                <tr><td style="padding: 8px; font-weight: bold;">Priority:</td><td style="padding: 8px;">{priority}</td></tr>
                <tr><td style="padding: 8px; font-weight: bold;">Category:</td><td style="padding: 8px;">{category}</td></tr>
            </table>
            <p>We will review your request and get back to you shortly.</p>
            <p>Thank you for contacting us.</p>
            '''
        },
        'ticket_assigned': {
            'subject': 'Ticket Assigned: {ticket_number}',
            'body': '''
            <h2>New Ticket Assigned to You</h2>
            <p>Dear {agent_name},</p>
            <p>A new ticket has been assigned to you.</p>
            <table style="border-collapse: collapse; margin: 20px 0;">
                <tr><td style="padding: 8px; font-weight: bold;">Ticket Number:</td><td style="padding: 8px;">{ticket_number}</td></tr>
                <tr><td style="padding: 8px; font-weight: bold;">Subject:</td><td style="padding: 8px;">{subject}</td></tr>
                <tr><td style="padding: 8px; font-weight: bold;">Priority:</td><td style="padding: 8px;">{priority}</td></tr>
                <tr><td style="padding: 8px; font-weight: bold;">Customer:</td><td style="padding: 8px;">{customer_email}</td></tr>
            </table>
            <p>Please review and respond within the SLA timeframe.</p>
            '''
        },
        'status_changed': {
            'subject': 'Ticket Status Updated: {ticket_number}',
            'body': '''
            <h2>Ticket Status Updated</h2>
            <p>The status of your ticket has been updated.</p>
            <table style="border-collapse: collapse; margin: 20px 0;">
                <tr><td style="padding: 8px; font-weight: bold;">Ticket Number:</td><td style="padding: 8px;">{ticket_number}</td></tr>
                <tr><td style="padding: 8px; font-weight: bold;">Subject:</td><td style="padding: 8px;">{subject}</td></tr>
                <tr><td style="padding: 8px; font-weight: bold;">Previous Status:</td><td style="padding: 8px;">{old_status}</td></tr>
                <tr><td style="padding: 8px; font-weight: bold;">New Status:</td><td style="padding: 8px;">{new_status}</td></tr>
            </table>
            '''
        },
        'new_comment': {
            'subject': 'New Comment on Ticket: {ticket_number}',
            'body': '''
            <h2>New Comment Added</h2>
            <p>A new comment has been added to your ticket.</p>
            <table style="border-collapse: collapse; margin: 20px 0;">
                <tr><td style="padding: 8px; font-weight: bold;">Ticket Number:</td><td style="padding: 8px;">{ticket_number}</td></tr>
                <tr><td style="padding: 8px; font-weight: bold;">Subject:</td><td style="padding: 8px;">{subject}</td></tr>
                <tr><td style="padding: 8px; font-weight: bold;">Comment By:</td><td style="padding: 8px;">{commenter_name}</td></tr>
            </table>
            <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                {comment_content}
            </div>
            '''
        },
        'sla_warning': {
            'subject': 'SLA Warning: {ticket_number}',
            'body': '''
            <h2 style="color: #f59e0b;">⚠️ SLA Deadline Approaching</h2>
            <p>The following ticket is approaching its SLA deadline.</p>
            <table style="border-collapse: collapse; margin: 20px 0;">
                <tr><td style="padding: 8px; font-weight: bold;">Ticket Number:</td><td style="padding: 8px;">{ticket_number}</td></tr>
                <tr><td style="padding: 8px; font-weight: bold;">Subject:</td><td style="padding: 8px;">{subject}</td></tr>
                <tr><td style="padding: 8px; font-weight: bold;">Priority:</td><td style="padding: 8px;">{priority}</td></tr>
                <tr><td style="padding: 8px; font-weight: bold;">Deadline:</td><td style="padding: 8px; color: #f59e0b;">{deadline}</td></tr>
            </table>
            <p>Please take action to resolve this ticket before the deadline.</p>
            '''
        },
        'sla_breached': {
            'subject': '🚨 SLA Breached: {ticket_number}',
            'body': '''
            <h2 style="color: #ef4444;">🚨 SLA Breached</h2>
            <p>The following ticket has breached its SLA deadline.</p>
            <table style="border-collapse: collapse; margin: 20px 0;">
                <tr><td style="padding: 8px; font-weight: bold;">Ticket Number:</td><td style="padding: 8px;">{ticket_number}</td></tr>
                <tr><td style="padding: 8px; font-weight: bold;">Subject:</td><td style="padding: 8px;">{subject}</td></tr>
                <tr><td style="padding: 8px; font-weight: bold;">Priority:</td><td style="padding: 8px;">{priority}</td></tr>
                <tr><td style="padding: 8px; font-weight: bold;">Assigned To:</td><td style="padding: 8px;">{agent_name}</td></tr>
            </table>
            <p style="color: #ef4444; font-weight: bold;">Immediate action required!</p>
            '''
        },
        'mention': {
            'subject': 'You were mentioned in Ticket: {ticket_number}',
            'body': '''
            <h2>You Were Mentioned</h2>
            <p>You were mentioned in a comment on ticket {ticket_number}.</p>
            <table style="border-collapse: collapse; margin: 20px 0;">
                <tr><td style="padding: 8px; font-weight: bold;">Ticket Number:</td><td style="padding: 8px;">{ticket_number}</td></tr>
                <tr><td style="padding: 8px; font-weight: bold;">Subject:</td><td style="padding: 8px;">{subject}</td></tr>
                <tr><td style="padding: 8px; font-weight: bold;">Mentioned By:</td><td style="padding: 8px;">{commenter_name}</td></tr>
            </table>
            <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                {comment_content}
            </div>
            '''
        }
    }
    
    @staticmethod
    def _send_async_email(app, msg, recipients):
        """Send email asynchronously."""
        with app.app_context():
            try:
                if not app.config.get('MAIL_ENABLED'):
                    app.logger.info(f"Email disabled. Would send to: {recipients}")
                    return
                
                server = smtplib.SMTP(
                    app.config['MAIL_SERVER'],
                    app.config['MAIL_PORT']
                )
                if app.config.get('MAIL_USE_TLS'):
                    server.starttls()
                
                if app.config.get('MAIL_USERNAME') and app.config.get('MAIL_PASSWORD'):
                    server.login(
                        app.config['MAIL_USERNAME'],
                        app.config['MAIL_PASSWORD']
                    )
                
                for recipient in recipients:
                    server.sendmail(
                        app.config['MAIL_DEFAULT_SENDER'],
                        recipient,
                        msg.as_string()
                    )
                
                server.quit()
                app.logger.info(f"Email sent to: {recipients}")
            except Exception as e:
                app.logger.error(f"Failed to send email: {str(e)}")
    
    @classmethod
    def send_email(cls, template_name, recipients, **kwargs):
        """Send an email using a template."""
        if not recipients:
            return
        
        if isinstance(recipients, str):
            recipients = [recipients]
        
        template = cls.TEMPLATES.get(template_name)
        if not template:
            current_app.logger.error(f"Email template not found: {template_name}")
            return
        
        try:
            subject = template['subject'].format(**kwargs)
            body = template['body'].format(**kwargs)
        except KeyError as e:
            current_app.logger.error(f"Missing template variable: {e}")
            return
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = current_app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = ', '.join(recipients)
        
        # Wrap body in HTML template
        html_body = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                h2 {{ color: #2563eb; }}
                table {{ width: 100%; }}
            </style>
        </head>
        <body>
            {body}
            <hr style="margin-top: 30px; border: none; border-top: 1px solid #ddd;">
            <p style="color: #666; font-size: 12px;">
                This is an automated message from the Support Ticket System.
            </p>
        </body>
        </html>
        '''
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send asynchronously
        app = current_app._get_current_object()
        thread = Thread(target=cls._send_async_email, args=(app, msg, recipients))
        thread.start()
    
    @classmethod
    def notify_ticket_created(cls, ticket):
        """Send notification when ticket is created (FR-003)."""
        cls.send_email(
            'ticket_created',
            ticket.customer_email,
            ticket_number=ticket.ticket_number,
            subject=ticket.subject,
            priority=ticket.priority.upper(),
            category=ticket.category.replace('_', ' ').title()
        )
    
    @classmethod
    def notify_ticket_assigned(cls, ticket, agent):
        """Send notification when ticket is assigned (FR-007)."""
        cls.send_email(
            'ticket_assigned',
            agent.email,
            ticket_number=ticket.ticket_number,
            subject=ticket.subject,
            priority=ticket.priority.upper(),
            customer_email=ticket.customer_email,
            agent_name=agent.name
        )
    
    @classmethod
    def notify_status_changed(cls, ticket, old_status, new_status, recipients):
        """Send notification when status changes (FR-014)."""
        cls.send_email(
            'status_changed',
            recipients,
            ticket_number=ticket.ticket_number,
            subject=ticket.subject,
            old_status=old_status.replace('_', ' ').title(),
            new_status=new_status.replace('_', ' ').title()
        )
    
    @classmethod
    def notify_new_comment(cls, ticket, comment, commenter, recipients):
        """Send notification when comment is added (FR-018)."""
        cls.send_email(
            'new_comment',
            recipients,
            ticket_number=ticket.ticket_number,
            subject=ticket.subject,
            commenter_name=commenter.name,
            comment_content=comment.content
        )
    
    @classmethod
    def notify_sla_warning(cls, ticket, deadline, recipients):
        """Send SLA warning notification (FR-035)."""
        cls.send_email(
            'sla_warning',
            recipients,
            ticket_number=ticket.ticket_number,
            subject=ticket.subject,
            priority=ticket.priority.upper(),
            deadline=deadline.strftime('%Y-%m-%d %H:%M UTC')
        )
    
    @classmethod
    def notify_sla_breached(cls, ticket, recipients):
        """Send SLA breach notification (FR-035)."""
        agent_name = ticket.assigned_agent.name if ticket.assigned_agent else 'Unassigned'
        cls.send_email(
            'sla_breached',
            recipients,
            ticket_number=ticket.ticket_number,
            subject=ticket.subject,
            priority=ticket.priority.upper(),
            agent_name=agent_name
        )
    
    @classmethod
    def notify_mention(cls, ticket, comment, commenter, mentioned_user):
        """Send notification when user is mentioned (FR-017)."""
        cls.send_email(
            'mention',
            mentioned_user.email,
            ticket_number=ticket.ticket_number,
            subject=ticket.subject,
            commenter_name=commenter.name,
            comment_content=comment.content
        )
