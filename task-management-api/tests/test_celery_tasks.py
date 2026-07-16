"""Tests for Celery background tasks."""
import pytest
from datetime import datetime, timedelta
from app.tasks.celery_tasks import (
    send_email_notification,
    send_task_assignment_email,
    generate_user_report,
    send_due_date_reminders,
    cleanup_old_notifications
)
from app.models.task import Task
from app.models.notification import Notification


class TestEmailNotifications:
    """Test email notification tasks."""
    
    def test_send_email_notification_success(self, app, mocker):
        """Test sending email notification successfully."""
        mock_mail = mocker.patch('app.tasks.celery_tasks.mail.send')
        
        with app.app_context():
            result = send_email_notification(
                'test@example.com',
                'Test Subject',
                'Test Body',
                '<p>Test HTML</p>'
            )
        
        assert 'Email sent to test@example.com' in result
        mock_mail.assert_called_once()
    
    def test_send_email_notification_failure(self, app, mocker):
        """Test email notification failure handling."""
        mock_mail = mocker.patch('app.tasks.celery_tasks.mail.send', side_effect=Exception('SMTP Error'))
        
        with app.app_context():
            with pytest.raises(Exception):
                send_email_notification('test@example.com', 'Subject', 'Body')
    
    def test_send_task_assignment_email(self, app, db_session, test_task, another_user, mocker):
        """Test sending task assignment email."""
        mock_send = mocker.patch('app.tasks.celery_tasks.send_email_notification')
        
        with app.app_context():
            result = send_task_assignment_email(test_task.id, another_user.id)
        
        mock_send.assert_called_once()
        call_args = mock_send.call_args[0]
        assert call_args[0] == another_user.email
        assert 'New Task Assigned' in call_args[1]
        assert test_task.title in call_args[2]
    
    def test_send_task_assignment_email_task_not_found(self, app, another_user, mocker):
        """Test sending assignment email when task doesn't exist."""
        mock_send = mocker.patch('app.tasks.celery_tasks.send_email_notification')
        
        with app.app_context():
            result = send_task_assignment_email(99999, another_user.id)
        
        assert 'not found' in result
        mock_send.assert_not_called()


class TestReportGeneration:
    """Test report generation tasks."""
    
    def test_generate_user_report_summary(self, app, db_session, test_user, multiple_tasks):
        """Test generating summary report."""
        with app.app_context():
            report = generate_user_report(test_user.id, 'summary')
        
        assert report['user_id'] == test_user.id
        assert report['report_type'] == 'summary'
        assert 'owned_tasks' in report
        assert 'assigned_tasks' in report
        assert report['owned_tasks']['total'] == 10
        assert 'generated_at' in report
    
    def test_generate_user_report_detailed(self, app, db_session, test_user, multiple_tasks):
        """Test generating detailed report."""
        with app.app_context():
            report = generate_user_report(test_user.id, 'detailed')
        
        assert report['report_type'] == 'detailed'
        assert 'task_details' in report
        assert 'owned' in report['task_details']
        assert len(report['task_details']['owned']) == 10
    
    def test_generate_user_report_with_completed_tasks(self, app, db_session, test_user, completed_task):
        """Test report includes completed task statistics."""
        with app.app_context():
            report = generate_user_report(test_user.id, 'summary')
        
        assert report['owned_tasks']['completed'] == 1
        assert report['owned_tasks']['total'] == 1
    
    def test_generate_user_report_user_not_found(self, app):
        """Test report generation when user doesn't exist."""
        with app.app_context():
            report = generate_user_report(99999, 'summary')
        
        assert 'error' in report
        assert report['error'] == 'User not found'
    
    def test_generate_user_report_overdue_tasks(self, app, db_session, test_user):
        """Test report includes overdue task count."""
        # Create overdue task
        overdue_task = Task(
            title='Overdue Task',
            description='This task is overdue',
            status='pending',
            priority='high',
            user_id=test_user.id,
            due_date=datetime.utcnow() - timedelta(days=1)
        )
        db_session.session.add(overdue_task)
        db_session.session.commit()
        
        with app.app_context():
            report = generate_user_report(test_user.id, 'summary')
        
        assert report['owned_tasks']['overdue'] == 1


class TestScheduledTasks:
    """Test scheduled background tasks."""
    
    def test_send_due_date_reminders(self, app, db_session, test_user, another_user, mocker):
        """Test sending due date reminders for upcoming tasks."""
        mock_send = mocker.patch('app.tasks.celery_tasks.send_email_notification')
        
        # Create task due tomorrow
        tomorrow_task = Task(
            title='Due Tomorrow',
            description='Task due tomorrow',
            status='pending',
            priority='high',
            user_id=test_user.id,
            assigned_to_id=another_user.id,
            due_date=datetime.utcnow() + timedelta(hours=12)
        )
        db_session.session.add(tomorrow_task)
        db_session.session.commit()
        
        with app.app_context():
            result = send_due_date_reminders()
        
        assert result['reminders_sent'] == 1
        assert result['tasks_checked'] == 1
        mock_send.delay.assert_called_once()
    
    def test_send_due_date_reminders_no_upcoming_tasks(self, app, db_session, mocker):
        """Test reminders when no tasks are due soon."""
        mock_send = mocker.patch('app.tasks.celery_tasks.send_email_notification')
        
        with app.app_context():
            result = send_due_date_reminders()
        
        assert result['reminders_sent'] == 0
        assert result['tasks_checked'] == 0
        mock_send.delay.assert_not_called()
    
    def test_send_due_date_reminders_skip_completed(self, app, db_session, test_user, another_user, mocker):
        """Test that reminders skip completed tasks."""
        mock_send = mocker.patch('app.tasks.celery_tasks.send_email_notification')
        
        # Create completed task due tomorrow
        completed_task = Task(
            title='Completed Task',
            description='Already completed',
            status='completed',
            priority='high',
            user_id=test_user.id,
            assigned_to_id=another_user.id,
            due_date=datetime.utcnow() + timedelta(hours=12)
        )
        db_session.session.add(completed_task)
        db_session.session.commit()
        
        with app.app_context():
            result = send_due_date_reminders()
        
        assert result['reminders_sent'] == 0
        mock_send.delay.assert_not_called()
    
    def test_cleanup_old_notifications(self, app, db_session, test_user):
        """Test cleaning up old read notifications."""
        # Create old read notification
        old_notification = Notification(
            user_id=test_user.id,
            type='task_assigned',
            title='Old Notification',
            message='This is old',
            read=True,
            created_at=datetime.utcnow() - timedelta(days=35)
        )
        
        # Create recent notification
        recent_notification = Notification(
            user_id=test_user.id,
            type='task_assigned',
            title='Recent Notification',
            message='This is recent',
            read=True,
            created_at=datetime.utcnow() - timedelta(days=5)
        )
        
        # Create unread old notification
        unread_notification = Notification(
            user_id=test_user.id,
            type='task_assigned',
            title='Unread Notification',
            message='This is unread',
            read=False,
            created_at=datetime.utcnow() - timedelta(days=35)
        )
        
        db_session.session.add_all([old_notification, recent_notification, unread_notification])
        db_session.session.commit()
        
        with app.app_context():
            result = cleanup_old_notifications(days=30)
        
        assert result['deleted_count'] == 1
        
        # Verify only old read notification was deleted
        remaining = Notification.query.all()
        assert len(remaining) == 2
        assert recent_notification in remaining
        assert unread_notification in remaining
    
    def test_cleanup_old_notifications_custom_days(self, app, db_session, test_user):
        """Test cleanup with custom day threshold."""
        old_notification = Notification(
            user_id=test_user.id,
            type='task_assigned',
            title='Old Notification',
            message='This is old',
            read=True,
            created_at=datetime.utcnow() - timedelta(days=8)
        )
        db_session.session.add(old_notification)
        db_session.session.commit()
        
        with app.app_context():
            result = cleanup_old_notifications(days=7)
        
        assert result['deleted_count'] == 1


class TestTaskErrorHandling:
    """Test error handling in background tasks."""
    
    def test_email_task_logs_error(self, app, mocker):
        """Test that email errors are logged."""
        mock_logger = mocker.patch('app.tasks.celery_tasks.logger')
        mocker.patch('app.tasks.celery_tasks.mail.send', side_effect=Exception('SMTP Error'))
        
        with app.app_context():
            with pytest.raises(Exception):
                send_email_notification('test@example.com', 'Subject', 'Body')
        
        mock_logger.error.assert_called_once()
    
    def test_report_generation_logs_error(self, app, mocker):
        """Test that report generation errors are logged."""
        mock_logger = mocker.patch('app.tasks.celery_tasks.logger')
        mocker.patch('app.tasks.celery_tasks.User.query.get', side_effect=Exception('DB Error'))
        
        with app.app_context():
            with pytest.raises(Exception):
                generate_user_report(1, 'summary')
        
        mock_logger.error.assert_called_once()
    
    def test_cleanup_rollback_on_error(self, app, db_session, test_user, mocker):
        """Test that cleanup rolls back on error."""
        notification = Notification(
            user_id=test_user.id,
            type='task_assigned',
            title='Test',
            message='Test',
            read=True,
            created_at=datetime.utcnow() - timedelta(days=35)
        )
        db_session.session.add(notification)
        db_session.session.commit()
        
        # Mock commit to raise an error
        mocker.patch.object(db_session.session, 'commit', side_effect=Exception('DB Error'))
        mock_rollback = mocker.patch.object(db_session.session, 'rollback')
        
        with app.app_context():
            with pytest.raises(Exception):
                cleanup_old_notifications(days=30)
        
        mock_rollback.assert_called_once()
