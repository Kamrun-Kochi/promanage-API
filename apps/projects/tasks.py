"""
Async tasks for the projects app using Celery.

These tasks run in the background to handle:
- Email notifications for task assignments
- Daily task summaries
- Overdue task reminders
"""

from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_task_assignment_email(self, task_id, user_email, task_title, project_title):
    """
    Send email notification when a task is assigned to a user.
    
    Args:
        task_id: ID of the assigned task
        user_email: Email of the assigned user
        task_title: Title of the task
        project_title: Title of the project
    """
    try:
        subject = f'Task Assigned: {task_title}'
        message = f'''
Hello,

You have been assigned a new task:

Task: {task_title}
Project: {project_title}

Please log in to your dashboard to view the task details.

Best regards,
ProManage Team
'''
        send_mail(
            subject=subject,
            message=message,
            from_email='noreply@promanage.com',
            recipient_list=[user_email],
            fail_silently=False,
        )
        logger.info(f'Task assignment email sent to {user_email} for task {task_id}')
        return f'Email sent successfully to {user_email}'
    
    except Exception as exc:
        logger.error(f'Failed to send task assignment email: {exc}')
        # Retry the task up to 3 times
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_task_status_update_email(self, task_id, user_email, task_title, old_status, new_status):
    """
    Send email notification when a task status is updated.
    """
    try:
        subject = f'Task Status Updated: {task_title}'
        message = f'''
Hello,

The status of a task has been updated:

Task: {task_title}
Status: {old_status} → {new_status}

Please log in to your dashboard to view the task.

Best regards,
ProManage Team
'''
        send_mail(
            subject=subject,
            message=message,
            from_email='noreply@promanage.com',
            recipient_list=[user_email],
            fail_silently=False,
        )
        logger.info(f'Task status update email sent to {user_email}')
        return f'Email sent successfully'
    
    except Exception as exc:
        logger.error(f'Failed to send status update email: {exc}')
        raise self.retry(exc=exc, countdown=60)


@shared_task
def send_daily_task_summary():
    """
    Send daily summary of tasks to all users.
    
    This is scheduled via Celery Beat to run daily at 8 AM.
    """
    from apps.projects.models import Task
    from apps.users.models import User
    
    users = User.objects.filter(is_active=True)
    
    for user in users:
        # Get user's tasks
        assigned_tasks = Task.objects.filter(
            assigned_to=user,
            status__in=['TODO', 'IN_PROGRESS']
        )
        
        # Get tasks due today or overdue
        today = timezone.now().date()
        due_today = assigned_tasks.filter(due_date__date=today)
        overdue = assigned_tasks.filter(due_date__date__lt=today)
        
        if assigned_tasks.exists():
            try:
                subject = f'Daily Task Summary - {today}'
                message = f'''
Hello {user.get_full_name() or user.username},

Here's your daily task summary:

Total Active Tasks: {assigned_tasks.count()}
- Due Today: {due_today.count()}
- Overdue: {overdue.count()}

Please log in to your dashboard to view your tasks.

Best regards,
ProManage Team
'''
                send_mail(
                    subject=subject,
                    message=message,
                    from_email='noreply@promanage.com',
                    recipient_list=[user.email],
                    fail_silently=True,
                )
                logger.info(f'Daily summary sent to {user.email}')
            except Exception as exc:
                logger.error(f'Failed to send daily summary to {user.email}: {exc}')
    
    return f'Daily summary processed for {users.count()} users'


@shared_task
def check_overdue_tasks():
    """
    Check for overdue tasks and send reminders.
    
    This is scheduled via Celery Beat to run every hour.
    """
    from apps.projects.models import Task
    
    today = timezone.now().date()
    
    # Find overdue tasks that aren't done
    overdue_tasks = Task.objects.filter(
        due_date__date__lt=today,
        status__in=['TODO', 'IN_PROGRESS']
    ).select_related('assigned_to', 'project')
    
    reminders_sent = 0
    
    for task in overdue_tasks:
        if task.assigned_to and task.assigned_to.email:
            try:
                days_overdue = (today - task.due_date.date()).days
                subject = f'Overdue Task Reminder: {task.title}'
                message = f'''
Hello {task.assigned_to.get_full_name() or task.assigned_to.username},

This is a reminder that the following task is overdue:

Task: {task.title}
Project: {task.project.title}
Days Overdue: {days_overdue}

Please update the task status or contact your project manager.

Best regards,
ProManage Team
'''
                send_mail(
                    subject=subject,
                    message=message,
                    from_email='noreply@promanage.com',
                    recipient_list=[task.assigned_to.email],
                    fail_silently=True,
                )
                reminders_sent += 1
            except Exception as exc:
                logger.error(f'Failed to send overdue reminder: {exc}')
    
    logger.info(f'Overdue task check completed. Sent {reminders_sent} reminders.')
    return f'Checked overdue tasks. Sent {reminders_sent} reminders.'


@shared_task
def generate_project_report(project_id):
    """
    Generate a project report in the background.
    
    This task runs asynchronously to generate reports for large projects.
    """
    from apps.projects.models import Project
    
    try:
        project = Project.objects.get(id=project_id)
        tasks = project.tasks.all()
        
        # Generate report data
        report_data = {
            'project_title': project.title,
            'total_tasks': tasks.count(),
            'completed_tasks': tasks.filter(status='DONE').count(),
            'in_progress_tasks': tasks.filter(status='IN_PROGRESS').count(),
            'todo_tasks': tasks.filter(status='TODO').count(),
        }
        
        # In a real application, you would save this to a file or database
        logger.info(f'Project report generated for {project.title}: {report_data}')
        return report_data
    
    except Project.DoesNotExist:
        logger.error(f'Project {project_id} not found')
        return {'error': 'Project not found'}
