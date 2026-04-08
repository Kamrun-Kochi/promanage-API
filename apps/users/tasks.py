"""
Async tasks for the users app using Celery.

These tasks handle user-related background operations.
"""

from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_welcome_email(self, user_id):
    """
    Send a welcome email to a newly registered user.
    
    Args:
        user_id: ID of the newly registered user
    """
    from apps.users.models import User
    
    try:
        user = User.objects.get(id=user_id)
        
        subject = 'Welcome to ProManage!'
        message = f'''
Hello {user.get_full_name() or user.username},

Welcome to ProManage! We're excited to have you on board.

With ProManage, you can:
- Create and manage projects
- Assign and track tasks
- Collaborate with your team

Get started by logging in and creating your first project!

Best regards,
ProManage Team
'''
        send_mail(
            subject=subject,
            message=message,
            from_email='noreply@promanage.com',
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f'Welcome email sent to {user.email}')
        return f'Welcome email sent to {user.email}'
    
    except User.DoesNotExist:
        logger.error(f'User {user_id} not found')
        return 'User not found'
    except Exception as exc:
        logger.error(f'Failed to send welcome email: {exc}')
        raise self.retry(exc=exc, countdown=60)


@shared_task
def send_password_reset_email(user_id, reset_token):
    """
    Send password reset email to user.
    
    Args:
        user_id: ID of the user requesting password reset
        reset_token: Password reset token
    """
    from apps.users.models import User
    
    try:
        user = User.objects.get(id=user_id)
        
        subject = 'Password Reset Request - ProManage'
        message = f'''
Hello {user.get_full_name() or user.username},

You requested a password reset for your ProManage account.

Reset Token: {reset_token}

If you didn't request this, please ignore this email.

Best regards,
ProManage Team
'''
        send_mail(
            subject=subject,
            message=message,
            from_email='noreply@promanage.com',
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f'Password reset email sent to {user.email}')
        return f'Password reset email sent'
    
    except User.DoesNotExist:
        logger.error(f'User {user_id} not found')
        return 'User not found'


@shared_task
def cleanup_inactive_users():
    """
    Clean up inactive users or send re-engagement emails.
    
    This could be scheduled to run weekly or monthly.
    """
    from apps.users.models import User
    from datetime import timedelta
    
    # Find users who haven't logged in for 90 days
    ninety_days_ago = timezone.now() - timedelta(days=90)
    inactive_users = User.objects.filter(
        last_login__lt=ninety_days_ago,
        is_active=True
    )
    
    # Could send re-engagement emails or deactivate accounts
    logger.info(f'Found {inactive_users.count()} inactive users')
    
    return f'Found {inactive_users.count()} inactive users'


@shared_task
def export_user_data(user_id):
    """
    Export user data in the background.
    
    This is useful for GDPR data export requests.
    """
    from apps.users.models import User
    from apps.projects.models import Project, Task
    import json
    
    try:
        user = User.objects.get(id=user_id)
        
        # Gather user data
        user_data = {
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'date_joined': user.date_joined.isoformat(),
            },
            'owned_projects': list(
                user.owned_projects.values('id', 'title', 'created_at')
            ),
            'assigned_tasks': list(
                user.assigned_tasks.values(
                    'id', 'title', 'status', 'due_date', 'project__title'
                )
            ),
        }
        
        # In a real application, you would save this to a file
        # or store in a model for download
        logger.info(f'User data exported for {user.username}')
        return user_data
    
    except User.DoesNotExist:
        logger.error(f'User {user_id} not found')
        return {'error': 'User not found'}
