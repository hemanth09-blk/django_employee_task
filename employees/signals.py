import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Employee, EmployeeAudit


logger = logging.getLogger(__name__)


@receiver(post_save, sender=Employee)
def employee_audit_signal(sender, instance, created, **kwargs):
    try:
        action = "CREATE" if created else "UPDATE"

        EmployeeAudit.objects.create(
            employee=instance,
            action=action,
        )

        logger.info(
            "Employee audit created | employee_id=%s | action=%s",
            instance.id,
            action,
        )

    except Exception:
        logger.exception(
            "Failed to create employee audit | employee_id=%s",
            instance.id,
        )