from app import db
from app.models.notification import Notification


def create_notification(user_id, notification_type, title, message=None, task_id=None, project_id=None):
    """
    Create a new notification for a user.
    
    Args:
        user_id: ID of the user to notify
        notification_type: Type of notification (task_assigned, task_updated, project_invite, comment)
        title: Notification title
        message: Optional notification message
        task_id: Optional related task ID
        project_id: Optional related project ID
    
    Returns:
        Notification: The created notification object
    """
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        task_id=task_id,
        project_id=project_id
    )
    db.session.add(notification)
    db.session.commit()
    return notification


def notify_task_assigned(task, assignee_id):
    """Notify user when a task is assigned to them."""
    return create_notification(
        user_id=assignee_id,
        notification_type='task_assigned',
        title='Task Assigned',
        message=f'You have been assigned to task "{task.title}"',
        task_id=task.id,
        project_id=task.project_id
    )


def notify_task_updated(task, user_ids, updater_id):
    """Notify relevant users when a task is updated."""
    notifications = []
    for user_id in user_ids:
        if user_id != updater_id:  # Don't notify the person who made the update
            notification = create_notification(
                user_id=user_id,
                notification_type='task_updated',
                title='Task Updated',
                message=f'Task "{task.title}" has been updated',
                task_id=task.id,
                project_id=task.project_id
            )
            notifications.append(notification)
    return notifications


def notify_project_invite(project, user_id, inviter_name):
    """Notify user when they are invited to a project."""
    return create_notification(
        user_id=user_id,
        notification_type='project_invite',
        title='Project Invitation',
        message=f'{inviter_name} has invited you to project "{project.name}"',
        project_id=project.id
    )
