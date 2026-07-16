"""Celery background tasks for asynchronous processing."""
from flask_mail import Message
from app import celery, mail, db
from app.models.task import Task
from app.models.user import User
from app.models.notification import Notification
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@celery.task(name='tasks.send_email_notification')
def send_email_notification(user_email, subject, body, html=None):
    """
    Send email notification asynchronously.
    
    Args:
        user_email: Recipient email address
        subject: Email subject
        body: Plain text email body
        html: Optional HTML email body
        
    Returns:
        str: Success message
    """
    try:
        msg = Message(
            subject=subject,
            recipients=[user_email],
            body=body,
            html=html
        )
        mail.send(msg)
        logger.info(f"Email sent successfully to {user_email}")
        return f"Email sent to {user_email}"
    except Exception as e:
        logger.error(f"Failed to send email to {user_email}: {str(e)}")
        raise


@celery.task(name='tasks.send_task_assignment_email')
def send_task_assignment_email(task_id, assignee_id):
    """
    Send email notification when a task is assigned.
    
    Args:
        task_id: ID of the assigned task
        assignee_id: ID of the user assigned to the task
        
    Returns:
        str: Success message
    """
    try:
        task = Task.query.get(task_id)
        assignee = User.query.get(assignee_id)
        
        if not task or not assignee:
            logger.warning(f"Task {task_id} or Assignee {assignee_id} not found")
            return "Task or assignee not found"
        
        subject = f"New Task Assigned: {task.title}"
        body = f"""
Hello {assignee.name},

You have been assigned a new task:

Title: {task.title}
Priority: {task.priority}
Status: {task.status}
Due Date: {task.due_date.strftime('%Y-%m-%d %H:%M') if task.due_date else 'Not set'}

Description:
{task.description or 'No description provided'}

Please log in to the task management system to view more details.

Best regards,
Task Management System
        """
        
        html = f"""
<html>
<body>
    <h2>New Task Assigned</h2>
    <p>Hello {assignee.name},</p>
    <p>You have been assigned a new task:</p>
    <ul>
        <li><strong>Title:</strong> {task.title}</li>
        <li><strong>Priority:</strong> {task.priority}</li>
        <li><strong>Status:</strong> {task.status}</li>
        <li><strong>Due Date:</strong> {task.due_date.strftime('%Y-%m-%d %H:%M') if task.due_date else 'Not set'}</li>
    </ul>
    <p><strong>Description:</strong></p>
    <p>{task.description or 'No description provided'}</p>
    <p>Please log in to the task management system to view more details.</p>
    <p>Best regards,<br>Task Management System</p>
</body>
</html>
        """
        
        return send_email_notification(assignee.email, subject, body, html)
    except Exception as e:
        logger.error(f"Failed to send task assignment email: {str(e)}")
        raise


@celery.task(name='tasks.generate_user_report')
def generate_user_report(user_id, report_type='summary'):
    """
    Generate user task report asynchronously.
    
    Args:
        user_id: ID of the user
        report_type: Type of report (summary, detailed, analytics)
        
    Returns:
        dict: Report data
    """
    try:
        user = User.query.get(user_id)
        if not user:
            logger.warning(f"User {user_id} not found")
            return {"error": "User not found"}
        
        # Get user's tasks
        tasks = Task.query.filter_by(user_id=user_id).all()
        assigned_tasks = Task.query.filter_by(assigned_to_id=user_id).all()
        
        # Calculate statistics
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == 'completed'])
        in_progress_tasks = len([t for t in tasks if t.status == 'in_progress'])
        pending_tasks = len([t for t in tasks if t.status == 'pending'])
        
        total_assigned = len(assigned_tasks)
        completed_assigned = len([t for t in assigned_tasks if t.status == 'completed'])
        
        # Overdue tasks
        now = datetime.utcnow()
        overdue_tasks = [t for t in tasks if t.due_date and t.due_date < now and t.status != 'completed']
        
        report = {
            'user_id': user_id,
            'user_name': user.name,
            'report_type': report_type,
            'generated_at': datetime.utcnow().isoformat(),
            'owned_tasks': {
                'total': total_tasks,
                'completed': completed_tasks,
                'in_progress': in_progress_tasks,
                'pending': pending_tasks,
                'overdue': len(overdue_tasks)
            },
            'assigned_tasks': {
                'total': total_assigned,
                'completed': completed_assigned
            }
        }
        
        if report_type == 'detailed':
            report['task_details'] = {
                'owned': [{'id': t.id, 'title': t.title, 'status': t.status, 'priority': t.priority} for t in tasks],
                'assigned': [{'id': t.id, 'title': t.title, 'status': t.status, 'priority': t.priority} for t in assigned_tasks]
            }
        
        logger.info(f"Report generated for user {user_id}")
        return report
    except Exception as e:
        logger.error(f"Failed to generate report for user {user_id}: {str(e)}")
        raise


@celery.task(name='tasks.send_due_date_reminders')
def send_due_date_reminders():
    """
    Send reminders for tasks due within 24 hours.
    Scheduled task to run daily.
    
    Returns:
        dict: Summary of reminders sent
    """
    try:
        tomorrow = datetime.utcnow() + timedelta(days=1)
        today = datetime.utcnow()
        
        # Find tasks due within 24 hours
        upcoming_tasks = Task.query.filter(
            Task.due_date.between(today, tomorrow),
            Task.status != 'completed'
        ).all()
        
        reminders_sent = 0
        for task in upcoming_tasks:
            if task.assigned_to_id:
                assignee = User.query.get(task.assigned_to_id)
                if assignee:
                    subject = f"Task Due Soon: {task.title}"
                    body = f"""
Hello {assignee.name},

This is a reminder that the following task is due within 24 hours:

Title: {task.title}
Priority: {task.priority}
Due Date: {task.due_date.strftime('%Y-%m-%d %H:%M')}

Please ensure it is completed on time.

Best regards,
Task Management System
                    """
                    send_email_notification.delay(assignee.email, subject, body)
                    reminders_sent += 1
        
        logger.info(f"Sent {reminders_sent} due date reminders")
        return {
            'reminders_sent': reminders_sent,
            'tasks_checked': len(upcoming_tasks)
        }
    except Exception as e:
        logger.error(f"Failed to send due date reminders: {str(e)}")
        raise


@celery.task(name='tasks.cleanup_old_notifications')
def cleanup_old_notifications(days=30):
    """
    Clean up old read notifications.
    
    Args:
        days: Delete notifications older than this many days
        
    Returns:
        dict: Summary of cleanup
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        old_notifications = Notification.query.filter(
            Notification.created_at < cutoff_date,
            Notification.read == True
        ).all()
        
        count = len(old_notifications)
        for notification in old_notifications:
            db.session.delete(notification)
        
        db.session.commit()
        logger.info(f"Cleaned up {count} old notifications")
        
        return {
            'deleted_count': count,
            'cutoff_date': cutoff_date.isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to cleanup notifications: {str(e)}")
        db.session.rollback()
        raise
