"""
Common async tasks using Celery.

These are general tasks that can be used across the application.
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def cleanup_old_logs():
    """
    Clean up old log entries from the database.
    
    This is scheduled via Celery Beat to run daily at midnight.
    Keeps only the last 30 days of logs.
    """
    # This is a placeholder - implement based on your logging model
    # If you have a Log model, you would delete old entries here
    
    logger.info('Running log cleanup task')
    
    # Example (if you have a Log model):
    # from apps.common.models import Log
    # thirty_days_ago = timezone.now() - timedelta(days=30)
    # deleted_count = Log.objects.filter(created_at__lt=thirty_days_ago).delete()[0]
    # logger.info(f'Cleaned up {deleted_count} old log entries')
    
    return 'Log cleanup completed'


@shared_task
def clear_cache():
    """
    Clear the Redis cache.
    
    Can be called manually or scheduled to clear stale cache.
    """
    from django.core.cache import cache
    
    try:
        cache.clear()
        logger.info('Cache cleared successfully')
        return 'Cache cleared successfully'
    except Exception as exc:
        logger.error(f'Failed to clear cache: {exc}')
        return f'Failed to clear cache: {exc}'


@shared_task
def health_check():
    """
    Health check task to verify Celery is working.
    
    Can be used for monitoring and uptime checks.
    """
    logger.info('Health check executed successfully')
    return {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
    }


@shared_task
def send_bulk_notification(user_ids, subject, message):
    """
    Send a notification to multiple users.
    
    Args:
        user_ids: List of user IDs to send notifications to
        subject: Email subject
        message: Email message body
    """
    from django.core.mail import send_mail
    from apps.users.models import User
    
    users = User.objects.filter(id__in=user_ids, is_active=True, email__isnull=False)
    emails = list(users.values_list('email', flat=True))
    
    if emails:
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email='noreply@promanage.com',
                recipient_list=emails,
                fail_silently=True,
            )
            logger.info(f'Bulk notification sent to {len(emails)} users')
            return f'Notification sent to {len(emails)} users'
        except Exception as exc:
            logger.error(f'Failed to send bulk notification: {exc}')
            return f'Failed: {exc}'
    
    return 'No valid recipients found'
